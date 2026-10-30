INTRO = [
"In this chapter, I present the analysis and design of the Intelligent Agent Identity Verification System. I define its registration, identity checking, decision, access control and administrative functions, together with the quality, data and interface requirements that support them. I then describe the system models, interface wireframes and verification plan. These designs connect the project requirements to the implementation and evaluation presented in Chapter 5.",
"I use Object-Oriented Analysis and Design (OOAD) to describe the actors, domain objects and interactions. For the classifier, I use an experimental machine learning workflow that separates model development from evaluation. The selected views are a use case diagram, class diagram, entity relationship diagram, system architecture diagram, sequence diagram, database schema and interface wireframes. Together they address the human workflow, evidence processing, data relationships and presentation of decisions. The machine learning data design is documented separately because a transactional database diagram does not describe training and evaluation separation."
]

FR = [
('Agent registration and authentication',[
('FR-01','H / A','The system shall authenticate an account through email and password or Google sign-in before allowing protected agent functions.','C4-T01: valid, invalid, expired and unconfirmed account scenarios.'),
('FR-02','H / A','The system shall allow an authenticated agent to submit full name, phone number, national ID number and date of birth as a personal profile.','C4-T02: required fields, invalid dates and persisted profile values.'),
('FR-03','H / A','The system shall accept identity evidence as JPEG or PNG images up to 5 MiB per file for the supported national ID, passport and driving licence capture flows.','C4-T03: supported formats, file-size boundary and document-side cases.'),
('FR-04','H / A','The system shall guide the agent through live camera selfie capture and a displayed face movement or blink challenge before continuing the capture workflow.','C4-T04: successful challenge, camera refusal and failed capture.'),
('FR-05','H / O','The system shall reject creation of an agent profile whose national ID number is already assigned to another profile.','C4-T02: duplicate identifier returns a conflict without a second profile.'),
('FR-06','M / O','The system shall reject registration attempts using an email domain on the configured disposable-domain block list.','C4-T02: blocked and permitted domains; inspect rejection record.')]),
('Verification pipeline',[
('FR-07','H / A','The system shall assess document and selfie blur, brightness and contrast before the full OCR, face matching and liveness pipeline proceeds.','C4-T05: clear and degraded images produce quality measurements.'),
('FR-08','H / A','The system shall stop downstream verification when the image quality gate fails and identify the image and condition requiring recapture.','C4-T05: quality failure prevents subsequent model calls.'),
('FR-09','H / A','The system shall compare OCR-extracted identity fields with registered details and return text-agreement evidence and a confidence score.','C4-T06: matched, mismatched and unreadable name, ID and date fields.'),
('FR-10','H / A','The system shall compare the document portrait with the captured selfie and return a numerical face-match score.','C4-T06: matching and non-matching pairs, and a missing-face case.'),
('FR-11','H / A','The system shall assess presentation-attack evidence from the selfie and return a liveness score.','C4-T06: genuine and photo-presentation samples; record limitations.'),
('FR-12','H / O','The system shall retain the six pipeline scores against the verification request as processing progresses.','C4-T07: inspect stored quality, OCR, face and liveness values.'),
('FR-13','H / R','The system shall classify a complete valid six-score vector as Verified, Manual Review or Rejected using the available decision model.','C4-T08: validate input contract, class mapping and prediction output.')]),
('Access control and guardrails',[
('FR-14','H / A','The system shall permit the verified-agent workspace only when the current authorised access decision grants access.','C4-T09: verified agent can enter the protected workspace.'),
('FR-15','H / B','The system shall place Manual Review cases in the administrator queue while withholding verified-agent workspace access.','C4-T09: review case is visible to administrators and cannot enter workspace.'),
('FR-16','H / O','The system shall withhold verified-agent workspace access when the current decision is Rejected.','C4-T09: rejected account cannot use the protected workspace.'),
('FR-17','M / O','The system shall block further applicable registration attempts from an IP address when its recorded failures reach the configured limit within the configured window.','C4-T10: default limit of 3 failures in 24 hours and boundary cases.'),
('FR-18','M / O','The system shall apply the configured failure limit to registration attempts associated with the same device fingerprint.','C4-T10: repeated fingerprint, expiry of window and separate devices.')]),
('Administrator management and audit',[
('FR-19','H / B','The system shall allow an authorised administrator to inspect review cases with their available identity images and verification scores.','C4-T11: review queue, detail panel and expired-image state.'),
('FR-20','H / B','The system shall record an authorised administrator approval or rejection and apply the corresponding access outcome.','C4-T11: decision, status, access record and audit entry agree.'),
('FR-21','M / B','The system shall allow an administrator to retrieve an agent\'s verification history and associated audit trail.','C4-T11: distinguish multiple attempts and retain previous outcomes.'),
('FR-22','L / B','The system shall export administrator-selected audit records as CSV using date-range and agent filters.','C4-T12: filtered rows, valid CSV and no unauthorised export.'),
('FR-23','M / B','The system shall notify connected administrator interfaces when a case enters Manual Review.','C4-T12: new or updated review case and connection recovery.'),
('FR-24','H / O','The system shall append an audit entry for each defined significant authentication, registration, verification, decision and administrator action.','C4-T13: compare expected action sequence with recorded events.'),
('FR-25','H / O','Each audit entry shall identify its action, outcome, time and responsible user or system, with request, agent and network context where available.','C4-T13: validate event values, including events before profile creation.'),
('FR-26','H / O','The system shall prevent ordinary authenticated agent and administrator clients from updating or deleting audit entries.','C4-T13: negative client write tests and policy inspection.')]),
('Current interface and operational capabilities',[
('FR-27','M / A','The system shall support account confirmation and password recovery without granting access solely because a recovery request was submitted.','C4-T01: confirmation, reset request, expired link and successful recovery.'),
('FR-28','M / A','The system shall allow an authenticated user on a supported device to enrol a passkey.','C4-T14: enrolment, cancellation and unsupported-device behaviour.'),
('FR-29','M / A','The system shall authenticate a registered passkey using a fresh server challenge and the credential public key.','C4-T14: valid assertion, invalid signature and expired or reused challenge.'),
('FR-30','M / A','The system shall allow users to list, rename and remove their own passkeys under the account recovery checks.','C4-T14: ownership, rename, removal and available recovery method.'),
('FR-31','H / A','The system shall allow permitted recapture of failed evidence without requiring resubmission of evidence that remains acceptable.','C4-T05: document-only and selfie-only recapture; retry limits.'),
('FR-32','M / A','The system shall display an agent\'s own verification progress, decision and available action in the identity workspace.','C4-T15: processing, review, verified, rejected and error states.'),
('FR-33','M / B','The administrator directory shall support searching and status filtering, including verified agents whose image audit window is open.','C4-T11: search, filter and three-business-day window boundary.'),
('FR-34','M / B','The system shall display available model status and saved evaluation results to authorised administrators.','C4-T16: available report, loading failure and fallback state.')])
]

