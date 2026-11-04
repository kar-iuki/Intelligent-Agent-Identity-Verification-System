# Intelligent Agent Identity Verification System — documentation handoff

Prepared on 31 October 2026, Africa/Nairobi time. Product name: **Verity**. Earlier concept name/context: **SalesMesh**. Repository: `Intelligent-Agent-Identity-Verification-System`.

This is a detailed transfer of project context for another documentation chat. It combines the current local source, saved experiment results, existing chapters, Git history, and available project conversations. Read this handoff first, then consult the appended conversations and evidence when more detail is needed. Historical messages preserve what was said at the time; they are not all descriptions of the final system.

## 1. Scope and reliability of this export

The inspected repository was on `main`, at commit `7bd4632` (`frontend updates`). The local `origin/main` reference pointed to the same commit; no remote fetch was performed. There were no reported tracked/untracked changes before creating this export. The local history contains 32 commits from 1 September through 31 October 2026.

The export includes 18 relevant available chats containing 129 turns. Every returned older-page cursor for these chats was followed. It includes user messages and assistant responses, including available progress messages, but excludes internal reasoning, tool execution bodies, credentials, and ambient browser state. This is an evidence-backed project export, not a guarantee that every conversation ever held in every account or application is available. One historical KYC prompt response was truncated by the chat retrieval service at 20,000 characters; the related implementation brief and subsequent results are also preserved in the model-development chat. Some image attachments and linked message bodies were not returned as readable content. The coverage appendix records these limits.

No application code, model, production configuration or database was changed for this export. No new training, runtime test campaign, deployment or live database query was performed. Test and deployment results below retain their original dates and scope. Secret `.env` files and raw identity images are not included. Current cloud pricing, hosting eligibility and legal claims in old chats have not been revalidated; treat those passages as historical discussion.

When sources disagree, use current source for current local behavior, saved reports for measured results, dated chat messages for user confirmations, and the most recent documentation for intended requirements. A requirement in Chapter 4 is not proof it has been implemented. A local change is not proof it has been deployed.

## 2. What the project is about

This final-year Computer Science project is a web-based system for registering independent agents, checking identity evidence, deciding whether verification should succeed or need review, and controlling access based on the outcome. The original business context was SalesMesh, a distributed sales/onboarding platform where organisations rely on independent agents. The product was later named Verity during hosting work.

Here, an **agent is a human applicant or independent worker**, not an autonomous software agent. The system coordinates pretrained computer-vision components and a separately trained KYC decision classifier. It does not use a conversational large language model to inspect identity documents or make operational verification decisions.

The problem is that unverified registrations, impersonation, poor document images and inconsistent checks can undermine trust and access control. The implemented workflow gathers personal details, document images and a live selfie; measures quality, text agreement, facial similarity and liveness; combines six scores; records a decision; and supports administrator review and audit.

The five objectives carried through the documentation are:

1. Identify current methods used for agent registration and verification in distributed onboarding systems.
2. Analyse challenges associated with agent verification, identity fraud and access control.
3. Examine existing digital identity verification/KYC technologies and platforms.
4. Develop an AI-enabled agent registration, KYC verification and access-control system.
5. Test and validate its effectiveness, accuracy and usability.

The first three objectives are linked in Chapters 5–6 to the literature review and requirements work. The available repository does not itself contain a complete authoritative copy of Chapters 1–3. Do not invent their literature findings, citations, participant interviews or comparative results.

The demonstrated contribution is an integrated implementation and a reproducible synthetic score-classification experiment. The evidence does not establish reliable unattended approval of real applicants, a measured reduction in fraud or staffing time, superiority over commercial KYC products, or legal compliance.

## 3. Scope evolution and abandoned proposals

Early brainstorming included a generic trust score, reputation/behaviour signals, résumé evaluation with spaCy and Sentence Transformers, compliance questionnaires, Microsoft/Apple login, optional government identity APIs, mobile applications and biometric scanners. Logistic Regression was initially suggested; Random Forest was also discussed and the user wanted another approach. Those ideas must not be presented as completed modules. The implemented decision model is an RBF SVM, with a Decision Tree comparison and an identity-only SVM experiment.

The early proposed synthetic dataset was roughly 3,000–5,000 rows; historical code used 4,000. The revised experiment uses 10,000 synthetic rows plus a separate fresh 1,500-case evaluation set for v3. Initial design diagrams and explanations therefore require version-aware reading.

Hugging Face and Heroku hosting were explored. The later confirmed hosting arrangement is Vercel + Render + Azure Container Apps + Supabase. Old Hugging Face deployment instructions remain in some model documentation; they are historical compatibility instructions, not the final hosting description.

## 4. Architecture and technology

```text
Applicant / administrator browser
        |
        v
Vue 3 frontend — Vite, Vue Router, Axios, MediaPipe, Socket.IO client
        |
        v
Node.js / Express backend — authentication, roles, files, workflow, decisions, audit
        |                                      |
        v                                      v
Python / Flask AI service                 Supabase
OpenCV, EasyOCR, InsightFace,              Auth, PostgreSQL, private Storage
Silent-Face, scikit-learn SVM              and database-change subscriptions
        |
        v
Six numerical scores -> calibrated SVM -> decision/probabilities
```

| Layer | Local location | Main purpose | Local default |
|---|---|---|---|
| Browser application | `frontend/` | Account pages, capture wizard, dashboards, administrator review | Port 5173 |
| Application API | `backend/` | Coordinates protected operations and persistent records | Port 3000 |
| AI service | `ai-service/` | Image processing and saved-model inference | Port 5000 |
| Database scripts | `database/` | PostgreSQL schema, policies, functions and storage configuration | Supabase |
| Reports | `documentation/` | Chapters, evaluation evidence, wireframes and render checks | Local artifacts |

