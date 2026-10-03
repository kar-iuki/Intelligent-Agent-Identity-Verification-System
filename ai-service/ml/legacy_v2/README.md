# KYC experiment v2: reproducibility and deployment

Run from the repository root (Python 3.13 used for the recorded run):

```powershell
python -m venv .venv-kyc
.\.venv-kyc\Scripts\python.exe -m pip install -r ai-service/ml/requirements-experiment.lock.txt
.\.venv-kyc\Scripts\python.exe ai-service/ml/train_model.py --version 2.0.0 --jobs 2
.\.venv-kyc\Scripts\python.exe ai-service/tests/test_svm.py
.\.venv-kyc\Scripts\python.exe ai-service/tests/test_kyc_experiment.py
node --test backend/tests/kycDecision.test.js
```

`requirements-experiment.lock.txt` is an isolated experiment environment; it does
not require downloading the image/face/OCR models. Production still uses
`ai-service/requirements.txt`. Pickles require compatible scikit-learn (1.9.0 in
this run); load only trusted artifacts. No online or automatic training exists.
Do not run a training job concurrently with the serving process. Stop/restart the
service after copying the **whole** `ml/models` artifact set; startup verifies
model/scaler hashes, version and feature contract. The Hugging Face Space must
include those files and use the matching dependency versions. This local change
does not itself publish a new Space revision.

## Data and methodology

The exact shared feature order is:
1. `face_match_score`: ArcFace score, 0–100.
2. `liveness_score`: anti-spoof score, 0–1.
3. `ocr_confidence_score`: document text agreement score, 0–1.
4. `blur_score`: raw Laplacian variance, nonnegative (higher means sharper).
5. `brightness_score`: raw mean HSV V, 0–255.
6. `contrast_score`: raw grayscale standard deviation, 0–127.5.

**Quality scores are not normalized inputs.** The 0.72/0.81/0.76 example is valid
numerically but means an extremely low-quality image in the current pipeline.
There is no documented conversion from generic 0–1 quality ratings to these raw
metrics; silently guessing one would break compatibility. MinMaxScaler handles
normalization after receiving raw features and clips to training extrema.

The stored local LFW (1,000 pairs), NUAA (1,200 presentations), MIDV quality
(500 frames), and MIDV OCR measurements are read directly. Their hashes and
computed moments are recorded in the dataset metadata. We do not claim to have
rerun their source images or independently verified historical measurements.
LFW uses the project's face scoring implementation; NUAA measures real/photo
presentations; MIDV OCR measures text similarity to ground-truth fields, not
solely EasyOCR's internal confidence. None supplies three-class KYC decisions.

`generation_config.json` fixes all scenario probabilities, borderline parameters,
quality shifts and observation noise **before** test evaluation. There are 6,000
Verified, 2,000 Manual Review and 2,000 Rejected simulated adjudication outcomes.
These are experimental quotas, not prevalence estimates. Scenarios are sampled
within each quota. Faces and liveness use truncated normals informed by local
measured means/SDs. Truncation changes resulting moments, especially near zero or
one. Clear OCR uses measured moments conditional on the upper half of observed
agreement (the conditioning itself is an assumption). Quality uses a continuous
multivariate normal over log1p(blur), brightness and contrast fitted to measured
quality covariance. Fresh draws avoid copying benchmark observations.

Class labels describe *assumed latent scenarios*, not a threshold applied to
observed scores. Borderline genuine and unresolved cases deliberately share
observed distributions, representing information missing from the six scores.
No labels are flipped and no accuracy is targeted. This ambiguity is a modelling
assumption, not evidence that real adjudicators would label those cases that way.
The simulator therefore tests behavior under an explicit assumed population;
it cannot establish a real operational decision policy.

Rejected scenarios include face mismatch, photograph presentation, document
mismatch, difficult face mismatch and difficult presentation attacks; unaffected
channels can remain strong. Review contains uncertain face, OCR, presentation,
multiple uncertainties and genuine recapture cases. Quality is shared across
identity outcomes except the explicitly simulated recapture condition. Poor
latent sharpness/contrast reduces OCR agreement in every class. Brightness alone
does not assign a rejected label; excellent quality does not replace identity
signals. The coefficients in this measurement simulation are assumptions, not
manual classifier feature weights. The SVM learns its boundary without weights
on individual features.

Exact and near-duplicate checks occur before splitting, failing closed if found.
The narrow near-duplicate tolerance is documented in the report and is a useful
screen, not proof of statistical independence. There are no persistent simulated
subjects or resampled parent observations crossing partitions. A stratified
70/15/15 row split gives 7,000/1,500/1,500. `split_manifest.csv` records assignments;
its row IDs and the latent scenarios never enter the seven-column training CSV.

