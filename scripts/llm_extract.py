"""Step 3 (and reused in Steps 5 and 9B): LLM extraction of EPS mentions from a parsed filing.

The model returns each mention as a verbatim `value_text` plus a verbatim `context` snippet; character
offsets into the parsed `text` are then resolved locally (LLMs cannot count characters reliably).

Usage:
  python scripts/llm_extract.py --variant A                 # all 50 filings -> data/prelabels/A/<acc>.json
  python scripts/llm_extract.py --variant B --only acc1,acc2
  python scripts/llm_extract.py --variant A --model claude-opus-5 --workers 4
"""
import argparse, json, os, re, sys, time, glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import anthropic

try:
    import winreg
except ImportError:  # not Windows
    winreg = None

ROOT = Path(__file__).resolve().parent.parent
PARSED = ROOT / "data" / "parsed"
DEFAULT_MODEL = "claude-opus-5"


def api_key():
    """The desktop app may not inherit user-scope variables, so fall back to the Windows registry."""
    k = os.environ.get("ANTHROPIC_API_KEY")
    if k:
        return k
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            return winreg.QueryValueEx(key, "ANTHROPIC_API_KEY")[0]
    except Exception:
        return None


TYPES = ["GAAP_BASIC", "GAAP_DILUTED", "NON_GAAP", "GUIDANCE"]
PERIOD_KINDS = ["current_quarter", "prior_year_quarter", "prior_quarter", "current_ytd", "prior_ytd",
                "full_year", "guidance_period", "other"]

