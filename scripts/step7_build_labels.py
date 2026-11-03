"""Step 7a: build the adjudicated label set and the train / val / test split.

Adjudicated set (per the project spec: "anchored-matched + my spot-check corrections"):
  - the 13 spot-checked filings, with the reviewer's verdicts from data/spotcheck/spotcheck.md applied
  - every other filing whose LLM primary value matched its 10-Q anchor in Step 4 (labels taken as-is,
    plus the documented overrides in data/label_overrides.json)
Filings that are neither (unanchored and not reviewed) are excluded and listed in the output.

Split: the test set is drawn ONLY from anchored filings, so its gold primary EPS is the independent
10-Q XBRL value rather than anything an LLM produced. Seeded; written to data/splits.json before training.

Outputs: data/gold/<accession>.json, data/gold_summary.json, data/splits.json
"""
import json, re, random
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
GOLD = D / "gold"
GOLD.mkdir(exist_ok=True)
SEED = 42
N_TEST = 12
N_VAL = 5

anchors = {r["accession"]: r for r in json.loads((D / "anchors.json").read_text(encoding="utf-8"))}
cross = {r["accession"]: r for r in json.loads((D / "crossval.json").read_text(encoding="utf-8"))}
spot = json.loads((D / "spotcheck" / "spotcheck.json").read_text(encoding="utf-8"))
overrides = json.loads((D / "label_overrides.json").read_text(encoding="utf-8"))

# ---- parse reviewer verdicts ----
verdicts, adds = {}, {}
cur_filing = None
id_to_acc = {m["id"]: m["accession"] for m in spot["mentions"]}
for line in (D / "spotcheck" / "spotcheck.md").read_text(encoding="utf-8").split("\n"):
    m = re.match(r"## (\d+)\. .*\((\d{10}-\d{2}-\d{6})\)", line)
    if m:
        cur_filing = m.group(2)
    if re.match(r"\| \d+\.\d+ \|", line):
        cells = line.strip().strip("|").split("|")
        v = cells[-1].strip()
        if v and v.upper() != "OK":
            verdicts[cells[0].strip()] = v
    if line.strip().upper().startswith("ADD:"):
        adds.setdefault(cur_filing, []).append(line.strip()[4:].strip())


def apply_verdict(m, v):
    out = dict(m)
    for part in [p.strip() for p in v.split(";") if p.strip()]:
        if part.upper() == "DROP":
            return None
        k, _, val = part.partition("=")
        k = k.strip().upper()
        if k == "TYPE":
            out["type"] = val.strip()
        elif k == "VALUE":
            out["value"] = float(val)
        elif k == "PERIOD":
            out["period_kind"] = val.strip()
        else:
            raise ValueError(f"unknown verdict '{part}'")
    out["reviewed_change"] = v
    return out


def primary_from(mentions):
    vals = [m["value"] for m in mentions if m["type"] == "GAAP_DILUTED" and m["period_kind"] == "current_quarter"]
    return Counter(vals).most_common(1)[0][0] if vals else None


summary, members = [], []
for acc in sorted(anchors):
    a, c = anchors[acc], cross[acc]
    pre = json.loads((D / "prelabels" / "A" / f"{acc}.json").read_text(encoding="utf-8"))
    text = json.loads((D / "parsed" / f"{acc}.json").read_text(encoding="utf-8"))["text"]
    reviewed = acc in spot["batch"]
    if reviewed:
        source = "spot-checked"
    elif c["status"] == "match":
        source = "anchor-matched"
    else:
        summary.append({"accession": acc, "company": a["company"], "included": False,
                        "reason": f"step4={c['status']}, not in spot-check batch"})
        continue

    drop_idx = set(overrides.get(acc, {}).get("drop_mention_indices", []))
    gold = []
    for i, m in enumerate(pre["mentions"]):
        base = {k: m[k] for k in ("value", "value_text", "type", "period", "period_kind", "start", "end", "span_text")}
        base["source"] = source
        if reviewed:
            sid = next((x["id"] for x in spot["mentions"] if x["accession"] == acc and x["mention_index"] == i), None)
            if sid in verdicts:
                base = apply_verdict(base, verdicts[sid])
                if base is None:
                    continue
        if i in drop_idx:
            continue
        if base["start"] is None:
            raise RuntimeError(f"unresolved span in gold {acc} #{i}")
        assert text[base["start"]:base["end"]] == base["span_text"]
        gold.append(base)
    if acc in adds:
        raise NotImplementedError(f"ADD lines present for {acc}; handle before training")

    gold.sort(key=lambda m: m["start"])
    prim = primary_from(gold)
    anchored = a["status"] == "anchored"
    gold_primary = a["anchor_eps"] if anchored else prim
    rec = {"accession": acc, "company": a["company"], "source": source, "anchored": anchored,
           "gold_primary_eps": gold_primary, "gold_primary_source": "10-Q XBRL" if anchored else "adjudicated label",
           "label_primary_eps": prim, "n_mentions": len(gold),
           "n_by_type": dict(Counter(m["type"] for m in gold)), "mentions": gold}
    if anchored and (prim is None or abs(prim - a["anchor_eps"]) > 1e-9):
        raise RuntimeError(f"{acc} {a['company']}: adjudicated labels give primary {prim} but anchor is {a['anchor_eps']}")
    (GOLD / f"{acc}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
    members.append(rec)
    summary.append({"accession": acc, "company": a["company"], "included": True, "source": source,
                    "anchored": anchored, "gold_primary_eps": gold_primary, "n_mentions": len(gold)})

# ---- split ----
rng = random.Random(SEED)
anch = sorted(m["accession"] for m in members if m["anchored"])
test = sorted(rng.sample(anch, N_TEST))
rest = sorted(m["accession"] for m in members if m["accession"] not in test)
val = sorted(rng.sample(rest, N_VAL))
train = sorted(a for a in rest if a not in val)
splits = {"seed": SEED, "train": train, "val": val, "test": test,
          "excluded": [s["accession"] for s in summary if not s["included"]]}
(D / "splits.json").write_text(json.dumps(splits, indent=1), encoding="utf-8")
(D / "gold_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")

print(f"reviewer verdicts applied: {len(verdicts)}  overrides: { {k: len(v['drop_mention_indices']) for k, v in overrides.items()} }")
print(f"included: {len(members)}  (spot-checked {sum(m['source']=='spot-checked' for m in members)}, "
      f"anchor-matched {sum(m['source']=='anchor-matched' for m in members)})")
print("excluded:", [(s["company"], s["reason"]) for s in summary if not s["included"]])
print(f"split: train={len(train)} val={len(val)} test={len(test)}")
by = {m["accession"]: m for m in members}
for name in ("test", "val"):
    print(f"  {name}: " + ", ".join(f"{by[a]['company'][:22]}({by[a]['gold_primary_eps']})" for a in splits[name]))
tot = Counter()
for m in members:
    tot.update(m["n_by_type"])
print("gold mentions by type:", dict(tot), " total", sum(tot.values()))
