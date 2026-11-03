"""Step 4: compare the LLM pre-label's primary GAAP diluted EPS (current quarter) with the 10-Q anchor.

  match      -> auto-accepted
  mismatch   -> flagged for manual review
  no_primary -> the LLM found no current-quarter GAAP_DILUTED mention (flagged)
  unanchored -> no 10-Q anchor (handled in Step 5)
"""
import json, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
variant = sys.argv[1] if len(sys.argv) > 1 else "A"
PRE = ROOT / "data" / "prelabels" / variant

anchors = json.loads((ROOT / "data" / "anchors.json").read_text(encoding="utf-8"))
rows = []
for a in anchors:
    p = PRE / f"{a['accession']}.json"
    if not p.exists():
        rows.append({"accession": a["accession"], "company": a["company"], "status": "missing_prelabel"})
        continue
    pl = json.loads(p.read_text(encoding="utf-8"))
    prim = pl["primary_gaap_diluted_eps"]
    cands = pl["primary_candidates"]
    row = {"accession": a["accession"], "company": a["company"], "anchor_eps": a["anchor_eps"],
           "anchor_tag": a.get("anchor_tag"), "llm_primary": prim, "llm_candidates": cands,
           "n_mentions": pl["n_mentions"], "n_unresolved": pl["n_unresolved"]}
    if a["status"] != "anchored":
        row["status"] = "unanchored"
    elif prim is None:
        row["status"] = "no_primary"
    elif abs(prim - a["anchor_eps"]) < 1e-6 and len(cands) == 1:
        row["status"] = "match"
    elif abs(prim - a["anchor_eps"]) < 1e-6:
        row["status"] = "match_but_multiple_candidates"
    else:
        row["status"] = "mismatch"
    rows.append(row)

(ROOT / "data" / "crossval.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
print(Counter(r["status"] for r in rows))
for r in rows:
    if r["status"] not in ("match", "unanchored"):
        print(f"  {r['status']:30} {r['accession']} {r['company'][:30]:30} anchor={r.get('anchor_eps')} llm={r.get('llm_primary')} cands={r.get('llm_candidates')}")
print("\nunresolved spans total:", sum(r.get("n_unresolved", 0) for r in rows))