SCHEMA = {
    "type": "object",
    "properties": {
        "mentions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "value": {"type": "number"},
                    "value_text": {"type": "string"},
                    "context": {"type": "string"},
                    "type": {"type": "string", "enum": TYPES},
                    "period": {"type": "string"},
                    "period_kind": {"type": "string", "enum": PERIOD_KINDS},
                },
                "required": ["value", "value_text", "context", "type", "period", "period_kind"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["mentions"],
    "additionalProperties": False,
}

# ---- Prompt variant A: definitional / rule-based phrasing ----
SYSTEM_A = """You are a financial-data annotator. You will be given the plain text of an SEC Form 8-K earnings release (Item 2.02 plus Exhibit 99.1). Table rows appear on one line with cells separated by " | ".

Task: find EVERY mention of an earnings-per-share (EPS) figure in the document and return each one as a structured record.

Definitions
- GAAP_DILUTED: diluted net income (loss) per share under GAAP. If a single figure is labeled "basic and diluted", classify it as GAAP_DILUTED.
- GAAP_BASIC: basic net income (loss) per share under GAAP.
- NON_GAAP: any adjusted / core / operating / non-GAAP / "excluding items" per-share figure for a completed period.
- GUIDANCE: any forward-looking EPS figure (outlook, guidance, target, range endpoint), GAAP or non-GAAP.

Rules
- Include every occurrence: headline, bullets, narrative sentences, tables, reconciliations. The same number appearing three times is three mentions.
- Include prior-period comparatives (prior-year quarter, year-to-date, etc.) and set period_kind accordingly.
- Exclude per-share amounts that are not earnings: dividends, book value, share price, buyback prices, net asset value, percentages, share counts.
- Exclude per-share figures for individual items (e.g. "an impairment of $0.10 per share") unless they are labeled as an EPS/net income per share total. Segment-level or continuing-operations EPS totals are included; put the qualifier in `period`.
- `value` is the numeric EPS with losses NEGATIVE, even when the text shows a positive number next to the word "loss" (e.g. "net loss per share of $0.42" -> -0.42; "(0.42)" -> -0.42).
- `value_text` is the EXACT characters of the number as it appears in the document, without the leading "$" (e.g. "0.71", "(0.42)", "-1.19", "15.19").
- `context` is an EXACT, contiguous, verbatim substring of the document (40 to 200 characters) that contains `value_text` and enough surrounding words to locate it unambiguously. Copy it character-for-character, including " | " separators inside table rows. Do not paraphrase, do not fix typos, do not merge lines.
- `period` is a short human description, e.g. "Q1 2020", "Q1 2019", "six months ended March 31, 2020", "FY2020 guidance".
- `period_kind`: current_quarter = the quarter this release reports; prior_year_quarter = same quarter one year earlier; prior_quarter = immediately preceding quarter; current_ytd / prior_ytd = year-to-date totals; full_year = a completed fiscal year; guidance_period = forward-looking; other = anything else.
"""

# ---- Prompt variant B: example-driven / conversational phrasing ----
SYSTEM_B = """You annotate earnings press releases for a machine-learning dataset. The input is the text of an 8-K earnings release; tables are flattened so each row is one line with " | " between cells.

Go through the whole document and pull out each place an earnings-per-share number is stated. Think of it as highlighting every EPS number a careful analyst would notice, including the ones in the financial tables at the end and the comparison figures for last year.

For each highlighted number tell me:
- value: the number as a signed decimal. A loss is negative. "loss per share of $0.42" is -0.42 and "(0.42)" is -0.42.
- value_text: the number exactly as printed, minus any "$" sign. Keep parentheses and minus signs. Examples: "0.71", "(0.42)", "-1.19".
- context: a verbatim copy of the surrounding text, between 40 and 200 characters, that includes value_text. This must be a character-for-character substring of the input (keep the " | " separators if it is a table row). I will use it to locate the number in the file, so it must match exactly.
- type: one of
    GAAP_DILUTED - reported diluted EPS (also use this when a line says "basic and diluted"),
    GAAP_BASIC - reported basic EPS,
    NON_GAAP - adjusted, core, operating, cash, or otherwise non-GAAP EPS for a period that has already ended,
    GUIDANCE - any EPS number about the future (outlook, targets, guidance ranges; use this for both GAAP and non-GAAP outlook numbers).
- period: what period the number is for, in plain words ("Q1 2020", "Q1 2019", "fiscal 2020 outlook", "nine months ended March 31, 2020").
- period_kind: current_quarter, prior_year_quarter, prior_quarter, current_ytd, prior_ytd, full_year, guidance_period, or other.

Do not include dividends per share, book value per share, stock prices, or share counts. Do not include the per-share effect of a single item (like "a $0.05 per share charge") unless the document labels it as an EPS total. If the same EPS number is printed in several places, report each place separately.
"""

VARIANTS = {"A": SYSTEM_A, "B": SYSTEM_B}


def user_message(doc_text):
    return ("Document begins.\n\n" + doc_text + "\n\nDocument ends. Return the JSON with every EPS mention.")


_ws = re.compile(r"\s+")


def _norm(s):
    return _ws.sub(" ", s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')).strip()


def _variants(vt):
    out = [vt]
    if vt.startswith("(") and vt.endswith(")"):
        core = vt[1:-1]
        out += ["($" + core + ")", "-" + core, "−" + core, core]
    elif vt.startswith("-"):
        out += ["(" + vt[1:] + ")", "($" + vt[1:] + ")", vt[1:]]
    return list(dict.fromkeys(out))


def _standalone(text, a, b):
    if a > 0 and (text[a - 1].isdigit() or text[a - 1] == "."):
        return False
    if b < len(text) and (text[b].isdigit() or (text[b] == "." and b + 1 < len(text) and text[b + 1].isdigit())):
        return False
    return True


def resolve_offsets(text, mention, used):
    """Returns (start, end, how), or (None, None, reason) when the mention cannot be placed."""
    ctx, vt = mention["context"], mention["value_text"]
    if not vt:
        return None, None, "empty value_text"
    # candidate context start positions, from strict to tolerant matching
    tries = []
    if ctx:
        tries.append(("exact", [m.start() for m in re.finditer(re.escape(ctx), text)]))
        pat = r"\s+".join(re.escape(tok) for tok in _norm(ctx).split(" "))
        pat = pat.replace(r"'", "['’‘]").replace(r'\"', '["“”]')
        tries.append(("normalized", [m.start() for m in re.finditer(pat, text)]))
        # tolerant: alphanumeric tokens only, anything non-alphanumeric allowed between them
        toks = re.findall(r"[A-Za-z0-9]+", ctx)
        if len(toks) >= 3:
            pat2 = r"[^A-Za-z0-9]*".join(re.escape(t) for t in toks)
            tries.append(("tolerant", [m.start() for m in re.finditer(pat2, text)]))
    found_ctx = False
    for method, starts in tries:
        if not starts:
            continue
        found_ctx = True
        for s in starts:
            seg = text[s:s + len(ctx) + 60]
            for v in _variants(vt):
                for m in re.finditer(re.escape(v), seg):
                    a, b = _bare_number(text, s + m.start(), s + m.end())
                    if _standalone(text, a, b) and (a, b) not in used:
                        return a, b, method if v == vt else method + "+variant"
    # last resort: a line that shares most of the context's words and contains the value
    toks = [t for t in re.findall(r"[A-Za-z0-9]+", ctx) if len(t) >= 3]
    if toks:
        pos = 0
        for line in text.split("\n"):
            hit = sum(1 for t in toks if t in line)
            if hit >= max(2, int(0.6 * len(toks))):
                for v in _variants(vt):
                    for m in re.finditer(re.escape(v), line):
                        a, b = _bare_number(text, pos + m.start(), pos + m.end())
                        if _standalone(text, a, b) and (a, b) not in used:
                            return a, b, "line-fuzzy"
            pos += len(line) + 1
    return None, None, ("value_text not found in context" if found_ctx else "context not found")


def _bare_number(text, a, b):
    while a < b and text[a] in "($-− ":
        a += 1
    while b > a and text[b - 1] in ") ":
        b -= 1
    return a, b


def postprocess(text, raw_mentions):
    used = set()
    mentions = []
    for m in raw_mentions:
        base = {k: m[k] for k in ("value", "value_text", "context", "type", "period", "period_kind")}
        a, b, how = resolve_offsets(text, base, used)
        if a is not None:
            used.add((a, b))
        mentions.append({**base, "start": a, "end": b, "resolve": how,
                         "span_text": text[a:b] if a is not None else None})
    mentions.sort(key=lambda m: (m["start"] is None, m["start"] or 0))
    primary_vals = [m["value"] for m in mentions if m["type"] == "GAAP_DILUTED" and m["period_kind"] == "current_quarter"]
    primary = max(set(primary_vals), key=primary_vals.count) if primary_vals else None
    return mentions, primary, sorted(set(primary_vals))


def extract_one(client, model, variant, rec, max_retries=2):
    text = rec["text"]
    sysmsg = VARIANTS[variant]
    last_err = None
    for attempt in range(max_retries + 1):
        try:
            with client.messages.stream(
                model=model,
                max_tokens=32000,
                system=sysmsg,
                messages=[{"role": "user", "content": user_message(text)}],
                output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
            ) as stream:
                msg = stream.get_final_message()
            if msg.stop_reason == "refusal":
                raise RuntimeError(f"refusal: {msg.stop_details}")
            if msg.stop_reason == "max_tokens":
                raise RuntimeError("hit max_tokens")
            out = json.loads(next(b.text for b in msg.content if b.type == "text"))
            usage = {"input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens}
            break
        except (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.InternalServerError, RuntimeError) as e:
            last_err = e
            time.sleep(5 * (attempt + 1))
    else:
        raise RuntimeError(f"extraction failed for {rec['accession']}: {last_err}")

    mentions, primary, cands = postprocess(text, out["mentions"])
    return {
        "accession": rec["accession"], "company": rec["company"], "variant": variant, "model": model,
        "primary_gaap_diluted_eps": primary,
        "primary_candidates": cands,
        "n_mentions": len(mentions),
        "n_unresolved": sum(m["start"] is None for m in mentions),
        "usage": usage, "mentions": mentions,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="A", choices=list(VARIANTS))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--only", default=None, help="comma-separated accession numbers")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=None, help="output dir (default data/prelabels/<variant>)")
    ap.add_argument("--force", action="store_true", help="re-run even if output exists")
    ap.add_argument("--reresolve", action="store_true", help="only re-resolve offsets of existing outputs (no API calls)")
    args = ap.parse_args()

    outdir = Path(args.out) if args.out else ROOT / "data" / "prelabels" / args.variant
    outdir.mkdir(parents=True, exist_ok=True)
    client = anthropic.Anthropic(api_key=api_key())
    recs = [json.loads(Path(p).read_text(encoding="utf-8")) for p in sorted(glob.glob(str(PARSED / "*.json")))]
    if args.only:
        keep = set(args.only.split(","))
        recs = [r for r in recs if r["accession"] in keep]
    if args.reresolve:
        n_un = 0
        for r in recs:
            p = outdir / f"{r['accession']}.json"
            if not p.exists():
                continue
            res = json.loads(p.read_text(encoding="utf-8"))
            res["mentions"], res["primary_gaap_diluted_eps"], res["primary_candidates"] = postprocess(r["text"], res["mentions"])
            res["n_unresolved"] = sum(m["start"] is None for m in res["mentions"])
            n_un += res["n_unresolved"]
            p.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"re-resolved {len(recs)} filings; unresolved spans now: {n_un}")
        return
    todo = [r for r in recs if args.force or not (outdir / f"{r['accession']}.json").exists()]
    print(f"variant={args.variant} model={args.model} filings={len(recs)} to_run={len(todo)} -> {outdir}")

    tot_in = tot_out = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(extract_one, client, args.model, args.variant, r): r for r in todo}
        for f in as_completed(futs):
            r = futs[f]
            try:
                res = f.result()
            except Exception as e:
                print(f"FAILED {r['accession']} {r['company']}: {e}")
                continue
            (outdir / f"{r['accession']}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
            tot_in += res["usage"]["input_tokens"]; tot_out += res["usage"]["output_tokens"]
            print(f"{r['accession']} | {r['company'][:28]:28} | mentions={res['n_mentions']:3d} unresolved={res['n_unresolved']:2d} "
                  f"| primary={res['primary_gaap_diluted_eps']} cands={res['primary_candidates']} | tok in/out {res['usage']['input_tokens']}/{res['usage']['output_tokens']}")
    print(f"\nTOTAL tokens in={tot_in} out={tot_out}")


if __name__ == "__main__":
    main()
