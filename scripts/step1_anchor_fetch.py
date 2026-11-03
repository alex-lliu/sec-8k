"""Step 1: for each local 8-K (EX-99.1) filing, locate the matching 10-Q on EDGAR and
parse its inline XBRL for us-gaap:EarningsPerShareDiluted (3-month, consolidated context).

Outputs data/anchors.json with one record per filing:
  accession, cik, company, form8k_date, tenq_accession, tenq_report_date, anchor_eps, status, reason
"""
import json, os, re, time, glob, warnings
from datetime import date, datetime, timedelta
from pathlib import Path
import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

ROOT = Path(__file__).resolve().parent.parent
FILINGS = ROOT / "Training_Filings"
CACHE = ROOT / "data" / "cache"
CACHE.mkdir(parents=True, exist_ok=True)
_last = [0.0]


def sec_headers():
    ua = os.environ.get("SEC_USER_AGENT")
    if not ua:
        raise SystemExit('Set SEC_USER_AGENT to "Your Name your@email.com". The SEC requires a contact in the User-Agent.')
    return {"User-Agent": ua, "Accept-Encoding": "gzip, deflate"}


def get(url):
    key = re.sub(r"[^A-Za-z0-9._-]", "_", url.split("://", 1)[1])[-180:]
    p = CACHE / key
    if p.exists():
        return p.read_text(encoding="utf-8", errors="ignore")
    dt = time.time() - _last[0]
    if dt < 0.12:
        time.sleep(0.12 - dt)
    r = requests.get(url, headers=sec_headers(), timeout=60)
    _last[0] = time.time()
    r.raise_for_status()
    p.write_bytes(r.content)
    return r.text


def load_index(accessions):
    m = {}
    for q in ["2020Q2", "2020Q1", "2020Q3"]:
        p = CACHE / f"form_{q}.idx"
        if not p.exists():
            yr, qtr = q[:4], q[5]
            p.write_text(get(f"https://www.sec.gov/Archives/edgar/full-index/{yr}/QTR{qtr}/form.idx"), encoding="utf-8")
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line.startswith("8-K"):
                continue
            mm = re.search(r"edgar/data/(\d+)/(\d{10}-\d{2}-\d{6})\.txt", line)
            if mm:
                cik, acc = mm.group(1), mm.group(2)
                name = line[12:74].strip()
                m[acc] = (cik, name)
        if all(a in m for a in accessions):
            break
    return m


