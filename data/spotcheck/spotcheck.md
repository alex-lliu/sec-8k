# EPS spot-check batch

Legend for the **Verdict** column (leave blank or write `OK` to accept as-is):
- `DROP` - not an EPS mention / wrong span
- `TYPE=GAAP_DILUTED|GAAP_BASIC|NON_GAAP|GUIDANCE` - fix the type
- `VALUE=-0.42` - fix the numeric value (sign matters)
- `PERIOD=current_quarter|prior_year_quarter|prior_quarter|current_ytd|prior_ytd|full_year|guidance_period|other` - fix the period
- combine with `;` e.g. `TYPE=NON_GAAP; PERIOD=prior_year_quarter`

To add a mention the model missed, add a line under the filing's **Missed mentions** heading:
`ADD: <verbatim context copied from the document> | <value_text> | <TYPE> | <period_kind>`

Anchor = diluted EPS parsed from the company's 10-Q XBRL (Step 1). Primary = the model's current-quarter GAAP diluted value.


## 1. STANDARD MOTOR PRODUCTS, INC.  (0001140361-20-010070)

Anchor (10-Q): **0.38** (us-gaap:EarningsPerShareDiluted) | Model primary: **0.42** | mentions: 20 | Reason in batch: Step 4 mismatch: anchor=0.38 llm=0.42 cands=[-0.04, 0.38, 0.42] / Step 5 A/B disagree: GAAP_BASIC current-quarter values differ: A=[-0.05, 0.38, 0.43] B=[0.38, 0.43]; GAAP_DILUTED current-quarter values differ: A=[-0.04, 0.38, 0.42] B=[0.38, 0.42]

| ID | Span | Type | Period kind | Period | Value | Context (span in [[ ]]) | Verdict |
|---|---|---|---|---|---|---|---|
| 1.1 | `42` | GAAP_DILUTED | current_quarter | Q1 2020 (continuing operations) | 0.42 | 9. ⏎ Earnings from continuing operations for the first quarter of 2020 were $9.6 million or [[42]] cents per diluted share, compared to $13.1 million or 57 ce | DROP |
| 1.2 | `57` | GAAP_DILUTED | prior_year_quarter | Q1 2019 (continuing operations) | 0.57 | ter of 2020 were $9.6 million or 42 cents per diluted share, compared to $13.1 million or [[57]] cents per diluted share in the first quarter of 2019. Exclu | DROP |
| 1.3 | `43` | NON_GAAP | current_quarter | Q1 2020 (continuing operations, non-GAAP) | 0.43 | s, earnings from continuing operations for the first quarter of 2020 were $9.8 million or [[43]] cents per diluted share, compared to $13.1 million or 57 ce |  |
| 1.4 | `57` | NON_GAAP | prior_year_quarter | Q1 2019 (continuing operations, non-GAAP) | 0.57 | ter of 2020 were $9.8 million or 43 cents per diluted share, compared to $13.1 million or [[57]] cents per diluted share in ⏎ the first quarter of 2019. ⏎ 37-18 |  |
| 1.5 | `0.43` | GAAP_BASIC | current_quarter | Q1 2020 (continuing operations) | 0.43 | 627 ¦ $12,216 ⏎ NET EARNINGS PER COMMON SHARE: ⏎ BASIC EARNINGS FROM CONTINUING OPERATIONS ¦ $[[0.43]] ¦ $0.58 ⏎ DISCONTINUED OPERATION ¦ (0.05) ¦ (0.04) ⏎ NET EARNIN | DROP |
| 1.6 | `0.58` | GAAP_BASIC | prior_year_quarter | Q1 2019 (continuing operations) | 0.58 | 2,216 ⏎ NET EARNINGS PER COMMON SHARE: ⏎ BASIC EARNINGS FROM CONTINUING OPERATIONS ¦ $0.43 ¦ $[[0.58]] ⏎ DISCONTINUED OPERATION ¦ (0.05) ¦ (0.04) ⏎ NET EARNINGS PER C | DROP |
| 1.7 | `0.05` | GAAP_BASIC | current_quarter | Q1 2020 (discontinued operation, basic) | -0.05 | HARE: ⏎ BASIC EARNINGS FROM CONTINUING OPERATIONS ¦ $0.43 ¦ $0.58 ⏎ DISCONTINUED OPERATION ¦ ([[0.05]]) ¦ (0.04) ⏎ NET EARNINGS PER COMMON SHARE - BASIC ¦ $0.38 ¦ $ | DROP |
| 1.8 | `0.04` | GAAP_BASIC | prior_year_quarter | Q1 2019 (discontinued operation, basic) | -0.04 | IC EARNINGS FROM CONTINUING OPERATIONS ¦ $0.43 ¦ $0.58 ⏎ DISCONTINUED OPERATION ¦ (0.05) ¦ ([[0.04]]) ⏎ NET EARNINGS PER COMMON SHARE - BASIC ¦ $0.38 ¦ $0.54 ⏎ DILU | DROP |
| 1.9 | `0.38` | GAAP_BASIC | current_quarter | Q1 2020 | 0.38 | ¦ $0.58 ⏎ DISCONTINUED OPERATION ¦ (0.05) ¦ (0.04) ⏎ NET EARNINGS PER COMMON SHARE - BASIC ¦ $[[0.38]] ¦ $0.54 ⏎ DILUTED EARNINGS FROM CONTINUING OPERATIONS ¦ $0.42 |  |
| 1.10 | `0.54` | GAAP_BASIC | prior_year_quarter | Q1 2019 | 0.54 | DISCONTINUED OPERATION ¦ (0.05) ¦ (0.04) ⏎ NET EARNINGS PER COMMON SHARE - BASIC ¦ $0.38 ¦ $[[0.54]] ⏎ DILUTED EARNINGS FROM CONTINUING OPERATIONS ¦ $0.42 ¦ $0.57 |  |
| 1.11 | `0.42` | GAAP_DILUTED | current_quarter | Q1 2020 (continuing operations) | 0.42 | S PER COMMON SHARE - BASIC ¦ $0.38 ¦ $0.54 ⏎ DILUTED EARNINGS FROM CONTINUING OPERATIONS ¦ $[[0.42]] ¦ $0.57 ⏎ DISCONTINUED OPERATION ¦ (0.04) ¦ (0.04) ⏎ NET EARNIN | DROP |
| 1.12 | `0.57` | GAAP_DILUTED | prior_year_quarter | Q1 2019 (continuing operations) | 0.57 | MMON SHARE - BASIC ¦ $0.38 ¦ $0.54 ⏎ DILUTED EARNINGS FROM CONTINUING OPERATIONS ¦ $0.42 ¦ $[[0.57]] ⏎ DISCONTINUED OPERATION ¦ (0.04) ¦ (0.04) ⏎ NET EARNINGS PER C | DROP |
| 1.13 | `0.04` | GAAP_DILUTED | current_quarter | Q1 2020 (discontinued operation, diluted) | -0.04 | .54 ⏎ DILUTED EARNINGS FROM CONTINUING OPERATIONS ¦ $0.42 ¦ $0.57 ⏎ DISCONTINUED OPERATION ¦ ([[0.04]]) ¦ (0.04) ⏎ NET EARNINGS PER COMMON SHARE - DILUTED ¦ $0.38 ¦ | DROP |
| 1.14 | `0.04` | GAAP_DILUTED | prior_year_quarter | Q1 2019 (discontinued operation, diluted) | -0.04 | ED EARNINGS FROM CONTINUING OPERATIONS ¦ $0.42 ¦ $0.57 ⏎ DISCONTINUED OPERATION ¦ (0.04) ¦ ([[0.04]]) ⏎ NET EARNINGS PER COMMON SHARE - DILUTED ¦ $0.38 ¦ $0.53 ⏎ WE | DROP |
| 1.15 | `0.38` | GAAP_DILUTED | current_quarter | Q1 2020 | 0.38 | $0.57 ⏎ DISCONTINUED OPERATION ¦ (0.04) ¦ (0.04) ⏎ NET EARNINGS PER COMMON SHARE - DILUTED ¦ $[[0.38]] ¦ $0.53 ⏎ WEIGHTED AVERAGE NUMBER OF COMMON SHARES ¦ 22,438,0 |  |
| 1.16 | `0.53` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | 0.53 | SCONTINUED OPERATION ¦ (0.04) ¦ (0.04) ⏎ NET EARNINGS PER COMMON SHARE - DILUTED ¦ $0.38 ¦ $[[0.53]] ⏎ WEIGHTED AVERAGE NUMBER OF COMMON SHARES ¦ 22,438,087 ¦ 22, |  |
| 1.17 | `0.42` | GAAP_DILUTED | current_quarter | Q1 2020 (continuing operations) | 0.42 |  FROM CONTINUING OPERATIONS ⏎ GAAP DILUTED EARNINGS PER SHARE FROM CONTINUING OPERATIONS ¦ $[[0.42]] ¦ $0.57 ⏎ RESTRUCTURING AND INTEGRATION EXPENSES ¦ 0.01 ¦ - ⏎ I | DROP |
| 1.18 | `0.57` | GAAP_DILUTED | prior_year_quarter | Q1 2019 (continuing operations) | 0.57 | NTINUING OPERATIONS ⏎ GAAP DILUTED EARNINGS PER SHARE FROM CONTINUING OPERATIONS ¦ $0.42 ¦ $[[0.57]] ⏎ RESTRUCTURING AND INTEGRATION EXPENSES ¦ 0.01 ¦ - ⏎ INCOME TA | DROP |
| 1.19 | `0.43` | NON_GAAP | current_quarter | Q1 2020 (continuing operations, non-GAAP) | 0.43 | CONCILING ITEMS ¦ - ¦ - ⏎ NON-GAAP DILUTED EARNINGS PER SHARE FROM CONTINUING OPERATIONS ¦ $[[0.43]] ¦ $0.57 ⏎ OPERATING INCOME ⏎ GAAP OPERATING INCOME ¦ $14,323 ¦  |  |
| 1.20 | `0.57` | NON_GAAP | prior_year_quarter | Q1 2019 (continuing operations, non-GAAP) | 0.57 | G ITEMS ¦ - ¦ - ⏎ NON-GAAP DILUTED EARNINGS PER SHARE FROM CONTINUING OPERATIONS ¦ $0.43 ¦ $[[0.57]] ⏎ OPERATING INCOME ⏎ GAAP OPERATING INCOME ¦ $14,323 ¦ $17,957 ⏎  |  |

Pass B (second prompt) current-quarter mentions for comparison: GAAP_DILUTED current_quarter 0.42 `42`; NON_GAAP current_quarter 0.43 `43`; GAAP_BASIC current_quarter 0.43 `0.43`; GAAP_BASIC current_quarter 0.38 `0.38`; GAAP_DILUTED current_quarter 0.42 `0.42`; GAAP_DILUTED current_quarter 0.38 `0.38`; GAAP_DILUTED current_quarter 0.42 `0.42`; NON_GAAP current_quarter 0.43 `0.43`

**Missed mentions** (add `ADD:` lines below):


## 2. AGNC Investment Corp.  (0001423689-20-000040)

Anchor (10-Q): **-4.46** (us-gaap:EarningsPerShareDiluted) | Model primary: **-4.46** | mentions: 55 | Reason in batch: Step 4 match_but_multiple_candidates: anchor=-4.46 llm=-4.46 cands=[-4.46, -3.61]

