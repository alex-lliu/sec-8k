"""Steps 9 and 9B: evaluate the fine-tuned DeBERTa model and the zero-shot LLM baseline on the held-out
test split with the same metric.

PRIMARY METRIC: exact match of the filing's primary EPS value (current-quarter GAAP diluted EPS) against
the gold value from the company's 10-Q XBRL. Every test filing is anchored, so gold is independent of
any LLM output. Per filing each system emits at most one value:
  TP = emitted and equal to gold;  FP = emitted and wrong;  FN = gold not matched (wrong or nothing emitted)
  precision = TP/(TP+FP), recall = TP/(TP+FN), F1 = harmonic mean. A wrong answer counts as FP and FN.
Equality is numeric with sign, compared at 4 decimal places.

How each system produces its one value:
  DeBERTa  - token spans tagged EPS_GAAP_DILUTED -> signed values (eps_decode) -> PRIMARY_RULE, which was
             chosen on train+val gold before the test set was scored.
  Zero-shot LLM - the Step 3 prompt (variant A) returns typed mentions with a period; primary = most
             frequent current-quarter GAAP_DILUTED value, the same rule used to pre-label in Step 3.

SECONDARY METRIC: entity-level exact match on (char start, char end, type) for the 3 trained types.
Caveat: for test filings that were not spot-checked, gold mentions are LLM pre-labels, so this metric is
biased toward the LLM. It is reported for transparency, not as the headline.

Writes results/eval.json and results/eval_table.md.
"""
import json, math, sys, warnings
from pathlib import Path
from collections import Counter

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification

from eps_dataset import EPSWindowDataset, make_loader, TYPE2TAG
from step8_train import predict_documents, entity_scores

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
RES.mkdir(exist_ok=True)


def prf(pairs):
    """pairs: list of (pred or None, gold)."""
    tp = sum(p is not None and round(p, 4) == round(g, 4) for p, g in pairs)
    emitted = sum(p is not None for p, _ in pairs)
    fp = emitted - tp
    fn = len(pairs) - tp
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return {"n": len(pairs), "tp": tp, "fp": fp, "fn": fn, "emitted": emitted, "precision": p, "recall": r, "f1": f1}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    ph = k / n
    d = 1 + z * z / n
    c = ph + z * z / (2 * n)
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def llm_entities(acc, path):
    pl = json.loads(path.read_text(encoding="utf-8"))
    return pl, {(m["start"], m["end"], TYPE2TAG[m["type"]]) for m in pl["mentions"]
                if m["type"] in TYPE2TAG and m["start"] is not None}


