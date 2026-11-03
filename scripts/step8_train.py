"""Step 8: fine-tune microsoft/deberta-v3-base for EPS token classification on a single consumer GPU.

Defaults sized for an RTX 4050 Laptop (6 GB): 512-token windows, micro-batch 4 (4.7 GiB peak in bf16),
gradient accumulation 2 (effective batch 8). Train/val loss are printed as training runs and written to
runs/<name>/metrics.csv; the best epoch by validation entity-F1 is saved to runs/<name>/best/.

  python scripts/step8_train.py --epochs 15
"""
import argparse, csv, json, math, os, random, time, warnings
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, get_linear_schedule_with_warmup

from eps_dataset import EPSWindowDataset, make_loader, LABELS, L2I, TYPE2TAG, IGNORE
from eps_decode import bio_spans, decode_mentions, pick_primary, PRIMARY_RULE

warnings.filterwarnings("ignore")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

ROOT = Path(__file__).resolve().parent.parent
MODEL_NAME = "microsoft/deberta-v3-base"


def set_seed(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)


@torch.no_grad()
def predict_documents(model, ds, loader, device):
    """Run every window, average logits for tokens covered by overlapping windows, return per-doc
    token label ids plus mean loss over labeled tokens."""
    model.eval()
    sums = {acc: torch.zeros(d["n_tokens"], len(LABELS)) for acc, d in ds.docs.items()}
    cnts = {acc: torch.zeros(d["n_tokens"], 1) for acc, d in ds.docs.items()}
    tot_loss, tot_tok = 0.0, 0
    for batch in loader:
        ids = batch["input_ids"].to(device); att = batch["attention_mask"].to(device); lab = batch["labels"].to(device)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            out = model(input_ids=ids, attention_mask=att)
        logits = out.logits.float()
        mask = lab != IGNORE
        if mask.any():
            tot_loss += torch.nn.functional.cross_entropy(logits[mask], lab[mask], reduction="sum").item()
            tot_tok += int(mask.sum())
        logits = logits.cpu()
        for i, meta in enumerate(batch["meta"]):
            n = meta["tok_end"] - meta["tok_start"]
            sums[meta["accession"]][meta["tok_start"]:meta["tok_end"]] += logits[i, 1:1 + n]
            cnts[meta["accession"]][meta["tok_start"]:meta["tok_end"]] += 1
    preds = {acc: (sums[acc] / cnts[acc].clamp(min=1)).argmax(-1).tolist() for acc in sums}
    return preds, (tot_loss / max(tot_tok, 1)) if tot_tok else None