| ID | Span | Type | Period kind | Period | Value | Context (span in [[ ]]) | Verdict |
|---|---|---|---|---|---|---|---|
| 2.1 | `3.61` | GAAP_DILUTED | current_quarter | Q1 2020 (comprehensive loss per common share) | -3.61 | sults for the quarter ended March 31, 2020. ⏎ FIRST QUARTER 2020 FINANCIAL HIGHLIGHTS ⏎ • ¦ $([[3.61]]) comprehensive loss per common share, comprised of: ⏎ ◦ ¦ $(4 | DROP |
| 2.2 | `4.46` | GAAP_DILUTED | current_quarter | Q1 2020 | -4.46 | FINANCIAL HIGHLIGHTS ⏎ • ¦ $(3.61) comprehensive loss per common share, comprised of: ⏎ ◦ ¦ $([[4.46]]) net loss per common share ⏎ ◦ ¦ $0.85 other comprehensive in |  |
| 2.3 | `0.57` | NON_GAAP | current_quarter | Q1 2020 | 0.57 | ehensive income ("OCI") per common share on investments marked-to-market through OCI ⏎ • ¦ $[[0.57]] net spread and dollar roll income per common share, excludi |  |
| 2.4 | `0.57` | NON_GAAP | current_quarter | Q1 2020 | 0.57 | et spread and dollar roll income (a non-GAAP financial measure) for the first quarter of $[[0.57]] per common share, excluding $(0.44) per common share of "ca |  |
| 2.5 | `0.57` | NON_GAAP | prior_quarter | Q4 2019 | 0.57 |  excluding $(0.44) per common share of "catch-up" premium amortization cost, compared to $[[0.57]] per common share for the prior quarter, excluding $0.09 per |  |
| 2.6 | `4.46` | GAAP_BASIC | current_quarter | Q1 2020 | -4.46 | ed ¦ 548.0 ¦ 542.6 ¦ 546.4 ¦ 537.8 ¦ 537.2 ⏎ Net income (loss) per common share - basic ¦ $([[4.46]]) ¦ $1.56 ¦ $(0.03) ¦ $(0.85) ¦ $0.48 ⏎ Net income (loss) per  |  |
| 2.7 | `1.56` | GAAP_BASIC | prior_quarter | Q4 2019 | 1.56 | 0 ¦ 542.6 ¦ 546.4 ¦ 537.8 ¦ 537.2 ⏎ Net income (loss) per common share - basic ¦ $(4.46) ¦ $[[1.56]] ¦ $(0.03) ¦ $(0.85) ¦ $0.48 ⏎ Net income (loss) per common sh |  |
| 2.8 | `0.03` | GAAP_BASIC | other | Q3 2019 | -0.03 |  ¦ 546.4 ¦ 537.8 ¦ 537.2 ⏎ Net income (loss) per common share - basic ¦ $(4.46) ¦ $1.56 ¦ $([[0.03]]) ¦ $(0.85) ¦ $0.48 ⏎ Net income (loss) per common share - dil |  |
| 2.9 | `0.85` | GAAP_BASIC | other | Q2 2019 | -0.85 |  537.8 ¦ 537.2 ⏎ Net income (loss) per common share - basic ¦ $(4.46) ¦ $1.56 ¦ $(0.03) ¦ $([[0.85]]) ¦ $0.48 ⏎ Net income (loss) per common share - diluted ¦ $(4 |  |
| 2.10 | `0.48` | GAAP_BASIC | prior_year_quarter | Q1 2019 | 0.48 | 537.2 ⏎ Net income (loss) per common share - basic ¦ $(4.46) ¦ $1.56 ¦ $(0.03) ¦ $(0.85) ¦ $[[0.48]] ⏎ Net income (loss) per common share - diluted ¦ $(4.46) ¦ $1 |  |
| 2.11 | `4.46` | GAAP_DILUTED | current_quarter | Q1 2020 | -4.46 | .46) ¦ $1.56 ¦ $(0.03) ¦ $(0.85) ¦ $0.48 ⏎ Net income (loss) per common share - diluted ¦ $([[4.46]]) ¦ $1.56 ¦ $(0.03) ¦ $(0.85) ¦ $0.47 ⏎ Comprehensive income ( |  |
| 2.12 | `1.56` | GAAP_DILUTED | prior_quarter | Q4 2019 | 1.56 | .56 ¦ $(0.03) ¦ $(0.85) ¦ $0.48 ⏎ Net income (loss) per common share - diluted ¦ $(4.46) ¦ $[[1.56]] ¦ $(0.03) ¦ $(0.85) ¦ $0.47 ⏎ Comprehensive income (loss) per |  |
| 2.13 | `0.03` | GAAP_DILUTED | other | Q3 2019 | -0.03 | .03) ¦ $(0.85) ¦ $0.48 ⏎ Net income (loss) per common share - diluted ¦ $(4.46) ¦ $1.56 ¦ $([[0.03]]) ¦ $(0.85) ¦ $0.47 ⏎ Comprehensive income (loss) per common s |  |
| 2.14 | `0.85` | GAAP_DILUTED | other | Q2 2019 | -0.85 | .85) ¦ $0.48 ⏎ Net income (loss) per common share - diluted ¦ $(4.46) ¦ $1.56 ¦ $(0.03) ¦ $([[0.85]]) ¦ $0.47 ⏎ Comprehensive income (loss) per common share - bas |  |
| 2.15 | `0.47` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | 0.47 | .48 ⏎ Net income (loss) per common share - diluted ¦ $(4.46) ¦ $1.56 ¦ $(0.03) ¦ $(0.85) ¦ $[[0.47]] ⏎ Comprehensive income (loss) per common share - basic ¦ $(3. |  |
| 2.16 | `3.61` | GAAP_BASIC | current_quarter | Q1 2020 (comprehensive income (loss) per share) | -3.61 | 1.56 ¦ $(0.03) ¦ $(0.85) ¦ $0.47 ⏎ Comprehensive income (loss) per common share - basic ¦ $([[3.61]]) ¦ $1.59 ¦ $0.42 ¦ $(0.15) ¦ $1.22 ⏎ Comprehensive income (lo | DROP |
| 2.17 | `1.59` | GAAP_BASIC | prior_quarter | Q4 2019 (comprehensive income (loss) per share) | 1.59 | 0.03) ¦ $(0.85) ¦ $0.47 ⏎ Comprehensive income (loss) per common share - basic ¦ $(3.61) ¦ $[[1.59]] ¦ $0.42 ¦ $(0.15) ¦ $1.22 ⏎ Comprehensive income (loss) per c | DROP |
| 2.18 | `0.42` | GAAP_BASIC | other | Q3 2019 (comprehensive income (loss) per share) | 0.42 | $(0.85) ¦ $0.47 ⏎ Comprehensive income (loss) per common share - basic ¦ $(3.61) ¦ $1.59 ¦ $[[0.42]] ¦ $(0.15) ¦ $1.22 ⏎ Comprehensive income (loss) per common sh | DROP |
| 2.19 | `0.15` | GAAP_BASIC | other | Q2 2019 (comprehensive income (loss) per share) | -0.15 |  $0.47 ⏎ Comprehensive income (loss) per common share - basic ¦ $(3.61) ¦ $1.59 ¦ $0.42 ¦ $([[0.15]]) ¦ $1.22 ⏎ Comprehensive income (loss) per common share - dil | DROP |
| 2.20 | `1.22` | GAAP_BASIC | prior_year_quarter | Q1 2019 (comprehensive income (loss) per share) | 1.22 | mprehensive income (loss) per common share - basic ¦ $(3.61) ¦ $1.59 ¦ $0.42 ¦ $(0.15) ¦ $[[1.22]] ⏎ Comprehensive income (loss) per common share - diluted ¦ $( | DROP |
| 2.21 | `3.61` | GAAP_DILUTED | current_quarter | Q1 2020 (comprehensive income (loss) per share) | -3.61 | 1.59 ¦ $0.42 ¦ $(0.15) ¦ $1.22 ⏎ Comprehensive income (loss) per common share - diluted ¦ $([[3.61]]) ¦ $1.59 ¦ $0.42 ¦ $(0.15) ¦ $1.22 ⏎ Dividends declared per c | DROP |
| 2.22 | `1.59` | GAAP_DILUTED | prior_quarter | Q4 2019 (comprehensive income (loss) per share) | 1.59 | .42 ¦ $(0.15) ¦ $1.22 ⏎ Comprehensive income (loss) per common share - diluted ¦ $(3.61) ¦ $[[1.59]] ¦ $0.42 ¦ $(0.15) ¦ $1.22 ⏎ Dividends declared per common sha | DROP |
| 2.23 | `0.42` | GAAP_DILUTED | other | Q3 2019 (comprehensive income (loss) per share) | 0.42 | 0.15) ¦ $1.22 ⏎ Comprehensive income (loss) per common share - diluted ¦ $(3.61) ¦ $1.59 ¦ $[[0.42]] ¦ $(0.15) ¦ $1.22 ⏎ Dividends declared per common share ¦ $0. | DROP |
| 2.24 | `0.15` | GAAP_DILUTED | other | Q2 2019 (comprehensive income (loss) per share) | -0.15 | 1.22 ⏎ Comprehensive income (loss) per common share - diluted ¦ $(3.61) ¦ $1.59 ¦ $0.42 ¦ $([[0.15]]) ¦ $1.22 ⏎ Dividends declared per common share ¦ $0.48 ¦ $0.4 | DROP |
| 2.25 | `1.22` | GAAP_DILUTED | prior_year_quarter | Q1 2019 (comprehensive income (loss) per share) | 1.22 | rehensive income (loss) per common share - diluted ¦ $(3.61) ¦ $1.59 ¦ $0.42 ¦ $(0.15) ¦ $[[1.22]] ⏎ Dividends declared per common share ¦ $0.48 ¦ $0.48 ¦ $0.48 | DROP |
| 2.26 | `0.13` | NON_GAAP | current_quarter | Q1 2020 | 0.13 | 2.6 ¦ 547.1 ¦ 538.4 ¦ 537.2 ⏎ Net spread and dollar roll income per common share - basic ¦ $[[0.13]] ¦ $0.66 ¦ $0.49 ¦ $0.38 ¦ $0.45 ⏎ Net spread and dollar roll  |  |
| 2.27 | `0.66` | NON_GAAP | prior_quarter | Q4 2019 | 0.66 | 7.1 ¦ 538.4 ¦ 537.2 ⏎ Net spread and dollar roll income per common share - basic ¦ $0.13 ¦ $[[0.66]] ¦ $0.49 ¦ $0.38 ¦ $0.45 ⏎ Net spread and dollar roll income p |  |
| 2.28 | `0.49` | NON_GAAP | other | Q3 2019 | 0.49 | 8.4 ¦ 537.2 ⏎ Net spread and dollar roll income per common share - basic ¦ $0.13 ¦ $0.66 ¦ $[[0.49]] ¦ $0.38 ¦ $0.45 ⏎ Net spread and dollar roll income per commo |  |
| 2.29 | `0.38` | NON_GAAP | other | Q2 2019 | 0.38 | 7.2 ⏎ Net spread and dollar roll income per common share - basic ¦ $0.13 ¦ $0.66 ¦ $0.49 ¦ $[[0.38]] ¦ $0.45 ⏎ Net spread and dollar roll income per common share  |  |
| 2.30 | `0.45` | NON_GAAP | prior_year_quarter | Q1 2019 | 0.45 | spread and dollar roll income per common share - basic ¦ $0.13 ¦ $0.66 ¦ $0.49 ¦ $0.38 ¦ $[[0.45]] ⏎ Net spread and dollar roll income per common share - dilute |  |
| 2.31 | `0.13` | NON_GAAP | current_quarter | Q1 2020 | 0.13 | 6 ¦ $0.49 ¦ $0.38 ¦ $0.45 ⏎ Net spread and dollar roll income per common share - diluted ¦ $[[0.13]] ¦ $0.66 ¦ $0.49 ¦ $0.38 ¦ $0.45 ⏎ Net spread and dollar roll  |  |
| 2.32 | `0.66` | NON_GAAP | prior_quarter | Q4 2019 | 0.66 | 9 ¦ $0.38 ¦ $0.45 ⏎ Net spread and dollar roll income per common share - diluted ¦ $0.13 ¦ $[[0.66]] ¦ $0.49 ¦ $0.38 ¦ $0.45 ⏎ Net spread and dollar roll income,  |  |
| 2.33 | `0.49` | NON_GAAP | other | Q3 2019 | 0.49 | 8 ¦ $0.45 ⏎ Net spread and dollar roll income per common share - diluted ¦ $0.13 ¦ $0.66 ¦ $[[0.49]] ¦ $0.38 ¦ $0.45 ⏎ Net spread and dollar roll income, excludin |  |
| 2.34 | `0.38` | NON_GAAP | other | Q2 2019 | 0.38 | 5 ⏎ Net spread and dollar roll income per common share - diluted ¦ $0.13 ¦ $0.66 ¦ $0.49 ¦ $[[0.38]] ¦ $0.45 ⏎ Net spread and dollar roll income, excluding "catch |  |
| 2.35 | `0.45` | NON_GAAP | prior_year_quarter | Q1 2019 | 0.45 | read and dollar roll income per common share - diluted ¦ $0.13 ¦ $0.66 ¦ $0.49 ¦ $0.38 ¦ $[[0.45]] ⏎ Net spread and dollar roll income, excluding "catch-up" pre |  |
| 2.36 | `0.57` | NON_GAAP | current_quarter | Q1 2020 | 0.57 | ollar roll income, excluding "catch-up" premium amortization, per common share - basic ¦ $[[0.57]] ¦ $0.57 ¦ $0.59 ¦ $0.49 ¦ $0.52 ⏎ Net spread and dollar roll  |  |
| 2.37 | `0.57` | NON_GAAP | prior_quarter | Q4 2019 | 0.57 | ll income, excluding "catch-up" premium amortization, per common share - basic ¦ $0.57 ¦ $[[0.57]] ¦ $0.59 ¦ $0.49 ¦ $0.52 ⏎ Net spread and dollar roll income,  |  |
| 2.38 | `0.59` | NON_GAAP | other | Q3 2019 | 0.59 | e, excluding "catch-up" premium amortization, per common share - basic ¦ $0.57 ¦ $0.57 ¦ $[[0.59]] ¦ $0.49 ¦ $0.52 ⏎ Net spread and dollar roll income, excludin |  |
| 2.39 | `0.49` | NON_GAAP | other | Q2 2019 | 0.49 | ding "catch-up" premium amortization, per common share - basic ¦ $0.57 ¦ $0.57 ¦ $0.59 ¦ $[[0.49]] ¦ $0.52 ⏎ Net spread and dollar roll income, excluding "catch |  |
| 2.40 | `0.52` | NON_GAAP | prior_year_quarter | Q1 2019 | 0.52 | tch-up" premium amortization, per common share - basic ¦ $0.57 ¦ $0.57 ¦ $0.59 ¦ $0.49 ¦ $[[0.52]] ⏎ Net spread and dollar roll income, excluding "catch-up" pre |  |
| 2.41 | `0.57` | NON_GAAP | current_quarter | Q1 2020 | 0.57 | lar roll income, excluding "catch-up" premium amortization, per common share - diluted ¦ $[[0.57]] ¦ $0.57 ¦ $0.59 ¦ $0.49 ¦ $0.52 ⏎ AGNC Investment Corp. ⏎ April |  |
| 2.42 | `0.57` | NON_GAAP | prior_quarter | Q4 2019 | 0.57 |  income, excluding "catch-up" premium amortization, per common share - diluted ¦ $0.57 ¦ $[[0.57]] ¦ $0.59 ¦ $0.49 ¦ $0.52 ⏎ AGNC Investment Corp. ⏎ April 29, 202 |  |
| 2.43 | `0.59` | NON_GAAP | other | Q3 2019 | 0.59 |  excluding "catch-up" premium amortization, per common share - diluted ¦ $0.57 ¦ $0.57 ¦ $[[0.59]] ¦ $0.49 ¦ $0.52 ⏎ AGNC Investment Corp. ⏎ April 29, 2020 ⏎ Page 1 |  |
| 2.44 | `0.49` | NON_GAAP | other | Q2 2019 | 0.49 | ng "catch-up" premium amortization, per common share - diluted ¦ $0.57 ¦ $0.57 ¦ $0.59 ¦ $[[0.49]] ¦ $0.52 ⏎ AGNC Investment Corp. ⏎ April 29, 2020 ⏎ Page 10 ⏎ AGNC I |  |
| 2.45 | `0.52` | NON_GAAP | prior_year_quarter | Q1 2019 | 0.52 | h-up" premium amortization, per common share - diluted ¦ $0.57 ¦ $0.57 ¦ $0.59 ¦ $0.49 ¦ $[[0.52]] ⏎ AGNC Investment Corp. ⏎ April 29, 2020 ⏎ Page 10 ⏎ AGNC INVESTMEN |  |
| 2.46 | `0.20` | NON_GAAP | current_quarter | Q1 2020 (estimated REIT taxable income per share) | 0.2 | ¦ 542.6 ¦ 547.1 ¦ 538.4 ¦ 537.2 ⏎ Estimated REIT taxable income per common share - basic ¦ $[[0.20]] ¦ $0.18 ¦ $0.29 ¦ $0.32 ¦ $0.37 ⏎ Estimated REIT taxable inco |  |
| 2.47 | `0.18` | NON_GAAP | prior_quarter | Q4 2019 (estimated REIT taxable income per share) | 0.18 | ¦ 547.1 ¦ 538.4 ¦ 537.2 ⏎ Estimated REIT taxable income per common share - basic ¦ $0.20 ¦ $[[0.18]] ¦ $0.29 ¦ $0.32 ¦ $0.37 ⏎ Estimated REIT taxable income per c |  |
| 2.48 | `0.29` | NON_GAAP | other | Q3 2019 (estimated REIT taxable income per share) | 0.29 | ¦ 538.4 ¦ 537.2 ⏎ Estimated REIT taxable income per common share - basic ¦ $0.20 ¦ $0.18 ¦ $[[0.29]] ¦ $0.32 ¦ $0.37 ⏎ Estimated REIT taxable income per common sh |  |
| 2.49 | `0.32` | NON_GAAP | other | Q2 2019 (estimated REIT taxable income per share) | 0.32 | ¦ 537.2 ⏎ Estimated REIT taxable income per common share - basic ¦ $0.20 ¦ $0.18 ¦ $0.29 ¦ $[[0.32]] ¦ $0.37 ⏎ Estimated REIT taxable income per common share - di |  |
| 2.50 | `0.37` | NON_GAAP | prior_year_quarter | Q1 2019 (estimated REIT taxable income per share) | 0.37 | Estimated REIT taxable income per common share - basic ¦ $0.20 ¦ $0.18 ¦ $0.29 ¦ $0.32 ¦ $[[0.37]] ⏎ Estimated REIT taxable income per common share - diluted ¦  |  |
| 2.51 | `0.20` | NON_GAAP | current_quarter | Q1 2020 (estimated REIT taxable income per share) | 0.2 | $0.18 ¦ $0.29 ¦ $0.32 ¦ $0.37 ⏎ Estimated REIT taxable income per common share - diluted ¦ $[[0.20]] ¦ $0.18 ¦ $0.29 ¦ $0.32 ¦ $0.36 ⏎ Beginning cumulative non-de |  |
| 2.52 | `0.18` | NON_GAAP | prior_quarter | Q4 2019 (estimated REIT taxable income per share) | 0.18 | $0.29 ¦ $0.32 ¦ $0.37 ⏎ Estimated REIT taxable income per common share - diluted ¦ $0.20 ¦ $[[0.18]] ¦ $0.29 ¦ $0.32 ¦ $0.36 ⏎ Beginning cumulative non-deductible |  |
| 2.53 | `0.29` | NON_GAAP | other | Q3 2019 (estimated REIT taxable income per share) | 0.29 | $0.32 ¦ $0.37 ⏎ Estimated REIT taxable income per common share - diluted ¦ $0.20 ¦ $0.18 ¦ $[[0.29]] ¦ $0.32 ¦ $0.36 ⏎ Beginning cumulative non-deductible net cap |  |
| 2.54 | `0.32` | NON_GAAP | other | Q2 2019 (estimated REIT taxable income per share) | 0.32 | $0.37 ⏎ Estimated REIT taxable income per common share - diluted ¦ $0.20 ¦ $0.18 ¦ $0.29 ¦ $[[0.32]] ¦ $0.36 ⏎ Beginning cumulative non-deductible net capital los |  |
| 2.55 | `0.36` | NON_GAAP | prior_year_quarter | Q1 2019 (estimated REIT taxable income per share) | 0.36 | timated REIT taxable income per common share - diluted ¦ $0.20 ¦ $0.18 ¦ $0.29 ¦ $0.32 ¦ $[[0.36]] ⏎ Beginning cumulative non-deductible net capital loss ¦ $394 |  |

**Missed mentions** (add `ADD:` lines below):


## 3. AZZ INC  (0000008947-20-000044)

Anchor (10-Q): **None** (unanchored) | Model primary: **-0.41** | mentions: 25 | Reason in batch: random sample (unflagged)

| ID | Span | Type | Period kind | Period | Value | Context (span in [[ ]]) | Verdict |
|---|---|---|---|---|---|---|---|
| 3.1 | `2.71` | NON_GAAP | full_year | FY2020 (year ended February 29, 2020) | 2.71 | nc. Reports Financial Results for Fiscal Year 2020 ⏎ Full Year Fiscal 2020 Adjusted EPS of $[[2.71]], up 38% over prior year, with reported EPS of $1.84 ⏎ Annual  |  |
| 3.2 | `1.84` | GAAP_DILUTED | full_year | FY2020 (year ended February 29, 2020) | 1.84 | ull Year Fiscal 2020 Adjusted EPS of $2.71, up 38% over prior year, with reported EPS of $[[1.84]] ⏎ Annual Revenues of $1.06 billion, up 14.5% over prior year ⏎  |  |
| 3.3 | `2.65` | GUIDANCE | guidance_period | FY2021 guidance | 2.65 | prior year ⏎ Company discontinues previously issued Fiscal Year 2021 EPS guidance range of $[[2.65]] to $3.15 and sales guidance range of $970 million to $1.06  |  |
| 3.4 | `3.15` | GUIDANCE | guidance_period | FY2021 guidance | 3.15 | r ⏎ Company discontinues previously issued Fiscal Year 2021 EPS guidance range of $2.65 to $[[3.15]] and sales guidance range of $970 million to $1.06 billion d |  |
| 3.5 | `1.84` | GAAP_DILUTED | full_year | FY2020 | 1.84 | ctivities of 144.8 million, an increase of 29.9% compared to prior year. Reported EPS of $[[1.84]] includes pre-tax adjusted items of $18.6 million for the lo |  |
| 3.6 | `2.71` | NON_GAAP | full_year | FY2020 | 2.71 | ems, adjusted net income was $71.3 million, up 39.3% compared to prior year, and EPS was $[[2.71]], up 38.3% compared to $1.96 for the prior year, on a dilute |  |
| 3.7 | `1.96` | NON_GAAP | full_year | FY2019 | 1.96 |  $71.3 million, up 39.3% compared to prior year, and EPS was $2.71, up 38.3% compared to $[[1.96]] for the prior year, on a diluted basis.” ⏎ “During the year,  |  |
| 3.8 | `1.84` | GAAP_DILUTED | full_year | FY2020 | 1.84 | ared to prior year. Net income for the twelve months decreased 5.8% to $48.2 million, or $[[1.84]] per diluted share on a reported basis, compared to $51.2 mi |  |
| 3.9 | `1.96` | GAAP_DILUTED | full_year | FY2019 | 1.96 | 2 million, or $1.84 per diluted share on a reported basis, compared to $51.2 million, or $[[1.96]] per diluted share compared to the prior fiscal year. The re |  |
| 3.10 | `2.71` | NON_GAAP | full_year | FY2020 | 2.71 | d net income was $71.3 million, up 39.1% compared to prior year, and EPS would have been $[[2.71]], up 38.3% compared to prior year. ⏎ Bookings for fiscal 2020  |  |
| 3.11 | `.41` | GAAP_DILUTED | current_quarter | Q4 FY2020 | -0.41 | e quarter last year. Reported net income for the fourth quarter was $(10.6) million, or $([[.41]]) per diluted share, compared to net income of $8.8 million, |  |
| 3.12 | `0.34` | GAAP_DILUTED | prior_year_quarter | Q4 FY2019 | 0.34 | $(10.6) million, or $(.41) per diluted share, compared to net income of $8.8 million, or $[[0.34]] per diluted share, for last year’s fourth fiscal quarter. T |  |
| 3.13 | `0.47` | NON_GAAP | current_quarter | Q4 FY2020 | 0.47 | I. The adjusted non-GAAP net income without these items would have been $12.4 million or $[[0.47]] per share, as disclosed in the accompanying tables to our p |  |
| 3.14 | `0.41` | GAAP_BASIC | current_quarter | Q4 FY2020 (three months ended February 29, 2020) | -0.41 | loss) ¦ $(10,643) ¦ $8,851 ¦ $48,234 ¦ $51,208 ⏎ Earnings (loss) per common share ⏎ Basic ¦ $([[0.41]]) ¦ $0.34 ¦ $1.84 ¦ $1.97 ⏎ Diluted ¦ $(0.41) ¦ $0.34 ¦ $1.84  |  |
| 3.15 | `0.34` | GAAP_BASIC | prior_year_quarter | Q4 FY2019 (three months ended February 28, 2019) | 0.34 | (10,643) ¦ $8,851 ¦ $48,234 ¦ $51,208 ⏎ Earnings (loss) per common share ⏎ Basic ¦ $(0.41) ¦ $[[0.34]] ¦ $1.84 ¦ $1.97 ⏎ Diluted ¦ $(0.41) ¦ $0.34 ¦ $1.84 ¦ $1.96 ⏎ D |  |
| 3.16 | `1.84` | GAAP_BASIC | full_year | twelve months ended February 29, 2020 | 1.84 |  ¦ $8,851 ¦ $48,234 ¦ $51,208 ⏎ Earnings (loss) per common share ⏎ Basic ¦ $(0.41) ¦ $0.34 ¦ $[[1.84]] ¦ $1.97 ⏎ Diluted ¦ $(0.41) ¦ $0.34 ¦ $1.84 ¦ $1.96 ⏎ Diluted a |  |
| 3.17 | `1.97` | GAAP_BASIC | full_year | twelve months ended February 28, 2019 | 1.97 | 1 ¦ $48,234 ¦ $51,208 ⏎ Earnings (loss) per common share ⏎ Basic ¦ $(0.41) ¦ $0.34 ¦ $1.84 ¦ $[[1.97]] ⏎ Diluted ¦ $(0.41) ¦ $0.34 ¦ $1.84 ¦ $1.96 ⏎ Diluted average s |  |
| 3.18 | `0.41` | GAAP_DILUTED | current_quarter | Q4 FY2020 (three months ended February 29, 2020) | -0.41 | ,208 ⏎ Earnings (loss) per common share ⏎ Basic ¦ $(0.41) ¦ $0.34 ¦ $1.84 ¦ $1.97 ⏎ Diluted ¦ $([[0.41]]) ¦ $0.34 ¦ $1.84 ¦ $1.96 ⏎ Diluted average shares outstanding |  |
| 3.19 | `0.34` | GAAP_DILUTED | prior_year_quarter | Q4 FY2019 (three months ended February 28, 2019) | 0.34 | ings (loss) per common share ⏎ Basic ¦ $(0.41) ¦ $0.34 ¦ $1.84 ¦ $1.97 ⏎ Diluted ¦ $(0.41) ¦ $[[0.34]] ¦ $1.84 ¦ $1.96 ⏎ Diluted average shares outstanding ¦ 26,209 |  |
| 3.20 | `1.84` | GAAP_DILUTED | full_year | twelve months ended February 29, 2020 | 1.84 | ss) per common share ⏎ Basic ¦ $(0.41) ¦ $0.34 ¦ $1.84 ¦ $1.97 ⏎ Diluted ¦ $(0.41) ¦ $0.34 ¦ $[[1.84]] ¦ $1.96 ⏎ Diluted average shares outstanding ¦ 26,209 ¦ 26,15 |  |
| 3.21 | `1.96` | GAAP_DILUTED | full_year | twelve months ended February 28, 2019 | 1.96 | common share ⏎ Basic ¦ $(0.41) ¦ $0.34 ¦ $1.84 ¦ $1.97 ⏎ Diluted ¦ $(0.41) ¦ $0.34 ¦ $1.84 ¦ $[[1.96]] ⏎ Diluted average shares outstanding ¦ 26,209 ¦ 26,153 ¦ 26,2 |  |
| 3.22 | `0.41` | GAAP_DILUTED | current_quarter | three months ended February 29, 2020 | -0.41 | d Share ⏎ GAAP net income (loss) and GAAP diluted earnings (loss) per share ¦ $(10,643) ¦ $([[0.41]]) ¦ $48,234 ¦ $1.84 ⏎ Adjustments to reconcile GAAP to non-GAA |  |
| 3.23 | `1.84` | GAAP_DILUTED | full_year | twelve months ended February 29, 2020 | 1.84 | come (loss) and GAAP diluted earnings (loss) per share ¦ $(10,643) ¦ $(0.41) ¦ $48,234 ¦ $[[1.84]] ⏎ Adjustments to reconcile GAAP to non-GAAP financial measure |  |
| 3.24 | `0.47` | NON_GAAP | current_quarter | three months ended February 29, 2020 | 0.47 | 12 ¦ 0.88 ¦ 23,012 ¦ 0.87 ⏎ Non-GAAP net income and diluted earnings per share ¦ $12,369 ¦ $[[0.47]] ¦ $71,246 ¦ $2.71 ⏎ --END-- |  |
| 3.25 | `2.71` | NON_GAAP | full_year | twelve months ended February 29, 2020 | 2.71 |  ¦ 0.87 ⏎ Non-GAAP net income and diluted earnings per share ¦ $12,369 ¦ $0.47 ¦ $71,246 ¦ $[[2.71]] ⏎ --END-- |  |

