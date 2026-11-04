# Current chapter text snapshots

Extracted from saved DOCX files on 31 October 2026. Text and table-cell order are preserved; figures, image annotations and pagination are not reconstructed. These documents predate some latest capture/UI changes.


---

## Chapter_4_Revised.docx

Chapter 4 System Analysis and Design

4.1 Introduction

In this chapter, I present the analysis and design of the Intelligent Agent Identity Verification System. I define its registration, identity checking, decision, access control and administrative functions, together with the quality, data and interface requirements that support them. I then describe the system models, interface wireframes and verification plan. These designs connect the project requirements to the implementation and evaluation presented in Chapter 5.

I use Object-Oriented Analysis and Design (OOAD) to describe the actors, domain objects and interactions. For the classifier, I use an experimental machine learning workflow that separates model development from evaluation. The selected views are a use case diagram, class diagram, entity relationship diagram, system architecture diagram, sequence diagram, database schema and interface wireframes. Together they address the human workflow, evidence processing, data relationships and presentation of decisions. The machine learning data design is documented separately because a transactional database diagram does not describe training and evaluation separation.

I base the system description on the application source, database migrations and version 3 experiment records, together with the implementation and evaluation documented in Chapter 5. Model-development details are recorded in the project's machine learning README, experiment protocol, split manifests and saved reports. The wireframe source-to-screen mapping is retained with the editable figure files.

4.2 System Requirements

The requirements define required behaviour, quality conditions, data obligations and integration boundaries. I use ISO/IEC/IEEE 29148:2018 to guide requirements organisation and ISO/IEC 25010:2023 to organise the quality categories (ISO/IEC/IEEE, 2018; ISO/IEC, 2023).

I organise the requirements by system function, quality, data and interface needs. Each requirement has a unique identifier, a priority, a source category and a planned verification method. The source category identifies the stakeholder or technical need that motivates the requirement. The following notation key explains how to read the tables.

Table 4.1: Stakeholder needs used to organise the requirements

Stakeholder or need | Design responsibility

Agent | Complete onboarding, understand failures and see the current outcome without accessing another agent's data.

Administrator | Inspect exception cases and decision evidence, make accountable interventions and retrieve audit history.

System maintainer | Protect credentials and stored evidence, handle failures and manage retention and recovery.

Research evaluation | Preserve data/model provenance, isolate evaluation and report consequential classification errors.



Requirement notation

FR, NFR, DR and IR identify functional, non-functional, data, and interface and integration requirements respectively. Each identifier ends with its sequence number. H, M and L indicate high, medium and low priority. Source codes identify agent needs (A), administrator needs (B), operational needs (O) and research and evaluation needs (R). The slash separates priority from source; H / A therefore means a high-priority agent requirement.

C4-T01 identifies planned test scenario 01 in Chapter 4; Table 4.10 lists all scenarios. For example, FR-01 | H / A | C4-T01 links the high-priority authentication requirement to its account-access checks. Scenario identifiers refer to planned checks, with results reported in Chapter 5. O1 to O5 identify project objectives, while O alone identifies operational needs. Figure and section references point to the relevant design views.

4.2.1 Functional Requirements

The functional requirements describe the actor, required behaviour and expected verification. Registration establishes the account and personal profile; evidence capture then supplies the document and live selfie. Automated processing produces a decision, while administrators handle exceptions. A client-side capture challenge and model-based liveness analysis serve different parts of this workflow.

Table 4.2: Functional requirements

IDPriority /source | Requirement | Verification plan

 | Agent registration and authentication | 

FR-01H / A | The system shall authenticate an account through email and password or Google sign-in before allowing protected agent functions. | C4-T01: valid, invalid, expired and unconfirmed account scenarios.

FR-02H / A | The system shall allow an authenticated agent to submit full name, phone number, national ID number and date of birth as a personal profile. | C4-T02: required fields, invalid dates and persisted profile values.

FR-03H / A | The system shall accept identity evidence as JPEG or PNG images up to 5 MiB per file for the supported national ID, passport and driving licence capture flows. | C4-T03: supported formats, file-size boundary and document-side cases.

FR-04H / A | The system shall guide the agent through live camera selfie capture and a displayed face movement or blink challenge before continuing the capture workflow. | C4-T04: successful challenge, camera refusal and failed capture.

FR-05H / O | The system shall reject creation of an agent profile whose national ID number is already assigned to another profile. | C4-T02: duplicate identifier returns a conflict without a second profile.

FR-06M / O | The system shall reject registration attempts using an email domain on the configured disposable-domain block list. | C4-T02: blocked and permitted domains; inspect rejection record.

 | Verification pipeline | 

FR-07H / A | The system shall assess document and selfie blur, brightness and contrast before the full OCR, face matching and liveness pipeline proceeds. | C4-T05: clear and degraded images produce quality measurements.

FR-08H / A | The system shall stop downstream verification when the image quality gate fails and identify the image and condition requiring recapture. | C4-T05: quality failure prevents subsequent model calls.

FR-09H / A | The system shall compare OCR-extracted identity fields with registered details and return text-agreement evidence and a confidence score. | C4-T06: matched, mismatched and unreadable name, ID and date fields.

FR-10H / A | The system shall compare the document portrait with the captured selfie and return a numerical face-match score. | C4-T06: matching and non-matching pairs, and a missing-face case.

FR-11H / A | The system shall assess presentation-attack evidence from the selfie and return a liveness score. | C4-T06: genuine and photo-presentation samples; record limitations.

FR-12H / O | The system shall retain the six pipeline scores against the verification request as processing progresses. | C4-T07: inspect stored quality, OCR, face and liveness values.

FR-13H / R | The system shall classify a complete valid six-score vector as Verified, Manual Review or Rejected using the available decision model. | C4-T08: validate input contract, class mapping and prediction output.

 | Access control and guardrails | 

FR-14H / A | The system shall permit the verified-agent workspace only when the current authorised access decision grants access. | C4-T09: verified agent can enter the protected workspace.

FR-15H / B | The system shall place Manual Review cases in the administrator queue while withholding verified-agent workspace access. | C4-T09: review case is visible to administrators and cannot enter workspace.

FR-16H / O | The system shall withhold verified-agent workspace access when the current decision is Rejected. | C4-T09: rejected account cannot use the protected workspace.

FR-17M / O | The system shall block further applicable registration attempts from an IP address when its recorded failures reach the configured limit within the configured window. | C4-T10: default limit of 3 failures in 24 hours and boundary cases.

FR-18M / O | The system shall apply the configured failure limit to registration attempts associated with the same device fingerprint. | C4-T10: repeated fingerprint, expiry of window and separate devices.

 | Administrator management and audit | 

FR-19H / B | The system shall allow an authorised administrator to inspect review cases with their available identity images and verification scores. | C4-T11: review queue, detail panel and expired-image state.

FR-20H / B | The system shall record an authorised administrator approval or rejection and apply the corresponding access outcome. | C4-T11: decision, status, access record and audit entry agree.

FR-21M / B | The system shall allow an administrator to retrieve an agent's verification history and associated audit trail. | C4-T11: distinguish multiple attempts and retain previous outcomes.

FR-22L / B | The system shall export administrator-selected audit records as CSV using date-range and agent filters. | C4-T12: filtered rows, valid CSV and no unauthorised export.

FR-23M / B | The system shall notify connected administrator interfaces when a case enters Manual Review. | C4-T12: new or updated review case and connection recovery.

FR-24H / O | The system shall append an audit entry for each defined significant authentication, registration, verification, decision and administrator action. | C4-T13: compare expected action sequence with recorded events.

FR-25H / O | Each audit entry shall identify its action, outcome, time and responsible user or system, with request, agent and network context where available. | C4-T13: validate event values, including events before profile creation.

FR-26H / O | The system shall prevent ordinary authenticated agent and administrator clients from updating or deleting audit entries. | C4-T13: negative client write tests and policy inspection.

 | Current interface and operational capabilities | 

FR-27M / A | The system shall support account confirmation and password recovery without granting access solely because a recovery request was submitted. | C4-T01: confirmation, reset request, expired link and successful recovery.

FR-28M / A | The system shall allow an authenticated user on a supported device to enrol a passkey. | C4-T14: enrolment, cancellation and unsupported-device behaviour.

FR-29M / A | The system shall authenticate a registered passkey using a fresh server challenge and the credential public key. | C4-T14: valid assertion, invalid signature and expired or reused challenge.

FR-30M / A | The system shall allow users to list, rename and remove their own passkeys under the account recovery checks. | C4-T14: ownership, rename, removal and available recovery method.

FR-31H / A | The system shall allow permitted recapture of failed evidence without requiring resubmission of evidence that remains acceptable. | C4-T05: document-only and selfie-only recapture; retry limits.

FR-32M / A | The system shall display an agent's own verification progress, decision and available action in the identity workspace. | C4-T15: processing, review, verified, rejected and error states.

FR-33M / B | The administrator directory shall support searching and status filtering, including verified agents whose image audit window is open. | C4-T11: search, filter and three-business-day window boundary.

FR-34M / B | The system shall display available model status and saved evaluation results to authorised administrators. | C4-T16: available report, loading failure and fallback state.



The repeated-attempt defaults are three recorded failures per IP or device within 24 hours; they are configurable guardrail choices and must be tested at their boundaries. Evidence is limited to JPEG or PNG at 5 MiB per file, where 1 MiB equals 1,048,576 bytes. Completing account registration or a selfie challenge does not itself confer verified-agent access.

4.2.2 Non-Functional Requirements

The quality requirements cover performance measurement, security, privacy, reliability, interaction quality, maintainability and model evaluation. Performance is specified through a reproducible measurement protocol. An operational response-time acceptance limit must be justified using measurements in the intended environment and stakeholder needs before it is treated as a service commitment. Cold-start and steady-state behaviour must be reported separately.

Table 4.3: Quality and evaluation requirements

IDPriority /source | Requirement | Verification plan

 | Performance and readiness | 

NFR-01H / A | The evaluation shall measure complete pipeline elapsed time over ten sequential single-user runs in a declared environment, separating warm and cold starts. | C4-T17: record start/end events, median, maximum and all failures.

NFR-02M / A | The evaluation shall measure representative non-pipeline API response times under a declared workload and record the host and network conditions. | C4-T17: authentication, profile, status and administrator queries.

NFR-03M / O | Readiness checks shall distinguish process availability from availability of the model components needed for verification. | C4-T18: service running with model absent, loading or ready.

 | Security and privacy | 