NFR=[
('Performance and readiness',[
('NFR-01','H / A','The evaluation shall measure complete pipeline elapsed time over ten sequential single-user runs in a declared environment, separating warm and cold starts.','C4-T17: record start/end events, median, maximum and all failures.'),
('NFR-02','M / A','The evaluation shall measure representative non-pipeline API response times under a declared workload and record the host and network conditions.','C4-T17: authentication, profile, status and administrator queries.'),
('NFR-03','M / O','Readiness checks shall distinguish process availability from availability of the model components needed for verification.','C4-T18: service running with model absent, loading or ready.')]),
('Security and privacy',[
('NFR-04','H / O','Protected agent operations shall reject missing or invalid authentication and prevent cross-agent access.','C4-T01 and C4-T09: absent/expired token and other-agent identifiers.'),
('NFR-05','H / B','Administrator operations shall reject an authenticated user without the administrator role.','C4-T09: agent token against every administrator route family.'),
('NFR-06','H / A','Identity images shall remain private; an authorised signed URL shall last at most one hour and shall not outlive an applicable verified-case audit window.','C4-T19: public access denied; expiry and remaining-window boundaries.'),
('NFR-07','H / O','Production network connections carrying credentials or identity evidence shall use HTTPS.','C4-T19: inspect frontend, backend, AI and storage endpoints.'),
('NFR-08','H / O','Database client access shall be restricted by ownership and role; privileged service credentials shall remain on the server.','C4-T19: policy and configuration inspection plus cross-agent tests.')]),
('Reliability and failure handling',[
('NFR-09','H / O','Threshold fallback shall be permitted only when valid complete scores exist and the SVM decision service is unavailable or returns an unusable prediction.','C4-T08 and C4-T18: fallback has a recorded cause and decision basis.'),
('NFR-10','H / O','An incomplete or failed evidence-processing step shall not be represented as a successful completed verification.','C4-T18: inject quality, OCR, face, liveness and storage failures.')]),
('Interaction quality and human oversight',[
('NFR-11','M / A','The interface shall label each onboarding step and identify the current step, completed steps and the next available action.','C4-T15: walkthrough; record task completion and assistance needed.'),
('NFR-12','H / A','Validation and quality failures shall identify the affected field or image and provide a corrective action.','C4-T05 and C4-T15: invalid fields, blur, denied camera and service error.'),
('NFR-13','H / B','Each decision shall retain its basis so administrators can distinguish a model result, threshold fallback, quality failure and manual intervention.','C4-T07 and C4-T08: persist and retrieve the correct provenance.'),
('NFR-14','H / B','Manual overrides shall require administrator authority and retain the actor, time and resulting access outcome.','C4-T11 and C4-T13: approve/reject override and trace resulting records.'),
('NFR-15','M / O','Image quality, OCR, face matching, liveness and decision services shall expose separate contracts that can be checked independently.','C4-T20: module inspection and representative contract tests.')]),
('Model evaluation and accessibility',[
('NFR-16','H / R','Model evaluation shall report per-class precision, recall and F1, macro F1, accuracy and a confusion matrix on an isolated evaluation set.','C4-T21: metrics derived from saved predictions and declared labels.'),
('NFR-17','H / R','Model evaluation shall report Rejected-to-Verified and Manual-Review-to-Verified errors separately from aggregate accuracy.','C4-T21: explicit numerators, denominators and error interpretation.'),
('NFR-18','H / R','Evaluation shall state the synthetic population assumptions and the untested demographic, camera, document and attack conditions.','C4-T21: inspect provenance, evaluated coverage and untested conditions.'),
('NFR-19','M / A','Essential form, navigation and review controls shall expose labels, keyboard operation, visible focus and understandable status text.','C4-T15: keyboard and screen-reader checks, including modal focus.'),
('NFR-20','M / A','The interface shall preserve essential tasks on desktop and mobile layouts without losing field labels, feedback or access restrictions.','C4-T15: representative desktop and phone widths; both display themes.')])
]