Frontend dependencies include Vue 3.5, Vue Router 4.5, Vite 6, Axios, Supabase JavaScript client, MediaPipe Tasks Vision, SimpleWebAuthn browser support, Socket.IO client and Lucide icons. Backend dependencies include Express 4, Supabase client, SimpleWebAuthn server, Helmet, CORS, Multer, dotenv, Socket.IO and UA parsing. Test tools include Node's test runner, PGlite, Vitest/jsdom, Playwright and Python unittest/pytest-style tests. Exact package manifests are retained in the source appendix; version ranges should not be confused with a newly verified deployment inventory.

The saved model manifest records experiment versions including scikit-learn 1.9.0, NumPy 2.5.3, SciPy 1.18.1, pandas 3.0.6, joblib 1.6.0, Matplotlib 3.11.2 and Flask 3.1.3. These are recorded artifact metadata, not an independent audit of installed production libraries.

## 5. User roles and account workflow

There are two application roles: `agent` and `admin`. Supabase provides authentication; the application stores user/profile and verification records. Users can register/sign in with email/password or Google. Email confirmation, resend confirmation, forgot-password and reset-password flows are implemented. Google sign-in users complete required profile fields before protected agent functions.

Profile information includes full name, email/account association, phone number, national ID/identity identifier and date of birth. Date validation and duplicate identifier checks are present. The Google-prefilled name was changed to be editable because Google profile names can be nicknames. The interface asks for the official document name.

Protected backend routes use authentication and role middleware. Frontend route guards guide users to login, profile completion or the appropriate dashboard. Frontend guards are navigation controls; backend checks remain necessary. A verified-agent workspace exists; this is not evidence of a complete external SalesMesh sales platform integration.

The password-login human check is an internal five-character SVG CAPTCHA. Challenges expire after five minutes and are consumed on the first verification attempt. They are held in an in-process Map, with pruning/cap behavior. This differs from passkey challenges, which have database-backed mechanisms. CAPTCHA restart/multiple-instance behavior and an accessible non-visual alternative remain documented gaps.

## 6. Verification workflow

1. Authenticate and complete personal details.
2. Select national ID, passport or driving licence and provide the required document side(s).
3. Capture or upload document images under the current attempt policy; complete the live selfie flow.
4. Validate JPEG/PNG format and the per-file 5 MiB limit. The server uses in-memory multipart handling and private Supabase Storage.
5. Perform image-quality assessment, including individual capture-step checks and the verification gate. Give recapture feedback if quality fails.
6. Create/persist verification request and score information as the workflow progresses.
7. Run document text extraction/comparison, document-to-selfie face matching, and image-based liveness analysis.
8. Supply a complete valid six-score vector to the SVM decision service; use separately identified threshold fallback when the model path is unavailable and scores are valid.
9. Store final class, probabilities and decision basis; update request status and access records; add audit events.
10. Show the agent results, reasons, progress and next steps. Surface Manual Review cases to administrators, including real-time notifications.
11. An authorised administrator can inspect evidence and history, approve/reject, and have the resulting decision/access/audit state recorded.

`pending` is a workflow status. The three classifier outputs are `verified`, `review`, `rejected`, displayed as Verified, Manual Review, Rejected. Do not describe pending as a fourth SVM class.

### Current document retry and camera behavior

The first submitted verification attempt may use supported document uploads. From the second attempt onward, document inputs must follow the camera capture workflow. The backend determines this by the presence of a stored verification request for that agent, including quality-failed attempts; it does not rely on a browser-only counter or expiring strike count. This survives refresh and sign-in on another session.

The backend rejects non-camera source markers for submitted front/back images and the legacy upload path when a camera is required. Source metadata is workflow enforcement, not cryptographic proof that a physical camera produced the bytes. Do not claim the policy guarantees forgery prevention.

Document/selfie capture boxes were reduced so instructions and buttons stay visible. Retake now reopens the camera. The frontend's active selfie challenge now randomly requests **left or right head turns only**. Blink/open-eye challenges were removed on 30 October. These movement challenges use MediaPipe in `LiveSelfieChallenge.vue`; they are distinct from the Python image-based anti-spoof model. Chapter 4's older reference to a movement or blink challenge needs updating if the documentation is refreshed to the latest code.

## 7. Image processing and the six-score contract

| Input order | Canonical feature | Backend alias | Meaning and valid units |
|---:|---|---|---|
| 1 | `face_match_score` | `faceMatchScore` | Clipped cosine similarity × 100, range 0–100 |
| 2 | `liveness_score` | `livenessScore` | Image-based anti-spoofing score, range 0–1 |
| 3 | `ocr_confidence_score` | `ocrConfidenceScore` | Document-text agreement score, range 0–1 |
| 4 | `blur_score` | `blurScore` | Raw Laplacian variance, nonnegative, no arbitrary finite maximum |
| 5 | `brightness_score` | `brightnessScore` | Mean HSV V channel, range 0–255 |
| 6 | `contrast_score` | `contrastScore` | Grayscale standard deviation, range 0–127.5 |

The quality inputs are **raw image measurements**, not generic 0–1 quality ratings. Higher blur-score values mean greater sharpness because the measurement is Laplacian variance. `ocr_confidence_score` represents document text agreement in this pipeline, not simply EasyOCR's confidence in recognising characters.

### Quality and document preprocessing

OpenCV measures sharpness, brightness and contrast. Document preprocessing includes document localisation, quadrilateral ordering/perspective correction and template/crop support. Quality is evaluated on a located document at native size when available, to reduce influence from desks or backgrounds. Different document types and selfies have different defaults; environment overrides are supported.