**Missed mentions** (add `ADD:` lines below):


## 4. HORIZON BANCORP INC /IN/  (0000706129-20-000012)

Anchor (10-Q): **0.26** (us-gaap:EarningsPerShareDiluted) | Model primary: **0.26** | mentions: 59 | Reason in batch: random sample (unflagged)

| ID | Span | Type | Period kind | Period | Value | Context (span in [[ ]]) | Verdict |
|---|---|---|---|---|---|---|---|
| 4.1 | `0.26` | GAAP_DILUTED | current_quarter | Q1 2020 | 0.26 | s ¦ 2.38% ¦ 2.32% ¦ 2.80% ⏎ Net income for the first quarter of 2020 was $11.7 million, or $[[0.26]] diluted earnings per share, compared to $18.5 million, or $ |  |
| 4.2 | `0.41` | GAAP_DILUTED | prior_quarter | Q4 2019 | 0.41 | 20 was $11.7 million, or $0.26 diluted earnings per share, compared to $18.5 million, or $[[0.41]] diluted earnings per share, for the fourth quarter of 2019  |  |
| 4.3 | `0.28` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | 0.28 | r $0.41 diluted earnings per share, for the fourth quarter of 2019 and $10.8 million, or $[[0.28]] diluted earnings per share, for the first quarter of 2019.  |  |
| 4.4 | `0.24` | NON_GAAP | current_quarter | Q1 2020 | 0.24 | es and death benefit on bank owned life insurance‚ core net income was $11.2 million, or $[[0.24]] diluted earnings per share for the first quarter of 2020, c |  |
| 4.5 | `0.41` | NON_GAAP | prior_quarter | Q4 2019 | 0.41 |  diluted earnings per share for the first quarter of 2020, compared to $18.5 million, or $[[0.41]] diluted earnings per share, for the fourth quarter of 2019  |  |
| 4.6 | `0.37` | NON_GAAP | prior_year_quarter | Q1 2019 | 0.37 | r $0.41 diluted earnings per share, for the fourth quarter of 2019 and $14.2 million, or $[[0.37]] diluted earnings per share, for the first quarter of 2019.  |  |
| 4.7 | `0.26` | GAAP_DILUTED | current_quarter | Q1 2020 | 0.26 | come Statement Highlights ⏎ Net income for the first quarter of 2020 was $11.7 million, or $[[0.26]] diluted earnings per share, compared to $18.5 million, or $ |  |
| 4.8 | `0.41` | GAAP_DILUTED | prior_quarter | Q4 2019 | 0.41 | 20 was $11.7 million, or $0.26 diluted earnings per share, compared to $18.5 million, or $[[0.41]] diluted earnings per share, for the fourth quarter of 2019. |  |
| 4.9 | `0.24` | NON_GAAP | current_quarter | Q1 2020 | 0.24 | rth quarter of 2019. Core net income for the first quarter of 2020 was $11.2 million, or $[[0.24]] diluted earnings per share, compared to $18.5 million, or $ |  |
| 4.10 | `0.41` | NON_GAAP | prior_quarter | Q4 2019 | 0.41 | 20 was $11.2 million, or $0.24 diluted earnings per share, compared to $18.5 million, or $[[0.41]] diluted earnings per share, for the fourth quarter of 2019. |  |
| 4.11 | `0.26` | GAAP_DILUTED | current_quarter | Q1 2020 | 0.26 | erest income of $129,000. ⏎ Net income for the first quarter of 2020 was $11.7 million, or $[[0.26]] diluted earnings per share, compared to $10.8 million, or $ |  |
| 4.12 | `0.28` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | 0.28 | 20 was $11.7 million, or $0.26 diluted earnings per share, compared to $10.8 million, or $[[0.28]] diluted earnings per share for the first quarter of 2019. C |  |
| 4.13 | `0.24` | NON_GAAP | current_quarter | Q1 2020 | 0.24 | rst quarter of 2019. Core net income for the first quarter of 2020 was $11.2 million, or $[[0.24]] diluted earnings per share, compared to $14.2 million, or $ |  |
| 4.14 | `0.37` | NON_GAAP | prior_year_quarter | Q1 2019 | 0.37 | 20 was $11.2 million, or $0.24 diluted earnings per share, compared to $14.2 million, or $[[0.37]] diluted earnings per share for the first quarter of 2019. T |  |
| 4.15 | `0.26` | GAAP_DILUTED | current_quarter | Q1 2020 | 0.26 | ch 31, ⏎ 2020 ¦ 2019 ¦ 2019 ¦ 2019 ¦ 2019 ⏎ Diluted earnings per share (“EPS”) as reported ¦ $[[0.26]] ¦ $0.41 ¦ $0.46 ¦ $0.37 ¦ $0.28 ⏎ Merger expenses ¦ — ¦ — ¦ — |  |
| 4.16 | `0.41` | GAAP_DILUTED | prior_quarter | Q4 2019 | 0.41 | 020 ¦ 2019 ¦ 2019 ¦ 2019 ¦ 2019 ⏎ Diluted earnings per share (“EPS”) as reported ¦ $0.26 ¦ $[[0.41]] ¦ $0.46 ¦ $0.37 ¦ $0.28 ⏎ Merger expenses ¦ — ¦ — ¦ — ¦ 0.03  |  |
| 4.17 | `0.46` | GAAP_DILUTED | other | Q3 2019 | 0.46 | 19 ¦ 2019 ¦ 2019 ¦ 2019 ⏎ Diluted earnings per share (“EPS”) as reported ¦ $0.26 ¦ $0.41 ¦ $[[0.46]] ¦ $0.37 ¦ $0.28 ⏎ Merger expenses ¦ — ¦ — ¦ — ¦ 0.03 ¦ 0.11 ⏎ T |  |
| 4.18 | `0.37` | GAAP_DILUTED | other | Q2 2019 | 0.37 | 9 ¦ 2019 ¦ 2019 ⏎ Diluted earnings per share (“EPS”) as reported ¦ $0.26 ¦ $0.41 ¦ $0.46 ¦ $[[0.37]] ¦ $0.28 ⏎ Merger expenses ¦ — ¦ — ¦ — ¦ 0.03 ¦ 0.11 ⏎ Tax effec |  |
| 4.19 | `0.28` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | 0.28 |  ¦ 2019 ⏎ Diluted earnings per share (“EPS”) as reported ¦ $0.26 ¦ $0.41 ¦ $0.46 ¦ $0.37 ¦ $[[0.28]] ⏎ Merger expenses ¦ — ¦ — ¦ — ¦ 0.03 ¦ 0.11 ⏎ Tax effect ¦ — ¦  |  |
| 4.20 | `0.26` | NON_GAAP | current_quarter | Q1 2020 | 0.26 | ¦ 0.03 ¦ 0.11 ⏎ Tax effect ¦ — ¦ — ¦ — ¦ — ¦ (0.02) ⏎ Diluted EPS excluding merger expenses ¦ [[0.26]] ¦ 0.41 ¦ 0.46 ¦ 0.40 ¦ 0.37 ⏎ (Gain)/loss on sale of investme |  |
| 4.21 | `0.41` | NON_GAAP | prior_quarter | Q4 2019 | 0.41 | ¦ 0.11 ⏎ Tax effect ¦ — ¦ — ¦ — ¦ — ¦ (0.02) ⏎ Diluted EPS excluding merger expenses ¦ 0.26 ¦ [[0.41]] ¦ 0.46 ¦ 0.40 ¦ 0.37 ⏎ (Gain)/loss on sale of investment secu |  |
| 4.22 | `0.46` | NON_GAAP | other | Q3 2019 | 0.46 | Tax effect ¦ — ¦ — ¦ — ¦ — ¦ (0.02) ⏎ Diluted EPS excluding merger expenses ¦ 0.26 ¦ 0.41 ¦ [[0.46]] ¦ 0.40 ¦ 0.37 ⏎ (Gain)/loss on sale of investment securities  |  |
| 4.23 | `0.40` | NON_GAAP | other | Q2 2019 | 0.4 | ect ¦ — ¦ — ¦ — ¦ — ¦ (0.02) ⏎ Diluted EPS excluding merger expenses ¦ 0.26 ¦ 0.41 ¦ 0.46 ¦ [[0.40]] ¦ 0.37 ⏎ (Gain)/loss on sale of investment securities ¦ (0.01 |  |
| 4.24 | `0.37` | NON_GAAP | prior_year_quarter | Q1 2019 | 0.37 |  ¦ — ¦ — ¦ — ¦ (0.02) ⏎ Diluted EPS excluding merger expenses ¦ 0.26 ¦ 0.41 ¦ 0.46 ¦ 0.40 ¦ [[0.37]] ⏎ (Gain)/loss on sale of investment securities ¦ (0.01) ¦ — ¦ |  |
| 4.25 | `0.25` | NON_GAAP | current_quarter | Q1 2020 | 0.25 | x effect ¦ — ¦ — ¦ — ¦ — ¦ — ⏎ Diluted EPS excluding (gain)/loss on investment securities ¦ [[0.25]] ¦ 0.41 ¦ 0.46 ¦ 0.40 ¦ 0.37 ⏎ Death benefit on BOLI ¦ (0.01)  |  |
| 4.26 | `0.41` | NON_GAAP | prior_quarter | Q4 2019 | 0.41 | t ¦ — ¦ — ¦ — ¦ — ¦ — ⏎ Diluted EPS excluding (gain)/loss on investment securities ¦ 0.25 ¦ [[0.41]] ¦ 0.46 ¦ 0.40 ¦ 0.37 ⏎ Death benefit on BOLI ¦ (0.01) ¦ — ¦ ( |  |
| 4.27 | `0.46` | NON_GAAP | other | Q3 2019 | 0.46 |  — ¦ — ¦ — ¦ — ⏎ Diluted EPS excluding (gain)/loss on investment securities ¦ 0.25 ¦ 0.41 ¦ [[0.46]] ¦ 0.40 ¦ 0.37 ⏎ Death benefit on BOLI ¦ (0.01) ¦ — ¦ (0.01) ¦ |  |
| 4.28 | `0.40` | NON_GAAP | other | Q2 2019 | 0.4 | ¦ — ¦ — ⏎ Diluted EPS excluding (gain)/loss on investment securities ¦ 0.25 ¦ 0.41 ¦ 0.46 ¦ [[0.40]] ¦ 0.37 ⏎ Death benefit on BOLI ¦ (0.01) ¦ — ¦ (0.01) ¦ (0.01) |  |
| 4.29 | `0.37` | NON_GAAP | prior_year_quarter | Q1 2019 | 0.37 |  ⏎ Diluted EPS excluding (gain)/loss on investment securities ¦ 0.25 ¦ 0.41 ¦ 0.46 ¦ 0.40 ¦ [[0.37]] ⏎ Death benefit on BOLI ¦ (0.01) ¦ — ¦ (0.01) ¦ (0.01) ¦ — ⏎ Di |  |
| 4.30 | `0.24` | NON_GAAP | current_quarter | Q1 2020 | 0.24 |  on BOLI ¦ (0.01) ¦ — ¦ (0.01) ¦ (0.01) ¦ — ⏎ Diluted EPS excluding death benefit on BOLI ¦ [[0.24]] ¦ 0.41 ¦ 0.45 ¦ 0.39 ¦ 0.37 ⏎ Core Diluted EPS ¦ $0.24 ¦ $0.4 |  |
| 4.31 | `0.41` | NON_GAAP | prior_quarter | Q4 2019 | 0.41 | I ¦ (0.01) ¦ — ¦ (0.01) ¦ (0.01) ¦ — ⏎ Diluted EPS excluding death benefit on BOLI ¦ 0.24 ¦ [[0.41]] ¦ 0.45 ¦ 0.39 ¦ 0.37 ⏎ Core Diluted EPS ¦ $0.24 ¦ $0.41 ¦ $0. |  |
| 4.32 | `0.45` | NON_GAAP | other | Q3 2019 | 0.45 | 01) ¦ — ¦ (0.01) ¦ (0.01) ¦ — ⏎ Diluted EPS excluding death benefit on BOLI ¦ 0.24 ¦ 0.41 ¦ [[0.45]] ¦ 0.39 ¦ 0.37 ⏎ Core Diluted EPS ¦ $0.24 ¦ $0.41 ¦ $0.45 ¦ $0 |  |
| 4.33 | `0.39` | NON_GAAP | other | Q2 2019 | 0.39 |  ¦ (0.01) ¦ (0.01) ¦ — ⏎ Diluted EPS excluding death benefit on BOLI ¦ 0.24 ¦ 0.41 ¦ 0.45 ¦ [[0.39]] ¦ 0.37 ⏎ Core Diluted EPS ¦ $0.24 ¦ $0.41 ¦ $0.45 ¦ $0.39 ¦ $ |  |
| 4.34 | `0.37` | NON_GAAP | prior_year_quarter | Q1 2019 | 0.37 | 1) ¦ (0.01) ¦ — ⏎ Diluted EPS excluding death benefit on BOLI ¦ 0.24 ¦ 0.41 ¦ 0.45 ¦ 0.39 ¦ [[0.37]] ⏎ Core Diluted EPS ¦ $0.24 ¦ $0.41 ¦ $0.45 ¦ $0.39 ¦ $0.37 ⏎ 5 ⏎  |  |
| 4.35 | `0.24` | NON_GAAP | current_quarter | Q1 2020 | 0.24 | PS excluding death benefit on BOLI ¦ 0.24 ¦ 0.41 ¦ 0.45 ¦ 0.39 ¦ 0.37 ⏎ Core Diluted EPS ¦ $[[0.24]] ¦ $0.41 ¦ $0.45 ¦ $0.39 ¦ $0.37 ⏎ 5 ⏎ Horizon Bancorp, Inc. Ann |  |
| 4.36 | `0.41` | NON_GAAP | prior_quarter | Q4 2019 | 0.41 | ding death benefit on BOLI ¦ 0.24 ¦ 0.41 ¦ 0.45 ¦ 0.39 ¦ 0.37 ⏎ Core Diluted EPS ¦ $0.24 ¦ $[[0.41]] ¦ $0.45 ¦ $0.39 ¦ $0.37 ⏎ 5 ⏎ Horizon Bancorp, Inc. Announces F |  |
| 4.37 | `0.45` | NON_GAAP | other | Q3 2019 | 0.45 | th benefit on BOLI ¦ 0.24 ¦ 0.41 ¦ 0.45 ¦ 0.39 ¦ 0.37 ⏎ Core Diluted EPS ¦ $0.24 ¦ $0.41 ¦ $[[0.45]] ¦ $0.39 ¦ $0.37 ⏎ 5 ⏎ Horizon Bancorp, Inc. Announces First Qua |  |
| 4.38 | `0.39` | NON_GAAP | other | Q2 2019 | 0.39 | it on BOLI ¦ 0.24 ¦ 0.41 ¦ 0.45 ¦ 0.39 ¦ 0.37 ⏎ Core Diluted EPS ¦ $0.24 ¦ $0.41 ¦ $0.45 ¦ $[[0.39]] ¦ $0.37 ⏎ 5 ⏎ Horizon Bancorp, Inc. Announces First Quarter 202 |  |
| 4.39 | `0.37` | NON_GAAP | prior_year_quarter | Q1 2019 | 0.37 | LI ¦ 0.24 ¦ 0.41 ¦ 0.45 ¦ 0.39 ¦ 0.37 ⏎ Core Diluted EPS ¦ $0.24 ¦ $0.41 ¦ $0.45 ¦ $0.39 ¦ $[[0.37]] ⏎ 5 ⏎ Horizon Bancorp, Inc. Announces First Quarter 2020 Financ |  |
| 4.40 | `0.26` | GAAP_BASIC | current_quarter | Q1 2020 | 0.26 | 1,655 ¦ $18,543 ¦ $20,537 ¦ $16,642 ¦ $10,816 ⏎ Per share data: ⏎ Basic earnings per share ¦ $[[0.26]] ¦ $0.41 ¦ $0.46 ¦ $0.37 ¦ $0.28 ⏎ Diluted earnings per share  |  |
| 4.41 | `0.41` | GAAP_BASIC | prior_quarter | Q4 2019 | 0.41 | $18,543 ¦ $20,537 ¦ $16,642 ¦ $10,816 ⏎ Per share data: ⏎ Basic earnings per share ¦ $0.26 ¦ $[[0.41]] ¦ $0.46 ¦ $0.37 ¦ $0.28 ⏎ Diluted earnings per share ¦ 0.26 ¦ |  |
| 4.42 | `0.46` | GAAP_BASIC | other | Q3 2019 | 0.46 | ¦ $20,537 ¦ $16,642 ¦ $10,816 ⏎ Per share data: ⏎ Basic earnings per share ¦ $0.26 ¦ $0.41 ¦ $[[0.46]] ¦ $0.37 ¦ $0.28 ⏎ Diluted earnings per share ¦ 0.26 ¦ 0.41 ¦  |  |
| 4.43 | `0.37` | GAAP_BASIC | other | Q2 2019 | 0.37 | 7 ¦ $16,642 ¦ $10,816 ⏎ Per share data: ⏎ Basic earnings per share ¦ $0.26 ¦ $0.41 ¦ $0.46 ¦ $[[0.37]] ¦ $0.28 ⏎ Diluted earnings per share ¦ 0.26 ¦ 0.41 ¦ 0.46 ¦ 0 |  |
| 4.44 | `0.28` | GAAP_BASIC | prior_year_quarter | Q1 2019 | 0.28 | 642 ¦ $10,816 ⏎ Per share data: ⏎ Basic earnings per share ¦ $0.26 ¦ $0.41 ¦ $0.46 ¦ $0.37 ¦ $[[0.28]] ⏎ Diluted earnings per share ¦ 0.26 ¦ 0.41 ¦ 0.46 ¦ 0.37 ¦ 0. |  |
| 4.45 | `0.26` | GAAP_DILUTED | current_quarter | Q1 2020 | 0.26 | c earnings per share ¦ $0.26 ¦ $0.41 ¦ $0.46 ¦ $0.37 ¦ $0.28 ⏎ Diluted earnings per share ¦ [[0.26]] ¦ 0.41 ¦ 0.46 ¦ 0.37 ¦ 0.28 ⏎ Cash dividends declared per com |  |
| 4.46 | `0.41` | GAAP_DILUTED | prior_quarter | Q4 2019 | 0.41 | ngs per share ¦ $0.26 ¦ $0.41 ¦ $0.46 ¦ $0.37 ¦ $0.28 ⏎ Diluted earnings per share ¦ 0.26 ¦ [[0.41]] ¦ 0.46 ¦ 0.37 ¦ 0.28 ⏎ Cash dividends declared per common sha |  |
| 4.47 | `0.46` | GAAP_DILUTED | other | Q3 2019 | 0.46 |  share ¦ $0.26 ¦ $0.41 ¦ $0.46 ¦ $0.37 ¦ $0.28 ⏎ Diluted earnings per share ¦ 0.26 ¦ 0.41 ¦ [[0.46]] ¦ 0.37 ¦ 0.28 ⏎ Cash dividends declared per common share ¦ 0. |  |
| 4.48 | `0.37` | GAAP_DILUTED | other | Q2 2019 | 0.37 | ¦ $0.26 ¦ $0.41 ¦ $0.46 ¦ $0.37 ¦ $0.28 ⏎ Diluted earnings per share ¦ 0.26 ¦ 0.41 ¦ 0.46 ¦ [[0.37]] ¦ 0.28 ⏎ Cash dividends declared per common share ¦ 0.12 ¦ 0. |  |
| 4.49 | `0.28` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | 0.28 |  ¦ $0.41 ¦ $0.46 ¦ $0.37 ¦ $0.28 ⏎ Diluted earnings per share ¦ 0.26 ¦ 0.41 ¦ 0.46 ¦ 0.37 ¦ [[0.28]] ⏎ Cash dividends declared per common share ¦ 0.12 ¦ 0.12 ¦ 0. |  |
| 4.50 | `0.26` | GAAP_BASIC | current_quarter | Q1 2020 | 0.26 |  ⏎ Net Income ¦ $11,655 ¦ $18,543 ¦ $20,537 ¦ $16,642 ¦ $10,816 ⏎ Basic Earnings Per Share ¦ $[[0.26]] ¦ $0.41 ¦ $0.46 ¦ $0.37 ¦ $0.28 ⏎ Diluted Earnings Per Share  |  |
| 4.51 | `0.41` | GAAP_BASIC | prior_quarter | Q4 2019 | 0.41 | ome ¦ $11,655 ¦ $18,543 ¦ $20,537 ¦ $16,642 ¦ $10,816 ⏎ Basic Earnings Per Share ¦ $0.26 ¦ $[[0.41]] ¦ $0.46 ¦ $0.37 ¦ $0.28 ⏎ Diluted Earnings Per Share ¦ 0.26 ¦ |  |
| 4.52 | `0.46` | GAAP_BASIC | other | Q3 2019 | 0.46 | 1,655 ¦ $18,543 ¦ $20,537 ¦ $16,642 ¦ $10,816 ⏎ Basic Earnings Per Share ¦ $0.26 ¦ $0.41 ¦ $[[0.46]] ¦ $0.37 ¦ $0.28 ⏎ Diluted Earnings Per Share ¦ 0.26 ¦ 0.41 ¦  |  |
| 4.53 | `0.37` | GAAP_BASIC | other | Q2 2019 | 0.37 | $18,543 ¦ $20,537 ¦ $16,642 ¦ $10,816 ⏎ Basic Earnings Per Share ¦ $0.26 ¦ $0.41 ¦ $0.46 ¦ $[[0.37]] ¦ $0.28 ⏎ Diluted Earnings Per Share ¦ 0.26 ¦ 0.41 ¦ 0.46 ¦ 0 |  |
| 4.54 | `0.28` | GAAP_BASIC | prior_year_quarter | Q1 2019 | 0.28 | ¦ $20,537 ¦ $16,642 ¦ $10,816 ⏎ Basic Earnings Per Share ¦ $0.26 ¦ $0.41 ¦ $0.46 ¦ $0.37 ¦ $[[0.28]] ⏎ Diluted Earnings Per Share ¦ 0.26 ¦ 0.41 ¦ 0.46 ¦ 0.37 ¦ 0. |  |
| 4.55 | `0.26` | GAAP_DILUTED | current_quarter | Q1 2020 | 0.26 | c Earnings Per Share ¦ $0.26 ¦ $0.41 ¦ $0.46 ¦ $0.37 ¦ $0.28 ⏎ Diluted Earnings Per Share ¦ [[0.26]] ¦ 0.41 ¦ 0.46 ¦ 0.37 ¦ 0.28 ⏎ 18 |  |
| 4.56 | `0.41` | GAAP_DILUTED | prior_quarter | Q4 2019 | 0.41 | ngs Per Share ¦ $0.26 ¦ $0.41 ¦ $0.46 ¦ $0.37 ¦ $0.28 ⏎ Diluted Earnings Per Share ¦ 0.26 ¦ [[0.41]] ¦ 0.46 ¦ 0.37 ¦ 0.28 ⏎ 18 |  |
| 4.57 | `0.46` | GAAP_DILUTED | other | Q3 2019 | 0.46 |  Share ¦ $0.26 ¦ $0.41 ¦ $0.46 ¦ $0.37 ¦ $0.28 ⏎ Diluted Earnings Per Share ¦ 0.26 ¦ 0.41 ¦ [[0.46]] ¦ 0.37 ¦ 0.28 ⏎ 18 |  |
| 4.58 | `0.37` | GAAP_DILUTED | other | Q2 2019 | 0.37 | ¦ $0.26 ¦ $0.41 ¦ $0.46 ¦ $0.37 ¦ $0.28 ⏎ Diluted Earnings Per Share ¦ 0.26 ¦ 0.41 ¦ 0.46 ¦ [[0.37]] ¦ 0.28 ⏎ 18 |  |
| 4.59 | `0.28` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | 0.28 |  ¦ $0.41 ¦ $0.46 ¦ $0.37 ¦ $0.28 ⏎ Diluted Earnings Per Share ¦ 0.26 ¦ 0.41 ¦ 0.46 ¦ 0.37 ¦ [[0.28]] ⏎ 18 |  |