NFR-04H / O | Protected agent operations shall reject missing or invalid authentication and prevent cross-agent access. | C4-T01 and C4-T09: absent/expired token and other-agent identifiers.

NFR-05H / B | Administrator operations shall reject an authenticated user without the administrator role. | C4-T09: agent token against every administrator route family.

NFR-06H / A | Identity images shall remain private; an authorised signed URL shall last at most one hour and shall not outlive an applicable verified-case audit window. | C4-T19: public access denied; expiry and remaining-window boundaries.

NFR-07H / O | Production network connections carrying credentials or identity evidence shall use HTTPS. | C4-T19: inspect frontend, backend, AI and storage endpoints.

NFR-08H / O | Database client access shall be restricted by ownership and role; privileged service credentials shall remain on the server. | C4-T19: policy and configuration inspection plus cross-agent tests.

 | Reliability and failure handling | 

NFR-09H / O | Threshold fallback shall be permitted only when valid complete scores exist and the SVM decision service is unavailable or returns an unusable prediction. | C4-T08 and C4-T18: fallback has a recorded cause and decision basis.

NFR-10H / O | An incomplete or failed evidence-processing step shall not be represented as a successful completed verification. | C4-T18: inject quality, OCR, face, liveness and storage failures.

 | Interaction quality and human oversight | 

NFR-11M / A | The interface shall label each onboarding step and identify the current step, completed steps and the next available action. | C4-T15: walkthrough; record task completion and assistance needed.

NFR-12H / A | Validation and quality failures shall identify the affected field or image and provide a corrective action. | C4-T05 and C4-T15: invalid fields, blur, denied camera and service error.

NFR-13H / B | Each decision shall retain its basis so administrators can distinguish a model result, threshold fallback, quality failure and manual intervention. | C4-T07 and C4-T08: persist and retrieve the correct provenance.

NFR-14H / B | Manual overrides shall require administrator authority and retain the actor, time and resulting access outcome. | C4-T11 and C4-T13: approve/reject override and trace resulting records.

NFR-15M / O | Image quality, OCR, face matching, liveness and decision services shall expose separate contracts that can be checked independently. | C4-T20: module inspection and representative contract tests.

 | Model evaluation and accessibility | 

NFR-16H / R | Model evaluation shall report per-class precision, recall and F1, macro F1, accuracy and a confusion matrix on an isolated evaluation set. | C4-T21: metrics derived from saved predictions and declared labels.

NFR-17H / R | Model evaluation shall report Rejected-to-Verified and Manual-Review-to-Verified errors separately from aggregate accuracy. | C4-T21: explicit numerators, denominators and error interpretation.

NFR-18H / R | Evaluation shall state the synthetic population assumptions and the untested demographic, camera, document and attack conditions. | C4-T21: inspect provenance, evaluated coverage and untested conditions.

NFR-19M / A | Essential form, navigation and review controls shall expose labels, keyboard operation, visible focus and understandable status text. | C4-T15: keyboard and screen-reader checks, including modal focus.

NFR-20M / A | The interface shall preserve essential tasks on desktop and mobile layouts without losing field labels, feedback or access restrictions. | C4-T15: representative desktop and phone widths; both display themes.



Model quality is assessed through the cost-relevant errors as well as aggregate metrics. A comparative improvement on synthetic data is not an absolute operational approval threshold. Deployment acceptance for real applicants requires justified error tolerances and representative evidence. I use selected WCAG 2.2 criteria to plan checks for labels, keyboard operation, focus and status feedback. These checks form part of the planned interface evaluation (World Wide Web Consortium, 2023).

4.2.3 Data Requirements

The transactional data comprise account references, agent profiles, document-object references, verification attempts, six-score records, decisions, access outcomes and audit events. The authentication provider manages passwords and sessions, while the application stores account references. Optional passkeys store credential identifiers, public keys and supporting authentication metadata; the application does not receive the device's local fingerprint or face template through WebAuthn.

Table 4.4 defines the data requirements and the planned checks for each one. I distinguish these design requirements from the results reported in Chapter 5. The data design includes informed collection, retention rules for each decision category and a controlled backup and restoration procedure.

Table 4.4: Data requirements

IDPriority /source | Requirement | Verification plan

DR-01H / A | Profile data shall link a unique user account to personal identity details, validating required values and dates before persistence. | C4-T02: missing fields, duplicate identifier and invalid/future dates.

DR-02H / A | Each stored evidence object shall be associated with an agent and an evidence type, including national ID front/back where required and selfie. | C4-T03: allowed image types, references and correct object ownership.

DR-03H / R | The six-score feature vector shall use the names, order, units and permitted ranges defined in Table 4.5. | C4-T08: missing, non-numeric, non-finite and out-of-range inputs.

DR-04H / O | Requests, scores, decisions and access records shall preserve stable keys and valid relationships while allowing an incomplete attempt to remain incomplete. | C4-T07: uniqueness, foreign keys and interrupted processing.

DR-05H / B | Audit records shall retain structured action context with nullable agent/request links where no corresponding profile or request exists. | C4-T13: registration rejection, authentication and pipeline event cases.

DR-06H / O | Verified-agent evidence images shall expire three business days after the latest successful verification, including manual approval. | C4-T22: Monday-Friday, Africa/Nairobi, weekend and repeated-approval cases.

DR-07H / O | Expired verified-case image cleanup shall preserve document metadata, scores, decisions and audit records and retry failed object removals. | C4-T22: failed removal, cleared references and surviving metadata.

DR-08H / O | Retention periods for pending, review and rejected evidence and retained metadata shall be explicitly defined before operational rollout. | C4-T22: policy review; these cases are excluded from current automatic purge.

DR-09H / A | The onboarding process shall communicate the purpose, access conditions and retention of identity evidence before collection. | C4-T15: inspect disclosure, informed acknowledgement and acceptance evidence.

DR-10H / R | Synthetic data generation shall retain its configuration, seed, source-measurement provenance, label assumptions and duplicate-screening results. | C4-T23: regenerate from configuration and inspect recorded metadata.

DR-11H / R | Training, calibration, selection and evaluation partitions shall be separated so evaluation records do not fit transformations or select candidates. | C4-T23: split manifest, training folds and frozen selection artifacts.

DR-12M / O | The maintainer shall retain controlled backups of necessary metadata, configuration and model artifacts and verify a restoration procedure. | C4-T24: isolated restore and integrity check; record retention and exclusions.



Verification feature contract

The classifier consumes the ordered features in Table 4.5. Raw image-quality values are not interchangeable with arbitrary zero-to-one ratings. The fitted model pipeline performs its defined transformations. When the backend aggregates document and selfie quality, the resulting score must retain the same physical definition and unit used in development. Missing, non-finite or invalid values must not be silently converted to successful evidence.

Table 4.5: Six-feature input contract

Feature | Meaning | Range | Interpretation

face_match_score | Face similarity | 0 to 100 | Document portrait versus selfie; score, not a probability of identity.

liveness_score | Presentation evidence | 0 to 1 | Selfie anti-spoof estimate; evaluation is limited to tested attacks.

ocr_confidence_score | Text agreement | 0 to 1 | Agreement between extracted and registered fields; not proof of authenticity.

blur_score | Laplacian variance | Finite and non-negative | Raw sharpness measure; larger values generally indicate sharper images.

brightness_score | Mean HSV value | 0 to 255 | Raw image brightness.

contrast_score | Grayscale standard deviation | 0 to 127.5 | Raw image contrast.



Training and evaluation data design

The decision-model development dataset contains 10,000 synthetic records: 6,000 Verified, 2,000 Manual Review and 2,000 Rejected. These are experimental class quotas rather than estimates of real applicant prevalence. Each record contains six generated verification-score features and one assumed adjudication label. The earlier 4,000-record dataset is retained as historical work and is not the final experiment described here.

The generator uses stored local measurements from Labeled Faces in the Wild for face matching, NUAA for real/photo presentation scores, and MIDV document frames and OCR measurements. The measurement files and their provenance inform score distributions. They do not provide joint three-class KYC ground truth. The synthetic labels, relationships between channels and uncertain-case scenarios are modelling assumptions. The generator reuses historical measurements rather than reprocessing every source image with the current pipeline.

The original stratified split is 7,000 training, 1,500 validation and 1,500 test records. For version 3 development, the validation partition is divided into 750 calibration and 750 selection records. The original test partition is retired because earlier results informed the follow-up research questions. A fresh 1,500-record evaluation sample, comprising 900 Verified, 300 Manual Review and 300 Rejected cases, is drawn after candidate selection is frozen. This creates 11,500 unique experimental records across the original and fresh datasets, not an 11,500-record training set.

Preprocessing is fitted within training folds during cross-validation. Calibration fits only on its designated partition, and candidate/policy selection uses the separate selection partition. A stored configuration, seed lineage, source hashes, split manifests and duplicate checks support reproduction. The fresh evaluation sample is generated from the same simulator assumptions; it is not independent real-world validation. I distinguish the predeclared release check from model tuning when interpreting the evaluation results.

I distinguish model class probabilities from threshold-rule outputs in the decision records and evaluation. A threshold decision may use 0/1 indicator values for compatibility, but these are not calibrated certainty estimates. The model remains static during a verification request; completed cases do not automatically retrain it. Any later retraining requires a separate offline process using appropriately governed and confirmed data.

Retention and recovery

Verified-case images are retained for three business days after the latest successful decision, including manual approval. Business days are Monday to Friday in Africa/Nairobi; public holidays are not excluded. For example, a Friday approval at 14:00 expires on Wednesday at 14:00. Cleanup is checked at startup and every 15 minutes, so scheduled deletion depends on a running backend. Failed removals are retried; signed links must not extend access beyond the permitted window.

Cleanup removes the image objects and clears their references while retaining metadata, scores, decisions and audit history. Pending, review and rejected cases are excluded from this automatic policy. The retention policy must specify their retention periods and the lifetime of retained metadata. A recovery procedure must also account for storage copies and backups so restored data do not silently reintroduce expired evidence.

4.2.4 Interface and Integration Requirements

The design separates the Vue presentation layer, Express application layer, Flask AI layer and Supabase persistence and identity services. The hosted arrangement uses Vercel for the frontend, Render for the backend and Microsoft Azure Container Apps for the AI service. Supabase provides authentication, PostgreSQL, object storage and database-change events. This deployment allocation preserves the logical separation. Chapter 5 describes the hosted environment, configuration and available evaluation evidence.