Current located-document blur defaults are 25 for national ID and 20 for passport/driving licence. Located-document brightness defaults are 30–248 and contrast minimum 12. A soft-blur factor of 0.6 can allow an intermediate result with a warning. Selfie defaults include blur 2, brightness 10–245 and contrast 2. Generic/fallback paths also retain other thresholds; do not publish one number as the universal quality criterion. The source explicitly notes permissive document thresholds during cross-phone testing; these are not validated operational acceptance limits.

### OCR and identity agreement

EasyOCR extracts text. Additional code handles document preprocessing, front/back evidence, document-type templates, field selection, dates, identifiers and machine-readable-zone parsing/checks. Template configuration and calibration tooling are included.

Name matching was corrected to compare complete distinct name parts, ignoring order/capitalisation. Every token in the shorter name set must occur in the longer set, with at least two distinct names matching. This supports an entered two-part name within a longer official name and the reverse subset case. A single common name or partial-word substring is insufficient. The ID comparison is exact after its normalisation; date parsing/comparison is separate. The name-rule change does not make OCR proof of document authenticity.

### Face matching

InsightFace loads the pretrained `buffalo_l` package and produces ArcFace-style embeddings. The service finds a face (choosing the largest if more than one is detected), computes cosine similarity and scales/clips it to 0–100. It records model-initialisation failures. The component's own match threshold is 70; this is separate from fallback decision thresholds and the learned SVM boundary. The project did not train ArcFace from scratch.

### Liveness

Silent-Face-Anti-Spoofing uses the bundled MiniFASNet weights and a face detector. The repository contains `2.7_80x80_MiniFASNetV2.pth`, `4_0_0_80x80_MiniFASNetV1SE.pth` and detector resources. The service uses live/spoof thresholds of 0.75 and 0.50 and image preparation without distorting the face. It reports unavailable model state rather than establishing a successful result without the models.

This is pretrained image-based presentation-attack scoring. Early concept messages claimed broad attacks such as deepfakes and 3D masks; the retained evaluation does not establish protection against those classes. NUAA measurements do not constitute a modern comprehensive attack test.

## 8. SVM API, validation, fallback and access control

The Flask prediction endpoint is `POST /api/svm/predict`. Canonical snake_case requests receive display labels and a probabilities mapping. Legacy camelCase requests retain lowercase backend/database enums and legacy probability fields. Both use the same physical units and exact feature order. Probability columns are mapped from `classes_`, never assumed positional.

Validation rejects non-object bodies, unknown fields, duplicate aliases for one feature, missing values, strings, booleans, non-finite numbers, negative values and out-of-range bounded scores. Missing or inconsistent model artifacts result in service-unavailable behavior. Model/scaler/version/feature contract hashes are validated. Successful model responses use `decisionBasis: svm_model`.

Backend decision normalisation checks the six inputs before inference/fallback; invalid evidence must not silently become a valid zero vector. Response validation checks enums, decision basis, finite probabilities in [0,1] and their sum. This does not mean every historical upstream controller path is free of numeric coercion: source still contains initial/default score handling. The strict guarantee concerns the validated decision boundary.

The SVM status and prediction calls each use the `SVM_TIMEOUT_MS` setting, default 5,000 ms in local source. They are separate calls, so 5 seconds is not a verified end-to-end deadline. A deployment chat suggested 180,000 ms to accommodate startup, but the effective current cloud value was not independently verified for this export.

If model inference is unavailable or invalid after valid scores, the backend logs a fallback reason and uses `placeholder_threshold`. Its exact rules are:

* Reject first if face < 50, liveness < 0.50, OCR agreement < 0.40, or blur < 80 together with face < 65.
* Otherwise verify only if face > 80, liveness > 0.75 and OCR agreement > 0.70, all strictly satisfied.
* Otherwise return Manual Review.

Fallback outputs contain 0/1 class indicators; these are deterministic rule outputs, not calibrated certainty. The SVM may return decisions that differ from these rules. Preserve the distinction in reports, logs and database analyses.

`access_control_records` grants access only for verified decisions. Administrator overrides and platform status checks are implemented, but the supplied live exports did not independently demonstrate every deployed access-control path. The audit utility checks expected event presence/order; it is not a cryptographic tamper-proof ledger.

## 9. Model development history and methodology

### Version 1 and the methodological audit

The original synthetic data contained 4,000 rows and nearly separated class-specific feature ranges. Old runs approached 100% performance. The audit did not deliberately corrupt labels or target a lower accuracy. It found that the simulated problem was too easy, including quality channels acting as artificial class identifiers. Individual small trees on quality features reached roughly 0.93–0.97 training-CV macro F1. The original notebook fitted scaling before CV, allowing fold-level preprocessing leakage; older retraining code hard-coded earlier winners.

No exact duplicates/cross-split duplicate vectors or direct target-column use were found in the inspected old-data/code audit. The absence of historical repeated test use cannot be established. Keep this distinction: questionable synthetic separability is not proof that every possible type of leakage occurred. Legacy v1 and v2 code/artifacts remain preserved.

### Version 2 data generation

The revised generator uses stored local measurements: 1,000 LFW face pairs, 1,200 NUAA presentations, 500 MIDV image-quality observations and 480 MIDV OCR observations. The revised work reused these measurements; it did not independently rerun all original benchmark images. These datasets do not supply end-to-end three-class KYC labels.

Ten thousand simulated cases contain six features plus the target only. Labels come from explicitly assumed latent scenarios. Face/liveness distributions use measured moments; quality uses a continuous joint representation including log1p blur and covariance. OCR and quality relationships, borderline cases, observation noise and scenario mixtures are modelling assumptions. Scenarios include face mismatch with otherwise strong evidence, presentation attacks, document disagreement, uncertain identity signals, genuine recapture problems and overlapping adjudication outcomes. There are no arbitrary label flips and no hand-assigned feature weights in the SVM.

