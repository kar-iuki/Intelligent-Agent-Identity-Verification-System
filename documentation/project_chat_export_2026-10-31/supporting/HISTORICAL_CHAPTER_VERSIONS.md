# Other saved chapter versions

Historical variants are retained here for context. Prefer the current chapter snapshots and handoff for current documentation.


---

## Chapter_5.docx

CHAPTER 5

System Implementation Testing and Evaluation

Intelligent Agent Identity Verification System

5.1 Introduction

This chapter presents the implementation, testing and evaluation of the Intelligent Agent Identity Verification System. The system was developed to register agents, collect identity evidence, combine document and biometric scores, and support verification decisions and controlled access. The implementation comprised a Vue web interface, an Express application server, a Flask artificial intelligence service and a Supabase PostgreSQL database.

The chapter follows a hybrid software and machine learning structure. It explains the implemented modules and data flow, describes the synthetic dataset and model development procedure, and evaluates the recorded functional tests and classification results. The latest saved model, version 3.0.0, achieved 75.800% accuracy on 1,500 fresh synthetic cases. This result measured performance under the simulator assumptions and did not establish operational identity verification accuracy.

5.2 Implementation Environment

5.2.1 Hardware and deployment environment

The implementation was organised as a local web prototype connected to managed Supabase services. The documented development ports were 5173 for the interface, 3000 for Express and 5000 for Flask. Network access was required for Supabase and initial model downloads. The recorded experiment identified Python 3.13, but did not establish a minimum tested processor, memory, storage capacity or client-device specification. Consequently, hardware minimums and public deployment availability were not inferred from software configuration. The project README documented the local setup, while the machine learning README recorded the experiment environment.

Table 5.1 Implementation environment and evidence

Layer | Recorded configuration | Evidence and scope

Client | Browser with camera access | Capture components; no minimum device benchmark recorded.

Application services | Vue, Express and Flask; local development ports | README setup; no measured concurrent-user capacity.

Data services | Supabase authentication, PostgreSQL and storage | Schema and integration code; region and service tier not established.

AI execution | CPU-capable face and liveness inference | Model-loading code; no minimum hardware certification.

Experiment | Python 3.13; saved model v3.0.0 | ML README and artifact manifest; isolated offline experiment.



5.2.2 Software services and configuration

The interface used Vue and Vue Router to separate authentication, verification and administrator screens. Express coordinated authenticated requests and database operations. Python provided the image-processing and classification libraries. The package manifests recorded dependency ranges, whereas the experiment lock file and model manifest recorded exact versions for the saved model. These two forms of evidence were distinguished because a declared range does not prove which application package version was tested. These dependencies were documented in the frontend and backend package manifests, the AI service requirements file and the saved model manifest.

Table 5.2 Software dependencies and their roles

Component | Version evidence | Role

Vue / Vue Router | ^3.5.13 / ^4.5.0 | Interface and navigation

Vite | ^6.0.7 | Development server and frontend build

Express | ^4.21.2 | Application API and request handling

Supabase JavaScript client | ^2.49.1 | Authentication and data integration

SimpleWebAuthn | Server ^14.0.3; browser ^14.0.0 | Optional passkey authentication

Flask | 3.1.3 in model manifest | AI service endpoints

scikit-learn | 1.9.0 in model manifest | SVM, scaling and calibration

NumPy / SciPy | 2.5.3 / 1.18.1 in manifest | Numerical processing

OpenCV | >=4.8,<5 in requirements | Image preprocessing and quality metrics

EasyOCR / InsightFace | Unpinned in service requirements | Text extraction and face embeddings

PyTorch / Silent-Face | PyTorch unpinned; local model weights | Presentation-attack scoring



Backend configuration supplied the Supabase URL and keys, AI service URL, listening port and authentication-related settings. Service-role credentials remained server-side. Optional passkeys required the configured relying-party identifier and allowed origins; the project README specified Node.js 22 or newer for this feature. The README also retained an older general Node.js 18 prerequisite, so Node.js 22 or newer was the relevant documented requirement for the complete passkey-enabled application.

The full image-processing environment was distinct from the smaller locked machine learning experiment environment. The latter supported reproduction of the classifier experiment without downloading every OCR, face and anti-spoofing model. Unpinned production dependencies limited exact reproduction of the complete image pipeline. No container-based deployment was established by the evidence reviewed.

5.2.3 Deployment and reproducibility

A reproducible installation required the application source, authorised Supabase access, database scripts, dependency files and the complete saved model bundle. The following procedure describes the repository setup; it does not constitute evidence that a fresh deployment was executed during preparation of this chapter.

1. Obtain the project repository and record the source revision. Create a new Supabase project or use an authorised isolated test project. Apply database/schema.sql only to a fresh database; apply the relevant access-control, audit, date-of-birth, storage, row-level-security and optional passkey scripts according to their prerequisites.

2. Configure the backend and AI service environment files without publishing credentials. Supply the Supabase connection settings, AI service URL and frontend origin. Configure passkey relying-party settings when that feature is enabled.

3. Install backend and frontend packages from their respective package directories. Create a Python virtual environment and install ai-service/requirements.txt for the full AI service. Preserve compatible scikit-learn versions for the supplied model files.

4. Make the InsightFace models and Silent-Face weights available. Retain the complete ai-service/ml/models bundle and the supporting ml.decision_model module. Stop the serving process before replacing a model bundle, then restart it so startup validation can run.

5. Start the backend with npm run dev, the AI service with python app.py, and the frontend with npm run dev. Verify the backend and AI /health endpoints, then inspect /api/svm/status to confirm that the expected model version is loaded.

6. Run isolated tests before demonstrating a lawful sample registration, document capture, selfie capture and verification workflow. Check the resulting request, scores, decision basis and access record in the authorised test environment.

For model reproduction, ai-service/ml/requirements-experiment.lock.txt supplied the exact experiment dependencies. The v3 workflow was invoked through ai-service/ml/improve_model.py --jobs 3 --promote in the documented virtual environment. Reproduction belongs in an isolated copy because promotion changes the active model bundle. The runner refused to repeat a completed experiment against the same evaluation draw. Running the older train_model.py workflow could replace the bundle with v2 artifacts and was therefore not interchangeable with reproducing v3.

Health checks established service responsiveness only. They did not prove that authentication, database permissions, image inference and access enforcement all worked together. The recorded model promotion changed local artifacts; it did not demonstrate publication to a remote hosting service.

5.3 System Implementation

The implemented architecture separated presentation, application coordination, image analysis and persistence. This separation allowed the browser to guide capture while the backend managed protected operations and the AI service produced numerical evidence. The descriptions below trace implemented capabilities rather than assigning unverified Chapter 4 requirement numbers.

5.3.1 Database and data implementation

The relational schema represented users, agent profiles and verification attempts as separate entities. UUID primary keys identified records, while foreign keys linked an agent to a user and each request to an agent and document. Unique constraints on user email, agent user reference and national identity number limited duplicate account and profile records. Verification scores and decisions used unique request references so that each request had one associated score row and decision row. The database schema and accompanying SQL migration scripts defined these entities and constraints.

Table 5.3 Core database entities

Entity | Important contents | Relationship or purpose

users | user_id, email, role | Authentication-linked account and role

agents | agent_id, user_id, national_id | Profile linked uniquely to a user

documents | document_id, agent_id, file_url | Evidence references for an agent

verification_requests | request_id, document_id, status | Tracks a submitted verification

verification_scores | request_id and six scores | One score record per request

kyc_decisions | Decision, probabilities, basis, time | One outcome per request

access_control_records | agent_id, decision_id, access_granted | Records access enforcement

audit_logs | Action, outcome, actor, time, details | Traceable application events



Status values distinguished pending, verified, review and rejected requests. The decision enumeration excluded pending because it represented completed classification outcomes. The decision_basis field distinguished SVM classifications from placeholder threshold decisions. This distinction supported interpretation of stored outputs when model inference was unavailable.

Row-level security was enabled in the base schema, with policies supplied separately. Enabling row-level security alone did not demonstrate that every deployed policy was correct. The backend also validated bearer tokens through Supabase and checked roles before protected actions. Database configuration and server-side checks therefore formed separate parts of the access-control implementation.

The retention implementation removed stored identity images and selfies after three business days following the latest successful verification, while preserving decision and audit metadata. Business days were Monday to Friday in Africa/Nairobi, without public-holiday exclusions. Cleanup ran at startup and at fifteen-minute intervals, and failed storage removals were retried. This policy depended on the backend remaining active; it did not purge pending, review or rejected cases. The document-retention service and the README described this policy.

5.3.2 Application modules and verification workflow

Authentication and profile management supported agent registration, sign-in and completion of identity details. Authentication middleware rejected missing or invalid bearer tokens, and role middleware restricted administrator operations. Optional passkeys supplemented password and Google sign-in. The passkey implementation used WebAuthn credentials rather than storing a user’s fingerprint or other device biometric. The authentication and role middleware, together with the project README, documented these controls.

Document and selfie capture components guided evidence collection. The image-quality service calculated sharpness, brightness and contrast, while document preprocessing supported extraction. OCR compared extracted identity information with registered details. Face matching used InsightFace embeddings to compare a document portrait and selfie, and liveness scoring used Silent-Face anti-spoofing models. These produced evidence signals; neither text agreement nor facial similarity independently proved that a document was authentic.

The backend sent evidence to the quality, OCR, face and liveness endpoints and assembled six numerical features. The classifier returned Verified, Manual Review or Rejected, together with class probabilities and model provenance. Backend integration preserved the lowercase database values verified, review and rejected. Decision and access-control records connected the classification to the agent’s permitted workflow. Administrator screens supported inspection and human decision-making.

Table 5.4 Classifier feature contract

Feature | Unit or range | Interpretation

face_match_score | 0–100 | Face similarity score

liveness_score | 0–1 | Anti-spoofing score

ocr_confidence_score | 0–1 | Agreement with registered identity text

blur_score | Nonnegative raw value | Laplacian variance; higher means sharper

brightness_score | 0–255 | Mean HSV value-channel intensity

contrast_score | 0–127.5 | Grayscale standard deviation



Raw image-quality measurements were retained in their original units. MinMax scaling occurred within the model processing path; generic 0–1 quality ratings were not substituted for the expected raw metrics. Missing, non-finite, wrongly typed or out-of-range evidence was rejected rather than silently converted to zero.

5.3.3 Exception handling and decision provenance

At the AI endpoint, an unavailable or inconsistent model bundle produced an unavailable-service response. At application level, valid complete evidence could instead enter the existing threshold fallback when SVM inference failed. The fallback recorded placeholder_threshold and an audit reason; its zero-or-one outputs were rule outcomes rather than calibrated confidence. Therefore, model-only evaluation results did not measure the combined application, quality gates, fallback and human-review workflow.

5.3.4 Dataset description and preparation

The decision-model dataset contained 10,000 synthetic cases: 6,000 Verified, 2,000 Manual Review and 2,000 Rejected. Each training record contained the six numerical features and a class label. These class quotas were experimental assumptions rather than estimates of operational prevalence. No genuine identity records or invented participant data were required to describe the classifier experiment. The machine learning README, generation configuration and dataset metadata recorded the composition and assumptions of the dataset.

Local benchmark measurements informed parts of the generator. The recorded sources included 1,000 LFW face pairs, 1,200 NUAA presentations, 500 MIDV quality frames and MIDV OCR measurements. Stored measurement hashes and summary statistics were retained. The experiment read these measurements; it did not establish that the original source images had been reprocessed or that historical measurements had been independently verified. These datasets did not supply the final three-class KYC labels.

Face and liveness values were sampled from truncated distributions informed by recorded measurements. OCR and quality generation combined measured statistics with explicit simulation assumptions. Quality measurements used a multivariate distribution over transformed blur, brightness and contrast. Some unresolved and genuine scenarios deliberately shared observed distributions, representing information absent from the six features. Thus, labels represented assumed latent scenarios rather than a simple threshold applied to the observed scores.

Exact and near-duplicate checks preceded partitioning. Row identifiers and latent scenario descriptions were excluded from model predictors. Scaling and optional quality transformations were fitted within training folds, reducing leakage from validation and evaluation records. The duplicate checks screened close observations but did not prove that the simulated population represented real applicants. Dataset ownership, licence conditions and permission to redistribute original benchmark material required separate verification; the chapter makes no redistribution claim.

Table 5.5 Data partitions used in the v3 experiment

Partition | Cases | Function

Training | 7,000 | Model fitting and five-fold cross-validation

Calibration | 750 | Probability calibration only

Selection | 750 | Candidate and decision-policy selection

Original test | 1,500 | Retired from v3 model selection and fitting

Fresh evaluation | 1,500 | Frozen candidate and incumbent comparison



Calibration and selection each contained 450 Verified, 150 Manual Review and 150 Rejected cases. The fresh evaluation contained 900, 300 and 300 respectively. A new draw was generated after candidate selection was frozen, and duplicate checks covered all 11,500 original and fresh records. The original test set was retired because previous results had informed the new research questions.

5.3.5 Model training selection and packaging

An RBF support vector machine was used to combine the six features into a three-class decision. Training compared C values of 0.1, 1, 10 and 100, with gamma values of 0.001, 0.01, 0.1, 1, scale and auto. Five-fold shuffled stratified cross-validation used macro F1, balanced class weights and seed 42. This produced 24 parameter combinations per grid. Preprocessing remained inside the cross-validation pipeline. The training scripts and frozen experiment protocol recorded the parameter grid and cross-validation procedure.

The v3 experiment compared raw and transformed quality inputs, native multiclass and explicit one-versus-rest SVM variants, and sigmoid, isotonic and temperature calibration. Three additional grids were fitted, while the prior raw-native winner was reused with provenance. Calibration used only the calibration partition. Candidate selection used the separate selection partition and imposed safeguards on macro F1, review recall and both false-verification counts relative to the comparable calibration baseline.

The selected configuration was raw_native_sigmoid, with C = 10 and gamma = scale. Its recorded training cross-validation macro F1 was 0.672766. Its probability policy used a review multiplier of 1.0, verification threshold of 0.0 and verification margin of 0.0. These settings did not provide an additional conservative verification threshold beyond the selected probability policy.

The release gate required strictly higher fresh-set accuracy, non-decreasing macro F1 and no increase in either Rejected-to-Verified or Manual-Review-to-Verified errors relative to the saved v2 incumbent on the same fresh records. The selected candidate passed this recorded gate and was promoted to the local version 3.0.0 bundle. Passing the gate established the specified comparative condition; it did not establish an acceptable operational false-approval rate.

The model manifest recorded the feature order, class names, library versions and artifact hashes. The service validated the model bundle at startup and mapped class probabilities using the model’s class labels rather than assuming a fixed column order. Saved model, scaler and supporting code were required together for reproduction. The model remained static during service operation; completed verification attempts did not trigger online learning. The artifact manifest and SVM service implementation documented these loading and prediction checks.

5.4 Testing and Evaluation

5.4.1 Test strategy and acceptance criteria

The recorded evaluation combined isolated classifier-contract tests, experiment-integrity checks, backend decision tests and a held-out synthetic model comparison. Functional assertions checked valid outputs, invalid inputs, model unavailability and preservation of decision provenance. The experiment assessed accuracy, macro and weighted F1, class-specific precision and recall, calibration and consequential misclassification counts. Existing logs are reported as recorded evidence, not as tests freshly rerun for this chapter.

End-to-end live database behaviour, target-device compatibility, user acceptance, accessibility, throughput and recovery required separate evidence. Source code and isolated passing tests were not treated as substitutes for those evaluations.