The browser communicates with the application API using JSON or multipart uploads and bearer authentication. Email/password and Google authentication use Supabase Auth. The backend verifies identity, role and object ownership before protected operations. Server-held Supabase and AI credentials are not included in browser code. Camera permission and browser support are prerequisites for the live capture flow; password and Google recovery paths remain available when passkeys are unsupported.

The backend coordinates separate quality, OCR, face, liveness and SVM requests. Quality, OCR, face and liveness endpoints consume image data; the SVM endpoint consumes the six-score JSON vector. For the hosted AI service, a server-held API key accompanies requests. The configured SVM call timeout defaults to five seconds. The integration design requires documented timeout limits, bounded retries and controlled failure responses for each external service.

An unavailable SVM can trigger a logged threshold decision only after a complete valid score vector exists. Failure of the whole AI service before evidence extraction cannot be repaired by classifying missing scores. Such a failure returns a controlled error or incomplete state. Automatic retries of writes must not create duplicate profiles, requests, decisions or access records; the verification plan therefore includes retry checks at each operation boundary.

Files are written to private storage and retrieved as buffers for processing. Authorised administrator image views use signed URLs lasting no more than one hour and, for verified cases, no longer than the remaining image audit window. Socket.io conveys review notifications after database INSERT or UPDATE events place a request into review. Recipient authorisation, reconnect behaviour and consistency with the persisted queue are separate verification concerns.

Table 4.6: Interface and integration requirements

IDPriority /source | Requirement | Verification plan

IR-01H / A | The browser interface shall support labelled onboarding, role-appropriate navigation and inline validation on desktop and mobile devices. | C4-T15: wireframe walkthrough and implementation accessibility checks.

IR-02H / O | Protected backend requests shall carry a valid Supabase bearer token and be checked for the required role and resource ownership. | C4-T01 and C4-T09: 401/403 and cross-agent scenarios.

IR-03H / O | Backend-to-AI calls shall use the defined REST contracts, with multipart images or JSON scores and structured JSON responses. | C4-T20: each endpoint input/output contract and invalid response.

IR-04H / O | Calls to the hosted AI service shall authenticate using the server-held API credential over HTTPS. | C4-T19: absent/wrong credential, secret location and transport inspection.

IR-05H / O | The decision-service call shall use its configured timeout; other integration calls shall have an explicitly documented failure and retry policy. | C4-T18: timeout, service refusal and bounded retry behaviour.

IR-06H / O | The storage integration shall upload and retrieve private objects through authorised server operations and issue bounded signed image links. | C4-T03 and C4-T19: upload failure, private retrieval and expiry.

IR-07M / B | Review notifications shall connect database review-state events to the administrator interface and recover from a disconnected client. | C4-T12: insert/update transition, toast and reconnect; check recipient access.

IR-08M / A | Passkey integration shall use browser WebAuthn support and server verification while leaving established recovery sign-in methods available. | C4-T14: browser capability, challenge verification and recovery.

IR-09H / A | Camera capture shall request permission, report an unavailable camera and show the preview used to produce the submitted evidence. | C4-T04 and C4-T15: allow/deny permissions and capture framing.

IR-10M / B | The administrator evaluation interface shall label saved metrics with their model and dataset context and show an explicit unavailable-report state. | C4-T16: report metadata, missing report and active/fallback indicator.



4.3 System Analysis Diagrams

4.3.1 Use Case Diagram

The use case view identifies the agent and administrator services within the identity-verification workflow. It relates registration and evidence submission to FR-01 to FR-13, controlled access to FR-14 to FR-16, and administration and auditing to FR-19 to FR-26. Its purpose is to clarify responsibility and the service boundary.

Figure 4.1: Use Case Diagram

The agent initiates onboarding and checks the outcome; the administrator reviews exceptions and inspects the audit history. Automated evidence processing supports those user goals. Eligibility for the protected workspace is a business precondition evaluated from the access decision. Visiting an outcome screen does not grant access; the recorded access decision controls entry. The AI processing layer is a system component in the architecture described in Section 4.4.3.

4.4 System Design Diagrams

4.4.1 Class Diagram

The class view organises the domain concepts used to describe accounts, agents, documents, verification attempts, processing results, decisions and access. It supports the separation of responsibilities required by FR-07 to FR-13 and NFR-15. The conceptual model provides vocabulary for implementation without requiring every concept to become a separate database table.

Figure 4.2: Class Diagram

A verification attempt provides the context for image-quality, OCR, face-match and liveness results. The decision consumes completed evidence, while access enforcement consumes the decision. Audit events refer to the relevant agent or request when those objects exist. I represent ownership through the relationships in the model and specify the supporting keys, validation and transaction boundaries in the data design. These controls address orphaned records and partially completed attempts.

4.4.2 Entity Relationship Diagram

The entity relationship view describes the persistent registration and verification records and their associations. It supports DR-01 to DR-05 by linking identity evidence and decisions to the relevant agent and request. The logical entity catalogue in Section 4.4.5 identifies the attributes and integrity rules needed by the current design.

Figure 4.3: Entity Relationship Diagram

An account may exist before an agent profile is completed, and a request may exist before scores or a decision have been produced. A unique request reference permits at most one associated score row or decision row; it does not force the child row to exist. This distinction represents pending and failed attempts without requiring a completed result. Audit references may be absent for authentication or blocked registration events that occur before profile creation.

4.4.3 System Architecture Diagram

The architecture view separates presentation, application coordination, evidence inference and persistent records. The four logical layers support the interface requirements in Table 4.6 and allow the verification services to be evaluated independently. The hosted service allocation does not change the responsibilities of these layers.

Figure 4.4: System Architecture Diagram

The frontend sends authenticated requests to the backend, which coordinates AI calls and persistence. Responses return through the relevant interfaces. Supabase authentication and database-change events introduce additional interactions, while review notifications travel from the backend to the administrator interface. Model-stage fallback depends on valid existing scores; a complete evidence-service outage instead leaves an error or incomplete attempt. Layer separation supports component replacement through defined interfaces. A replacement still requires integration checks against those interfaces.

4.4.4 Sequence Diagram

The sequence view describes the progression from evidence submission to a recorded outcome and administrator review where required. It supports FR-07 to FR-16 and FR-24. The runtime design uses the backend to coordinate the individual AI endpoints and to associate their results with a verification request.

Figure 4.5: Sequence Diagram

Quality assessment gates subsequent processing. The backend stores the quality record and updates it as OCR, face and liveness evidence becomes available, then requests classification and applies the access decision. Audit events accompany the defined significant steps. A failed early step does not become a successful classifier input, and a manual-review outcome withholds verified workspace access. Administrator intervention is a separate authorised action that changes the recorded decision and access state.

4.4.5 Database Schema

The schema view presents the persistent entities, while Table 4.7 provides the logical keys, attributes and integrity conditions required by the current system. The logical design is the focus of this chapter; exact SQL declarations, indexes and deployed policy scripts are implementation evidence for Chapter 5.

Figure 4.6: Database Schema

Profile, evidence, verification and decision records are separated to avoid repeating personal data in every attempt. Unique keys prevent duplicate associations, foreign keys maintain valid references, and allowed status values constrain state representation. Access-control policy and audit append-only behaviour require separate enforcement. Restricting inserts does not by itself prohibit updates or deletion. Privileged service operations remain outside ordinary-client row policies, so administrator database privileges must be governed separately.

Table 4.7 records the logical schema independently of implementation-specific SQL types. Each identifier denotes a stable key. The operational schema uses UUID identifiers; the logical rules allow an uncompleted account or attempt to exist without its later records.

Table 4.7: Logical entity and integrity catalogue

Entity | Important attributes | Relationship and integrity rule

users | user_id; email; role; created_at | Account reference; unique email; identity is linked to Supabase Auth.

agents | agent_id; user_id; full_name; phone_number; national_id; date_of_birth | user_id is unique; an account has zero or one agent profile. national_id is unique.

documents | document_id; agent_id; document_type; file_url; uploaded_at | An agent may have several evidence records. Expired images can have cleared file references.

verification requests | request_id; agent_id; document_id; status; created_at | Each request belongs to an agent and references its identity evidence.

verification scores | score_id; request_id; six score attributes | request_id is unique. An attempt may have no score record before processing.

kyc decisions | decision_id; request_id; final_decision; class probabilities; decision_basis; decided_at | request_id is unique. A decision is absent until processing or intervention produces one.

access control records | record_id; agent_id; decision_id; access_granted; enforced_at | decision_id is unique; the record reflects the enforced outcome.

audit logs | log_id; agent_id; request_id; action; outcome; details; performed_by; ip_address; timestamp | Agent/request references may be absent for early events. Ordinary clients cannot alter entries.

passkeys and authentication support | Credential public key and identifier; user reference; counter; label; device metadata; challenge/rate-limit records | Optional authentication extension. Private keys and device biometrics remain outside the application.



The core separation reduces duplication: account identity, personal profile, evidence metadata and repeated verification attempts are distinct. Derived scores and decisions reference the attempt instead of copying the profile. Structured audit details support varied event context without adding a column for every event type. The optional passkey support entities extend authentication rather than the classifier feature set. The implementation checks cover the deployed policies and schema migrations that enforce these rules.

4.4.6 User Interface Design and Wireframes

I use grayscale wireframes to document the principal screens and interaction states of the current system. Bracketed placeholders represent input fields, images and report values. Each wireframe is linked to the requirements it supports and is accompanied by an explanation of its controls, navigation and error states.

Agents move from authentication through details, document capture, selfie and outcome. Administrators navigate the directory, review, audit and model views. The desktop sidebar collapses into a mobile menu; paired fields stack in reading order. Only an authorised verified outcome permits workspace access.

4.4.6.1 Account registration and sign in

The authentication wireframe separates account creation from sign-in. It provides the entry point for an agent or administrator before protected functions are offered. Registration gathers the account details, while sign-in presents password, Google and supported passkey options.

Requirements addressed: FR-01, FR-06, FR-27 to FR-29; NFR-04; IR-02 and IR-08.

Figure 4.7: Account registration and sign in wireframe

Persistent labels identify the required inputs and a dedicated message region exposes validation or authentication failures. Password recovery and confirmation messages retain a route back to sign-in. The human-check control reflects the current password-login interface; its accessible alternative remains part of accessibility evaluation. Passkey cancellation returns control to established sign-in methods. The two panels represent separate screens, not one combined form.