Each SVM grid has C=[0.1,1,10,100] and gamma=[0.001,0.01,0.1,1,scale,auto], with
5-fold shuffled stratification, macro F1, RBF kernel, balanced classes and seed
42. MinMaxScaler is inside the grid Pipeline, so each fold fits only on its
training rows. Refit uses only the 7,000 training rows. Both six-feature and
identity-only SVMs are tuned independently using identical folds and candidate
grids. Identity-only order is face, liveness, OCR, the first three columns of the
shared contract. The Decision Tree grid searches max_depth=[3,5,8,None] and
min_samples_leaf=[5,20,50], also on training CV only.

Sigmoid CalibratedClassifierCV wraps a FrozenEstimator, learning calibration on
validation only without changing the SVM or scaler. Deployed decisions use the
largest calibrated probability. Calibration can change the balanced SVM's
original decisions toward the experimental class prior; this is reported rather
than hidden. The tree baseline reports its native predictions/probabilities;
a separate sigmoid tree comparison is also saved for probability diagnostics.
Validation is consumed for calibration and is not an independent calibration
test. Test metrics, reliability curves and importance are computed only after
all models/calibrators are frozen. No test-guided redesign is performed.

Permutation importance is the actual drop in test macro F1 over 20 shuffles,
with standard deviation across shuffles. Correlated features can share or mask
importance. Tree importance is impurity decrease, with its known split-selection
biases; the two quantities are not interchangeable. Ablation uses paired bootstrap
resampling of the same test predictions (1,000 replicates). Its interval is
conditional on this generator and fitted models, not all training randomness or
real-world populations. Six features remain the production contract regardless
of ablation outcome; no feature is removed automatically.

## API and backend compatibility

`POST /api/svm/predict` accepts all six snake_case fields and returns display
labels (`Verified`, `Manual Review`, `Rejected`) and a `probabilities` mapping.
It also returns the three legacy probability fields. Class columns are mapped
using `classes_`; no positional class assumption is made.

All-camelCase requests remain supported and receive the existing lowercase
`finalDecision` enum (`verified`, `review`, `rejected`) required by Node/Supabase.
Units are identical for both spellings. Supplying both aliases for one feature,
unknown fields, missing values, booleans, strings, non-finite numbers, negative
values or out-of-range bounded scores returns HTTP 400. A missing/inconsistent
model bundle returns 503. High but finite raw blur is allowed, not assigned an
arbitrary physical maximum. Model responses always say `decisionBasis=svm_model`.

The only backend changes remove number coercion and zero defaults for missing
scores. Invalid evidence fails before inference or placeholder fallback.
Existing fallback decisions still say `placeholder_threshold`, log the reason,
and persist their different basis through the existing controller. Their 0/1
values are rule outputs, not calibrated model certainty. No database migration
or changes to face/OCR/liveness processing were made by this experiment.

## Historical audit and limitations

Old code/artifacts are preserved in `legacy_v1`; the original 4,000-row CSV is
retained. The original notebooks are historical v1 analyses, not the authority
for v2 results. Use `train_model.py` for reproducible v2 training.

The old generator preassigned labels then sampled almost isolated ranges in all
six channels, including quality. Training-set-only scaler fitting was correct
at the outer split level, but notebook CV reused that scaler across folds. The
retraining script hard-coded earlier grid winners. There is no direct target
column in its predictor or observed code evidence of final-test fitting; absence
of historical repeated test use cannot be established. The audit reports exact,
conflicting and near duplicates and individual-feature training CV scores.

The new audit addresses target/identifier exclusion, artificial class patterns,
within-class variation, fold-local scaling, cross-split duplicates, explicit
calibration separation, fixed protocol before test, trivial feature separators
and scenario-label artifacts. If accuracy >=98%, the report flags a near-perfect
result for investigation; it must not trigger automatic label alteration or
parameter changes. Even moderate performance is not proof of realism.

Dissertation limitations: synthetic labels and assumed joint dependencies;
limited benchmark domains and sample sizes; source measurement version drift
(the image pipeline has ongoing local changes); no demographic fairness, modern
attack, camera/domain shift or external prospective validation; text agreement
cannot prove document authenticity; experimental class prior affects calibration;
false verification costs are not represented by macro F1 alone. A real deployment
needs confirmed labels, cost-aware policy validation and external calibration.
Future retraining is explicit offline batch work using administrator-confirmed
records, never triggered by completing a KYC attempt.
