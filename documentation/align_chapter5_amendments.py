from pathlib import Path
from copy import deepcopy
import re
from docx import Document
from docx.text.paragraph import Paragraph
from docx.oxml import OxmlElement
from docx.shared import Pt, Inches

root = Path(__file__).resolve().parent
doc = Document(root / 'Chapter_5_Hosted_Deployment.docx')
p = list(doc.paragraphs)

def replace(i, text):
    p[i].text = text

def after(i, paragraphs):
    anchor = p[i]
    for text in paragraphs:
        el = OxmlElement('w:p')
        anchor._p.addnext(el)
        q = Paragraph(el, anchor._parent)
        q.style = doc.styles['Normal']
        q.add_run(text)
        anchor = q

replace(0, 'Chapter 5 System Implementation Testing and Evaluation')
replace(3, 'In this chapter, I explain how I implemented the system design, the environment in which it ran, and the testing and evaluation completed. The system registers agents, collects identity evidence, combines document and biometric scores, and supports verification decisions and controlled access. I distinguish the amended Chapter 4 requirements from inspected source code, confirmed deployment information and executed tests. Proposed controls remain outstanding where implementation or test evidence is absent.')
replace(7, 'I developed the system locally and deployed the Vue frontend on Vercel, the Express backend on Render and the Flask AI service on Microsoft Azure Container Apps. I previously reported using Supabase Free for authentication, PostgreSQL and storage; the current subscription and account-specific backup facilities have not been independently verified. I confirmed successful operation of the hosted workflow on 27 October 2026. Local development used ports 5173, 3000 and 5000, while the public services used HTTPS. Table 5.1 separates the development equipment from hosting information; these are not measured minimum requirements.')
after(12, [
    'Origin configuration. In backend/server.js, the HTTP CORS check combines http://localhost:5173 and http://127.0.0.1:5173 with comma-separated FRONTEND_URL values. It accepts requests without an Origin header and rejects origins outside that list. Socket.IO uses the same allowedOrigins list with GET and POST. The local source therefore retains development origins alongside configured frontend origins. ai-service/app.py uses unrestricted CORS(app). The deployed FRONTEND_URL values and effective HTTP and real-time origin behaviour have not been verified.',
    'The amended IR-12 requires explicit production HTTPS origins, separate development settings and coverage of HTTP and real-time connections. The source configuration does not establish those conditions. CORS controls whether browser scripts can read cross-origin responses; it does not authenticate an API caller (Express, n.d.). Bearer-token and role checks, backend-to-AI credentials and WebAuthn origin validation are separate controls. The backend AI client sends X-API-Key when configured and requires a sufficiently long key for a non-local AI host; this source inspection does not establish the deployed secret or its enforcement.'
])
after(25, [
    'Recovery design and current evidence. Supabase lists automatic backups and point-in-time recovery as excluded from Free. Its database backups contain Storage metadata, not the image objects themselves (Supabase, n.d.-a, n.d.-b; checked 29 October 2026). These published facilities do not confirm the current project subscription or prove that a recoverable copy exists.',
    'Under the amended DR-12, I propose encrypted daily exports of necessary database records, restricted access and seven-day backup retention, with controlled copies of model artifacts and deployment configuration maintained separately. Raw identity images are excluded from the proposed off-site backup set. Restoration must use an isolated environment and verify record relationships, model hashes, access policies and retention deadlines before access resumes. Expired-data deletions and documented preservation decisions must be reapplied; restored metadata must not make deleted image evidence appear available. Lost images would require lawful recollection where necessary.',
    'No scheduled export configuration, encrypted backup inventory, seven-day deletion record or completed isolated-restoration result was available for this review. Saved model artifacts and database migrations support reproduction but do not demonstrate recovery. C4-T24 therefore remains untested; no backup, restore or production-setting change was performed for this document revision.'
])
replace(28, '5.3.1 Design Changes and Implementation Gaps')
replace(29, 'Table 5.3 preserves the recorded design changes from the earlier draft. The amended Chapter 4 additionally specifies retention, consent, recovery, human-check and origin controls. I compare these requirements with the source inspected on 29 October 2026 in the following subsections. A requirement or proposed policy is not treated as an implemented control or a passing test.')
replace(35, 'The inspected documentRetentionService.js considers the latest request for each agent and skips it unless its status is verified. For eligible verified cases, the audit window expires three business days after the successful decision; business days are Monday to Friday in Africa/Nairobi, without public-holiday exclusions. The job runs at startup and every fifteen minutes while the backend is running. It removes eligible image objects and clears file references while retaining document rows, scores, decisions and audit history. Failed removals leave references available for a later cleanup attempt. This describes the source; live deletion scheduling and object removal have not been demonstrated.')
after(35, [
    'The amended DR-08 instead requires each pending, review or rejected image to expire 30 calendar days after upload, including abandoned uploads. Viewing or a status change must not restart this deadline. Verification metadata, scores, decisions, consent records and related audit history are to expire 180 calendar days after attempt closure, unless a documented lawful preservation obligation applies. Closure is a final verified or rejected decision, or expiry of an incomplete attempt. These are proposed project periods, not statutory retention periods.',
    'The current verified-only purge does not implement the 30-day policy, an abandoned-upload expiry path, the 180-day metadata lifecycle or the preservation-exception record. The amended DR-07 limits metadata preservation to its defined period, and NFR-06 requires signed URLs not to outlive the applicable image deadline. The existing verified-case window supplies only part of this behaviour. Expiry enforcement for non-verified evidence and safe reapplication after restoration remain implementation and testing gaps.'
])
replace(37, p[37].text + ' WebAuthn relying-party, origin and fresh-challenge validation are distinct from the HTTP CORS policy (World Wide Web Consortium, 2021).')
after(37, [
    'Human check. The internal captcha.js utility generates a five-character image challenge, stores its answer in process memory and sets a five-minute lifetime. The first validation attempt consumes the challenge, whether the answer is correct or incorrect. authController.js checks the CAPTCHA before calling password authentication and returns missing/invalid-challenge feedback. LoginPage.vue provides a refresh button and a labelled input. No external CAPTCHA provider is integrated.',
    'A process restart loses outstanding challenges, and separate backend processes do not share the in-memory challenge map. A challenge generated on one instance may therefore fail on another unless deployment routing or a shared store addresses this. Neither arrangement was verified. The image description and refresh control do not provide a non-visual solution. Google sign-in and optional registered passkeys are other account-access paths, but their availability and accessibility do not establish an equivalent alternative for every password user. The accessible-alternative part of IR-11 and restart/multiple-instance behaviour remain untested.',
    'Browser integration. The HTTP, Socket.IO and AI CORS settings described in Section 5.2.2 are source findings. An allowed origin does not bypass authentication, and absence of an Origin header is not proof of a trusted caller. Production origin separation, permitted/unlisted-origin preflights and real-time behaviour require C4-T26 execution against the actual deployed configuration.'
])
after(38, [
    'Disclosure and consent. The inspected frontend, backend and database files did not contain the proposed pre-collection consent control, a corresponding account/purpose/notice-version/server-timestamp record, backend enforcement of that record, or withdrawal handling. Under amended DR-09, these controls are required where consent is the approved processing basis. Account registration and submission of images do not demonstrate that this requirement has been met. Both the collection controls and the applicable processing basis remain unresolved; the proposed notice alone does not close DR-09.'
])
replace(45, 'Audit logging. The central utility attempts to insert standardised action and outcome records for significant operations, with contextual identifiers and a server timestamp. Its error handling logs failures and returns null rather than guaranteeing persistence. I therefore distinguish an inspected logging call from a successfully stored audit event.')
replace(50, p[50].text + ' The inspected flow did not enforce the amended pre-upload consent requirement; C4-T27 addresses this gap.')
replace(55, 'Defined significant steps call the audit utility. Reconstruction of an individual request requires the corresponding persisted audit rows; the request, score and decision exports alone do not establish a complete audit sequence.')
replace(58, 'At the AI endpoint, an unavailable or inconsistent model bundle produces an unavailable-service response. At application level, complete valid scores may enter threshold fallback when SVM inference is unavailable or unusable. The decision basis is placeholder_threshold, and the rule outputs are not calibrated probabilities. These application paths are outside the model-only results in Section 5.4.3.')
after(58, [
    'In verificationService.js, SVM_TIMEOUT_MS defaults to 5000 milliseconds and can be overridden by the environment. A separate AbortSignal timeout applies to the status request and then to the prediction request. This is not a five-second deadline for the complete verification workflow. The deployed timeout value, an overall verification deadline and a uniform bounded retry policy were not verified. No longer timeout, warm-up schedule or minimum-replica arrangement is claimed as configured.',
    'The source distinguishes a status-request transport failure, a reported unavailable model, a prediction transport failure, a prediction HTTP error and an invalid prediction. A non-successful status response can be reduced to modelLoaded: false, so the resulting model-unavailable reason does not by itself distinguish every upstream status error. Diagnosis requires the status/prediction response details and service logs, with cold and warm measurements recorded separately.',
    'accessControlService.js attempts to append KYC_DECISION_MADE with details.svmFallback = true, details.reason, the request and agent context and a system actor. auditLogger.js may return null if insertion fails. A logging attempt therefore does not prove that the reason persisted. The four historical placeholder decisions require matching audit rows and backend/AI logs joined by request identifier and time. Those matching records were not available; their failure causes and hosting environments remain unknown. I do not attribute them to Azure cold starts.'
])
replace(84, p[84].text.replace('The author separately confirmed that the hosted workflow worked.', 'I separately confirmed that the hosted workflow worked.'))
after(86, [
    'Amended Chapter 4 verification scenarios. I reviewed the relevant source and existing evidence on 29 October 2026. This was a documentation and source review, not execution of the new scenarios. The 46 passing tests retain their actual date of 23 October 2026 and local environment. The additional and extended checks below are not included in that total. For each unexecuted check, there is no execution date, measured actual outcome or pass verdict.',
    'C4-T18 — failure and readiness. Existing local classifier and decision tests on 23 October 2026 passed their assertions for unavailable models and invalid/incomplete evidence, as recorded in Table 5.8 and the retained test logs. The extended test must separately inject status-call delay/failure, prediction-call delay/failure, model absence and invalid responses; record the effective timeout and total deadline; and compare cold and warm hosted runs. Expected: bounded failure handling, no decision from incomplete scores, and a persisted fallback cause linked to the request when valid-score fallback is used. Actual for this extension: untested. Required evidence: dated settings, timings, responses and matching audit/service logs from an isolated test environment and identified hosted revision.',
    'C4-T22 — retention. Five local Node.js retention tests passed on 23 October 2026 using mocked database/storage access. They checked Nairobi business-day expiry, the exact verified-window boundary, removal of eligible and superseded images, exclusion of non-verified cases and preservation of references after failed removal. Expected and actual results agreed for that existing scope. Exclusion of pending/review/rejected images is not a pass against amended DR-08. The extended check must cover 30-day image and 180-day metadata boundaries, abandoned/replacement uploads, repeated approvals, access denial after expiry, retries and preservation exceptions. Actual for the extension: untested; source review shows missing non-verified and metadata expiry. Required evidence: controlled timestamps, access responses, before/after object and record inventories and cleanup logs in an isolated environment.',
    'C4-T24 — recovery. Proposed environment: an isolated restoration target with restricted credentials and test data. Expected: encrypted daily database exports, restricted access, seven-day expiry, separate recoverable model/configuration copies, no raw-image backup, intact record relationships and access policies, and reapplication of expired-data deletion before access resumes. Actual: untested; no backup or restoration execution date is recorded. Required evidence: export schedule, protected inventory and hashes, expiry log, restore log and post-restore integrity/access/retention checks. The subscription and available account-specific backup facilities also require verification.',
    'C4-T25 — human-check interface. Proposed environment: isolated backend and browser, controlled clock and one/multiple backend processes. Expected: correct response permits password authentication; incorrect, missing, expired or reused challenges are rejected; refresh and challenge-service failure provide usable feedback; and an accessible alternative supports the essential task. Restart and cross-instance checks must establish the deployed handling of in-memory challenges. Actual: untested; the five-character, five-minute and first-attempt rules were inspected in source on 29 October 2026, not executed as this scenario. Required evidence: assertions for each case, request/response records and keyboard/screen-reader task observations.',
    'C4-T26 — origins and CORS. Proposed environment: isolated production/development configurations, followed by controlled browser checks of the identified deployment. Expected: only listed frontend origins can read cross-origin responses; production HTTPS origins exclude development defaults; preflights and real-time connections follow the configured policy; protected routes reject unauthenticated calls independently of Origin. Actual: untested; source inspection found mixed localhost/configured origins and unrestricted Flask CORS. Required evidence: sanitized effective settings, allowed/unlisted/no-Origin responses, preflight headers, browser observations and real-time transport results. Source inspection does not establish the deployed verdict.',
    'C4-T27 — disclosure and consent. Proposed environment: isolated frontend, backend and database using test accounts. Expected: the notice appears before evidence collection, consent is initially unchecked where applicable, direct API submissions without valid consent fail, and accepted records contain account, purpose, notice version and a server-generated timestamp. Withdrawal must trigger the approved processing/retention response. Actual: untested; the corresponding controls and record were not found in source. Required evidence: notice/UI records, rejected and accepted API results, stored consent rows and withdrawal records. Implementation and approval of the processing basis are prerequisites to a compliance verdict.'
])
replace(111, 'I used Claude (Anthropic) for documentation and implementation prompts and OpenAI Codex to help inspect the source and saved reports, prepare this chapter, run the recorded isolated tests and offline threshold comparison, and check the Word layout. I remain responsible for reviewing the final chapter, checking its alignment with the project objectives and references, and approving its submission. The 29 October amendment revised the documentation and verification plan; it did not implement the proposed application controls or rerun the 46 tests.')
replace(117, p[117].text.replace('author-confirmed successful operation', 'my confirmation of successful operation'))
replace(123, 'Retention and informed collection remain incomplete against the amended design. The verified-only cleanup and its passing local tests do not demonstrate the 30-day non-verified image policy, 180-day metadata expiry, abandoned-upload handling or preservation exceptions. The required consent control, backend record/enforcement and withdrawal route were not found. DR-08 and DR-09 therefore remain unresolved. Unpinned image-processing dependencies and the absence of a historical environment snapshot also limit exact reproduction of the complete pipeline.')
replace(124, 'Recovery and integration verification remain incomplete. The reported Supabase Free subscription requires a live account check; encrypted daily exports, seven-day backup expiry and isolated restoration have not been demonstrated. The SVM five-second value is a per-call source default, not a confirmed deployed setting or overall deadline. Matching reasons for the four historical fallback decisions, cold/warm timings and effective cloud settings remain unavailable. The extended C4-T18 and C4-T24 scenarios are untested.')
replace(125, 'IR-11 and IR-12 are not fully demonstrated. The internal CAPTCHA lacks an established accessible alternative and verified restart/multiple-instance behaviour. The source combines development and configured frontend origins and enables unrestricted AI CORS; actual production HTTP and real-time settings remain unverified. C4-T25, C4-T26 and C4-T27 are untested, and no full accessibility-conformance claim is made.')
after(125, [
    'Data protection review. I use Kenya’s Data Protection Act, 2019 as the reference for notice, lawful processing, consent, retention and security, including sections 25 and 29–32, 39–41, sensitive-data processing under sections 44–45 and overseas transfers under sections 48–49 (Republic of Kenya, 2019). No supervisor or institutional decision confirming the processing basis, biometric-processing safeguards, impact-assessment outcome or overseas-hosting safeguards is recorded. These review outcomes remain unverified; neither hosting nor a proposed consent notice establishes legal compliance.',
    'Outstanding application work is separate from this document amendment: implement the non-verified-image and metadata lifecycles, applicable consent/withdrawal controls, an accessible human-check alternative, production origin separation and the recovery procedure. Select any SVM timeout or replica/warm-up changes only after measurement. Outstanding evidence includes current account and deployment settings, backup/restore records, matching historical fallback audit/log records, execution results for the extended scenarios and the institutional review outcome. None is treated as completed by editing this chapter.'
])