4.4.6.2 Personal profile details

The profile wireframe is the first protected onboarding step. It links the authenticated email to the identity details later compared with the document and displays the four-stage progress indicator.

Requirements addressed: FR-02 and FR-05; NFR-11, NFR-12; DR-01; IR-01.

Figure 4.8: Personal profile details wireframe

The account email is read-only. Full name, phone number, national ID and date of birth remain grouped as one task, with validation beside the affected input. The Next action persists valid details before advancing. On a narrow screen, the paired fields stack in reading order. Existing values are restored when the user returns, and a duplicate national ID produces an explicit conflict rather than a second profile.

4.4.6.3 Identity document capture

The document wireframe combines document-type selection, camera or file input, preview and image-quality feedback. It represents the selected capture step; national ID front and back are captured in sequence, while passport and driving-licence flows use their relevant document face.

Requirements addressed: FR-03, FR-07, FR-08 and FR-31; DR-02; IR-06 and IR-09.

Figure 4.9: Identity document capture wireframe

Capture guidance is placed beside the preview and quality feedback remains visible before continuation. A user may retake or replace an image. The action changes from quality checking to continuation when the check succeeds. Rejected type/size, permission denial and service errors keep the user on the affected step. A successful image-quality check improves suitability for processing but does not establish that the document is authentic.

4.4.6.4 Live selfie and challenge

The selfie wireframe provides a live preview, a face-position guide and the instruction for the current capture challenge. It separates capture readiness from later model-based liveness scoring.

Requirements addressed: FR-04 and FR-11; NFR-11 and NFR-12; IR-09.

Figure 4.10: Live selfie and challenge wireframe

The first instruction asks the user to face the camera; the next displays the selected movement or blink task. Status text reports progress without relying only on colour. The user can retry after a failed capture or return to the previous step. The camera-permission error provides guidance on restoring access. The capture challenge supports the live-capture workflow; its completion alone does not demonstrate resistance to every presentation attack.

4.4.6.5 Verification progress and decision states

The verification wireframe presents the processing state and the principal outcome alternatives. The four state panels are shown together for design inspection; the operational interface displays the state relevant to the current attempt.

Requirements addressed: FR-08 and FR-13 to FR-16, FR-31 and FR-32; NFR-09 to NFR-13.

Figure 4.11: Verification progress and decision states wireframe

Only a verified outcome with an authorised access grant exposes the protected-workspace action. Review explains that an administrator must decide. Rejection and capture failure show the reason and a permitted next action; the interface must distinguish retaking poor evidence from an identity decision. The recorded decision basis distinguishes a model result from threshold fallback. A retry is offered only while the backend permits it, and a failed integration does not show a success state.

4.4.6.6 Administrator directory

The administrator directory provides an overview of agents, review workload and current model status. Role-specific navigation connects the directory with the review queue, recent verified cases, flagged attempts, audit records and model evaluation.

Requirements addressed: FR-19, FR-21, FR-23 and FR-33; NFR-05; DR-06.

Figure 4.12: Administrator directory wireframe

The search and status controls narrow the displayed agent set. Each row provides status, an audit deadline when applicable and a route to case detail. Recently verified cases use the three-business-day image window, while the broader directory retains record history after images expire. Real-time review notifications invite the administrator to open a case; the persisted queue remains the reference if a notification is missed. Counts in the wireframe are placeholders, not study results.

4.4.6.7 Administrator case review

The case-review wireframe groups identity images, registered and extracted fields, the six scores, decision provenance and available administrator actions. It abstracts the existing detail drawer into a readable design view.

Requirements addressed: FR-19 to FR-21 and FR-24; NFR-13 and NFR-14; DR-03 to DR-07.

Figure 4.13: Administrator case review wireframe

The reviewer can compare evidence before deciding, inspect the audit history and close the case without making a change. Approve and Reject are authorised backend actions. A rejection dialog may record a reason; actor, time and outcome must be retained for either decision. An expired image is labelled unavailable while its metadata remains visible. Deleted images are unavailable for further inspection. Administrators interpret model probabilities alongside the retained scores, decision basis and audit history.

4.4.6.8 Audit history and export

The audit wireframe makes actions, outcomes and responsible actors available for administrator inspection. Pagination supports navigation through the event history, and a separate export dialog defines the requested subset.

Requirements addressed: FR-22, FR-24 to FR-26; DR-05; NFR-05.

Figure 4.14: Audit history and export wireframe

Date and optional agent filters determine the CSV output. Export retains server-side role checks and exposes a readable failure if the request cannot complete. The log view contains no editing or deletion control for ordinary administrator use. Empty results must be distinguished from loading errors. The dialog is shown alongside the log for documentation and would appear as an overlay during use.

4.4.6.9 Passkey management

The passkey wireframe provides account-level enrolment and credential management outside the evidence-capture flow. It identifies the registered device credentials without displaying secret key material or local device biometric templates.

Requirements addressed: FR-28 to FR-30; IR-08; NFR-19.

Figure 4.15: Passkey management wireframe

Each credential shows its label, device metadata and relevant dates, with Rename and Remove actions. Removal opens a confirmation dialog and remains subject to available recovery methods. Unsupported devices retain existing authentication routes. Loading, cancellation and failure messages are exposed in a status region. A successful registration does not bypass identity verification or grant access to the verified workspace.

4.4.6.10 Model evaluation interface

The evaluation wireframe presents the saved model report to an administrator, including aggregate metrics, class-specific results and the confusion matrix. It links the report to its model and dataset context.

Requirements addressed: FR-34; NFR-16 to NFR-18; IR-10.

Figure 4.16: Model evaluation interface wireframe

The view distinguishes saved synthetic evaluation from current applicant outcomes and exposes a fallback or unavailable-report state. The wireframe uses placeholders for report values. The report is designed to display class-specific recall and false-verification errors alongside the aggregate metrics. The interface supports inspection; it does not initiate online training or establish that a hosted service is running the same model version as a local report.

Interface states and responsive behaviour

Each asynchronous screen distinguishes loading, empty, success and failure states. The interface keeps the relevant error beside the affected task, avoids duplicate submission while a request is active and preserves a route to recovery. The backend enforces access to protected content independently of the controls displayed in the browser. Text labels supplement colour, navigation exposes the current location and modal focus returns to its trigger on dismissal.

On a phone, the navigation menu precedes the task, form columns become a single sequence and image previews retain their aspect ratio. Wide administrator tables require controlled horizontal navigation or an equivalent readable presentation. Both light and dark modes require contrast and focus checks. The evaluation plan includes device and assistive-technology checks for camera and human-check accessibility.

Table 4.8: Interface state coverage

View group | Important state or exception | Verification

Authentication | Unconfirmed email; failed credentials; cancelled passkey; recovery link | C4-T01, C4-T14

Profile and capture | Invalid field; duplicate ID; denied camera; poor image; partial recapture | C4-T02 to C4-T05

Verification | Processing; verified; review; rejected; unavailable service | C4-T08, C4-T09, C4-T18

Administrator | Empty queue; new review event; expired images; authorised intervention | C4-T11, C4-T12, C4-T22

Audit and model report | No matches; failed export; missing report; active/fallback distinction | C4-T12, C4-T13, C4-T16



4.5 Requirements Traceability and Verification Plan

I use the traceability matrix to connect the project objectives, requirements, design views and planned checks. The objective references follow the five themes used in the project evaluation: O1 investigates existing registration and verification practice; O2 identifies challenges and fraud risks; O3 examines existing KYC platforms; O4 develops the system; and O5 tests and validates effectiveness. O1 and O3 supply research context through the literature review, while O2, O4 and O5 directly drive the software and evaluation requirements.

Table 4.9 links each requirement group to its objective, design reference and planned verification scenario. The complete scenarios are listed in Table 4.10. In C4-T01, C4 identifies this chapter, T identifies a planned test scenario and 01 is its sequence number. I use these references consistently throughout Chapter 4; Chapter 5 retains its separate TC identifiers for reported tests. A scenario reference identifies the check to perform, while the test record supplies its result.

Table 4.9: Requirements traceability matrix

Requirement group | Objective and need | Design reference | Scenario

FR-01 to FR-06; FR-27 | O2, O4; A/O | 4.2.1; Figures 4.7-4.10 | C4-T01 to C4-T04

FR-07 to FR-12; FR-31 | O2, O4; A/O | 4.2.1; Figures 4.2, 4.5, 4.9-4.11 | C4-T05 to C4-T07

FR-13; FR-34 | O4, O5; B/R | 4.2.3; Figures 4.4, 4.16 | C4-T08, C4-T16, C4-T21

FR-14 to FR-16; FR-32 | O2, O4; A/O | 4.4.4; Figure 4.11 | C4-T09, C4-T15

FR-17 and FR-18 | O2, O4; O | 4.2.1 guardrails | C4-T10

FR-19 to FR-21; FR-33 | O4, O5; B | Figures 4.12 and 4.13 | C4-T11

FR-22 to FR-26 | O2, O4; B/O | 4.4.5; Figure 4.14 | C4-T12, C4-T13

FR-28 to FR-30 | O4; A/O | 4.2.4; Figures 4.7 and 4.15 | C4-T14

NFR-01 to NFR-03 | O5; A/O | 4.2.2; 4.2.4 | C4-T17, C4-T18

NFR-04 to NFR-08 | O2, O4; A/B/O | 4.2.4; 4.4.5 | C4-T01, C4-T09, C4-T19

NFR-09 and NFR-10 | O2, O4; O | 4.2.4; 4.4.4 | C4-T08, C4-T18

NFR-11 and NFR-12; NFR-19 and NFR-20 | O4, O5; A/B | 4.4.6 all wireframes | C4-T05, C4-T15

NFR-13 and NFR-14 | O2, O4; B/O | 4.4.5; Figure 4.13 | C4-T07, C4-T08, C4-T11, C4-T13

NFR-15 | O4; O | 4.4.1; 4.4.3 | C4-T20

NFR-16 to NFR-18 | O5; R/B | 4.2.3; Figure 4.16 | C4-T21

DR-01 to DR-05 | O2, O4; A/B/O/R | Tables 4.5 and 4.7 | C4-T02, C4-T03, C4-T07, C4-T08, C4-T13

DR-06 to DR-09 | O2, O4; A/O | 4.2.3; Figures 4.12 and 4.13 | C4-T15, C4-T22