def main(run="deberta_eps"):
    splits = json.loads((ROOT / "data" / "splits.json").read_text(encoding="utf-8"))
    test = splits["test"]
    assert not set(test) & (set(splits["train"]) | set(splits["val"])), "test overlaps train/val"

    # ---- DeBERTa ----
    ckpt = ROOT / "runs" / run / "best"
    tok = AutoTokenizer.from_pretrained(ckpt)
    model = AutoModelForTokenClassification.from_pretrained(ckpt).to("cuda")
    cfg = json.loads((ROOT / "runs" / run / "config.json").read_text())
    ds = EPSWindowDataset(test, tok, cfg["max_len"], cfg["stride"])
    dl, _ = make_loader(ds, tok, 8)
    preds, test_loss = predict_documents(model, ds, dl, "cuda")
    sc = entity_scores(ds, preds)
    deb_pairs = [(sc["per_doc"][a]["pred_primary"], sc["per_doc"][a]["gold_primary"]) for a in test]

    # ---- zero-shot LLM ----
    llm_pairs, llm_tp = [], Counter()
    rows = []
    for a in test:
        gold = json.loads((ROOT / "data" / "gold" / f"{a}.json").read_text(encoding="utf-8"))
        pl, P = llm_entities(a, ROOT / "data" / "zeroshot" / f"{a}.json")
        G = {(m["start"], m["end"], TYPE2TAG[m["type"]]) for m in gold["mentions"] if m["type"] in TYPE2TAG}
        llm_tp["tp"] += len(P & G); llm_tp["fp"] += len(P - G); llm_tp["fn"] += len(G - P)
        llm_pairs.append((pl["primary_gaap_diluted_eps"], gold["gold_primary_eps"]))
        rows.append({"accession": a, "company": gold["company"], "gold": gold["gold_primary_eps"],
                     "deberta": sc["per_doc"][a]["pred_primary"], "llm": pl["primary_gaap_diluted_eps"],
                     "llm_candidates": pl["primary_candidates"], "reviewed": gold["source"] == "spot-checked"})

    deb, llm = prf(deb_pairs), prf(llm_pairs)
    lp = llm_tp["tp"] / max(llm_tp["tp"] + llm_tp["fp"], 1)
    lr = llm_tp["tp"] / max(llm_tp["tp"] + llm_tp["fn"], 1)
    out = {
        "test_size_filings": len(test),
        "test_accessions": test,
        "primary_metric": {"deberta": deb, "zero_shot_llm": llm,
                           "deberta_acc_95ci_wilson": wilson(deb["tp"], deb["n"]),
                           "llm_acc_95ci_wilson": wilson(llm["tp"], llm["n"])},
        "secondary_entity_metric": {
            "deberta": {"p": sc["entity_p"], "r": sc["entity_r"], "f1": sc["entity_f1"], "tp": sc["tp"], "fp": sc["fp"], "fn": sc["fn"],
                        "per_type": sc["per_type"]},
            "zero_shot_llm": {"p": lp, "r": lr, "f1": 2 * lp * lr / (lp + lr) if lp + lr else 0.0, **llm_tp},
            "n_gold_entities": sc["tp"] + sc["fn"]},
        "deberta_test_token_loss": test_loss,
        "per_filing": rows,
        "deberta_checkpoint": ckpt.relative_to(ROOT).as_posix(), "deberta_best_epoch": json.loads((ckpt / "epoch.json").read_text()),
    }
    (RES / "eval.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")

    fmt = lambda x: "none" if x is None else f"{x:g}"
    md = [f"Test set: **{len(test)} filings** (held out before training; all anchored to 10-Q XBRL)", "",
          "| System | Precision | Recall | F1 | Correct / emitted / filings |", "|---|---|---|---|---|"]
    for name, r in (("Fine-tuned DeBERTa-v3-base", deb), ("Zero-shot LLM (claude-opus-5, Step 3 prompt)", llm)):
        md.append(f"| {name} | {r['precision']:.3f} | {r['recall']:.3f} | {r['f1']:.3f} | {r['tp']} / {r['emitted']} / {r['n']} |")
    md += ["", "| Filing | Gold (10-Q) | DeBERTa | Zero-shot LLM |", "|---|---|---|---|"]
    for r in rows:
        mark = lambda v: fmt(v) + ("" if v is not None and round(v, 4) == round(r["gold"], 4) else " ✗")
        md.append(f"| {r['company']} | {fmt(r['gold'])} | {mark(r['deberta'])} | {mark(r['llm'])} |")
    md += ["", "Secondary, entity-level exact span+type (biased toward the LLM; see caveat):", "",
           "| System | P | R | F1 |", "|---|---|---|---|",
           f"| DeBERTa | {sc['entity_p']:.3f} | {sc['entity_r']:.3f} | {sc['entity_f1']:.3f} |",
           f"| Zero-shot LLM | {lp:.3f} | {lr:.3f} | {out['secondary_entity_metric']['zero_shot_llm']['f1']:.3f} |"]
    (RES / "eval_table.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    print("\nDeBERTa per-type entity F1:", {t: round(v["f1"], 3) for t, v in sc["per_type"].items()})
    print("Wilson 95% CI on primary accuracy: DeBERTa", [round(x, 2) for x in out["primary_metric"]["deberta_acc_95ci_wilson"]],
          "LLM", [round(x, 2) for x in out["primary_metric"]["llm_acc_95ci_wilson"]])


if __name__ == "__main__":
    main(*sys.argv[1:])
