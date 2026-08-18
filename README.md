# NSW LGA Income Analysis

Predicting median weekly household income across NSW Local Government Areas
using demographic composition from the 2021 ABS Census.

## Question

Can the demographic composition of an area predict its median household income?

The aim was to test whether characteristics like age structure, educational
attainment, birthplace and language predict income at the area level, using
only variables that describe *who lives there* rather than what they earn.

## Data

2021 ABS Census, NSW Local Government Areas (n = 129).

- **G02** (medians and averages) — target variable
- **G01** (selected person characteristics) — feature source
- **2021 ASGS Non-ABS Structures** — LGA code to name mapping

### Excluded variables

`Median_tot_prsnl_inc_weekly` and `Median_tot_fam_inc_weekly` were dropped.
Household income is broadly personal income aggregated across a household,
so including either would leak the target: the model would score highly while
answering a trivial question rather than the demographic one.

`Median_rent_weekly`, `Median_mortgage_repay_monthly`,
`Average_num_psns_per_bedroom` and `Average_household_size` were dropped on
similar grounds — housing costs are largely determined by income, and household
size is a direct component of household income.

`Median_age_persons` was dropped as redundant rather than leaky, since age
structure is captured by the two age proportion features.

### Features

Seven proportions engineered from raw G01 counts, each divided by total
population: share aged 15–24, share aged 65+, share born in Australia, share
speaking only English at home, share who completed Year 12, share with Year 8
or below, and share identifying as Indigenous.

## Method

Evaluated with 5-fold cross-validation rather than a single train/test split.
With 129 rows an 80/20 split leaves only ~26 LGAs in test, making the score
highly dependent on the random draw.

Scaling is done inside a `Pipeline` so the scaler is refit within each fold,
preventing validation-fold statistics from leaking into training.

### Fold shuffling

The initial run used unshuffled folds and produced R² = 0.695 (sd 0.170), with
one fold as low as 0.377. The dataframe is indexed by ABS LGA code, which is
assigned systematically rather than randomly, so contiguous folds grouped
structurally similar councils. Shuffling raised the mean to 0.782 and nearly
halved the spread.

The shuffled result is the better estimate of performance on a randomly chosen
LGA. The unshuffled result is still informative: it suggests the model performs
worse on certain structural groups of councils, which shuffling averages away.

## Results

| Model | R² (mean) | sd |
|---|---|---|
| OLS | 0.775 | 0.103 |
| Ridge (α=0.01) | 0.775 | 0.102 |
| Ridge (α=0.1) | 0.776 | 0.101 |
| Ridge (α=1) | 0.782 | 0.090 |
| Ridge (α=10) | 0.787 | 0.068 |
| Ridge (α=100) | 0.713 | 0.052 |
| Random Forest | 0.835 | 0.091 |

Random Forest MAE: **$138/week**, against a target ranging $885–$3192
(mean $1602, sd $506).

### Regularisation

Ridge peaks at α=10 (0.787) but only improves on OLS by 0.012, well inside the
fold-to-fold spread. The α sweep shows the bias–variance trade-off clearly:
standard deviation falls monotonically (0.102 → 0.052) as α increases, while
the mean rises slightly then collapses at α=100. Regularisation stabilises the
estimate here but doesn't meaningfully improve it.

### Random Forest vs linear models

Random Forest outperforms every linear configuration by roughly 0.05,
suggesting non-linear structure or feature interactions that a linear model
can't represent.

## Findings

**Education dominates.** The two education features account for 76% of Random
Forest importance (`pct_low_education` 0.542, `pct_completed_yr12` 0.214) and
carry the largest Ridge coefficients (+227 and −143 per standard deviation).

**The two models disagree on which education feature matters most.** Ridge
ranks Year 12 completion highest; the forest ranks low education highest by a
wide margin. `pct_low_education` is tightly clustered (0.006–0.081) with a long
tail, a shape where threshold splits isolate distinctive groups more
effectively than a linear coefficient can. This is a plausible source of the
forest's advantage, though not tested directly.

**Age effects run in expected directions, with one exception.**
`pct_aged_65_plus` has the second-largest negative coefficient (−143),
consistent with fewer earners per household. `pct_aged_15_24` is weakly
*positive* (+21). This is an ecological relationship rather than an individual
one — LGAs with high youth shares tend to be inner-city and university areas
that are higher-income for other reasons.

**Birthplace and language are highly collinear (r = 0.94)** and both receive
low forest importance (0.016, 0.014). Correlated features split importance
between themselves, so this understates their joint contribution. Both were
retained: they measure conceptually distinct things, since migrants from
English-speaking countries score low on nativity and high on language.

## Limitations

- n = 129 is small. Fold-to-fold R² varies by roughly ±0.09, so differences
  under that threshold shouldn't be treated as meaningful.
- Feature importances and coefficients are fitted on all 129 rows and are
  descriptive, not out-of-sample.
- Cross-sectional single-year data; no causal claims.

## Files

- `Data.ipynb` — data preparation, feature engineering, modelling
- `helpers.py` — `find_max_feature()` utility
- `findmaxfeatureinput.py` — interactive script for querying column extremes
- `NSW-LGA/` — raw ABS Census CSVs (G01, G02)
- `2021Census_geog_desc_1st_2nd_3rd_release.xlsx` — LGA code to name mapping
- `bigger_df_clean.csv` — cleaned, joined dataset