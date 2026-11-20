# Verity v3.1.1 face-review SVM candidate

This offline candidate learns all three outcomes from six scores. The proposed 25–50 face-similarity band appears only in evaluation. Inference uses the fitted RBF SVM and its probability estimates. Verity still serves v3.1.0.

## Training

The generator uses the median and interquartile range of detected same-person LFW scores to model a clear comparison. A separate uncertain-face component includes examples with both ordinary and poor image quality. These distributions overlap. Their mixture and routing labels are design assumptions. Liveness, text mismatch, and recapture scenarios remain in the simulation.

The candidate trained on 7,000 synthetic cases including 3,000 Verified, 2,400 Manual Review, and 1,600 Rejected. All six features use min–max scaling fitted on these rows. The selected LIBSVM C-SVC uses an RBF kernel, C of 10, gamma of 1, inverse-frequency class weights, and LIBSVM probability estimation. Its probabilities reflect the training mixture. Production probability calibration would require representative labeled cases.

Development used a separate seed and three capture profiles. Scenario distributions, training class allocations, and gamma were explored on development data. Both the class balance and the label assumptions differ from v3.1.0, so the results evaluate the combined change. A fresh draw of 3,000 cases and three additional quality profiles were evaluated after candidate selection.

## Comparison

Both models saw identical inputs in each comparison. Strong evidence means OCR and liveness each scored at least 0.90. Each additional capture profile combines a fixed quality triple with perfect OCR and liveness and a sweep of fractional face scores.

| Measurement | v3.1.0 | v3.1.1 candidate |
|---|---:|---:|
| Original strong-evidence cases in the 25–50 band sent to review | 0/16 | 16/16 |
| Fresh strong-evidence cases in the band sent to review | 1/28 | 28/28 |
| New capture-profile probes in the band sent to review | 0/75 | 74/75 |
| Revised synthetic accuracy | 75.93% | 86.07% |
| Original synthetic accuracy | 76.73% | 67.33% |
| Originally labeled Verified cases routed to review | 62/900 | 260/900 |
| Revised synthetic Rejected cases automatically verified | 45/600 | 25/600 |

On the new capture profiles the candidate also rejected 68 of 75 below 25 and verified 146 of 150 above 50. The remaining cases in those two bands went to review. One in-band probe was verified. The model has learned approximate boundaries.

A sensitivity check used measured LFW scores with the other inputs fixed. Both models rejected 23 of 500 same-person pairs and all 500 different-person pairs. The candidate moved 19 same-person pairs from approval to review in aggregate. LFW informed the generator and the accompanying OCR, liveness, and quality scores were simulated. These counts do not estimate field performance. Evaluation on representative adjudicated selfie-to-ID cases is still outstanding.

## Reproduction

From this directory, use Python with NumPy and pandas, and LIBSVM's standard svm-train and svm-predict executables on PATH. Re-evaluating the v3.1.0 pickles also needs joblib and the scikit-learn version in its artifact manifest. A separate output directory keeps the saved candidate available for comparison.

```sh
python run.py train --out /tmp/verity-face-review
python run.py development --out /tmp/verity-face-review
python run.py evaluate --out /tmp/verity-face-review
```

The recorded run used native LIBSVM 3.10. Library versions can affect calibration and exact model bytes. The local baseline calculation used the archived SVM parameters and reproduced the full published v3.1.0 confusion matrix. The runner uses joblib for the baseline when that environment is available. The candidate is stored in standard LIBSVM text format with a separate scaler and class mapping. The comparison JSON gives the confusion matrices and prediction counts.
