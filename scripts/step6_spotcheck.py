"""Step 6: build the manual spot-check batch.

Priority: every filing flagged in Step 4 (anchor mismatch / no primary) or Step 5 (pass A vs B disagree),
then a seeded random sample of unflagged filings to reach TARGET filings.

Outputs
  data/spotcheck/spotcheck.md   -> editable review sheet (fill the Verdict column; see legend at top)
  data/spotcheck/spotcheck.html -> same content, span highlighted, for quick reading
  data/spotcheck/spotcheck.json -> machine copy of every mention shown (used by Step 7 to apply verdicts)
"""
import json, random, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "spotcheck"
OUT.mkdir(parents=True, exist_ok=True)
TARGET = 13
SEED = 42

cross = {r["accession"]: r for r in json.loads((ROOT / "data" / "crossval.json").read_text(encoding="utf-8"))}
sc_path = ROOT / "data" / "selfconsistency.json"
selfc = {r["accession"]: r for r in json.loads(sc_path.read_text(encoding="utf-8"))} if sc_path.exists() else {}

flag_reason = {}
for acc, r in cross.items():
    if r["status"] in ("mismatch", "no_primary", "match_but_multiple_candidates", "missing_prelabel"):
        flag_reason.setdefault(acc, []).append(f"Step 4 {r['status']}: anchor={r.get('anchor_eps')} llm={r.get('llm_primary')} cands={r.get('llm_candidates')}")
for acc, r in selfc.items():
    if not r["consistent"]:
        flag_reason.setdefault(acc, []).append("Step 5 A/B disagree: " + "; ".join(r["reasons"]))

flagged = sorted(flag_reason)
unflagged = sorted(a for a in cross if a not in flag_reason)
rng = random.Random(SEED)
fill = rng.sample(unflagged, max(0, min(TARGET - len(flagged), len(unflagged))))
batch = flagged + sorted(fill)
print(f"flagged={len(flagged)} random fill={len(fill)} batch={len(batch)}")

LEGEND = """# EPS spot-check batch

Legend for the **Verdict** column (leave blank or write `OK` to accept as-is):
- `DROP` - not an EPS mention / wrong span
- `TYPE=GAAP_DILUTED|GAAP_BASIC|NON_GAAP|GUIDANCE` - fix the type
- `VALUE=-0.42` - fix the numeric value (sign matters)
- `PERIOD=current_quarter|prior_year_quarter|prior_quarter|current_ytd|prior_ytd|full_year|guidance_period|other` - fix the period
- combine with `;` e.g. `TYPE=NON_GAAP; PERIOD=prior_year_quarter`

To add a mention the model missed, add a line under the filing's **Missed mentions** heading:
`ADD: <verbatim context copied from the document> | <value_text> | <TYPE> | <period_kind>`

Anchor = diluted EPS parsed from the company's 10-Q XBRL (Step 1). Primary = the model's current-quarter GAAP diluted value.
"""

md = [LEGEND]
hp = ["<html><head><meta charset='utf-8'><style>body{font-family:Segoe UI,Arial;font-size:13px;margin:24px} table{border-collapse:collapse;margin:8px 0 20px} "
      "td,th{border:1px solid #ccc;padding:4px 6px;vertical-align:top} th{background:#eee} mark{background:#ffe066;font-weight:bold} "
      ".flag{color:#b00;font-weight:bold} .ctx{font-family:Consolas,monospace;font-size:12px;white-space:pre-wrap;max-width:720px}</style></head><body>",
      "<h1>EPS spot-check batch</h1><p>Yellow = the labeled span. Edit verdicts in <code>spotcheck.md</code>.</p>"]
machine = []

for i, acc in enumerate(batch, 1):
    A = json.loads((ROOT / "data" / "prelabels" / "A" / f"{acc}.json").read_text(encoding="utf-8"))
    parsed = json.loads((ROOT / "data" / "parsed" / f"{acc}.json").read_text(encoding="utf-8"))
    text = parsed["text"]
    cr = cross[acc]
    why = flag_reason.get(acc, ["random sample (unflagged)"])
    head = f"## {i}. {A['company']}  ({acc})"
    meta = (f"Anchor (10-Q): **{cr.get('anchor_eps')}** ({cr.get('anchor_tag') or 'unanchored'}) | "
            f"Model primary: **{A['primary_gaap_diluted_eps']}** | mentions: {A['n_mentions']} | "
            f"Reason in batch: {' / '.join(why)}")
    md += ["", head, "", meta, "", "| ID | Span | Type | Period kind | Period | Value | Context (span in [[ ]]) | Verdict |",
           "|---|---|---|---|---|---|---|---|"]
    hp.append(f"<h2>{i}. {html.escape(A['company'])} <small>({acc})</small></h2><p class='{'flag' if acc in flag_reason else ''}'>{html.escape(meta.replace('**',''))}</p>")
    hp.append("<table><tr><th>ID</th><th>Span</th><th>Type</th><th>Period kind</th><th>Period</th><th>Value</th><th>Context</th></tr>")
    for j, m in enumerate(A["mentions"], 1):
        mid = f"{i}.{j}"
        if m["start"] is not None:
            s, e = m["start"], m["end"]
            lo, hi = max(0, s - 90), min(len(text), e + 60)
            ctx_md = (text[lo:s] + "[[" + text[s:e] + "]]" + text[e:hi]).replace("\n", " ⏎ ").replace("|", "¦")
            ctx_html = html.escape(text[lo:s]) + "<mark>" + html.escape(text[s:e]) + "</mark>" + html.escape(text[e:hi])
        else:
            ctx_md = "(UNRESOLVED) " + m["context"].replace("\n", " ⏎ ").replace("|", "¦")
            ctx_html = "(UNRESOLVED) " + html.escape(m["context"])
        md.append(f"| {mid} | `{m['span_text'] or m['value_text']}` | {m['type']} | {m['period_kind']} | {m['period']} | {m['value']} | {ctx_md} |  |")
        hp.append(f"<tr><td>{mid}</td><td><b>{html.escape(str(m['span_text'] or m['value_text']))}</b></td><td>{m['type']}</td><td>{m['period_kind']}</td>"
                  f"<td>{html.escape(m['period'])}</td><td>{m['value']}</td><td class='ctx'>{ctx_html}</td></tr>")
        machine.append({"id": mid, "accession": acc, "mention_index": j - 1, **{k: m[k] for k in ("value", "value_text", "type", "period", "period_kind", "start", "end", "span_text")}})
    hp.append("</table>")
    if acc in selfc and not selfc[acc]["consistent"]:
        B = json.loads((ROOT / "data" / "prelabels" / "B" / f"{acc}.json").read_text(encoding="utf-8"))
        bl = [f"{m['type']} {m['period_kind']} {m['value']} `{m['span_text'] or m['value_text']}`" for m in B["mentions"] if m["period_kind"] == "current_quarter"]
        md += ["", "Pass B (second prompt) current-quarter mentions for comparison: " + "; ".join(bl)]
        hp.append("<p><i>Pass B current-quarter mentions:</i> " + html.escape("; ".join(bl)) + "</p>")
    md += ["", "**Missed mentions** (add `ADD:` lines below):", ""]

(OUT / "spotcheck.md").write_text("\n".join(md), encoding="utf-8")
(OUT / "spotcheck.html").write_text("\n".join(hp) + "</body></html>", encoding="utf-8")
(OUT / "spotcheck.json").write_text(json.dumps({"batch": batch, "flagged": flagged, "random_fill": sorted(fill), "mentions": machine}, indent=1), encoding="utf-8")
print("batch:", batch)
print(f"rows: {len(machine)}")