def entity_scores(ds, preds):
    """Entity-level exact match on (char start, char end, type) after tightening to the number,
    plus primary-EPS exact match against the filing's gold primary value."""
    tp = fp = fn = 0
    per_type = {t: [0, 0, 0] for t in TYPE2TAG.values()}
    prim_ok = prim_n = 0
    per_doc = {}
    for acc, d in ds.docs.items():
        text = d["text"]
        spans = bio_spans(preds[acc], d["offsets"], LABELS)
        pred_m = decode_mentions(text, spans)
        P = {(m["start"], m["end"], m["type"]) for m in pred_m}
        G = {(m["start"], m["end"], TYPE2TAG[m["type"]]) for m in d["gold"]["mentions"] if m["type"] in TYPE2TAG}
        tp += len(P & G); fp += len(P - G); fn += len(G - P)
        for t in per_type:
            Pt = {x for x in P if x[2] == t}; Gt = {x for x in G if x[2] == t}
            per_type[t][0] += len(Pt & Gt); per_type[t][1] += len(Pt - Gt); per_type[t][2] += len(Gt - Pt)
        prim = pick_primary(text, pred_m, PRIMARY_RULE)
        gold_prim = d["gold"]["gold_primary_eps"]
        prim_n += 1
        prim_ok += int(prim is not None and abs(prim - gold_prim) < 1e-9)
        per_doc[acc] = {"pred_primary": prim, "gold_primary": gold_prim, "pred_mentions": pred_m}
    f = lambda tp, fp, fn: (tp / (tp + fp) if tp + fp else 0.0, tp / (tp + fn) if tp + fn else 0.0)
    p, r = f(tp, fp, fn)
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    pt = {}
    for t, (a, b, c) in per_type.items():
        pp, rr = f(a, b, c)
        pt[t] = {"p": pp, "r": rr, "f1": 2 * pp * rr / (pp + rr) if pp + rr else 0.0, "support": a + c}
    return {"entity_p": p, "entity_r": r, "entity_f1": f1, "tp": tp, "fp": fp, "fn": fn,
            "primary_acc": prim_ok / max(prim_n, 1), "primary_correct": prim_ok, "n_docs": prim_n,
            "per_type": pt, "per_doc": per_doc}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=15)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--batch_size", type=int, default=4)
    ap.add_argument("--grad_accum", type=int, default=2)
    ap.add_argument("--max_len", type=int, default=512)
    ap.add_argument("--stride", type=int, default=128)
    ap.add_argument("--neg_fraction", type=float, default=0.3)
    ap.add_argument("--warmup", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--log_every", type=int, default=10)
    ap.add_argument("--name", default="deberta_eps")
    args = ap.parse_args()

    set_seed(args.seed)
    device = "cuda"
    out = ROOT / "runs" / args.name
    out.mkdir(parents=True, exist_ok=True)
    (out / "config.json").write_text(json.dumps(vars(args), indent=1))
    splits = json.loads((ROOT / "data" / "splits.json").read_text(encoding="utf-8"))

    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
    train_ds = EPSWindowDataset(splits["train"], tok, args.max_len, args.stride)
    val_ds = EPSWindowDataset(splits["val"], tok, args.max_len, args.stride)
    train_dl, sampler = make_loader(train_ds, tok, args.batch_size, train=True, neg_fraction=args.neg_fraction, seed=args.seed)
    val_dl, _ = make_loader(val_ds, tok, 8)

    model = AutoModelForTokenClassification.from_pretrained(
        MODEL_NAME, num_labels=len(LABELS), id2label=dict(enumerate(LABELS)), label2id=L2I).to(device)
    no_decay = ("bias", "LayerNorm.weight")
    groups = [{"params": [p for n, p in model.named_parameters() if not any(k in n for k in no_decay)], "weight_decay": 0.01},
              {"params": [p for n, p in model.named_parameters() if any(k in n for k in no_decay)], "weight_decay": 0.0}]
    opt = torch.optim.AdamW(groups, lr=args.lr)
    steps_per_epoch = math.ceil(len(sampler) / args.batch_size / args.grad_accum)
    total = steps_per_epoch * args.epochs
    sched = get_linear_schedule_with_warmup(opt, int(args.warmup * total), total)

    print(f"train: {len(splits['train'])} filings, {len(train_ds)} windows ({len(sampler)} sampled/epoch) | "
          f"val: {len(splits['val'])} filings, {len(val_ds)} windows | {steps_per_epoch} optimizer steps/epoch, {total} total",
          flush=True)
    fields = ["epoch", "step", "train_loss", "val_loss", "val_entity_p", "val_entity_r", "val_entity_f1", "val_primary_acc", "lr", "secs"]
    with open(out / "metrics.csv", "w", newline="") as f:
        csv.writer(f).writerow(fields)
    steplog = open(out / "train_steps.csv", "w", newline="")
    sw = csv.writer(steplog); sw.writerow(["step", "epoch", "train_loss"])

    best = (-1.0, float("inf"))
    step, t0 = 0, time.time()
    for epoch in range(1, args.epochs + 1):
        model.train(); sampler.set_epoch(epoch)
        run_loss, run_n, ep_loss, ep_n = 0.0, 0, 0.0, 0
        opt.zero_grad(set_to_none=True)
        for i, batch in enumerate(train_dl):
            ids = batch["input_ids"].to(device); att = batch["attention_mask"].to(device); lab = batch["labels"].to(device)
            with torch.autocast("cuda", dtype=torch.bfloat16):
                loss = model(input_ids=ids, attention_mask=att, labels=lab).loss
            (loss / args.grad_accum).backward()
            run_loss += loss.item(); run_n += 1; ep_loss += loss.item(); ep_n += 1
            if (i + 1) % args.grad_accum == 0 or i + 1 == len(train_dl):
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step(); sched.step(); opt.zero_grad(set_to_none=True); step += 1
                if step % args.log_every == 0:
                    print(f"  epoch {epoch:2d} step {step:4d}/{total} | train_loss {run_loss / run_n:.4f} | lr {sched.get_last_lr()[0]:.2e}", flush=True)
                    sw.writerow([step, epoch, run_loss / run_n]); steplog.flush()
                    run_loss, run_n = 0.0, 0
        preds, val_loss = predict_documents(model, val_ds, val_dl, device)
        sc = entity_scores(val_ds, preds)
        row = [epoch, step, ep_loss / ep_n, val_loss, sc["entity_p"], sc["entity_r"], sc["entity_f1"], sc["primary_acc"],
               sched.get_last_lr()[0], time.time() - t0]
        with open(out / "metrics.csv", "a", newline="") as f:
            csv.writer(f).writerow(row)
        tag = ""
        if (sc["entity_f1"], -val_loss) > (best[0], -best[1]):
            best = (sc["entity_f1"], val_loss)
            model.save_pretrained(out / "best"); tok.save_pretrained(out / "best")
            (out / "best" / "epoch.json").write_text(json.dumps({"epoch": epoch, "val_entity_f1": sc["entity_f1"], "val_loss": val_loss}))
            tag = "  <- best, saved"
        print(f"EPOCH {epoch:2d} | train_loss {ep_loss / ep_n:.4f} | val_loss {val_loss:.4f} | val entity P/R/F1 "
              f"{sc['entity_p']:.3f}/{sc['entity_r']:.3f}/{sc['entity_f1']:.3f} | val primary {sc['primary_correct']}/{sc['n_docs']} "
              f"| {time.time() - t0:.0f}s{tag}", flush=True)
    steplog.close()
    print(f"DONE best val entity F1 {best[0]:.3f} (val loss {best[1]:.4f}) -> {out / 'best'}", flush=True)


if __name__ == "__main__":
    main()