Every feature has overlapping central 90% intervals across class pairs. Some different adjudication classes deliberately share observed distributions, representing missing information. This ambiguity is a simulator assumption, not a measured property of real applicants. The v3 identifiability diagnostic records an 8% minimum population error contribution from observationally identical components with different assumed outcomes.

| Partition | Verified | Manual Review | Rejected | Total |
|---|---:|---:|---:|---:|
| Full original revised dataset | 6,000 | 2,000 | 2,000 | 10,000 |
| Training | 4,200 | 1,400 | 1,400 | 7,000 |
| Original validation/calibration | 900 | 300 | 300 | 1,500 |
| Original test | 900 | 300 | 300 | 1,500 |

The 60/20/20 class mix is an experimental quota, not a population fraud-prevalence estimate. Seed 42, configurations, hashes, split manifests and duplicate checks support reproducibility. Exact, conflicting-label, cross-split and documented near-duplicate checks reported zero under their specified tolerances.

### Training and calibration

The classifier is scikit-learn `SVC` with an RBF kernel, balanced class weighting and training-fold preprocessing. Each SVM grid compares C = [0.1, 1, 10, 100] and gamma = [0.001, 0.01, 0.1, 1, scale, auto]: 24 candidates × 5 stratified shuffled folds. Macro F1 is the selection metric. Each fold learns its own MinMaxScaler; final scaling/classifier fitting uses only the 7,000 training cases. The held-out original test is excluded from fitting/tuning/calibration.

For five-fold CV, each fit trains on 5,600 training-subset rows and validates on 1,400; fresh models are fitted per fold. It is not another model independently certifying the SVM. The selected full model uses C=10, gamma=scale, training-CV macro F1 0.672766. A frozen classifier receives sigmoid calibration from held-out calibration data. Decisions use calibrated probabilities. Calibration can alter argmax decisions under the experimental class prior.

The RBF kernel computes `K(x,z) = exp(-gamma * ||x-z||²)` on scaled feature vectors. Learned support-vector coefficients and intercepts create nonlinear decision scores. The model does not simply choose the nearest case, and gamma is not a manual weight on one feature.

### Original v2 measured results — original 1,500-case test

| Model | Accuracy | Macro F1 | Weighted F1 | Rejected -> Verified | Review -> Verified |
|---|---:|---:|---:|---:|---:|
| Full six-feature SVM | 74.333% | 0.621383 | 0.705566 | 57 | 217 |
| Identity-only SVM | 73.600% | 0.639735 | 0.714382 | 53 | 196 |
| Decision Tree | 74.200% | 0.618165 | 0.704358 | 107 | 227 |

Identity-only SVM selected C=100, gamma=auto, CV macro F1 0.675051. The tree selected depth 3 and minimum leaf size 5, CV macro F1 0.654701.

Full v2 SVM confusion matrix, actual rows/predicted columns in order Verified, Manual Review, Rejected:

```text
836  12  52
217  57  26
 57  21 222
```

Per-class precision/recall/F1: Verified 0.753153/0.928889/0.831841; Manual Review 0.633333/0.190000/0.292308; Rejected 0.740000/0.740000/0.740000.

V2 permutation importance (20 repeats, mean macro-F1 drop): liveness 0.180015, face 0.107227, OCR 0.047299, blur 0.001410, brightness -0.000072, contrast -0.004103. Negative values were retained. Tree impurity importance is a different measure and must not be compared as if the same statistic.

Adding quality features did not improve macro F1 over identity-only in v2: full-minus-identity difference -0.018352, paired 95% interval [-0.036007, -0.000685]. Accuracy and probability metrics improved modestly while false-verification counts worsened. All six features remained the production contract.

V2 probability metrics: full SVM log loss 0.692656, multiclass Brier 0.391520; identity-only 0.704705/0.398989; native tree 0.805264/0.470119; sigmoid-calibrated tree 0.716709/0.403878. These describe the synthetic evaluation, not certainty about real identity.

### Version 3 improvement and promotion

After v2 results were observed, the original test was retired. The 1,500 development-validation cases were split into 750 calibration and 750 selection cases. A fresh 1,500-case synthetic evaluation set was generated only after candidate selection was frozen. Training remains 7,000; the old 1,500 test remains historical. Do not describe all 11,500 cases as training data.

The comparison examined raw versus power-transformed quality inputs, native multiclass versus explicit one-vs-rest SVMs, sigmoid/isotonic/temperature calibration and review/verification decision policies. Three new 24-point five-fold searches ran; the prior raw-native winner was reused with provenance. Checkpoint recovery, frozen selection, fresh evaluation and a predeclared release gate automate the offline workflow. This is not online learning.

The selected candidate is `raw_native_sigmoid`, C=10, gamma=scale. Its probability policy uses review multiplier 1.0, verification threshold 0.0 and margin 0.0. More complex alternatives did not beat the selection baseline while satisfying the defined constraints. The current local bundle is **v3.0.0**.

| Same fresh 1,500 cases | Saved v2 | Selected v3 | Saved Decision Tree | Existing threshold rules |
|---|---:|---:|---:|---:|
| Accuracy | 75.733% | 75.800% | 75.667% | 28.667% |
| Macro F1 | 0.651909 | 0.654082 | 0.648469 | 0.263647 |
| Rejected -> Verified | 44 | 43 | 95 | 0 |
| Manual Review -> Verified | 186 | 184 | 208 | 8 |

The threshold comparison was an additional offline descriptive evaluation on 23 October; it did not tune or select the SVM. The tree was a saved reference, not retrained on the fresh test. Exact complete comparison tables are retained in Chapter 5 and `improvement_report.json`.