DR=[
('DR-01','H / A','Profile data shall link a unique user account to personal identity details, validating required values and dates before persistence.','C4-T02: missing fields, duplicate identifier and invalid/future dates.'),
('DR-02','H / A','Each stored evidence object shall be associated with an agent and an evidence type, including national ID front/back where required and selfie.','C4-T03: allowed image types, references and correct object ownership.'),
('DR-03','H / R','The six-score feature vector shall use the names, order, units and permitted ranges defined in Table 4.5.','C4-T08: missing, non-numeric, non-finite and out-of-range inputs.'),
('DR-04','H / O','Requests, scores, decisions and access records shall preserve stable keys and valid relationships while allowing an incomplete attempt to remain incomplete.','C4-T07: uniqueness, foreign keys and interrupted processing.'),
('DR-05','H / B','Audit records shall retain structured action context with nullable agent/request links where no corresponding profile or request exists.','C4-T13: registration rejection, authentication and pipeline event cases.'),
('DR-06','H / O','Verified-agent evidence images shall expire three business days after the latest successful verification, including manual approval.','C4-T22: Monday-Friday, Africa/Nairobi, weekend and repeated-approval cases.'),
('DR-07','H / O','Expired verified-case image cleanup shall preserve document metadata, scores, decisions and audit records and retry failed object removals.','C4-T22: failed removal, cleared references and surviving metadata.'),
('DR-08','H / O','Retention periods for pending, review and rejected evidence and retained metadata shall be explicitly defined before operational rollout.','C4-T22: policy review; these cases are excluded from current automatic purge.'),
('DR-09','H / A','The onboarding process shall communicate the purpose, access conditions and retention of identity evidence before collection.','C4-T15: inspect disclosure, informed acknowledgement and acceptance evidence.'),
('DR-10','H / R','Synthetic data generation shall retain its configuration, seed, source-measurement provenance, label assumptions and duplicate-screening results.','C4-T23: regenerate from configuration and inspect recorded metadata.'),
('DR-11','H / R','Training, calibration, selection and evaluation partitions shall be separated so evaluation records do not fit transformations or select candidates.','C4-T23: split manifest, training folds and frozen selection artifacts.'),
('DR-12','M / O','The maintainer shall retain controlled backups of necessary metadata, configuration and model artifacts and verify a restoration procedure.','C4-T24: isolated restore and integrity check; record retention and exclusions.')
]

IR=[
('IR-01','H / A','The browser interface shall support labelled onboarding, role-appropriate navigation and inline validation on desktop and mobile devices.','C4-T15: wireframe walkthrough and implementation accessibility checks.'),
('IR-02','H / O','Protected backend requests shall carry a valid Supabase bearer token and be checked for the required role and resource ownership.','C4-T01 and C4-T09: 401/403 and cross-agent scenarios.'),
('IR-03','H / O','Backend-to-AI calls shall use the defined REST contracts, with multipart images or JSON scores and structured JSON responses.','C4-T20: each endpoint input/output contract and invalid response.'),
('IR-04','H / O','Calls to the hosted AI service shall authenticate using the server-held API credential over HTTPS.','C4-T19: absent/wrong credential, secret location and transport inspection.'),
('IR-05','H / O','The decision-service call shall use its configured timeout; other integration calls shall have an explicitly documented failure and retry policy.','C4-T18: timeout, service refusal and bounded retry behaviour.'),
('IR-06','H / O','The storage integration shall upload and retrieve private objects through authorised server operations and issue bounded signed image links.','C4-T03 and C4-T19: upload failure, private retrieval and expiry.'),
('IR-07','M / B','Review notifications shall connect database review-state events to the administrator interface and recover from a disconnected client.','C4-T12: insert/update transition, toast and reconnect; check recipient access.'),
('IR-08','M / A','Passkey integration shall use browser WebAuthn support and server verification while leaving established recovery sign-in methods available.','C4-T14: browser capability, challenge verification and recovery.'),
('IR-09','H / A','Camera capture shall request permission, report an unavailable camera and show the preview used to produce the submitted evidence.','C4-T04 and C4-T15: allow/deny permissions and capture framing.'),
('IR-10','M / B','The administrator evaluation interface shall label saved metrics with their model and dataset context and show an explicit unavailable-report state.','C4-T16: report metadata, missing report and active/fallback indicator.')
]