**Missed mentions** (add `ADD:` lines below):


## 5. BRIDGE BANCORP, INC.  (0000846617-20-000024)

Anchor (10-Q): **0.47** (us-gaap:EarningsPerShareDiluted) | Model primary: **0.47** | mentions: 9 | Reason in batch: random sample (unflagged)

| ID | Span | Type | Period kind | Period | Value | Context (span in [[ ]]) | Verdict |
|---|---|---|---|---|---|---|---|
| 5.1 | `0.47` | GAAP_DILUTED | current_quarter | Q1 2020 | 0.47 | inancial results included: ⏎ · ¦ Net income for the 2020 first quarter of $9.3 million, or $[[0.47]] per diluted share. ⏎ · ¦ Net interest income for the 2020 fir |  |
| 5.2 | `0.47` | GAAP_DILUTED | current_quarter | Q1 2020 | 0.47 | ses.” ⏎ Net Earnings and Returns ⏎ Net income in the 2020 first quarter was $9.3 million, or $[[0.47]] per diluted share, a decrease of $3.6 million compared to t |  |
| 5.3 | `0.47` | GAAP_DILUTED | current_quarter | Q1 2020 | 0.47 | tangible common equity was 9.59% for the 2020 first quarter. ⏎ “Our reported net income of $[[0.47]] per diluted share was impacted by a higher provision for cr |  |
| 5.4 | `0.47` | GAAP_BASIC | current_quarter | Q1 2020 | 0.47 | e common shares outstanding ¦ 19,532 ¦ 19,538 ¦ 19,500 ⏎ Basic earnings per common share ¦ $[[0.47]] ¦ $0.71 ¦ $0.65 ⏎ Weighted average common shares outstanding  |  |
| 5.5 | `0.71` | GAAP_BASIC | prior_quarter | Q4 2019 | 0.71 |  shares outstanding ¦ 19,532 ¦ 19,538 ¦ 19,500 ⏎ Basic earnings per common share ¦ $0.47 ¦ $[[0.71]] ¦ $0.65 ⏎ Weighted average common shares outstanding ¦ 19,532 |  |
| 5.6 | `0.65` | GAAP_BASIC | prior_year_quarter | Q1 2019 | 0.65 | outstanding ¦ 19,532 ¦ 19,538 ¦ 19,500 ⏎ Basic earnings per common share ¦ $0.47 ¦ $0.71 ¦ $[[0.65]] ⏎ Weighted average common shares outstanding ¦ 19,532 ¦ 19,53 |  |
| 5.7 | `0.47` | GAAP_DILUTED | current_quarter | Q1 2020 | 0.47 | valent shares outstanding ¦ 19,566 ¦ 19,578 ¦ 19,526 ⏎ Diluted earnings per common share ¦ $[[0.47]] ¦ $0.71 ¦ $0.65 ⏎ BRIDGE BANCORP, INC. AND SUBSIDIARIES ⏎ Conso |  |
| 5.8 | `0.71` | GAAP_DILUTED | prior_quarter | Q4 2019 | 0.71 | hares outstanding ¦ 19,566 ¦ 19,578 ¦ 19,526 ⏎ Diluted earnings per common share ¦ $0.47 ¦ $[[0.71]] ¦ $0.65 ⏎ BRIDGE BANCORP, INC. AND SUBSIDIARIES ⏎ Consolidated  |  |
| 5.9 | `0.65` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | 0.65 | tstanding ¦ 19,566 ¦ 19,578 ¦ 19,526 ⏎ Diluted earnings per common share ¦ $0.47 ¦ $0.71 ¦ $[[0.65]] ⏎ BRIDGE BANCORP, INC. AND SUBSIDIARIES ⏎ Consolidated Financia |  |