5.4.2 Functional test cases and recorded results

Table 5.6 links representative test scenarios to implemented capabilities. The test identifiers organise this chapter and are not asserted to be the approved Chapter 4 requirement identifiers. Expected outcomes come from test assertions, while observed verdicts come from the saved v3 verification log. The saved verification_checks.json file in the v3 experiment directory contained the suite outputs and exit codes.

Table 5.6 Functional test cases and results

ID and scope | Scenario and expected result | Recorded result

TC01 Input validation | Submit missing, malformed, non-finite and out-of-range values; reject them. | Pass: SVM contract validation test.

TC02 Output mapping | Vary class order; map each probability to its class label. | Pass: class-order test.

TC03 Model consistency | Compare saved artifact and API predictions; retain legacy API fields. | Pass: artifact parity and legacy-contract test.

TC04 Availability | Make the model unavailable; do not invent an AI-service prediction. | Pass: unavailable-model contract test.

TC05 Dataset integrity | Regenerate saved data and inspect predictors; preserve reproducibility and exclude hidden predictors. | Pass: dataset integrity test.

TC06 Leakage control | Inspect split manifest and scaler fitting; fit preprocessing on training data. | Pass: partition and scaler test.

TC07 Decision policy | Apply review policy; preserve original returned probabilities. | Pass: saved-policy and improvement tests.

TC08 Backend validation | Supply incomplete scores; fail before inference or threshold fallback. | Pass: backend decision test.

TC09 Persistence contract | Return a model prediction; preserve database enums and decision basis. | Pass: backend decision test.



Table 5.7 Recorded suite totals

Suite | Tests | Result

test_svm.py | 6 | 6 passed

test_kyc_experiment.py | 2 | 2 passed

test_kyc_improvement.py | 4 | 4 passed

backend/tests/kycDecision.test.js | 2 | 2 passed

Total in saved v3 log | 14 | 14 passed; zero recorded failures



These totals describe one retained verification log. They do not cover every test file in the repository or certify current uncommitted interface changes. No complete defect register and chronological retest record accompanied these results; consequently, no defect-resolution counts were inferred. Live registration, capture, administrator review and access enforcement remained outside the conclusions supported by this isolated log.

5.4.3 Model evaluation results

Both the saved v2 incumbent and selected v3 model were evaluated on the same 1,500 fresh synthetic cases. Using a common evaluation set avoided presenting the older v2 result from a different sample as a direct before-and-after comparison. The v3 experiment summary and improvement report contained the metrics presented in Tables 5.8–5.10.

Table 5.8 Model comparison on the same fresh evaluation set

Metric | Saved v2 | Selected v3

Accuracy | 75.733% | 75.800%

Macro F1 | 0.651909 | 0.654082

Weighted F1 | 0.730391 | 0.731979

Rejected predicted Verified | 44 | 43

Manual Review predicted Verified | 186 | 184

Log loss | 0.660123 | 0.659596

Multiclass Brier score | 0.373659 | 0.373110



The accuracy difference was 0.067 percentage points, equivalent to one additional correct decision. The paired-bootstrap 95% interval for the accuracy difference extended from −0.133 to +0.333 percentage points. The macro F1 difference was 0.002173, with an interval from −0.001051 to +0.006855. Both intervals included zero, so the results did not establish a statistically conclusive improvement. They described uncertainty for the fitted models under the same simulator, not across real-world populations or all possible training runs.

Table 5.9 Selected v3 confusion matrix

Actual class | Predicted Verified | Predicted Review | Predicted Rejected

Verified | 831 | 15 | 54

Manual Review | 184 | 82 | 34

Rejected | 43 | 33 | 224



Table 5.10 Selected v3 class-specific performance

Class | Precision | Recall | F1

Verified | 0.785444 | 0.923333 | 0.848825

Manual Review | 0.630769 | 0.273333 | 0.381395

Rejected | 0.717949 | 0.746667 | 0.732026



The weakest class was Manual Review: only 82 of 300 cases were retained for review, while 184 were verified. In addition, 43 of 300 rejected cases were verified. Combining these errors gave 227 false verifications among 600 non-Verified cases, or 37.83%. Of all 1,058 predicted verifications, 227 were incorrect under the synthetic labels, or 21.46%. These derived rates have different denominators and should not be confused with the 24.20% overall classification error.

5.4.4 Error analysis and interpretation

The class imbalance and overlapping scenarios helped explain why accuracy alone overstated useful review performance. Verified cases represented 60% of the fresh sample and had high recall, whereas review cases frequently resembled verified cases in the observed feature space. The simulator deliberately included indistinguishable components with different latent labels. The stored identifiability analysis attributed a minimum eight-percentage-point population error contribution to those components, with further overlap potentially adding error. This was a property of the simulation, not an estimated limit for real identity verification.

Table 5.11 Permutation importance for the selected model

Feature | Macro F1 decrease | Repeat standard deviation

Liveness | 0.201380 | 0.008477

Face match | 0.110442 | 0.005995

OCR agreement | 0.049802 | 0.007588

Blur | 0.003831 | 0.003357

Brightness | −0.000359 | 0.003924

Contrast | −0.003439 | 0.003605



Liveness and face matching had the strongest measured influence on classification under permutation. OCR provided additional information, while brightness and contrast showed negligible or slightly negative average importance. Negative values meant that shuffling slightly improved the measured score in that experiment; they did not prove that image quality was useless. Quality also affected capture and extraction before the classifier, and correlated features could mask one another’s contribution. The saved permutation-importance results recorded the mean changes and variation across repeats.

Log loss and Brier score improved slightly, but probability calibration remained conditional on the simulated class mixture. A score interpreted as confidence under a 60/20/20 synthetic distribution was not automatically a trustworthy probability for a different applicant population. Errors that grant access to a non-Verified case also carried a different operational consequence from errors that direct a genuine applicant to review. The evaluation therefore retained the two false-verification counts alongside aggregate metrics.

5.5 Version Control and Implementation Evidence

Project repository

The repository contained separate frontend, backend, AI-service and database directories, setup instructions, dependency files, SQL scripts, tests and saved experiment reports. Recent history included commits 1119c41, describing OCR changes, and 9d0fe2c, describing README work; the inspected HEAD was 870b303. Some current interface and passkey changes were uncommitted, so that commit alone did not identify every file described in the working implementation.

Legacy model artifacts were retained separately from the active v3 bundle, supporting comparison and rollback. Generic commit messages limited the explanatory value of parts of the history. Branch reviews, issue tracking, release tags, repository licensing and supervisor access were not established by the inspected evidence and were not claimed as completed practices.

5.6 Author Oversight and Use of AI Assisted Tools

OpenAI Codex assisted with preparation of this chapter by inspecting the project source, organising the supplied Chapter 5 guidelines, and drafting descriptions and tables from saved implementation and evaluation evidence. The draft distinguished recorded results from unverified deployment and user-evaluation claims. The student remains responsible for checking the chapter against the approved objectives, confirming the evidence and citations, and approving the final submission. This declaration does not assert that student or supervisor review has already occurred.

5.7 Evaluation Discussion and Limitations

5.7.1 Assessment of implemented capabilities

The implementation supported an integrated evidence-processing architecture: agents could be represented in the database, document and selfie components supplied inputs, separate services produced six scores, and decision outputs carried model or fallback provenance. The saved contract and backend tests supported correctness of selected interfaces and invalid-input handling. They did not establish that the complete live workflow met every approved requirement.

For automated classification, the available evidence supported a narrower finding: v3 achieved 75.800% accuracy and 0.654082 macro F1 on the declared fresh synthetic sample and passed its comparative release gate. The small improvement over v2 was inconclusive, while low review recall and 227 false verifications showed that the gate did not establish safe autonomous approval. Human-review facilities were implemented, but the experiment did not measure whether human reviewers corrected those errors.

For traceability and access control, linked score, decision, access and audit records provided an implemented basis for reconstructing verification actions. Role checks, token validation and retention logic added controls. Their presence did not establish resistance to every attack, complete privacy compliance or successful recovery under failures. A full-system acceptance verdict could not be derived from the recorded model and contract tests alone.

5.7.2 Limitations affecting the findings

Data validity was the main limitation. Synthetic adjudication labels, fixed class quotas and assumed score relationships constrained generalisation. The fresh sample came from the same simulator rather than independent real applicants. Historical benchmark measurements were reused, and changes to the current image pipeline could create mismatch between measured source distributions and deployed scores.

Evaluation coverage was also limited. No demographic fairness study, modern presentation-attack campaign, target-camera comparison, prospective pilot, participant-based usability study or measured end-to-end latency and throughput result was established. Minimum hardware, cloud capacity and long-duration reliability were therefore unresolved. The small calibration and selection partitions also left a risk of overfitting candidate policies.

Finally, classifier metrics excluded application quality gates, threshold fallback and administrator intervention. Unpinned dependencies and uncommitted changes limited exact reproduction of the complete system. The evidence supported a functioning implementation structure and a reproducible synthetic classifier experiment, while the extent of real-world effectiveness remained unestablished. Final conclusions, recommendations and future work belong in Chapter 6.


---

## Chapter_5_Final_Revised.docx

Chapter 5: System Implementation, Testing and Evaluation

Intelligent Agent Identity Verification System

5.1 Introduction

This chapter explains how the design approved in Chapter 4 was implemented, the environment in which it ran, and how it was tested and evaluated. The system registers agents, collects identity evidence, combines document and biometric scores, and supports verification decisions and controlled access. It was implemented as a Vue web interface, an Express application server, a Flask artificial intelligence service and a Supabase PostgreSQL database.

The chapter follows a hybrid software and machine learning structure. Sections 5.2 and 5.3 describe the environment, the deviations from the approved design, the implemented modules and workflow, and the dataset and model development procedure. Section 5.4 reports the tests and classification results, Section 5.5 describes the version-control evidence, Section 5.6 declares the AI-assisted tools used, and Section 5.7 discusses the results against the project objectives and states the limitations. The latest saved model, version 3.0.0, achieved 75.800% accuracy on 1,500 fresh synthetic cases. This result was measured under the simulator assumptions described in Section 5.3.6 and does not represent operational identity verification accuracy.

5.2 Implementation Environment

5.2.1 Hardware and Deployment Environment

The system was implemented as a web prototype connected to Supabase on the Free plan. The documented local interface, application server and AI service used ports 5173, 3000 and 5000. At the time of this report, deployment of the AI service to Microsoft Azure was in progress; completed Azure hosting was not claimed. Table 5.1 records the current development equipment and the confirmed service configuration. These are observed configurations, not measured minimum requirements.

Table 5.1: Implementation environment and evidence

Layer | Configuration | Evidence

Development machine | AMD Ryzen 5 5625U with Radeon Graphics; 7.4 GiB OS-reported usable memory; C: volume 475.8 GiB; Windows 11 Home Single Language, version 10.0.26200 | Host inventory on 23 October 2026; current development machine, not a benchmarked minimum

Client browser | Camera-capable browser required; historically tested browser names and versions were not recorded | No browser-compatibility verdict established

Application services | Vue (port 5173), Express (port 3000) and Flask (port 5000) on the development machine | Project README

AI service hosting | Local Flask configuration, port 5000; Microsoft Azure deployment in progress | Project configuration and author confirmation; no completed Azure deployment claimed

Data services | Supabase Free plan: authentication, PostgreSQL and storage; region not recorded | Author confirmation, SQL scripts and supplied database exports

Model experiment | Python 3.13, locked dependencies, saved model version 3.0.0 | ML README, requirements lock file, model manifest



5.2.2 Software, Services and Configuration

Vue and Vue Router separated the authentication, verification and administrator screens. Express coordinated authenticated requests and database operations, and Python supplied the image-processing and classification libraries. Table 5.2 lists the dependencies. The package manifests declare version ranges, whereas the model manifest records the exact versions used to produce the saved model.

Table 5.2: Software dependencies and their roles

Component | Version evidence | Role

Vue / Vue Router | ^3.5.13 / ^4.5.0 | Interface and navigation

Vite | ^6.0.7 | Development server and frontend build

Express | ^4.21.2 | Application API and request handling

Supabase JavaScript client | ^2.49.1 | Authentication and data integration

SimpleWebAuthn | Server ^14.0.3; browser ^14.0.0 | Optional passkey authentication

Flask | 3.1.3 (model manifest) | AI service endpoints

scikit-learn | 1.9.0 (model manifest) | SVM, scaling and calibration (Pedregosa et al., 2011)

NumPy / SciPy | 2.5.3 / 1.18.1 (model manifest) | Numerical processing

OpenCV | >=4.8,<5 (requirements file) | Image preprocessing and quality metrics

EasyOCR / InsightFace | Unpinned in requirements file | Text extraction and face embeddings

PyTorch / Silent-Face | PyTorch unpinned; local model weights | Presentation-attack scoring



Backend configuration supplied the Supabase URL and keys, the AI service URL, the listening port and authentication settings. Service-role credentials remained server-side. Optional passkeys required a configured relying-party identifier, allowed origins and Node.js 22 or newer. The isolated classifier environment used Python 3.13.3, scikit-learn 1.9.0, NumPy 2.5.3 and Flask 3.1.3, verified during the 23 October 2026 test run. The full image-processing requirements left EasyOCR, InsightFace and PyTorch unpinned. Those packages were not installed in the inspected general Python environment, so their historically tested versions could not be established. The intended cloud host was Microsoft Azure, with deployment still in progress. An Azure service tier, region and completed deployment endpoint were not established.

5.2.3 Deployment and Reproducibility

The procedure below describes how the repository is installed, configured and verified.

Obtain the repository and record the source revision. Create a Supabase project, or use an isolated test project. Apply database/schema.sql to a fresh database, then the access-control, audit, date-of-birth, storage, row-level-security and optional passkey scripts in prerequisite order.

Configure the backend and AI service environment files without publishing credentials. Supply the Supabase connection settings, the AI service URL and the frontend origin, and the passkey relying-party settings when passkeys are enabled.

Install the backend and frontend packages from their package directories. Create a Python virtual environment and install ai-service/requirements.txt. Keep the scikit-learn version compatible with the supplied model files.

Make the InsightFace models and Silent-Face weights available, and keep the complete ai-service/ml/models bundle together with the supporting ml.decision_model module.

Start the backend with npm run dev, the AI service with python app.py and the frontend with npm run dev. Check the /health endpoints of the backend and AI service, then call /api/svm/status to confirm that model version 3.0.0 is loaded.

Run the isolated tests, then perform a registration with lawful sample data: document capture, selfie capture and verification. Check the request, scores, decision basis and access record in the test database.

The classifier reproduction procedure used ai-service/ml/requirements-experiment.lock.txt and ai-service/ml/improve_model.py with --jobs 3 and --promote. Reproduction requires an isolated copy because promotion replaces the active model bundle, and the runner refuses to repeat a completed experiment on the same evaluation draw. The older train_model.py script produces version 2 artifacts and is not interchangeable with the version 3 workflow. The model was not retrained for this documentation update. Health endpoints provide service-responsiveness checks. Separate live-test evidence was supplied as exports of verification requests, scores and decisions; the observed results are summarised in Table 5.10.

5.3 System Implementation

The implemented architecture separated presentation, application coordination, image analysis and persistence. The browser guided evidence capture, the Express server managed protected operations, and the Flask service produced the numerical evidence used for classification. The subsections below follow this architecture and the Chapter 4 design.

5.3.1 Deviations from the Approved Design

Table 5.3 compares the design choices stated in the project draft with the inspected implementation. The implementation column is supported by code and experiment records; the approved Chapters 3 and 4 were not independently revalidated during this update.