FEATURES=[
('face_match_score','Face similarity','0 to 100','Document portrait versus selfie; score, not a probability of identity.'),
('liveness_score','Presentation evidence','0 to 1','Selfie anti-spoof estimate; evaluation is limited to tested attacks.'),
('ocr_confidence_score','Text agreement','0 to 1','Agreement between extracted and registered fields; not proof of authenticity.'),
('blur_score','Laplacian variance','Finite and non-negative','Raw sharpness measure; larger values generally indicate sharper images.'),
('brightness_score','Mean HSV value','0 to 255','Raw image brightness.'),
('contrast_score','Grayscale standard deviation','0 to 127.5','Raw image contrast.')]

DATA_TEXT=[
"The transactional data comprise account references, agent profiles, document-object references, verification attempts, six-score records, decisions, access outcomes and audit events. The authentication provider manages passwords and sessions. The application stores account references; password management remains with the authentication provider. Optional passkeys store credential identifiers, public keys and supporting authentication metadata; the application does not receive the device's local fingerprint or face template through WebAuthn.",
"Table 4.4 defines the data requirements and the planned checks for each one. I distinguish these design requirements from the results reported in Chapter 5. Informed collection, retention beyond verified cases and backup restoration remain areas requiring policy definition and evaluation evidence."
]

DATASET_TEXT=[
"The decision-model development dataset contains 10,000 synthetic records: 6,000 Verified, 2,000 Manual Review and 2,000 Rejected. These are experimental class quotas rather than estimates of real applicant prevalence. Each record contains six generated verification-score features and one assumed adjudication label. The earlier 4,000-record dataset is retained as historical work and is not the final experiment described here.",
"The generator uses stored local measurements from Labeled Faces in the Wild for face matching, NUAA for real/photo presentation scores, and MIDV document frames and OCR measurements. The measurement files and their provenance inform score distributions. They do not provide joint three-class KYC ground truth. The synthetic labels, relationships between channels and uncertain-case scenarios are modelling assumptions. The generator reuses historical measurements rather than reprocessing every source image with the current pipeline.",
"The original stratified split is 7,000 training, 1,500 validation and 1,500 test records. For version 3 development, the validation partition is divided into 750 calibration and 750 selection records. The original test partition is retired because earlier results informed the follow-up research questions. A fresh 1,500-record evaluation sample, comprising 900 Verified, 300 Manual Review and 300 Rejected cases, is drawn after candidate selection is frozen. This creates 11,500 unique experimental records across the original and fresh datasets, not an 11,500-record training set.",
"Preprocessing is fitted within training folds during cross-validation. Calibration fits only on its designated partition, and candidate/policy selection uses the separate selection partition. A stored configuration, seed lineage, source hashes, split manifests and duplicate checks support reproduction. The fresh evaluation sample is generated from the same simulator assumptions; it is not independent real-world validation. I distinguish the predeclared release check from model tuning when interpreting the evaluation results.",
"I distinguish model class probabilities from threshold-rule outputs in the decision records and evaluation. A threshold decision may use 0/1 indicator values for compatibility, but these are not calibrated certainty estimates. The model remains static during a verification request; completed cases do not automatically retrain it. Any later retraining requires a separate offline process using appropriately governed and confirmed data."
]