**Missed mentions** (add `ADD:` lines below):


## 6. HARTFORD FINANCIAL SERVICES GROUP, INC.  (0000874766-20-000033)

Anchor (10-Q): **0.74** (us-gaap:EarningsPerShareDiluted) | Model primary: **0.74** | mentions: 12 | Reason in batch: random sample (unflagged)

| ID | Span | Type | Period kind | Period | Value | Context (span in [[ ]]) | Verdict |
|---|---|---|---|---|---|---|---|
| 6.1 | `0.74` | GAAP_DILUTED | current_quarter | Q1 2020 | 0.74 | D-19 ⏎ • ¦ First quarter 2020 net income available to common stockholders of $268 million ($[[0.74]] per diluted share) decreased 57% from first quarter 2019, a |  |
| 6.2 | `1.34` | NON_GAAP | current_quarter | Q1 2020 | 1.34 | st quarter 2019, and core earnings* of $485 million (core earnings per diluted share* of $[[1.34]]) declined 4% from first quarter 2019 ⏎ • ¦ Net income ROE for |  |
| 6.3 | `0.74` | GAAP_DILUTED | current_quarter | Q1 2020 | 0.74 | s ¦ $268 ¦ $625 ¦ (57)% ⏎ Net income available to common stockholders per diluted share2 ¦ $[[0.74]] ¦ $1.71 ¦ (57)% ⏎ Core earnings ¦ $485 ¦ $507 ¦ (4)% ⏎ Core ear |  |
| 6.4 | `1.71` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | 1.71 |  ¦ $625 ¦ (57)% ⏎ Net income available to common stockholders per diluted share2 ¦ $0.74 ¦ $[[1.71]] ¦ (57)% ⏎ Core earnings ¦ $485 ¦ $507 ¦ (4)% ⏎ Core earnings pe |  |
| 6.5 | `1.34` | NON_GAAP | current_quarter | Q1 2020 | 1.34 | .74 ¦ $1.71 ¦ (57)% ⏎ Core earnings ¦ $485 ¦ $507 ¦ (4)% ⏎ Core earnings per diluted share ¦ $[[1.34]] ¦ $1.39 ¦ (4)% ⏎ Book value per diluted share ¦ $41.42 ¦ $38. |  |
| 6.6 | `1.39` | NON_GAAP | prior_year_quarter | Q1 2019 | 1.39 | .71 ¦ (57)% ⏎ Core earnings ¦ $485 ¦ $507 ¦ (4)% ⏎ Core earnings per diluted share ¦ $1.34 ¦ $[[1.39]] ¦ (4)% ⏎ Book value per diluted share ¦ $41.42 ¦ $38.36 ¦ 8% ⏎  |  |
| 6.7 | `0.74` | GAAP_DILUTED | current_quarter | Q1 2020 | 0.74 | AOCI ⏎ First quarter 2020 net income available to common stockholders was $268 million, or $[[0.74]] per diluted share, down 57% from first quarter 2019. The de |  |
| 6.8 | `1.34` | NON_GAAP | current_quarter | Q1 2020 | 1.34 | ognized as a deferred gain on retroactive reinsurance. ⏎ Core earnings of $485 million, or $[[1.34]] per diluted share, declined 4% from first quarter 2019, pri |  |
| 6.9 | `0.74` | GAAP_DILUTED | current_quarter | Q1 2020 | 0.74 | uted earnings per common share: ⏎ Net income available to common stockholders per share1 ¦ $[[0.74]] ¦ $1.71 ¦ (57)% ⏎ Adjustment made to reconcile net income ava |  |
| 6.10 | `1.71` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | 1.71 | nings per common share: ⏎ Net income available to common stockholders per share1 ¦ $0.74 ¦ $[[1.71]] ¦ (57)% ⏎ Adjustment made to reconcile net income available t |  |
| 6.11 | `1.34` | NON_GAAP | current_quarter | Q1 2020 | 1.34 | fit) on items excluded from core earnings ¦ (0.16) ¦ 0.09 ¦ NM ⏎ Core earnings per share ¦ $[[1.34]] ¦ $1.39 ¦ (4)% ⏎ [1] Net income (loss) available to common st |  |
| 6.12 | `1.39` | NON_GAAP | prior_year_quarter | Q1 2019 | 1.39 | items excluded from core earnings ¦ (0.16) ¦ 0.09 ¦ NM ⏎ Core earnings per share ¦ $1.34 ¦ $[[1.39]] ¦ (4)% ⏎ [1] Net income (loss) available to common stockholde |  |

