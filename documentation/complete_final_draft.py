from pathlib import Path
from copy import deepcopy
import json,re
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE as RT

root=Path(__file__).resolve().parents[1]
out=root/'documentation'
doc=Document(r'C:\Users\ikari\Downloads\Chapter 5 System Implementation, Testing and Evaluation.docx')
if 'Caption' not in doc.styles:
 from docx.enum.style import WD_STYLE_TYPE
 doc.styles.add_style('Caption',WD_STYLE_TYPE.PARAGRAPH)
ps=list(doc.paragraphs)
def setp(i,text): ps[i].text=text
def after(i,text):
 el=OxmlElement('w:p'); ps[i]._p.addnext(el); p=Paragraph(el,ps[i]._parent); p.style=doc.styles['Normal']; p.add_run(text); return p
def remove(i): ps[i]._p.getparent().remove(ps[i]._p)
def cell(t,r,c,text): doc.tables[t].cell(r,c).text=text
def fig(i,filename,caption):
 p=ps[i]; p.clear(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
 p.add_run().add_picture(str(root/'ai-service/ml/experiments/v3'/filename),width=Inches(5.5))
 p.paragraph_format.keep_with_next=True
 cap=after(i,caption); cap.style=doc.styles['Caption']; cap.alignment=WD_ALIGN_PARAGRAPH.CENTER

setp(12,'Backend configuration supplied the Supabase URL and keys, the AI service URL, the listening port and authentication settings. Service-role credentials remained server-side. Optional passkeys required a configured relying-party identifier, allowed origins and Node.js 22 or newer. The isolated classifier environment used Python 3.13.3, scikit-learn 1.9.0, NumPy 2.5.3 and Flask 3.1.3, verified during the 23 October 2026 test run. The full image-processing requirements left EasyOCR, InsightFace and PyTorch unpinned. Those packages were not installed in the inspected general Python environment, so their historically tested versions could not be established. The local repository did not contain a Docker deployment configuration confirming a Hugging Face release.')
setp(21,'The classifier reproduction procedure used ai-service/ml/requirements-experiment.lock.txt and ai-service/ml/improve_model.py with --jobs 3 and --promote. Reproduction requires an isolated copy because promotion replaces the active model bundle, and the runner refuses to repeat a completed experiment on the same evaluation draw. The older train_model.py script produces version 2 artifacts and is not interchangeable with the version 3 workflow. The model was not retrained for this documentation update. Health endpoints provide service-responsiveness checks, but successful live health checks and a complete database-backed demonstration were not recorded in this update.')
setp(25,'Table 5.3 compares the design choices stated in the project draft with the inspected implementation. The implementation column is supported by code and experiment records; the approved Chapters 3 and 4 were not independently revalidated during this update.')
setp(28,ps[28].text.replace('exactly one score row and one decision row','at most one score row and one decision row').replace('The Chapter 4 ERD uses camel-case attribute names, while the implemented schema uses snake case; the entities and relationships are the same.','The implemented schema uses snake_case attribute names. Foreign keys and unique constraints define relationships, but successful processing is needed to create the corresponding score and decision records.'))
setp(33,'Authentication, roles and passkeys. Authentication middleware rejected missing or invalid bearer tokens, and role middleware restricted administrator operations. Email/password and Google sign-in were supplemented by WebAuthn passkeys using SimpleWebAuthn. The public.passkeys table stored the credential identifier, public key, signature counter, transports, device type, backup status, label and device metadata; the application did not receive device fingerprint or face templates from WebAuthn. Challenge and rate-limit records were stored separately. Client support detection controlled which passkey actions were offered.')
setp(34,'Registration and evidence capture. Agents entered personal details and supplied document and selfie images through the capture interface. Server upload middleware accepted JPEG and PNG MIME types and imposed a 5 MiB limit per file, returning a validation message for unsupported or oversized files. Registration logic checked existing national identity numbers. The storage integration used a private Supabase bucket; its deployed access settings were not live-tested in this update.')
setp(39,'Administrator review. The administrator controller implemented approval and rejection, updated the associated decision, request status and access record, and recorded the acting administrator. Dashboard endpoints returned totals by verification status and daily counts. Image viewing used signed URLs, normally valid for up to one hour and further limited by the remaining audit window for verified cases. The realtime service emitted new_review_case notifications through Socket.IO. These behaviours were confirmed from source code; a live administrator demonstration was not recorded in this update.')
setp(40,'Registration-time guardrails. Middleware checked duplicate national identity numbers, blocked disposable email domains, and counts of guardrail events and failed verification initiations from an IP address or device fingerprint. The defaults allowed three counted events in a 24-hour lookback window, with environment variables able to override these values. Duplicate identities produced a conflict response and attempt limits produced a rate-limit response with retry information. These are configured rules, not measured attack-detection rates.')
remove(42)
for i in [45,47,48,51,52]: setp(i,re.sub(r' \(Figure 5\.\d+\)','',ps[i].text))
setp(44,'The implemented workflow connected the following interface, application and database operations. The sequence describes code paths; the live execution status is reported separately in Table 5.10.')
setp(53,'Interface screenshots were not included as test evidence because no captured live demonstration accompanied this evaluation. The model figures below visualise recorded numerical results and do not imply that the complete user workflow was exercised.')
setp(58,'The generator reused stored benchmark measurements: 1,000 LFW face pairs, 1,200 NUAA presentations and 500 MIDV quality frames together with MIDV OCR measurements. The machine learning README and dataset metadata recorded summary statistics and file hashes. These historical measurements informed score distributions; the source images were not reprocessed during the version 3 experiment or this documentation update. None of the benchmark sources supplied the three-class KYC labels.')
after(64,'For each parameter combination, the 7,000 training cases were divided into five stratified folds of approximately 1,400 cases. A fresh SVM was fitted on four folds (approximately 5,600 cases) and assessed on the remaining fold; the held-out fold changed across five rounds. Macro F1 was averaged across the five validation results. The 24 combinations therefore required 120 fold-level fits per grid, followed by refitting the selected configuration on all 7,000 training cases. Scaling was fitted only on the training portion of each fold. The calibration, selection and fresh evaluation cases were excluded from this cross-validation process.')
setp(73,'Automated testing covered classifier contracts, experiment integrity, backend decisions, retention and passkey controls. The three Python suites used unittest from Python 3.13.3; backend suites used Node.js 24.19.0 and its built-in node:test runner. Tests used synthetic features, test credentials, mocks and an embedded PostgreSQL database for the passkey migration. The recorded version 3 log contained 14 passing tests. On 23 October 2026, those tests were rerun and the scope was expanded as summarised in Table 5.9. Live system and participant-based evaluations remained separate and were not inferred from isolated test success. Requirement identifiers in Tables 5.8 and 5.10 are retained from the supplied draft.')
setp(76,'Table 5.8 summarises representative automated test cases. All nine scenarios were covered by the saved version 3 test log and the successful rerun on 23 October 2026. Each pass required the executable assertions to agree with the expected outcome, rather than a manual judgement that the interface appeared to work.')
setp(79,'Table 5.9 records the expanded automated run of 23 October 2026. Python used the existing .venv-kyc environment; backend tests ran with node --test against the five listed files. Logs are retained in documentation/final_draft_evidence. Passkey service tests used controlled session and storage boundaries, and the database test executed the migration in PGlite. Retention tests used mocked storage and database records. These tests did not certify a live Supabase deployment, physical authenticators, image inference or user acceptance. Table 5.10 therefore distinguishes local coverage from unexecuted live scenarios.')
setp(82,'The saved version 2 incumbent, selected version 3 SVM and saved Decision Tree reference were evaluated on the same 1,500 fresh synthetic cases in the recorded version 3 experiment. The Decision Tree values were recovered from the reference_models section of improvement_report.json; the tree was not retrained or selected using this evaluation set. On 23 October 2026, the unchanged applyPlaceholderDecision function was additionally executed offline on those same cases. This post-hoc threshold comparison is descriptive and did not influence the earlier SVM selection or release gate. Table 5.11 reports all four approaches.')
after(88,'The Decision Tree achieved 75.667% accuracy and macro F1 of 0.648469, compared with 75.800% and 0.654082 for version 3. The SVM therefore exceeded the tree on these point estimates, but no paired significance test between these two models was recorded. The threshold rules achieved 28.667% accuracy and macro F1 of 0.263647. They verified no Rejected cases and only eight Manual Review cases, but rejected 471 of the 900 Verified cases and sent another 363 to review. Their low false-verification count therefore came with substantially poorer acceptance of genuine simulated cases. Rule outputs were not calibrated probabilities, so log loss and Brier scores were not reported for that baseline.')
fig(87,'candidate_confusion_matrix.png','Figure 5.1: Version 3 confusion matrix on 1,500 fresh synthetic cases. Source: saved version 3 evaluation artifacts.')
fig(92,'svm_permutation_importance.png','Figure 5.2: Version 3 permutation importance measured by the decrease in macro F1. Error bars show variation across repeated shuffles. Source: saved version 3 evaluation artifacts.')
setp(96,'Project repository: https://github.com/kar-iuki/Intelligent-Agent-Identity-Verification-System')
setp(97,'The repository contained the frontend, backend, AI service, database scripts, dependency files, tests and saved experiment reports. The inspected local HEAD was a8f64cb, dated 20 October 2026. Its reachable history contained 25 commits dated from 1 September to 20 October 2026. No release tags were present. The revised chapter and its new evidence files were local additions and were not represented by that commit. Legacy model bundles were retained for comparison and rollback. Supervisor access and a repository-wide licence were not verified; no public reuse permission is asserted here.')
setp(98,'The .gitignore excluded .env and .env.local files, dependency folders, build output, local AI caches and selected test artifacts. These exclusions do not prove that credentials were never committed or that all private datasets are excluded. A complete repository-history secret audit was not performed, and no claim of a clean historical secret scan or credential rotation is made.')
setp(100,'Claude (Anthropic) was identified in the supplied draft as assisting with documentation and implementation prompts. OpenAI Codex assisted with reviewing the source and saved reports, preparing this chapter, executing the isolated automated tests and the offline threshold comparison, and checking the Word layout. Its changes were checked against the inspected code and retained test outputs. The student remains responsible for reviewing the final chapter, verifying alignment with the approved objectives and references, and approving the submission.')
setp(106,'The implementation provided an integrated evidence-processing architecture: separate services produced six scores and decisions retained model or fallback provenance. The automated checks supported selected interface, invalid-input, passkey and retention behaviours. Table 5.10 shows that a complete live verification workflow and user acceptance were not established by this evaluation; passing isolated tests did not satisfy those broader requirements.')
setp(108,'Linked score, decision, access and audit records provided a basis for reconstructing verification activity. Token validation, role checks, guardrails and image retention added controls. The successful passkey and retention tests supplied limited executable evidence for those modules, while the other access-control and security scenarios in Table 5.10 remained unverified in a live deployment. No general security certification or privacy-compliance conclusion was drawn.')
setp(111,'Evaluation coverage remained limited. No demographic fairness study, current presentation-attack campaign, target-camera comparison, prospective pilot, participant-based usability study or ten-run full-pipeline performance benchmark was established by the retained evidence. Local automated tests used controlled dependencies and did not replace those evaluations. The small calibration and selection partitions left a risk of policy overfitting. Classifier metrics also excluded quality gates, threshold fallback and administrator intervention.')
setp(112,'The retention job removed images only for verified agents, while pending, review and rejected cases were excluded from the automated purge. The local retention tests confirmed that exclusion, so it remained a data-minimisation limitation. Unpinned image-processing dependencies and the absence of a historical environment snapshot also limited exact reproduction of the complete pipeline.')

cell(0,1,1,'AMD Ryzen 5 5625U with Radeon Graphics; 7.4 GiB OS-reported usable memory; C: volume 475.8 GiB; Windows 11 Home Single Language, version 10.0.26200')
cell(0,1,2,'Host inventory on 23 October 2026; current development machine, not a benchmarked minimum')
cell(0,2,1,'Camera-capable browser required; historically tested browser names and versions were not recorded')
cell(0,2,2,'No browser-compatibility verdict established')
cell(0,4,1,'Local Flask configuration, port 5000; remote Hugging Face hosting not verified')
cell(0,5,1,'Supabase authentication, PostgreSQL and storage; service plan and region not verified')
cell(2,4,2,'Saved v2 and v3 SVMs and Decision Tree evaluated on the same fresh set; existing threshold rules added as an offline descriptive baseline')
cell(2,2,3,'Only NUAA measurements were recorded; the reason for omitting Replay-Attack was not independently established')
cell(3,9,0,'passkeys (optional)');cell(3,9,1,'credential_id, public_key, counter, label, device and transport metadata')
cell(6,1,1,'4,000-row synthetic generator with largely separable class ranges; earlier scaler/CV methodology')
cell(6,1,2,'100.000% accuracy and macro F1 1.000000 on 600 historical test cases; artificially easy separation limits interpretation')
cell(6,2,1,'10,000 scenarios with overlap, fold-local scaling, training-only tuning and held-out calibration')
cell(6,2,2,'74.333% accuracy and macro F1 0.621383 on its original 1,500-case test set')

t=doc.tables[8]
while len(t.rows)>1:t._tbl.remove(t.rows[-1]._tr)
rows=[('test_svm.py','6','6 passed'),('test_kyc_experiment.py','2','2 passed'),('test_kyc_improvement.py','4','4 passed'),('kycDecision.test.js','2','2 passed'),('documentRetention.test.js','5','5 passed'),('passkeys.test.js','9','9 passed'),('passkeyRoutes.test.js','1','1 passed'),('passkeyDatabase.test.js','1','1 passed')]
frontend=(out/'final_draft_evidence/frontend_retest_unrestricted.txt').read_text(encoding='utf-8',errors='replace')
clean=re.sub(r'\x1b\[[0-9;]*m','',frontend)
match=re.search(r'Tests\s+(\d+) passed',clean)
ft=int(match.group(1)) if match else 0
if ft: rows.append(('Frontend unit tests (Vitest 5.0.3)',str(ft),f'{ft} passed'))
rows.append(('Expanded run total',str(30+ft),f'{30+ft} passed; no assertion failures in completed suites'))
for row in rows:
 for c,v in zip(t.add_row().cells,row):c.text=v
after(79,('Frontend unit tests used Vitest 5.0.3 with jsdom. The initial launch used an incorrect relative path, and the corrected launch encountered a filesystem permission restriction before tests started. The path and execution permissions were corrected without changing application code; the subsequent run passed '+str(ft)+' tests. These startup incidents are retained with the rerun logs and were not application assertion failures.') if ft else 'Frontend execution encountered a test-runner startup problem; its output was retained separately and no frontend pass verdict was added to the successful test total.')
for r in range(1,len(doc.tables[9].rows)):cell(9,r,4,'Not executed as a live system test; no pass/fail verdict')
cell(9,1,4,'Partial: local passkey-route authentication checks passed; full live token scenario not executed')
cell(9,16,4,'Partial: isolated passkey service, route and database checks passed; physical-device sign-in not executed')
cell(9,17,4,'Partial: 5 retention tests passed with mocked storage; live bucket cleanup not executed')
cell(9,18,3,'Task completion without assistance, measured with consented participants') if len(doc.tables[9].rows)>18 else None
# TC27 is the last scenario row.
cell(9,len(doc.tables[9].rows)-1,3,'Task completion without assistance, measured with consented participants')
cell(9,len(doc.tables[9].rows)-1,4,'No participant study recorded; usability effectiveness not established')
ref=json.loads((root/'ai-service/ml/experiments/v3/improvement_report.json').read_text())['reference_models']['decision_tree']
thr=json.loads((out/'final_draft_evidence/threshold_metrics.json').read_text())
vals=[f"{ref['accuracy']*100:.3f}%",f"{ref['macro_f1']:.6f}",f"{ref['weighted_f1']:.6f}",'95','208',f"{ref['probability_calibration']['log_loss']:.6f}",f"{ref['probability_calibration']['multiclass_brier_sum']:.6f}"]
tv=[f"{thr['accuracy']*100:.3f}%",f"{thr['macro_f1']:.6f}",f"{thr['weighted_f1']:.6f}",'0','8','Not applicable','Not applicable']
for r,(a,b) in enumerate(zip(vals,tv),1):cell(10,r,3,a);cell(10,r,4,b)
cell(14,5,1,'Tables 5.8 and 5.9: automated test evidence; Table 5.10: live evaluation coverage; Tables 5.11–5.14: classifier and baseline results')
cell(14,5,2,f'Partly met: {30+ft} isolated automated tests passed in the expanded run; synthetic classifier performance established; full live system effectiveness and usability not established')

# User-confirmed deployment details and the subsequently supplied database exports.
setp(7,'The system was implemented as a web prototype connected to Supabase on the Free plan. The documented local interface, application server and AI service used ports 5173, 3000 and 5000. At the time of this report, deployment of the AI service to Microsoft Azure was in progress; completed Azure hosting was not claimed. Table 5.1 records the current development equipment and the confirmed service configuration. These are observed configurations, not measured minimum requirements.')
setp(12,ps[12].text.replace('The local repository did not contain a Docker deployment configuration confirming a Hugging Face release.','The intended cloud host was Microsoft Azure, with deployment still in progress. An Azure service tier, region and completed deployment endpoint were not established.'))
cell(0,4,1,'Local Flask configuration, port 5000; Microsoft Azure deployment in progress')
cell(0,4,2,'Project configuration and author confirmation; no completed Azure deployment claimed')
cell(0,5,1,'Supabase Free plan: authentication, PostgreSQL and storage; region not recorded')
cell(0,5,2,'Author confirmation, SQL scripts and supplied database exports')
setp(21,ps[21].text.replace('Health endpoints provide service-responsiveness checks, but successful live health checks and a complete database-backed demonstration were not recorded in this update.','Health endpoints provide service-responsiveness checks. Separate live-test evidence was supplied as exports of verification requests, scores and decisions; the observed results are summarised in Table 5.10.'))
setp(53,'The supplied live-test evidence consisted of database exports rather than interface screenshots. Their aggregate results are reported in Table 5.10. Personal identifiers and image links are omitted from the chapter. Figures 5.1 and 5.2 show the separate recorded model evaluation.')
setp(73,ps[73].text.replace('Live system and participant-based evaluations remained separate and were not inferred from isolated test success. Requirement identifiers in Tables 5.8 and 5.10 are retained from the supplied draft.','Three Supabase exports additionally documented live request, score and decision records. These observations were assessed separately from automated assertions and did not establish participant-based usability. Requirement identifiers in Table 5.8 are retained from the supplied draft.'))
setp(79,f'The expanded run on 23 October 2026 passed {30+ft} automated tests, as shown in Table 5.9. Python used unittest in .venv-kyc; backend tests used node:test, with PGlite for the passkey migration and mocks for storage and session boundaries. Frontend tests used Vitest with jsdom. The original 14 tests are included in this total, not additional to it. Logs are retained in documentation/final_draft_evidence. Table 5.10 separately summarises the live Supabase exports and the limits of the available system-level evidence.')
setp(80,'Table 5.10: Live test observations and system-level coverage')
t=doc.tables[9]
while len(t.rows)>1:t._tbl.remove(t.rows[-1]._tr)
for c,v in zip(t.rows[0].cells,['Area','Evidence','Observed result','Interpretation','Status']):c.text=v
live_rows=[
('Request and score storage','Request and score CSV exports','12 requests across 8 agent identifiers; all 12 linked to six-score records','Supports persistence of verification evidence','Observed'),
('Decision output','Decision CSV joined by request_id','9 linked decisions: 7 Verified, 2 Rejected; all matched request status','Supports recorded outcome generation; no Manual Review example','Observed'),
('Decision provenance','decision_basis values','5 svm_model and 4 placeholder_threshold decisions','Both paths occurred; model version and fallback cause were not recorded','Observed'),
('Incomplete attempts','Request-to-decision join','3 pending requests had no decision in the supplied exports','Completion was not demonstrated for every recorded attempt','Open'),
('Passkeys and retention','Isolated automated test logs','Passkey service, route and migration checks and 5 retention tests passed','Does not certify physical authenticators or live storage cleanup','Locally tested'),
('Other system requirements','No corresponding records supplied','Access grants, administrator actions, negative security cases, latency and participant usability not established','Requires separate records; no pass/fail result assigned','Not verified')]
for row in live_rows:
 for c,v in zip(t.add_row().cells,row):c.text=v
after(80,'The supplied files were Supabase Snippet Untitled query.csv (decisions), query (1).csv (requests) and query (2).csv (scores). Their timestamps covered 21 September to 3 October 2026 in Africa/Nairobi. Nine decision probability triples summed to one, and every exported decision linked to a request with matching status. These records show stored outputs, not classification accuracy: they contain no independently adjudicated ground truth, no model-version field and no access-control or audit-log export. Historical threshold outputs must not be assumed to replay under the current rule revision.')
setp(106,'The implementation combined evidence capture, numerical scoring and persistent verification decisions. The live exports supported this path through 12 request/score pairs and nine matching decisions. The automated tests added evidence for selected interfaces, input handling, passkeys and retention. However, three attempts remained pending, and access enforcement, administrator intervention and user acceptance were not established by the supplied exports.')
setp(108,'Decision provenance distinguished SVM outputs from threshold-rule outputs in the live records. Token validation, role checks, guardrails and image retention were implemented, but the exports did not include access-control or audit records that would prove their live enforcement. The successful isolated passkey and retention tests supplied narrower evidence for those modules; no general security or privacy-compliance conclusion was drawn.')
setp(111,'Evaluation coverage remained limited. The live evidence comprised 12 requests from eight agent identifiers, with no independent identity labels or recorded model versions; it could not establish real-world accuracy. No demographic fairness study, presentation-attack campaign, camera comparison, participant usability study or timed ten-run pipeline benchmark was documented. Small calibration and selection partitions also left a risk of policy overfitting. Model metrics excluded the full effects of capture quality gates, fallback and administrator intervention.')
cell(14,5,2,f'Partly met: {30+ft} automated tests passed; live exports showed 12 score-linked requests and 9 decisions. Real-world accuracy, complete security coverage and usability remain unestablished.')

# Preserve the supplied chapter structure, with consistent readable table formatting.
for style in ['Normal','Heading 1','Heading 2','Heading 3','Caption']:
 doc.styles[style].font.name='Times New Roman';doc.styles[style].font.color.rgb=RGBColor(0,0,0)
doc.styles['Normal'].font.size=Pt(11)
doc.styles['Normal'].paragraph_format.space_after=Pt(5)
doc.styles['Normal'].paragraph_format.line_spacing=1.05
for p in doc.paragraphs:
 if p.text.startswith('Frontend unit tests used Vitest'):
  p.text='Frontend startup failed initially because of an invocation-path error and then a filesystem restriction. After correcting the execution setup without changing application code, all 16 tests passed. Initial outputs and the successful rerun were retained.'
 if p.text.startswith('The supplied files were Supabase'):
  ps[80]._p.addprevious(p._p)
 if p._p.xpath('.//w:drawing'):
  p.paragraph_format.space_before=Pt(8)
  p.paragraph_format.line_spacing=1.0
 if p.text.startswith('Table 5.'):
  p.style=doc.styles['Caption'];p.paragraph_format.keep_with_next=True
 if p.style.name.startswith('Heading'):p.paragraph_format.keep_with_next=True
for ti,t in enumerate(doc.tables):
 t.autofit=False
 widths={3:[1.6,2.8,2.1],4:[.8,1.4,2.7,1.6],5:[.45,.8,1.65,1.7,1.9]}[len(t.columns)]
 if ti==10:widths=[2.1,1.1,1.1,1.1,1.1]
 if ti in [11,12]:widths=[2,1.5,1.5,1.5]
 if ti==7:widths=[.5,1.3,3.9,.8]
 if ti==8:widths=[3.5,.6,2.4]
 if ti==9:widths=[1.05,1.1,2,1.6,.75]
 for col,w in zip(t.columns,widths):col.width=Inches(w)
 borders=OxmlElement('w:tblBorders')
 for edge in ['top','bottom','left','right','insideH','insideV']:
  e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
 t._tbl.tblPr.append(borders)
 for ri,row in enumerate(t.rows):
  pr=row._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
  if ri==0:pr.append(OxmlElement('w:tblHeader'))
  for c,w in zip(row.cells,widths):
   c.width=Inches(w)
   if ri==0:
    sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E7E6E6');c._tc.get_or_add_tcPr().append(sh)
   for p in c.paragraphs:
    p.paragraph_format.space_before=Pt(3);p.paragraph_format.space_after=Pt(3);p.paragraph_format.line_spacing=1
    if ri==0:p.paragraph_format.keep_with_next=True
    for r in p.runs:r.font.size=Pt(9);r.bold=ri==0
for e in list(doc.element.iter(qn('w:pBdr')))+list(doc.styles.element.iter(qn('w:pBdr'))):e.getparent().remove(e)
alltext='\n'.join([p.text for p in doc.paragraphs]+[c.text for t in doc.tables for r in t.rows for c in r.cells])
assert not re.search(r'\[TO |\[TBC\]|\[confirm|\[Revise|\[If ',alltext), 'Unresolved editing prompt'
doc.save(out/'Chapter_5_Final_Revised.docx')
print('Saved revised chapter; automated total',30+ft)