INTERFACE_TEXT=[
"The design separates the Vue presentation layer, Express application layer, Flask AI layer and Supabase persistence and identity services. The hosted arrangement uses Vercel for the frontend, Render for the backend and Microsoft Azure Container Apps for the AI service. Supabase provides authentication, PostgreSQL, object storage and database-change events. This deployment allocation preserves the logical separation. Chapter 5 describes the hosted environment, configuration and available evaluation evidence.",
"The browser communicates with the application API using JSON or multipart uploads and bearer authentication. Email/password and Google authentication use Supabase Auth. The backend verifies identity, role and object ownership before protected operations. Server-held Supabase and AI credentials are not included in browser code. Camera permission and browser support are prerequisites for the live capture flow; password and Google recovery paths remain available when passkeys are unsupported.",
"The backend coordinates separate quality, OCR, face, liveness and SVM requests. Quality, OCR, face and liveness endpoints consume image data; the SVM endpoint consumes the six-score JSON vector. For the hosted AI service, a server-held API key accompanies requests. The configured SVM call timeout defaults to five seconds. A uniform bounded timeout and retry policy for the remaining integrations has not yet been fully verified. This limitation is included in the integration verification plan.",
"An unavailable SVM can trigger a logged threshold decision only after a complete valid score vector exists. Failure of the whole AI service before evidence extraction cannot be repaired by classifying missing scores. Such a failure returns a controlled error or incomplete state. Automatic retries of writes must not create duplicate profiles, requests, decisions or access records; the verification plan therefore includes retry checks at each operation boundary.",
"Files are written to private storage and retrieved as buffers for processing. Authorised administrator image views use signed URLs lasting no more than one hour and, for verified cases, no longer than the remaining image audit window. Socket.io conveys review notifications after database INSERT or UPDATE events place a request into review. Recipient authorisation, reconnect behaviour and consistency with the persisted queue are separate verification concerns."
]

SCHEMA=[
('users','user_id; email; role; created_at','Account reference; unique email; identity is linked to Supabase Auth.'),
('agents','agent_id; user_id; full_name; phone_number; national_id; date_of_birth','user_id is unique; an account has zero or one agent profile. national_id is unique.'),
('documents','document_id; agent_id; document_type; file_url; uploaded_at','An agent may have several evidence records. Expired images can have cleared file references.'),
('verification_requests','request_id; agent_id; document_id; status; created_at','Each request belongs to an agent and references its identity evidence.'),
('verification_scores','score_id; request_id; six score attributes','request_id is unique. An attempt may have no score record before processing.'),
('kyc_decisions','decision_id; request_id; final_decision; class probabilities; decision_basis; decided_at','request_id is unique. A decision is absent until processing or intervention produces one.'),
('access_control_records','record_id; agent_id; decision_id; access_granted; enforced_at','decision_id is unique; the record reflects the enforced outcome.'),
('audit_logs','log_id; agent_id; request_id; action; outcome; details; performed_by; ip_address; timestamp','Agent/request references may be absent for early events. Ordinary clients cannot alter entries.'),
('passkeys and authentication support','Credential public key and identifier; user reference; counter; label; device metadata; challenge/rate-limit records','Optional authentication extension. Private keys and device biometrics remain outside the application.')]

FIGURES=[
('4.3.1 Use Case Diagram','Use Case Diagram',
 'The use case view identifies the agent and administrator services within the identity-verification workflow. It relates registration and evidence submission to FR-01 to FR-13, controlled access to FR-14 to FR-16, and administration and auditing to FR-19 to FR-26. Its purpose is to clarify responsibility and the service boundary.',
 'The agent initiates onboarding and checks the outcome; the administrator reviews exceptions and inspects the audit history. Automated evidence processing supports those user goals. Eligibility for the protected workspace is a business precondition evaluated from the access decision. Visiting an outcome screen does not grant access; the recorded access decision controls entry. The AI processing layer is a system component in the architecture described in Section 4.4.3.'),
('4.4.1 Class Diagram','Class Diagram',
 'The class view organises the domain concepts used to describe accounts, agents, documents, verification attempts, processing results, decisions and access. It supports the separation of responsibilities required by FR-07 to FR-13 and NFR-15. The conceptual model provides vocabulary for implementation without requiring every concept to become a separate database table.',
 'A verification attempt provides the context for image-quality, OCR, face-match and liveness results. The decision consumes completed evidence, while access enforcement consumes the decision. Audit events refer to the relevant agent or request when those objects exist. I represent ownership through the relationships in the model and specify the supporting keys, validation and transaction boundaries in the data design. These controls address orphaned records and partially completed attempts.'),
('4.4.2 Entity Relationship Diagram','Entity Relationship Diagram',
 'The entity relationship view describes the persistent registration and verification records and their associations. It supports DR-01 to DR-05 by linking identity evidence and decisions to the relevant agent and request. The logical entity catalogue in Section 4.4.5 identifies the attributes and integrity rules needed by the current design.',
 'An account may exist before an agent profile is completed, and a request may exist before scores or a decision have been produced. A unique request reference permits at most one associated score row or decision row; it does not force the child row to exist. This distinction represents pending and failed attempts without requiring a completed result. Audit references may be absent for authentication or blocked registration events that occur before profile creation.'),
('4.4.3 System Architecture Diagram','System Architecture Diagram',
 'The architecture view separates presentation, application coordination, evidence inference and persistent records. The four logical layers support the interface requirements in Table 4.6 and allow the verification services to be evaluated independently. The hosted service allocation does not change the responsibilities of these layers.',
 'The frontend sends authenticated requests to the backend, which coordinates AI calls and persistence. Responses return through the relevant interfaces. Supabase authentication and database-change events introduce additional interactions, while review notifications travel from the backend to the administrator interface. Model-stage fallback depends on valid existing scores; a complete evidence-service outage instead leaves an error or incomplete attempt. Layer separation supports component replacement through defined interfaces. A replacement still requires integration checks against those interfaces.'),
('4.4.4 Sequence Diagram','Sequence Diagram',
 'The sequence view describes the progression from evidence submission to a recorded outcome and administrator review where required. It supports FR-07 to FR-16 and FR-24. The runtime design uses the backend to coordinate the individual AI endpoints and to associate their results with a verification request.',
 'Quality assessment gates subsequent processing. The backend stores the quality record and updates it as OCR, face and liveness evidence becomes available, then requests classification and applies the access decision. Audit events accompany the defined significant steps. A failed early step does not become a successful classifier input, and a manual-review outcome withholds verified workspace access. Administrator intervention is a separate authorised action that changes the recorded decision and access state.'),
('4.4.5 Database Schema','Database Schema',
 'The schema view presents the persistent entities, while Table 4.7 provides the logical keys, attributes and integrity conditions required by the current system. The logical design is the focus of this chapter; exact SQL declarations, indexes and deployed policy scripts are implementation evidence for Chapter 5.',
 'Profile, evidence, verification and decision records are separated to avoid repeating personal data in every attempt. Unique keys prevent duplicate associations, foreign keys maintain valid references, and allowed status values constrain state representation. Access-control policy and audit append-only behaviour require separate enforcement. Restricting inserts does not by itself prohibit updates or deletion. Privileged service operations remain outside ordinary-client row policies, so administrator database privileges must be governed separately.')
]