V3 gained **one correct classification**, or 0.067 percentage points of accuracy, over v2 on the same set. The accuracy-difference 95% paired bootstrap interval is [-0.001333, 0.003333] in fraction units (approximately -0.133 to +0.333 percentage points). Macro F1 difference is 0.002173 with interval [-0.001051, 0.006855]. Both include zero: the gain is inconclusive, not a statistically established improvement. Do not use the old 74.333% test result as the before-value for 75.800%.

V3 confusion matrix, actual rows/predicted columns Verified, Manual Review, Rejected:

```text
831  15  54
184  82  34
 43  33 224
```

V3 precision/recall/F1: Verified 0.785444/0.923333/0.848825; Manual Review 0.630769/0.273333/0.381395; Rejected 0.717949/0.746667/0.732026. Weighted F1 is 0.731979. Manual Review recall is only 27.33%.

There are 227 false verifications among 600 non-Verified synthetic cases (37.83%). There are 227 incorrect results among 1,058 predicted verifications (21.46%). Overall classification error is 24.20%. These percentages use different denominators.

V3 log loss/Brier are 0.659596/0.373110, compared with incumbent 0.660123/0.373659. V3 permutation-importance mean drops are liveness 0.201380, face 0.110442, OCR 0.049802, blur 0.003831, brightness -0.000359 and contrast -0.003439. Repeat SDs and plots are retained in the report.

The production model remains static after training. Finishing KYC does not retrain it. Future batch retraining needs independently checked, administrator-confirmed real records, explicit evaluation, versioning and rollback. Running the v2 training script can replace the v3 artifacts; the README warns about this.

## 10. Database and persistent records

The real implementation uses snake_case table names. Conceptual diagram labels such as KYCDecisions are not the literal SQL names.

| Table | Key role and relationships |
|---|---|
| `users` | UUID user, unique email, role, creation time; optional schema password_hash field is not evidence that app passwords bypass Supabase Auth |
| `agents` | UUID agent, unique user reference and national ID, name, phone, date of birth, profile-photo reference |
| `documents` | UUID document, agent reference, type, stored file reference, upload time |
| `verification_requests` | UUID attempt, agent and document references, status, creation time |
| `verification_scores` | One unique score record per request with all six feature columns |
| `kyc_decisions` | One unique decision per request, three probabilities, basis, decision time |
| `access_control_records` | Agent/decision references, access_granted, enforcement timestamp |
| `audit_logs` | Action, outcome, time, actor and optional agent/request/IP/device context, JSON details |
| `passkeys` | Verified WebAuthn public credential data and management metadata |
| `passkey_challenges` | Challenge lifecycle and purpose/user binding |
| `passkey_rate_limits` | Database-backed rate-limit state |

Schema design uses UUID primary keys, foreign keys, uniqueness constraints and indexes. Several cascades mean deleting document records could erase linked verification history; retention intentionally removes image objects and clears file references while retaining rows.

SQL files include `schema.sql`, `agents_date_of_birth.sql`, `rls_policies.sql`, `storage_agent_documents.sql`, `access_control_module8.sql`, `audit_logging_module10.sql`, `audit_logs_nullable_request.sql` and `passkeys.sql`. The passkey migration defines challenge-consumption/rate-limit/removal functions and privileges. The original schema alone is not the whole installation; later migrations/policies matter. Do not rerun a destructive or conflicting initial schema against an existing deployment merely to add passkeys.

Supabase RLS is enabled and applicable policies restrict own-record/admin reads and ordinary audit updates/deletes. The backend service-role credential is privileged; RLS policy presence must not be represented as preventing every privileged server action. Identity images use the private `agent-documents` bucket and temporary signed access, rather than public image URLs.

## 11. Optional passkeys

WebAuthn was added without removing password or Google login. Agents can enrol a passkey, sign in, and manage credentials with add/rename/remove. The login screen uses a compact icon-only passkey button beside Sign In. Setup prompts and unsupported-device/cancel/error handling exist.

Server behavior includes random challenges, origin/RP validation, user verification, opaque user handles, verified-credential storage, replay/expiry/purpose binding, signature verification through SimpleWebAuthn, credential-counter handling and database-backed rate limiting. Synced credentials with zero counters are handled. Rename/delete is scoped to the authenticated owner and removal protects the last usable sign-in method, accounting for email/Google alternatives. A successful passkey flow issues the normal Supabase session through the implemented exchange.

The server stores credential public keys and metadata, not fingerprint/face templates or the authenticator private key. Device unlock may use biometrics, PIN or screen lock, depending on the device.

Hosted passkey troubleshooting found two distinct configuration issues: localhost/ngrok origins no longer matched the Vercel domain, and `WEBAUTHN_RP_ID` was incorrectly given a full URL. The recorded correct public settings are:

```dotenv
FRONTEND_URL=https://intelligent-agent-identity-verifica.vercel.app
WEBAUTHN_RP_ID=intelligent-agent-identity-verifica.vercel.app
WEBAUTHN_ORIGINS=https://intelligent-agent-identity-verifica.vercel.app
```

RP ID is a hostname, without protocol/path. Origin is the exact full HTTPS origin, without a trailing slash. Localhost credentials cannot simply be reused for the hosted domain; users must sign in another way and enrol a credential for that domain. Earlier ngrok configuration and a 200 endpoint response were verified historically, but a real-device ceremony still needed checking at that point. The latest hosted fix was diagnosed and instructions supplied; this export does not confirm that the user applied them or completed a successful hosted enrolment.

## 12. Fraud guardrails, audit and retention

Implemented guardrails include duplicate identifiers, configured disposable-email-domain blocking, repeated failed attempts by IP and device fingerprint, strike recording and administrator strike reset. Defaults are three failures per IP, three per device, a 24-hour lookback and three strikes before rejection. They are configurable. A fingerprint or IP limit is not reliable proof of unique personhood.

