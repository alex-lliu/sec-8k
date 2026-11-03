"""Plot train (per logged step and per epoch) and validation loss, plus validation entity F1, from a run."""
import csv, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
run = sys.argv[1] if len(sys.argv) > 1 else "deberta_eps"
d = ROOT / "runs" / run
steps = list(csv.DictReader(open(d / "train_steps.csv")))
eps = list(csv.DictReader(open(d / "metrics.csv")))

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
a1.plot([int(r["step"]) for r in steps], [float(r["train_loss"]) for r in steps], color="#9aa5b1", lw=1, label="train (every 10 steps)")
a1.plot([int(r["step"]) for r in eps], [float(r["train_loss"]) for r in eps], "o-", color="#2563eb", label="train (epoch mean)")
a1.plot([int(r["step"]) for r in eps], [float(r["val_loss"]) for r in eps], "s-", color="#dc2626", label="validation")
a1.set_yscale("log"); a1.set_xlabel("optimizer step"); a1.set_ylabel("token cross-entropy (log scale)")
a1.set_title("Loss"); a1.legend(frameon=False); a1.grid(alpha=.25)
a2.plot([int(r["epoch"]) for r in eps], [float(r["val_entity_f1"]) for r in eps], "o-", color="#059669", label="val entity F1")
a2.plot([int(r["epoch"]) for r in eps], [float(r["val_primary_acc"]) for r in eps], "s--", color="#7c3aed", label="val primary-EPS accuracy")
a2.set_ylim(0, 1.02); a2.set_xlabel("epoch"); a2.set_title("Validation (5 filings)"); a2.legend(frameon=False, loc="lower right"); a2.grid(alpha=.25)
fig.tight_layout()
(ROOT / "results").mkdir(exist_ok=True)
fig.savefig(ROOT / "results" / "training_curves.png", dpi=150)
print("saved results/training_curves.png")