**Missed mentions** (add `ADD:` lines below):


## 7. VERTEX PHARMACEUTICALS INC / MA  (0000875320-20-000014)

Anchor (10-Q): **2.29** (us-gaap:EarningsPerShareDiluted) | Model primary: **2.29** | mentions: 12 | Reason in batch: random sample (unflagged)

| ID | Span | Type | Period kind | Period | Value | Context (span in [[ ]]) | Verdict |
|---|---|---|---|---|---|---|---|
| 7.1 | `2.29` | GAAP_DILUTED | current_quarter | Q1 2020 | 2.29 | 69 ¦ 124% ⏎ Non-GAAP Net income ¦ $674 ¦ $296 ¦ 128% ⏎ GAAP Net income per share - diluted ¦ $[[2.29]] ¦ $1.03 ¦ 122% ⏎ Non-GAAP Net income per share - diluted ¦ $2 |  |
| 7.2 | `1.03` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | 1.03 | % ⏎ Non-GAAP Net income ¦ $674 ¦ $296 ¦ 128% ⏎ GAAP Net income per share - diluted ¦ $2.29 ¦ $[[1.03]] ¦ 122% ⏎ Non-GAAP Net income per share - diluted ¦ $2.56 ¦ $1 |  |
| 7.3 | `2.56` | NON_GAAP | current_quarter | Q1 2020 | 2.56 | ome per share - diluted ¦ $2.29 ¦ $1.03 ¦ 122% ⏎ Non-GAAP Net income per share - diluted ¦ $[[2.56]] ¦ $1.14 ¦ 125% ⏎ 1 ⏎ Total product revenues increased 77% compa |  |
| 7.4 | `1.14` | NON_GAAP | prior_year_quarter | Q1 2019 | 1.14 | share - diluted ¦ $2.29 ¦ $1.03 ¦ 122% ⏎ Non-GAAP Net income per share - diluted ¦ $2.56 ¦ $[[1.14]] ¦ 125% ⏎ 1 ⏎ Total product revenues increased 77% compared to t |  |
| 7.5 | `2.32` | GAAP_BASIC | current_quarter | Q1 2020 | 2.32 |  ¦ 54,781 ¦ 51,534 ⏎ Net income ¦ $602,753 ¦ $268,631 ⏎ Net income per common share: ⏎ Basic ¦ $[[2.32]] ¦ $1.05 ⏎ Diluted ¦ $2.29 ¦ $1.03 ⏎ Shares used in per share ca |  |
| 7.6 | `1.05` | GAAP_BASIC | prior_year_quarter | Q1 2019 | 1.05 | 1 ¦ 51,534 ⏎ Net income ¦ $602,753 ¦ $268,631 ⏎ Net income per common share: ⏎ Basic ¦ $2.32 ¦ $[[1.05]] ⏎ Diluted ¦ $2.29 ¦ $1.03 ⏎ Shares used in per share calculatio |  |
| 7.7 | `2.29` | GAAP_DILUTED | current_quarter | Q1 2020 | 2.29 | ncome ¦ $602,753 ¦ $268,631 ⏎ Net income per common share: ⏎ Basic ¦ $2.32 ¦ $1.05 ⏎ Diluted ¦ $[[2.29]] ¦ $1.03 ⏎ Shares used in per share calculations: ⏎ Basic ¦ 259, |  |
| 7.8 | `1.03` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | 1.03 | $602,753 ¦ $268,631 ⏎ Net income per common share: ⏎ Basic ¦ $2.32 ¦ $1.05 ⏎ Diluted ¦ $2.29 ¦ $[[1.03]] ⏎ Shares used in per share calculations: ⏎ Basic ¦ 259,815 ¦ 25 |  |
| 7.9 | `2.29` | GAAP_DILUTED | current_quarter | Q1 2020 | 2.29 | 2) ⏎ Non-GAAP net income ¦ $674,454 ¦ $295,830 ⏎ Net income per diluted common share: ⏎ GAAP ¦ $[[2.29]] ¦ $1.03 ⏎ Non-GAAP ¦ $2.56 ¦ $1.14 ⏎ Shares used in diluted per |  |
| 7.10 | `1.03` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | 1.03 | AAP net income ¦ $674,454 ¦ $295,830 ⏎ Net income per diluted common share: ⏎ GAAP ¦ $2.29 ¦ $[[1.03]] ⏎ Non-GAAP ¦ $2.56 ¦ $1.14 ⏎ Shares used in diluted per share c |  |
| 7.11 | `2.56` | NON_GAAP | current_quarter | Q1 2020 | 2.56 | $674,454 ¦ $295,830 ⏎ Net income per diluted common share: ⏎ GAAP ¦ $2.29 ¦ $1.03 ⏎ Non-GAAP ¦ $[[2.56]] ¦ $1.14 ⏎ Shares used in diluted per share calculations: ⏎ GAAP |  |
| 7.12 | `1.14` | NON_GAAP | prior_year_quarter | Q1 2019 | 1.14 |  ¦ $295,830 ⏎ Net income per diluted common share: ⏎ GAAP ¦ $2.29 ¦ $1.03 ⏎ Non-GAAP ¦ $2.56 ¦ $[[1.14]] ⏎ Shares used in diluted per share calculations: ⏎ GAAP and Non |  |

**Missed mentions** (add `ADD:` lines below):


## 8. SiteOne Landscape Supply, Inc.  (0001104659-20-052683)

Anchor (10-Q): **-0.42** (us-gaap:EarningsPerShareDiluted) | Model primary: **-0.42** | mentions: 4 | Reason in batch: random sample (unflagged)

| ID | Span | Type | Period kind | Period | Value | Context (span in [[ ]]) | Verdict |
|---|---|---|---|---|---|---|---|
| 8.1 | `0.42` | GAAP_BASIC | current_quarter | Q1 2020 | -0.42 | enefit ¦ (13.5) ¦ (9.6) ⏎ Net loss ¦ $(17.5) ¦ $(24.1) ⏎ Net loss per common share: ⏎ Basic ¦ $([[0.42]]) ¦ $(0.59) ⏎ Diluted ¦ $(0.42) ¦ $(0.59) ⏎ Weighted average num |  |
| 8.2 | `0.59` | GAAP_BASIC | prior_year_quarter | Q1 2019 | -0.59 | 13.5) ¦ (9.6) ⏎ Net loss ¦ $(17.5) ¦ $(24.1) ⏎ Net loss per common share: ⏎ Basic ¦ $(0.42) ¦ $([[0.59]]) ⏎ Diluted ¦ $(0.42) ¦ $(0.59) ⏎ Weighted average number of com |  |
| 8.3 | `0.42` | GAAP_DILUTED | current_quarter | Q1 2020 | -0.42 | loss ¦ $(17.5) ¦ $(24.1) ⏎ Net loss per common share: ⏎ Basic ¦ $(0.42) ¦ $(0.59) ⏎ Diluted ¦ $([[0.42]]) ¦ $(0.59) ⏎ Weighted average number of common shares outstan |  |
| 8.4 | `0.59` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | -0.59 | 7.5) ¦ $(24.1) ⏎ Net loss per common share: ⏎ Basic ¦ $(0.42) ¦ $(0.59) ⏎ Diluted ¦ $(0.42) ¦ $([[0.59]]) ⏎ Weighted average number of common shares outstanding: ⏎ Basi |  |

**Missed mentions** (add `ADD:` lines below):


## 9. MDC PARTNERS INC  (0001104659-20-052792)

Anchor (10-Q): **None** (unanchored) | Model primary: **-0.03** | mentions: 6 | Reason in batch: random sample (unflagged)

| ID | Span | Type | Period kind | Period | Value | Context (span in [[ ]]) | Verdict |
|---|---|---|---|---|---|---|---|
| 9.1 | `0.03` | GAAP_DILUTED | current_quarter | Q1 2020 | -0.03 | share attributable to MDC Partners common shareholders for the first quarter of 2020 was $[[0.03]] versus diluted loss ⏎ per share of $0.04 for the first quarte |  |
| 9.2 | `0.04` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | -0.04 | on shareholders for the first quarter of 2020 was $0.03 versus diluted loss ⏎ per share of $[[0.04]] for the first quarter of ⏎ 2019. ⏎ Adjusted EBITDA for the firs |  |
| 9.3 | `0.03` | GAAP_BASIC | current_quarter | Q1 2020 | -0.03 | er Common Share: ⏎ Basic ⏎ Net loss attributable to MDC Partners Inc. common shareholders ¦ $([[0.03]]) ¦ $(0.04) ⏎ Diluted ⏎ Net loss attributable to MDC Partners In |  |
| 9.4 | `0.04` | GAAP_BASIC | prior_year_quarter | Q1 2019 | -0.04 | Share: ⏎ Basic ⏎ Net loss attributable to MDC Partners Inc. common shareholders ¦ $(0.03) ¦ $([[0.04]]) ⏎ Diluted ⏎ Net loss attributable to MDC Partners Inc. common  |  |
| 9.5 | `0.03` | GAAP_DILUTED | current_quarter | Q1 2020 | -0.03 | .03) ¦ $(0.04) ⏎ Diluted ⏎ Net loss attributable to MDC Partners Inc. common shareholders ¦ $([[0.03]]) ¦ $(0.04) ⏎ Weighted Average Number of Common Shares Outstan |  |
| 9.6 | `0.04` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | -0.04 | .04) ⏎ Diluted ⏎ Net loss attributable to MDC Partners Inc. common shareholders ¦ $(0.03) ¦ $([[0.04]]) ⏎ Weighted Average Number of Common Shares Outstanding: ⏎ Basi |  |

**Missed mentions** (add `ADD:` lines below):


## 10. TETRA TECH INC  (0001104659-20-053534)

Anchor (10-Q): **0.66** (us-gaap:EarningsPerShareDiluted) | Model primary: **0.66** | mentions: 22 | Reason in batch: random sample (unflagged)