def submissions(cik):
    return json.loads(get(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json"))


def recent_rows(sub):
    r = sub["filings"]["recent"]
    rows = [dict(zip(r.keys(), vals)) for vals in zip(*r.values())]
    for extra in sub["filings"].get("files", []):
        ex = json.loads(get("https://data.sec.gov/submissions/" + extra["name"]))
        rows += [dict(zip(ex.keys(), vals)) for vals in zip(*ex.values())]
    return rows


def find_10q(rows, acc):
    eight_k = next((r for r in rows if r["accessionNumber"] == acc), None)
    if not eight_k:
        return None, None, "8-K accession not found in submissions"
    fdate = datetime.strptime(eight_k["filingDate"], "%Y-%m-%d").date()
    cands = []
    for r in rows:
        if r["form"] not in ("10-Q", "10-Q/A"):
            continue
        rd = datetime.strptime(r["reportDate"], "%Y-%m-%d").date() if r["reportDate"] else None
        fd = datetime.strptime(r["filingDate"], "%Y-%m-%d").date()
        if rd and fdate - timedelta(days=75) <= rd <= fdate and fd >= fdate - timedelta(days=1):
            cands.append(r)
    if not cands:
        return eight_k, None, "no 10-Q with period end within 75 days before the 8-K"
    cands.sort(key=lambda r: (r["form"] != "10-Q", r["filingDate"]))  # prefer original 10-Q, earliest
    return eight_k, cands[0], None


warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

ACCEPT_TAGS = ["us-gaap:EarningsPerShareDiluted", "us-gaap:EarningsPerShareBasicAndDiluted"]


def _num(txt, scale, sign, nil):
    txt = txt.replace(",", "").replace("$", "").strip()
    if nil or txt in ("", "-", "—", "–"):
        return None
    if txt.startswith("(") and txt.endswith(")"):
        txt = txt[1:-1]
    v = float(txt) * (10 ** int(scale or 0))
    return -v if sign == "-" else v


def facts_from_inline(html):
    """Returns (contexts, facts). contexts: id -> (start, end, [axis names]); facts: [(tag, ctxid, value)]"""
    soup = BeautifulSoup(html, "lxml")
    ctx = {}
    for c in soup.find_all(re.compile(r"(xbrli:)?context$")):
        sd = c.find(re.compile(r"(xbrli:)?startdate$"))
        ed = c.find(re.compile(r"(xbrli:)?enddate$"))
        axes = [m.get("dimension") for m in c.find_all(re.compile(r"(xbrldi:)?(explicitmember|typedmember)$"))]
        ctx[c.get("id")] = (sd.text.strip() if sd else None, ed.text.strip() if ed else None, axes)
    facts, tags = [], set()
    for f in soup.find_all("ix:nonfraction"):
        n = f.get("name", "")
        if "PerShare" in n or "PerDiluted" in n or "PerBasic" in n:
            tags.add(n)
        if n in ACCEPT_TAGS:
            v = _num(f.get_text(strip=True), f.get("scale"), f.get("sign"), f.get("xsi:nil") == "true")
            facts.append((n, f.get("contextref"), v))
    return ctx, facts, sorted(tags)


def facts_from_instance(xml):
    soup = BeautifulSoup(xml, "xml")
    ctx = {}
    for c in soup.find_all("context"):
        sd, ed = c.find("startDate"), c.find("endDate")
        axes = [m.get("dimension") for m in c.find_all(["explicitMember", "typedMember"])]
        ctx[c.get("id")] = (sd.text.strip() if sd else None, ed.text.strip() if ed else None, axes)
    facts, tags = [], set()
    for f in soup.find_all(True):
        if not f.prefix or f.prefix == "xbrli" or f.get("contextRef") is None:
            continue
        n = f"{f.prefix}:{f.name}"
        if "PerShare" in n or "PerDiluted" in n or "PerBasic" in n:
            tags.add(n)
        if n in ACCEPT_TAGS:
            v = _num(f.get_text(strip=True), 0, None, f.get("xsi:nil") == "true")
            facts.append((n, f.get("contextRef"), v))
    return ctx, facts, sorted(tags)


def pick_anchor(ctx, facts, report_date):
    """Choose the quarterly diluted EPS. Prefers EarningsPerShareDiluted with an undimensioned context;
    accepts class-of-stock-dimensioned facts only if every class reports the same value."""
    for tag in ACCEPT_TAGS:
        plain, by_class = [], []
        for n, cid, v in facts:
            if n != tag or v is None:
                continue
            sd, ed, axes = ctx.get(cid, (None, None, None))
            if not sd or not ed:
                continue
            d0, d1 = date.fromisoformat(sd), date.fromisoformat(ed)
            if d1 != report_date or not (80 <= (d1 - d0).days <= 100):
                continue
            v = round(v, 4)
            if not axes:
                plain.append(v)
            elif axes == ["us-gaap:StatementClassOfStockAxis"]:
                by_class.append(v)
        if plain:
            u = sorted(set(plain))
            return (u[0], tag, None) if len(u) == 1 else (None, tag, f"conflicting values {u}")
        if by_class:
            u = sorted(set(by_class))
            if len(u) == 1:
                return u[0], tag, "class-of-stock dimension only; all classes report the same value"
            return None, tag, f"per-class values disagree {u}"
    return None, None, None


def instance_url(cik, accnd):
    items = json.loads(get(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accnd}/index.json"))["directory"]["item"]
    xml = [i["name"] for i in items if i["name"].lower().endswith(".xml")
           and not any(k in i["name"].lower() for k in ("_cal", "_def", "_lab", "_pre", "filingsummary"))]
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accnd}/{xml[0]}" if xml else None


def main():
    files = sorted(glob.glob(str(FILINGS / "*.html")))
    accessions = [Path(p).stem for p in files]
    idx = load_index(accessions)
    out = []
    for path in files:
        acc = Path(path).stem
        rec = {"file": Path(path).name, "accession": acc, "cik": None, "company": None,
               "form8k_date": None, "tenq_accession": None, "tenq_report_date": None, "tenq_url": None,
               "anchor_eps": None, "status": "unanchored", "reason": None, "other_eps_tags": None}
        try:
            if acc not in idx:
                rec["reason"] = "accession not in 2020 EDGAR 8-K index"
                out.append(rec); print(rec); continue
            cik, name = idx[acc]
            rec.update(cik=cik, company=name)
            sub = submissions(cik)
            rows = recent_rows(sub)
            ek, tq, why = find_10q(rows, acc)
            if ek:
                rec["form8k_date"] = ek["filingDate"]
            if not tq:
                rec["reason"] = why
                out.append(rec)
                print(f"{acc} | {name} | unanchored | {why}")
                continue
            rec["tenq_accession"] = tq["accessionNumber"]
            rec["tenq_report_date"] = tq["reportDate"]
            rd = date.fromisoformat(tq["reportDate"])
            accnd = tq["accessionNumber"].replace("-", "")
            url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accnd}/{tq['primaryDocument']}"
            rec["tenq_url"] = url
            html = get(url)
            if re.search(r"<ix:nonfraction", html, re.I):
                ctx, facts, tags = facts_from_inline(html)
                rec["xbrl_source"] = "inline"
            else:
                iurl = instance_url(cik, accnd)
                rec["tenq_url"] = iurl or url
                if not iurl:
                    rec["reason"] = "10-Q has neither inline XBRL nor an XBRL instance file"
                    out.append(rec); print(f"{acc} | {name} | unanchored | {rec['reason']}"); continue
                ctx, facts, tags = facts_from_instance(get(iurl))
                rec["xbrl_source"] = "instance-xml (10-Q predates inline XBRL for this filer)"
            rec["other_eps_tags"] = tags
            val, tag, note = pick_anchor(ctx, facts, rd)
            rec["anchor_tag"], rec["anchor_note"] = tag, note
            if val is not None:
                rec["anchor_eps"] = val
                rec["status"] = "anchored"
            elif tag:
                rec["reason"] = f"{tag}: {note}"
            else:
                rec["reason"] = ("10-Q found but no us-gaap:EarningsPerShareDiluted / EarningsPerShareBasicAndDiluted "
                                 "fact for the 3-month consolidated context ending on the report date")
        except Exception as e:
            rec["reason"] = f"error: {type(e).__name__}: {e}"
        out.append(rec)
        print(f"{acc} | {rec['company']} | {rec['status']} | eps={rec['anchor_eps']} | {rec['reason'] or ''}")
    (ROOT / "data" / "anchors.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    n = sum(r["status"] == "anchored" for r in out)
    print(f"\nANCHORED: {n}/{len(out)}   UNANCHORED: {len(out)-n}")


if __name__ == "__main__":
    main()