# Keep table results, numbering and figures; amend status wording without changing metrics.
doc.tables[0].cell(5,1).text = 'Supabase Free previously reported for authentication, PostgreSQL and storage; current subscription, backup facilities and region unverified'
doc.tables[0].cell(5,2).text = 'My earlier setup confirmation, SQL scripts and database exports; live account check outstanding'
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            for q in cell.paragraphs:
                s=q.text.replace('Author-confirmed deployment', 'Deployment confirmed by me').replace('Author confirmation', 'My confirmation').replace('author confirmation', 'my confirmation').replace('author reported successful workflow', 'I reported successful workflow').replace('workflow author-confirmed', 'workflow confirmed by me').replace('operation was author-confirmed', 'I confirmed operation')
                if s!=q.text:q.text=s

# Supplementary references for this amendment; retain existing in-text research citations.
doc.add_heading('References for the amended controls', level=1)
for text in [
    'Express. (n.d.). CORS middleware. Retrieved October 29, 2026, from https://expressjs.com/en/resources/middleware/cors/',
    'Republic of Kenya. (2019). Data Protection Act, 2019 (No. 24 of 2019). https://kentrade.go.ke/wp-content/uploads/2022/09/Data-Protection-Act-1.pdf',
    'Supabase. (n.d.-a). Database backups. Retrieved October 29, 2026, from https://supabase.com/docs/guides/platform/backups',
    'Supabase. (n.d.-b). Pricing & fees. Retrieved October 29, 2026, from https://supabase.com/pricing',
    'World Wide Web Consortium. (2021). Web authentication: An API for accessing public key credentials, level 2. https://www.w3.org/TR/webauthn-2/'
]: doc.add_paragraph(text)

