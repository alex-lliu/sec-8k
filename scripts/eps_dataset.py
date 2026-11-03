"""Step 7b: PyTorch Dataset / DataLoader for EPS token classification.

Documents are tokenized once and every token keeps its character offsets, so predictions map back to the
text without re-tokenizing. GUIDANCE mentions are labeled O; the labels are
O, B/I-EPS_GAAP_DILUTED, B/I-EPS_GAAP_BASIC, B/I-EPS_NONGAAP.
"""
import json, random, warnings
from pathlib import Path

import torch
from torch.utils.data import Dataset, DataLoader, Sampler
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
LABELS = ["O", "B-EPS_GAAP_DILUTED", "I-EPS_GAAP_DILUTED", "B-EPS_GAAP_BASIC", "I-EPS_GAAP_BASIC",
          "B-EPS_NONGAAP", "I-EPS_NONGAAP"]
L2I = {l: i for i, l in enumerate(LABELS)}
TYPE2TAG = {"GAAP_DILUTED": "EPS_GAAP_DILUTED", "GAAP_BASIC": "EPS_GAAP_BASIC", "NON_GAAP": "EPS_NONGAAP"}
IGNORE = -100


def load_filing(acc):
    text = json.loads((ROOT / "data" / "parsed" / f"{acc}.json").read_text(encoding="utf-8"))["text"]
    gold = json.loads((ROOT / "data" / "gold" / f"{acc}.json").read_text(encoding="utf-8"))
    return text, gold


def encode_document(tokenizer, text, mentions=None):
    enc = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True, verbose=False)
    ids, offs = enc["input_ids"], enc["offset_mapping"]
    if mentions is None:
        return ids, offs, None
    labels = [L2I["O"]] * len(ids)
    ents = sorted((m["start"], m["end"], TYPE2TAG[m["type"]]) for m in mentions if m["type"] in TYPE2TAG)
    j = 0
    for s, e, tag in ents:
        first = True
        # advance to first token that could overlap
        while j < len(offs) and offs[j][1] <= s:
            j += 1
        k = j
        while k < len(offs) and offs[k][0] < e:
            a, b = offs[k]
            if b > s and a < e and b > a:  # overlap with the entity span
                labels[k] = L2I[("B-" if first else "I-") + tag]
                first = False
            k += 1
        if first:
            raise RuntimeError(f"entity {text[s:e]!r}@{s} mapped to no token")
    return ids, offs, labels


def make_windows(ids, offs, labels, cls_id, sep_id, max_len=512, stride=128):
    body = max_len - 2
    step = body - stride
    out, start = [], 0
    while True:
        end = min(start + body, len(ids))
        w = {"input_ids": [cls_id] + ids[start:end] + [sep_id],
             "offsets": [(0, 0)] + [tuple(o) for o in offs[start:end]] + [(0, 0)],
             "tok_start": start, "tok_end": end}
        if labels is not None:
            w["labels"] = [IGNORE] + labels[start:end] + [IGNORE]
            w["has_entity"] = any(l not in (L2I["O"], IGNORE) for l in w["labels"])
        out.append(w)
        if end >= len(ids):
            break
        start += step
    return out


class EPSWindowDataset(Dataset):
    def __init__(self, accessions, tokenizer, max_len=512, stride=128, with_labels=True):
        self.items = []
        self.docs = {}
        for acc in accessions:
            text, gold = load_filing(acc)
            ids, offs, labels = encode_document(tokenizer, text, gold["mentions"] if with_labels else None)
            self.docs[acc] = {"text": text, "n_tokens": len(ids), "offsets": offs, "token_labels": labels, "gold": gold}
            for w in make_windows(ids, offs, labels, tokenizer.cls_token_id, tokenizer.sep_token_id, max_len, stride):
                w["accession"] = acc
                self.items.append(w)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        return self.items[i]


def collate(batch, pad_id):
    n = max(len(b["input_ids"]) for b in batch)
    ids = torch.full((len(batch), n), pad_id, dtype=torch.long)
    att = torch.zeros((len(batch), n), dtype=torch.long)
    lab = torch.full((len(batch), n), IGNORE, dtype=torch.long)
    for i, b in enumerate(batch):
        L = len(b["input_ids"])
        ids[i, :L] = torch.tensor(b["input_ids"])
        att[i, :L] = 1
        if "labels" in b:
            lab[i, :L] = torch.tensor(b["labels"])
    return {"input_ids": ids, "attention_mask": att, "labels": lab,
            "meta": [{k: b[k] for k in ("accession", "tok_start", "tok_end")} for b in batch]}


class PositiveBiasedSampler(Sampler):
    """Most windows are boilerplate with no EPS, so only a fraction of them is sampled to keep the O class
    from swamping training."""

    def __init__(self, dataset, neg_fraction=0.3, seed=0):
        self.pos = [i for i, w in enumerate(dataset.items) if w["has_entity"]]
        self.neg = [i for i, w in enumerate(dataset.items) if not w["has_entity"]]
        self.neg_fraction, self.epoch, self.seed = neg_fraction, 0, seed

    def set_epoch(self, e):
        self.epoch = e

    def _indices(self):
        rng = random.Random(self.seed + self.epoch)
        idx = self.pos + rng.sample(self.neg, int(len(self.neg) * self.neg_fraction))
        rng.shuffle(idx)
        return idx

    def __iter__(self):
        return iter(self._indices())

    def __len__(self):
        return len(self.pos) + int(len(self.neg) * self.neg_fraction)


def make_loader(ds, tokenizer, batch_size, train=False, neg_fraction=0.3, seed=0):
    fn = lambda b: collate(b, tokenizer.pad_token_id)
    if train:
        sampler = PositiveBiasedSampler(ds, neg_fraction, seed)
        return DataLoader(ds, batch_size=batch_size, sampler=sampler, collate_fn=fn), sampler
    return DataLoader(ds, batch_size=batch_size, shuffle=False, collate_fn=fn), None


if __name__ == "__main__":
    # self-check: every gold span is recoverable exactly from token labels + offsets
    warnings.filterwarnings("ignore")
    tok = AutoTokenizer.from_pretrained("microsoft/deberta-v3-base")
    splits = json.loads((ROOT / "data" / "splits.json").read_text(encoding="utf-8"))
    for name in ("train", "val", "test"):
        ds = EPSWindowDataset(splits[name], tok)
        n_ent = n_ok = 0
        for acc, d in ds.docs.items():
            labs, offs, text = d["token_labels"], d["offsets"], d["text"]
            spans, cur = [], None
            for k, l in enumerate(labs):
                tag = LABELS[l]
                if tag.startswith("B-"):
                    if cur: spans.append(cur)
                    cur = [offs[k][0], offs[k][1], tag[2:]]
                elif tag.startswith("I-") and cur and tag[2:] == cur[2]:
                    cur[1] = offs[k][1]
                else:
                    if cur: spans.append(cur); cur = None
            if cur: spans.append(cur)
            got = {(text[a:b].strip(), a + (len(text[a:b]) - len(text[a:b].lstrip())), t) for a, b, t in spans}
            want = {(m["span_text"], m["start"], TYPE2TAG[m["type"]]) for m in d["gold"]["mentions"] if m["type"] in TYPE2TAG}
            n_ent += len(want); n_ok += len(want & got)
        pos = sum(w["has_entity"] for w in ds.items)
        print(f"{name:5} filings={len(ds.docs):2} windows={len(ds):4} (with entity {pos}) "
              f"tokens={sum(d['n_tokens'] for d in ds.docs.values())} entities={n_ent} round-trip exact={n_ok}")
