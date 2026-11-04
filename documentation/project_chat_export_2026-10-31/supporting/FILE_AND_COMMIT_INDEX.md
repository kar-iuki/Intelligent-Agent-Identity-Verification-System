# Repository files and Git history

Snapshot date: 31 October 2026. Paths are repository-relative. This is the visible project-file inventory excluding dependency environments and this export; it is not a list of private .env values.


---

## Commit history

```text
7da76db | 2026-09-01T14:38:31+03:00 | Initial commit
eda97de | 2026-09-10T11:19:57+03:00 | registration and login
90d767c | 2026-09-17T09:21:53+03:00 | account creation and login
bff3291 | 2026-09-17T09:23:02+03:00 | fraud guardrails
e60bb39 | 2026-09-17T09:23:46+03:00 | agent dashboard
a576ce3 | 2026-09-17T09:24:46+03:00 | agent dashboard and json packages
afe862b | 2026-09-17T09:26:09+03:00 | admin dashboard and auth
5db1968 | 2026-09-17T09:27:30+03:00 | extra guardrails and auth
eaeea1f | 2026-09-17T09:30:43+03:00 | controllers and routes
0912335 | 2026-09-17T09:31:31+03:00 | database configuration
e208068 | 2026-09-17T09:32:21+03:00 | capture of face and dashboard to diaplay results
e564d7b | 2026-09-17T09:32:47+03:00 | configuration of ports and listening ports
f7019cb | 2026-09-17T09:33:27+03:00 | ngrok for live testing
d6031d6 | 2026-09-17T09:39:43+03:00 | liveness and face matching
2172d3e | 2026-09-17T09:40:26+03:00 | ocr for extraction of details
94ff884 | 2026-09-17T09:46:04+03:00 | testing and python app
915231b | 2026-09-17T09:46:56+03:00 | ai documentation
eff4a34 | 2026-09-17T09:49:18+03:00 | dataset and training
ec8448d | 2026-09-17T09:55:02+03:00 | liveliness detection environment
85abd34 | 2026-09-17T09:59:08+03:00 | python routes
9d0fe2c | 2026-09-17T09:59:48+03:00 | readme file for the project
1119c41 | 2026-09-18T21:30:55+03:00 | updates to ocr and what it picks from an ID
870b303 | 2026-10-03T08:03:24+03:00 | updates
ebb5721 | 2026-10-16T07:27:00+03:00 | passkey
a8f64cb | 2026-10-20T07:24:43+03:00 | captcha and forgot password
8065ad3 | 2026-10-26T17:05:35+03:00 | Create vercel.json
4850f24 | 2026-10-26T17:22:53+03:00 | final details
8e00a21 | 2026-10-26T17:23:02+03:00 | Merge branch 'main' of https://github.com/kar-iuki/Intelligent-Agent-Identity-Verification-System
3a83f56 | 2026-10-30T22:24:42+03:00 | final updates
7898e9e | 2026-10-30T22:39:36+03:00 | Remove blink twice and open your eyes
2382407 | 2026-10-31T09:07:14+03:00 | landing page
7bd4632 | 2026-10-31T09:22:07+03:00 | frontend updates

```


---

## Commit change summaries