| ID | Span | Type | Period kind | Period | Value | Context (span in [[ ]]) | Verdict |
|---|---|---|---|---|---|---|---|
| 10.1 | `0.66` | GAAP_DILUTED | current_quarter | Q2 fiscal 2020 | 0.66 | Quarter 2020 ⏎ Results ⏎ · ¦ Revenue of $734 million and Net Revenue of $584 million ⏎ · ¦ EPS $[[0.66]]; Adjusted EPS $0.73 ⏎ · ¦ Increased quarterly dividend by 13% |  |
| 10.2 | `0.73` | NON_GAAP | current_quarter | Q2 fiscal 2020 | 0.73 |  ⏎ · ¦ Revenue of $734 million and Net Revenue of $584 million ⏎ · ¦ EPS $0.66; Adjusted EPS $[[0.73]] ⏎ · ¦ Increased quarterly dividend by 13% to $0.17 ⏎ Pasadena,  |  |
| 10.3 | `0.66` | GAAP_DILUTED | current_quarter | Q2 fiscal 2020 | 0.66 | ed ⏎ revenue1 totaled $740 million and adjusted net revenue1 totaled $590 million. EPS was $[[0.66]] on a GAAP ⏎ basis, down 34% year-over-year primarily due to a |  |
| 10.4 | `0.73` | NON_GAAP | current_quarter | Q2 fiscal 2020 | 0.73 | non-recurring tax benefit amounting to $0.39 of EPS in the prior year. ⏎ Adjusted EPS1 was $[[0.73]], up 4% year-over-year. Backlog at the end of the quarter in |  |
| 10.5 | `1.51` | GAAP_DILUTED | current_ytd | six months ended March 29, 2020 | 1.51 | scal 2019. Operating income ⏎ for the six-month period was $111 million, up 7% and EPS was $[[1.51]], down 13% compared to the same period in fiscal 2019, prima |  |
| 10.6 | `1.57` | NON_GAAP | current_ytd | six months ended March 29, 2020 | 1.57 | recurring tax benefits amounting to $0.43 of EPS in the prior year. Adjusted EPS totaled $[[1.57]], up 12% year-over-year. ⏎ Liquidity and Capital Allocation ⏎ As |  |
| 10.7 | `0.66` | GAAP_DILUTED | current_quarter | Q2 fiscal 2020 | 0.66 | 165 ⏎ Adjusted Net Revenue ¦ $590,145 ¦ $590,125 ¦ 0% ¦ $1,204,167 ¦ $1,142,912 ¦ 5% ⏎ EPS ¦ $[[0.66]] ¦ $1.00 ¦ (34%) ¦ $1.51 ¦ $1.74 ¦ (13%) ⏎ Non-core Equipment  |  |
| 10.8 | `1.00` | GAAP_DILUTED | prior_year_quarter | Q2 fiscal 2019 | 1.0 | sted Net Revenue ¦ $590,145 ¦ $590,125 ¦ 0% ¦ $1,204,167 ¦ $1,142,912 ¦ 5% ⏎ EPS ¦ $0.66 ¦ $[[1.00]] ¦ (34%) ¦ $1.51 ¦ $1.74 ¦ (13%) ⏎ Non-core Equipment Disposit |  |
| 10.9 | `1.51` | GAAP_DILUTED | current_ytd | six months ended March 29, 2020 | 1.51 |  ¦ $590,145 ¦ $590,125 ¦ 0% ¦ $1,204,167 ¦ $1,142,912 ¦ 5% ⏎ EPS ¦ $0.66 ¦ $1.00 ¦ (34%) ¦ $[[1.51]] ¦ $1.74 ¦ (13%) ⏎ Non-core Equipment Disposition ¦ (0.03) ¦ - |  |
| 10.10 | `1.74` | GAAP_DILUTED | prior_ytd | six months ended March 31, 2019 | 1.74 | 145 ¦ $590,125 ¦ 0% ¦ $1,204,167 ¦ $1,142,912 ¦ 5% ⏎ EPS ¦ $0.66 ¦ $1.00 ¦ (34%) ¦ $1.51 ¦ $[[1.74]] ¦ (13%) ⏎ Non-core Equipment Disposition ¦ (0.03) ¦ - ¦ (0.04 |  |
| 10.11 | `0.73` | NON_GAAP | current_quarter | Q2 fiscal 2020 | 0.73 |  - ¦ 0.08 ¦ - ¦ 0.08 ⏎ Non-recurring Tax Benefits ¦ - ¦ (0.39) ¦ - ¦ (0.43) ⏎ Adjusted EPS ¦ $[[0.73]] ¦ $0.70 ¦ 4% ¦ $1.57 ¦ $1.40 ¦ 12% ⏎ March 29, 2020 ⏎ Current P |  |
| 10.12 | `0.70` | NON_GAAP | prior_year_quarter | Q2 fiscal 2019 | 0.7 | 8 ¦ - ¦ 0.08 ⏎ Non-recurring Tax Benefits ¦ - ¦ (0.39) ¦ - ¦ (0.43) ⏎ Adjusted EPS ¦ $0.73 ¦ $[[0.70]] ¦ 4% ¦ $1.57 ¦ $1.40 ¦ 12% ⏎ March 29, 2020 ⏎ Current Portion o |  |
| 10.13 | `1.57` | NON_GAAP | current_ytd | six months ended March 29, 2020 | 1.57 | Non-recurring Tax Benefits ¦ - ¦ (0.39) ¦ - ¦ (0.43) ⏎ Adjusted EPS ¦ $0.73 ¦ $0.70 ¦ 4% ¦ $[[1.57]] ¦ $1.40 ¦ 12% ⏎ March 29, 2020 ⏎ Current Portion of Long-term D |  |
| 10.14 | `1.40` | NON_GAAP | prior_ytd | six months ended March 31, 2019 | 1.4 | rring Tax Benefits ¦ - ¦ (0.39) ¦ - ¦ (0.43) ⏎ Adjusted EPS ¦ $0.73 ¦ $0.70 ¦ 4% ¦ $1.57 ¦ $[[1.40]] ¦ 12% ⏎ March 29, 2020 ⏎ Current Portion of Long-term Debt ¦ $1 |  |
| 10.15 | `0.67` | GAAP_BASIC | current_quarter | Q2 fiscal 2020 | 0.67 | 397 ¦ $55,911 ¦ $83,707 ¦ $97,907 ⏎ Earnings per share attributable to Tetra Tech: ⏎ Basic ¦ $[[0.67]] ¦ $1.01 ¦ $1.53 ¦ $1.77 ⏎ Diluted ¦ $0.66 ¦ $1.00 ¦ $1.51 ¦ $ |  |
| 10.16 | `1.01` | GAAP_BASIC | prior_year_quarter | Q2 fiscal 2019 | 1.01 | 5,911 ¦ $83,707 ¦ $97,907 ⏎ Earnings per share attributable to Tetra Tech: ⏎ Basic ¦ $0.67 ¦ $[[1.01]] ¦ $1.53 ¦ $1.77 ⏎ Diluted ¦ $0.66 ¦ $1.00 ¦ $1.51 ¦ $1.74 ⏎ Wei |  |
| 10.17 | `1.53` | GAAP_BASIC | current_ytd | six months ended March 29, 2020 | 1.53 | $83,707 ¦ $97,907 ⏎ Earnings per share attributable to Tetra Tech: ⏎ Basic ¦ $0.67 ¦ $1.01 ¦ $[[1.53]] ¦ $1.77 ⏎ Diluted ¦ $0.66 ¦ $1.00 ¦ $1.51 ¦ $1.74 ⏎ Weighted-av |  |
| 10.18 | `1.77` | GAAP_BASIC | prior_ytd | six months ended March 31, 2019 | 1.77 | ¦ $97,907 ⏎ Earnings per share attributable to Tetra Tech: ⏎ Basic ¦ $0.67 ¦ $1.01 ¦ $1.53 ¦ $[[1.77]] ⏎ Diluted ¦ $0.66 ¦ $1.00 ¦ $1.51 ¦ $1.74 ⏎ Weighted-average co |  |
| 10.19 | `0.66` | GAAP_DILUTED | current_quarter | Q2 fiscal 2020 | 0.66 | gs per share attributable to Tetra Tech: ⏎ Basic ¦ $0.67 ¦ $1.01 ¦ $1.53 ¦ $1.77 ⏎ Diluted ¦ $[[0.66]] ¦ $1.00 ¦ $1.51 ¦ $1.74 ⏎ Weighted-average common shares outs |  |
| 10.20 | `1.00` | GAAP_DILUTED | prior_year_quarter | Q2 fiscal 2019 | 1.0 | hare attributable to Tetra Tech: ⏎ Basic ¦ $0.67 ¦ $1.01 ¦ $1.53 ¦ $1.77 ⏎ Diluted ¦ $0.66 ¦ $[[1.00]] ¦ $1.51 ¦ $1.74 ⏎ Weighted-average common shares outstanding: |  |
| 10.21 | `1.51` | GAAP_DILUTED | current_ytd | six months ended March 29, 2020 | 1.51 | ributable to Tetra Tech: ⏎ Basic ¦ $0.67 ¦ $1.01 ¦ $1.53 ¦ $1.77 ⏎ Diluted ¦ $0.66 ¦ $1.00 ¦ $[[1.51]] ¦ $1.74 ⏎ Weighted-average common shares outstanding: ⏎ Basic ¦ |  |
| 10.22 | `1.74` | GAAP_DILUTED | prior_ytd | six months ended March 31, 2019 | 1.74 | e to Tetra Tech: ⏎ Basic ¦ $0.67 ¦ $1.01 ¦ $1.53 ¦ $1.77 ⏎ Diluted ¦ $0.66 ¦ $1.00 ¦ $1.51 ¦ $[[1.74]] ⏎ Weighted-average common shares outstanding: ⏎ Basic ¦ 54,699  |  |

**Missed mentions** (add `ADD:` lines below):


## 11. HomeTrust Bancshares, Inc.  (0001538263-20-000014)

Anchor (10-Q): **0.07** (us-gaap:EarningsPerShareDiluted) | Model primary: **0.07** | mentions: 14 | Reason in batch: random sample (unflagged)

| ID | Span | Type | Period kind | Period | Value | Context (span in [[ ]]) | Verdict |
|---|---|---|---|---|---|---|---|
| 11.1 | `0.07` | GAAP_DILUTED | current_quarter | Q3 fiscal 2020 (quarter ended March 31, 2020) | 0.07 | come was $1.2 million, compared to $3.3 million; ⏎ •diluted earnings per share ("EPS") was $[[0.07]], compared to $0.18; ⏎ •return on assets ("ROA") was 0.14%, co |  |
| 11.2 | `0.18` | GAAP_DILUTED | prior_year_quarter | Q3 fiscal 2019 (quarter ended March 31, 2019) | 0.18 | on, compared to $3.3 million; ⏎ •diluted earnings per share ("EPS") was $0.07, compared to $[[0.18]]; ⏎ •return on assets ("ROA") was 0.14%, compared to 0.39%; ⏎ •r |  |
| 11.3 | `1.08` | GAAP_DILUTED | current_ytd | nine months ended March 31, 2020 | 1.08 | in the previous year: ⏎ •net income was $19.2 million, compared to $19.1 million; ⏎ •EPS was $[[1.08]], compared to $1.02; ⏎ •ROA was 0.72%, compared to 0.76%; ⏎ •ROE |  |
| 11.4 | `1.02` | GAAP_DILUTED | prior_ytd | nine months ended March 31, 2019 | 1.02 | r: ⏎ •net income was $19.2 million, compared to $19.1 million; ⏎ •EPS was $1.08, compared to $[[1.02]]; ⏎ •ROA was 0.72%, compared to 0.76%; ⏎ •ROE was 6.19%, compare |  |
| 11.5 | `0.07` | GAAP_BASIC | current_quarter | three months ended March 31, 2020 | 0.07 | 31, ¦ March 31, ⏎ 2020 ¦ 2019 ¦ 2019 ¦ 2020 ¦ 2019 ⏎ Net income per common share:(1) ⏎ Basic ¦ $[[0.07]] ¦ $0.54 ¦ $0.19 ¦ $1.12 ¦ $1.07 ⏎ Diluted ¦ $0.07 ¦ $0.52 ¦ $ |  |
| 11.6 | `0.54` | GAAP_BASIC | prior_quarter | three months ended December 31, 2019 | 0.54 | rch 31, ⏎ 2020 ¦ 2019 ¦ 2019 ¦ 2020 ¦ 2019 ⏎ Net income per common share:(1) ⏎ Basic ¦ $0.07 ¦ $[[0.54]] ¦ $0.19 ¦ $1.12 ¦ $1.07 ⏎ Diluted ¦ $0.07 ¦ $0.52 ¦ $0.18 ¦ $ |  |
| 11.7 | `0.19` | GAAP_BASIC | prior_year_quarter | three months ended March 31, 2019 | 0.19 | 2020 ¦ 2019 ¦ 2019 ¦ 2020 ¦ 2019 ⏎ Net income per common share:(1) ⏎ Basic ¦ $0.07 ¦ $0.54 ¦ $[[0.19]] ¦ $1.12 ¦ $1.07 ⏎ Diluted ¦ $0.07 ¦ $0.52 ¦ $0.18 ¦ $1.08 ¦ $ |  |
| 11.8 | `1.12` | GAAP_BASIC | current_ytd | nine months ended March 31, 2020 | 1.12 | 019 ¦ 2019 ¦ 2020 ¦ 2019 ⏎ Net income per common share:(1) ⏎ Basic ¦ $0.07 ¦ $0.54 ¦ $0.19 ¦ $[[1.12]] ¦ $1.07 ⏎ Diluted ¦ $0.07 ¦ $0.52 ¦ $0.18 ¦ $1.08 ¦ $1.02 ⏎ Ave |  |
| 11.9 | `1.07` | GAAP_BASIC | prior_ytd | nine months ended March 31, 2019 | 1.07 | 19 ¦ 2020 ¦ 2019 ⏎ Net income per common share:(1) ⏎ Basic ¦ $0.07 ¦ $0.54 ¦ $0.19 ¦ $1.12 ¦ $[[1.07]] ⏎ Diluted ¦ $0.07 ¦ $0.52 ¦ $0.18 ¦ $1.08 ¦ $1.02 ⏎ Average sha |  |
| 11.10 | `0.07` | GAAP_DILUTED | current_quarter | three months ended March 31, 2020 | 0.07 |  ⏎ Net income per common share:(1) ⏎ Basic ¦ $0.07 ¦ $0.54 ¦ $0.19 ¦ $1.12 ¦ $1.07 ⏎ Diluted ¦ $[[0.07]] ¦ $0.52 ¦ $0.18 ¦ $1.08 ¦ $1.02 ⏎ Average shares outstanding: |  |
| 11.11 | `0.52` | GAAP_DILUTED | prior_quarter | three months ended December 31, 2019 | 0.52 | ome per common share:(1) ⏎ Basic ¦ $0.07 ¦ $0.54 ¦ $0.19 ¦ $1.12 ¦ $1.07 ⏎ Diluted ¦ $0.07 ¦ $[[0.52]] ¦ $0.18 ¦ $1.08 ¦ $1.02 ⏎ Average shares outstanding: ⏎ Basic ¦ |  |
| 11.12 | `0.18` | GAAP_DILUTED | prior_year_quarter | three months ended March 31, 2019 | 0.18 | common share:(1) ⏎ Basic ¦ $0.07 ¦ $0.54 ¦ $0.19 ¦ $1.12 ¦ $1.07 ⏎ Diluted ¦ $0.07 ¦ $0.52 ¦ $[[0.18]] ¦ $1.08 ¦ $1.02 ⏎ Average shares outstanding: ⏎ Basic ¦ 16,688, |  |
| 11.13 | `1.08` | GAAP_DILUTED | current_ytd | nine months ended March 31, 2020 | 1.08 | hare:(1) ⏎ Basic ¦ $0.07 ¦ $0.54 ¦ $0.19 ¦ $1.12 ¦ $1.07 ⏎ Diluted ¦ $0.07 ¦ $0.52 ¦ $0.18 ¦ $[[1.08]] ¦ $1.02 ⏎ Average shares outstanding: ⏎ Basic ¦ 16,688,646 ¦ 16 |  |
| 11.14 | `1.02` | GAAP_DILUTED | prior_ytd | nine months ended March 31, 2019 | 1.02 |  ⏎ Basic ¦ $0.07 ¦ $0.54 ¦ $0.19 ¦ $1.12 ¦ $1.07 ⏎ Diluted ¦ $0.07 ¦ $0.52 ¦ $0.18 ¦ $1.08 ¦ $[[1.02]] ⏎ Average shares outstanding: ⏎ Basic ¦ 16,688,646 ¦ 16,906,457 |  |

**Missed mentions** (add `ADD:` lines below):


## 12. SAIA INC  (0001564590-20-019431)

Anchor (10-Q): **1.06** (us-gaap:EarningsPerShareDiluted) | Model primary: **1.06** | mentions: 6 | Reason in batch: random sample (unflagged)

| ID | Span | Type | Period kind | Period | Value | Context (span in [[ ]]) | Verdict |
|---|---|---|---|---|---|---|---|
| 12.1 | `1.06` | GAAP_DILUTED | current_quarter | Q1 2020 | 1.06 | ted first quarter 2020 financial results. Diluted earnings per share in the quarter were $[[1.06]] compared to $0.85 in the first quarter of 2019. ⏎ Highlights  |  |
| 12.2 | `0.85` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | 0.85 | 2020 financial results. Diluted earnings per share in the quarter were $1.06 compared to $[[0.85]] in the first quarter of 2019. ⏎ Highlights from the first qua |  |
| 12.3 | `1.08` | GAAP_BASIC | current_quarter | Q1 2020 | 1.08 | Average common shares outstanding - diluted ¦ 26,492 ¦ 26,322 ⏎ Basic earnings per share ¦ $[[1.08]] ¦ $0.86 ⏎ Diluted earnings per share ¦ $1.06 ¦ $0.85 ⏎ Saia, In |  |
| 12.4 | `0.86` | GAAP_BASIC | prior_year_quarter | Q1 2019 | 0.86 | common shares outstanding - diluted ¦ 26,492 ¦ 26,322 ⏎ Basic earnings per share ¦ $1.08 ¦ $[[0.86]] ⏎ Diluted earnings per share ¦ $1.06 ¦ $0.85 ⏎ Saia, Inc. and S |  |
| 12.5 | `1.06` | GAAP_DILUTED | current_quarter | Q1 2020 | 1.06 |  ¦ 26,492 ¦ 26,322 ⏎ Basic earnings per share ¦ $1.08 ¦ $0.86 ⏎ Diluted earnings per share ¦ $[[1.06]] ¦ $0.85 ⏎ Saia, Inc. and Subsidiaries ⏎ Condensed Consolidated  |  |
| 12.6 | `0.85` | GAAP_DILUTED | prior_year_quarter | Q1 2019 | 0.85 | 2 ¦ 26,322 ⏎ Basic earnings per share ¦ $1.08 ¦ $0.86 ⏎ Diluted earnings per share ¦ $1.06 ¦ $[[0.85]] ⏎ Saia, Inc. and Subsidiaries ⏎ Condensed Consolidated Statemen |  |

**Missed mentions** (add `ADD:` lines below):


## 13. FAIR ISAAC CORP  (0001564590-20-019755)

Anchor (10-Q): **1.94** (us-gaap:EarningsPerShareDiluted) | Model primary: **1.94** | mentions: 21 | Reason in batch: random sample (unflagged)

| ID | Span | Type | Period kind | Period | Value | Context (span in [[ ]]) | Verdict |
|---|---|---|---|---|---|---|---|
| 13.1 | `1.94` | GAAP_DILUTED | current_quarter | Q2 fiscal 2020 | 1.94 |  by reference in this Item 2.02. ⏎  ⏎ [EXHIBIT 99.1] ⏎ Exhibit 99.1 ⏎ FICO Announces Earnings of $[[1.94]] per Share for ⏎ Second Quarter Fiscal 2020 ⏎ Revenue of $308 mi |  |
| 13.2 | `1.94` | GAAP_DILUTED | current_quarter | Q2 fiscal 2020 | 1.94 | nd Quarter Fiscal 2020 GAAP Results ⏎ Net income for the quarter totaled $58.3 million, or $[[1.94]] per share, versus $33.4 million, or $1.10 per share, in the |  |
| 13.3 | `1.10` | GAAP_DILUTED | prior_year_quarter | Q2 fiscal 2019 | 1.1 | come for the quarter totaled $58.3 million, or $1.94 per share, versus $33.4 million, or $[[1.10]] per share, in the prior year period. ⏎ Net cash provided by o |  |
| 13.4 | `2.14` | NON_GAAP | current_quarter | Q2 fiscal 2020 | 2.14 |  million versus $47.3 million in the prior year period. Non-GAAP EPS for the quarter was $[[2.14]] versus $1.56 in the prior year period. Free cash flow for t |  |
| 13.5 | `1.56` | NON_GAAP | prior_year_quarter | Q2 fiscal 2019 | 1.56 | us $47.3 million in the prior year period. Non-GAAP EPS for the quarter was $2.14 versus $[[1.56]] in the prior year period. Free cash flow for the quarter wa |  |
| 13.6 | `2.00` | GAAP_BASIC | current_quarter | Q2 fiscal 2020 | 2.0 | 742 ⏎ Net income ¦ $ 58,288 ¦ $ 33,381 ¦ $ 113,209 ¦ $ 73,388 ⏎ Basic earnings per share: ¦ $ [[2.00]] ¦ $ 1.15 ¦ $ 3.89 ¦ $ 2.53 ⏎ Diluted earnings per share: ¦ $  |  |
| 13.7 | `1.15` | GAAP_BASIC | prior_year_quarter | Q2 fiscal 2019 | 1.15 | ncome ¦ $ 58,288 ¦ $ 33,381 ¦ $ 113,209 ¦ $ 73,388 ⏎ Basic earnings per share: ¦ $ 2.00 ¦ $ [[1.15]] ¦ $ 3.89 ¦ $ 2.53 ⏎ Diluted earnings per share: ¦ $ 1.94 ¦ $  |  |
| 13.8 | `3.89` | GAAP_BASIC | current_ytd | six months ended March 31, 2020 | 3.89 |  58,288 ¦ $ 33,381 ¦ $ 113,209 ¦ $ 73,388 ⏎ Basic earnings per share: ¦ $ 2.00 ¦ $ 1.15 ¦ $ [[3.89]] ¦ $ 2.53 ⏎ Diluted earnings per share: ¦ $ 1.94 ¦ $ 1.10 ¦ $  |  |
| 13.9 | `2.53` | GAAP_BASIC | prior_ytd | six months ended March 31, 2019 | 2.53 |  $ 33,381 ¦ $ 113,209 ¦ $ 73,388 ⏎ Basic earnings per share: ¦ $ 2.00 ¦ $ 1.15 ¦ $ 3.89 ¦ $ [[2.53]] ⏎ Diluted earnings per share: ¦ $ 1.94 ¦ $ 1.10 ¦ $ 3.76 ¦ $  |  |
| 13.10 | `1.94` | GAAP_DILUTED | current_quarter | Q2 fiscal 2020 | 1.94 | c earnings per share: ¦ $ 2.00 ¦ $ 1.15 ¦ $ 3.89 ¦ $ 2.53 ⏎ Diluted earnings per share: ¦ $ [[1.94]] ¦ $ 1.10 ¦ $ 3.76 ¦ $ 2.42 ⏎ Shares used in computing earning |  |
| 13.11 | `1.10` | GAAP_DILUTED | prior_year_quarter | Q2 fiscal 2019 | 1.1 | s per share: ¦ $ 2.00 ¦ $ 1.15 ¦ $ 3.89 ¦ $ 2.53 ⏎ Diluted earnings per share: ¦ $ 1.94 ¦ $ [[1.10]] ¦ $ 3.76 ¦ $ 2.42 ⏎ Shares used in computing earnings per sha |  |
| 13.12 | `3.76` | GAAP_DILUTED | current_ytd | six months ended March 31, 2020 | 3.76 | re: ¦ $ 2.00 ¦ $ 1.15 ¦ $ 3.89 ¦ $ 2.53 ⏎ Diluted earnings per share: ¦ $ 1.94 ¦ $ 1.10 ¦ $ [[3.76]] ¦ $ 2.42 ⏎ Shares used in computing earnings per share: ⏎ Basic |  |
| 13.13 | `2.42` | GAAP_DILUTED | prior_ytd | six months ended March 31, 2019 | 2.42 | .00 ¦ $ 1.15 ¦ $ 3.89 ¦ $ 2.53 ⏎ Diluted earnings per share: ¦ $ 1.94 ¦ $ 1.10 ¦ $ 3.76 ¦ $ [[2.42]] ⏎ Shares used in computing earnings per share: ⏎ Basic ¦ 29,194 |  |
| 13.14 | `1.94` | GAAP_DILUTED | current_quarter | Q2 fiscal 2020 | 1.94 | t income ¦ $ 64,308 ¦ $ 47,271 ¦ $ 118,494 ¦ $ 91,182 ⏎ GAAP diluted earnings per share ¦ $ [[1.94]] ¦ $ 1.10 ¦ $ 3.76 ¦ $ 2.42 ⏎ Amortization of intangible asset |  |
| 13.15 | `1.10` | GAAP_DILUTED | prior_year_quarter | Q2 fiscal 2019 | 1.1 | ¦ $ 64,308 ¦ $ 47,271 ¦ $ 118,494 ¦ $ 91,182 ⏎ GAAP diluted earnings per share ¦ $ 1.94 ¦ $ [[1.10]] ¦ $ 3.76 ¦ $ 2.42 ⏎ Amortization of intangible assets ¦ 0.04  |  |
| 13.16 | `3.76` | GAAP_DILUTED | current_ytd | six months ended March 31, 2020 | 3.76 | 8 ¦ $ 47,271 ¦ $ 118,494 ¦ $ 91,182 ⏎ GAAP diluted earnings per share ¦ $ 1.94 ¦ $ 1.10 ¦ $ [[3.76]] ¦ $ 2.42 ⏎ Amortization of intangible assets ¦ 0.04 ¦ 0.05 ¦  |  |
| 13.17 | `2.42` | GAAP_DILUTED | prior_ytd | six months ended March 31, 2019 | 2.42 | 271 ¦ $ 118,494 ¦ $ 91,182 ⏎ GAAP diluted earnings per share ¦ $ 1.94 ¦ $ 1.10 ¦ $ 3.76 ¦ $ [[2.42]] ⏎ Amortization of intangible assets ¦ 0.04 ¦ 0.05 ¦ 0.10 ¦ 0. |  |
| 13.18 | `2.14` | NON_GAAP | current_quarter | Q2 fiscal 2020 | 2.14 | s tax benefit ¦ (0.40) ¦ (0.08) ¦ (1.13) ¦ (0.52) ⏎ Non-GAAP diluted earnings per share ¦ $ [[2.14]] ¦ $ 1.56 ¦ $ 3.94 ¦ $ 3.01 ⏎ Free cash flow ⏎ Net cash provided |  |
| 13.19 | `1.56` | NON_GAAP | prior_year_quarter | Q2 fiscal 2019 | 1.56 | efit ¦ (0.40) ¦ (0.08) ¦ (1.13) ¦ (0.52) ⏎ Non-GAAP diluted earnings per share ¦ $ 2.14 ¦ $ [[1.56]] ¦ $ 3.94 ¦ $ 3.01 ⏎ Free cash flow ⏎ Net cash provided by opera |  |
| 13.20 | `3.94` | NON_GAAP | current_ytd | six months ended March 31, 2020 | 3.94 | .40) ¦ (0.08) ¦ (1.13) ¦ (0.52) ⏎ Non-GAAP diluted earnings per share ¦ $ 2.14 ¦ $ 1.56 ¦ $ [[3.94]] ¦ $ 3.01 ⏎ Free cash flow ⏎ Net cash provided by operating acti |  |
| 13.21 | `3.01` | NON_GAAP | prior_ytd | six months ended March 31, 2019 | 3.01 | .08) ¦ (1.13) ¦ (0.52) ⏎ Non-GAAP diluted earnings per share ¦ $ 2.14 ¦ $ 1.56 ¦ $ 3.94 ¦ $ [[3.01]] ⏎ Free cash flow ⏎ Net cash provided by operating activities ¦  |  |

**Missed mentions** (add `ADD:` lines below):