WIREFRAMES=[
('Account registration and sign in','figure_4_07_authentication','FR-01, FR-06, FR-27 to FR-29; NFR-04; IR-02 and IR-08',
 'The authentication wireframe separates account creation from sign-in. It provides the entry point for an agent or administrator before protected functions are offered. Registration gathers the account details, while sign-in presents password, Google and supported passkey options.',
 'Persistent labels identify the required inputs and a dedicated message region exposes validation or authentication failures. Password recovery and confirmation messages retain a route back to sign-in. The human-check control reflects the current password-login interface; its accessible alternative remains part of accessibility evaluation. Passkey cancellation returns control to established sign-in methods. The two panels represent separate screens, not one combined form.'),
('Personal profile details','figure_4_08_personal_details','FR-02 and FR-05; NFR-11, NFR-12; DR-01; IR-01',
 'The profile wireframe is the first protected onboarding step. It links the authenticated email to the identity details later compared with the document and displays the four-stage progress indicator.',
 'The account email is read-only. Full name, phone number, national ID and date of birth remain grouped as one task, with validation beside the affected input. The Next action persists valid details before advancing. On a narrow screen, the paired fields stack in reading order. Existing values are restored when the user returns, and a duplicate national ID produces an explicit conflict rather than a second profile.'),
('Identity document capture','figure_4_09_document_capture','FR-03, FR-07, FR-08 and FR-31; DR-02; IR-06 and IR-09',
 'The document wireframe combines document-type selection, camera or file input, preview and image-quality feedback. It represents the selected capture step; national ID front and back are captured in sequence, while passport and driving-licence flows use their relevant document face.',
 'Capture guidance is placed beside the preview and quality feedback remains visible before continuation. A user may retake or replace an image. The action changes from quality checking to continuation when the check succeeds. Rejected type/size, permission denial and service errors keep the user on the affected step. A successful image-quality check improves suitability for processing but does not establish that the document is authentic.'),
('Live selfie and challenge','figure_4_10_live_selfie','FR-04 and FR-11; NFR-11 and NFR-12; IR-09',
 'The selfie wireframe provides a live preview, a face-position guide and the instruction for the current capture challenge. It separates capture readiness from later model-based liveness scoring.',
 'The first instruction asks the user to face the camera; the next displays the selected movement or blink task. Status text reports progress without relying only on colour. The user can retry after a failed capture or return to the previous step. The camera-permission error provides guidance on restoring access. The capture challenge supports the live-capture workflow; its completion alone does not demonstrate resistance to every presentation attack.'),
('Verification progress and decision states','figure_4_11_verification_states','FR-08 and FR-13 to FR-16, FR-31 and FR-32; NFR-09 to NFR-13',
 'The verification wireframe presents the processing state and the principal outcome alternatives. The four state panels are shown together for design inspection; the operational interface displays the state relevant to the current attempt.',
 'Only a verified outcome with an authorised access grant exposes the protected-workspace action. Review explains that an administrator must decide. Rejection and capture failure show the reason and a permitted next action; the interface must distinguish retaking poor evidence from an identity decision. The recorded decision basis distinguishes a model result from threshold fallback. A retry is offered only while the backend permits it, and a failed integration does not show a success state.'),
('Administrator directory','figure_4_12_admin_directory','FR-19, FR-21, FR-23 and FR-33; NFR-05; DR-06',
 'The administrator directory provides an overview of agents, review workload and current model status. Role-specific navigation connects the directory with the review queue, recent verified cases, flagged attempts, audit records and model evaluation.',
 'The search and status controls narrow the displayed agent set. Each row provides status, an audit deadline when applicable and a route to case detail. Recently verified cases use the three-business-day image window, while the broader directory retains record history after images expire. Real-time review notifications invite the administrator to open a case; the persisted queue remains the reference if a notification is missed. Counts in the wireframe are placeholders, not study results.'),
('Administrator case review','figure_4_13_case_review','FR-19 to FR-21 and FR-24; NFR-13 and NFR-14; DR-03 to DR-07',
 'The case-review wireframe groups identity images, registered and extracted fields, the six scores, decision provenance and available administrator actions. It abstracts the existing detail drawer into a readable design view.',
 'The reviewer can compare evidence before deciding, inspect the audit history and close the case without making a change. Approve and Reject are authorised backend actions. A rejection dialog may record a reason; actor, time and outcome must be retained for either decision. An expired image is labelled unavailable while its metadata remains visible. Deleted images are unavailable for further inspection. Administrators interpret model probabilities alongside the retained scores, decision basis and audit history.'),
('Audit history and export','figure_4_14_audit_export','FR-22, FR-24 to FR-26; DR-05; NFR-05',
 'The audit wireframe makes actions, outcomes and responsible actors available for administrator inspection. Pagination supports navigation through the event history, and a separate export dialog defines the requested subset.',
 'Date and optional agent filters determine the CSV output. Export retains server-side role checks and exposes a readable failure if the request cannot complete. The log view contains no editing or deletion control for ordinary administrator use. Empty results must be distinguished from loading errors. The dialog is shown alongside the log for documentation and would appear as an overlay during use.'),
('Passkey management','figure_4_15_passkey_management','FR-28 to FR-30; IR-08; NFR-19',
 'The passkey wireframe provides account-level enrolment and credential management outside the evidence-capture flow. It identifies the registered device credentials without displaying secret key material or local device biometric templates.',
 'Each credential shows its label, device metadata and relevant dates, with Rename and Remove actions. Removal opens a confirmation dialog and remains subject to available recovery methods. Unsupported devices retain existing authentication routes. Loading, cancellation and failure messages are exposed in a status region. A successful registration does not bypass identity verification or grant access to the verified workspace.'),
('Model evaluation interface','figure_4_16_model_evaluation','FR-34; NFR-16 to NFR-18; IR-10',
 'The evaluation wireframe presents the saved model report to an administrator, including aggregate metrics, class-specific results and the confusion matrix. It links the report to its model and dataset context.',
 'The view distinguishes saved synthetic evaluation from current applicant outcomes and exposes a fallback or unavailable-report state. The wireframe uses placeholders for report values. My evaluation discussion examines false-verification errors and the limitations in Manual Review recall alongside the aggregate metrics. The interface supports inspection; it does not initiate online training or establish that a hosted service is running the same model version as a local report.')
]

