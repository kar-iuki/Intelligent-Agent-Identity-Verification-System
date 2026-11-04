# Recorded KYC experiment results

Model **3.1.0**, trained 2026-11-04T18:44:02+00:00; seed 42.
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
| Full SVM | 0.767333 | 0.679446 | 0.749505 | 22 | 169 |
| Identity-only SVM | 0.770667 | 0.678461 | 0.750589 | 22 | 173 |
| Decision Tree | 0.741333 | 0.682694 | 0.743059 | 16 | 153 |

### Full SVM

Selected parameters: `{'C': 10, 'gamma': 1}`. Training CV macro F1: **0.710958**.

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Verified | 0.809950 | 0.904444 | 0.854593 | 900 |
| Manual Review | 0.491979 | 0.306667 | 0.377823 | 300 |
| Rejected | 0.795455 | 0.816667 | 0.805921 | 300 |

Confusion matrix: actual rows / predicted columns; order Verified, Manual Review, Rejected.

```text
[814, 62, 24]
[169, 92, 39]
[22, 33, 245]
```

All off-diagonal errors:
- Verified -> Manual Review: 62
- Verified -> Rejected: 24
- Manual Review -> Verified: 169
- Manual Review -> Rejected: 39
- Rejected -> Verified: 22
- Rejected -> Manual Review: 33

### Identity-only SVM

Selected parameters: `{'C': 100, 'gamma': 1}`. Training CV macro F1: **0.706363**.

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Verified | 0.808636 | 0.915556 | 0.858781 | 900 |
| Manual Review | 0.520231 | 0.300000 | 0.380550 | 300 |
| Rejected | 0.785714 | 0.806667 | 0.796053 | 300 |

Confusion matrix: actual rows / predicted columns; order Verified, Manual Review, Rejected.

```text
[824, 47, 29]
[173, 90, 37]
[22, 36, 242]
```

All off-diagonal errors:
- Verified -> Manual Review: 47
- Verified -> Rejected: 29
- Manual Review -> Verified: 173
- Manual Review -> Rejected: 37
- Rejected -> Verified: 22
- Rejected -> Manual Review: 36

### Decision Tree

Selected parameters: `{'max_depth': 5, 'min_samples_leaf': 20}`. Training CV macro F1: **0.699150**.

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Verified | 0.818864 | 0.848889 | 0.833606 | 900 |
| Manual Review | 0.396825 | 0.416667 | 0.406504 | 300 |
| Rejected | 0.884921 | 0.743333 | 0.807971 | 300 |

Confusion matrix: actual rows / predicted columns; order Verified, Manual Review, Rejected.

```text
[764, 129, 7]
[153, 125, 22]
[16, 61, 223]
```

All off-diagonal errors:
- Verified -> Manual Review: 129
- Verified -> Rejected: 7
- Manual Review -> Verified: 153
- Manual Review -> Rejected: 22
- Rejected -> Verified: 16
- Rejected -> Manual Review: 61

## Probability quality

| Model | Log loss | Multiclass Brier (sum) |
|---|---:|---:|
| Full SVM | 0.615813 | 0.350726 |
| Identity-only SVM | 0.624319 | 0.353755 |
| Decision Tree | 0.693903 | 0.386282 |
| Decision Tree, sigmoid | 0.593573 | 0.334291 |

Lower is better. Brier is mean sum of three squared probability errors, range 0–2. SVM calibration uses validation only. Reliability diagrams and per-class ten-bin ECE are saved; synthetic calibration does not imply real certainty.

## Importance

| SVM feature | Mean macro F1 drop | Repeat SD |
|---|---:|---:|
| liveness_score | 0.179344 | 0.007381 |
| ocr_confidence_score | 0.134949 | 0.007287 |
| face_match_score | 0.049646 | 0.004907 |
| blur_score | 0.002585 | 0.003141 |
| brightness_score | 0.002089 | 0.004200 |
| contrast_score | 0.000929 | 0.003377 |

20 permutations; seed 42. SD is across repeats, not a population confidence interval.

| Decision Tree feature | Impurity importance |
|---|---:|
| liveness_score | 0.499406 |
| ocr_confidence_score | 0.306559 |
| face_match_score | 0.175841 |
| blur_score | 0.015528 |
| contrast_score | 0.002665 |
| brightness_score | 0.000000 |

Tree impurity importance and SVM permutation drops are different quantities; correlated predictors can change both rankings.

## Ablation

Full-minus-identity macro F1: **0.000985**.
Paired bootstrap 95% interval: [-0.014476344247495498, 0.016385613319433848] (1,000 replicates).
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
    "min": 14.111516158481663,
    "p01": 26.388015471157452,
    "p50": 64.35066865877764
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
    "face_match_score": 0.3776807707392223,
    "liveness_score": 0.5736846226423242,
    "ocr_confidence_score": 0.4816119250822462,
    "blur_score": 0.2267550693631019,
    "brightness_score": 0.3232091558292084,
    "contrast_score": 0.29284742768936034
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

Quality features improved observed macro F1 in this run.
Classification metrics, security errors and probability quality must be considered separately.
The full model incorrectly verified 22 of 300 Rejected cases and 169 of 300 Manual Review cases. These errors do not justify automatic operational approval. No test-guided retuning was performed.