DR-10 and DR-11 | O5; R | 4.2.3 experimental data design | C4-T23

DR-12 | O4, O5; O | 4.2.3 recovery policy | C4-T24

IR-01 and IR-09 | O4; A | 4.4.6; Figures 4.8-4.10 | C4-T04, C4-T15

IR-02 and IR-04 | O2, O4; O | 4.2.4 authentication boundaries | C4-T01, C4-T09, C4-T19

IR-03 and IR-05 | O4, O5; O | 4.2.4; Figure 4.4 | C4-T18, C4-T20

IR-06 and IR-07 | O4; A/B/O | 4.2.4; Figures 4.12-4.14 | C4-T03, C4-T12, C4-T19

IR-08 and IR-10 | O4, O5; A/B | Figures 4.15 and 4.16 | C4-T14, C4-T16



Table 4.10: Planned verification scenarios

Scenario | Focus | Required evidence

C4-T01 | Account and session | Valid and invalid login, confirmation, recovery, expired tokens and protected endpoints.

C4-T02 | Profile and guardrails | Valid profile, missing/invalid values, duplicate national ID and blocked email domains.

C4-T03 | Evidence storage | JPEG/PNG, 5 MiB boundary, document type/sides, private object ownership and upload failure.

C4-T04 | Live capture | Camera permission, framing, challenge completion, failure and browser/device compatibility.

C4-T05 | Quality and recapture | Clear/degraded evidence, downstream gate, explanatory feedback and targeted recapture.

C4-T06 | Evidence processing | OCR agreement, matching/non-matching faces and tested genuine/spoof presentations.

C4-T07 | Persistence and provenance | Linked scores/decisions/access records, partial attempts, key integrity and decision basis.

C4-T08 | Classifier contract | Six valid features, invalid/missing values, class-probability mapping and SVM fallback.

C4-T09 | Role and access | Verified/review/rejected access, unauthorised administrator calls and cross-agent identifiers.

C4-T10 | Repeated attempts | IP and fingerprint limits, configured 24-hour window and limit boundary.

C4-T11 | Administrator workflow | Directory/search, review/override, images, audit deadline and attempt history.

C4-T12 | Notification and export | Review-state events, reconnect, recipient access, CSV date/agent filtering and failure.

C4-T13 | Audit accountability | Required events, actor/context, early nullable references and forbidden client mutations.

C4-T14 | Passkeys | Enrolment, signatures, challenge expiry/replay, ownership, rename, removal and recovery.

C4-T15 | Interface and accessibility | Wireframe tasks, state feedback, keyboard/focus, mobile layout, disclosure and assistance.

C4-T16 | Model report interface | Correct model/data labels, active/fallback state and unavailable report.

C4-T17 | Performance measurement | Declared hosts/network, cold/warm runs, whole pipeline and representative API timings.

C4-T18 | Failure and readiness | Service/model unavailability, timeout, invalid response, partial persistence and safe retries.

C4-T19 | Data protection | HTTPS, API credentials, client ownership policies, private objects and signed-link expiry.

C4-T20 | Service contracts | Independent image/score endpoints, defined inputs, outputs, errors and compatibility.

C4-T21 | Model evaluation | Held-out metrics, confusion matrix, false verification, calibration and stated limitations.

C4-T22 | Retention | Business-day expiry, repeat approvals, cleanup retries, metadata and non-verified policy scope.

C4-T23 | Experiment reproducibility | Configuration/seed/source records, duplicates, split isolation and fitted preprocessing.

C4-T24 | Recovery | Controlled backup, isolated restoration and record/model integrity without premature data deletion.



Evaluation records and change control

For system-level verification, I specify dated records of the environment, software and model revision, input conditions, expected and actual results, and linked requirement. The evaluation plan covers latency, demographic fairness, presentation-attack coverage, accessibility, informed disclosure and restoration. Chapter 5 reports the resulting evidence and evaluation limitations. Changes to a requirement are reflected in the related interfaces, data rules, diagrams and verification scenarios.

4.6 Chapter Summary

The design connects account registration and controlled evidence capture with six-score processing, an explicit decision basis and role-dependent access. Administrator review, audit history, bounded image retention and optional passkeys support the main workflow. The requirements catalogue, logical entity description, interface wireframes and traceability plan establish what the implementation and evaluation must demonstrate. Chapter 5 reports the implemented environment, actual tests, classifier results and remaining evidence limitations.

References

ISO/IEC. (2023). Systems and software engineering - Systems and software Quality Requirements and Evaluation (SQuaRE) - Product quality model (ISO/IEC 25010:2023).

https://www.iso.org/standard/78176.html

ISO/IEC/IEEE. (2018). Systems and software engineering - Life cycle processes - Requirements engineering (ISO/IEC/IEEE 29148:2018).

https://www.iso.org/standard/72089.html

World Wide Web Consortium. (2023). Web Content Accessibility Guidelines 2.2 and supporting quick reference.

https://www.w3.org/WAI/WCAG22/quickref/


---

## Chapter_5_Aligned_Chapter_4.docx

Chapter 5 System Implementation Testing and Evaluation

Intelligent Agent Identity Verification System

5.1 Introduction

In this chapter, I explain how I implemented the system design, the environment in which it ran, and the testing and evaluation completed. The system registers agents, collects identity evidence, combines document and biometric scores, and supports verification decisions and controlled access. I distinguish the amended Chapter 4 requirements from inspected source code, confirmed deployment information and executed tests. Proposed controls remain outstanding where implementation or test evidence is absent.

The chapter follows a hybrid software and machine learning structure. Sections 5.2 and 5.3 describe the environment, the deviations from the approved design, the implemented modules and workflow, and the dataset and model development procedure. Section 5.4 reports the tests and classification results, Section 5.5 describes the version-control evidence, Section 5.6 declares the AI-assisted tools used, and Section 5.7 discusses the results against the project objectives and states the limitations. The latest saved model, version 3.0.0, achieved 75.800% accuracy on 1,500 fresh synthetic cases. This result was measured under the simulator assumptions described in Section 5.3.6 and does not represent operational identity verification accuracy.

5.2 Implementation Environment

5.2.1 Hardware and Deployment Environment

I developed the system locally and deployed the Vue frontend on Vercel, the Express backend on Render and the Flask AI service on Microsoft Azure Container Apps. I use the Supabase Free plan for authentication, PostgreSQL and storage, with the project hosted in Ireland. I confirmed these deployment details on 30 October 2026. I confirmed successful operation of the hosted workflow on 27 October 2026. Local development used ports 5173, 3000 and 5000, while the public services used HTTPS. Table 5.1 separates the development equipment from hosting information; these are not measured minimum requirements.

Table 5.1: Implementation environment and evidence

Layer | Configuration | Evidence

Development machine | AMD Ryzen 5 5625U with Radeon Graphics; 7.4 GiB OS-reported usable memory; C: volume 475.8 GiB; Windows 11 Home Single Language, version 10.0.26200 | Host inventory on 23 October 2026; current development machine, not a benchmarked minimum

Client browser | Camera-capable browser required; historically tested browser names and versions were not recorded | No browser-compatibility verdict established

Application services | Development: Vue 5173, Express 3000, Flask 5000. Hosted: Vercel frontend and Render backend over HTTPS. | Deployment confirmed by me; frontend and backend health checked 27 October 2026

AI service hosting | Microsoft Azure Container Apps; South Africa North hostname; public HTTPS AI service. Compute tier not recorded. | Deployment confirmed by me; AI health endpoint returned HTTP 200 on 27 October 2026

Data services | Supabase Free plan for authentication, PostgreSQL and storage; project region: Ireland. | My confirmation of the project configuration on 30 October 2026; SQL scripts and supplied database exports.

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



Backend configuration supplied the Supabase URL and keys, the AI service URL, the listening port and authentication settings. Service-role credentials remained server-side. Optional passkeys required a configured relying-party identifier, allowed origins and Node.js 22 or newer. The isolated classifier environment used Python 3.13.3, scikit-learn 1.9.0, NumPy 2.5.3 and Flask 3.1.3, verified during the 23 October 2026 test run. The full image-processing requirements left EasyOCR, InsightFace and PyTorch unpinned. Those packages were not installed in the inspected general Python environment, so their historically tested versions could not be established. The deployed AI hostname identified the Azure South Africa North region. The Supabase project is hosted in Ireland. Azure compute allocation and the Render and Vercel service tiers were not recorded. The Render backend connected to the Azure AI endpoint; the frontend used the public backend address. Deployment secrets remained outside the report. The dependency versions above describe the recorded local experiment, not an independently inspected cloud runtime.

Origin configuration. In backend/server.js, the HTTP CORS check combines http://localhost:5173 and http://127.0.0.1:5173 with comma-separated FRONTEND_URL values. It accepts requests without an Origin header and rejects origins outside that list. Socket.IO uses the same allowedOrigins list with GET and POST. The local source therefore retains development origins alongside configured frontend origins. ai-service/app.py uses unrestricted CORS(app). The deployed FRONTEND_URL values and effective HTTP and real-time origin behaviour have not been verified.

The amended IR-12 requires explicit production HTTPS origins, separate development settings and coverage of HTTP and real-time connections. The source configuration does not establish those conditions. CORS controls whether browser scripts can read cross-origin responses; it does not authenticate an API caller (Express, n.d.). Bearer-token and role checks, backend-to-AI credentials and WebAuthn origin validation are separate controls. The backend AI client sends X-API-Key when configured and requires a sufficiently long key for a non-local AI host; this source inspection does not establish the deployed secret or its enforcement.

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

Recovery design and current evidence. Supabase lists automatic backups and point-in-time recovery as excluded from Free. Its database backups contain Storage metadata, not the image objects themselves (Supabase, n.d.-a, n.d.-b; checked 29 October 2026). I use the Free plan and maintain a separate daily scripted backup to Google Drive.

Under the amended DR-12, I propose encrypted daily exports of necessary database records, restricted access and seven-day backup retention, with controlled copies of model artifacts and deployment configuration maintained separately. Raw identity images are excluded from the proposed off-site backup set. Restoration must use an isolated environment and verify record relationships, model hashes, access policies and retention deadlines before access resumes. Expired-data deletions and documented preservation decisions must be reapplied; restored metadata must not make deleted image evidence appear available. Lost images would require lawful recollection where necessary.