```text
7da76db | 2026-09-01 | Initial commit

 README.md | 1 +
 1 file changed, 1 insertion(+)
eda97de | 2026-09-10 | registration and login

 .gitignore                                        |   26 +
 README.md                                         |  160 +-
 ai-service/.env.example                           |    2 +
 ai-service/.gitignore                             |    7 +
 ai-service/app.py                                 |   35 +
 ai-service/models/.gitkeep                        |    0
 ai-service/requirements.txt                       |    9 +
 ai-service/routes/.gitkeep                        |    0
 ai-service/routes/__init__.py                     |    0
 ai-service/routes/qualityRoutes.py                |   49 +
 ai-service/services/.gitkeep                      |    0
 ai-service/services/__init__.py                   |    0
 ai-service/services/imageQualityService.py        |   60 +
 ai-service/tests/test_image_quality.py            |   73 +
 backend/.env.example                              |   18 +
 backend/.gitignore                                |    2 +
 backend/package-lock.json                         | 1090 ++++++++++++
 backend/package.json                              |   19 +
 backend/server.js                                 |   27 +
 backend/src/controllers/.gitkeep                  |    0
 backend/src/controllers/agentController.js        |  314 ++++
 backend/src/controllers/authController.js         |  199 +++
 backend/src/controllers/verificationController.js |  285 ++++
 backend/src/middleware/.gitkeep                   |    0
 backend/src/middleware/authMiddleware.js          |   43 +
 backend/src/middleware/roleMiddleware.js          |   13 +
 backend/src/middleware/uploadMiddleware.js        |   45 +
 backend/src/routes/.gitkeep                       |    0
 backend/src/routes/agentRoutes.js                 |   33 +
 backend/src/routes/authRoutes.js                  |   19 +
 backend/src/routes/verificationRoutes.js          |   15 +
 backend/src/services/.gitkeep                     |    0
 backend/src/services/verificationService.js       |   47 +
 backend/src/utils/supabaseAnon.js                 |   19 +
 backend/src/utils/supabaseClient.js               |   19 +
 database/audit_logs_nullable_request.sql          |    6 +
 database/rls_policies.sql                         |   52 +
 database/schema.sql                               |  141 ++
 database/storage_agent_documents.sql              |   55 +
 frontend/.gitignore                               |   24 +
 frontend/index.html                               |   13 +
 frontend/package-lock.json                        | 1844 +++++++++++++++++++++
 frontend/package.json                             |   21 +
 frontend/src/App.vue                              |    8 +
 frontend/src/components/.gitkeep                  |    0
 frontend/src/components/CameraCapture.vue         |  223 +++
 frontend/src/components/ImageUpload.vue           |  224 +++
 frontend/src/main.js                              |    6 +
 frontend/src/router/index.js                      |   93 ++
 frontend/src/services/agentService.js             |   29 +
 frontend/src/services/api.js                      |   38 +
 frontend/src/services/supabase.js                 |    8 +
 frontend/src/services/verificationService.js      |   14 +
 frontend/src/stores/.gitkeep                      |    0
 frontend/src/stores/authStore.js                  |  200 +++
 frontend/src/style.css                            |   19 +
 frontend/src/utils/authToken.js                   |   17 +
 frontend/src/views/AdminDashboard.vue             |  110 ++
 frontend/src/views/AgentDashboard.vue             |  803 +++++++++
 frontend/src/views/CompleteProfilePage.vue        |  230 +++
 frontend/src/views/HomeView.vue                   |   31 +
 frontend/src/views/LoginPage.vue                  |  248 +++
 frontend/src/views/PendingVerificationPage.vue    |   88 +
 frontend/src/views/RegisterPage.vue               |  277 ++++
 frontend/vite.config.js                           |   15 +
 package-lock.json                                 |  329 ++++
 package.json                                      |   25 +
 67 files changed, 7818 insertions(+), 1 deletion(-)
90d767c | 2026-09-17 | account creation and login

 .gitignore                          |   4 ++
 backend/src/routes/authRoutes.js    |   2 +
 frontend/src/router/index.js        |  25 ++++++++
 frontend/src/services/supabase.js   |  12 +++-
 frontend/src/stores/authStore.js    | 123 +++++++++++++++++++++++++++++++-----
 frontend/src/views/LoginPage.vue    |  40 ++++++++----
 frontend/src/views/RegisterPage.vue |  62 +++++++++---------
 7 files changed, 205 insertions(+), 63 deletions(-)
bff3291 | 2026-09-17 | fraud guardrails

 backend/server.js                                  |  60 +++++-
 backend/src/config/blockedEmailDomains.js          |  17 ++
 backend/src/config/fraudConfig.js                  |  58 +++++
 .../src/middleware/fraudGuardrailsMiddleware.js    | 236 +++++++++++++++++++++
 backend/src/services/strikeService.js              | 153 +++++++++++++
 backend/src/utils/auditLogger.js                   | 124 +++++++++++
 backend/src/utils/auditTrailVerifier.js            | 129 +++++++++++
 backend/src/utils/runAuditTrailCheck.js            |  20 ++
 8 files changed, 794 insertions(+), 3 deletions(-)
e60bb39 | 2026-09-17 | agent dashboard

 frontend/src/views/AgentAuditLog.vue       | 197 +++++++++
 frontend/src/views/AgentDashboard.vue      | 657 +++++++++++++++++++++++------
 frontend/src/views/AgentPlatformPage.vue   | 106 +++++
 frontend/src/views/CheckEmailPage.vue      | 198 +++++++++
 frontend/src/views/CompleteProfilePage.vue |  74 +++-
 5 files changed, 1103 insertions(+), 129 deletions(-)
a576ce3 | 2026-09-17 | agent dashboard and json packages

 ai-service/backend/package-lock.json  | 261 ++++++++++++++++++++++++++++++++++
 ai-service/backend/package.json       |   5 +
 ai-service/frontend/package-lock.json | 120 ++++++++++++++++
 ai-service/frontend/package.json      |   5 +
 frontend/package-lock.json            |  93 ++++++++++++
 frontend/package.json                 |   2 +
 frontend/src/services/agentService.js |  44 +++++-
 frontend/src/services/api.js          |  22 ++-
 frontend/src/utils/auditLabels.js     |  23 +++
 package.json                          |   4 +-
 10 files changed, 571 insertions(+), 8 deletions(-)
afe862b | 2026-09-17 | admin dashboard and auth

 backend/src/controllers/authController.js  |  261 ++++-
 backend/src/middleware/uploadMiddleware.js |    4 +
 backend/src/routes/adminRoutes.js          |   38 +
 frontend/src/services/adminService.js      |   78 ++
 frontend/src/views/AdminDashboard.vue      | 1517 +++++++++++++++++++++++++++-
 5 files changed, 1814 insertions(+), 84 deletions(-)
5db1968 | 2026-09-17 | extra guardrails and auth

 backend/package-lock.json                    | 234 ++++++++-
 backend/package.json                         |   6 +-
 backend/src/controllers/adminController.js   | 733 +++++++++++++++++++++++++++
 backend/src/middleware/authMiddleware.js     |   8 +
 frontend/src/services/socket.js              |  30 ++
 frontend/src/services/verificationService.js |  18 +-
 frontend/src/utils/deviceFingerprint.js      |  65 +++
 7 files changed, 1088 insertions(+), 6 deletions(-)
eaeea1f | 2026-09-17 | controllers and routes

 backend/src/controllers/agentController.js        | 384 +++++++----
 backend/src/controllers/verificationController.js | 738 +++++++++++++++++++++-
 backend/src/middleware/requestLogger.js           |  22 +
 backend/src/routes/agentRoutes.js                 |  17 +-
 backend/src/routes/verificationRoutes.js          |  20 +-
 backend/src/services/accessControlService.js      | 160 +++++
 backend/src/services/realtimeService.js           |  81 +++
 backend/src/services/verificationService.js       | 155 +++++
 backend/src/utils/validateDateOfBirth.js          |  46 ++
 9 files changed, 1471 insertions(+), 152 deletions(-)
0912335 | 2026-09-17 | database configuration

 database/access_control_module8.sql | 16 ++++++++++++
 database/agents_date_of_birth.sql   |  5 ++++
 database/audit_logging_module10.sql | 52 +++++++++++++++++++++++++++++++++++++
 database/rls_policies.sql           |  8 ++++++
 database/schema.sql                 |  8 +++++-
 5 files changed, 88 insertions(+), 1 deletion(-)
e208068 | 2026-09-17 | capture of face and dashboard to diaplay results

 frontend/src/components/DocumentCaptureStep.vue | 308 ++++++++++++++
 frontend/src/components/Lightbox.vue            | 177 ++++++++
 frontend/src/components/LiveSelfieChallenge.vue | 544 ++++++++++++++++++++++++
 frontend/src/components/ScoreBar.vue            |  86 ++++
 4 files changed, 1115 insertions(+)
e564d7b | 2026-09-17 | configuration of ports and listening ports

 frontend/vite.config.js | 8 ++++++++
 1 file changed, 8 insertions(+)
f7019cb | 2026-09-17 | ngrok for live testing

 ngrok.yml | 26 ++++++++++++++++++++++++++
 1 file changed, 26 insertions(+)
d6031d6 | 2026-09-17 | liveness and face matching

 ai-service/routes/faceRoutes.py            |  54 ++++++++++
 ai-service/routes/livenessRoutes.py        |  48 +++++++++
 ai-service/services/faceMatchService.py    | 134 +++++++++++++++++++++++
 ai-service/services/imageQualityService.py |  86 +++++++++++++--
 ai-service/services/livenessService.py     | 168 +++++++++++++++++++++++++++++
 ai-service/tests/test_face_match.py        |  70 ++++++++++++
 ai-service/tests/test_liveness.py          |  60 +++++++++++
 ai-service/tests/test_ocr.py               |  77 +++++++++++++
 8 files changed, 686 insertions(+), 11 deletions(-)
2172d3e | 2026-09-17 | ocr for extraction of details

 ai-service/routes/ocrRoutes.py    |  58 +++++++++
 ai-service/services/ocrService.py | 242 ++++++++++++++++++++++++++++++++++++++
 2 files changed, 300 insertions(+)
94ff884 | 2026-09-17 | testing and python app

 ai-service/app.py              |   6 +++
 ai-service/silent_face/test.py | 109 +++++++++++++++++++++++++++++++++++++++++
 2 files changed, 115 insertions(+)
915231b | 2026-09-17 | ai documentation

 ai-service/requirements.txt                        |    8 +-
 ai-service/silent_face/requirements.txt            |    8 +
 .../anti_spoof_models/2.7_80x80_MiniFASNetV2.pth   |  Bin 0 -> 1849453 bytes
 .../4_0_0_80x80_MiniFASNetV1SE.pth                 |  Bin 0 -> 1856130 bytes
 .../Widerface-RetinaFace.caffemodel                |  Bin 0 -> 1866013 bytes
 .../resources/detection_model/deploy.prototxt      | 2499 ++++++++++++++++++++
 6 files changed, 2514 insertions(+), 1 deletion(-)
eff4a34 | 2026-09-17 | dataset and training

 .../silent_face/src/data_io/dataset_folder.py      |  65 ++++
 .../silent_face/src/data_io/dataset_loader.py      |  33 ++
 ai-service/silent_face/src/data_io/transform.py    | 347 +++++++++++++++++++++
 ai-service/silent_face/src/train_main.py           | 146 +++++++++
 4 files changed, 591 insertions(+)
ec8448d | 2026-09-17 | liveliness detection environment

 ai-service/silent_face/README.md                   | 112 ++++
 ai-service/silent_face/src/__init__.py             |   0
 ai-service/silent_face/src/anti_spoof_predict.py   | 153 ++++++
 ai-service/silent_face/src/data_io/__init__.py     |   0
 ai-service/silent_face/src/data_io/functional.py   | 589 +++++++++++++++++++++
 ai-service/silent_face/src/default_config.py       |  73 +++
 ai-service/silent_face/src/generate_patches.py     |  65 +++
 ai-service/silent_face/src/model_lib/MiniFASNet.py | 296 +++++++++++
 ai-service/silent_face/src/model_lib/MultiFTNet.py |  79 +++
 ai-service/silent_face/src/model_lib/__init__.py   |   0
 ai-service/silent_face/src/utility.py              |  41 ++
 11 files changed, 1408 insertions(+)
85abd34 | 2026-09-17 | python routes

 ai-service/routes/qualityRoutes.py | 36 ++++++++++++++++++++++++++++++++++--
 backend/.env.example               |  8 ++++++++
 2 files changed, 42 insertions(+), 2 deletions(-)
9d0fe2c | 2026-09-17 | readme file for the project

 README.md | 30 +++++++++++++++++++++++++++++-
 1 file changed, 29 insertions(+), 1 deletion(-)
1119c41 | 2026-09-18 | updates to ocr and what it picks from an ID

 .gitignore                                        |   1 +
 ai-service/routes/ocrRoutes.py                    |  11 +-
 ai-service/services/documentPreprocessService.py  | 349 ++++++++++
 ai-service/services/imageQualityService.py        |   6 +-
 ai-service/services/ocrService.py                 | 771 ++++++++++++++++------
 ai-service/tests/test_document_preprocess.py      | 109 +++
 ai-service/tests/test_ocr.py                      | 265 +++++++-
 backend/src/controllers/adminController.js        |   5 +
 backend/src/controllers/verificationController.js |  37 +-
 frontend/src/views/AdminDashboard.vue             |   7 +
 10 files changed, 1353 insertions(+), 208 deletions(-)
870b303 | 2026-10-03 | updates

 .gitignore                                         |     7 +
 README.md                                          |    96 +
 ai-service/app.py                                  |     2 +
 ai-service/config/ocr_templates.json               |   142 +
 ai-service/ml/README.md                            |   166 +
 ai-service/ml/audit.py                             |    60 +
 ai-service/ml/data/benchmarks/lfw_face_match.csv   |  1001 ++
 .../ml/data/benchmarks/midv_image_quality.csv      |   501 +
 ai-service/ml/data/benchmarks/midv_ocr.csv         |   481 +
 ai-service/ml/data/benchmarks/nuaa_liveness.csv    |  1201 +++
 ai-service/ml/data/kyc_synthetic_dataset_10000.csv | 10001 +++++++++++++++++++
 .../data/kyc_synthetic_dataset_10000.metadata.json |   250 +
 .../ml/data/synthetic_verification_dataset.csv     |  4001 ++++++++
 ai-service/ml/decision_model.py                    |    63 +
 ai-service/ml/evaluation.py                        |   117 +
 ai-service/ml/experiments/v3/README.md             |    82 +
 ai-service/ml/experiments/v3/SUMMARY.md            |   128 +
 .../v3/baseline_calibration_diagnostic.json        |    30 +
 .../ml/experiments/v3/candidate_calibration.png    |   Bin 0 -> 78148 bytes
 .../experiments/v3/candidate_confusion_matrix.png  |   Bin 0 -> 30181 bytes
 ai-service/ml/experiments/v3/candidate_model.pkl   |   Bin 0 -> 398221 bytes
 ai-service/ml/experiments/v3/candidate_scaler.pkl  |   Bin 0 -> 903 bytes
 ai-service/ml/experiments/v3/comparison.png        |   Bin 0 -> 55832 bytes
 .../experiments/v3/development_split_manifest.csv  |  8501 ++++++++++++++++
 .../ml/experiments/v3/fresh_evaluation_1500.csv    |  1501 +++
 .../experiments/v3/fresh_evaluation_metadata.json  |   250 +
 .../experiments/v3/identifiability_diagnostic.json |    33 +
 .../ml/experiments/v3/improvement_report.json      |  1160 +++
 .../ml/experiments/v3/incumbent_calibration.png    |   Bin 0 -> 71291 bytes
 .../experiments/v3/incumbent_confusion_matrix.png  |   Bin 0 -> 30568 bytes
 ai-service/ml/experiments/v3/power_native_grid.csv |    25 +
 .../ml/experiments/v3/power_native_training.pkl    |   Bin 0 -> 404648 bytes
 ai-service/ml/experiments/v3/power_ovr_grid.csv    |    25 +
 .../ml/experiments/v3/power_ovr_training.pkl       |   Bin 0 -> 743208 bytes
 ai-service/ml/experiments/v3/protocol.json         |    46 +
 .../ml/experiments/v3/raw_native_training.pkl      |   Bin 0 -> 397594 bytes
 ai-service/ml/experiments/v3/raw_ovr_grid.csv      |    25 +
 ai-service/ml/experiments/v3/raw_ovr_training.pkl  |   Bin 0 -> 733846 bytes
 ai-service/ml/experiments/v3/selection_frozen.json |    38 +
 .../experiments/v3/svm_permutation_importance.csv  |     7 +
 .../experiments/v3/svm_permutation_importance.png  |   Bin 0 -> 30162 bytes
 .../ml/experiments/v3/validation_candidates.csv    |   493 +
 .../ml/experiments/v3/verification_checks.json     |    22 +
 ai-service/ml/generate_dataset.py                  |    98 +
 ai-service/ml/generation_config.json               |    41 +
 ai-service/ml/improve_model.py                     |   310 +
 ai-service/ml/improvement_reporting.py             |    78 +
 ai-service/ml/legacy_v1/evaluation_report.json     |    71 +
 ai-service/ml/legacy_v1/generate_dataset.py        |   154 +
 ai-service/ml/legacy_v1/models/model_version.txt   |     2 +
 ai-service/ml/legacy_v1/models/scaler.pkl          |   Bin 0 -> 903 bytes
 ai-service/ml/legacy_v1/models/svm_kyc_model.pkl   |   Bin 0 -> 100723 bytes
 ai-service/ml/legacy_v1/train_model.py             |   173 +
 ai-service/ml/legacy_v2/README.md                  |   164 +
 ai-service/ml/legacy_v2/generation_config.json     |    41 +
 .../ml/legacy_v2/models/artifact_manifest.json     |    34 +
 .../legacy_v2/models/decision_tree_calibrated.pkl  |   Bin 0 -> 3761 bytes
 .../ml/legacy_v2/models/decision_tree_model.pkl    |   Bin 0 -> 2817 bytes
 .../ml/legacy_v2/models/identity_only_scaler.pkl   |   Bin 0 -> 799 bytes
 .../ml/legacy_v2/models/identity_only_svm.pkl      |   Bin 0 -> 289792 bytes
 ai-service/ml/legacy_v2/models/model_version.txt   |     2 +
 ai-service/ml/legacy_v2/models/scaler.pkl          |   Bin 0 -> 903 bytes
 ai-service/ml/legacy_v2/models/svm_kyc_model.pkl   |   Bin 0 -> 397523 bytes
 ai-service/ml/legacy_v2/reports/FILE_INDEX.md      |    79 +
 .../ml/legacy_v2/reports/TECHNICAL_SUMMARY.md      |   208 +
 .../ml/legacy_v2/reports/ablation_comparison.json  |   459 +
 .../legacy_v2/reports/benchmark_measurements.json  |   260 +
 .../ml/legacy_v2/reports/correlation_matrix.png    |   Bin 0 -> 90824 bytes
 .../reports/decision_tree_calibration.png          |   Bin 0 -> 77572 bytes
 .../reports/decision_tree_confusion_matrix.png     |   Bin 0 -> 30054 bytes
 .../reports/decision_tree_feature_importance.csv   |     7 +
 .../reports/decision_tree_feature_importance.png   |   Bin 0 -> 32452 bytes
 .../reports/decision_tree_grid_search.csv          |    13 +
 .../reports/descriptive_statistics_by_class.csv    |     6 +
 .../legacy_v2/reports/distribution_blur_score.png  |   Bin 0 -> 31994 bytes
 .../reports/distribution_brightness_score.png      |   Bin 0 -> 35448 bytes
 .../reports/distribution_contrast_score.png        |   Bin 0 -> 35601 bytes
 .../reports/distribution_face_match_score.png      |   Bin 0 -> 33120 bytes
 .../reports/distribution_liveness_score.png        |   Bin 0 -> 29133 bytes
 .../reports/distribution_ocr_confidence_score.png  |   Bin 0 -> 33741 bytes
 .../reports/distribution_overlap_diagnostics.json  |   290 +
 .../ml/legacy_v2/reports/evaluation_report.json    |  1888 ++++
 .../ml/legacy_v2/reports/feature_correlations.csv  |     7 +
 .../reports/frozen_experiment_protocol.json        |    32 +
 .../ml/legacy_v2/reports/full_svm_calibration.png  |   Bin 0 -> 68260 bytes
 .../reports/full_svm_confusion_matrix.png          |   Bin 0 -> 29532 bytes
 .../ml/legacy_v2/reports/full_svm_grid_search.csv  |    25 +
 .../reports/identity_only_svm_calibration.png      |   Bin 0 -> 74304 bytes
 .../reports/identity_only_svm_confusion_matrix.png |   Bin 0 -> 32040 bytes
 .../legacy_v2/reports/identity_svm_grid_search.csv |    25 +
 .../reports/legacy_methodology_audit.json          |    30 +
 ai-service/ml/legacy_v2/reports/split_manifest.csv | 10001 +++++++++++++++++++
 .../reports/svm_permutation_importance.csv         |     7 +
 .../reports/svm_permutation_importance.png         |   Bin 0 -> 33961 bytes
 .../ml/legacy_v2/reports/verification_checks.json  |    27 +
 ai-service/ml/legacy_v2/train_model.py             |   214 +
 ai-service/ml/measure_benchmarks.py                |   286 +
 ai-service/ml/models/artifact_manifest.json        |    40 +
 ai-service/ml/models/decision_tree_calibrated.pkl  |   Bin 0 -> 3761 bytes
 ai-service/ml/models/decision_tree_model.pkl       |   Bin 0 -> 2817 bytes
 ai-service/ml/models/identity_only_scaler.pkl      |   Bin 0 -> 799 bytes
 ai-service/ml/models/identity_only_svm.pkl         |   Bin 0 -> 289792 bytes
 ai-service/ml/models/model_version.txt             |     2 +
 ai-service/ml/models/scaler.pkl                    |   Bin 0 -> 903 bytes
 ai-service/ml/models/svm_kyc_model.pkl             |   Bin 0 -> 398221 bytes
 ai-service/ml/reporting.py                         |    72 +
 ai-service/ml/reports/FILE_INDEX.md                |    81 +
 ai-service/ml/reports/TECHNICAL_SUMMARY.md         |   128 +
 ai-service/ml/reports/ablation_comparison.json     |     4 +
 ai-service/ml/reports/benchmark_measurements.json  |   260 +
 ai-service/ml/reports/correlation_matrix.png       |   Bin 0 -> 90824 bytes
 .../ml/reports/decision_tree_calibration.png       |   Bin 0 -> 83863 bytes
 .../ml/reports/decision_tree_confusion_matrix.png  |   Bin 0 -> 31260 bytes
 .../reports/decision_tree_feature_importance.csv   |     7 +
 .../reports/decision_tree_feature_importance.png   |   Bin 0 -> 32452 bytes
 .../ml/reports/decision_tree_grid_search.csv       |    13 +
 .../ml/reports/descriptive_statistics_by_class.csv |     6 +
 ai-service/ml/reports/distribution_blur_score.png  |   Bin 0 -> 31994 bytes
 .../ml/reports/distribution_brightness_score.png   |   Bin 0 -> 35448 bytes
 .../ml/reports/distribution_contrast_score.png     |   Bin 0 -> 35601 bytes
 .../ml/reports/distribution_face_match_score.png   |   Bin 0 -> 33120 bytes
 .../ml/reports/distribution_liveness_score.png     |   Bin 0 -> 29133 bytes
 .../reports/distribution_ocr_confidence_score.png  |   Bin 0 -> 33741 bytes
 .../reports/distribution_overlap_diagnostics.json  |   290 +
 ai-service/ml/reports/evaluation_report.json       |  1350 +++
 ai-service/ml/reports/feature_correlations.csv     |     7 +
 .../ml/reports/frozen_experiment_protocol.json     |    32 +
 ai-service/ml/reports/full_svm_calibration.png     |   Bin 0 -> 77805 bytes
 .../ml/reports/full_svm_confusion_matrix.png       |   Bin 0 -> 29753 bytes
 ai-service/ml/reports/full_svm_grid_search.csv     |    25 +
 .../ml/reports/identity_only_svm_calibration.png   |   Bin 0 -> 81280 bytes
 .../reports/identity_only_svm_confusion_matrix.png |   Bin 0 -> 32177 bytes
 ai-service/ml/reports/identity_svm_grid_search.csv |    25 +
 .../ml/reports/legacy_methodology_audit.json       |    30 +
 ai-service/ml/reports/split_manifest.csv           | 10001 +++++++++++++++++++
 .../ml/reports/svm_permutation_importance.csv      |     7 +
 .../ml/reports/svm_permutation_importance.png      |   Bin 0 -> 30162 bytes
 ai-service/ml/reports/verification_checks.json     |    27 +
 ai-service/ml/requirements-experiment.lock.txt     |    26 +
 ai-service/ml/requirements-ml.txt                  |     8 +
 ai-service/ml/schema.py                            |    38 +
 ai-service/ml/train_model.py                       |   214 +
 .../notebooks/01_distribution_analysis.ipynb       |  1242 +++
 ai-service/notebooks/02_model_training.ipynb       |  2052 ++++
 .../notebooks/03_kyc_experiment_results.ipynb      |    52 +
 ai-service/requirements.txt                        |     4 +-
 ai-service/routes/ocrRoutes.py                     |    22 +-
 ai-service/routes/qualityRoutes.py                 |    48 +-
 ai-service/routes/svmRoutes.py                     |    48 +
 ai-service/scripts/calibrate_ocr_template.py       |   319 +
 ai-service/services/documentPreprocessService.py   |   651 +-
 ai-service/services/imageQualityService.py         |   125 +-
 ai-service/services/mrzService.py                  |   354 +
 ai-service/services/ocrService.py                  |  1511 ++-
 ai-service/services/svmService.py                  |   134 +
 ai-service/tests/test_document_preprocess.py       |   157 +-
 ai-service/tests/test_kyc_experiment.py            |    40 +
 ai-service/tests/test_kyc_improvement.py           |    52 +
 ai-service/tests/test_ocr.py                       |   372 +
 ai-service/tests/test_svm.py                       |    92 +
 backend/.env.example                               |     7 +
 backend/package-lock.json                          |   427 +-
 backend/package.json                               |    10 +-
 backend/server.js                                  |     7 +-
 backend/src/config/passkeyConfig.js                |    12 +
 backend/src/controllers/adminController.js         |    88 +-
 backend/src/controllers/agentController.js         |    25 +-
 backend/src/controllers/authController.js          |    15 +-
 backend/src/controllers/verificationController.js  |   123 +-
 backend/src/routes/adminRoutes.js                  |     4 +
 backend/src/routes/authRoutes.js                   |     6 +
 backend/src/routes/passkeyRoutes.js                |    72 +
 backend/src/services/accessControlService.js       |   112 +-
 backend/src/services/documentRetentionService.js   |   103 +
 backend/src/services/passkeyService.js             |   107 +
 .../src/services/verificationFeedbackService.js    |   209 +
 backend/src/services/verificationService.js        |   104 +
 backend/src/utils/auditWindow.js                   |    21 +
 backend/tests/documentRetention.test.js            |    76 +
 backend/tests/helpers/passkeyMemoryDb.js           |    50 +
 backend/tests/kycDecision.test.js                  |    40 +
 backend/tests/passkeyDatabase.test.js              |    47 +
 backend/tests/passkeyRoutes.test.js                |    40 +
 backend/tests/passkeys.test.js                     |    87 +
 database/passkeys.sql                              |    69 +
 frontend/package-lock.json                         |  1119 ++-
 frontend/package.json                              |    12 +-
 frontend/playwright.config.js                      |    10 +
 frontend/src/components/DocumentCaptureStep.vue    |    69 +-
 frontend/src/components/LiveSelfieChallenge.vue    |    40 +-
 frontend/src/components/PasskeyButton.vue          |    17 +
 frontend/src/components/PasskeyDialog.vue          |    30 +
 frontend/src/components/PasskeyPrompt.vue          |    65 +
 frontend/src/composables/usePasskeySupport.js      |    22 +
 frontend/src/main.js                               |     1 +
 frontend/src/router/index.js                       |    16 +-
 frontend/src/services/adminService.js              |    13 +-
 frontend/src/services/agentService.js              |     5 +-
 frontend/src/services/api.js                       |     8 +-
 frontend/src/services/passkeyService.js            |    70 +
 frontend/src/services/supabase.js                  |     6 +-
 frontend/src/stores/authStore.js                   |    79 +-
 frontend/src/utils/authToken.js                    |     8 +-
 frontend/src/utils/passkeyStorage.js               |    37 +
 frontend/src/views/AdminDashboard.vue              |   260 +-
 frontend/src/views/AdminModelEvaluation.vue        |   544 +
 frontend/src/views/AgentAuditLog.vue               |     3 +-
 frontend/src/views/AgentDashboard.vue              |   203 +-
 frontend/src/views/AgentPlatformPage.vue           |     6 +-
 frontend/src/views/CompleteProfilePage.vue         |    24 +-
 frontend/src/views/LoginPage.vue                   |    57 +-
 frontend/src/views/ManagePasskeysPage.vue          |   104 +
 frontend/src/workspace.css                         |   129 +
 frontend/tests/e2e/passkeys.spec.js                |   134 +
 frontend/tests/e2e/server.mjs                      |    28 +
 frontend/tests/unit/passkeyCeremony.test.js        |    41 +
 frontend/tests/unit/passkeys.test.js               |    61 +
 frontend/vite.config.js                            |     2 +-
 frontend/vitest.config.js                          |     3 +
 219 files changed, 70202 insertions(+), 340 deletions(-)
ebb5721 | 2026-10-16 | passkey

 backend/src/routes/passkeyRoutes.js                |   6 +-
 ...stem_Implementation_Testing_and_Evaluation.docx | Bin 0 -> 52633 bytes
 ...System_Implementation_Testing_and_Evaluation.md | 304 ++++++++++++++++++++
 documentation/build_chapter5.py                    | 235 ++++++++++++++++
 documentation/export_chapter5.py                   |  33 +++
 frontend/src/App.vue                               |   5 +-
 frontend/src/components/AuthShell.vue              |  15 +
 frontend/src/components/PasskeyButton.vue          |   7 +-
 frontend/src/components/PasskeyPrompt.vue          |   4 +-
 frontend/src/components/WorkspaceShell.vue         |  75 +++++
 frontend/src/services/passkeyService.js            |   8 +
 frontend/src/views/AdminDashboard.vue              |  39 ++-
 frontend/src/views/AdminModelEvaluation.vue        |   1 -
 frontend/src/views/AgentAuditLog.vue               |   5 +-
 frontend/src/views/AgentDashboard.vue              |   6 +-
 frontend/src/views/AgentPlatformPage.vue           |  24 +-
 frontend/src/views/LoginPage.vue                   |  26 +-
 frontend/src/views/ManagePasskeysPage.vue          |   8 +-
 frontend/src/workspace.css                         | 308 ++++++++++++---------
 frontend/tests/e2e/passkeys.spec.js                |  10 +-
 frontend/tests/e2e/workspace.spec.js               |  89 ++++++
 frontend/tests/unit/passkeyCeremony.test.js        |  10 +-
 22 files changed, 1013 insertions(+), 205 deletions(-)
a8f64cb | 2026-10-20 | captcha and forgot password

 backend/src/controllers/authController.js   | 121 +++++++++++++++-
 backend/src/routes/authRoutes.js            |   6 +
 backend/src/routes/passkeyRoutes.js         |   7 +-
 backend/src/services/passkeyService.js      |  67 ++++++++-
 backend/src/utils/auditLogger.js            |   2 +
 backend/src/utils/captcha.js                | 103 ++++++++++++++
 backend/src/utils/supabaseAnon.js           |   3 +
 backend/tests/helpers/passkeyMemoryDb.js    |   8 ++
 backend/tests/passkeyDatabase.test.js       |   6 +
 backend/tests/passkeys.test.js              |  20 ++-
 database/passkeys.sql                       |  22 ++-
 frontend/index.html                         |   8 ++
 frontend/src/components/PasskeyPrompt.vue   |   3 +-
 frontend/src/components/WorkspaceShell.vue  |  10 +-
 frontend/src/composables/useTheme.js        |  24 ++++
 frontend/src/main.js                        |   3 +
 frontend/src/router/index.js                |  22 ++-
 frontend/src/services/api.js                |   6 +-
 frontend/src/services/passkeyService.js     |  69 ++++++++-
 frontend/src/stores/authStore.js            | 169 ++++++++++++++++++----
 frontend/src/utils/passkeyStorage.js        |   8 ++
 frontend/src/views/ForgotPasswordPage.vue   |  76 ++++++++++
 frontend/src/views/LoginPage.vue            | 213 ++++++++++++++++++++++++----
 frontend/src/views/ManagePasskeysPage.vue   |  14 +-
 frontend/src/views/ResetPasswordPage.vue    | 125 ++++++++++++++++
 frontend/src/workspace.css                  |  60 +++++++-
 frontend/tests/unit/passkeyCeremony.test.js |  13 +-
 27 files changed, 1091 insertions(+), 97 deletions(-)
8065ad3 | 2026-10-26 | Create vercel.json

 frontend/vercel.json | 8 ++++++++
 1 file changed, 8 insertions(+)
4850f24 | 2026-10-26 | final details

 backend/.env.example                               |   5 +
 backend/src/services/verificationService.js        |  27 +++-
 documentation/Chapter_5.docx                       | Bin 0 -> 51877 bytes
 documentation/Chapter_5_Final_Revised.docx         | Bin 0 -> 75433 bytes
 documentation/chapter5_word_qa/Chapter_5.pdf       | Bin 0 -> 590914 bytes
 documentation/chapter5_word_qa/final-1.png         | Bin 0 -> 185337 bytes
 documentation/chapter5_word_qa/final-10.png        | Bin 0 -> 219043 bytes
 documentation/chapter5_word_qa/final-11.png        | Bin 0 -> 246992 bytes
 documentation/chapter5_word_qa/final-2.png         | Bin 0 -> 177686 bytes
 documentation/chapter5_word_qa/final-3.png         | Bin 0 -> 229398 bytes
 documentation/chapter5_word_qa/final-4.png         | Bin 0 -> 180710 bytes
 documentation/chapter5_word_qa/final-5.png         | Bin 0 -> 208680 bytes
 documentation/chapter5_word_qa/final-6.png         | Bin 0 -> 212377 bytes
 documentation/chapter5_word_qa/final-7.png         | Bin 0 -> 230779 bytes
 documentation/chapter5_word_qa/final-8.png         | Bin 0 -> 158806 bytes
 documentation/chapter5_word_qa/final-9.png         | Bin 0 -> 165077 bytes
 documentation/chapter5_word_qa/page-1.png          | Bin 0 -> 185450 bytes
 documentation/chapter5_word_qa/page-10.png         | Bin 0 -> 219043 bytes
 documentation/chapter5_word_qa/page-11.png         | Bin 0 -> 246992 bytes
 documentation/chapter5_word_qa/page-2.png          | Bin 0 -> 177686 bytes
 documentation/chapter5_word_qa/page-3.png          | Bin 0 -> 229398 bytes
 documentation/chapter5_word_qa/page-4.png          | Bin 0 -> 180710 bytes
 documentation/chapter5_word_qa/page-5.png          | Bin 0 -> 208680 bytes
 documentation/chapter5_word_qa/page-6.png          | Bin 0 -> 212377 bytes
 documentation/chapter5_word_qa/page-7.png          | Bin 0 -> 230779 bytes
 documentation/chapter5_word_qa/page-8.png          | Bin 0 -> 158806 bytes
 documentation/chapter5_word_qa/page-9.png          | Bin 0 -> 165077 bytes
 documentation/collect_chapter5_evidence.py         |  18 +++
 documentation/complete_final_draft.py              | 177 +++++++++++++++++++++
 documentation/evaluate_threshold_baseline.mjs      |  11 ++
 documentation/final_draft_evidence/backend.json    |  14 ++
 documentation/final_draft_evidence/frontend.json   |  12 ++
 .../final_draft_evidence/frontend_retest.txt       |  26 +++
 .../frontend_retest_unrestricted.txt               |   9 ++
 .../final_draft_evidence/live_summary.json         | 158 ++++++++++++++++++
 .../final_draft_evidence/test_kyc_experiment.json  |  11 ++
 .../final_draft_evidence/test_kyc_improvement.json |  11 ++
 documentation/final_draft_evidence/test_svm.json   |  11 ++
 .../final_draft_evidence/threshold_metrics.json    |  22 +++
 .../threshold_predictions.json                     |   1 +
 .../final_draft_qa/Chapter_5_Final_Revised.pdf     | Bin 0 -> 312419 bytes
 documentation/final_draft_qa/final-1.png           | Bin 0 -> 181778 bytes
 documentation/final_draft_qa/final-10.png          | Bin 0 -> 189348 bytes
 documentation/final_draft_qa/final-11.png          | Bin 0 -> 100444 bytes
 documentation/final_draft_qa/final-12.png          | Bin 0 -> 137343 bytes
 documentation/final_draft_qa/final-13.png          | Bin 0 -> 149364 bytes
 documentation/final_draft_qa/final-14.png          | Bin 0 -> 175314 bytes
 documentation/final_draft_qa/final-15.png          | Bin 0 -> 177081 bytes
 documentation/final_draft_qa/final-2.png           | Bin 0 -> 203470 bytes
 documentation/final_draft_qa/final-3.png           | Bin 0 -> 167855 bytes
 documentation/final_draft_qa/final-4.png           | Bin 0 -> 176466 bytes
 documentation/final_draft_qa/final-5.png           | Bin 0 -> 209614 bytes
 documentation/final_draft_qa/final-6.png           | Bin 0 -> 221748 bytes
 documentation/final_draft_qa/final-7.png           | Bin 0 -> 202337 bytes
 documentation/final_draft_qa/final-8.png           | Bin 0 -> 201122 bytes
 documentation/final_draft_qa/final-9.png           | Bin 0 -> 147218 bytes
 documentation/final_draft_qa/page-1.png            | Bin 0 -> 175296 bytes
 documentation/final_draft_qa/page-10.png           | Bin 0 -> 165101 bytes
 documentation/final_draft_qa/page-11.png           | Bin 0 -> 166348 bytes
 documentation/final_draft_qa/page-12.png           | Bin 0 -> 89191 bytes
 documentation/final_draft_qa/page-13.png           | Bin 0 -> 149505 bytes
 documentation/final_draft_qa/page-14.png           | Bin 0 -> 195570 bytes
 documentation/final_draft_qa/page-15.png           | Bin 0 -> 198036 bytes
 documentation/final_draft_qa/page-16.png           | Bin 0 -> 44438 bytes
 documentation/final_draft_qa/page-2.png            | Bin 0 -> 174255 bytes
 documentation/final_draft_qa/page-3.png            | Bin 0 -> 178683 bytes
 documentation/final_draft_qa/page-4.png            | Bin 0 -> 144637 bytes
 documentation/final_draft_qa/page-5.png            | Bin 0 -> 215554 bytes
 documentation/final_draft_qa/page-6.png            | Bin 0 -> 195343 bytes
 documentation/final_draft_qa/page-7.png            | Bin 0 -> 203621 bytes
 documentation/final_draft_qa/page-8.png            | Bin 0 -> 206994 bytes
 documentation/final_draft_qa/page-9.png            | Bin 0 -> 173957 bytes
 documentation/revise_chapter5.py                   |  58 +++++++
 documentation/summarize_live_exports.py            |  11 ++
 74 files changed, 574 insertions(+), 8 deletions(-)
8e00a21 | 2026-10-26 | Merge branch 'main' of https://github.com/kar-iuki/Intelligent-Agent-Identity-Verification-System
3a83f56 | 2026-10-30 | final updates

 README.md                                          |  20 ++
 backend/.env.hosted.example                        |   6 +
 backend/src/config/passkeyConfig.js                |   8 +-
 backend/src/controllers/agentController.js         |  16 +-
 backend/src/services/documentCapturePolicy.js      |  19 ++
 backend/tests/documentCapturePolicy.test.js        |  58 ++++
 backend/tests/passkeys.test.js                     |  12 +
 documentation/Chapter_4_Revised.docx               | Bin 0 -> 4039026 bytes
 documentation/Chapter_4_Revised.pdf                | Bin 0 -> 2801910 bytes
 documentation/Chapter_4_Wireframes.zip             | Bin 0 -> 2247025 bytes
 documentation/Chapter_5_Aligned_Chapter_4.docx     | Bin 0 -> 83168 bytes
 documentation/Chapter_5_Hosted_Deployment.docx     | Bin 0 -> 77084 bytes
 documentation/Chapter_5_Hosted_Deployment.pdf      | Bin 0 -> 323078 bytes
 ...onclusions_Recommendations_and_Future_Work.docx | Bin 0 -> 41804 bytes
 ..._Conclusions_Recommendations_and_Future_Work.md |  75 +++++
 documentation/align_chapter5_amendments.py         | 129 +++++++++
 .../aligned_qa/Chapter_5_Aligned_Chapter_4.pdf     | Bin 0 -> 448334 bytes
 documentation/aligned_qa/backup_confirmed.pdf      | Bin 0 -> 448182 bytes
 .../aligned_qa/before_backup_confirmation.docx     | Bin 0 -> 83014 bytes
 documentation/aligned_qa/check-1.png               | Bin 0 -> 610671 bytes
 documentation/aligned_qa/check-2.png               | Bin 0 -> 644708 bytes
 documentation/aligned_qa/check-3.png               | Bin 0 -> 607306 bytes
 documentation/aligned_qa/check-4.png               | Bin 0 -> 533162 bytes
 documentation/aligned_qa/check-5.png               | Bin 0 -> 505728 bytes
 documentation/aligned_qa/check-6.png               | Bin 0 -> 54631 bytes
 documentation/aligned_qa/final-1.png               | Bin 0 -> 127343 bytes
 documentation/aligned_qa/final-10.png              | Bin 0 -> 131573 bytes
 documentation/aligned_qa/final-11.png              | Bin 0 -> 121512 bytes
 documentation/aligned_qa/final-12.png              | Bin 0 -> 123381 bytes
 documentation/aligned_qa/final-13.png              | Bin 0 -> 160469 bytes
 documentation/aligned_qa/final-14.png              | Bin 0 -> 122901 bytes
 documentation/aligned_qa/final-15.png              | Bin 0 -> 82388 bytes
 documentation/aligned_qa/final-16.png              | Bin 0 -> 102508 bytes
 documentation/aligned_qa/final-17.png              | Bin 0 -> 133442 bytes
 documentation/aligned_qa/final-18.png              | Bin 0 -> 133144 bytes
 documentation/aligned_qa/final-19.png              | Bin 0 -> 125487 bytes
 documentation/aligned_qa/final-2.png               | Bin 0 -> 132718 bytes
 documentation/aligned_qa/final-20.png              | Bin 0 -> 43164 bytes
 documentation/aligned_qa/final-3.png               | Bin 0 -> 145039 bytes
 documentation/aligned_qa/final-4.png               | Bin 0 -> 124360 bytes
 documentation/aligned_qa/final-5.png               | Bin 0 -> 112595 bytes
 documentation/aligned_qa/final-6.png               | Bin 0 -> 158785 bytes
 documentation/aligned_qa/final-7.png               | Bin 0 -> 143174 bytes
 documentation/aligned_qa/final-8.png               | Bin 0 -> 142834 bytes
 documentation/aligned_qa/final-9.png               | Bin 0 -> 134112 bytes
 documentation/aligned_qa/page-1.png                | Bin 0 -> 164496 bytes
 documentation/aligned_qa/page-10.png               | Bin 0 -> 167690 bytes
 documentation/aligned_qa/page-11.png               | Bin 0 -> 156460 bytes
 documentation/aligned_qa/page-12.png               | Bin 0 -> 159707 bytes
 documentation/aligned_qa/page-13.png               | Bin 0 -> 201601 bytes
 documentation/aligned_qa/page-14.png               | Bin 0 -> 151716 bytes
 documentation/aligned_qa/page-15.png               | Bin 0 -> 74605 bytes
 documentation/aligned_qa/page-16.png               | Bin 0 -> 112587 bytes
 documentation/aligned_qa/page-17.png               | Bin 0 -> 124957 bytes
 documentation/aligned_qa/page-18.png               | Bin 0 -> 122002 bytes
 documentation/aligned_qa/page-19.png               | Bin 0 -> 161097 bytes
 documentation/aligned_qa/page-2.png                | Bin 0 -> 168599 bytes
 documentation/aligned_qa/page-20.png               | Bin 0 -> 183619 bytes
 documentation/aligned_qa/page-21.png               | Bin 0 -> 22887 bytes
 documentation/aligned_qa/page-3.png                | Bin 0 -> 186899 bytes
 documentation/aligned_qa/page-4.png                | Bin 0 -> 159156 bytes
 documentation/aligned_qa/page-5.png                | Bin 0 -> 148831 bytes
 documentation/aligned_qa/page-6.png                | Bin 0 -> 204638 bytes
 documentation/aligned_qa/page-7.png                | Bin 0 -> 183365 bytes
 documentation/aligned_qa/page-8.png                | Bin 0 -> 183444 bytes
 documentation/aligned_qa/page-9.png                | Bin 0 -> 170306 bytes
 documentation/aligned_qa/updated-1.png             | Bin 0 -> 127066 bytes
 documentation/aligned_qa/updated-10.png            | Bin 0 -> 135562 bytes
 documentation/aligned_qa/updated-11.png            | Bin 0 -> 120485 bytes
 documentation/aligned_qa/updated-12.png            | Bin 0 -> 116845 bytes
 documentation/aligned_qa/updated-13.png            | Bin 0 -> 160407 bytes
 documentation/aligned_qa/updated-14.png            | Bin 0 -> 128008 bytes
 documentation/aligned_qa/updated-15.png            | Bin 0 -> 67247 bytes
 documentation/aligned_qa/updated-16.png            | Bin 0 -> 98436 bytes
 documentation/aligned_qa/updated-17.png            | Bin 0 -> 107624 bytes
 documentation/aligned_qa/updated-18.png            | Bin 0 -> 114449 bytes
 documentation/aligned_qa/updated-19.png            | Bin 0 -> 155656 bytes
 documentation/aligned_qa/updated-2.png             | Bin 0 -> 130809 bytes
 documentation/aligned_qa/updated-20.png            | Bin 0 -> 56659 bytes
 documentation/aligned_qa/updated-3.png             | Bin 0 -> 147629 bytes
 documentation/aligned_qa/updated-4.png             | Bin 0 -> 122570 bytes
 documentation/aligned_qa/updated-5.png             | Bin 0 -> 100241 bytes
 documentation/aligned_qa/updated-6.png             | Bin 0 -> 155833 bytes
 documentation/aligned_qa/updated-7.png             | Bin 0 -> 143615 bytes
 documentation/aligned_qa/updated-8.png             | Bin 0 -> 139411 bytes
 documentation/aligned_qa/updated-9.png             | Bin 0 -> 140875 bytes
 .../Chapter_4_Revised.docx                         | Bin 0 -> 4039262 bytes
 .../Chapter_4_Revised.pdf                          | Bin 0 -> 2799941 bytes
 .../Chapter_4_Wireframes.zip                       | Bin 0 -> 2247095 bytes
 .../build_chapter4_document.py                     | 284 +++++++++++++++++++
 .../chapter4_content.py                            | 253 +++++++++++++++++
 .../before_final_hashes.json                       | 138 +++++++++
 .../Chapter_4_Revised.docx                         | Bin 0 -> 4039948 bytes
 .../Chapter_4_Revised.pdf                          | Bin 0 -> 2805454 bytes
 .../Chapter_5_Hosted_Deployment.docx               | Bin 0 -> 76601 bytes
 .../build_chapter4_document.py                     | 296 +++++++++++++++++++
 .../before_final_writing_fixes/chapter4_content.py | 253 +++++++++++++++++
 .../chapter4_revision_work/chapter4_text.txt       | 313 +++++++++++++++++++++
 .../chapter5_final_render/page-1.png               | Bin 0 -> 293320 bytes
 .../chapter5_final_render/page-10.png              | Bin 0 -> 250866 bytes
 .../chapter5_final_render/page-11.png              | Bin 0 -> 275391 bytes
 .../chapter5_final_render/page-12.png              | Bin 0 -> 113294 bytes
 .../chapter5_final_render/page-13.png              | Bin 0 -> 192356 bytes
 .../chapter5_final_render/page-14.png              | Bin 0 -> 207358 bytes
 .../chapter5_final_render/page-15.png              | Bin 0 -> 214830 bytes
 .../chapter5_final_render/page-16.png              | Bin 0 -> 298570 bytes
 .../chapter5_final_render/page-17.png              | Bin 0 -> 154383 bytes
 .../chapter5_final_render/page-2.png               | Bin 0 -> 262653 bytes
 .../chapter5_final_render/page-3.png               | Bin 0 -> 297686 bytes
 .../chapter5_final_render/page-4.png               | Bin 0 -> 228688 bytes
 .../chapter5_final_render/page-5.png               | Bin 0 -> 312499 bytes
 .../chapter5_final_render/page-6.png               | Bin 0 -> 287022 bytes
 .../chapter5_final_render/page-7.png               | Bin 0 -> 338737 bytes
 .../chapter5_final_render/page-8.png               | Bin 0 -> 296763 bytes
 .../chapter5_final_render/page-9.png               | Bin 0 -> 272890 bytes
 .../chapter5_final_render/page_inventory.json      |  87 ++++++
 .../chapter4_revision_work/final_render/page-1.png | Bin 0 -> 231330 bytes
 .../final_render/page-10.png                       | Bin 0 -> 294832 bytes
 .../final_render/page-11.png                       | Bin 0 -> 301142 bytes
 .../final_render/page-12.png                       | Bin 0 -> 156511 bytes
 .../final_render/page-13.png                       | Bin 0 -> 265907 bytes
 .../final_render/page-14.png                       | Bin 0 -> 232483 bytes
 .../final_render/page-15.png                       | Bin 0 -> 162693 bytes
 .../final_render/page-16.png                       | Bin 0 -> 207255 bytes
 .../final_render/page-17.png                       | Bin 0 -> 234094 bytes
 .../final_render/page-18.png                       | Bin 0 -> 197752 bytes
 .../final_render/page-19.png                       | Bin 0 -> 186130 bytes
 .../chapter4_revision_work/final_render/page-2.png | Bin 0 -> 150310 bytes
 .../final_render/page-20.png                       | Bin 0 -> 231391 bytes
 .../final_render/page-21.png                       | Bin 0 -> 153186 bytes
 .../final_render/page-22.png                       | Bin 0 -> 181261 bytes
 .../final_render/page-23.png                       | Bin 0 -> 159972 bytes
 .../final_render/page-24.png                       | Bin 0 -> 194970 bytes
 .../final_render/page-25.png                       | Bin 0 -> 177575 bytes
 .../final_render/page-26.png                       | Bin 0 -> 193117 bytes
 .../final_render/page-27.png                       | Bin 0 -> 155796 bytes
 .../final_render/page-28.png                       | Bin 0 -> 166966 bytes
 .../final_render/page-29.png                       | Bin 0 -> 172005 bytes
 .../chapter4_revision_work/final_render/page-3.png | Bin 0 -> 247870 bytes
 .../final_render/page-30.png                       | Bin 0 -> 155551 bytes
 .../final_render/page-31.png                       | Bin 0 -> 232661 bytes
 .../final_render/page-32.png                       | Bin 0 -> 207134 bytes
 .../final_render/page-33.png                       | Bin 0 -> 232966 bytes
 .../final_render/page-34.png                       | Bin 0 -> 84533 bytes
 .../chapter4_revision_work/final_render/page-4.png | Bin 0 -> 253108 bytes
 .../chapter4_revision_work/final_render/page-5.png | Bin 0 -> 219760 bytes
 .../chapter4_revision_work/final_render/page-6.png | Bin 0 -> 250936 bytes
 .../chapter4_revision_work/final_render/page-7.png | Bin 0 -> 245877 bytes
 .../chapter4_revision_work/final_render/page-8.png | Bin 0 -> 259366 bytes
 .../chapter4_revision_work/final_render/page-9.png | Bin 0 -> 221036 bytes
 .../final_render/page_inventory.json               | 172 +++++++++++
 .../original_figures/figure_4_01.png               | Bin 0 -> 366012 bytes
 .../original_figures/figure_4_02.png               | Bin 0 -> 443726 bytes
 .../original_figures/figure_4_03.png               | Bin 0 -> 165682 bytes
 .../original_figures/figure_4_04.png               | Bin 0 -> 298995 bytes
 .../original_figures/figure_4_05.png               | Bin 0 -> 308921 bytes
 .../original_figures/figure_4_06.png               | Bin 0 -> 231293 bytes
 .../chapter4_revision_work/render/overview-1.png   | Bin 0 -> 533916 bytes
 .../chapter4_revision_work/render/overview-2.png   | Bin 0 -> 546571 bytes
 .../chapter4_revision_work/render/overview-3.png   | Bin 0 -> 349571 bytes
 .../chapter4_revision_work/render/overview-4.png   | Bin 0 -> 359235 bytes
 .../chapter4_revision_work/render/overview-5.png   | Bin 0 -> 313624 bytes
 .../chapter4_revision_work/render/overview-6.png   | Bin 0 -> 306311 bytes
 .../chapter4_revision_work/render/page-1.png       | Bin 0 -> 246654 bytes
 .../chapter4_revision_work/render/page-10.png      | Bin 0 -> 306930 bytes
 .../chapter4_revision_work/render/page-11.png      | Bin 0 -> 305619 bytes
 .../chapter4_revision_work/render/page-12.png      | Bin 0 -> 156057 bytes
 .../chapter4_revision_work/render/page-13.png      | Bin 0 -> 268029 bytes
 .../chapter4_revision_work/render/page-14.png      | Bin 0 -> 231780 bytes
 .../chapter4_revision_work/render/page-15.png      | Bin 0 -> 163327 bytes
 .../chapter4_revision_work/render/page-16.png      | Bin 0 -> 206776 bytes
 .../chapter4_revision_work/render/page-17.png      | Bin 0 -> 236704 bytes
 .../chapter4_revision_work/render/page-18.png      | Bin 0 -> 197599 bytes
 .../chapter4_revision_work/render/page-19.png      | Bin 0 -> 186363 bytes
 .../chapter4_revision_work/render/page-2.png       | Bin 0 -> 278280 bytes
 .../chapter4_revision_work/render/page-20.png      | Bin 0 -> 231585 bytes
 .../chapter4_revision_work/render/page-21.png      | Bin 0 -> 153529 bytes
 .../chapter4_revision_work/render/page-22.png      | Bin 0 -> 181115 bytes
 .../chapter4_revision_work/render/page-23.png      | Bin 0 -> 160116 bytes
 .../chapter4_revision_work/render/page-24.png      | Bin 0 -> 194745 bytes
 .../chapter4_revision_work/render/page-25.png      | Bin 0 -> 178306 bytes
 .../chapter4_revision_work/render/page-26.png      | Bin 0 -> 191671 bytes
 .../chapter4_revision_work/render/page-27.png      | Bin 0 -> 155797 bytes
 .../chapter4_revision_work/render/page-28.png      | Bin 0 -> 166532 bytes
 .../chapter4_revision_work/render/page-29.png      | Bin 0 -> 175011 bytes
 .../chapter4_revision_work/render/page-3.png       | Bin 0 -> 247547 bytes
 .../chapter4_revision_work/render/page-30.png      | Bin 0 -> 156099 bytes
 .../chapter4_revision_work/render/page-31.png      | Bin 0 -> 232979 bytes
 .../chapter4_revision_work/render/page-32.png      | Bin 0 -> 206502 bytes
 .../chapter4_revision_work/render/page-33.png      | Bin 0 -> 224305 bytes
 .../chapter4_revision_work/render/page-34.png      | Bin 0 -> 174381 bytes
 .../chapter4_revision_work/render/page-4.png       | Bin 0 -> 253169 bytes
 .../chapter4_revision_work/render/page-5.png       | Bin 0 -> 220726 bytes
 .../chapter4_revision_work/render/page-6.png       | Bin 0 -> 250116 bytes
 .../chapter4_revision_work/render/page-7.png       | Bin 0 -> 247845 bytes
 .../chapter4_revision_work/render/page-8.png       | Bin 0 -> 264502 bytes
 .../chapter4_revision_work/render/page-9.png       | Bin 0 -> 220763 bytes
 .../render/page_inventory.json                     | 274 ++++++++++++++++++
 documentation/chapter4_wireframes/README.md        |  47 ++++
 .../figure_4_07_authentication.png                 | Bin 0 -> 234665 bytes
 .../figure_4_07_authentication.svg                 |  43 +++
 .../figure_4_08_personal_details.png               | Bin 0 -> 246823 bytes
 .../figure_4_08_personal_details.svg               |  47 ++++
 .../figure_4_09_document_capture.png               | Bin 0 -> 297658 bytes
 .../figure_4_09_document_capture.svg               |  56 ++++
 .../figure_4_10_live_selfie.png                    | Bin 0 -> 286937 bytes
 .../figure_4_10_live_selfie.svg                    |  45 +++
 .../figure_4_11_verification_states.png            | Bin 0 -> 337675 bytes
 .../figure_4_11_verification_states.svg            |  49 ++++
 .../figure_4_12_admin_directory.png                | Bin 0 -> 294139 bytes
 .../figure_4_12_admin_directory.svg                |  65 +++++
 .../figure_4_13_case_review.png                    | Bin 0 -> 317517 bytes
 .../figure_4_13_case_review.svg                    |  51 ++++
 .../figure_4_14_audit_export.png                   | Bin 0 -> 276554 bytes
 .../figure_4_14_audit_export.svg                   |  64 +++++
 .../figure_4_15_passkey_management.png             | Bin 0 -> 285531 bytes
 .../figure_4_15_passkey_management.svg             |  39 +++
 .../figure_4_16_model_evaluation.png               | Bin 0 -> 305548 bytes
 .../figure_4_16_model_evaluation.svg               |  71 +++++
 documentation/chapter4_wireframes/manifest.json    |  16 ++
 documentation/chapter6_work/Chapter_4_Revised.txt  | 313 +++++++++++++++++++++
 .../chapter6_work/Chapter_5_Aligned_Chapter_4.txt  | 266 +++++++++++++++++
 documentation/chapter6_work/build_chapter6.py      |  50 ++++
 documentation/chapter6_work/render/Chapter_6.pdf   | Bin 0 -> 120512 bytes
 documentation/chapter6_work/render/approved-1.png  | Bin 0 -> 273969 bytes
 documentation/chapter6_work/render/approved-2.png  | Bin 0 -> 333351 bytes
 documentation/chapter6_work/render/approved-3.png  | Bin 0 -> 297599 bytes
 documentation/chapter6_work/render/approved-4.png  | Bin 0 -> 278705 bytes
 documentation/chapter6_work/render/final-1.png     | Bin 0 -> 342229 bytes
 documentation/chapter6_work/render/final-2.png     | Bin 0 -> 379444 bytes
 documentation/chapter6_work/render/final-3.png     | Bin 0 -> 317263 bytes
 documentation/chapter6_work/render/final-4.png     | Bin 0 -> 317065 bytes
 documentation/chapter6_work/render/page-1.png      | Bin 0 -> 312685 bytes
 documentation/chapter6_work/render/page-2.png      | Bin 0 -> 378808 bytes
 documentation/chapter6_work/render/page-3.png      | Bin 0 -> 364839 bytes
 documentation/chapter6_work/render/page-4.png      | Bin 0 -> 294886 bytes
 documentation/deployment_checks_2026-10-27.json    |  21 ++
 .../hosted_qa/Chapter_5_Hosted_Deployment.pdf      | Bin 0 -> 318273 bytes
 documentation/hosted_qa/page-1.png                 | Bin 0 -> 151431 bytes
 documentation/hosted_qa/page-10.png                | Bin 0 -> 133971 bytes
 documentation/hosted_qa/page-11.png                | Bin 0 -> 138331 bytes
 documentation/hosted_qa/page-12.png                | Bin 0 -> 73244 bytes
 documentation/hosted_qa/page-13.png                | Bin 0 -> 100768 bytes
 documentation/hosted_qa/page-14.png                | Bin 0 -> 118197 bytes
 documentation/hosted_qa/page-15.png                | Bin 0 -> 128854 bytes
 documentation/hosted_qa/page-16.png                | Bin 0 -> 125437 bytes
 documentation/hosted_qa/page-2.png                 | Bin 0 -> 136951 bytes
 documentation/hosted_qa/page-3.png                 | Bin 0 -> 139088 bytes
 documentation/hosted_qa/page-4.png                 | Bin 0 -> 115038 bytes
 documentation/hosted_qa/page-5.png                 | Bin 0 -> 155782 bytes
 documentation/hosted_qa/page-6.png                 | Bin 0 -> 144286 bytes
 documentation/hosted_qa/page-7.png                 | Bin 0 -> 159259 bytes
 documentation/hosted_qa/page-8.png                 | Bin 0 -> 144409 bytes
 documentation/hosted_qa/page-9.png                 | Bin 0 -> 141140 bytes
 documentation/update_hosted_chapter5.py            |  58 ++++
 frontend/src/components/DocumentCaptureStep.vue    |  85 ++++--
 frontend/src/components/LiveSelfieChallenge.vue    |  16 +-
 frontend/src/services/agentService.js              |   3 +
 frontend/src/services/passkeyService.js            |   2 +-
 frontend/src/utils/documentCaptureSource.js        |  12 +
 frontend/src/views/AgentDashboard.vue              |  12 +-
 frontend/tests/e2e/documentCapture.spec.js         |  89 ++++++
 frontend/tests/unit/documentCapture.test.js        |  69 +++++
 frontend/tests/unit/passkeyCeremony.test.js        |   2 +-
 264 files changed, 3961 insertions(+), 43 deletions(-)
7898e9e | 2026-10-30 | Remove blink twice and open your eyes

 frontend/src/components/LiveSelfieChallenge.vue | 40 ++-----------------------
 1 file changed, 2 insertions(+), 38 deletions(-)
2382407 | 2026-10-31 | landing page

 frontend/index.html                   |   6 +-
 frontend/public/verity.svg            |   1 +
 frontend/src/App.vue                  |   3 +-
 frontend/src/components/AuthShell.vue |   2 +-
 frontend/src/landing.css              |  36 ++++++++++
 frontend/src/router/index.js          |  15 +++-
 frontend/src/views/HomeView.vue       | 129 +++++++++++++++++++++++++++-------
 frontend/tests/e2e/landing.spec.js    |  52 ++++++++++++++
 8 files changed, 213 insertions(+), 31 deletions(-)
7bd4632 | 2026-10-31 | frontend updates

 frontend/COLORS.md                              |  25 +++
 frontend/src/components/CameraCapture.vue       |  18 +--
 frontend/src/components/DocumentCaptureStep.vue |  34 ++--
 frontend/src/components/ImageUpload.vue         |  28 ++--
 frontend/src/components/Lightbox.vue            |   6 +-
 frontend/src/components/LiveSelfieChallenge.vue |  46 +++---
 frontend/src/components/PasskeyButton.vue       |   8 +-
 frontend/src/components/PasskeyDialog.vue       |   8 +-
 frontend/src/components/ScoreBar.vue            |  27 +++-
 frontend/src/landing.css                        |   2 +-
 frontend/src/main.js                            |   1 +
 frontend/src/style.css                          |   4 +-
 frontend/src/theme.css                          |  82 ++++++++++
 frontend/src/views/AdminDashboard.vue           | 164 ++++++++++---------
 frontend/src/views/AdminModelEvaluation.vue     |  71 ++++----
 frontend/src/views/AgentAuditLog.vue            |  42 ++---
 frontend/src/views/AgentDashboard.vue           | 166 +++++++++----------
 frontend/src/views/AgentPlatformPage.vue        |  22 +--
 frontend/src/views/CheckEmailPage.vue           |  30 ++--
 frontend/src/views/CompleteProfilePage.vue      |  28 ++--
 frontend/src/views/ForgotPasswordPage.vue       |  10 +-
 frontend/src/views/LoginPage.vue                |  60 +++----
 frontend/src/views/ManagePasskeysPage.vue       |  14 +-
 frontend/src/views/PendingVerificationPage.vue  |  20 +--
 frontend/src/views/RegisterPage.vue             |  30 ++--
 frontend/src/views/ResetPasswordPage.vue        |   8 +-
 frontend/src/workspace.css                      | 206 ++++++++++--------------
 frontend/tests/e2e/theme.spec.js                |  67 ++++++++
 28 files changed, 686 insertions(+), 541 deletions(-)

```


