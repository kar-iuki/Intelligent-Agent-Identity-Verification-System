from pathlib import Path
import json, zipfile, re
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from PIL import Image
from chapter4_content import *

ROOT=Path(r'C:\Users\ikari\Desktop\School Work\Intelligent-Agent-Identity-Verification-System')
OUT=ROOT/'documentation'
ASSETS=OUT/'chapter4_wireframes'
WORK=OUT/'chapter4_revision_work'
WORK.mkdir(exist_ok=True)
DOC=Document()
sec=DOC.sections[0]
sec.page_width=Cm(21);sec.page_height=Cm(29.7)
sec.top_margin=Cm(2.3);sec.bottom_margin=Cm(2.2);sec.left_margin=Cm(2.4);sec.right_margin=Cm(2.4)
sec.header_distance=Cm(1);sec.footer_distance=Cm(1)
page_num=OxmlElement('w:pgNumType');page_num.set(qn('w:start'),'41');sec._sectPr.append(page_num)
for name in ['Normal','Title','Heading 1','Heading 2','Heading 3','Caption']:
 s=DOC.styles[name];s.font.name='Times New Roman';s.font.color.rgb=RGBColor(0,0,0)
 fonts=s.element.get_or_add_rPr().rFonts
 for key in list(fonts.attrib):
  if 'Theme' in key:del fonts.attrib[key]
 for key in ['ascii','hAnsi','cs','eastAsia']:fonts.set(qn('w:'+key),'Times New Roman')
 if name=='Normal':
  s.font.size=Pt(12);s.paragraph_format.line_spacing=1.15;s.paragraph_format.space_after=Pt(7)
 elif name=='Title':
  s.font.size=Pt(16);s.font.bold=True;s.paragraph_format.space_after=Pt(14)
 elif name.startswith('Heading'):
  s.font.size=Pt({'Heading 1':14,'Heading 2':12.5,'Heading 3':12}[name]);s.font.bold=True
  s.paragraph_format.space_before=Pt(12);s.paragraph_format.space_after=Pt(6);s.paragraph_format.keep_with_next=True
 else:
  s.font.size=Pt(11);s.paragraph_format.space_before=Pt(5);s.paragraph_format.space_after=Pt(8)
DOC.styles['Normal'].paragraph_format.widow_control=True
for element in list(DOC.styles.element.iter(qn('w:pBdr'))):element.getparent().remove(element)
DOC.core_properties.title='Chapter 4 System Analysis and Design'
DOC.core_properties.subject='Intelligent Agent Identity Verification System'
DOC.core_properties.author=''
DOC.core_properties.keywords='requirements, system design, identity verification, wireframes'
p=sec.footer.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.CENTER
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');p._p.append(fld)

def para(s,style=None,keep=False):
 p=DOC.add_paragraph(s,style)
 if not style:
  p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
  p.paragraph_format.keep_together=True
 p.paragraph_format.keep_with_next=bool(keep or (style and (style.startswith('Heading ') or style=='Title')))
 return p
NEXT_PAGE=False
def heading(s,level=1):
 global NEXT_PAGE
 p=para(s,'Heading '+str(level))
 if NEXT_PAGE:p.paragraph_format.page_break_before=True;NEXT_PAGE=False
 return p
def newpage():
 global NEXT_PAGE
 NEXT_PAGE=True
def caption(s,above=False):
 p=para(s,'Caption',above);p.alignment=WD_ALIGN_PARAGRAPH.CENTER;return p