Audit records cover significant registration, authentication, upload, quality, OCR, face, liveness, decision, access and administrator events. They retain actor/context and outcomes, including events before a request/profile exists. Administrators can filter/export CSV and inspect per-agent history. Agents can see their own audit history. An audit-verification command checks expected events and ordering, including quality-only rejection paths.

Successfully verified agents' identity images remain available for **three full business days** from the applicable successful decision. The calculation uses Africa/Nairobi (UTC+03:00), preserves time of day and skips Saturday/Sunday. It does not implement a public-holiday calendar. Cleanup runs at backend startup and every 15 minutes.

The cleanup checks the latest request/decision, removes eligible stored images and superseded uploads, clears matching stored file references, retains metadata/decisions/scores/audit history, protects newer uploads and leaves references for retry after storage deletion failure. It does not implement the amended 30-day non-verified/abandoned-image policy or 180-day metadata expiry. Current exclusions for pending/review/rejected cases are not passing evidence for those newer requirements.

The administrator directory was moved before recent activity. A Last 3 business days view shows verified cases in the audit window with deadlines. Earlier navy/teal styling was later superseded by the current deep-teal/ivory shared theme.

## 13. Interface work completed

The frontend includes public Home, Login, Register, Check Email, Forgot Password, Reset Password, Pending Verification and Complete Profile views; Agent Dashboard, Audit, Platform and Manage Passkeys views; and Administrator Dashboard and Model Evaluation views.

Shared `WorkspaceShell` and `AuthShell` components support consistent layouts. Work completed includes a collapsible left navigation with saved preference, a mobile drawer, persistent administrator section selection, responsive forms/tables/cards, keyboard focus behavior and shared light/dark themes. Components include document capture, camera capture, live selfie challenge, score bars, image lightbox and passkey dialogs/prompts.

The new public landing page was finished on 31 October. It includes Register now/Sign in calls to action, an animated identity card, interactive previews, scroll transitions, process explanation, features, FAQs and mobile navigation. The router preserves authentication/recovery callbacks arriving at the site root and respects reduced-motion settings for supported navigation effects. A Vercel single-page-app rewrite fixes direct route and OAuth-return 404s.

The administrator Model Evaluation page obtains a saved JSON report through the backend. By default, the backend reads `ai-service/ml/reports/evaluation_report.json`, which contains the original v2 evaluation; `MODEL_EVALUATION_REPORT_PATH` can override it. The model-loaded/version indicator separately queries the AI service. Therefore an available v3 model does not automatically mean every dashboard evaluation figure describes v3. The default file path also needs to exist in a backend-only deployment. The current source has no separate Flask `/api/svm/evaluation` route.

`frontend/src/theme.css` now owns shared colour roles; `frontend/COLORS.md` documents them. Brand deep teal is #193D36, warm ivory #F8F8F1, success green #15803D, warning amber #B45309, danger red #B91C1C and information blue #2563EB. Status labels/icons accompany colour; score bars include assessments. The public landing page intentionally stays ivory while workspace/account views have light/dark equivalents. Browser checks do not amount to full accessibility certification.

## 14. Deployment history and recorded environment

| Service | Recorded host/address | Evidence level |
|---|---|---|
| Frontend | `https://intelligent-agent-identity-verifica.vercel.app` | User-confirmed hosted; HTTP 200 recorded 27 October |
| Backend | `https://verity-backend-gvbs.onrender.com` | User-confirmed hosted; /health HTTP 200 recorded |
| AI | `https://verity-ai.greenpond-207a4102.southafricanorth.azurecontainerapps.io` | Azure Container Apps; /health HTTP 200 recorded |
| Authentication/database/storage | Supabase Free, Ireland | User confirmation on 30 October |
| Backup destination | Google Drive, daily scripted database backup | User-reported practice; script/restore not independently verified |

A separate chat, `Estimate SalesMesh AI memory needs`, contains substantial deployment work even though its working directory differs from this repository. It is included in this export. The user changed the product name to Verity during that work.

The initial memory review inspected code/model sizes and provisionally estimated 2–4 GB for overlapping inference in one process, with 4–6 GB suggested as an initial profiling environment. These were estimates, not measured memory peaks. Cached EasyOCR weights were about 98.3 MB, InsightFace ONNX weights about 341.3 MB, Silent-Face weights about 3.7 MB plus a 1.9 MB detector, and the SVM roughly 398 KB. Model-file size is not runtime RAM.

Deployment packages were prepared outside this repository: an approximately 387 MB bundle, a 5.4 MB model-download-at-build variant and a GitHub build package. ACR Tasks were blocked for the subscription, so the workflow switched to GitHub Actions and GHCR, with a private `verity-ai-deploy` repository and recorded image `ghcr.io/kar-iukii/verity-ai:v1`. A missing-folders/workflow upload problem was corrected. An OpenCV `libxcb.so.1` import failure was addressed by uninstalling conflicting OpenCV distributions and reinstalling the headless package in the Dockerfile. The user subsequently reported the build succeeded.

The deployment package used Gunicorn on port 8000 and an API-key-protected service wrapper. Its `wsgi.py` requires a key of at least 32 characters, validates the model bundle, caps request size at 20 MiB and exempts only `/health` from the constant-time API-key comparison. The packaged Gunicorn command uses one worker, one thread and a 240-second worker timeout; this is separate from the backend's per-call timeout. Azure startup troubleshooting covered missing/too-short API secrets, the difference between a secret's name and value, incorrect secret references, region restrictions, ingress/port readiness and possible worker memory pressure. SIGKILL was treated as a possible memory issue, not definitive proof. The allowed region list included South Africa North, which became the deployed region. Suggested configuration was 2 CPUs/4 GiB, min 0/max 1 replicas and disabled zone redundancy; current effective allocation was not independently audited here.

