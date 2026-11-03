# Results

Summary of the final numbers. Method, caveats and reproduction steps are in [README.md](README.md). Raw output is in
[results/eval.json](results/eval.json) and [results/eval_table.md](results/eval_table.md).

## 1. Final dataset

| | Filings |
|---|---|
| Collected | 50 (8-K earnings releases, all filed 2020-04-28/29) |
| With a 10-Q XBRL anchor | 45 |
| Included in the adjudicated label set | 47 (34 anchor-matched, 13 spot-checked) |
| Excluded | 3 (Valaris, Oshkosh, nVent: no anchor, not in the spot-check batch) |

| Split | Filings | 512-token windows | Gold EPS entities |
|---|---|---|---|
| Train | 30 | 530 | 468 |
| Validation | 5 | 71 | 82 |
| Test | 12 | 292 | 175 |

The split was fixed before training. Test filings were drawn only from anchored filings, so each one's gold primary
EPS is its 10-Q XBRL value and does not depend on any LLM output. Gold mentions across the 47 filings: 737
(345 GAAP diluted, 253 non-GAAP, 127 GAAP basic, 12 guidance, which are labeled `O` for training).

## 2. Fine-tuned model (DeBERTa-v3-base)

Training: 15 epochs, 13.5 minutes on an RTX 4050 Laptop GPU. The checkpoint with the best validation entity F1 was
kept, which was epoch 13 (validation entity F1 0.836, validation primary EPS correct on 5 of 5).

### Primary metric: headline EPS value per filing (test set, 12 filings)

Each system emits one value per filing, the current-quarter GAAP diluted EPS, scored as an exact signed match against
the 10-Q value. A wrong value counts as both a false positive and a false negative.

| Precision | Recall | F1 | Correct |
|---|---|---|---|
| 0.833 | 0.833 | 0.833 | 10 / 12 |

95% Wilson interval on accuracy: 0.55 to 0.95.

### Per label: mention-level exact match on character span and type (test set, 175 gold entities)

| Label | Precision | Recall | F1 | Gold support |
|---|---|---|---|---|
| EPS_GAAP_DILUTED | 0.804 | 0.881 | 0.841 | 84 |
| EPS_GAAP_BASIC | 0.806 | 1.000 | 0.893 | 25 |
| EPS_NONGAAP | 0.529 | 0.970 | 0.684 | 66 |
| **All three labels** | **0.668** | **0.931** | **0.778** | **175** |

Recall is high for every label and precision is the weak point, most of all for non-GAAP. The model tends to tag extra
numbers rather than miss real ones. In one test filing it tagged natural-gas prices per Mcf as diluted EPS.

**Caveat on this table.** 9 of the 12 test filings were not hand-reviewed, so their gold mentions are the same LLM's
pre-labels. This metric is biased toward the LLM baseline and describes how closely DeBERTa reproduces the label set.
It is not an independent measure of accuracy.

## 3. Baselines

### Zero-shot LLM (run)

Claude Opus 5, the same prompt used for pre-labeling, no fine-tuning and no examples, run fresh on the 12 test filings.
Its primary value is the most frequent current-quarter GAAP diluted value.

| System | Precision | Recall | F1 | Correct |
|---|---|---|---|---|
| Zero-shot LLM | 1.000 | 1.000 | 1.000 | 12 / 12 |
| Fine-tuned DeBERTa-v3-base | 0.833 | 0.833 | 0.833 | 10 / 12 |

95% Wilson interval on accuracy: 0.76 to 1.00 for the LLM. The intervals overlap, so 12 filings cannot separate the two
systems statistically.

Mention-level, same caveat as above:

| System | Precision | Recall | F1 |
|---|---|---|---|
| Zero-shot LLM | 0.967 | 1.000 | 0.983 |
| DeBERTa | 0.668 | 0.931 | 0.778 |

The two DeBERTa misses, both on the primary metric:

| Filing | Gold (10-Q) | DeBERTa | Zero-shot LLM |
|---|---|---|---|
| Antero Resources | -1.19 | 3.17 | -1.19 |
| Criteo | 0.25 | 0.29 | 0.25 |

In both filings DeBERTa tagged the correct EPS values. The table lists last year's column first, and the rule that
picks the current-quarter value chose the wrong column. The label set has no period, so the tagger cannot tell the
columns apart.

### XBRL-only baseline (not run)

No XBRL-only baseline was built. The 10-Q XBRL value is the ground truth for the test set, so scoring it against itself
would be meaningless. A meaningful alternative would be extracting EPS from XBRL attached to the 8-K itself, but the
filings here are 2020 press releases that mostly carry no such data, so that approach would return nothing for most
filings. This is listed as a gap, not as a result.

## 4. Post-hoc fix (not the reported result)

After the test set was scored, a second primary-value rule was written that reads the table's year header and takes the
column with the latest year.

| Rule | Train + val gold (35 filings) | Val predictions (5) | Test predictions (12) |
|---|---|---|---|
| First diluted cell in the table, chosen before testing | 35 | 5 | 10, F1 0.833 |
| Header-based current column, written after testing | 35 | 5 | 12, F1 1.000 |

The header rule was written after inspecting the two test failures. It ties on every filing that was not inspected, so
**1.000 is not a valid test score.** The reported result stays 0.833. A fair number for the new rule needs filings that
neither rule has seen. Raw output: [results/posthoc_header_rule.json](results/posthoc_header_rule.json).

## 5. Deviations from the original plan

**Changes to the labeling approach**
- **Label set size.** The plan was to label all 50 filings. The final set has 47. Valaris, Oshkosh and nVent had no
  anchor and were not in the spot-check batch.
- **Definition of GAAP EPS.** Only net EPS counts. Continuing-operations, discontinued-operations and comprehensive-income
  per-share figures are dropped. This came out of your spot-check of two flagged filings, and I applied the same rule
  to Cree through a documented override in [data/label_overrides.json](data/label_overrides.json).
- **Guidance EPS** is labeled `O` for training because the requested label set has no guidance class. The LLM
  pre-labels do include it as a type.
- **Test set drawn only from anchored filings**, so test ground truth is independent of any LLM.

**Changes you approved at the first checkpoint**
- 10-Q anchors may come from the separate XBRL instance file when the 10-Q predates inline XBRL (10 filings), and the
  `EarningsPerShareBasicAndDiluted` tag counts as the diluted anchor (5 filings).
- Item 2.02 text was fetched from EDGAR because the local files hold only Exhibit 99.1.

**Things that did not work on the first attempt**
- The first anchor pass covered 31 of 50 filings. Handling instance files, alternate tags and per-class reporting
  brought it to 45.
- Majority vote for the primary value failed on Standard Motor Products, because the release repeats its
  continuing-operations number more often than the net number.
- The first offset resolver left 3 mentions unplaced and the first sign decoder recovered 539 of 550 values. Both were
  fixed to 100% before training, using only training and validation data.
- Epoch 1 of training scored F1 0.000, as the model first predicted "not EPS" everywhere. It reached 0.43 by epoch 2.

**What did not change.** The base model is `microsoft/deberta-v3-base`, as specified, with the seven requested labels.
An extra package, `sentencepiece`, was installed because its tokenizer requires it.