TESTS=[
('C4-T01','Account and session','Valid and invalid login, confirmation, recovery, expired tokens and protected endpoints.'),
('C4-T02','Profile and guardrails','Valid profile, missing/invalid values, duplicate national ID and blocked email domains.'),
('C4-T03','Evidence storage','JPEG/PNG, 5 MiB boundary, document type/sides, private object ownership and upload failure.'),
('C4-T04','Live capture','Camera permission, framing, challenge completion, failure and browser/device compatibility.'),
('C4-T05','Quality and recapture','Clear/degraded evidence, downstream gate, explanatory feedback and targeted recapture.'),
('C4-T06','Evidence processing','OCR agreement, matching/non-matching faces and tested genuine/spoof presentations.'),
('C4-T07','Persistence and provenance','Linked scores/decisions/access records, partial attempts, key integrity and decision basis.'),
('C4-T08','Classifier contract','Six valid features, invalid/missing values, class-probability mapping and SVM fallback.'),
('C4-T09','Role and access','Verified/review/rejected access, unauthorised administrator calls and cross-agent identifiers.'),
('C4-T10','Repeated attempts','IP and fingerprint limits, configured 24-hour window and limit boundary.'),
('C4-T11','Administrator workflow','Directory/search, review/override, images, audit deadline and attempt history.'),
('C4-T12','Notification and export','Review-state events, reconnect, recipient access, CSV date/agent filtering and failure.'),
('C4-T13','Audit accountability','Required events, actor/context, early nullable references and forbidden client mutations.'),
('C4-T14','Passkeys','Enrolment, signatures, challenge expiry/replay, ownership, rename, removal and recovery.'),
('C4-T15','Interface and accessibility','Wireframe tasks, state feedback, keyboard/focus, mobile layout, disclosure and assistance.'),
('C4-T16','Model report interface','Correct model/data labels, active/fallback state and unavailable report.'),
('C4-T17','Performance measurement','Declared hosts/network, cold/warm runs, whole pipeline and representative API timings.'),
('C4-T18','Failure and readiness','Service/model unavailability, timeout, invalid response, partial persistence and safe retries.'),
('C4-T19','Data protection','HTTPS, API credentials, client ownership policies, private objects and signed-link expiry.'),
('C4-T20','Service contracts','Independent image/score endpoints, defined inputs, outputs, errors and compatibility.'),
('C4-T21','Model evaluation','Held-out metrics, confusion matrix, false verification, calibration and stated limitations.'),
('C4-T22','Retention','Business-day expiry, repeat approvals, cleanup retries, metadata and non-verified policy scope.'),
('C4-T23','Experiment reproducibility','Configuration/seed/source records, duplicates, split isolation and fitted preprocessing.'),
('C4-T24','Recovery','Controlled backup, isolated restoration and record/model integrity without premature data deletion.')]

