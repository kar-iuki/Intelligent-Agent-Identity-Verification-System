# KYC v3 improvement experiment

Production promotion: **True**. Passed predeclared release gate: accuracy increased, macro F1 and both false-verification counts did not worsen.

Both rows below were evaluated on the SAME fresh 1,500 synthetic cases. The original v2 74.33% result used a different test set and must not be used as the before value here.

| Model | Accuracy | Macro F1 | Weighted F1 | Rejected → Verified | Manual Review → Verified |
|---|---:|---:|---:|---:|---:|
| Saved v2 incumbent | 75.733% | 0.651909 | 0.730391 | 44 | 186 |
| Selected v3 candidate | 75.800% | 0.654082 | 0.731979 | 43 | 184 |

Accuracy difference: **0.067 percentage points**.
Paired bootstrap 95% interval: [-0.0013333333333333333, 0.0033333333333333335] (accuracy fraction).
Macro F1 difference: 0.002173; paired interval: [-0.0010511307847866746, 0.006854749742914959].

## Selected model and policy

Candidate: **raw_native_sigmoid**.
Training-only hyperparameters: `{'C': 10, 'gamma': 'scale'}`; CV macro F1: 0.672766.
Policy: probability; review multiplier 1.0; verification threshold 0.0; verification margin 0.0.
All six input features and the generator assumptions were retained. Quality transforms, where selected, are learned inside training folds. Probabilities are unchanged by the decision policy.

| Selection metrics | Accuracy | Macro F1 | Review recall | Rejected → Verified | Review → Verified |
|---|---:|---:|---:|---:|---:|
| Comparable baseline | 0.757333 | 0.659895 | 0.300000 | 29 | 92 |
| Selected candidate | 0.757333 | 0.659895 | 0.300000 | 29 | 92 |

## Fresh per-class results

| Model | Class | Precision | Recall | F1 |
|---|---|---:|---:|---:|
| v2 | Verified | 0.783427 | 0.924444 | 0.848114 |
| v2 | Manual Review | 0.634921 | 0.266667 | 0.375587 |
| v2 | Rejected | 0.717949 | 0.746667 | 0.732026 |
| v3 | Verified | 0.785444 | 0.923333 | 0.848825 |
| v3 | Manual Review | 0.630769 | 0.273333 | 0.381395 |
| v3 | Rejected | 0.717949 | 0.746667 | 0.732026 |

## incumbent confusion matrix

Actual rows / predicted columns; order Verified, Manual Review, Rejected.

```text
[832, 14, 54]
[186, 80, 34]
[44, 32, 224]
```

## candidate confusion matrix

Actual rows / predicted columns; order Verified, Manual Review, Rejected.

```text
[831, 15, 54]
[184, 82, 34]
[43, 33, 224]
```

## Probability quality

| Model | Log loss | Multiclass Brier |
|---|---:|---:|
| incumbent | 0.660123 | 0.373659 |
| candidate | 0.659596 | 0.373110 |

## What was compared

Four SVM variants (raw/power quality × native/explicit one-vs-rest), three calibration methods (sigmoid/isotonic/temperature), and native versus validation-selected review policies. Three new 24-point five-fold searches were run; the prior raw-native CV winner was reused with provenance. All policy/calibration variants are in `validation_candidates.csv`.

## Isolation and autonomy

Original train=7,000; calibration=750; selection=750. Original test=1,500 retired. Fresh evaluation=1,500, generated only after selection freeze. Exact and near-duplicate checks cover all 11,500 rows. The test is used once for reported evaluation and a predeclared release acceptance check, not candidate tuning. Training checkpoints allow recovery from implementation errors; completed experiments are not silently rerun. No online learning exists.

## Permutation importance

| Feature | Macro F1 decrease | Repeat SD |
|---|---:|---:|
| liveness_score | 0.201380 | 0.008477 |
| face_match_score | 0.110442 | 0.005995 |
| ocr_confidence_score | 0.049802 | 0.007588 |
| blur_score | 0.003831 | 0.003357 |
| brightness_score | -0.000359 | 0.003924 |
| contrast_score | -0.003439 | 0.003605 |

## Limitations

- Fresh synthetic draw from the SAME assumptions; not independent real-world validation.
- Previously observed v2 results motivated the hypotheses; original test was retired.
- Calibration and selection are disjoint but small (750 each); searching policies can overfit selection.
- Isotonic calibration may overfit small calibration samples; temperature can preserve poor decision rankings.
- Latent review and genuine scenarios can share observed distributions; missing evidence remains irreducible.
- Decision-policy preferences do not change calibrated probability values.
- Quality transform and calibrators are static; no online learning.
- The original data contains observationally identical components with different assumed adjudication outcomes. Their minimum population error contribution is 8%; other overlap can add more.
- Accuracy improvements do not by themselves establish acceptable false-approval rates. Examine the exact counts above.
- Local integration and API checks do not constitute remote Hugging Face deployment or live database validation.

## Files

- [baseline_calibration_diagnostic.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/baseline_calibration_diagnostic.json>)
- [candidate_calibration.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/candidate_calibration.png>)
- [candidate_confusion_matrix.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/candidate_confusion_matrix.png>)
- [candidate_model.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/candidate_model.pkl>)
- [candidate_scaler.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/candidate_scaler.pkl>)
- [comparison.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/comparison.png>)
- [development_split_manifest.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/development_split_manifest.csv>)
- [fresh_evaluation_1500.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/fresh_evaluation_1500.csv>)
- [fresh_evaluation_metadata.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/fresh_evaluation_metadata.json>)
- [identifiability_diagnostic.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/identifiability_diagnostic.json>)
- [improvement_report.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/improvement_report.json>)
- [incumbent_calibration.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/incumbent_calibration.png>)
- [incumbent_confusion_matrix.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/incumbent_confusion_matrix.png>)
- [power_native_grid.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/power_native_grid.csv>)
- [power_native_training.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/power_native_training.pkl>)
- [power_ovr_grid.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/power_ovr_grid.csv>)
- [power_ovr_training.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/power_ovr_training.pkl>)
- [protocol.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/protocol.json>)
- [raw_native_training.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/raw_native_training.pkl>)
- [raw_ovr_grid.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/raw_ovr_grid.csv>)
- [raw_ovr_training.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/raw_ovr_training.pkl>)
- [README.md](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/README.md>)
- [selection_frozen.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/selection_frozen.json>)
- [svm_permutation_importance.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/svm_permutation_importance.csv>)
- [svm_permutation_importance.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/svm_permutation_importance.png>)
- [validation_candidates.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/validation_candidates.csv>)

- [Runner](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/improve_model.py>)
- [Saved-policy implementation](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/decision_model.py>)
