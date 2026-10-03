# Automated offline KYC improvement experiment (v3)

Run from the repository root using the existing locked environment:

```powershell
.\.venv-kyc\Scripts\python.exe ai-service/ml/improve_model.py --jobs 3 --promote
```

The runner saves resumable training checkpoints and refuses to rerun a completed
experiment against the same evaluation draw. Inspect `improvement_report.json`
after completion. Do not delete it to try different models on the same test set.
Reproducing this exact experiment in a clean copy is valid; its evaluation is
then reproduction, not a newly unseen test. Source modules `ml.decision_model`
and their matching scikit-learn runtime must accompany the pickled v3 model.

## What is automated

- Reuse the original 7,000 training rows and unchanged labels.
- Fit three additional 24-candidate RBF SVM grids with five-fold training CV.
- Compare native multiclass SVC with explicit OneVsRest SVC using continuous
  binary margins. Every underlying SVC keeps balanced classes and seed 42.
- Compare raw features with a training-fitted Yeo–Johnson quality transform.
  The latter normalizes skewed quality distributions, then uses MinMaxScaler.
  Six input columns and their order remain unchanged; identity columns are
  untouched by the quality transformation. All fitted transforms stay inside CV.
- Reuse the original raw-native grid winner, with recorded dataset-hash and
  training-CV provenance; do not repeat that already completed search.
- Divide the original 1,500 validation rows into 750 calibration and 750 selection
  rows, stratified with seed 42. Each has 450 Verified, 150 Review, 150 Rejected.
- Fit sigmoid, isotonic and temperature calibrators on calibration rows only.
  Isotonic has a particular overfitting risk at this sample size; its independent
  selection metrics are retained rather than assuming it is superior.
- Compare native classifier decisions and probability-based review policies.
  Policy candidates vary a review preference multiplier, verification confidence
  threshold and verification margin. These are empirically selected decision
  parameters, not manual feature weights. They never alter returned probabilities.
- Select the highest validation accuracy among candidates whose macro F1,
  Manual Review recall and both false-verification counts are no worse than a
  raw-native-sigmoid comparator calibrated on the same 750 calibration rows.
- Freeze the candidate, then draw one fresh 1,500-row synthetic evaluation set
  (900/300/300). Its independent seed comes from NumPy SeedSequence(42).
- Audit duplicates against all 10,000 original rows, then evaluate the frozen
  candidate and saved v2 incumbent on identical fresh rows. Also record the
  saved tree and identity-only models as descriptive references, not candidates.
- Report paired bootstrap intervals, calibration diagnostics and permutation
  importance. A predeclared release check requires higher fresh accuracy,
  non-decreasing macro F1, and no increase in either false-verification count.
  Failure leaves v2 active; it does not trigger retuning or candidate switching.

## What this experiment can establish

This is a model/decision-policy comparison under an unchanged simulator. It does
not improve accuracy by changing labels or making class distributions easier.
The original test set is retired because its outcomes informed the new research
questions. It is neither training data nor selection data here. The fresh test
is generated only after candidate selection. The release check uses it once for
acceptance, not tuning; report that distinction when presenting promoted models.

The existing simulator intentionally contains some observationally identical
Verified and Manual Review components. Their missing adjudication information
cannot be recovered by a more powerful classifier. Better score modelling and
calibration may improve measured performance, but high accuracy is not promised.

A better score on the fresh set demonstrates improvement only for the same
synthetic assumptions. It does not establish real-world KYC performance. The
bootstrap interval describes these fitted models on this simulated population,
not uncertainty over all possible training data or operational conditions.

## Deployment contract

The model remains static after training; there is no online learning or automatic
retraining when KYC completes. `svmService` now calls the saved model's `predict`
method so a learned review policy is honored. It still returns the classifier's
unchanged class probabilities, `decisionBasis=svm_model`, and model version. A
new optional `decisionPolicy` object explains whether the decision used native
boundaries or calibrated-probability review parameters. The Node/Supabase enum
contract and fallback provenance remain unchanged.

Prior v2 artifacts and reports are preserved under `ml/legacy_v2`. If promoted,
the new SVM and raw MinMaxScaler replace the production pair; the fitted quality
transform is packaged inside the model. No remote Hugging Face publication or
live database writes are performed by this experiment.