TRACE=[
('FR-01 to FR-06; FR-27','O2, O4; A/O','4.2.1; Figures 4.7-4.10','C4-T01 to C4-T04'),
('FR-07 to FR-12; FR-31','O2, O4; A/O','4.2.1; Figures 4.2, 4.5, 4.9-4.11','C4-T05 to C4-T07'),
('FR-13; FR-34','O4, O5; B/R','4.2.3; Figures 4.4, 4.16','C4-T08, C4-T16, C4-T21'),
('FR-14 to FR-16; FR-32','O2, O4; A/O','4.4.4; Figure 4.11','C4-T09, C4-T15'),
('FR-17 and FR-18','O2, O4; O','4.2.1 guardrails','C4-T10'),
('FR-19 to FR-21; FR-33','O4, O5; B','Figures 4.12 and 4.13','C4-T11'),
('FR-22 to FR-26','O2, O4; B/O','4.4.5; Figure 4.14','C4-T12, C4-T13'),
('FR-28 to FR-30','O4; A/O','4.2.4; Figures 4.7 and 4.15','C4-T14'),
('NFR-01 to NFR-03','O5; A/O','4.2.2; 4.2.4','C4-T17, C4-T18'),
('NFR-04 to NFR-08','O2, O4; A/B/O','4.2.4; 4.4.5','C4-T01, C4-T09, C4-T19'),
('NFR-09 and NFR-10','O2, O4; O','4.2.4; 4.4.4','C4-T08, C4-T18'),
('NFR-11 and NFR-12; NFR-19 and NFR-20','O4, O5; A/B','4.4.6 all wireframes','C4-T05, C4-T15'),
('NFR-13 and NFR-14','O2, O4; B/O','4.4.5; Figure 4.13','C4-T07, C4-T08, C4-T11, C4-T13'),
('NFR-15','O4; O','4.4.1; 4.4.3','C4-T20'),
('NFR-16 to NFR-18','O5; R/B','4.2.3; Figure 4.16','C4-T21'),
('DR-01 to DR-05','O2, O4; A/B/O/R','Tables 4.5 and 4.7','C4-T02, C4-T03, C4-T07, C4-T08, C4-T13'),
('DR-06 to DR-09','O2, O4; A/O','4.2.3; Figures 4.12 and 4.13','C4-T15, C4-T22'),
('DR-10 and DR-11','O5; R','4.2.3 experimental data design','C4-T23'),
('DR-12','O4, O5; O','4.2.3 recovery policy','C4-T24'),
('IR-01 and IR-09','O4; A','4.4.6; Figures 4.8-4.10','C4-T04, C4-T15'),
('IR-02 and IR-04','O2, O4; O','4.2.4 authentication boundaries','C4-T01, C4-T09, C4-T19'),
('IR-03 and IR-05','O4, O5; O','4.2.4; Figure 4.4','C4-T18, C4-T20'),
('IR-06 and IR-07','O4; A/B/O','4.2.4; Figures 4.12-4.14','C4-T03, C4-T12, C4-T19'),
('IR-08 and IR-10','O4, O5; A/B','Figures 4.15 and 4.16','C4-T14, C4-T16')]

REFERENCES=[
('ISO/IEC/IEEE. (2018). ISO/IEC/IEEE 29148:2018 Systems and software engineering - Life cycle processes - Requirements engineering.','https://www.iso.org/standard/72089.html'),
('ISO/IEC. (2023). ISO/IEC 25010:2023 Systems and software engineering - Systems and software Quality Requirements and Evaluation - Product quality model.','https://www.iso.org/standard/78176.html'),
('World Wide Web Consortium. (2023). Web Content Accessibility Guidelines 2.2 and supporting quick reference.','https://www.w3.org/WAI/WCAG22/quickref/')]