I back up the Supabase database to Google Drive using code that runs daily. This records my current backup practice; the script, execution logs and backup contents have not been independently inspected for this evaluation. Encryption, access restrictions, seven-day backup expiry, exclusion of raw identity images and separate model/configuration copies remain unverified. I have not performed a restoration. Backup creation is therefore reported as an operational practice, while the isolated-restoration and integrity checks required by C4-T24 remain untested.

5.3 System Implementation

The implemented architecture separated presentation, application coordination, image analysis and persistence. The browser guided evidence capture, the Express server managed protected operations, and the Flask service produced the numerical evidence used for classification. The subsections below follow this architecture and the Chapter 4 design. In the hosted arrangement, the browser loaded the Vercel frontend, which called the Render API. The backend coordinated requests to the Azure AI service and Supabase. This preserved the separation between the user interface, application logic, inference and persistent records.

5.3.1 Design Changes and Implementation Gaps

Table 5.3 preserves the recorded design changes from the earlier draft. The amended Chapter 4 additionally specifies retention, consent, recovery, human-check and origin controls. I compare these requirements with the source inspected on 29 October 2026 in the following subsections. A requirement or proposed policy is not treated as an implemented control or a passing test.

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

The inspected documentRetentionService.js considers the latest request for each agent and skips it unless its status is verified. For eligible verified cases, the audit window expires three business days after the successful decision; business days are Monday to Friday in Africa/Nairobi, without public-holiday exclusions. The job runs at startup and every fifteen minutes while the backend is running. It removes eligible image objects and clears file references while retaining document rows, scores, decisions and audit history. Failed removals leave references available for a later cleanup attempt. This describes the source; live deletion scheduling and object removal have not been demonstrated.

The amended DR-08 instead requires each pending, review or rejected image to expire 30 calendar days after upload, including abandoned uploads. Viewing or a status change must not restart this deadline. Verification metadata, scores, decisions, consent records and related audit history are to expire 180 calendar days after attempt closure, unless a documented lawful preservation obligation applies. Closure is a final verified or rejected decision, or expiry of an incomplete attempt. These are proposed project periods, not statutory retention periods.

The current verified-only purge does not implement the 30-day policy, an abandoned-upload expiry path, the 180-day metadata lifecycle or the preservation-exception record. The amended DR-07 limits metadata preservation to its defined period, and NFR-06 requires signed URLs not to outlive the applicable image deadline. The existing verified-case window supplies only part of this behaviour. Expiry enforcement for non-verified evidence and safe reapplication after restoration remain implementation and testing gaps.

5.3.3 Application Modules

Authentication, roles and passkeys. Authentication middleware rejected missing or invalid bearer tokens, and role middleware restricted administrator operations. Email/password and Google sign-in were supplemented by WebAuthn passkeys using SimpleWebAuthn. The public.passkeys table stored the credential identifier, public key, signature counter, transports, device type, backup status, label and device metadata; the application did not receive device fingerprint or face templates from WebAuthn. Challenge and rate-limit records were stored separately. Client support detection controlled which passkey actions were offered. WebAuthn relying-party, origin and fresh-challenge validation are distinct from the HTTP CORS policy (World Wide Web Consortium, 2021).

Human check. The internal captcha.js utility generates a five-character image challenge, stores its answer in process memory and sets a five-minute lifetime. The first validation attempt consumes the challenge, whether the answer is correct or incorrect. authController.js checks the CAPTCHA before calling password authentication and returns missing/invalid-challenge feedback. LoginPage.vue provides a refresh button and a labelled input. No external CAPTCHA provider is integrated.

A process restart loses outstanding challenges, and separate backend processes do not share the in-memory challenge map. A challenge generated on one instance may therefore fail on another unless deployment routing or a shared store addresses this. Neither arrangement was verified. The image description and refresh control do not provide a non-visual solution. Google sign-in and optional registered passkeys are other account-access paths, but their availability and accessibility do not establish an equivalent alternative for every password user. The accessible-alternative part of IR-11 and restart/multiple-instance behaviour remain untested.

Browser integration. The HTTP, Socket.IO and AI CORS settings described in Section 5.2.2 are source findings. An allowed origin does not bypass authentication, and absence of an Origin header is not proof of a trusted caller. Production origin separation, permitted/unlisted-origin preflights and real-time behaviour require C4-T26 execution against the actual deployed configuration.

Registration and evidence capture. Agents entered personal details and supplied document and selfie images through the capture interface. Server upload middleware accepted JPEG and PNG MIME types and imposed a 5 MiB limit per file, returning a validation message for unsupported or oversized files. Registration logic checked existing national identity numbers. The storage integration used a private Supabase bucket; its deployed access settings were not live-tested in this update.

Disclosure and consent. The inspected frontend, backend and database files did not contain the proposed pre-collection consent control, a corresponding account/purpose/notice-version/server-timestamp record, backend enforcement of that record, or withdrawal handling. Under amended DR-09, these controls are required where consent is the approved processing basis. Account registration and submission of images do not demonstrate that this requirement has been met. Both the collection controls and the applicable processing basis remain unresolved; the proposed notice alone does not close DR-09.

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

Audit logging. The central utility attempts to insert standardised action and outcome records for significant operations, with contextual identifiers and a server timestamp. Its error handling logs failures and returns null rather than guaranteeing persistence. I therefore distinguish an inspected logging call from a successfully stored audit event.

5.3.4 End-to-End User Workflow

The implemented workflow connected the following interface, application and database operations. The sequence describes code paths; the live execution status is reported separately in Table 5.10.

The agent signed up or signed in. The backend validated the token and role, and the guardrail middleware checked the national identity number, the email domain and recent failed attempts.

The agent entered personal details, which were stored in the agents table and linked to the user record.

The agent uploaded the identity document and captured a selfie. Format and size were validated in the browser and on the server, and the files were stored in the private bucket with a documents record. The inspected flow did not enforce the amended pre-upload consent requirement; C4-T27 addresses this gap.

The backend sent both images to the quality service. A failed check returned specific reasons, such as an image being too blurry or too dark, and asked the agent to resubmit.

Images that passed went through OCR, face matching and liveness scoring, and the six scores were stored in verification_scores.

The classifier returned a class and probabilities. The backend stored the decision with its decision_basis and wrote the access_control_records entry.

The agent saw the outcome. Manual Review cases appeared in the administrator queue, where an approval or rejection updated the decision and access records.

Defined significant steps call the audit utility. Reconstruction of an individual request requires the corresponding persisted audit rows; the request, score and decision exports alone do not establish a complete audit sequence.

The supplied live-test evidence consisted of database exports rather than interface screenshots. Their aggregate results are reported in Table 5.10. Personal identifiers and image links are omitted from the chapter. Figures 5.1 and 5.2 show the separate recorded model evaluation.

5.3.5 Exception Handling and Decision Provenance

At the AI endpoint, an unavailable or inconsistent model bundle produces an unavailable-service response. At application level, complete valid scores may enter threshold fallback when SVM inference is unavailable or unusable. The decision basis is placeholder_threshold, and the rule outputs are not calibrated probabilities. These application paths are outside the model-only results in Section 5.4.3.

In verificationService.js, SVM_TIMEOUT_MS defaults to 5000 milliseconds and can be overridden by the environment. A separate AbortSignal timeout applies to the status request and then to the prediction request. This is not a five-second deadline for the complete verification workflow. The deployed timeout value, an overall verification deadline and a uniform bounded retry policy were not verified. No longer timeout, warm-up schedule or minimum-replica arrangement is claimed as configured.

The source distinguishes a status-request transport failure, a reported unavailable model, a prediction transport failure, a prediction HTTP error and an invalid prediction. A non-successful status response can be reduced to modelLoaded: false, so the resulting model-unavailable reason does not by itself distinguish every upstream status error. Diagnosis requires the status/prediction response details and service logs, with cold and warm measurements recorded separately.

accessControlService.js attempts to append KYC_DECISION_MADE with details.svmFallback = true, details.reason, the request and agent context and a system actor. auditLogger.js may return null if insertion fails. A logging attempt therefore does not prove that the reason persisted. The four historical placeholder decisions require matching audit rows and backend/AI logs joined by request identifier and time. Those matching records were not available; their failure causes and hosting environments remain unknown. I do not attribute them to Azure cold starts.

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

Hosted availability was checked on 27 October 2026: the Vercel frontend returned HTTP 200, and both backend and AI /health endpoints returned HTTP 200 with status: ok. The AI /api/svm/status endpoint returned HTTP 401 to an unauthenticated request, so the deployed model version was not independently established. I separately confirmed that the hosted workflow worked. These checks demonstrate reachability and service health; they are not a rerun of the 46 local automated tests or a measured hosted accuracy study.

Frontend startup failed initially because of an invocation-path error and then a filesystem restriction. After correcting the execution setup without changing application code, all 16 tests passed. Initial outputs and the successful rerun were retained.

The supplied files were Supabase Snippet Untitled query.csv (decisions), query (1).csv (requests) and query (2).csv (scores). Their timestamps covered 21 September to 3 October 2026 in Africa/Nairobi. Nine decision probability triples summed to one, and every exported decision linked to a request with matching status. These records show stored outputs, not classification accuracy: they contain no independently adjudicated ground truth, no model-version field and no access-control or audit-log export. Historical threshold outputs must not be assumed to replay under the current rule revision.

Amended Chapter 4 verification scenarios. I reviewed the relevant source and existing evidence on 29 October 2026. This was a documentation and source review, not execution of the new scenarios. The 46 passing tests retain their actual date of 23 October 2026 and local environment. The additional and extended checks below are not included in that total. For each unexecuted check, there is no execution date, measured actual outcome or pass verdict.

C4-T18 — failure and readiness. Existing local classifier and decision tests on 23 October 2026 passed their assertions for unavailable models and invalid/incomplete evidence, as recorded in Table 5.8 and the retained test logs. The extended test must separately inject status-call delay/failure, prediction-call delay/failure, model absence and invalid responses; record the effective timeout and total deadline; and compare cold and warm hosted runs. Expected: bounded failure handling, no decision from incomplete scores, and a persisted fallback cause linked to the request when valid-score fallback is used. Actual for this extension: untested. Required evidence: dated settings, timings, responses and matching audit/service logs from an isolated test environment and identified hosted revision.