def table(headers,rows,widths,caption_text=None,font=10):
 if caption_text:caption(caption_text,True)
 t=DOC.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 for c,w in zip(t.columns,widths):c.width=Inches(w)
 for c,s in zip(t.rows[0].cells,headers):c.text=s
 for row in rows:
  cells=t.add_row().cells
  for c,s in zip(cells,row):c.text=str(s)
 for i,row in enumerate(t.rows):
  trp=row._tr.get_or_add_trPr();trp.append(OxmlElement('w:cantSplit'))
  if i==0:trp.append(OxmlElement('w:tblHeader'))
  for j,c in enumerate(row.cells):
   c.width=Inches(widths[j]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   pr=c._tc.get_or_add_tcPr();m=OxmlElement('w:tcMar')
   for side in ['top','left','bottom','right']:
    e=OxmlElement('w:'+side);e.set(qn('w:w'),'75' if side in ['top','bottom'] else '90');e.set(qn('w:type'),'dxa');m.append(e)
   pr.append(m)
   borders=OxmlElement('w:tcBorders')
   for side in ['top','left','bottom','right']:
    e=OxmlElement('w:'+side);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
   pr.append(borders)
   if i==0:
    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E8E8E8');pr.append(shade)
   for p in c.paragraphs:
    p.paragraph_format.space_after=Pt(1);p.paragraph_format.space_before=Pt(1);p.paragraph_format.line_spacing=1.04
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER if j==0 else WD_ALIGN_PARAGRAPH.LEFT
    if i==0:p.paragraph_format.keep_with_next=True
    for r in p.runs:r.font.size=Pt(font);r.bold=i==0
 return t
def req_table(groups,number,title):
 rows=[]
 for group,rs in groups:
  rows.append(('',group,''))
  for id,priority,statement,verify in rs:rows.append((id+'\n'+priority,statement,verify))
 t=table(['ID\nPriority\nSource','Requirement','Verification plan'],rows,[.83,3.37,2.17],f'Table {number}: {title}',10)
 for row in t.rows[1:]:
  if not row.cells[0].text:
   for c in row.cells:
    sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'F3F3F3');c._tc.get_or_add_tcPr().append(sh)
    for p in c.paragraphs:
     p.paragraph_format.keep_with_next=True
     for r in p.runs:r.bold=True
 return t
def fig(path,label,maxheight=5.55):
 im=Image.open(path);w,h=im.size
 width=min(6.36,maxheight*w/h)
 p=DOC.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(0);p.paragraph_format.keep_with_next=True
 shape=p.add_run().add_picture(str(path),width=Inches(width))
 shape._inline.docPr.set('descr',label)
 caption(label)
def hyperlink(text,url):
 p=DOC.add_paragraph();p.paragraph_format.space_after=Pt(6)
 h=OxmlElement('w:hyperlink');h.set(qn('r:id'),p.part.relate_to(url,RT.HYPERLINK,is_external=True))
 r=OxmlElement('w:r');rp=OxmlElement('w:rPr');c=OxmlElement('w:color');c.set(qn('w:val'),'222222');rp.append(c);r.append(rp)
 tx=OxmlElement('w:t');tx.text=text;r.append(tx);h.append(r);p._p.append(h)

para('Chapter 4 System Analysis and Design','Title')
heading('4.1 Introduction')
for p in INTRO:para(p)
heading('4.2 System Requirements')
para('The requirements define required behaviour, quality conditions, data obligations and integration boundaries. The catalogue follows the requirements-engineering focus of ISO/IEC/IEEE 29148:2018. Quality categories are informed by ISO/IEC 25010:2023; these references guide organisation and evaluation and are not a claim of certification (ISO/IEC/IEEE, 2018; ISO/IEC, 2023).')
para('Requirement identifiers are stable references. FR denotes a functional requirement, NFR a quality or evaluation requirement, DR a data requirement and IR an interface requirement. H, M and L indicate high, medium and low priority within the project. Source codes are A for agent task needs, B for administrator review needs, O for operational integrity and protection, and R for research reproducibility and evaluation. A stated verification method is a planned check, not a reported pass. Chapter 5 records the evidence actually obtained.')
table(['Stakeholder or need','Design responsibility'],[
 ('Agent','Complete onboarding, understand failures and see the current outcome without accessing another agent\'s data.'),
 ('Administrator','Inspect exception cases and decision evidence, make accountable interventions and retrieve audit history.'),
 ('System maintainer','Protect credentials and stored evidence, handle failures and manage retention and recovery.'),
 ('Research evaluation','Preserve data/model provenance, isolate evaluation and report consequential classification errors.')],[1.5,4.87],'Table 4.1: Stakeholder needs used to organise the requirements',10.5)

newpage();heading('4.2.1 Functional Requirements',2)
para('The functional requirements describe the actor, required behaviour and expected verification. Registration establishes the account and personal profile; evidence capture then supplies the document and live selfie. Automated processing produces a decision, while administrators handle exceptions. A client-side capture challenge and model-based liveness analysis serve different parts of this workflow.')
req_table(FR,'4.2','Functional requirements')
para('The repeated-attempt defaults are three recorded failures per IP or device within 24 hours; they are configurable guardrail choices and must be tested at their boundaries. Evidence is limited to JPEG or PNG at 5 MiB per file, where 1 MiB equals 1,048,576 bytes. Completing account registration or a selfie challenge does not itself confer verified-agent access.')

