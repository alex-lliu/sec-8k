"""Step 5: self-consistency filter for filings without a 10-Q anchor.

Runs the extraction a second time with prompt variant B (different phrasing) on every unanchored filing
(plus anything Step 4 flagged), then compares pass A vs pass B:
  - primary current-quarter GAAP diluted value must agree
  - the set of (type, value) pairs for current-quarter mentions must agree
Any disagreement flags the filing. Writes data/selfconsistency.json.
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
cross = json.loads((ROOT / "data" / "crossval.json").read_text(encoding="utf-8"))
targets = [r["accession"] for r in cross if r["status"] in ("unanchored", "mismatch", "no_primary", "match_but_multiple_candidates")]
print(f"running variant B on {len(targets)} filings: {targets}")
subprocess.run([sys.executable, str(ROOT / "scripts" / "llm_extract.py"), "--variant", "B", "--only", ",".join(targets)], check=True)


def cq_pairs(pl):
    return sorted({(m["type"], m["value"]) for m in pl["mentions"] if m["period_kind"] == "current_quarter"})


def cq_values_by_type(pl):
    d = {}
    for m in pl["mentions"]:
        if m["period_kind"] == "current_quarter":
            d.setdefault(m["type"], set()).add(m["value"])
    return {k: sorted(v) for k, v in d.items()}


out = []
for acc in targets:
    A = json.loads((ROOT / "data" / "prelabels" / "A" / f"{acc}.json").read_text(encoding="utf-8"))
    B = json.loads((ROOT / "data" / "prelabels" / "B" / f"{acc}.json").read_text(encoding="utf-8"))
    pa, pb = A["primary_gaap_diluted_eps"], B["primary_gaap_diluted_eps"]
    ta, tb = cq_values_by_type(A), cq_values_by_type(B)
    reasons = []
    if pa != pb:
        reasons.append(f"primary GAAP diluted differs: A={pa} B={pb}")
    for t in sorted(set(ta) | set(tb)):
        if ta.get(t) != tb.get(t):
            reasons.append(f"{t} current-quarter values differ: A={ta.get(t)} B={tb.get(t)}")
    status = next(r["status"] for r in cross if r["accession"] == acc)
    out.append({"accession": acc, "company": A["company"], "step4_status": status,
                "primary_A": pa, "primary_B": pb, "cq_by_type_A": ta, "cq_by_type_B": tb,
                "n_mentions_A": A["n_mentions"], "n_mentions_B": B["n_mentions"],
                "consistent": not reasons, "reasons": reasons})
    print(f"{acc} {A['company'][:28]:28} {'OK  ' if not reasons else 'FLAG'} primary A={pa} B={pb} mentions A={A['n_mentions']} B={B['n_mentions']} {'; '.join(reasons)}")
(ROOT / "data" / "selfconsistency.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(f"\nconsistent: {sum(o['consistent'] for o in out)}/{len(out)}  flagged: {sum(not o['consistent'] for o in out)}")