Table 5.3: Deviations from the approved design

Area | Approved design | Implemented | Reason

Training dataset | 4,000 records split 70/15/15 | 10,000 cases in training, calibration, selection and original-test partitions, plus a separate 1,500-case fresh evaluation set | Separate calibration and selection partitions prevented tuning on evaluation data; the original test set was retired once its results had informed model changes

Liveness benchmark | NUAA and Replay-Attack | NUAA only | Only NUAA measurements were recorded; the reason for omitting Replay-Attack was not independently established

Label generation | Labels from literature-based thresholds | Labels from latent scenarios with deliberately overlapping feature distributions | Some uncertainty in real verification is not visible in the six scores, so the classes were not made trivially separable

Model comparison | SVM compared with a Decision Tree | Saved v2 and v3 SVMs and Decision Tree evaluated on the same fresh set; existing threshold rules added as an offline descriptive baseline | A release gate was needed before promoting an improved model

Probability output | Class probabilities from the SVM | Sigmoid-calibrated probabilities fitted on a calibration partition | To report more reliable class probabilities

Authentication | Email and password, and Google sign-in | Optional passkey (WebAuthn) sign-in added | Faster sign-in on capable devices without storing biometric data

Identity images | Private storage with time-limited signed URLs | Images deleted three business days after the latest successful verification | Data minimisation



5.3.2 Database Implementation

The relational schema represented users, agent profiles and verification attempts as separate entities. UUID primary keys identified records, and foreign keys linked each agent to a user and each request to an agent and document. Unique constraints on user email, the agent-to-user reference and the national identity number limited duplicate accounts and profiles. Verification scores and decisions used unique request references so that each request had at most one score row and one decision row. Table 5.4 summarises the core entities. The implemented schema uses snake_case attribute names. Foreign keys and unique constraints define relationships, but successful processing is needed to create the corresponding score and decision records.

Table 5.4: Core database entities

Entity | Important contents | Purpose

users | user_id, email, role | Authentication-linked account and role

agents | agent_id, user_id, national_id | Profile linked uniquely to a user

documents | document_id, agent_id, file_url | Evidence references for an agent

verification_requests | request_id, document_id, status | Tracks a submitted verification

verification_scores | request_id and six scores | One score record per request

kyc_decisions | decision, probabilities, basis, time | One outcome per request

access_control_records | agent_id, decision_id, access_granted | Records access enforcement

audit_logs | action, outcome, actor, time, details | Traceable application events

passkeys (optional) | credential_id, public_key, counter, label, device and transport metadata | Passkey sign-in



Request status values distinguished pending, verified, review and rejected requests. The decision enumeration excluded pending because it represents completed classifications. The decision_basis field distinguished SVM classifications from placeholder threshold decisions, which allowed stored outputs to be interpreted correctly when model inference was unavailable. Row-level security was enabled in the base schema with policies supplied in separate scripts, and the backend independently validated bearer tokens through Supabase and checked roles before protected actions.

The retention implementation removed stored identity images and selfies three business days after the latest successful verification while preserving decision and audit metadata. Business days were Monday to Friday in the Africa/Nairobi time zone, without public-holiday exclusions. The cleanup job ran at startup and every fifteen minutes, and failed storage removals were retried. The job did not purge pending, review or rejected cases, a limitation discussed in Section 5.7.3.

5.3.3 Application Modules

Authentication, roles and passkeys. Authentication middleware rejected missing or invalid bearer tokens, and role middleware restricted administrator operations. Email/password and Google sign-in were supplemented by WebAuthn passkeys using SimpleWebAuthn. The public.passkeys table stored the credential identifier, public key, signature counter, transports, device type, backup status, label and device metadata; the application did not receive device fingerprint or face templates from WebAuthn. Challenge and rate-limit records were stored separately. Client support detection controlled which passkey actions were offered.

Registration and evidence capture. Agents entered personal details and supplied document and selfie images through the capture interface. Server upload middleware accepted JPEG and PNG MIME types and imposed a 5 MiB limit per file, returning a validation message for unsupported or oversized files. Registration logic checked existing national identity numbers. The storage integration used a private Supabase bucket; its deployed access settings were not live-tested in this update.

Verification pipeline. Four services produced the evidence signals. The quality service computed sharpness as Laplacian variance, brightness as the mean HSV value channel and contrast as the grayscale standard deviation, and images below the configured thresholds were rejected with specific messages before further processing. The OCR service compared the extracted name, identity number and date of birth with the registered details. Face matching compared document-portrait and selfie embeddings generated with the ArcFace implementation in InsightFace (Deng et al., 2019), and liveness scoring used the Silent-Face anti-spoofing models. These were evidence signals: neither text agreement nor facial similarity alone proved that a document was authentic.

The backend sent the evidence to the quality, OCR, face and liveness endpoints and assembled six numerical features, defined in Table 5.5. Raw image-quality measurements were kept in their original units, and MinMax scaling was applied inside the model processing path. Missing, non-finite, wrongly typed or out-of-range evidence was rejected rather than converted to zero.

Table 5.5: Classifier feature contract

Feature | Unit or range | Interpretation

face_match_score | 0 to 100 | Face similarity score

liveness_score | 0 to 1 | Anti-spoofing score

ocr_confidence_score | 0 to 1 | Agreement with registered identity text

blur_score | Non-negative raw value | Laplacian variance; higher means sharper

brightness_score | 0 to 255 | Mean HSV value-channel intensity

contrast_score | 0 to 127.5 | Grayscale standard deviation



Decision and access control. The classifier returned Verified, Manual Review or Rejected with class probabilities and model provenance. The backend preserved the lowercase database values verified, review and rejected, and the decision and access-control records connected each classification to the agent's permitted workflow.

Administrator review. The administrator controller implemented approval and rejection, updated the associated decision, request status and access record, and recorded the acting administrator. Dashboard endpoints returned totals by verification status and daily counts. Image viewing used signed URLs, normally valid for up to one hour and further limited by the remaining audit window for verified cases. The realtime service emitted new_review_case notifications through Socket.IO. These behaviours were confirmed from source code; a live administrator demonstration was not recorded in this update.

Registration-time guardrails. Middleware checked duplicate national identity numbers, blocked disposable email domains, and counts of guardrail events and failed verification initiations from an IP address or device fingerprint. The defaults allowed three counted events in a 24-hour lookback window, with environment variables able to override these values. Duplicate identities produced a conflict response and attempt limits produced a rate-limit response with retry information. These are configured rules, not measured attack-detection rates.

Audit logging. A central logging utility recorded standardised actions and outcomes for registration, each pipeline step, classification decisions, administrator actions, guardrail triggers and passkey events, with the actor and a timestamp.

5.3.4 End-to-End User Workflow

The implemented workflow connected the following interface, application and database operations. The sequence describes code paths; the live execution status is reported separately in Table 5.10.

The agent signed up or signed in. The backend validated the token and role, and the guardrail middleware checked the national identity number, the email domain and recent failed attempts.

The agent entered personal details, which were stored in the agents table and linked to the user record.

The agent uploaded the identity document and captured a selfie. Format and size were validated in the browser and on the server, and the files were stored in the private bucket with a documents record.

The backend sent both images to the quality service. A failed check returned specific reasons, such as an image being too blurry or too dark, and asked the agent to resubmit.

Images that passed went through OCR, face matching and liveness scoring, and the six scores were stored in verification_scores.

The classifier returned a class and probabilities. The backend stored the decision with its decision_basis and wrote the access_control_records entry.

The agent saw the outcome. Manual Review cases appeared in the administrator queue, where an approval or rejection updated the decision and access records.

Each step wrote an audit_logs entry, so the sequence could be reconstructed for any request.

The supplied live-test evidence consisted of database exports rather than interface screenshots. Their aggregate results are reported in Table 5.10. Personal identifiers and image links are omitted from the chapter. Figures 5.1 and 5.2 show the separate recorded model evaluation.

5.3.5 Exception Handling and Decision Provenance

At the AI endpoint, an unavailable or inconsistent model bundle produced an unavailable-service response. At application level, valid complete evidence could instead enter the existing threshold fallback when SVM inference failed. The fallback recorded placeholder_threshold and an audit reason, and its zero-or-one outputs were rule outcomes and not calibrated confidence. The model-only results in Section 5.4.3 therefore did not measure the combined application, which also includes the quality gates, the fallback and the human-review workflow.

5.3.6 Dataset Description and Preparation

The decision-model dataset contained 10,000 synthetic cases: 6,000 Verified, 2,000 Manual Review and 2,000 Rejected. Each record held the six features in Table 5.5 and a class label. The class quotas were experimental assumptions and not estimates of operational prevalence. No genuine identity records were used because real agent data raises privacy and consent concerns.

The generator reused stored benchmark measurements: 1,000 LFW face pairs, 1,200 NUAA presentations and 500 MIDV quality frames together with MIDV OCR measurements. The machine learning README and dataset metadata recorded summary statistics and file hashes. These historical measurements informed score distributions; the source images were not reprocessed during the version 3 experiment or this documentation update. None of the benchmark sources supplied the three-class KYC labels.

Face and liveness values were sampled from truncated distributions informed by the recorded measurements. OCR and image-quality values combined measured statistics with explicit simulation assumptions, and quality used a multivariate distribution over transformed blur, brightness and contrast. Some unresolved and genuine scenarios deliberately shared observed distributions to represent information that is absent from the six features. The labels therefore reflected assumed latent scenarios and not a threshold applied to the observed scores.

Exact and near-duplicate checks were run before partitioning. Row identifiers and latent scenario descriptions were excluded from the predictors, and scaling and optional quality transformations were fitted within training folds to avoid leakage. These checks screened close observations but could not show that the simulated population represents real applicants. The licence and redistribution terms of the benchmark datasets were not assessed here, and no redistribution claim is made.

Table 5.6: Data partitions used in the version 3 experiment

Partition | Cases | Function

Training | 7,000 | Model fitting and five-fold cross-validation

Calibration | 750 | Probability calibration only

Selection | 750 | Candidate and decision-policy selection

Original test | 1,500 | Retired from version 3 selection and fitting

Fresh evaluation | 1,500 | Frozen comparison of the candidate and the incumbent



The calibration and selection partitions each contained 450 Verified, 150 Manual Review and 150 Rejected cases, and the fresh evaluation set contained 900, 300 and 300 respectively. The fresh set was drawn after candidate selection was frozen, and duplicate checks covered all 11,500 original and fresh records. The original test set was retired because earlier results on it had informed the new research questions.

5.3.7 Model Training, Selection and Packaging

An RBF support vector machine combined the six features into a three-class decision (Pedregosa et al., 2011). Training compared C values of 0.1, 1, 10 and 100 with gamma values of 0.001, 0.01, 0.1, 1, scale and auto, giving 24 combinations per grid. Five-fold shuffled stratified cross-validation used macro F1 as the score, balanced class weights and seed 42, and preprocessing stayed inside the cross-validation pipeline.

For each parameter combination, the 7,000 training cases were divided into five stratified folds of approximately 1,400 cases. A fresh SVM was fitted on four folds (approximately 5,600 cases) and assessed on the remaining fold; the held-out fold changed across five rounds. Macro F1 was averaged across the five validation results. The 24 combinations therefore required 120 fold-level fits per grid, followed by refitting the selected configuration on all 7,000 training cases. Scaling was fitted only on the training portion of each fold. The calibration, selection and fresh evaluation cases were excluded from this cross-validation process.

The version 3 experiment compared raw and transformed quality inputs, native multiclass and explicit one-versus-rest SVM variants, and sigmoid, isotonic and temperature calibration. Three additional grids were fitted, and the earlier raw-native winner was reused with its provenance recorded. Calibration used only the calibration partition. Candidate selection used the separate selection partition and applied safeguards on macro F1, review recall and both false-verification counts relative to the comparable calibration baseline.

The selected configuration was raw_native_sigmoid with C = 10 and gamma = scale, and its training cross-validation macro F1 was 0.672766. Its probability policy used a review multiplier of 1.0, a verification threshold of 0.0 and a verification margin of 0.0, so no extra conservative verification threshold was applied beyond the selected policy.

The release gate required strictly higher accuracy on the fresh set, non-decreasing macro F1, and no increase in either Rejected-to-Verified or Manual-Review-to-Verified errors relative to the saved version 2 incumbent on the same fresh records. The selected candidate passed the gate and was promoted to the local version 3.0.0 bundle. Passing the gate met the specified comparison; it did not establish an acceptable operational false-approval rate.

The model manifest recorded the feature order, class names, library versions and artifact hashes. The service validated the bundle at startup and mapped probabilities using the model's class labels. The saved model, scaler and supporting code are required together. The model stayed static during operation, so completed verifications did not trigger online learning, and legacy artifacts were kept separately to allow comparison and rollback.

Table 5.7: Model version history

Version | Main change | Result on its evaluation set

Version 1 | 4,000-row synthetic generator with largely separable class ranges; earlier scaler/CV methodology | 100.000% accuracy and macro F1 1.000000 on 600 historical test cases; artificially easy separation limits interpretation

Version 2 | 10,000 scenarios with overlap, fold-local scaling, training-only tuning and held-out calibration | 74.333% accuracy and macro F1 0.621383 on its original 1,500-case test set

Version 3.0.0 | Calibrated raw-input SVM, C = 10, gamma = scale | 75.800% accuracy, macro F1 0.654082 on the fresh set



Results for versions 1 and 2 came from earlier evaluation sets and are not directly comparable with version 3. The like-for-like comparison of version 2 and version 3 on the same fresh records is in Table 5.11.

5.4 Testing and Evaluation

5.4.1 Test Strategy and Acceptance Criteria

Automated testing covered classifier contracts, experiment integrity, backend decisions, retention and passkey controls. The three Python suites used unittest from Python 3.13.3; backend suites used Node.js 24.19.0 and its built-in node:test runner. Tests used synthetic features, test credentials, mocks and an embedded PostgreSQL database for the passkey migration. The recorded version 3 log contained 14 passing tests. On 23 October 2026, those tests were rerun and the scope was expanded as summarised in Table 5.9. Three Supabase exports additionally documented live request, score and decision records. These observations were assessed separately from automated assertions and did not establish participant-based usability. Requirement identifiers in Table 5.8 are retained from the supplied draft.

The classifier was evaluated with accuracy, macro and weighted F1, class-specific precision and recall, log loss, the multiclass Brier score and the counts of non-Verified cases predicted as Verified, because those errors give access to agents who should not receive it.

5.4.2 Functional Test Cases and Results

Table 5.8 summarises representative automated test cases. All nine scenarios were covered by the saved version 3 test log and the successful rerun on 23 October 2026. Each pass required the executable assertions to agree with the expected outcome, rather than a manual judgement that the interface appeared to work.

Table 5.8: Isolated test cases and results

ID | Traceability | Scenario and expected result | Result

TC01 | FR-13, NFR-10 | Missing, malformed, non-finite and out-of-range values are rejected | Pass

TC02 | FR-13 | With the class order varied, each probability maps to its class label | Pass

TC03 | FR-13, NFR-13 | Saved artifact and API predictions agree, and legacy API fields are retained | Pass

TC04 | NFR-09 | With the model unavailable, no AI-service prediction is invented | Pass

TC05 | Data requirements (4.2.3) | Regenerated data are reproducible and hidden predictors are excluded | Pass

TC06 | Data requirements (4.2.3) | Split manifest and scaler show preprocessing fitted on training data only | Pass

TC07 | FR-13, FR-15 | The review policy is applied and original probabilities are preserved | Pass