The backend now uses a common `fetchAI()` helper to send `X-API-Key` from `VERITY_API_KEY`; remote hosts require a sufficiently long configured key and redirects are rejected. The local root Flask app does not itself show the deployment wrapper's full API-key enforcement. That wrapper lives in the separate deployment package; distinguish local source from deployed packaging.

An authenticated Azure status check in the deployment chat reported model loaded and version 3.0.0. Separately, the unauthenticated 27 October documentation check received 401 from `/api/svm/status` and therefore could not establish the model version through that particular check. These are different observations, not contradictory outcomes. Neither proves the latest local revision is deployed today.

Render CORS troubleshooting removed a trailing slash from FRONTEND_URL. Vercel received `frontend/vercel.json` rewrites to `/index.html` so `/login` and OAuth returns work. Backend status handling could display Fallback Mode when a status call was unauthorised, even while Azure's model was loaded; diagnosis focused on matching API keys and deploying the header-sending code.

Deployment chats describe local-to-deployment copying and image rebuilding/versioning; the separate AI repository is not automatically synchronised with this main project. Latest capture/theme/landing changes were reported as requiring frontend/backend redeployment. A local Git remote-tracking ref matching main does not verify their live rollout.

## 15. Recorded test evidence and live records

The consolidated Chapter 5 run on **23 October 2026** recorded **46 passing tests**:

| Suite | Count |
|---|---:|
| Python SVM contract | 6 |
| Python experiment integrity | 2 |
| Python v3 improvement | 4 |
| Backend KYC decision | 2 |
| Backend verified-image retention | 5 |
| Backend passkey service | 9 |
| Backend passkey routes | 1 |
| Backend passkey database migration | 1 |
| Frontend Vitest unit tests | 16 |
| Total | 46 |

These use local artifacts, mocks and PGlite for applicable boundaries. The earlier 14 tests are included in this total, not additional to it. The evidence folder preserves an initial frontend command-path failure and later successful retest; cite the completed result while retaining the execution history.

Other historical change-specific checks include: five isolated name-matching tests and frontend build; seven retention/dashboard checks and build; 10 backend, 14 frontend and 11 browser passkey checks during initial completion; 15 unit, 11 passkey browser and four navigation/layout checks for dashboard redesign; 44 automated checks and build for capture/retry changes; four landing browser checks and build; 35 checks and build for theme consistency. These counts overlap across different runs and scopes. They must not be added into one unique-test total or silently substitute for the dated 46-test Chapter 5 run.

The retained live export summary covers **12 verification requests from eight unique agents**, with 12 complete six-score records and nine decisions. Request statuses were seven verified, two rejected and three pending; decisions were seven verified and two rejected, with no Manual Review decision. Five decisions used `svm_model`; four used `placeholder_threshold`. Nine request/decision statuses matched, no orphan decisions were found, all requests had scores and probability sums were valid. The request date range was 20 September–3 October 2026. These are historical supplied records, not current database totals.

The nine decisions lack independent real-identity ground truth and recorded model versions sufficient for an accuracy claim. The causes of the four historical fallback decisions were not established by matching logs. Three pending requests must not be silently described as successful completions. Very low face scores on some verified SVM cases are observations to investigate, not evidence that those identities were correctly verified.

HTTP 200 health/page checks on 27 October establish availability at that time. The user confirmed the hosted workflow worked. This is separate from automated tests, full pipeline latency, modern attack testing, real-device passkeys, load testing or independent identity accuracy.

## 16. Documentation and academic artifacts

The current substantive chapter outputs are:

* `documentation/Chapter_4_Revised.docx` and `.pdf`: system analysis/design, OOAD, requirements, diagrams, data/ML design, wireframes and traceability.
* `documentation/Chapter_5_Aligned_Chapter_4.docx`: most recently aligned implementation/testing/evaluation chapter, including Supabase Free/Ireland and daily scripted backups with restoration untested.
* `documentation/Chapter_6_Conclusions_Recommendations_and_Future_Work.docx` and `.md`: four-page conclusion/recommendations/future-work document covering the five objectives.

Earlier Chapter 5 variants remain: initial Markdown and DOCX implementation/evaluation drafts, `Chapter_5.docx`, `Chapter_5_Final_Revised.docx`, `Chapter_5_Hosted_Deployment.docx/.pdf`, and multiple render-QA directories. They preserve the revision history; they are not equally current. Text from the latest chapters is included in the full export, and other available versions are retained in the supporting text package.

Chapter 4 review identified inconsistent relationship/multiplicity explanations, architecture/sequence narrative issues, a missing wireframe section, insufficiently explicit requirements/traceability and omissions of newer passkey/retention behavior. Revision introduced clear FR/NFR/DR/IR identifiers, priority/source notation, objective mappings and C4-T01–C4-T27 scenarios, corrected explanatory writing and created ten interface wireframes.

Wireframes 4.7–4.16 cover authentication, personal details, document capture, live selfie, verification states, administrator directory, case review, audit export, passkey management and model evaluation. Editable SVGs, PNGs, a manifest and ZIP are stored. Original six design figures are preserved in the revision work directory. Wireframes are schematic design evidence, not necessarily screenshots of the newest landing page/theme. The full text extraction cannot preserve diagram geometry; use the original artifacts when redrawing or checking relationships.

The user preferred writing in the author's own voice and evidence explained directly in prose instead of artificial E1/E2 labels. Chapter 5 revisions preserved recorded results while adding hosted context, same-set model comparisons, limitations and amended test scenarios. The chapter records assistance from Claude for prompts and Codex for source/evidence inspection, documentation, selected tests and layout checks, with the author responsible for review/submission. Supervisor/institutional review was not established as completed.

## 17. Outstanding requirements and evidence gaps