newpage();heading('4.2.2 Non Functional Requirements',2)
para('The quality requirements cover performance measurement, security, privacy, reliability, interaction quality, maintainability and model evaluation. Performance is specified through a reproducible measurement protocol. An operational response-time acceptance limit must be justified using measurements in the intended environment and stakeholder needs before it is treated as a service commitment. Cold-start and steady-state behaviour must be reported separately.')
req_table(NFR,'4.3','Quality and evaluation requirements')
para('Model quality is assessed through the cost-relevant errors as well as aggregate metrics. A comparative improvement on synthetic data is not an absolute operational approval threshold. Deployment acceptance for real applicants requires justified error tolerances and representative evidence. The interface review uses selected WCAG 2.2 concerns, including labels, keyboard use, focus and status feedback, without claiming full conformance from wireframe inspection alone (World Wide Web Consortium, 2023).')

newpage();heading('4.2.3 Data Requirements',2)
for p in DATA_TEXT:para(p)
table(['ID\nPriority\nSource','Requirement','Verification plan'],[(x+'\n'+p,s,v) for x,p,s,v in DR],[.83,3.37,2.17],'Table 4.4: Data requirements',10)
heading('Verification feature contract',3)
para('The classifier consumes the ordered features in Table 4.5. Raw image-quality values are not interchangeable with arbitrary zero-to-one ratings. The fitted model pipeline performs its defined transformations. When the backend aggregates document and selfie quality, the resulting score must retain the same physical definition and unit used in development. Missing, non-finite or invalid values must not be silently converted to successful evidence.')
table(['Feature','Meaning','Range','Interpretation'],FEATURES,[1.65,1.15,.98,2.59],'Table 4.5: Six-feature input contract',9.5)
heading('Training and evaluation data design',3)
for p in DATASET_TEXT:para(p)
heading('Retention and recovery',3)
para('Verified-case images are retained for three business days after the latest successful decision, including manual approval. Business days are Monday to Friday in Africa/Nairobi; public holidays are not excluded. For example, a Friday approval at 14:00 expires on Wednesday at 14:00. Cleanup is checked at startup and every 15 minutes, so scheduled deletion depends on a running backend. Failed removals are retried; signed links must not extend access beyond the permitted window.')
para('Cleanup removes the image objects and clears their references while retaining metadata, scores, decisions and audit history. Pending, review and rejected cases are excluded from this automatic policy. Their retention periods and the lifetime of retained metadata remain policy decisions requiring explicit definition. A recovery procedure must also account for storage copies and backups so restored data do not silently reintroduce expired evidence. No paid backup capability or completed restore test is assumed from the use of a hosted database.')

newpage();heading('4.2.4 Interface and Integration Requirements',2)
for p in INTERFACE_TEXT:para(p)
table(['ID\nPriority\nSource','Requirement','Verification plan'],[(x+'\n'+p,s,v) for x,p,s,v in IR],[.83,3.37,2.17],'Table 4.6: Interface and integration requirements',10)

for i,(section,title,before,after) in enumerate(FIGURES,1):
 newpage()
 if i==1:
  heading('4.3 System Analysis Diagrams')
 elif i==2:
  heading('4.4 System Design Diagrams')
 heading(section,2);para(before)
 fig(WORK/'original_figures'/f'figure_4_{i:02d}.png',f'Figure 4.{i}: {title}',5.5 if i!=3 else 5.75)
 para(after)
 if i==6:
  para('Table 4.7 records the logical schema independently of implementation-specific SQL types. Each identifier denotes a stable key. The operational schema uses UUID identifiers; the logical rules allow an uncompleted account or attempt to exist without its later records.')
  table(['Entity','Important attributes','Relationship and integrity rule'],[(entity.replace('_', ' '), attributes, rule) for entity, attributes, rule in SCHEMA],[1.28,2.48,2.61],'Table 4.7: Logical entity and integrity catalogue',10)
  para('The core separation reduces duplication: account identity, personal profile, evidence metadata and repeated verification attempts are distinct. Derived scores and decisions reference the attempt instead of copying the profile. Structured audit details support varied event context without adding a column for every event type. The optional passkey support entities extend authentication rather than the classifier feature set. Exact deployed policies and schema migrations require implementation-level inspection.')

newpage();heading('4.4.6 User Interface Design and Wireframes',2)
para('The wireframes show the principal screens and states using grayscale controls and bracketed data placeholders. They contain no applicant records and document the current design without claiming that they preceded implementation or establish usability. Each view links to the requirements it supports.')
para('Agents move from authentication through details, document capture, selfie and outcome. Administrators navigate the directory, review, audit and model views. The desktop sidebar collapses into a mobile menu; paired fields stack in reading order. Only an authorised verified outcome permits workspace access.')
for i,(title,name,req,before,after) in enumerate(WIREFRAMES,1):
 if i>1:newpage()
 heading(f'4.4.6.{i} {title}',3)
 para(before)
 p=para('Requirements addressed: '+req+'.');p.paragraph_format.space_after=Pt(7)
 for r in p.runs:r.italic=True;r.font.size=Pt(10.5)
 fig(ASSETS/(name+'.png'),f'Figure 4.{i+6}: {title} wireframe',4.5)
 para(after)