TC08 | FR-12, FR-13, NFR-10 | Incomplete scores fail before inference or threshold fallback | Pass

TC09 | FR-14 to FR-16, FR-24, NFR-13 | A model prediction preserves database enums and the decision basis | Pass



Table 5.9: Recorded suite totals

Suite | Tests | Result

test_svm.py | 6 | 6 passed

test_kyc_experiment.py | 2 | 2 passed

test_kyc_improvement.py | 4 | 4 passed

kycDecision.test.js | 2 | 2 passed

documentRetention.test.js | 5 | 5 passed

passkeys.test.js | 9 | 9 passed

passkeyRoutes.test.js | 1 | 1 passed

passkeyDatabase.test.js | 1 | 1 passed

Frontend unit tests (Vitest 5.0.3) | 16 | 16 passed

Expanded run total | 46 | 46 passed; no assertion failures in completed suites



The expanded run on 23 October 2026 passed 46 automated tests, as shown in Table 5.9. Python used unittest in .venv-kyc; backend tests used node:test, with PGlite for the passkey migration and mocks for storage and session boundaries. Frontend tests used Vitest with jsdom. The original 14 tests are included in this total, not additional to it. Logs are retained in documentation/final_draft_evidence. Table 5.10 separately summarises the live Supabase exports and the limits of the available system-level evidence.

Frontend startup failed initially because of an invocation-path error and then a filesystem restriction. After correcting the execution setup without changing application code, all 16 tests passed. Initial outputs and the successful rerun were retained.

The supplied files were Supabase Snippet Untitled query.csv (decisions), query (1).csv (requests) and query (2).csv (scores). Their timestamps covered 21 September to 3 October 2026 in Africa/Nairobi. Nine decision probability triples summed to one, and every exported decision linked to a request with matching status. These records show stored outputs, not classification accuracy: they contain no independently adjudicated ground truth, no model-version field and no access-control or audit-log export. Historical threshold outputs must not be assumed to replay under the current rule revision.

Table 5.10: Live test observations and system-level coverage

Area | Evidence | Observed result | Interpretation | Status

Request and score storage | Request and score CSV exports | 12 requests across 8 agent identifiers; all 12 linked to six-score records | Supports persistence of verification evidence | Observed

Decision output | Decision CSV joined by request_id | 9 linked decisions: 7 Verified, 2 Rejected; all matched request status | Supports recorded outcome generation; no Manual Review example | Observed

Decision provenance | decision_basis values | 5 svm_model and 4 placeholder_threshold decisions | Both paths occurred; model version and fallback cause were not recorded | Observed

Incomplete attempts | Request-to-decision join | 3 pending requests had no decision in the supplied exports | Completion was not demonstrated for every recorded attempt | Open

Passkeys and retention | Isolated automated test logs | Passkey service, route and migration checks and 5 retention tests passed | Does not certify physical authenticators or live storage cleanup | Locally tested

Other system requirements | No corresponding records supplied | Access grants, administrator actions, negative security cases, latency and participant usability not established | Requires separate records; no pass/fail result assigned | Not verified



5.4.3 Model Evaluation Results

The saved version 2 incumbent, selected version 3 SVM and saved Decision Tree reference were evaluated on the same 1,500 fresh synthetic cases in the recorded version 3 experiment. The Decision Tree values were recovered from the reference_models section of improvement_report.json; the tree was not retrained or selected using this evaluation set. On 23 October 2026, the unchanged applyPlaceholderDecision function was additionally executed offline on those same cases. This post-hoc threshold comparison is descriptive and did not influence the earlier SVM selection or release gate. Table 5.11 reports all four approaches.

Table 5.11: Model comparison on the same fresh evaluation set

Metric | Saved v2 | Selected v3 | Decision Tree | Threshold rules

Accuracy | 75.733% | 75.800% | 75.667% | 28.667%

Macro F1 | 0.651909 | 0.654082 | 0.648469 | 0.263647

Weighted F1 | 0.730391 | 0.731979 | 0.726834 | 0.212398

Rejected predicted Verified | 44 | 43 | 95 | 0

Manual Review predicted Verified | 186 | 184 | 208 | 8

Log loss | 0.660123 | 0.659596 | 0.789836 | Not applicable

Multiclass Brier score | 0.373659 | 0.373110 | 0.461111 | Not applicable



The accuracy difference between version 3 and version 2 was 0.067 percentage points, equivalent to one additional correct decision. The paired-bootstrap 95% interval for that difference ran from −0.133 to +0.333 percentage points. The macro F1 difference was 0.002173, with an interval from −0.001051 to +0.006855. Both intervals include zero, so the results do not show a conclusive improvement. They describe uncertainty for the fitted models under the same simulator, not across real populations or all possible training runs.

Table 5.12: Selected version 3 confusion matrix

Actual class | Predicted Verified | Predicted Review | Predicted Rejected

Verified | 831 | 15 | 54

Manual Review | 184 | 82 | 34

Rejected | 43 | 33 | 224



Table 5.13: Selected version 3 class-specific performance

Class | Precision | Recall | F1

Verified | 0.785444 | 0.923333 | 0.848825

Manual Review | 0.630769 | 0.273333 | 0.381395

Rejected | 0.717949 | 0.746667 | 0.732026



Figure 5.1: Version 3 confusion matrix on 1,500 fresh synthetic cases. Source: saved version 3 evaluation artifacts.

Manual Review was the weakest class: only 82 of 300 cases were retained for review, while 184 were verified. A further 43 of 300 rejected cases were verified. Together these gave 227 false verifications among 600 non-Verified cases, or 37.83%. Of the 1,058 predicted verifications, 227 were incorrect under the synthetic labels, or 21.46%. These rates have different denominators and should not be confused with the 24.20% overall classification error.

The Decision Tree achieved 75.667% accuracy and macro F1 of 0.648469, compared with 75.800% and 0.654082 for version 3. The SVM therefore exceeded the tree on these point estimates, but no paired significance test between these two models was recorded. The threshold rules achieved 28.667% accuracy and macro F1 of 0.263647. They verified no Rejected cases and only eight Manual Review cases, but rejected 471 of the 900 Verified cases and sent another 363 to review. Their low false-verification count therefore came with substantially poorer acceptance of genuine simulated cases. Rule outputs were not calibrated probabilities, so log loss and Brier scores were not reported for that baseline.

5.4.4 Error Analysis and Interpretation

Class imbalance and overlapping scenarios explain why accuracy alone overstated useful review performance. Verified cases made up 60% of the fresh sample and had high recall, whereas Manual Review cases frequently resembled Verified cases in the observed feature space. The simulator deliberately included indistinguishable components with different latent labels, and the stored identifiability analysis attributed a minimum eight-percentage-point population error contribution to them, with further overlap adding more. This is a property of the simulation and not an estimated limit for real identity verification.

Table 5.14: Permutation importance for the selected model

Feature | Macro F1 decrease | Repeat standard deviation

Liveness | 0.201380 | 0.008477

Face match | 0.110442 | 0.005995

OCR agreement | 0.049802 | 0.007588

Blur | 0.003831 | 0.003357

Brightness | −0.000359 | 0.003924

Contrast | −0.003439 | 0.003605



Figure 5.2: Version 3 permutation importance measured by the decrease in macro F1. Error bars show variation across repeated shuffles. Source: saved version 3 evaluation artifacts.

Liveness and face matching had the strongest measured influence on classification, and OCR added further information. Brightness and contrast showed negligible or slightly negative average importance. A negative value means that shuffling the feature slightly improved the measured score in that experiment; it does not show that image quality is useless, because quality also affected capture and text extraction before the classifier, and correlated features can mask one another.

Log loss and Brier score improved slightly, but probability calibration remains conditional on the simulated 60/20/20 class mixture. A score read as confidence under that mixture is not automatically a trustworthy probability for a different applicant population. Errors that grant access to a non-Verified case also have a different operational consequence from errors that send a genuine applicant to review, which is why the two false-verification counts were reported alongside the aggregate metrics.

5.5 Version Control and Implementation Evidence

Project repository: https://github.com/kar-iuki/Intelligent-Agent-Identity-Verification-System

The repository contained the frontend, backend, AI service, database scripts, dependency files, tests and saved experiment reports. The inspected local HEAD was a8f64cb, dated 20 October 2026. Its reachable history contained 25 commits dated from 1 September to 20 October 2026. No release tags were present. The revised chapter and its new evidence files were local additions and were not represented by that commit. Legacy model bundles were retained for comparison and rollback. Supervisor access and a repository-wide licence were not verified; no public reuse permission is asserted here.

The .gitignore excluded .env and .env.local files, dependency folders, build output, local AI caches and selected test artifacts. These exclusions do not prove that credentials were never committed or that all private datasets are excluded. A complete repository-history secret audit was not performed, and no claim of a clean historical secret scan or credential rotation is made.

5.6 Author Oversight and Use of AI-Assisted Tools

Claude (Anthropic) was identified in the supplied draft as assisting with documentation and implementation prompts. OpenAI Codex assisted with reviewing the source and saved reports, preparing this chapter, executing the isolated automated tests and the offline threshold comparison, and checking the Word layout. Its changes were checked against the inspected code and retained test outputs. The student remains responsible for reviewing the final chapter, verifying alignment with the approved objectives and references, and approving the submission.

5.7 Evaluation Results, Discussion and Limitations

5.7.1 Assessment Against the Objectives

Table 5.15 relates the evidence in this chapter to the five project objectives.

Table 5.15: Objectives, evidence and results

Objective | Output and evidence | Result

1. Investigate current registration and verification practice | Literature review, Chapter 2 | Addressed in Chapter 2 and used to derive the Chapter 4 requirements

2. Identify challenges and fraud risks | Chapter 2; countermeasures implemented as quality gates, liveness scoring and guardrails | Addressed; countermeasures implemented

3. Examine existing KYC platforms | Related-works comparison and research gap, Chapter 2 | Addressed in Chapter 2

4. Develop the system | Modules in Section 5.3; version 3.0.0 classifier | Implemented; classifier reached 75.800% accuracy and 0.654082 macro F1 on the fresh synthetic set

5. Test and validate effectiveness | Tables 5.8 and 5.9: automated test evidence; Table 5.10: live evaluation coverage; Tables 5.11–5.14: classifier and baseline results | Partly met: 46 automated tests passed; live exports showed 12 score-linked requests and 9 decisions. Real-world accuracy, complete security coverage and usability remain unestablished.



5.7.2 Discussion

The implementation combined evidence capture, numerical scoring and persistent verification decisions. The live exports supported this path through 12 request/score pairs and nine matching decisions. The automated tests added evidence for selected interfaces, input handling, passkeys and retention. However, three attempts remained pending, and access enforcement, administrator intervention and user acceptance were not established by the supplied exports.

For classification, version 3 achieved 75.800% accuracy and 0.654082 macro F1 on the fresh synthetic sample and passed its comparative release gate. The improvement over version 2 was inconclusive. Liveness and face matching carried most of the measured importance, which is consistent with the emphasis in the literature on liveness detection (Tan et al., 2014) and discriminative face embeddings (Deng et al., 2019) and supports the pipeline design in Chapter 3. The low Manual Review recall of 27.33% and the 227 false verifications show that the model should not approve agents autonomously. The Manual Review route and the administrator override exist to catch uncertain cases, but the experiment did not measure how often administrators would correct these errors.

Decision provenance distinguished SVM outputs from threshold-rule outputs in the live records. Token validation, role checks, guardrails and image retention were implemented, but the exports did not include access-control or audit records that would prove their live enforcement. The successful isolated passkey and retention tests supplied narrower evidence for those modules; no general security or privacy-compliance conclusion was drawn.

5.7.3 Limitations

Data validity was the main limitation. The labels were synthetic, the class quotas were fixed and the score relationships were assumed. The fresh evaluation sample came from the same simulator and not from independent real applicants, and the benchmark measurements were reused from earlier runs, so later changes to the image pipeline could cause a mismatch between the source distributions and deployed scores.

Evaluation coverage remained limited. The live evidence comprised 12 requests from eight agent identifiers, with no independent identity labels or recorded model versions; it could not establish real-world accuracy. No demographic fairness study, presentation-attack campaign, camera comparison, participant usability study or timed ten-run pipeline benchmark was documented. Small calibration and selection partitions also left a risk of policy overfitting. Model metrics excluded the full effects of capture quality gates, fallback and administrator intervention.

The retention job removed images only for verified agents, while pending, review and rejected cases were excluded from the automated purge. The local retention tests confirmed that exclusion, so it remained a data-minimisation limitation. Unpinned image-processing dependencies and the absence of a historical environment snapshot also limited exact reproduction of the complete pipeline.

The evidence supports a functioning implementation and a reproducible synthetic classifier experiment. The real-world effectiveness of the classifier remains unestablished. Conclusions, recommendations and future work, including periodic retraining on administrator-confirmed decisions, are presented in Chapter 6.


---

## Chapter_5_Hosted_Deployment.docx

Chapter 5: System Implementation, Testing and Evaluation

Intelligent Agent Identity Verification System

5.1 Introduction

This chapter explains how the design approved in Chapter 4 was implemented, the environment in which it ran, and how it was tested and evaluated. The system registers agents, collects identity evidence, combines document and biometric scores, and supports verification decisions and controlled access. It was implemented as a Vue web interface, an Express application server, a Flask artificial intelligence service and a Supabase PostgreSQL database.

The chapter follows a hybrid software and machine learning structure. Sections 5.2 and 5.3 describe the environment, the deviations from the approved design, the implemented modules and workflow, and the dataset and model development procedure. Section 5.4 reports the tests and classification results, Section 5.5 describes the version-control evidence, Section 5.6 declares the AI-assisted tools used, and Section 5.7 discusses the results against the project objectives and states the limitations. The latest saved model, version 3.0.0, achieved 75.800% accuracy on 1,500 fresh synthetic cases. This result was measured under the simulator assumptions described in Section 5.3.6 and does not represent operational identity verification accuracy.

5.2 Implementation Environment

5.2.1 Hardware and Deployment Environment

The system was developed locally and subsequently deployed using Vercel for the Vue frontend, Render for the Express backend, Microsoft Azure Container Apps for the Flask AI service and the Supabase Free plan for authentication, PostgreSQL and storage. By 27 October 2026, the author confirmed that the hosted workflow operated successfully. The local development ports remained 5173, 3000 and 5000; the public services used HTTPS endpoints. Table 5.1 distinguishes the development equipment from the hosted environment. These configurations are not measured minimum requirements.

Table 5.1: Implementation environment and evidence

Layer | Configuration | Evidence

Development machine | AMD Ryzen 5 5625U with Radeon Graphics; 7.4 GiB OS-reported usable memory; C: volume 475.8 GiB; Windows 11 Home Single Language, version 10.0.26200 | Host inventory on 23 October 2026; current development machine, not a benchmarked minimum

Client browser | Camera-capable browser required; historically tested browser names and versions were not recorded | No browser-compatibility verdict established

Application services | Development: Vue 5173, Express 3000, Flask 5000. Hosted: Vercel frontend and Render backend over HTTPS. | Author-confirmed deployment; frontend and backend health checked 27 October 2026

AI service hosting | Microsoft Azure Container Apps; South Africa North hostname; public HTTPS AI service. Compute tier not recorded. | Author-confirmed deployment; AI health endpoint returned HTTP 200 on 27 October 2026

Data services | Supabase Free plan: authentication, PostgreSQL and storage; region not recorded | Author confirmation, SQL scripts and supplied database exports

