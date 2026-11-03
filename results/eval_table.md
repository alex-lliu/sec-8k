Test set: **12 filings** (held out before training; all anchored to 10-Q XBRL)

| System | Precision | Recall | F1 | Correct / emitted / filings |
|---|---|---|---|---|
| Fine-tuned DeBERTa-v3-base | 0.833 | 0.833 | 0.833 | 10 / 12 / 12 |
| Zero-shot LLM (claude-opus-5, Step 3 prompt) | 1.000 | 1.000 | 1.000 | 12 / 12 / 12 |

| Filing | Gold (10-Q) | DeBERTa | Zero-shot LLM |
|---|---|---|---|
| HASBRO, INC. | -0.51 | -0.51 | -0.51 |
| MSA Safety Inc | 1.11 | 1.11 | 1.11 |
| HARTFORD FINANCIAL SERVICES GROUP, INC. | 0.74 | 0.74 | 0.74 |
| VERTEX PHARMACEUTICALS INC / MA | 2.29 | 2.29 | 2.29 |
| MANTECH INTERNATIONAL CORP | 0.71 | 0.71 | 0.71 |
| CREE, INC. | -0.57 | -0.57 | -0.57 |
| TETRA TECH INC | 0.66 | 0.66 | 0.66 |
| ANTERO RESOURCES Corp | -1.19 | 3.17 ✗ | -1.19 |
| Mastercard Inc | 1.68 | 1.68 | 1.68 |
| Spok Holdings, Inc | -0.24 | -0.24 | -0.24 |
| Cadence Bancorporation | -3.15 | -3.15 | -3.15 |
| Criteo S.A. | 0.25 | 0.29 ✗ | 0.25 |

Secondary, entity-level exact span+type (biased toward the LLM; see caveat):

| System | P | R | F1 |
|---|---|---|---|
| DeBERTa | 0.668 | 0.931 | 0.778 |
| Zero-shot LLM | 0.967 | 1.000 | 0.983 |