newpage();heading('Interface states and responsive behaviour',3)
para('Each asynchronous screen distinguishes loading, empty, success and failure states. The interface keeps the relevant error beside the affected task, avoids duplicate submission while a request is active and preserves a route to recovery. It must not expose protected content simply because a client button is visible; access is enforced by the backend. Text labels supplement colour, navigation exposes the current location and modal focus returns to its trigger on dismissal.')
para('On a phone, the navigation menu precedes the task, form columns become a single sequence and image previews retain their aspect ratio. Wide administrator tables require controlled horizontal navigation or an equivalent readable presentation. Both light and dark modes require contrast and focus checks. Camera and human-check accessibility require device and assistive-technology evaluation; a schematic alone cannot establish inclusive operation.')
table(['View group','Important state or exception','Verification'],[
 ('Authentication','Unconfirmed email; failed credentials; cancelled passkey; recovery link','C4-T01, C4-T14'),
 ('Profile and capture','Invalid field; duplicate ID; denied camera; poor image; partial recapture','C4-T02 to T05'),
 ('Verification','Processing; verified; review; rejected; unavailable service','C4-T08, C4-T09, C4-T18'),
 ('Administrator','Empty queue; new review event; expired images; authorised intervention','C4-T11, C4-T12, C4-T22'),
 ('Audit and model report','No matches; failed export; missing report; active/fallback distinction','C4-T12, C4-T13, C4-T16')],[1.28,3.7,1.39],'Table 4.8: Interface state coverage',10)

newpage();heading('4.5 Requirements Traceability and Verification Plan')
para('Traceability connects the problem and objectives to a requirement, a design view and a reproducible check. The objective references below follow the five objective themes used in the project evaluation: O1 investigates existing registration and verification practice; O2 identifies challenges and fraud risks; O3 examines existing KYC platforms; O4 develops the system; and O5 tests and validates effectiveness. O1 and O3 supply research context through the literature review, while O2, O4 and O5 directly drive the software and evaluation requirements.')
para('Table 4.9 maps the complete requirement catalogue to the design and the verification scenarios in Table 4.10. The C4-T identifiers are Chapter 4 planning references. They do not renumber or claim to be the TC identifiers already used in Chapter 5. In the table, T02 after C4-T01 is shorthand for C4-T02, and the same prefix applies to the remaining scenario numbers.')
table(['Requirement group','Objective and need','Design reference','Scenario'],TRACE,[1.74,.88,1.72,2.03],'Table 4.9: Requirements traceability matrix',9.5)
table(['Scenario','Focus','Required evidence'],TESTS,[.75,1.45,4.17],'Table 4.10: Planned verification scenarios',10)
heading('Connection to Chapter 5 evidence',2)
para('The Chapter 5 classifier-contract tests TC01 to TC04 and TC07 to TC09 provide evidence relevant to C4-T07, C4-T08 and part of C4-T18. Its experiment checks TC05 and TC06 relate to C4-T23. The recorded passkey and retention suites support parts of C4-T14 and C4-T22. Passing an isolated suite does not demonstrate the complete hosted user workflow, a real-device ceremony or live storage cleanup.')
para('System-level verification requires dated records from the configured environment, the software/model revision, input conditions, expected and actual results, and the requirement identifier. Latency, demographic fairness, presentation-attack coverage, accessibility, informed disclosure and restoration must remain unverified until their corresponding evidence exists. If a requirement changes, its affected interface, data rules, diagrams and tests must be reviewed together. Changes to approved project scope are discussed with the supervisor.')

heading('4.6 Chapter Summary')
para('The design connects account registration and controlled evidence capture with six-score processing, an explicit decision basis and role-dependent access. Administrator review, audit history, bounded image retention and optional passkeys support the main workflow. The requirements catalogue, logical entity description, interface wireframes and traceability plan establish what the implementation and evaluation must demonstrate. Chapter 5 reports the implemented environment, actual tests, classifier results and remaining evidence limitations.')
heading('References',1)
for text,url in REFERENCES:
 para(text);hyperlink(url,url)