Model experiment | Python 3.13, locked dependencies, saved model version 3.0.0 | ML README, requirements lock file, model manifest



5.2.2 Software, Services and Configuration

Vue and Vue Router separated the authentication, verification and administrator screens. Express coordinated authenticated requests and database operations, and Python supplied the image-processing and classification libraries. Table 5.2 lists the dependencies. The package manifests declare version ranges, whereas the model manifest records the exact versions used to produce the saved model.

Table 5.2: Software dependencies and their roles

Component | Version evidence | Role

Vue / Vue Router | ^3.5.13 / ^4.5.0 | Interface and navigation

Vite | ^6.0.7 | Development server and frontend build

Express | ^4.21.2 | Application API and request handling

Supabase JavaScript client | ^2.49.1 | Authentication and data integration

SimpleWebAuthn | Server ^14.0.3; browser ^14.0.0 | Optional passkey authentication

Flask | 3.1.3 (model manifest) | AI service endpoints

scikit-learn | 1.9.0 (model manifest) | SVM, scaling and calibration (Pedregosa et al., 2011)

NumPy / SciPy | 2.5.3 / 1.18.1 (model manifest) | Numerical processing

OpenCV | >=4.8,<5 (requirements file) | Image preprocessing and quality metrics

EasyOCR / InsightFace | Unpinned in requirements file | Text extraction and face embeddings

PyTorch / Silent-Face | PyTorch unpinned; local model weights | Presentation-attack scoring



Backend configuration supplied the Supabase URL and keys, the AI service URL, the listening port and authentication settings. Service-role credentials remained server-side. Optional passkeys required a configured relying-party identifier, allowed origins and Node.js 22 or newer. The isolated classifier environment used Python 3.13.3, scikit-learn 1.9.0, NumPy 2.5.3 and Flask 3.1.3, verified during the 23 October 2026 test run. The full image-processing requirements left EasyOCR, InsightFace and PyTorch unpinned. Those packages were not installed in the inspected general Python environment, so their historically tested versions could not be established. The deployed AI hostname identified the Azure South Africa North region. Azure compute allocation, Render and Vercel service tiers, and the Supabase region were not recorded. The Render backend connected to the Azure AI endpoint; the frontend used the public backend address. Deployment secrets remained outside the report. The dependency versions above describe the recorded local experiment, not an independently inspected cloud runtime.

5.2.3 Deployment and Reproducibility

The following steps describe the local installation used for development and reproduction. The subsequent paragraph records the hosted arrangement; local startup commands should not be interpreted as the full cloud deployment configuration.

Obtain the repository and record the source revision. Create a Supabase project, or use an isolated test project. Apply database/schema.sql to a fresh database, then the access-control, audit, date-of-birth, storage, row-level-security and optional passkey scripts in prerequisite order.

Configure the backend and AI service environment files without publishing credentials. Supply the Supabase connection settings, the AI service URL and the frontend origin, and the passkey relying-party settings when passkeys are enabled.

Install the backend and frontend packages from their package directories. Create a Python virtual environment and install ai-service/requirements.txt. Keep the scikit-learn version compatible with the supplied model files.

Make the InsightFace models and Silent-Face weights available, and keep the complete ai-service/ml/models bundle together with the supporting ml.decision_model module.

Start the backend with npm run dev, the AI service with python app.py and the frontend with npm run dev. Check the /health endpoints of the backend and AI service, then call /api/svm/status to confirm that model version 3.0.0 is loaded.

Run the isolated tests, then perform a registration with lawful sample data: document capture, selfie capture and verification. Check the request, scores, decision basis and access record in the test database.

The classifier reproduction procedure used ai-service/ml/requirements-experiment.lock.txt and ai-service/ml/improve_model.py with --jobs 3 and --promote. Reproduction requires an isolated copy because promotion replaces the active model bundle, and the runner refuses to repeat a completed experiment on the same evaluation draw. The older train_model.py script produces version 2 artifacts and is not interchangeable with the version 3 workflow. The model was not retrained for this documentation update. Health endpoints provide service-responsiveness checks. Separate live-test evidence was supplied as exports of verification requests, scores and decisions; the observed results are summarised in Table 5.10.

Hosted deployment separated the three application services. Vercel served the frontend build, Render ran the Express backend, and Azure Container Apps hosted AI inference. Reproduction requires the deployed source revisions, build/start settings, complete AI model bundle and environment configuration, including permitted frontend origins and passkey relying-party settings. Exact cloud resource settings and deployed revision identifiers were not supplied. Public entry points are linked below.

Frontend on Vercel

Backend on Render

AI service on Azure Container Apps

5.3 System Implementation

The implemented architecture separated presentation, application coordination, image analysis and persistence. The browser guided evidence capture, the Express server managed protected operations, and the Flask service produced the numerical evidence used for classification. The subsections below follow this architecture and the Chapter 4 design. In the hosted arrangement, the browser loaded the Vercel frontend, which called the Render API. The backend coordinated requests to the Azure AI service and Supabase. This preserved the separation between the user interface, application logic, inference and persistent records.

5.3.1 Deviations from the Approved Design

Table 5.3 compares the design choices stated in the project draft with the inspected implementation. The implementation column is supported by code and experiment records; the approved Chapters 3 and 4 were not independently revalidated during this update.

Table 5.3: Deviations from the approved design

Area | Approved design | Implemented | Reason

Training dataset | 4,000 records split 70/15/15 | 10,000 cases in training, calibration, selection and original-test partitions, plus a separate 1,500-case fresh evaluation set | Separate calibration and selection partitions prevented tuning on evaluation data; the original test set was retired once its results had informed model changes

Liveness benchmark | NUAA and Replay-Attack | NUAA only | Only NUAA measurements were recorded; the reason for omitting Replay-Attack was not independently established

Label generation | Labels from literature-based thresholds | Labels from latent scenarios with deliberately overlapping feature distributions | Some uncertainty in real verification is not visible in the six scores, so the classes were not made trivially separable

Model comparison | SVM compared with a Decision Tree | Saved v2 and v3 SVMs and Decision Tree evaluated on the same fresh set; existing threshold rules added as an offline descriptive baseline | A release gate was needed before promoting an improved model

Probability output | Class probabilities from the SVM | Sigmoid-calibrated probabilities fitted on a calibration partition | To report more reliable class probabilities

Authentication | Email and password, and Google sign-in | Optional passkey (WebAuthn) sign-in added | Faster sign-in on capable devices without storing biometric data

Identity images | Private storage with time-limited signed URLs | Images deleted three business days after the latest successful verification | Data minimisation



5.3.2 Database Implementation

The relational schema represented users, agent profiles and verification attempts as separate entities. UUID primary keys identified records, and foreign keys linked each agent to a user and each request to an agent and document. Unique constraints on user email, the agent-to-user reference and the national identity number limited duplicate accounts and profiles. Verification scores and decisions used unique request references so that each request had at most one score row and one decision row. Table 5.4 summarises the core entities. The implemented schema uses snake_case attribute names. Foreign keys and unique constraints define relationships, but successful processing is needed to create the corresponding score and decision records.

Table 5.4: Core database entities

Entity | Important contents | Purpose

users | user_id, email, role | Authentication-linked account and role

agents | agent_id, user_id, national_id | Profile linked uniquely to a user

documents | document_id, agent_id, file_url | Evidence references for an agent

verification_requests | request_id, document_id, status | Tracks a submitted verification

verification_scores | request_id and six scores | One score record per request

kyc_decisions | decision, probabilities, basis, time | One outcome per request

access_control_records | agent_id, decision_id, access_granted | Records access enforcement

audit_logs | action, outcome, actor, time, details | Traceable application events

passkeys (optional) | credential_id, public_key, counter, label, device and transport metadata | Passkey sign-in



Request status values distinguished pending, verified, review and rejected requests. The decision enumeration excluded pending because it represents completed classifications. The decision_basis field distinguished SVM classifications from placeholder threshold decisions, which allowed stored outputs to be interpreted correctly when model inference was unavailable. Row-level security was enabled in the base schema with policies supplied in separate scripts, and the backend independently validated bearer tokens through Supabase and checked roles before protected actions.

The retention implementation removed stored identity images and selfies three business days after the latest successful verification while preserving decision and audit metadata. Business days were Monday to Friday in the Africa/Nairobi time zone, without public-holiday exclusions. The cleanup job ran at startup and every fifteen minutes, and failed storage removals were retried. The job did not purge pending, review or rejected cases, a limitation discussed in Section 5.7.3.

5.3.3 Application Modules

Authentication, roles and passkeys. Authentication middleware rejected missing or invalid bearer tokens, and role middleware restricted administrator operations. Email/password and Google sign-in were supplemented by WebAuthn passkeys using SimpleWebAuthn. The public.passkeys table stored the credential identifier, public key, signature counter, transports, device type, backup status, label and device metadata; the application did not receive device fingerprint or face templates from WebAuthn. Challenge and rate-limit records were stored separately. Client support detection controlled which passkey actions were offered.

Registration and evidence capture. Agents entered personal details and supplied document and selfie images through the capture interface. Server upload middleware accepted JPEG and PNG MIME types and imposed a 5 MiB limit per file, returning a validation message for unsupported or oversized files. Registration logic checked existing national identity numbers. The storage integration used a private Supabase bucket; its deployed access settings were not live-tested in this update.

Verification pipeline. Four services produced the evidence signals. The quality service computed sharpness as Laplacian variance, brightness as the mean HSV value channel and contrast as the grayscale standard deviation, and images below the configured thresholds were rejected with specific messages before further processing. The OCR service compared the extracted name, identity number and date of birth with the registered details. Face matching compared document-portrait and selfie embeddings generated with the ArcFace implementation in InsightFace (Deng et al., 2019), and liveness scoring used the Silent-Face anti-spoofing models. These were evidence signals: neither text agreement nor facial similarity alone proved that a document was authentic.

The backend sent the evidence to the quality, OCR, face and liveness endpoints and assembled six numerical features, defined in Table 5.5. Raw image-quality measurements were kept in their original units, and MinMax scaling was applied inside the model processing path. Missing, non-finite, wrongly typed or out-of-range evidence was rejected rather than converted to zero.

Table 5.5: Classifier feature contract

Feature | Unit or range | Interpretation

face_match_score | 0 to 100 | Face similarity score

liveness_score | 0 to 1 | Anti-spoofing score

ocr_confidence_score | 0 to 1 | Agreement with registered identity text

blur_score | Non-negative raw value | Laplacian variance; higher means sharper

brightness_score | 0 to 255 | Mean HSV value-channel intensity

contrast_score | 0 to 127.5 | Grayscale standard deviation



Decision and access control. The classifier returned Verified, Manual Review or Rejected with class probabilities and model provenance. The backend preserved the lowercase database values verified, review and rejected, and the decision and access-control records connected each classification to the agent's permitted workflow.

Administrator review. The administrator controller implemented approval and rejection, updated the associated decision, request status and access record, and recorded the acting administrator. Dashboard endpoints returned totals by verification status and daily counts. Image viewing used signed URLs, normally valid for up to one hour and further limited by the remaining audit window for verified cases. The realtime service emitted new_review_case notifications through Socket.IO. These behaviours were confirmed from source code; a live administrator demonstration was not recorded in this update.

Registration-time guardrails. Middleware checked duplicate national identity numbers, blocked disposable email domains, and counts of guardrail events and failed verification initiations from an IP address or device fingerprint. The defaults allowed three counted events in a 24-hour lookback window, with environment variables able to override these values. Duplicate identities produced a conflict response and attempt limits produced a rate-limit response with retry information. These are configured rules, not measured attack-detection rates.

Audit logging. A central logging utility recorded standardised actions and outcomes for registration, each pipeline step, classification decisions, administrator actions, guardrail triggers and passkey events, with the actor and a timestamp.

5.3.4 End-to-End User Workflow

The implemented workflow connected the following interface, application and database operations. The sequence describes code paths; the live execution status is reported separately in Table 5.10.

The agent signed up or signed in. The backend validated the token and role, and the guardrail middleware checked the national identity number, the email domain and recent failed attempts.

The agent entered personal details, which were stored in the agents table and linked to the user record.

The agent uploaded the identity document and captured a selfie. Format and size were validated in the browser and on the server, and the files were stored in the private bucket with a documents record.

The backend sent both images to the quality service. A failed check returned specific reasons, such as an image being too blurry or too dark, and asked the agent to resubmit.

Images that passed went through OCR, face matching and liveness scoring, and the six scores were stored in verification_scores.

The classifier returned a class and probabilities. The backend stored the decision with its decision_basis and wrote the access_control_records entry.

The agent saw the outcome. Manual Review cases appeared in the administrator queue, where an approval or rejection updated the decision and access records.

Each step wrote an audit_logs entry, so the sequence could be reconstructed for any request.

The supplied live-test evidence consisted of database exports rather than interface screenshots. Their aggregate results are reported in Table 5.10. Personal identifiers and image links are omitted from the chapter. Figures 5.1 and 5.2 show the separate recorded model evaluation.

5.3.5 Exception Handling and Decision Provenance

At the AI endpoint, an unavailable or inconsistent model bundle produced an unavailable-service response. At application level, valid complete evidence could instead enter the existing threshold fallback when SVM inference failed. The fallback recorded placeholder_threshold and an audit reason, and its zero-or-one outputs were rule outcomes and not calibrated confidence. The model-only results in Section 5.4.3 therefore did not measure the combined application, which also includes the quality gates, the fallback and the human-review workflow.

5.3.6 Dataset Description and Preparation

The decision-model dataset contained 10,000 synthetic cases: 6,000 Verified, 2,000 Manual Review and 2,000 Rejected. Each record held the six features in Table 5.5 and a class label. The class quotas were experimental assumptions and not estimates of operational prevalence. No genuine identity records were used because real agent data raises privacy and consent concerns.

The generator reused stored benchmark measurements: 1,000 LFW face pairs, 1,200 NUAA presentations and 500 MIDV quality frames together with MIDV OCR measurements. The machine learning README and dataset metadata recorded summary statistics and file hashes. These historical measurements informed score distributions; the source images were not reprocessed during the version 3 experiment or this documentation update. None of the benchmark sources supplied the three-class KYC labels.

Face and liveness values were sampled from truncated distributions informed by the recorded measurements. OCR and image-quality values combined measured statistics with explicit simulation assumptions, and quality used a multivariate distribution over transformed blur, brightness and contrast. Some unresolved and genuine scenarios deliberately shared observed distributions to represent information that is absent from the six features. The labels therefore reflected assumed latent scenarios and not a threshold applied to the observed scores.

Exact and near-duplicate checks were run before partitioning. Row identifiers and latent scenario descriptions were excluded from the predictors, and scaling and optional quality transformations were fitted within training folds to avoid leakage. These checks screened close observations but could not show that the simulated population represents real applicants. The licence and redistribution terms of the benchmark datasets were not assessed here, and no redistribution claim is made.

Table 5.6: Data partitions used in the version 3 experiment

Partition | Cases | Function

Training | 7,000 | Model fitting and five-fold cross-validation

Calibration | 750 | Probability calibration only

Selection | 750 | Candidate and decision-policy selection

Original test | 1,500 | Retired from version 3 selection and fitting

Fresh evaluation | 1,500 | Frozen comparison of the candidate and the incumbent



The calibration and selection partitions each contained 450 Verified, 150 Manual Review and 150 Rejected cases, and the fresh evaluation set contained 900, 300 and 300 respectively. The fresh set was drawn after candidate selection was frozen, and duplicate checks covered all 11,500 original and fresh records. The original test set was retired because earlier results on it had informed the new research questions.

