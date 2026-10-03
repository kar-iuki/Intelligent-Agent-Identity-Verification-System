# Recorded KYC experiment results

Model **2.0.0**, trained 2026-10-02T19:14:14+00:00; seed 42.
All results below are from synthetic held-out data. No requested target accuracy was used.

## Dataset and split

| Partition | Verified | Manual Review | Rejected | Total |
|---|---:|---:|---:|---:|
| All | 6000 | 2000 | 2000 | 10000 |
| train | 4200 | 1400 | 1400 | 7000 |
| validation | 900 | 300 | 300 | 1500 |
| test | 900 | 300 | 300 | 1500 |

## Model comparison

| Model | Accuracy | Macro F1 | Weighted F1 | Rejected → Verified | Review → Verified |
|---|---:|---:|---:|---:|---:|
| Full SVM | 0.743333 | 0.621383 | 0.705566 | 57 | 217 |
| Identity-only SVM | 0.736000 | 0.639735 | 0.714382 | 53 | 196 |
| Decision Tree | 0.742000 | 0.618165 | 0.704358 | 107 | 227 |

### Full SVM

Selected parameters: `{'C': 10, 'gamma': 'scale'}`. Training CV macro F1: **0.672766**.

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Verified | 0.753153 | 0.928889 | 0.831841 | 900 |
| Manual Review | 0.633333 | 0.190000 | 0.292308 | 300 |
| Rejected | 0.740000 | 0.740000 | 0.740000 | 300 |

Confusion matrix: actual rows / predicted columns; order Verified, Manual Review, Rejected.

```text
[836, 12, 52]
[217, 57, 26]
[57, 21, 222]
```

All off-diagonal errors:
- Verified -> Manual Review: 12
- Verified -> Rejected: 52
- Manual Review -> Verified: 217
- Manual Review -> Rejected: 26
- Rejected -> Verified: 57
- Rejected -> Manual Review: 21

### Identity-only SVM

Selected parameters: `{'C': 100, 'gamma': 'auto'}`. Training CV macro F1: **0.675051**.

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Verified | 0.764650 | 0.898889 | 0.826353 | 900 |
| Manual Review | 0.497006 | 0.276667 | 0.355460 | 300 |
| Rejected | 0.770909 | 0.706667 | 0.737391 | 300 |

Confusion matrix: actual rows / predicted columns; order Verified, Manual Review, Rejected.

```text
[809, 49, 42]
[196, 83, 21]
[53, 35, 212]
```

All off-diagonal errors:
- Verified -> Manual Review: 49
- Verified -> Rejected: 42
- Manual Review -> Verified: 196
- Manual Review -> Rejected: 21
- Rejected -> Verified: 53
- Rejected -> Manual Review: 35

### Decision Tree

Selected parameters: `{'max_depth': 3, 'min_samples_leaf': 5}`. Training CV macro F1: **0.654701**.

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Verified | 0.725329 | 0.980000 | 0.833648 | 900 |
| Manual Review | 0.592920 | 0.223333 | 0.324455 | 300 |
| Rejected | 0.959064 | 0.546667 | 0.696391 | 300 |

Confusion matrix: actual rows / predicted columns; order Verified, Manual Review, Rejected.

```text
[882, 17, 1]
[227, 67, 6]
[107, 29, 164]
```

All off-diagonal errors:
- Verified -> Manual Review: 17
- Verified -> Rejected: 1
- Manual Review -> Verified: 227
- Manual Review -> Rejected: 6
- Rejected -> Verified: 107
- Rejected -> Manual Review: 29

## Probability quality

| Model | Log loss | Multiclass Brier (sum) |
|---|---:|---:|
| Full SVM | 0.692656 | 0.391520 |
| Identity-only SVM | 0.704705 | 0.398989 |
| Decision Tree | 0.805264 | 0.470119 |
| Decision Tree, sigmoid | 0.716709 | 0.403878 |

Lower is better. Brier is mean sum of three squared probability errors, range 0–2. SVM calibration uses validation only. Reliability diagrams and per-class ten-bin ECE are saved; synthetic calibration does not imply real certainty.

## Importance