---

## File inventory

- README.md
- package.json
- package-lock.json
- ngrok.yml
- database/storage_agent_documents.sql
- database/schema.sql
- database/rls_policies.sql
- database/passkeys.sql
- database/audit_logs_nullable_request.sql
- database/audit_logging_module10.sql
- database/agents_date_of_birth.sql
- database/access_control_module8.sql
- documentation/update_hosted_chapter5.py
- documentation/summarize_live_exports.py
- documentation/revise_chapter5.py
- documentation/Chapter_5_Hosted_Deployment.pdf
- documentation/align_chapter5_amendments.py
- documentation/Chapter_5_Hosted_Deployment.docx
- documentation/Chapter_5_Final_Revised.docx
- documentation/Chapter_5_Aligned_Chapter_4.docx
- documentation/build_chapter5.py
- documentation/Chapter_5.docx
- documentation/Chapter_4_Wireframes.zip
- documentation/Chapter_4_Revised.pdf
- documentation/Chapter_4_Revised.docx
- backend/tests/documentCapturePolicy.test.js
- backend/tests/passkeys.test.js
- backend/tests/passkeyRoutes.test.js
- backend/tests/passkeyDatabase.test.js
- backend/tests/kycDecision.test.js
- backend/tests/documentRetention.test.js
- backend/tests/helpers/passkeyMemoryDb.js
- documentation/complete_final_draft.py
- documentation/collect_chapter5_evidence.py
- documentation/Chapter_6_Conclusions_Recommendations_and_Future_Work.md
- documentation/Chapter_6_Conclusions_Recommendations_and_Future_Work.docx
- documentation/Chapter_5_System_Implementation_Testing_and_Evaluation.md
- documentation/Chapter_5_System_Implementation_Testing_and_Evaluation.docx
- documentation/export_chapter5.py
- documentation/evaluate_threshold_baseline.mjs
- documentation/deployment_checks_2026-10-27.json
- frontend/vitest.config.js
- frontend/vite.config.js
- frontend/vercel.json
- frontend/package.json
- frontend/package-lock.json
- frontend/index.html
- frontend/COLORS.md
- documentation/hosted_qa/page-9.png
- documentation/chapter4_wireframes/README.md
- documentation/hosted_qa/page-8.png
- documentation/final_draft_evidence/frontend_retest_unrestricted.txt
- documentation/hosted_qa/page-7.png
- documentation/hosted_qa/page-6.png
- documentation/hosted_qa/page-5.png
- documentation/hosted_qa/page-4.png
- documentation/hosted_qa/page-3.png
- documentation/hosted_qa/page-2.png
- documentation/hosted_qa/page-16.png
- documentation/final_draft_evidence/threshold_predictions.json
- documentation/hosted_qa/page-15.png
- documentation/hosted_qa/page-14.png
- documentation/hosted_qa/page-13.png
- documentation/hosted_qa/page-12.png
- documentation/hosted_qa/page-11.png
- documentation/final_draft_evidence/threshold_metrics.json
- documentation/hosted_qa/page-10.png
- documentation/hosted_qa/page-1.png
- documentation/hosted_qa/Chapter_5_Hosted_Deployment.pdf
- documentation/final_draft_evidence/test_svm.json
- documentation/final_draft_evidence/test_kyc_improvement.json
- documentation/final_draft_evidence/test_kyc_experiment.json
- documentation/final_draft_evidence/live_summary.json
- documentation/chapter6_work/Chapter_4_Revised.txt
- documentation/chapter6_work/build_chapter6.py
- documentation/chapter6_work/Chapter_5_Aligned_Chapter_4.txt
- documentation/chapter4_wireframes/manifest.json
- documentation/chapter4_wireframes/figure_4_16_model_evaluation.svg
- documentation/chapter4_wireframes/figure_4_16_model_evaluation.png
- documentation/chapter4_wireframes/figure_4_15_passkey_management.svg
- documentation/chapter4_wireframes/figure_4_15_passkey_management.png
- documentation/chapter4_wireframes/figure_4_14_audit_export.svg
- documentation/chapter4_wireframes/figure_4_14_audit_export.png
- documentation/chapter4_wireframes/figure_4_13_case_review.svg
- documentation/chapter4_wireframes/figure_4_13_case_review.png
- documentation/chapter4_wireframes/figure_4_12_admin_directory.svg
- documentation/chapter4_wireframes/figure_4_12_admin_directory.png
- documentation/chapter4_wireframes/figure_4_11_verification_states.svg
- documentation/chapter4_wireframes/figure_4_11_verification_states.png
- documentation/chapter4_wireframes/figure_4_10_live_selfie.svg
- documentation/chapter4_wireframes/figure_4_10_live_selfie.png
- documentation/chapter4_wireframes/figure_4_09_document_capture.svg
- documentation/chapter4_wireframes/figure_4_09_document_capture.png
- documentation/chapter4_wireframes/figure_4_08_personal_details.svg
- documentation/chapter4_wireframes/figure_4_08_personal_details.png
- documentation/chapter4_wireframes/figure_4_07_authentication.svg
- documentation/chapter4_wireframes/figure_4_07_authentication.png
- frontend/playwright.config.js
- documentation/final_draft_evidence/frontend_retest.txt
- documentation/final_draft_evidence/frontend.json
- documentation/final_draft_evidence/backend.json
- backend/package.json
- backend/package-lock.json
- backend/server.js
- documentation/chapter5_word_qa/final-11.png
- documentation/chapter5_word_qa/final-10.png
- documentation/chapter5_word_qa/final-1.png
- documentation/chapter5_word_qa/Chapter_5.pdf
- documentation/chapter5_word_qa/final-3.png
- documentation/chapter5_word_qa/final-2.png
- documentation/chapter5_word_qa/final-4.png
- backend/src/utils/auditTrailVerifier.js
- backend/src/utils/auditLogger.js
- frontend/tests/unit/passkeys.test.js
- frontend/tests/unit/passkeyCeremony.test.js
- frontend/tests/unit/documentCapture.test.js
- backend/src/config/passkeyConfig.js
- backend/src/config/fraudConfig.js
- backend/src/config/blockedEmailDomains.js
- documentation/chapter6_work/render/page-4.png
- documentation/chapter5_word_qa/page-1.png
- documentation/chapter6_work/render/page-3.png
- documentation/chapter5_word_qa/final-9.png
- documentation/chapter6_work/render/page-2.png
- documentation/chapter6_work/render/page-1.png
- documentation/chapter6_work/render/final-4.png
- documentation/chapter6_work/render/final-3.png
- documentation/chapter6_work/render/final-2.png
- documentation/chapter6_work/render/final-1.png
- documentation/chapter6_work/render/Chapter_6.pdf
- documentation/chapter6_work/render/approved-4.png
- documentation/chapter6_work/render/approved-3.png
- documentation/chapter6_work/render/approved-2.png
- documentation/chapter6_work/render/approved-1.png
- backend/src/utils/runAuditTrailCheck.js
- backend/src/utils/captcha.js
- backend/src/utils/auditWindow.js
- documentation/chapter5_word_qa/final-8.png
- backend/src/utils/supabaseAnon.js
- documentation/chapter5_word_qa/final-7.png
- backend/src/utils/supabaseClient.js
- documentation/chapter5_word_qa/final-6.png
- documentation/chapter5_word_qa/final-5.png
- documentation/chapter4_revision_work/chapter4_text.txt
- documentation/chapter5_word_qa/page-2.png
- documentation/chapter5_word_qa/page-11.png
- documentation/chapter5_word_qa/page-10.png
- documentation/chapter5_word_qa/page-3.png
- documentation/chapter5_word_qa/page-4.png
- backend/src/utils/validateDateOfBirth.js
- documentation/chapter5_word_qa/page-9.png
- documentation/chapter5_word_qa/page-8.png
- documentation/chapter5_word_qa/page-7.png
- documentation/chapter5_word_qa/page-6.png
- documentation/chapter5_word_qa/page-5.png
- documentation/chapter4_revision_work/before_final_hashes.json
- documentation/aligned_qa/before_backup_confirmation.docx
- documentation/aligned_qa/backup_confirmed.pdf
- documentation/aligned_qa/Chapter_5_Aligned_Chapter_4.pdf
- frontend/public/verity.svg
- frontend/tests/e2e/workspace.spec.js
- frontend/tests/e2e/theme.spec.js
- frontend/tests/e2e/server.mjs
- frontend/tests/e2e/passkeys.spec.js
- frontend/tests/e2e/landing.spec.js
- frontend/tests/e2e/documentCapture.spec.js
- backend/src/services/documentRetentionService.js
- backend/src/services/documentCapturePolicy.js
- backend/src/services/accessControlService.js
- backend/src/services/verificationService.js
- backend/src/services/verificationFeedbackService.js
- backend/src/services/strikeService.js
- backend/src/services/realtimeService.js
- backend/src/services/passkeyService.js
- documentation/final_draft_qa/final-6.png
- documentation/final_draft_qa/final-5.png
- documentation/final_draft_qa/final-4.png
- documentation/final_draft_qa/final-3.png
- documentation/final_draft_qa/final-2.png
- documentation/final_draft_qa/final-15.png
- documentation/final_draft_qa/final-14.png
- documentation/final_draft_qa/final-13.png
- documentation/final_draft_qa/final-12.png
- documentation/final_draft_qa/final-11.png
- documentation/final_draft_qa/final-10.png
- documentation/final_draft_qa/final-1.png
- documentation/final_draft_qa/Chapter_5_Final_Revised.pdf
- documentation/final_draft_qa/page-12.png
- documentation/final_draft_qa/page-11.png
- documentation/final_draft_qa/page-10.png
- documentation/final_draft_qa/page-1.png
- documentation/final_draft_qa/final-9.png
- documentation/final_draft_qa/final-8.png
- documentation/final_draft_qa/final-7.png
- documentation/final_draft_qa/page-15.png
- documentation/final_draft_qa/page-14.png
- documentation/final_draft_qa/page-13.png
- documentation/final_draft_qa/page-2.png
- documentation/final_draft_qa/page-16.png
- documentation/final_draft_qa/page-3.png
- documentation/aligned_qa/final-14.png
- documentation/aligned_qa/final-13.png
- documentation/aligned_qa/final-12.png
- documentation/aligned_qa/final-11.png
- documentation/aligned_qa/final-10.png
- documentation/aligned_qa/final-1.png
- documentation/aligned_qa/check-6.png
- documentation/aligned_qa/check-5.png
- documentation/aligned_qa/check-4.png
- documentation/aligned_qa/check-3.png
- documentation/aligned_qa/check-2.png
- documentation/aligned_qa/check-1.png
- documentation/aligned_qa/final-2.png
- documentation/aligned_qa/final-19.png
- documentation/aligned_qa/final-18.png
- documentation/aligned_qa/final-17.png
- documentation/aligned_qa/final-16.png
- documentation/aligned_qa/final-15.png
- documentation/aligned_qa/final-4.png
- documentation/aligned_qa/final-3.png
- documentation/aligned_qa/final-20.png
- documentation/aligned_qa/final-6.png
- documentation/aligned_qa/final-5.png
- documentation/aligned_qa/final-7.png
- frontend/src/workspace.css
- documentation/chapter4_revision_work/before_final_writing_fixes/Chapter_5_Hosted_Deployment.docx
- documentation/chapter4_revision_work/before_final_writing_fixes/Chapter_4_Revised.pdf
- documentation/chapter4_revision_work/before_final_writing_fixes/Chapter_4_Revised.docx
- documentation/chapter4_revision_work/before_final_writing_fixes/chapter4_content.py
- documentation/chapter4_revision_work/before_final_writing_fixes/build_chapter4_document.py
- documentation/final_draft_qa/page-6.png
- documentation/final_draft_qa/page-5.png
- documentation/final_draft_qa/page-4.png
- documentation/final_draft_qa/page-7.png
- documentation/final_draft_qa/page-8.png
- documentation/final_draft_qa/page-9.png
- documentation/aligned_qa/page-1.png
- documentation/aligned_qa/final-9.png
- documentation/aligned_qa/final-8.png
- documentation/aligned_qa/page-11.png
- documentation/aligned_qa/page-10.png
- documentation/aligned_qa/page-12.png
- backend/src/middleware/uploadMiddleware.js
- backend/src/middleware/roleMiddleware.js
- backend/src/middleware/requestLogger.js
- backend/src/middleware/fraudGuardrailsMiddleware.js
- backend/src/middleware/authMiddleware.js
- frontend/src/router/index.js
- frontend/src/main.js
- frontend/src/landing.css
- backend/src/routes/verificationRoutes.js
- backend/src/routes/passkeyRoutes.js
- backend/src/routes/authRoutes.js
- backend/src/routes/agentRoutes.js
- backend/src/routes/adminRoutes.js
- ai-service/app.py
- ai-service/backend/package-lock.json
- frontend/src/App.vue
- documentation/aligned_qa/updated-9.png
- documentation/aligned_qa/updated-8.png
- documentation/aligned_qa/updated-7.png
- documentation/aligned_qa/updated-6.png
- documentation/aligned_qa/updated-5.png
- documentation/aligned_qa/updated-4.png
- documentation/aligned_qa/updated-3.png
- documentation/aligned_qa/updated-20.png
- documentation/aligned_qa/updated-2.png
- documentation/aligned_qa/updated-19.png
- documentation/aligned_qa/updated-18.png
- documentation/aligned_qa/updated-17.png
- documentation/aligned_qa/updated-16.png
- documentation/aligned_qa/updated-15.png
- documentation/aligned_qa/updated-14.png
- documentation/aligned_qa/updated-13.png
- documentation/aligned_qa/updated-12.png
- documentation/aligned_qa/updated-11.png
- documentation/aligned_qa/updated-10.png
- documentation/aligned_qa/updated-1.png
- documentation/aligned_qa/page-9.png
- documentation/aligned_qa/page-8.png
- documentation/aligned_qa/page-7.png
- documentation/aligned_qa/page-6.png
- documentation/aligned_qa/page-5.png
- documentation/aligned_qa/page-4.png
- documentation/aligned_qa/page-3.png
- documentation/aligned_qa/page-21.png
- documentation/aligned_qa/page-20.png
- documentation/aligned_qa/page-2.png
- documentation/aligned_qa/page-19.png
- documentation/aligned_qa/page-18.png
- documentation/aligned_qa/page-17.png
- documentation/aligned_qa/page-16.png
- documentation/aligned_qa/page-15.png
- documentation/aligned_qa/page-14.png
- documentation/aligned_qa/page-13.png
- documentation/chapter4_revision_work/render/page-18.png
- documentation/chapter4_revision_work/render/page-17.png
- documentation/chapter4_revision_work/render/page-16.png
- documentation/chapter4_revision_work/render/page-15.png
- documentation/chapter4_revision_work/render/page-14.png
- documentation/chapter4_revision_work/render/page-13.png
- documentation/chapter4_revision_work/render/page-12.png
- documentation/chapter4_revision_work/render/page-11.png
- documentation/chapter4_revision_work/render/page-10.png
- documentation/chapter4_revision_work/render/page-1.png
- documentation/chapter4_revision_work/render/overview-6.png
- documentation/chapter4_revision_work/render/overview-5.png
- documentation/chapter4_revision_work/render/overview-4.png
- documentation/chapter4_revision_work/render/overview-3.png
- documentation/chapter4_revision_work/render/overview-2.png
- documentation/chapter4_revision_work/render/overview-1.png
- documentation/chapter4_revision_work/render/page-25.png
- documentation/chapter4_revision_work/render/page-24.png
- documentation/chapter4_revision_work/render/page-23.png
- documentation/chapter4_revision_work/render/page-22.png
- documentation/chapter4_revision_work/render/page-21.png
- documentation/chapter4_revision_work/render/page-20.png
- documentation/chapter4_revision_work/render/page-2.png
- documentation/chapter4_revision_work/render/page-19.png
- documentation/chapter4_revision_work/render/page-29.png
- documentation/chapter4_revision_work/render/page-28.png
- documentation/chapter4_revision_work/render/page-27.png
- documentation/chapter4_revision_work/render/page-26.png
- documentation/chapter4_revision_work/render/page-30.png
- documentation/chapter4_revision_work/render/page-3.png
- documentation/chapter4_revision_work/render/page-31.png
- documentation/chapter4_revision_work/render/page-32.png
- frontend/src/style.css
- documentation/chapter4_revision_work/original_figures/figure_4_06.png
- documentation/chapter4_revision_work/original_figures/figure_4_05.png
- documentation/chapter4_revision_work/original_figures/figure_4_04.png
- documentation/chapter4_revision_work/original_figures/figure_4_03.png
- documentation/chapter4_revision_work/original_figures/figure_4_02.png
- documentation/chapter4_revision_work/original_figures/figure_4_01.png
- documentation/chapter4_revision_work/render/page_inventory.json
- documentation/chapter4_revision_work/render/page-9.png
- documentation/chapter4_revision_work/render/page-8.png
- documentation/chapter4_revision_work/render/page-7.png
- documentation/chapter4_revision_work/render/page-6.png
- documentation/chapter4_revision_work/render/page-5.png
- documentation/chapter4_revision_work/render/page-4.png
- documentation/chapter4_revision_work/render/page-34.png
- documentation/chapter4_revision_work/render/page-33.png
- frontend/src/views/AgentAuditLog.vue
- frontend/src/views/AdminModelEvaluation.vue
- frontend/src/views/AdminDashboard.vue
- frontend/src/views/ResetPasswordPage.vue
- frontend/src/views/RegisterPage.vue
- frontend/src/views/PendingVerificationPage.vue
- frontend/src/views/ManagePasskeysPage.vue
- frontend/src/views/LoginPage.vue
- frontend/src/views/HomeView.vue
- frontend/src/views/ForgotPasswordPage.vue
- frontend/src/views/CompleteProfilePage.vue
- frontend/src/views/CheckEmailPage.vue
- frontend/src/views/AgentPlatformPage.vue
- frontend/src/views/AgentDashboard.vue
- ai-service/requirements.txt
- frontend/src/composables/useTheme.js
- frontend/src/composables/usePasskeySupport.js
- documentation/chapter4_revision_work/final_render/page-1.png
- frontend/src/theme.css
- backend/src/controllers/verificationController.js
- backend/src/controllers/authController.js
- backend/src/controllers/agentController.js
- ai-service/tests/test_svm.py
- backend/src/controllers/adminController.js
- ai-service/tests/test_ocr.py
- ai-service/tests/test_liveness.py
- ai-service/tests/test_kyc_improvement.py
- ai-service/tests/test_kyc_experiment.py
- ai-service/tests/test_image_quality.py
- ai-service/tests/test_face_match.py
- ai-service/tests/test_document_preprocess.py
- frontend/src/components/AuthShell.vue
- frontend/src/stores/authStore.js
- documentation/chapter4_revision_work/final_render/page-13.png
- documentation/chapter4_revision_work/final_render/page-12.png
- documentation/chapter4_revision_work/final_render/page-11.png
- documentation/chapter4_revision_work/final_render/page-10.png
- documentation/chapter4_revision_work/final_render/page-15.png
- documentation/chapter4_revision_work/final_render/page-14.png
- documentation/chapter4_revision_work/final_render/page-16.png
- frontend/src/components/WorkspaceShell.vue
- frontend/src/components/ScoreBar.vue
- frontend/src/components/PasskeyPrompt.vue
- frontend/src/components/PasskeyDialog.vue
- frontend/src/components/PasskeyButton.vue
- frontend/src/components/LiveSelfieChallenge.vue
- frontend/src/components/Lightbox.vue
- frontend/src/components/ImageUpload.vue
- frontend/src/components/DocumentCaptureStep.vue
- frontend/src/components/CameraCapture.vue
- documentation/chapter4_revision_work/chapter5_final_render/page-13.png
- documentation/chapter4_revision_work/chapter5_final_render/page-12.png
- documentation/chapter4_revision_work/chapter5_final_render/page-11.png
- documentation/chapter4_revision_work/chapter5_final_render/page-10.png
- documentation/chapter4_revision_work/chapter5_final_render/page-1.png
- documentation/chapter4_revision_work/chapter5_final_render/page-16.png
- documentation/chapter4_revision_work/chapter5_final_render/page-15.png
- documentation/chapter4_revision_work/chapter5_final_render/page-14.png
- documentation/chapter4_revision_work/chapter5_final_render/page-2.png
- documentation/chapter4_revision_work/chapter5_final_render/page-17.png
- documentation/chapter4_revision_work/chapter5_final_render/page-3.png
- documentation/chapter4_revision_work/final_render/page-2.png
- documentation/chapter4_revision_work/final_render/page-19.png
- documentation/chapter4_revision_work/final_render/page-18.png
- documentation/chapter4_revision_work/final_render/page-17.png
- documentation/chapter4_revision_work/final_render/page-21.png
- documentation/chapter4_revision_work/final_render/page-20.png
- documentation/chapter4_revision_work/final_render/page-22.png
- documentation/chapter4_revision_work/final_render/page-23.png
- ai-service/notebooks/03_kyc_experiment_results.ipynb
- ai-service/notebooks/02_model_training.ipynb
- ai-service/notebooks/01_distribution_analysis.ipynb
- frontend/src/utils/passkeyStorage.js
- frontend/src/utils/documentCaptureSource.js
- frontend/src/utils/deviceFingerprint.js
- frontend/src/utils/authToken.js
- frontend/src/utils/auditLabels.js
- ai-service/config/ocr_templates.json
- documentation/chapter4_revision_work/chapter5_final_render/page-5.png
- documentation/chapter4_revision_work/chapter5_final_render/page-4.png
- documentation/chapter4_revision_work/chapter5_final_render/page-6.png
- documentation/chapter4_revision_work/chapter5_final_render/page-7.png
- documentation/chapter4_revision_work/final_render/page-24.png
- documentation/chapter4_revision_work/final_render/page-25.png
- ai-service/frontend/package.json
- ai-service/frontend/package-lock.json
- frontend/src/services/agentService.js
- frontend/src/services/adminService.js
- frontend/src/services/api.js
- frontend/src/services/passkeyService.js
- ai-service/ml/decision_model.py
- frontend/src/services/verificationService.js
- frontend/src/services/supabase.js
- frontend/src/services/socket.js
- documentation/chapter4_revision_work/before_author_voice_revision/Chapter_4_Wireframes.zip
- documentation/chapter4_revision_work/chapter5_final_render/page_inventory.json
- documentation/chapter4_revision_work/before_author_voice_revision/Chapter_4_Revised.pdf
- documentation/chapter4_revision_work/chapter5_final_render/page-9.png
- documentation/chapter4_revision_work/before_author_voice_revision/Chapter_4_Revised.docx
- documentation/chapter4_revision_work/chapter5_final_render/page-8.png
- documentation/chapter4_revision_work/before_author_voice_revision/chapter4_content.py
- documentation/chapter4_revision_work/before_author_voice_revision/build_chapter4_document.py
- ai-service/services/documentPreprocessService.py
- ai-service/ml/improvement_reporting.py
- ai-service/ml/generation_config.json
- ai-service/ml/generate_dataset.py
- ai-service/scripts/calibrate_ocr_template.py
- ai-service/ml/evaluation.py
- ai-service/ml/audit.py
- ai-service/ml/improve_model.py
- ai-service/services/__init__.py
- ai-service/services/svmService.py
- ai-service/services/ocrService.py
- ai-service/services/mrzService.py
- ai-service/services/livenessService.py
- ai-service/services/imageQualityService.py
- ai-service/services/faceMatchService.py
- ai-service/silent_face/README.md
- ai-service/silent_face/test.py
- ai-service/ml/data/synthetic_verification_dataset.csv
- ai-service/ml/data/kyc_synthetic_dataset_10000.metadata.json
- ai-service/ml/data/kyc_synthetic_dataset_10000.csv
- ai-service/routes/__init__.py
- documentation/chapter4_revision_work/final_render/page_inventory.json
- ai-service/backend/package.json
- ai-service/routes/svmRoutes.py
- ai-service/silent_face/requirements.txt
- ai-service/routes/qualityRoutes.py
- ai-service/routes/ocrRoutes.py
- ai-service/routes/livenessRoutes.py
- ai-service/routes/faceRoutes.py
- ai-service/ml/legacy_v1/evaluation_report.json
- ai-service/ml/legacy_v1/generate_dataset.py
- documentation/chapter4_revision_work/final_render/page-9.png
- documentation/chapter4_revision_work/final_render/page-8.png
- documentation/chapter4_revision_work/final_render/page-7.png
- documentation/chapter4_revision_work/final_render/page-6.png
- documentation/chapter4_revision_work/final_render/page-5.png
- documentation/chapter4_revision_work/final_render/page-4.png
- documentation/chapter4_revision_work/final_render/page-34.png
- documentation/chapter4_revision_work/final_render/page-33.png
- documentation/chapter4_revision_work/final_render/page-32.png
- documentation/chapter4_revision_work/final_render/page-31.png
- documentation/chapter4_revision_work/final_render/page-30.png
- documentation/chapter4_revision_work/final_render/page-3.png
- documentation/chapter4_revision_work/final_render/page-29.png
- documentation/chapter4_revision_work/final_render/page-28.png
- documentation/chapter4_revision_work/final_render/page-27.png
- documentation/chapter4_revision_work/final_render/page-26.png
- ai-service/ml/legacy_v1/train_model.py
- ai-service/ml/measure_benchmarks.py
- ai-service/ml/README.md
- ai-service/ml/reporting.py
- ai-service/ml/requirements-ml.txt
- ai-service/ml/requirements-experiment.lock.txt
- ai-service/ml/schema.py
- ai-service/silent_face/src/__init__.py
- ai-service/ml/data/benchmarks/nuaa_liveness.csv
- ai-service/silent_face/src/utility.py
- ai-service/silent_face/src/train_main.py
- ai-service/ml/data/benchmarks/midv_ocr.csv
- ai-service/ml/data/benchmarks/midv_image_quality.csv
- ai-service/ml/data/benchmarks/lfw_face_match.csv
- ai-service/ml/reports/ablation_comparison.json
- ai-service/ml/reports/benchmark_measurements.json
- ai-service/ml/train_model.py
- ai-service/silent_face/src/anti_spoof_predict.py
- ai-service/ml/reports/decision_tree_feature_importance.csv
- ai-service/ml/reports/decision_tree_confusion_matrix.png
- ai-service/ml/reports/decision_tree_calibration.png
- ai-service/ml/reports/correlation_matrix.png
- ai-service/ml/reports/decision_tree_grid_search.csv
- ai-service/ml/reports/decision_tree_feature_importance.png
- ai-service/ml/reports/descriptive_statistics_by_class.csv
- ai-service/ml/experiments/v3/candidate_scaler.pkl
- ai-service/ml/experiments/v3/candidate_model.pkl
- ai-service/ml/experiments/v3/candidate_confusion_matrix.png
- ai-service/ml/experiments/v3/candidate_calibration.png
- ai-service/ml/experiments/v3/baseline_calibration_diagnostic.json
- ai-service/ml/experiments/v3/development_split_manifest.csv
- ai-service/ml/experiments/v3/comparison.png
- ai-service/ml/experiments/v3/fresh_evaluation_1500.csv
- ai-service/ml/experiments/v3/fresh_evaluation_metadata.json
- ai-service/ml/legacy_v2/generation_config.json
- ai-service/silent_face/src/default_config.py
- ai-service/silent_face/src/generate_patches.py
- ai-service/ml/legacy_v1/models/svm_kyc_model.pkl
- ai-service/ml/legacy_v2/train_model.py
- ai-service/ml/legacy_v1/models/scaler.pkl
- ai-service/ml/legacy_v1/models/model_version.txt
- ai-service/silent_face/src/data_io/dataset_folder.py
- ai-service/ml/reports/distribution_overlap_diagnostics.json
- ai-service/ml/reports/distribution_ocr_confidence_score.png
- ai-service/ml/reports/distribution_liveness_score.png
- ai-service/ml/reports/distribution_face_match_score.png
- ai-service/ml/reports/distribution_contrast_score.png
- ai-service/ml/reports/distribution_brightness_score.png
- ai-service/ml/reports/distribution_blur_score.png
- ai-service/ml/reports/frozen_experiment_protocol.json
- ai-service/ml/reports/FILE_INDEX.md
- ai-service/ml/reports/feature_correlations.csv
- ai-service/ml/reports/evaluation_report.json
- ai-service/silent_face/src/data_io/dataset_loader.py
- ai-service/ml/reports/full_svm_confusion_matrix.png
- ai-service/ml/reports/full_svm_calibration.png
- ai-service/ml/reports/full_svm_grid_search.csv
- ai-service/ml/experiments/v3/power_ovr_training.pkl
- ai-service/ml/experiments/v3/power_ovr_grid.csv
- ai-service/ml/experiments/v3/power_native_training.pkl
- ai-service/ml/experiments/v3/power_native_grid.csv
- ai-service/ml/experiments/v3/incumbent_confusion_matrix.png
- ai-service/ml/experiments/v3/incumbent_calibration.png
- ai-service/ml/experiments/v3/improvement_report.json
- ai-service/ml/experiments/v3/identifiability_diagnostic.json
- ai-service/ml/experiments/v3/raw_ovr_training.pkl
- ai-service/ml/experiments/v3/raw_ovr_grid.csv
- ai-service/ml/experiments/v3/raw_native_training.pkl
- ai-service/ml/experiments/v3/protocol.json
- ai-service/ml/experiments/v3/selection_frozen.json
- ai-service/ml/experiments/v3/README.md
- ai-service/ml/experiments/v3/SUMMARY.md
- ai-service/ml/experiments/v3/svm_permutation_importance.csv
- ai-service/silent_face/src/model_lib/__init__.py
- ai-service/silent_face/src/model_lib/MultiFTNet.py
- ai-service/silent_face/src/model_lib/MiniFASNet.py
- ai-service/ml/models/artifact_manifest.json
- ai-service/ml/models/decision_tree_calibrated.pkl
- ai-service/silent_face/src/data_io/functional.py
- ai-service/silent_face/src/data_io/transform.py
- ai-service/ml/experiments/v3/svm_permutation_importance.png
- ai-service/ml/experiments/v3/validation_candidates.csv
- ai-service/ml/legacy_v2/README.md
- ai-service/silent_face/src/data_io/__init__.py
- ai-service/ml/experiments/v3/verification_checks.json
- ai-service/ml/reports/identity_only_svm_calibration.png
- ai-service/ml/reports/identity_svm_grid_search.csv
- ai-service/ml/reports/identity_only_svm_confusion_matrix.png
- ai-service/ml/reports/legacy_methodology_audit.json
- ai-service/ml/models/identity_only_scaler.pkl
- ai-service/ml/models/decision_tree_model.pkl
- ai-service/ml/models/identity_only_svm.pkl
- ai-service/ml/models/svm_kyc_model.pkl
- ai-service/ml/reports/svm_permutation_importance.csv
- ai-service/ml/reports/split_manifest.csv
- ai-service/ml/models/scaler.pkl
- ai-service/ml/reports/svm_permutation_importance.png
- ai-service/ml/models/model_version.txt
- ai-service/ml/reports/TECHNICAL_SUMMARY.md
- ai-service/ml/reports/verification_checks.json
- ai-service/silent_face/resources/detection_model/Widerface-RetinaFace.caffemodel
- ai-service/silent_face/resources/detection_model/deploy.prototxt
- ai-service/silent_face/resources/anti_spoof_models/4_0_0_80x80_MiniFASNetV1SE.pth
- ai-service/silent_face/resources/anti_spoof_models/2.7_80x80_MiniFASNetV2.pth
- ai-service/ml/legacy_v2/models/decision_tree_calibrated.pkl
- ai-service/ml/legacy_v2/models/artifact_manifest.json
- ai-service/ml/legacy_v2/models/decision_tree_model.pkl
- ai-service/ml/legacy_v2/reports/ablation_comparison.json
- ai-service/ml/legacy_v2/models/identity_only_scaler.pkl
- ai-service/ml/legacy_v2/models/identity_only_svm.pkl
- ai-service/ml/legacy_v2/reports/benchmark_measurements.json
- ai-service/ml/legacy_v2/models/svm_kyc_model.pkl
- ai-service/ml/legacy_v2/models/scaler.pkl
- ai-service/ml/legacy_v2/models/model_version.txt
- ai-service/ml/legacy_v2/reports/decision_tree_confusion_matrix.png
- ai-service/ml/legacy_v2/reports/decision_tree_calibration.png
- ai-service/ml/legacy_v2/reports/correlation_matrix.png
- ai-service/ml/legacy_v2/reports/decision_tree_feature_importance.png
- ai-service/ml/legacy_v2/reports/decision_tree_feature_importance.csv
- ai-service/ml/legacy_v2/reports/decision_tree_grid_search.csv
- ai-service/ml/legacy_v2/reports/verification_checks.json
- ai-service/ml/legacy_v2/reports/TECHNICAL_SUMMARY.md
- ai-service/ml/legacy_v2/reports/svm_permutation_importance.png
- ai-service/ml/legacy_v2/reports/svm_permutation_importance.csv
- ai-service/ml/legacy_v2/reports/split_manifest.csv
- ai-service/ml/legacy_v2/reports/legacy_methodology_audit.json
- ai-service/ml/legacy_v2/reports/identity_svm_grid_search.csv
- ai-service/ml/legacy_v2/reports/identity_only_svm_confusion_matrix.png
- ai-service/ml/legacy_v2/reports/identity_only_svm_calibration.png
- ai-service/ml/legacy_v2/reports/full_svm_grid_search.csv
- ai-service/ml/legacy_v2/reports/full_svm_confusion_matrix.png
- ai-service/ml/legacy_v2/reports/full_svm_calibration.png
- ai-service/ml/legacy_v2/reports/frozen_experiment_protocol.json
- ai-service/ml/legacy_v2/reports/FILE_INDEX.md
- ai-service/ml/legacy_v2/reports/feature_correlations.csv
- ai-service/ml/legacy_v2/reports/evaluation_report.json
- ai-service/ml/legacy_v2/reports/distribution_overlap_diagnostics.json
- ai-service/ml/legacy_v2/reports/distribution_ocr_confidence_score.png
- ai-service/ml/legacy_v2/reports/distribution_liveness_score.png
- ai-service/ml/legacy_v2/reports/distribution_face_match_score.png
- ai-service/ml/legacy_v2/reports/distribution_contrast_score.png
- ai-service/ml/legacy_v2/reports/distribution_brightness_score.png
- ai-service/ml/legacy_v2/reports/distribution_blur_score.png
- ai-service/ml/legacy_v2/reports/descriptive_statistics_by_class.csv