5.3.7 Model Training, Selection and Packaging

An RBF support vector machine combined the six features into a three-class decision (Pedregosa et al., 2011). Training compared C values of 0.1, 1, 10 and 100 with gamma values of 0.001, 0.01, 0.1, 1, scale and auto, giving 24 combinations per grid. Five-fold shuffled stratified cross-validation used macro F1 as the score, balanced class weights and seed 42, and preprocessing stayed inside the cross-validation pipeline.

For each parameter combination, the 7,000 training cases were divided into five stratified folds of approximately 1,400 cases. A fresh SVM was fitted on four folds (approximately 5,600 cases) and assessed on the remaining fold; the held-out fold changed across five rounds. Macro F1 was averaged across the five validation results. The 24 combinations therefore required 120 fold-level fits per grid, followed by refitting the selected configuration on all 7,000 training cases. Scaling was fitted only on the training portion of each fold. The calibration, selection and fresh evaluation cases were excluded from this cross-validation process.

The version 3 experiment compared raw and transformed quality inputs, native multiclass and explicit one-versus-rest SVM variants, and sigmoid, isotonic and temperature calibration. Three additional grids were fitted, and the earlier raw-native winner was reused with its provenance recorded. Calibration used only the calibration partition. Candidate selection used the separate selection partition and applied safeguards on macro F1, review recall and both false-verification counts relative to the comparable calibration baseline.

The selected configuration was raw_native_sigmoid with C = 10 and gamma = scale, and its training cross-validation macro F1 was 0.672766. Its probability policy used a review multiplier of 1.0, a verification threshold of 0.0 and a verification margin of 0.0, so no extra conservative verification threshold was applied beyond the selected policy.

The release gate required strictly higher accuracy on the fresh set, non-decreasing macro F1, and no increase in either Rejected-to-Verified or Manual-Review-to-Verified errors relative to the saved version 2 incumbent on the same fresh records. The selected candidate passed the gate and was promoted to the local version 3.0.0 bundle. Passing the gate met the specified comparison; it did not establish an acceptable operational false-approval rate.

The model manifest recorded the feature order, class names, library versions and artifact hashes. The service validated the bundle at startup and mapped probabilities using the model's class labels. The saved model, scaler and supporting code are required together. The model stayed static during operation, so completed verifications did not trigger online learning, and legacy artifacts were kept separately to allow comparison and rollback.

Table 5.7: Model version history

Version | Main change | Result on its evaluation set

Version 1 | 4,000-row synthetic generator with largely separable class ranges; earlier scaler/CV methodology | 100.000% accuracy and macro F1 1.000000 on 600 historical test cases; artificially easy separation limits interpretation

Version 2 | 10,000 scenarios with overlap, fold-local scaling, training-only tuning and held-out calibration | 74.333% accuracy and macro F1 0.621383 on its original 1,500-case test set

Version 3.0.0 | Calibrated raw-input SVM, C = 10, gamma = scale | 75.800% accuracy, macro F1 0.654082 on the fresh set



Results for versions 1 and 2 came from earlier evaluation sets and are not directly comparable with version 3. The like-for-like comparison of version 2 and version 3 on the same fresh records is in Table 5.11.

5.4 Testing and Evaluation

5.4.1 Test Strategy and Acceptance Criteria

Automated testing covered classifier contracts, experiment integrity, backend decisions, retention and passkey controls. The three Python suites used unittest from Python 3.13.3; backend suites used Node.js 24.19.0 and its built-in node:test runner. Tests used synthetic features, test credentials, mocks and an embedded PostgreSQL database for the passkey migration. The recorded version 3 log contained 14 passing tests. On 23 October 2026, those tests were rerun and the scope was expanded as summarised in Table 5.9. Three Supabase exports additionally documented live request, score and decision records. These observations were assessed separately from automated assertions and did not establish participant-based usability. Requirement identifiers in Table 5.8 are retained from the supplied draft.

The classifier was evaluated with accuracy, macro and weighted F1, class-specific precision and recall, log loss, the multiclass Brier score and the counts of non-Verified cases predicted as Verified, because those errors give access to agents who should not receive it.

5.4.2 Functional Test Cases and Results

Table 5.8 summarises representative automated test cases. All nine scenarios were covered by the saved version 3 test log and the successful rerun on 23 October 2026. Each pass required the executable assertions to agree with the expected outcome, rather than a manual judgement that the interface appeared to work.

Table 5.8: Isolated test cases and results

ID | Traceability | Scenario and expected result | Result

TC01 | FR-13, NFR-10 | Missing, malformed, non-finite and out-of-range values are rejected | Pass

TC02 | FR-13 | With the class order varied, each probability maps to its class label | Pass

TC03 | FR-13, NFR-13 | Saved artifact and API predictions agree, and legacy API fields are retained | Pass

TC04 | NFR-09 | With the model unavailable, no AI-service prediction is invented | Pass

TC05 | Data requirements (4.2.3) | Regenerated data are reproducible and hidden predictors are excluded | Pass

TC06 | Data requirements (4.2.3) | Split manifest and scaler show preprocessing fitted on training data only | Pass

TC07 | FR-13, FR-15 | The review policy is applied and original probabilities are preserved | Pass

TC08 | FR-12, FR-13, NFR-10 | Incomplete scores fail before inference or threshold fallback | Pass

TC09 | FR-14 to FR-16, FR-24, NFR-13 | A model prediction preserves database enums and the decision basis | Pass



Table 5.9: Recorded suite totals

Suite | Tests | Result

test_svm.py | 6 | 6 passed

test_kyc_experiment.py | 2 | 2 passed

test_kyc_improvement.py | 4 | 4 passed

kycDecision.test.js | 2 | 2 passed

documentRetention.test.js | 5 | 5 passed

passkeys.test.js | 9 | 9 passed

passkeyRoutes.test.js | 1 | 1 passed

passkeyDatabase.test.js | 1 | 1 passed

Frontend unit tests (Vitest 5.0.3) | 16 | 16 passed

Expanded run total | 46 | 46 passed; no assertion failures in completed suites



The expanded run on 23 October 2026 passed 46 automated tests, as shown in Table 5.9. Python used unittest in .venv-kyc; backend tests used node:test, with PGlite for the passkey migration and mocks for storage and session boundaries. Frontend tests used Vitest with jsdom. The original 14 tests are included in this total, not additional to it. Logs are retained in documentation/final_draft_evidence. Table 5.10 separately summarises the live Supabase exports and the limits of the available system-level evidence.

Hosted availability was checked on 27 October 2026: the Vercel frontend returned HTTP 200, and both backend and AI /health endpoints returned HTTP 200 with status: ok. The AI /api/svm/status endpoint returned HTTP 401 to an unauthenticated request, so the deployed model version was not independently established. The author separately confirmed that the hosted workflow worked. These checks demonstrate reachability and service health; they are not a rerun of the 46 local automated tests or a measured hosted accuracy study.

Frontend startup failed initially because of an invocation-path error and then a filesystem restriction. After correcting the execution setup without changing application code, all 16 tests passed. Initial outputs and the successful rerun were retained.

The supplied files were Supabase Snippet Untitled query.csv (decisions), query (1).csv (requests) and query (2).csv (scores). Their timestamps covered 21 September to 3 October 2026 in Africa/Nairobi. Nine decision probability triples summed to one, and every exported decision linked to a request with matching status. These records show stored outputs, not classification accuracy: they contain no independently adjudicated ground truth, no model-version field and no access-control or audit-log export. Historical threshold outputs must not be assumed to replay under the current rule revision.

Table 5.10: Live test observations and system-level coverage

Area | Evidence | Observed result | Interpretation | Status

Request and score storage | Request and score CSV exports | 12 requests across 8 agent identifiers; all 12 linked to six-score records | Supports persistence of verification evidence | Observed

Decision output | Decision CSV joined by request_id | 9 linked decisions: 7 Verified, 2 Rejected; all matched request status | Supports recorded outcome generation; no Manual Review example | Observed

Decision provenance | decision_basis values | 5 svm_model and 4 placeholder_threshold decisions | Both paths occurred; model version and fallback cause were not recorded | Observed

Incomplete attempts | Request-to-decision join | 3 pending requests had no decision in the supplied exports | Completion was not demonstrated for every recorded attempt | Open

Passkeys and retention | Isolated automated test logs | Passkey service, route and migration checks and 5 retention tests passed | Does not certify physical authenticators or live storage cleanup | Locally tested

Other system requirements | No corresponding records supplied | Access grants, administrator actions, negative security cases, latency and participant usability not established | Requires separate records; no pass/fail result assigned | Not verified

Hosted application | Public endpoint checks and author confirmation, 27 October 2026 | Frontend and both health endpoints returned HTTP 200; author reported successful workflow | Unauthenticated model-status request returned 401; no hosted accuracy or load benchmark | Available; workflow author-confirmed



The classifier-contract tests TC01 to TC04 and TC07 to TC09 provide evidence relevant to C4-T07, C4-T08 and part of C4-T18. The experiment checks TC05 and TC06 relate to C4-T23. The recorded passkey and retention suites support parts of C4-T14 and C4-T22. Passing an isolated suite does not demonstrate the complete hosted user workflow, a real-device ceremony or live storage cleanup.

5.4.3 Model Evaluation Results

The saved version 2 incumbent, selected version 3 SVM and saved Decision Tree reference were evaluated on the same 1,500 fresh synthetic cases in the recorded version 3 experiment. The Decision Tree values were recovered from the reference_models section of improvement_report.json; the tree was not retrained or selected using this evaluation set. On 23 October 2026, the unchanged applyPlaceholderDecision function was additionally executed offline on those same cases. This post-hoc threshold comparison is descriptive and did not influence the earlier SVM selection or release gate. Table 5.11 reports all four approaches.

Table 5.11: Model comparison on the same fresh evaluation set

Metric | Saved v2 | Selected v3 | Decision Tree | Threshold rules

Accuracy | 75.733% | 75.800% | 75.667% | 28.667%

Macro F1 | 0.651909 | 0.654082 | 0.648469 | 0.263647

Weighted F1 | 0.730391 | 0.731979 | 0.726834 | 0.212398

Rejected predicted Verified | 44 | 43 | 95 | 0

Manual Review predicted Verified | 186 | 184 | 208 | 8

Log loss | 0.660123 | 0.659596 | 0.789836 | Not applicable

Multiclass Brier score | 0.373659 | 0.373110 | 0.461111 | Not applicable



The accuracy difference between version 3 and version 2 was 0.067 percentage points, equivalent to one additional correct decision. The paired-bootstrap 95% interval for that difference ran from −0.133 to +0.333 percentage points. The macro F1 difference was 0.002173, with an interval from −0.001051 to +0.006855. Both intervals include zero, so the results do not show a conclusive improvement. They describe uncertainty for the fitted models under the same simulator, not across real populations or all possible training runs.

Table 5.12: Selected version 3 confusion matrix

Actual class | Predicted Verified | Predicted Review | Predicted Rejected

Verified | 831 | 15 | 54

Manual Review | 184 | 82 | 34

Rejected | 43 | 33 | 224



Table 5.13: Selected version 3 class-specific performance

Class | Precision | Recall | F1

Verified | 0.785444 | 0.923333 | 0.848825

Manual Review | 0.630769 | 0.273333 | 0.381395

Rejected | 0.717949 | 0.746667 | 0.732026



Figure 5.1: Version 3 confusion matrix on 1,500 fresh synthetic cases. Source: saved version 3 evaluation artifacts.

Manual Review was the weakest class: only 82 of 300 cases were retained for review, while 184 were verified. A further 43 of 300 rejected cases were verified. Together these gave 227 false verifications among 600 non-Verified cases, or 37.83%. Of the 1,058 predicted verifications, 227 were incorrect under the synthetic labels, or 21.46%. These rates have different denominators and should not be confused with the 24.20% overall classification error.

The Decision Tree achieved 75.667% accuracy and macro F1 of 0.648469, compared with 75.800% and 0.654082 for version 3. The SVM therefore exceeded the tree on these point estimates, but no paired significance test between these two models was recorded. The threshold rules achieved 28.667% accuracy and macro F1 of 0.263647. They verified no Rejected cases and only eight Manual Review cases, but rejected 471 of the 900 Verified cases and sent another 363 to review. Their low false-verification count therefore came with substantially poorer acceptance of genuine simulated cases. Rule outputs were not calibrated probabilities, so log loss and Brier scores were not reported for that baseline.

5.4.4 Error Analysis and Interpretation

Class imbalance and overlapping scenarios explain why accuracy alone overstated useful review performance. Verified cases made up 60% of the fresh sample and had high recall, whereas Manual Review cases frequently resembled Verified cases in the observed feature space. The simulator deliberately included indistinguishable components with different latent labels, and the stored identifiability analysis attributed a minimum eight-percentage-point population error contribution to them, with further overlap adding more. This is a property of the simulation and not an estimated limit for real identity verification.

Table 5.14: Permutation importance for the selected model

Feature | Macro F1 decrease | Repeat standard deviation

Liveness | 0.201380 | 0.008477

Face match | 0.110442 | 0.005995

OCR agreement | 0.049802 | 0.007588

Blur | 0.003831 | 0.003357

Brightness | −0.000359 | 0.003924

Contrast | −0.003439 | 0.003605



Figure 5.2: Version 3 permutation importance measured by the decrease in macro F1. Error bars show variation across repeated shuffles. Source: saved version 3 evaluation artifacts.

Liveness and face matching had the strongest measured influence on classification, and OCR added further information. Brightness and contrast showed negligible or slightly negative average importance. A negative value means that shuffling the feature slightly improved the measured score in that experiment; it does not show that image quality is useless, because quality also affected capture and text extraction before the classifier, and correlated features can mask one another.

Log loss and Brier score improved slightly, but probability calibration remains conditional on the simulated 60/20/20 class mixture. A score read as confidence under that mixture is not automatically a trustworthy probability for a different applicant population. Errors that grant access to a non-Verified case also have a different operational consequence from errors that send a genuine applicant to review, which is why the two false-verification counts were reported alongside the aggregate metrics.

5.5 Version Control and Implementation Evidence

Project repository: https://github.com/kar-iuki/Intelligent-Agent-Identity-Verification-System

The repository contained the frontend, backend, AI service, database scripts, dependency files, tests and saved experiment reports. At the 23 October documentation review, the inspected local HEAD was a8f64cb, dated 20 October 2026. Its reachable history contained 25 commits dated from 1 September to 20 October 2026. No release tags were present at that review. Those historical repository details do not identify the later deployed revisions. The revised chapter and its new evidence files were local additions and were not represented by that commit. Legacy model bundles were retained for comparison and rollback. Supervisor access and a repository-wide licence were not verified; no public reuse permission is asserted here.

The .gitignore excluded .env and .env.local files, dependency folders, build output, local AI caches and selected test artifacts. These exclusions do not prove that credentials were never committed or that all private datasets are excluded. A complete repository-history secret audit was not performed, and no claim of a clean historical secret scan or credential rotation is made.

5.6 Author Oversight and Use of AI-Assisted Tools

Claude (Anthropic) was identified in the supplied draft as assisting with documentation and implementation prompts. OpenAI Codex assisted with reviewing the source and saved reports, preparing this chapter, executing the isolated automated tests and the offline threshold comparison, and checking the Word layout. Its changes were checked against the inspected code and retained test outputs. The student remains responsible for reviewing the final chapter, verifying alignment with the approved objectives and references, and approving the submission.

5.7 Evaluation Results, Discussion and Limitations

5.7.1 Assessment Against the Objectives