| SVM feature | Mean macro F1 drop | Repeat SD |
|---|---:|---:|
| liveness_score | 0.180015 | 0.010316 |
| face_match_score | 0.107227 | 0.008112 |
| ocr_confidence_score | 0.047299 | 0.006824 |
| blur_score | 0.001410 | 0.002998 |
| brightness_score | -0.000072 | 0.003925 |
| contrast_score | -0.004103 | 0.005582 |

20 permutations; seed 42. SD is across repeats, not a population confidence interval.

| Decision Tree feature | Impurity importance |
|---|---:|
| liveness_score | 0.588825 |
| face_match_score | 0.411004 |
| brightness_score | 0.000171 |
| ocr_confidence_score | 0.000000 |
| blur_score | 0.000000 |
| contrast_score | 0.000000 |

Tree impurity importance and SVM permutation drops are different quantities; correlated predictors can change both rankings.

## Ablation

Full-minus-identity macro F1: **-0.018352**.
Paired bootstrap 95% interval: [-0.03600691591113115, -0.000685255611252689] (1,000 replicates).
Interpret this as evidence conditional on the simulator and these fitted models. It is not proof of production benefit. Both models were tuned independently using comparable training CV; six production features remain.

## Duplicate and leakage diagnostics

```json
{
  "exact_duplicate_feature_vectors": 0,
  "conflicting_label_vectors": 0,
  "cross_split_duplicates": {
    "train_test": 0,
    "train_validation": 0,
    "validation_test": 0
  },
  "near_duplicate_pairs": 0,
  "near_duplicate_definition": "All differences <= face .1, live .001, OCR .001, log1p(blur) .01, brightness .1, contrast .1",
  "nearest_neighbor_tolerance_distance_percentiles": {
    "min": 14.391706328282226,
    "p01": 28.39143885849157,
    "p50": 64.53915163340258
  }
}
```

```json
{
  "split_rows_disjoint": true,
  "features_exclude_target_and_scenario_ids": true,
  "scaler_fit": "Each CV training fold; final scaler on 7000 training rows only.",
  "tuning": "5-fold stratified training CV only, both SVMs and tree.",
  "calibration": "Frozen estimators fitted on train; sigmoid calibrators fitted on 1500 validation rows only.",
  "test": "1500 rows used only for final metrics, diagnostic importance, plots and paired uncertainty, never selection.",
  "synthetic_label_limitation": "Outcomes assigned by assumed scenarios, not real adjudication. Some scenarios intentionally have identical observable distributions under different latent outcomes.",
  "single_feature_training_cv_macro_f1": {
    "face_match_score": 0.4793011614684854,
    "liveness_score": 0.5593005984693551,
    "ocr_confidence_score": 0.3801582275188119,
    "blur_score": 0.3128598072572787,
    "brightness_score": 0.29314221349682257,
    "contrast_score": 0.21943920610675693
  },
  "benchmark_limitations": "Local measurement files reused as distribution evidence, not independent real-world validation. Raw benchmark images not rerun in this experiment.",
  "near_perfect_trigger": false,
  "quality_dominates_permutation": false,
  "test_experiments_run": 1
}
```

Historical findings: see `legacy_methodology_audit.json`. Original data, scripts and model files are retained. Full methodology, API units, calibration policy and limitations are in `../README.md`.

## Defence explanation

The RBF SVM combines six upstream numerical verification signals. It does not process images. Face, liveness and OCR provide identity evidence; raw image-quality metrics provide context for unreliable captures. A training-only MinMaxScaler normalizes the scores, an RBF SVM learns nonlinear boundaries, and validation-only sigmoid calibration produces probabilities for Verified, Manual Review and Rejected. Results quantify performance under documented synthetic assumptions; independent real KYC evaluation is still required.

## Limitations

- Synthetic joint distributions and adjudication labels are assumptions.
- 60/20/20 is an experimental allocation, not prevalence.
- MIDV score is text agreement, not proof of document authenticity.
- LFW and NUAA are limited benchmarks; no demographic, modern attack or device shift validation.
- Calibration is for this synthetic population, not real-world certainty.
- Clipping outside training extrema may conceal production distribution shift.
- No online learning; explicit offline retraining needs confirmed real labels.

## Interpretation of this run

Quality features did not improve macro F1 in this run.
Classification metrics, security errors and probability quality must be considered separately.
The full model incorrectly verified 57 of 300 Rejected cases and 217 of 300 Manual Review cases. These errors do not justify automatic operational approval. No test-guided retuning was performed.