C4-T22 — retention. Five local Node.js retention tests passed on 23 October 2026 using mocked database/storage access. They checked Nairobi business-day expiry, the exact verified-window boundary, removal of eligible and superseded images, exclusion of non-verified cases and preservation of references after failed removal. Expected and actual results agreed for that existing scope. Exclusion of pending/review/rejected images is not a pass against amended DR-08. The extended check must cover 30-day image and 180-day metadata boundaries, abandoned/replacement uploads, repeated approvals, access denial after expiry, retries and preservation exceptions. Actual for the extension: untested; source review shows missing non-verified and metadata expiry. Required evidence: controlled timestamps, access responses, before/after object and record inventories and cleanup logs in an isolated environment.

C4-T24 — recovery. Proposed test environment: an isolated restoration target with restricted credentials and test data. Expected: encrypted daily database exports, restricted access, seven-day expiry, separate recoverable model/configuration copies, exclusion of raw identity images, intact record relationships and access policies, and reapplication of expired-data deletion before access resumes. Current practice: I confirmed on 30 October 2026 that code runs daily to back up the Supabase database to Google Drive. Actual test outcome: no restoration has been performed, and the complete recovery scenario remains untested. Required evidence includes the backup script and execution logs, protected backup inventory, retention and encryption settings, confirmation of backup contents, and a dated isolated-restoration result with integrity, access-policy and retention checks.

C4-T25 — human-check interface. Proposed environment: isolated backend and browser, controlled clock and one/multiple backend processes. Expected: correct response permits password authentication; incorrect, missing, expired or reused challenges are rejected; refresh and challenge-service failure provide usable feedback; and an accessible alternative supports the essential task. Restart and cross-instance checks must establish the deployed handling of in-memory challenges. Actual: untested; the five-character, five-minute and first-attempt rules were inspected in source on 29 October 2026, not executed as this scenario. Required evidence: assertions for each case, request/response records and keyboard/screen-reader task observations.

C4-T26 — origins and CORS. Proposed environment: isolated production/development configurations, followed by controlled browser checks of the identified deployment. Expected: only listed frontend origins can read cross-origin responses; production HTTPS origins exclude development defaults; preflights and real-time connections follow the configured policy; protected routes reject unauthenticated calls independently of Origin. Actual: untested; source inspection found mixed localhost/configured origins and unrestricted Flask CORS. Required evidence: sanitized effective settings, allowed/unlisted/no-Origin responses, preflight headers, browser observations and real-time transport results. Source inspection does not establish the deployed verdict.

C4-T27 — disclosure and consent. Proposed environment: isolated frontend, backend and database using test accounts. Expected: the notice appears before evidence collection, consent is initially unchecked where applicable, direct API submissions without valid consent fail, and accepted records contain account, purpose, notice version and a server-generated timestamp. Withdrawal must trigger the approved processing/retention response. Actual: untested; the corresponding controls and record were not found in source. Required evidence: notice/UI records, rejected and accepted API results, stored consent rows and withdrawal records. Implementation and approval of the processing basis are prerequisites to a compliance verdict.

Table 5.10: Live test observations and system-level coverage

Area | Evidence | Observed result | Interpretation | Status

Request and score storage | Request and score CSV exports | 12 requests across 8 agent identifiers; all 12 linked to six-score records | Supports persistence of verification evidence | Observed

Decision output | Decision CSV joined by request_id | 9 linked decisions: 7 Verified, 2 Rejected; all matched request status | Supports recorded outcome generation; no Manual Review example | Observed

Decision provenance | decision_basis values | 5 svm_model and 4 placeholder_threshold decisions | Both paths occurred; model version and fallback cause were not recorded | Observed

Incomplete attempts | Request-to-decision join | 3 pending requests had no decision in the supplied exports | Completion was not demonstrated for every recorded attempt | Open

Passkeys and retention | Isolated automated test logs | Passkey service, route and migration checks and 5 retention tests passed | Does not certify physical authenticators or live storage cleanup | Locally tested

Other system requirements | No corresponding records supplied | Access grants, administrator actions, negative security cases, latency and participant usability not established | Requires separate records; no pass/fail result assigned | Not verified

Hosted application | Public endpoint checks and my confirmation, 27 October 2026 | Frontend and both health endpoints returned HTTP 200; I reported successful workflow | Unauthenticated model-status request returned 401; no hosted accuracy or load benchmark | Available; workflow confirmed by me



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

I used Claude (Anthropic) for documentation and implementation prompts and OpenAI Codex to help inspect the source and saved reports, prepare this chapter, run the recorded isolated tests and offline threshold comparison, and check the Word layout. I remain responsible for reviewing the final chapter, checking its alignment with the project objectives and references, and approving its submission. The 29 October amendment revised the documentation and verification plan; it did not implement the proposed application controls or rerun the 46 tests.

5.7 Evaluation Results, Discussion and Limitations

5.7.1 Assessment Against the Objectives

Table 5.15 relates the evidence in this chapter to the five project objectives.

Table 5.15: Objectives, evidence and results

Objective | Output and evidence | Result

1. Investigate current registration and verification practice | Literature review, Chapter 2 | Addressed in Chapter 2 and used to derive the Chapter 4 requirements

2. Identify challenges and fraud risks | Chapter 2; countermeasures implemented as quality gates, liveness scoring and guardrails | Addressed; countermeasures implemented

3. Examine existing KYC platforms | Related-works comparison and research gap, Chapter 2 | Addressed in Chapter 2

4. Develop the system | Modules in Section 5.3; version 3.0.0 classifier | Implemented and hosted on Vercel, Render and Azure. Recorded synthetic classifier accuracy: 75.800%; macro F1: 0.654082.

5. Test and validate effectiveness | Tables 5.8 and 5.9: automated test evidence; Table 5.10: live evaluation coverage; Tables 5.11–5.14: classifier and baseline results | Partly met: 46 local automated tests passed; live exports contained 12 score-linked requests and 9 decisions. Hosted endpoints were available and I confirmed operation; real-world accuracy and comprehensive security/usability remain unestablished.



5.7.2 Discussion

The implementation combined evidence capture, numerical scoring and persistent verification decisions. The live exports supported this path through 12 request/score pairs and nine matching decisions. The automated tests added evidence for selected interfaces, input handling, passkeys and retention. However, three attempts remained pending, and access enforcement, administrator intervention and user acceptance were not established by the supplied exports. Deployment was subsequently completed across Vercel, Render and Azure, with public availability checks and my confirmation of successful operation recorded on 27 October 2026.

For classification, version 3 achieved 75.800% accuracy and 0.654082 macro F1 on the fresh synthetic sample and passed its comparative release gate. The improvement over version 2 was inconclusive. Liveness and face matching carried most of the measured importance, which is consistent with the emphasis in the literature on liveness detection (Tan et al., 2014) and discriminative face embeddings (Deng et al., 2019) and supports the pipeline design in Chapter 3. The low Manual Review recall of 27.33% and the 227 false verifications show that the model should not approve agents autonomously. The Manual Review route and the administrator override exist to catch uncertain cases, but the experiment did not measure how often administrators would correct these errors.

Decision provenance distinguished SVM outputs from threshold-rule outputs in the live records. Token validation, role checks, guardrails and image retention were implemented, but the exports did not include access-control or audit records that would prove their live enforcement. The successful isolated passkey and retention tests supplied narrower evidence for those modules; no general security or privacy-compliance conclusion was drawn.

5.7.3 Limitations

Data validity was the main limitation. The labels were synthetic, the class quotas were fixed and the score relationships were assumed. The fresh evaluation sample came from the same simulator and not from independent real applicants, and the benchmark measurements were reused from earlier runs, so later changes to the image pipeline could cause a mismatch between the source distributions and deployed scores.

Evaluation coverage remained limited. The live evidence comprised 12 requests from eight agent identifiers, with no independent identity labels or recorded model versions; it could not establish real-world accuracy. No demographic fairness study, presentation-attack campaign, camera comparison, participant usability study or timed ten-run pipeline benchmark was documented. Small calibration and selection partitions also left a risk of policy overfitting. Model metrics excluded the full effects of capture quality gates, fallback and administrator intervention. Completed hosting resolved the earlier deployment limitation, but did not provide measured cloud latency, concurrency or long-duration availability.

Retention and informed collection remain incomplete against the amended design. The verified-only cleanup and its passing local tests do not demonstrate the 30-day non-verified image policy, 180-day metadata expiry, abandoned-upload handling or preservation exceptions. The required consent control, backend record/enforcement and withdrawal route were not found. DR-08 and DR-09 therefore remain unresolved. Unpinned image-processing dependencies and the absence of a historical environment snapshot also limit exact reproduction of the complete pipeline.

Recovery and integration verification remain incomplete. I use Supabase Free in Ireland and maintain daily scripted database backups on Google Drive, but I have not tested restoration. Backup encryption, access restrictions, seven-day expiry, image exclusions and model/configuration coverage remain unverified. The SVM five-second value is a per-call source default, not a confirmed deployed setting or overall deadline. Matching reasons for the four historical fallback decisions, cold/warm timings and effective cloud settings remain unavailable. The extended C4-T18 and C4-T24 scenarios are untested.

IR-11 and IR-12 are not fully demonstrated. The internal CAPTCHA lacks an established accessible alternative and verified restart/multiple-instance behaviour. The source combines development and configured frontend origins and enables unrestricted AI CORS; actual production HTTP and real-time settings remain unverified. C4-T25, C4-T26 and C4-T27 are untested, and no full accessibility-conformance claim is made.

Data protection review. I use Kenya’s Data Protection Act, 2019 as the reference for notice, lawful processing, consent, retention and security, including sections 25 and 29–32, 39–41, sensitive-data processing under sections 44–45 and overseas transfers under sections 48–49 (Republic of Kenya, 2019). No supervisor or institutional decision confirming the processing basis, biometric-processing safeguards, impact-assessment outcome or overseas-hosting safeguards is recorded. These review outcomes remain unverified; neither hosting nor a proposed consent notice establishes legal compliance.

Outstanding application work is separate from this document amendment: implement the non-verified-image and metadata lifecycles, applicable consent/withdrawal controls, an accessible human-check alternative, production origin separation and the recovery procedure. Select any SVM timeout or replica/warm-up changes only after measurement. Outstanding evidence includes the remaining deployed service settings, the Google Drive backup script and execution records, verification of backup protections and retention, an isolated-restoration result, matching historical fallback audit/log records, execution results for the extended scenarios and the institutional review outcome. None is treated as completed by editing this chapter.