Table 5.15 relates the evidence in this chapter to the five project objectives.

Table 5.15: Objectives, evidence and results

Objective | Output and evidence | Result

1. Investigate current registration and verification practice | Literature review, Chapter 2 | Addressed in Chapter 2 and used to derive the Chapter 4 requirements

2. Identify challenges and fraud risks | Chapter 2; countermeasures implemented as quality gates, liveness scoring and guardrails | Addressed; countermeasures implemented

3. Examine existing KYC platforms | Related-works comparison and research gap, Chapter 2 | Addressed in Chapter 2

4. Develop the system | Modules in Section 5.3; version 3.0.0 classifier | Implemented and hosted on Vercel, Render and Azure. Recorded synthetic classifier accuracy: 75.800%; macro F1: 0.654082.

5. Test and validate effectiveness | Tables 5.8 and 5.9: automated test evidence; Table 5.10: live evaluation coverage; Tables 5.11–5.14: classifier and baseline results | Partly met: 46 local automated tests passed; live exports contained 12 score-linked requests and 9 decisions. Hosted endpoints were available and operation was author-confirmed; real-world accuracy and comprehensive security/usability remain unestablished.



5.7.2 Discussion

The implementation combined evidence capture, numerical scoring and persistent verification decisions. The live exports supported this path through 12 request/score pairs and nine matching decisions. The automated tests added evidence for selected interfaces, input handling, passkeys and retention. However, three attempts remained pending, and access enforcement, administrator intervention and user acceptance were not established by the supplied exports. Deployment was subsequently completed across Vercel, Render and Azure, with public availability checks and author-confirmed successful operation recorded on 27 October 2026.

For classification, version 3 achieved 75.800% accuracy and 0.654082 macro F1 on the fresh synthetic sample and passed its comparative release gate. The improvement over version 2 was inconclusive. Liveness and face matching carried most of the measured importance, which is consistent with the emphasis in the literature on liveness detection (Tan et al., 2014) and discriminative face embeddings (Deng et al., 2019) and supports the pipeline design in Chapter 3. The low Manual Review recall of 27.33% and the 227 false verifications show that the model should not approve agents autonomously. The Manual Review route and the administrator override exist to catch uncertain cases, but the experiment did not measure how often administrators would correct these errors.

Decision provenance distinguished SVM outputs from threshold-rule outputs in the live records. Token validation, role checks, guardrails and image retention were implemented, but the exports did not include access-control or audit records that would prove their live enforcement. The successful isolated passkey and retention tests supplied narrower evidence for those modules; no general security or privacy-compliance conclusion was drawn.

5.7.3 Limitations

Data validity was the main limitation. The labels were synthetic, the class quotas were fixed and the score relationships were assumed. The fresh evaluation sample came from the same simulator and not from independent real applicants, and the benchmark measurements were reused from earlier runs, so later changes to the image pipeline could cause a mismatch between the source distributions and deployed scores.

Evaluation coverage remained limited. The live evidence comprised 12 requests from eight agent identifiers, with no independent identity labels or recorded model versions; it could not establish real-world accuracy. No demographic fairness study, presentation-attack campaign, camera comparison, participant usability study or timed ten-run pipeline benchmark was documented. Small calibration and selection partitions also left a risk of policy overfitting. Model metrics excluded the full effects of capture quality gates, fallback and administrator intervention. Completed hosting resolved the earlier deployment limitation, but did not provide measured cloud latency, concurrency or long-duration availability.

The retention job removed images only for verified agents, while pending, review and rejected cases were excluded from the automated purge. The local retention tests confirmed that exclusion, so it remained a data-minimisation limitation. Unpinned image-processing dependencies and the absence of a historical environment snapshot also limited exact reproduction of the complete pipeline.

Recovery and integration testing remained incomplete. Backup availability and successful restoration had not been established through a completed recovery test. A uniform bounded timeout and retry policy for the external integrations had not been fully verified. The configured five-second SVM timeout defined one call boundary, but did not establish consistent failure recovery across the remaining services. These limitations correspond to scenarios C4-T18 and C4-T24 in Chapter 4.

Accessibility and informed-collection controls also required further evidence. Wireframe inspection did not establish full accessibility conformance, and the retained evaluation records did not establish informed disclosure and acknowledgement before collection. These limitations relate to scenario C4-T15 and the data and interface requirements in Chapter 4.

The evidence supports a functioning implementation and a reproducible synthetic classifier experiment. The real-world effectiveness of the classifier remains unestablished. Conclusions, recommendations and future work, including periodic retraining on administrator-confirmed decisions, are presented in Chapter 6.


---

## Chapter_5_System_Implementation_Testing_and_Evaluation.docx

CHAPTER 5

System Implementation Testing and Evaluation

Intelligent Agent Identity Verification System

5.1 Introduction

This chapter presents the implementation, testing and evaluation of the Intelligent Agent Identity Verification System. The system was developed to register agents, collect identity evidence, combine document and biometric scores, and support verification decisions and controlled access. The implementation comprised a Vue web interface, an Express application server, a Flask artificial intelligence service and a Supabase PostgreSQL database.

The chapter follows a hybrid software and machine learning structure. It explains the implemented modules and data flow, describes the synthetic dataset and model development procedure, and evaluates the recorded functional tests and classification results. Evidence references E1–E10 identify the repository files supporting the discussion. The latest saved model, version 3.0.0, achieved 75.800% accuracy on 1,500 fresh synthetic cases. This result measured performance under the simulator assumptions and did not establish operational identity verification accuracy.

5.2 Implementation Environment

5.2.1 Hardware and deployment environment

The implementation was organised as a local web prototype connected to managed Supabase services. The documented development ports were 5173 for the interface, 3000 for Express and 5000 for Flask. Network access was required for Supabase and initial model downloads. The recorded experiment identified Python 3.13, but did not establish a minimum tested processor, memory, storage capacity or client-device specification. Consequently, hardware minimums and public deployment availability were not inferred from software configuration. [E1, E5]

Table 5.1 Implementation environment and evidence

Layer | Recorded configuration | Evidence and scope

Client | Browser with camera access | Capture components; no minimum device benchmark recorded.

Application services | Vue, Express and Flask; local development ports | README setup; no measured concurrent-user capacity.

Data services | Supabase authentication, PostgreSQL and storage | Schema and integration code; region and service tier not established.

AI execution | CPU-capable face and liveness inference | Model-loading code; no minimum hardware certification.

Experiment | Python 3.13; saved model v3.0.0 | ML README and artifact manifest; isolated offline experiment.



5.2.2 Software services and configuration

The interface used Vue and Vue Router to separate authentication, verification and administrator screens. Express coordinated authenticated requests and database operations. Python provided the image-processing and classification libraries. The package manifests recorded dependency ranges, whereas the experiment lock file and model manifest recorded exact versions for the saved model. These two forms of evidence were distinguished because a declared range does not prove which application package version was tested. [E1, E2, E7]

Table 5.2 Software dependencies and their roles

Component | Version evidence | Role

Vue / Vue Router | ^3.5.13 / ^4.5.0 | Interface and navigation

Vite | ^6.0.7 | Development server and frontend build

Express | ^4.21.2 | Application API and request handling

Supabase JavaScript client | ^2.49.1 | Authentication and data integration

SimpleWebAuthn | Server ^14.0.3; browser ^14.0.0 | Optional passkey authentication

Flask | 3.1.3 in model manifest | AI service endpoints

scikit-learn | 1.9.0 in model manifest | SVM, scaling and calibration

NumPy / SciPy | 2.5.3 / 1.18.1 in manifest | Numerical processing

OpenCV | >=4.8,<5 in requirements | Image preprocessing and quality metrics

EasyOCR / InsightFace | Unpinned in service requirements | Text extraction and face embeddings

PyTorch / Silent-Face | PyTorch unpinned; local model weights | Presentation-attack scoring



Backend configuration supplied the Supabase URL and keys, AI service URL, listening port and authentication-related settings. Service-role credentials remained server-side. Optional passkeys required the configured relying-party identifier and allowed origins; the project README specified Node.js 22 or newer for this feature. The README also retained an older general Node.js 18 prerequisite, so Node.js 22 or newer was the relevant documented requirement for the complete passkey-enabled application. [E1]

The full image-processing environment was distinct from the smaller locked machine learning experiment environment. The latter supported reproduction of the classifier experiment without downloading every OCR, face and anti-spoofing model. Unpinned production dependencies limited exact reproduction of the complete image pipeline. No container-based deployment was established by the evidence reviewed.

5.2.3 Deployment and reproducibility

A reproducible installation required the application source, authorised Supabase access, database scripts, dependency files and the complete saved model bundle. The following procedure describes the repository setup; it does not constitute evidence that a fresh deployment was executed during preparation of this chapter. [E1, E2, E7]

1. Obtain the project repository and record the source revision. Create a new Supabase project or use an authorised isolated test project. Apply database/schema.sql only to a fresh database; apply the relevant access-control, audit, date-of-birth, storage, row-level-security and optional passkey scripts according to their prerequisites.

2. Configure the backend and AI service environment files without publishing credentials. Supply the Supabase connection settings, AI service URL and frontend origin. Configure passkey relying-party settings when that feature is enabled.

3. Install backend and frontend packages from their respective package directories. Create a Python virtual environment and install ai-service/requirements.txt for the full AI service. Preserve compatible scikit-learn versions for the supplied model files.

4. Make the InsightFace models and Silent-Face weights available. Retain the complete ai-service/ml/models bundle and the supporting ml.decision_model module. Stop the serving process before replacing a model bundle, then restart it so startup validation can run.

5. Start the backend with npm run dev, the AI service with python app.py, and the frontend with npm run dev. Verify the backend and AI /health endpoints, then inspect /api/svm/status to confirm that the expected model version is loaded.

6. Run isolated tests before demonstrating a lawful sample registration, document capture, selfie capture and verification workflow. Check the resulting request, scores, decision basis and access record in the authorised test environment.

For model reproduction, ai-service/ml/requirements-experiment.lock.txt supplied the exact experiment dependencies. The v3 workflow was invoked through ai-service/ml/improve_model.py --jobs 3 --promote in the documented virtual environment. Reproduction belongs in an isolated copy because promotion changes the active model bundle. The runner refused to repeat a completed experiment against the same evaluation draw. Running the older train_model.py workflow could replace the bundle with v2 artifacts and was therefore not interchangeable with reproducing v3. [E5, E6]

Health checks established service responsiveness only. They did not prove that authentication, database permissions, image inference and access enforcement all worked together. The recorded model promotion changed local artifacts; it did not demonstrate publication to a remote hosting service. [E6]

5.3 System Implementation

The implemented architecture separated presentation, application coordination, image analysis and persistence. This separation allowed the browser to guide capture while the backend managed protected operations and the AI service produced numerical evidence. The descriptions below trace implemented capabilities rather than assigning unverified Chapter 4 requirement numbers.

5.3.1 Database and data implementation

The relational schema represented users, agent profiles and verification attempts as separate entities. UUID primary keys identified records, while foreign keys linked an agent to a user and each request to an agent and document. Unique constraints on user email, agent user reference and national identity number limited duplicate account and profile records. Verification scores and decisions used unique request references so that each request had one associated score row and decision row. [E2]

Table 5.3 Core database entities

Entity | Important contents | Relationship or purpose

users | user_id, email, role | Authentication-linked account and role

agents | agent_id, user_id, national_id | Profile linked uniquely to a user

documents | document_id, agent_id, file_url | Evidence references for an agent

verification_requests | request_id, document_id, status | Tracks a submitted verification

verification_scores | request_id and six scores | One score record per request

kyc_decisions | Decision, probabilities, basis, time | One outcome per request

access_control_records | agent_id, decision_id, access_granted | Records access enforcement

audit_logs | Action, outcome, actor, time, details | Traceable application events



Status values distinguished pending, verified, review and rejected requests. The decision enumeration excluded pending because it represented completed classification outcomes. The decision_basis field distinguished SVM classifications from placeholder threshold decisions. This distinction supported interpretation of stored outputs when model inference was unavailable. [E2, E3]

Row-level security was enabled in the base schema, with policies supplied separately. Enabling row-level security alone did not demonstrate that every deployed policy was correct. The backend also validated bearer tokens through Supabase and checked roles before protected actions. Database configuration and server-side checks therefore formed separate parts of the access-control implementation. [E2, E3]

The retention implementation removed stored identity images and selfies after three business days following the latest successful verification, while preserving decision and audit metadata. Business days were Monday to Friday in Africa/Nairobi, without public-holiday exclusions. Cleanup ran at startup and at fifteen-minute intervals, and failed storage removals were retried. This policy depended on the backend remaining active; it did not purge pending, review or rejected cases. [E1, E10]

5.3.2 Application modules and verification workflow

Authentication and profile management supported agent registration, sign-in and completion of identity details. Authentication middleware rejected missing or invalid bearer tokens, and role middleware restricted administrator operations. Optional passkeys supplemented password and Google sign-in. The passkey implementation used WebAuthn credentials rather than storing a user’s fingerprint or other device biometric. [E1, E3]

Document and selfie capture components guided evidence collection. The image-quality service calculated sharpness, brightness and contrast, while document preprocessing supported extraction. OCR compared extracted identity information with registered details. Face matching used InsightFace embeddings to compare a document portrait and selfie, and liveness scoring used Silent-Face anti-spoofing models. These produced evidence signals; neither text agreement nor facial similarity independently proved that a document was authentic. [E4]

The backend sent evidence to the quality, OCR, face and liveness endpoints and assembled six numerical features. The classifier returned Verified, Manual Review or Rejected, together with class probabilities and model provenance. Backend integration preserved the lowercase database values verified, review and rejected. Decision and access-control records connected the classification to the agent’s permitted workflow. Administrator screens supported inspection and human decision-making. [E3, E7]

Table 5.4 Classifier feature contract

Feature | Unit or range | Interpretation

face_match_score | 0–100 | Face similarity score

liveness_score | 0–1 | Anti-spoofing score

ocr_confidence_score | 0–1 | Agreement with registered identity text

blur_score | Nonnegative raw value | Laplacian variance; higher means sharper

brightness_score | 0–255 | Mean HSV value-channel intensity

contrast_score | 0–127.5 | Grayscale standard deviation



Raw image-quality measurements were retained in their original units. MinMax scaling occurred within the model processing path; generic 0–1 quality ratings were not substituted for the expected raw metrics. Missing, non-finite, wrongly typed or out-of-range evidence was rejected rather than silently converted to zero. [E5, E7]

5.3.3 Exception handling and decision provenance

At the AI endpoint, an unavailable or inconsistent model bundle produced an unavailable-service response. At application level, valid complete evidence could instead enter the existing threshold fallback when SVM inference failed. The fallback recorded placeholder_threshold and an audit reason; its zero-or-one outputs were rule outcomes rather than calibrated confidence. Therefore, model-only evaluation results did not measure the combined application, quality gates, fallback and human-review workflow. [E3, E7]

5.3.4 Dataset description and preparation

The decision-model dataset contained 10,000 synthetic cases: 6,000 Verified, 2,000 Manual Review and 2,000 Rejected. Each training record contained the six numerical features and a class label. These class quotas were experimental assumptions rather than estimates of operational prevalence. No genuine identity records or invented participant data were required to describe the classifier experiment. [E5]

Local benchmark measurements informed parts of the generator. The recorded sources included 1,000 LFW face pairs, 1,200 NUAA presentations, 500 MIDV quality frames and MIDV OCR measurements. Stored measurement hashes and summary statistics were retained. The experiment read these measurements; it did not establish that the original source images had been reprocessed or that historical measurements had been independently verified. These datasets did not supply the final three-class KYC labels. [E5]

