"""Step 2: parse each 8-K into one document, `[ITEM 2.02]` then `[EXHIBIT 99.1]`, in data/parsed/.

The local files hold only Exhibit 99.1, so the 8-K body is fetched from EDGAR for the Item 2.02 text.
Table rows stay on one line with cells separated by ' | ', so EPS values stay next to their row labels.
All later character offsets refer to the `text` field.
"""
import json, re, glob
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Comment

from step1_anchor_fetch import get, submissions, recent_rows, ROOT, FILINGS

PARSED = ROOT / "data" / "parsed"
PARSED.mkdir(parents=True, exist_ok=True)

BLOCK = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "table", "ul", "ol",
         "section", "article", "header", "footer", "blockquote", "hr", "pre", "title", "tbody", "thead"}
SKIP = {"script", "style", "head", "meta", "link"}


def _inline_text(node):
    parts = []

    def walk(n):
        for ch in n.children:
            if isinstance(ch, NavigableString):
                if not isinstance(ch, Comment):
                    parts.append(str(ch))
            elif ch.name in SKIP:
                continue
            elif ch.name in BLOCK or ch.name in ("td", "th", "tr"):
                parts.append(" ")
                walk(ch)
                parts.append(" ")
            else:
                walk(ch)

    walk(node)
    return re.sub(r"\s+", " ", "".join(parts).replace("\xa0", " ")).strip()


def _row_text(tr):
    cells = [_inline_text(td) for td in tr.find_all(["td", "th"], recursive=False)]
    if not cells:  # cells nested in odd wrappers
        cells = [_inline_text(td) for td in tr.find_all(["td", "th"])]
    cells = [c for c in cells if c]
    row = " | ".join(cells)
    # re-join split currency / parenthesis / percent cells:  "$ | 0.71" -> "$0.71", "(1,345 | )" -> "(1,345)"
    row = re.sub(r"\$ \| (?=[\d(])", "$", row)
    row = re.sub(r"(?<=[\d.]) \| \)", ")", row)
    row = re.sub(r"(?<=[\d)]) \| %", "%", row)
    row = re.sub(r"(?<=[\d)]) \| \)%", ")%", row)
    return row


def html_to_text(html):
    # strip the EDGAR SGML wrapper (<type>, <sequence>, <filename>, <description>) if present
    m = re.search(r"<text>(.*)</text>", html, re.S | re.I)
    if m:
        html = m.group(1)
    html = re.sub(r"<!DOCTYPE[^>]*>", "", html, flags=re.I)
    soup = BeautifulSoup(html, "lxml")
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    for t in soup.find_all(list(SKIP)):
        t.decompose()
    for t in soup.find_all(style=re.compile(r"display\s*:\s*none", re.I)):
        t.decompose()
    for t in soup.find_all("ix:header"):
        t.decompose()
    out = []

    def walk(node):
        for ch in node.children:
            if isinstance(ch, NavigableString):
                out.append(str(ch))
            elif ch.name == "tr":
                out.append("\n" + _row_text(ch) + "\n")
            elif ch.name in BLOCK:
                out.append("\n")
                walk(ch)
                out.append("\n")
            else:
                walk(ch)

    walk(soup)
    txt = "".join(out).replace("\xa0", " ").replace("​", "").replace("﻿", "")
    lines = []
    for line in txt.split("\n"):
        line = re.sub(r"[ \t\r\f\v]+", " ", line).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


ITEM_RE = re.compile(r"(?im)^\s*item\s*(\d\.\d{2})(?!\d)[\s.:;\-]*")


def extract_item_202(text):
    """Return the Item 2.02 section body. Handles table-of-contents entries (takes the longest
    occurrence) and combined headings such as 'Item 2.02; Item 7.01' (extends through the next section)."""
    ms = list(ITEM_RE.finditer(text))
    if not ms:
        return None
    bounds = [(m, m.start(), ms[i + 1].start() if i + 1 < len(ms) else len(text)) for i, m in enumerate(ms)]
    best = None
    for i, (m, s, e) in enumerate(bounds):
        if m.group(1) != "2.02":
            continue
        end = e
        j = i
        # if the section body is only a heading, extend through following headings until real text appears
        while len(text[bounds[j][0].end():end].strip()) < 120 and j + 1 < len(bounds):
            j += 1
            end = bounds[j][2]
        sec = text[s:end]
        sig = re.search(r"(?im)^\s*signatures?\s*$", sec)
        if sig:
            sec = sec[:sig.start()]
        sec = sec.strip()
        if best is None or len(sec) > len(best):
            best = sec
    return best


def main():
    anchors = {r["accession"]: r for r in json.loads((ROOT / "data" / "anchors.json").read_text(encoding="utf-8"))}
    summary = []
    for path in sorted(glob.glob(str(FILINGS / "*.html"))):
        acc = Path(path).stem
        a = anchors[acc]
        cik = a["cik"]
        rows = recent_rows(submissions(cik))
        row = next(r for r in rows if r["accessionNumber"] == acc)
        url8k = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/{row['primaryDocument']}"
        body_text = html_to_text(get(url8k))
        item = extract_item_202(body_text)
        ex_html = Path(path).read_text(encoding="utf-8", errors="ignore")
        ex_text = html_to_text(ex_html)
        item_str = item if item else "(Item 2.02 not found in 8-K body)"
        text = f"[ITEM 2.02]\n{item_str}\n\n[EXHIBIT 99.1]\n{ex_text}"
        rec = {"accession": acc, "cik": cik, "company": a["company"], "8k_url": url8k,
               "item_202_found": item is not None, "item_202_text": item, "ex991_text": ex_text,
               "ex991_chars": len(ex_text), "text": text}
        (PARSED / f"{acc}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
        summary.append((acc, a["company"], item is not None, len(item or ""), len(ex_text)))
        print(f"{acc} | {a['company'][:30]:30} | item2.02={'Y' if item else 'N'} ({len(item or ''):5d} ch) | ex99.1={len(ex_text):6d} ch")
    n = sum(s[2] for s in summary)
    print(f"\nItem 2.02 found in {n}/{len(summary)} 8-K bodies; EX-99.1 text extracted for {len(summary)}/{len(summary)}")


if __name__ == "__main__":
    main()