alltext='\n'.join(q.text for q in doc.paragraphs)+'\n'+'\n'.join(c.text for t in doc.tables for r in t.rows for c in r.cells)
assert not re.search(r'\bthe (?:student|author)\b|author-confirmed', alltext, re.I)
assert len(doc.tables)==15 and len(doc.inline_shapes)==2
for v in ['75.800','0.654082','C4-T18','C4-T22','C4-T24','C4-T25','C4-T26','C4-T27','180 calendar days','30 calendar days']: assert v in alltext, v
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            for q in cell.paragraphs:
                for run in q.runs:
                    run.font.size = Pt(9)
doc.tables[9].cell(7,4).text = 'Available; workflow confirmed by me'
for run in doc.tables[9].cell(7,4).paragraphs[0].runs: run.font.size=Pt(9)
shape=doc.inline_shapes[0]
ratio=Inches(3.6)/shape.width
shape.height=int(shape.height*ratio)
shape.width=Inches(3.6)
for q in doc.paragraphs:
    if q.text.startswith('C4-T'):
        text=q.text
        lead, rest=text.split('. ',1)
        q.text=''
        q.add_run(lead+'. ').bold=True
        q.add_run(rest)
    if q.text=='References for the amended controls':
        q.paragraph_format.page_break_before=True
doc.save(root/'Chapter_5_Aligned_Chapter_4.docx')
print('Saved amended chapter; 15 original tables and 2 figures preserved.')