Face and liveness values were sampled from truncated distributions informed by recorded measurements. OCR and quality generation combined measured statistics with explicit simulation assumptions. Quality measurements used a multivariate distribution over transformed blur, brightness and contrast. Some unresolved and genuine scenarios deliberately shared observed distributions, representing information absent from the six features. Thus, labels represented assumed latent scenarios rather than a simple threshold applied to the observed scores.

Exact and near-duplicate checks preceded partitioning. Row identifiers and latent scenario descriptions were excluded from model predictors. Scaling and optional quality transformations were fitted within training folds, reducing leakage from validation and evaluation records. The duplicate checks screened close observations but did not prove that the simulated population represented real applicants. Dataset ownership, licence conditions and permission to redistribute original benchmark material required separate verification; the chapter makes no redistribution claim. [E5, E6]

Table 5.5 Data partitions used in the v3 experiment

Partition | Cases | Function

Training | 7,000 | Model fitting and five-fold cross-validation

Calibration | 750 | Probability calibration only

Selection | 750 | Candidate and decision-policy selection

Original test | 1,500 | Retired from v3 model selection and fitting

Fresh evaluation | 1,500 | Frozen candidate and incumbent comparison



Calibration and selection each contained 450 Verified, 150 Manual Review and 150 Rejected cases. The fresh evaluation contained 900, 300 and 300 respectively. A new draw was generated after candidate selection was frozen, and duplicate checks covered all 11,500 original and fresh records. The original test set was retired because previous results had informed the new research questions. [E6]

5.3.5 Model training selection and packaging

An RBF support vector machine was used to combine the six features into a three-class decision. Training compared C values of 0.1, 1, 10 and 100, with gamma values of 0.001, 0.01, 0.1, 1, scale and auto. Five-fold shuffled stratified cross-validation used macro F1, balanced class weights and seed 42. This produced 24 parameter combinations per grid. Preprocessing remained inside the cross-validation pipeline. [E5, E6]

The v3 experiment compared raw and transformed quality inputs, native multiclass and explicit one-versus-rest SVM variants, and sigmoid, isotonic and temperature calibration. Three additional grids were fitted, while the prior raw-native winner was reused with provenance. Calibration used only the calibration partition. Candidate selection used the separate selection partition and imposed safeguards on macro F1, review recall and both false-verification counts relative to the comparable calibration baseline.

The selected configuration was raw_native_sigmoid, with C = 10 and gamma = scale. Its recorded training cross-validation macro F1 was 0.672766. Its probability policy used a review multiplier of 1.0, verification threshold of 0.0 and verification margin of 0.0. These settings did not provide an additional conservative verification threshold beyond the selected probability policy. [E6]

The release gate required strictly higher fresh-set accuracy, non-decreasing macro F1 and no increase in either Rejected-to-Verified or Manual-Review-to-Verified errors relative to the saved v2 incumbent on the same fresh records. The selected candidate passed this recorded gate and was promoted to the local version 3.0.0 bundle. Passing the gate established the specified comparative condition; it did not establish an acceptable operational false-approval rate.

The model manifest recorded the feature order, class names, library versions and artifact hashes. The service validated the model bundle at startup and mapped class probabilities using the model’s class labels rather than assuming a fixed column order. Saved model, scaler and supporting code were required together for reproduction. The model remained static during service operation; completed verification attempts did not trigger online learning. [E7]

5.4 Testing and Evaluation

5.4.1 Test strategy and acceptance criteria

The recorded evaluation combined isolated classifier-contract tests, experiment-integrity checks, backend decision tests and a held-out synthetic model comparison. Functional assertions checked valid outputs, invalid inputs, model unavailability and preservation of decision provenance. The experiment assessed accuracy, macro and weighted F1, class-specific precision and recall, calibration and consequential misclassification counts. Existing logs are reported as recorded evidence, not as tests freshly rerun for this chapter. [E6, E8]

End-to-end live database behaviour, target-device compatibility, user acceptance, accessibility, throughput and recovery required separate evidence. Source code and isolated passing tests were not treated as substitutes for those evaluations.

5.4.2 Functional test cases and recorded results

Table 5.6 links representative test scenarios to implemented capabilities. The test identifiers organise this chapter and are not asserted to be the approved Chapter 4 requirement identifiers. Expected outcomes come from test assertions, while observed verdicts come from the saved v3 verification log. [E8]

Table 5.6 Functional test cases and results

ID and scope | Scenario and expected result | Recorded result

TC01 Input validation | Submit missing, malformed, non-finite and out-of-range values; reject them. | Pass: SVM contract validation test.

TC02 Output mapping | Vary class order; map each probability to its class label. | Pass: class-order test.

TC03 Model consistency | Compare saved artifact and API predictions; retain legacy API fields. | Pass: artifact parity and legacy-contract test.

TC04 Availability | Make the model unavailable; do not invent an AI-service prediction. | Pass: unavailable-model contract test.

TC05 Dataset integrity | Regenerate saved data and inspect predictors; preserve reproducibility and exclude hidden predictors. | Pass: dataset integrity test.

TC06 Leakage control | Inspect split manifest and scaler fitting; fit preprocessing on training data. | Pass: partition and scaler test.

TC07 Decision policy | Apply review policy; preserve original returned probabilities. | Pass: saved-policy and improvement tests.

TC08 Backend validation | Supply incomplete scores; fail before inference or threshold fallback. | Pass: backend decision test.

TC09 Persistence contract | Return a model prediction; preserve database enums and decision basis. | Pass: backend decision test.



Table 5.7 Recorded suite totals

Suite | Tests | Result

test_svm.py | 6 | 6 passed

test_kyc_experiment.py | 2 | 2 passed

test_kyc_improvement.py | 4 | 4 passed

backend/tests/kycDecision.test.js | 2 | 2 passed

Total in saved v3 log | 14 | 14 passed; zero recorded failures



These totals describe one retained verification log. They do not cover every test file in the repository or certify current uncommitted interface changes. No complete defect register and chronological retest record accompanied these results; consequently, no defect-resolution counts were inferred. Live registration, capture, administrator review and access enforcement remained outside the conclusions supported by this isolated log.

5.4.3 Model evaluation results

Both the saved v2 incumbent and selected v3 model were evaluated on the same 1,500 fresh synthetic cases. Using a common evaluation set avoided presenting the older v2 result from a different sample as a direct before-and-after comparison. [E6]

Table 5.8 Model comparison on the same fresh evaluation set

Metric | Saved v2 | Selected v3

Accuracy | 75.733% | 75.800%

Macro F1 | 0.651909 | 0.654082

Weighted F1 | 0.730391 | 0.731979

Rejected predicted Verified | 44 | 43

Manual Review predicted Verified | 186 | 184

Log loss | 0.660123 | 0.659596

Multiclass Brier score | 0.373659 | 0.373110



The accuracy difference was 0.067 percentage points, equivalent to one additional correct decision. The paired-bootstrap 95% interval for the accuracy difference extended from −0.133 to +0.333 percentage points. The macro F1 difference was 0.002173, with an interval from −0.001051 to +0.006855. Both intervals included zero, so the results did not establish a statistically conclusive improvement. They described uncertainty for the fitted models under the same simulator, not across real-world populations or all possible training runs.

Table 5.9 Selected v3 confusion matrix

Actual class | Predicted Verified | Predicted Review | Predicted Rejected

Verified | 831 | 15 | 54

Manual Review | 184 | 82 | 34

Rejected | 43 | 33 | 224



Table 5.10 Selected v3 class-specific performance

Class | Precision | Recall | F1

Verified | 0.785444 | 0.923333 | 0.848825

Manual Review | 0.630769 | 0.273333 | 0.381395

Rejected | 0.717949 | 0.746667 | 0.732026



The weakest class was Manual Review: only 82 of 300 cases were retained for review, while 184 were verified. In addition, 43 of 300 rejected cases were verified. Combining these errors gave 227 false verifications among 600 non-Verified cases, or 37.83%. Of all 1,058 predicted verifications, 227 were incorrect under the synthetic labels, or 21.46%. These derived rates have different denominators and should not be confused with the 24.20% overall classification error.

5.4.4 Error analysis and interpretation

The class imbalance and overlapping scenarios helped explain why accuracy alone overstated useful review performance. Verified cases represented 60% of the fresh sample and had high recall, whereas review cases frequently resembled verified cases in the observed feature space. The simulator deliberately included indistinguishable components with different latent labels. The stored identifiability analysis attributed a minimum eight-percentage-point population error contribution to those components, with further overlap potentially adding error. This was a property of the simulation, not an estimated limit for real identity verification. [E6]

Table 5.11 Permutation importance for the selected model

Feature | Macro F1 decrease | Repeat standard deviation

Liveness | 0.201380 | 0.008477

Face match | 0.110442 | 0.005995

OCR agreement | 0.049802 | 0.007588

Blur | 0.003831 | 0.003357

Brightness | −0.000359 | 0.003924

Contrast | −0.003439 | 0.003605



Liveness and face matching had the strongest measured influence on classification under permutation. OCR provided additional information, while brightness and contrast showed negligible or slightly negative average importance. Negative values meant that shuffling slightly improved the measured score in that experiment; they did not prove that image quality was useless. Quality also affected capture and extraction before the classifier, and correlated features could mask one another’s contribution. [E6]

Log loss and Brier score improved slightly, but probability calibration remained conditional on the simulated class mixture. A score interpreted as confidence under a 60/20/20 synthetic distribution was not automatically a trustworthy probability for a different applicant population. Errors that grant access to a non-Verified case also carried a different operational consequence from errors that direct a genuine applicant to review. The evaluation therefore retained the two false-verification counts alongside aggregate metrics.

5.5 Version Control and Implementation Evidence

Project repository: https://github.com/kar-iuki/Intelligent-Agent-Identity-Verification-System

The repository contained separate frontend, backend, AI-service and database directories, setup instructions, dependency files, SQL scripts, tests and saved experiment reports. Recent history included commits 1119c41, describing OCR changes, and 9d0fe2c, describing README work; the inspected HEAD was 870b303. Some current interface and passkey changes were uncommitted, so that commit alone did not identify every file described in the working implementation. [E9]

Legacy model artifacts were retained separately from the active v3 bundle, supporting comparison and rollback. Generic commit messages limited the explanatory value of parts of the history. Branch reviews, issue tracking, release tags, repository licensing and supervisor access were not established by the inspected evidence and were not claimed as completed practices.

5.6 Author Oversight and Use of AI Assisted Tools

OpenAI Codex assisted with preparation of this chapter by inspecting the project source, organising the supplied Chapter 5 guidelines, and drafting descriptions and tables from saved implementation and evaluation evidence. The draft distinguished recorded results from unverified deployment and user-evaluation claims. The student remains responsible for checking the chapter against the approved objectives, confirming the evidence and citations, and approving the final submission. This declaration does not assert that student or supervisor review has already occurred.

5.7 Evaluation Discussion and Limitations

5.7.1 Assessment of implemented capabilities

The implementation supported an integrated evidence-processing architecture: agents could be represented in the database, document and selfie components supplied inputs, separate services produced six scores, and decision outputs carried model or fallback provenance. The saved contract and backend tests supported correctness of selected interfaces and invalid-input handling. They did not establish that the complete live workflow met every approved requirement. [E2–E4, E8]

For automated classification, the available evidence supported a narrower finding: v3 achieved 75.800% accuracy and 0.654082 macro F1 on the declared fresh synthetic sample and passed its comparative release gate. The small improvement over v2 was inconclusive, while low review recall and 227 false verifications showed that the gate did not establish safe autonomous approval. Human-review facilities were implemented, but the experiment did not measure whether human reviewers corrected those errors. [E6]

For traceability and access control, linked score, decision, access and audit records provided an implemented basis for reconstructing verification actions. Role checks, token validation and retention logic added controls. Their presence did not establish resistance to every attack, complete privacy compliance or successful recovery under failures. A full-system acceptance verdict could not be derived from the recorded model and contract tests alone.

5.7.2 Limitations affecting the findings

Data validity was the main limitation. Synthetic adjudication labels, fixed class quotas and assumed score relationships constrained generalisation. The fresh sample came from the same simulator rather than independent real applicants. Historical benchmark measurements were reused, and changes to the current image pipeline could create mismatch between measured source distributions and deployed scores.

Evaluation coverage was also limited. No demographic fairness study, modern presentation-attack campaign, target-camera comparison, prospective pilot, participant-based usability study or measured end-to-end latency and throughput result was established. Minimum hardware, cloud capacity and long-duration reliability were therefore unresolved. The small calibration and selection partitions also left a risk of overfitting candidate policies.

Finally, classifier metrics excluded application quality gates, threshold fallback and administrator intervention. Unpinned dependencies and uncommitted changes limited exact reproduction of the complete system. The evidence supported a functioning implementation structure and a reproducible synthetic classifier experiment, while the extent of real-world effectiveness remained unestablished. Final conclusions, recommendations and future work belong in Chapter 6.

Chapter 5 Evidence References

The references below identify project artifacts used for implementation descriptions and recorded results. Paths are relative to the project root. The repository address appears in Section 5.5; saved outputs should be retained with the submitted revision so the examiner can inspect the same evidence.

E1 System setup and dependencies. README.md; frontend/package.json; backend/package.json; ai-service/requirements.txt.

E2 Database implementation. database/schema.sql; database/rls_policies.sql; database/storage_agent_documents.sql; database/access_control_module8.sql; database/audit_logging_module10.sql; database/audit_logs_nullable_request.sql; database/agents_date_of_birth.sql; database/passkeys.sql.

E3 Application integration and access control. backend/src/controllers/verificationController.js; backend/src/services/verificationService.js; backend/src/services/accessControlService.js; backend/src/middleware/authMiddleware.js; backend/src/middleware/roleMiddleware.js.

E4 Image processing and user interface. ai-service/services/imageQualityService.py; documentPreprocessService.py; ocrService.py; faceMatchService.py; livenessService.py in the same directory; frontend/src/components/DocumentCaptureStep.vue; CameraCapture.vue; LiveSelfieChallenge.vue; frontend/src/views/.

E5 Dataset and original methodology. ai-service/ml/README.md; generation_config.json; requirements-experiment.lock.txt; data/kyc_synthetic_dataset_10000.metadata.json; generate_dataset.py; train_model.py, all under ai-service/ml/.

E6 v3 experiment and results. ai-service/ml/experiments/v3/README.md; SUMMARY.md; protocol.json; improvement_report.json; selection_frozen.json; fresh_evaluation_metadata.json; identifiability_diagnostic.json; svm_permutation_importance.csv, all in the same v3 directory.

E7 Model deployment contract. ai-service/ml/models/artifact_manifest.json; ai-service/ml/models/model_version.txt; ai-service/ml/decision_model.py; ai-service/services/svmService.py; ai-service/routes/svmRoutes.py.

E8 Recorded test evidence. ai-service/ml/experiments/v3/verification_checks.json; ai-service/tests/test_svm.py; test_kyc_experiment.py; test_kyc_improvement.py in the same tests directory; backend/tests/kycDecision.test.js.

E9 Version-control evidence. Git remote and inspected history at HEAD 870b303, with local working changes present; repository: kar-iuki/Intelligent-Agent-Identity-Verification-System.

E10 Retention implementation. README.md, Verified-agent file retention; backend/src/services/documentRetentionService.js; backend/tests/documentRetention.test.js. Test-file presence is not a reported passing execution.
