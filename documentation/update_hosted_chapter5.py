from pathlib import Path
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from docx.opc.constants import RELATIONSHIP_TYPE as RT

root=Path(__file__).resolve().parent
d=Document(root/'Chapter_5_Final_Revised.docx')
def after(p,text):
 e=OxmlElement('w:p');p._p.addnext(e);q=Paragraph(e,p._parent);q.style=d.styles['Normal'];q.add_run(text);return q
def link(p,label,url):
 h=OxmlElement('w:hyperlink');h.set(qn('r:id'),p.part.relate_to(url,RT.HYPERLINK,is_external=True));r=OxmlElement('w:r');t=OxmlElement('w:t');t.text=label;r.append(t);h.append(r);p._p.append(h)
for p in list(d.paragraphs):
 s=p.text
 if s.startswith('The system was implemented as a web prototype'):
  p.text='The system was developed locally and subsequently deployed using Vercel for the Vue frontend, Render for the Express backend, Microsoft Azure Container Apps for the Flask AI service and the Supabase Free plan for authentication, PostgreSQL and storage. By 27 October 2026, the author confirmed that the hosted workflow operated successfully. The local development ports remained 5173, 3000 and 5000; the public services used HTTPS endpoints. Table 5.1 distinguishes the development equipment from the hosted environment. These configurations are not measured minimum requirements.'
 elif s.startswith('Backend configuration supplied'):
  p.text=s.replace('The intended cloud host was Microsoft Azure, with deployment still in progress. An Azure service tier, region and completed deployment endpoint were not established.','The deployed AI hostname identified the Azure South Africa North region. Azure compute allocation, Render and Vercel service tiers, and the Supabase region were not recorded. The Render backend connected to the Azure AI endpoint; the frontend used the public backend address. Deployment secrets remained outside the report. The dependency versions above describe the recorded local experiment, not an independently inspected cloud runtime.')
 elif s=='The procedure below describes how the repository is installed, configured and verified.':
  p.text='The following steps describe the local installation used for development and reproduction. The subsequent paragraph records the hosted arrangement; local startup commands should not be interpreted as the full cloud deployment configuration.'
 elif s.startswith('The classifier reproduction procedure'):
  q=after(p,'Hosted deployment separated the three application services. Vercel served the frontend build, Render ran the Express backend, and Azure Container Apps hosted AI inference. Reproduction requires the deployed source revisions, build/start settings, complete AI model bundle and environment configuration, including permitted frontend origins and passkey relying-party settings. Exact cloud resource settings and deployed revision identifiers were not supplied. Public entry points are linked below.')
  for label,url in [('Frontend on Vercel','https://intelligent-agent-identity-verifica.vercel.app'),('Backend on Render','https://verity-backend-gvbs.onrender.com'),('AI service on Azure Container Apps','https://verity-ai.greenpond-207a4102.southafricanorth.azurecontainerapps.io')]:
   q=after(q,'');link(q,label,url)
 elif s.startswith('The implemented architecture separated'):
  p.text=s+' In the hosted arrangement, the browser loaded the Vercel frontend, which called the Render API. The backend coordinated requests to the Azure AI service and Supabase. This preserved the separation between the user interface, application logic, inference and persistent records.'
 elif s.startswith('The expanded run on 23 October'):
  after(p,'Hosted availability was checked on 27 October 2026: the Vercel frontend returned HTTP 200, and both backend and AI /health endpoints returned HTTP 200 with status: ok. The AI /api/svm/status endpoint returned HTTP 401 to an unauthenticated request, so the deployed model version was not independently established. The author separately confirmed that the hosted workflow worked. These checks demonstrate reachability and service health; they are not a rerun of the 46 local automated tests or a measured hosted accuracy study.')
 elif s.startswith('The implementation combined evidence capture'):
  p.text=s+' Deployment was subsequently completed across Vercel, Render and Azure, with public availability checks and author-confirmed successful operation recorded on 27 October 2026.'
 elif s.startswith('Evaluation coverage remained limited.'):
  p.text=s+' Completed hosting resolved the earlier deployment limitation, but did not provide measured cloud latency, concurrency or long-duration availability.'
 elif s.startswith('The repository contained the frontend'):
  p.text=s.replace('The inspected local HEAD was','At the 23 October documentation review, the inspected local HEAD was').replace('No release tags were present.','No release tags were present at that review. Those historical repository details do not identify the later deployed revisions.')

env=d.tables[0]
env.cell(3,1).text='Development: Vue 5173, Express 3000, Flask 5000. Hosted: Vercel frontend and Render backend over HTTPS.'
env.cell(3,2).text='Author-confirmed deployment; frontend and backend health checked 27 October 2026'
env.cell(4,1).text='Microsoft Azure Container Apps; South Africa North hostname; public HTTPS AI service. Compute tier not recorded.'
env.cell(4,2).text='Author-confirmed deployment; AI health endpoint returned HTTP 200 on 27 October 2026'
tests=d.tables[9]
row=tests.add_row()
for c,t in zip(row.cells,['Hosted application','Public endpoint checks and author confirmation, 27 October 2026','Frontend and both health endpoints returned HTTP 200; author reported successful workflow','Unauthenticated model-status request returned 401; no hosted accuracy or load benchmark','Available; workflow author-confirmed']):c.text=t
from docx.shared import Pt
for c in row.cells:
 for p in c.paragraphs:
  p.paragraph_format.space_before=Pt(3);p.paragraph_format.space_after=Pt(3);p.paragraph_format.line_spacing=1
  for r in p.runs:r.font.size=Pt(9)
row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
obj=d.tables[14]
obj.cell(4,2).text='Implemented and hosted on Vercel, Render and Azure. Recorded synthetic classifier accuracy: 75.800%; macro F1: 0.654082.'
obj.cell(5,2).text='Partly met: 46 local automated tests passed; live exports contained 12 score-linked requests and 9 decisions. Hosted endpoints were available and operation was author-confirmed; real-world accuracy and comprehensive security/usability remain unestablished.'
text='\n'.join(p.text for p in d.paragraphs)+'\n'+'\n'.join(c.text for t in d.tables for r in t.rows for c in r.cells)
assert 'deployment still in progress' not in text and 'deployment in progress' not in text
assert len(d.tables)==15 and len(d.inline_shapes)==2
d.save(root/'Chapter_5_Hosted_Deployment.docx')
print('Saved hosted deployment revision; 15 tables and 2 figures retained.')