The evidence supports a functioning implementation and a reproducible synthetic classifier experiment. The real-world effectiveness of the classifier remains unestablished. Conclusions, recommendations and future work, including periodic retraining on administrator-confirmed decisions, are presented in Chapter 6.

References for the amended controls

Express. (n.d.). CORS middleware. Retrieved October 29, 2026, from https://expressjs.com/en/resources/middleware/cors/

Republic of Kenya. (2019). Data Protection Act, 2019 (No. 24 of 2019). https://kentrade.go.ke/wp-content/uploads/2022/09/Data-Protection-Act-1.pdf

Supabase. (n.d.-a). Database backups. Retrieved October 29, 2026, from https://supabase.com/docs/guides/platform/backups

Supabase. (n.d.-b). Pricing & fees. Retrieved October 29, 2026, from https://supabase.com/pricing

World Wide Web Consortium. (2021). Web authentication: An API for accessing public key credentials, level 2. https://www.w3.org/TR/webauthn-2/


---

## Chapter_6_Conclusions_Recommendations_and_Future_Work.docx

Chapter 6 Conclusions Recommendations and Future Work

Intelligent Agent Identity Verification System

6.1 Introduction

This project addressed the need to assess an agent's identity during registration and connect the verification outcome to controlled access. Its purpose was to combine document evidence, facial comparison and liveness assessment in an accountable verification workflow. I developed and hosted a system that captures identity evidence, produces six verification scores, classifies cases and provides an administrator review route. The findings establish a functioning implementation and a reproducible synthetic classifier experiment. They do not establish that the system can reliably approve real applicants without human oversight. This chapter draws conclusions against the five project objectives, recommends actions arising from the reported limitations and identifies priorities for further investigation.

6.2 Conclusions

6.2.1 Investigation of Current Registration and Verification Practice

The investigation of registration and verification practice provided the basis for the system requirements. As recorded in the objective assessment in Section 5.7.1, this objective was addressed through the Chapter 2 literature review and carried into Chapter 4. Its contribution was to define a workflow extending from account registration and evidence collection to a verification decision and administrative handling. The completed implementation demonstrates how those activities can be connected. The evidence does not establish a measured reduction in processing time or staff workload compared with an existing registration process.

6.2.2 Identification of Challenges and Fraud Risks

The identified verification challenges informed the image-quality gate, document-text comparison, facial matching, liveness scoring and registration guardrails. These countermeasures were implemented, but their presence does not establish their effectiveness against real fraud. In the fresh synthetic evaluation, the selected classifier verified 43 of 300 Rejected cases and 184 of 300 Manual Review cases. These results show that combining the available scores leaves consequential errors unresolved. The objective therefore informed the system's controls, while the evidence supports continued human oversight and does not establish a real-world fraud-prevention rate.

6.2.3 Examination of Existing KYC Platforms

The examination of existing know-your-customer platforms supplied the related-work comparison and research gap recorded in Chapter 2, as summarised in Table 5.15. This objective provided context for the project's development rather than a comparative product trial. Chapter 5 contains no matched operational evaluation against those platforms. The implemented workflow can therefore be presented as the project's response to the identified requirements, without claiming that it is more accurate, faster or more secure than existing KYC products.

6.2.4 Development of the Identity Verification System

I implemented the frontend, application backend, AI service and persistent records, and hosted the application across Vercel, Render and Azure with Supabase providing authentication, database and storage services. The recorded live exports contained 12 verification requests linked to complete six-score records and nine decisions whose outcomes matched the associated request status. This supports the implemented path from evidence scoring to stored decisions. Source inspection also established administrator review, access-control and audit mechanisms, although the exports did not independently demonstrate their live enforcement.

The selected decision approach was version 3.0.0 of a sigmoid-calibrated radial-basis-function support vector machine. It achieved 75.800% accuracy and a macro F1 score of 0.654082 on 1,500 fresh synthetic cases. On the same cases, the saved version 2 model achieved 75.733% accuracy and the Decision Tree achieved 75.667%. The version 3 improvement over version 2 was inconclusive because the reported confidence intervals for the accuracy and macro F1 differences included zero. The threshold baseline had much lower accuracy but fewer false verifications, illustrating the trade-off between accepting genuine cases and limiting incorrect approvals. These comparisons support the recorded model selection within the experiment; they do not establish general superiority.

The development objective was achieved for the core implemented and hosted workflow. Full coverage of the amended requirements remains incomplete, particularly for informed collection, non-verified image retention, metadata expiry, recovery and integration controls. Those omissions limit any claim of operational readiness.

6.2.5 Testing and Validation of Effectiveness

The testing objective was partly met. The recorded local evaluation passed 46 automated tests, providing evidence for selected classifier contracts, decision handling, passkeys, retention and frontend behaviour. Public endpoint checks established hosted availability, and I confirmed operation of the hosted workflow. However, three exported requests remained pending, no Manual Review decision appeared in the live sample, and the records lacked independent identity labels. These observations cannot establish real-world accuracy or complete workflow reliability.

Manual Review was the weakest classifier outcome, with recall of 27.33%. Across the two non-Verified classes, 227 of 600 synthetic cases were incorrectly verified. The evaluation therefore does not support autonomous approval, and the effectiveness of administrator intervention remains unmeasured. No representative participant usability study, demographic analysis, comprehensive security assessment or timed hosted pipeline benchmark was reported. Passing selected local tests does not resolve those gaps.

6.2.6 Project Contribution and Boundaries

The project contributes an integrated identity-verification implementation and a reproducible method for assessing a classifier that combines document and biometric scores. It preserves a distinction between model and threshold decisions and reports consequential classification errors alongside aggregate accuracy. Its strongest evidence concerns selected local software behaviours, stored request-to-decision relationships and model performance under the specified simulator assumptions. The findings remain bounded by synthetic labels, a fixed class mixture, a small live sample and incomplete operational verification. Hosting establishes availability; it does not establish safety, legal compliance, scalability or effectiveness across real applicant populations.

6.3 Recommendations

The following actions are prioritised by their importance to responsible use. They address findings and unfinished requirements reported in Chapter 5; they are not claims that the outstanding controls have already been completed.

6.3.1 Retain Human Oversight and Restrict Operational Use

The adopting organisation and system administrators should restrict current use to controlled evaluation and demonstration. Before any trial affects real access rights, they should establish authorised human review of proposed outcomes and verify that decisions, access records and audit events agree. Review must cover proposed Verified outcomes as well as cases placed in the Manual Review queue, because the experiment showed that many cases requiring review were classified as Verified. Human intervention is an essential safeguard, but its ability to correct errors must itself be evaluated before wider adoption.

6.3.2 Complete Informed Collection and Retention Controls

Before further operational collection of identity evidence, developers and the adopting institution should resolve the notice, applicable consent, withdrawal and processing-basis gaps identified in Section 5.7.3. Developers should complete and test the amended retention requirements for non-verified images, abandoned uploads, metadata and preservation exceptions, including access expiry and deletion retries. The verified-only cleanup tests do not establish these behaviours. The proposed 30-day image and 180-day metadata periods should remain subject to institutional approval, together with biometric-processing and overseas-hosting safeguards; they should not be presented as statutory periods or evidence of compliance.

6.3.3 Verify Recovery and Production Controls

System maintainers should inspect the daily Google Drive backup process and demonstrate an isolated restoration before relying on it for recovery. The checks should cover encryption, restricted access, the proposed seven-day expiry, backup contents, model and configuration recovery, record integrity and reapplication of expired-data deletion. This is essential because backup creation was reported but restoration was not tested. Developers should also complete production-origin separation and an accessible human-check alternative, then execute the outstanding failure, origin, consent and human-check scenarios. Source inspection and health responses are insufficient evidence of their deployed behaviour.

6.3.4 Establish Operational Evidence Before Optimisation

Developers and maintainers should record the deployed revision, model version, effective configuration and persisted decision provenance for each evaluated run. They should investigate incomplete requests and link fallback decisions to their actual failure causes. Chapter 5 could not determine why four historical decisions used threshold fallback, so infrastructure changes should not be justified by an assumed cold-start problem. Complete the planned cold and warm timing measurements, access-control checks and administrator walkthroughs first. Changes to timeouts, replicas or service tiers should depend on measured bottlenecks and agreed acceptance criteria. Optional performance tuning should follow the essential safeguards above.

6.4 Future Work

The following research directions are presented in priority order. They extend the evaluation beyond the completed study. Implementing and testing the outstanding Chapter 4 requirements remains current completion work under Section 6.3. The scope, resources and feasibility of each extension should be agreed with the supervisor before it begins.

6.4.1 External Validation of the Complete Verification Pipeline

The highest priority is to evaluate whether the synthetic findings transfer to real applicants. Researchers would require appropriately authorised identity samples, independently adjudicated outcomes and representative coverage of document types, cameras, capture conditions and relevant applicant groups. The principal change would be evaluation of the full capture-to-decision workflow against real ground truth, rather than generated score vectors. A held-out external set should measure per-class performance, both false-verification categories, calibration and subgroup uncertainty. Authorised presentation-attack testing should assess the liveness component separately. Success would depend on predefined error tolerances and consistent performance across the evaluated conditions, rather than aggregate accuracy alone.

6.4.2 Evaluation of Review Policies and Periodic Retraining

The low review recall and uncertain improvement over version 2 justify a controlled investigation of decision policies and model updating. Researchers should compare the existing model with recalibrated or more conservative review policies using the same development data and an untouched evaluation set. Required resources include sufficient adjudicated cases, documented error costs and a manageable administrator review capacity. Administrator-confirmed decisions could support periodic retraining after independent label checks; they should not be assumed correct merely because an administrator approved them. Evaluation should report false verifications, genuine-case rejection, review workload and calibration, with uncertainty estimates. Promotion should require a justified improvement at an acceptable review burden, and retain a versioned rollback path.

6.4.3 Longer Studies of Usability and Operational Reliability

After the essential controls and baseline checks are completed, a longer supervised study should examine how applicants and administrators use the system over time. This would require representative participants, an isolated or appropriately approved deployment, accessible task scenarios and monitoring across realistic workloads. The extension would assess sustained use and human decision-making, which were not measured in the present study. Outcomes should include task completion, assistance and recapture needs, accessibility barriers, administrator correction of errors, and cold and warm response times. Longer observation should also measure failures, recovery and changes in score or decision distributions. These results would determine whether the workflow remains usable and dependable beyond a short demonstration and whether broader deployment is justified.