para('Project design evidence: the maintained application source, database migrations and version 3 experiment records, together with Chapter 5 System Implementation Testing and Evaluation, hosted deployment revision dated 27 October 2026. Model-development details are recorded in the project\'s machine learning README, experiment protocol, split manifests and saved reports. The wireframe source-to-screen mapping is retained with the editable figure files.')

path=OUT/'Chapter_4_Revised.docx';DOC.save(path)

readme='''# Chapter 4 wireframe assets

The chapter contains ten grayscale wireframes as Figures 4.7 to 4.16.
Each figure is supplied as an editable SVG and a high-resolution PNG.
SVG files can be opened in a browser or edited in a vector editor.
They contain placeholder labels, not real applicant records or evaluation results.

## Source mapping

- 4.7: LoginPage.vue, RegisterPage.vue and passkey sign-in controls.
- 4.8: AgentDashboard.vue personal-details step and WorkspaceShell.vue.
- 4.9: AgentDashboard.vue document step and DocumentCaptureStep.vue.
- 4.10: LiveSelfieChallenge.vue.
- 4.11: AgentDashboard.vue progress and outcome states.
- 4.12: AdminDashboard.vue directory, status filters and WorkspaceShell.vue.
- 4.13: AdminDashboard.vue case-detail drawer and decision controls.
- 4.14: AdminDashboard.vue audit list and export dialog.
- 4.15: ManagePasskeysPage.vue.
- 4.16: AdminModelEvaluation.vue.

These are design abstractions, not screenshots or proof of prior design activity.
Multiple alternative screens/states appear together in Figures 4.7 and 4.11.
The review drawer is expanded for legibility in Figure 4.13.
The chapter explains mobile reflow, state handling and acceptance checks.

## Existing figures still to be corrected by the author

Figures 4.1 to 4.6 were preserved from the supplied PDF without changing their content.
Replace them in Word when the updated diagrams are ready. Keep the figure numbers.

- 4.1: Confirm system boundary and external actors; draw only justified UML relationships.
- 4.2: Use consistent UML multiplicity/ownership notation and identifier terminology.
- 4.3: Account/profile and incomplete-request optionality; required audit and decision fields.
- 4.4: Request/response directions, auth/storage/realtime interactions and hosted boundaries.
- 4.5: Backend coordination, per-step persistence, quality rejection and service-failure paths.
- 4.6: Align the logical schema with Table 4.7, including decision basis, audit context and optional passkey entities.

## Editorial and verification notes

- Original FR-01 to FR-26 and NFR-01 to NFR-15 identifiers are retained with clarified wording.
- Added FR-27 to FR-34, NFR-16 to NFR-20, DR-01 to DR-12 and IR-01 to IR-10.
- Original timing promises lacked an evidence basis; the chapter specifies measurement and does not invent an SLA.
- Requirements describe intended obligations, not completed implementation or passing tests.
- Disclosure, non-verified retention, backup restoration and broad integration retry policy still need explicit evidence/policy.
- Check the OOAD/experimental approach and objective wording against the final approved Chapters 1 and 3.
- The separate manual-versus-two-AI use-case comparison activity is not fabricated here. Preserve its actual manual diagram, tool outputs, prompts and comparison evidence separately if required by the course.
- AI assistance: Codex assisted with source review, requirements drafting, wireframe generation and layout checking on 27 October 2026. No manual-before-AI exercise or supervisor approval is claimed.
- Chapter pagination starts at 41 to match the supplied extract; update the full report pagination and contents/list-of-figures fields after merging.
'''
(ASSETS/'README.md').write_text(readme,encoding='utf-8')
with zipfile.ZipFile(OUT/'Chapter_4_Wireframes.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(ASSETS.iterdir()):
  if f.suffix in ['.svg','.png','.md']:z.write(f,f.name)

from docx.text.paragraph import Paragraph
from docx.table import Table
lines=[]
for element in DOC.element.body:
 if element.tag.endswith('}p'):
  p=Paragraph(element,DOC)
  if p.text:lines.append(p.text)
 elif element.tag.endswith('}tbl'):
  t=Table(element,DOC)
  for row in t.rows:lines.append(' | '.join(c.text.replace('\n',' ') for c in row.cells))
text='\n'.join(lines)
(WORK/'chapter4_text.txt').write_text(text,encoding='utf-8')
assert len(DOC.inline_shapes)==16
for kind,n in [('FR',34),('NFR',20),('DR',12),('IR',10)]:
 for i in range(1,n+1):assert f'{kind}-{i:02d}' in text
assert all(f'Figure 4.{i}:' in text for i in range(1,17))
print(f'Saved {path}; {len(text.split())} words; {len(DOC.tables)} tables; 16 figures.')