The amended requirements are deliberately more extensive than the implemented/evaluated scope. Do not mark them complete merely because they appear in a requirements table.

| Area | Current documented gap |
|---|---|
| C4-T18 failure/readiness extension | No complete injected status/prediction delay/failure campaign, effective deployed timeout/deadline record or controlled cold/warm timing study |
| C4-T22 retention extension | Verified-only cleanup is implemented; 30-day non-verified/abandoned images, 180-day metadata, preservation exceptions and all extended access/deletion cases are not implemented/verified |
| C4-T24 recovery | User reports daily Google Drive database backups; no restoration performed; backup encryption, access, seven-day expiry, image exclusion and model/configuration coverage unverified |
| C4-T25 human check | No established accessible equivalent; restart and multiple-instance challenge behavior not demonstrated |
| C4-T26 origin/CORS | Backend mixes localhost defaults with configured origins; local Flask enables unrestricted CORS; full production separation/preflight/real-time checks untested |
| C4-T27 disclosure/consent | Amended pre-collection notice, applicable consent record/enforcement and withdrawal handling absent from reviewed source |
| Evaluation | No representative usability study, demographic fairness analysis, modern presentation-attack campaign, external adjudicated identity dataset or timed hosted workload benchmark |
| Operational provenance | Historical fallback causes and several effective cloud settings not established; latest deployed revision not checked for this export |

The proposed 30-day, 180-day and seven-day periods are project/institutional policy proposals, not stated statutory periods. No legal-compliance conclusion should be inferred from the existence of authentication, encryption facilities or retention code.

Chapter 6 prioritises human oversight, completion of informed collection/retention, verified recovery/production controls and gathering operational evidence before tuning resources. Proposed Verified outcomes also need oversight because many simulated cases needing review were classified Verified. Future research includes external full-pipeline validation, cost-aware review/calibration and periodic offline retraining, followed by longer usability/reliability studies. These are recommendations, not completed work.

## 18. Local setup and reproduction context

The root package supplies `install:all`, component install commands, `dev`, `dev:web`, component start/dev commands, frontend build and ngrok commands. `npm run dev` starts frontend, backend and local AI. `npm run dev:web` starts only the web components, useful when AI_SERVICE_URL points to Azure. Backend reads PORT and listens on 0.0.0.0; frontend deployment is a Vite build with output `dist`.

The README gives Supabase schema setup and component installation. Required configuration families include Supabase URL/public/service-role keys, AI_SERVICE_URL, VERITY_API_KEY for the remote deployment, FRONTEND_URL, SVM_TIMEOUT_MS, WebAuthn RP/origins/name, TRUST_PROXY, fraud settings and Flask/quality options. The source appendix lists referenced environment variable names without exporting secret values.

The model experiment uses its isolated requirements lock and `.venv-kyc`. Production computer-vision dependencies are separate and large. InsightFace downloads/cache and EasyOCR resources matter for startup; pretrained Silent-Face resources are bundled. Load only trusted model artifacts and deploy the matching complete model/scaler/manifest set. Do not retrain while serving from files being replaced.

For exact commands and reproducibility details consult the included current README, model README, v3 README, protocols and manifests. Old cloud-provider commands in chats describe historical execution; they should be checked before being reused as current hosting advice.

## 19. API inventory

All Express paths below use the indicated mount prefix; middleware restrictions are defined in source.

| Prefix | Endpoints |
|---|---|
| `/api/auth` | POST register, resend-verification, login, forgot-password, reset-password, logout, complete-profile; GET captcha, me |
| `/api/auth` passkeys | POST passkey/login/options, passkey/login/verify, passkey/register/options, passkey/register/verify; GET passkeys; PATCH/DELETE passkeys/:id |
| `/api/agent` | POST registration, documents/quality-check, documents; GET profile, registration/status, audit |
| `/api/verification` | POST initiate; GET status, result |
| `/api/admin` | GET stats, model/status, model/evaluation, activity/recent, fraud/flagged, audit/export, cases/pending, agents, agents/:agentID/images, agents/:agentID/audit, agents/:agentID, audit-logs; POST agents/:agentID/reset-strikes, agents/:agentID/approve, agents/:agentID/reject |
| Flask `/api/quality` | POST assess, assess-single |
| Flask `/api/ocr` | POST verify |
| Flask `/api/face` | POST verify |
| Flask `/api/liveness` | POST detect |
| Flask `/api/svm` | POST predict; GET status |
| Both services | GET /health |

## 20. Guidance for the next documentation chat

Use this export as project context, then follow the user's new chapter/task instructions. Preserve exact measured numbers, dates, dataset boundaries and denominators. Distinguish implemented local behavior, reported hosted operation, tested behavior, planned requirements and future work.

Use Verity for the current product, with Intelligent Agent Identity Verification System as the academic title and SalesMesh as the original context where relevant. Explain that pretrained image models produce evidence and the trained SVM combines six scores. Do not describe résumé scoring, compliance quizzes, Microsoft/Apple sign-in or government-ID validation as implemented.

Keep the known weak Manual Review recall and false-verification counts visible. Do not inflate the one-case v3 gain, reuse the old test as a matched baseline, equate local tests with production verification, or claim universal spoof detection/document authenticity. Keep fallback provenance separate. Keep the latest left/right-only challenge, camera-only retries and landing/theme changes distinct from the older chapter snapshots.

Write in the project author's voice where a dissertation section calls for it. Use traceable source descriptions and proper verified academic references; the old chat's citation placeholders are not usable bibliographic references. Do not invent survey participants, supervisor approval, benchmark reruns, fairness results, restoration success, cloud resource measurements or current production settings.

The supporting export preserves fuller source material so a documentation chat can investigate details beyond this handoff rather than guessing.
