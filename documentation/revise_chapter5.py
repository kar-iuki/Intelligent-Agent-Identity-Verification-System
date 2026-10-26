from pathlib import Path
import re
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

base = Path(__file__).resolve().parent
doc = Document(base / 'Chapter_5_System_Implementation_Testing_and_Evaluation.docx')
remove = False
for para in list(doc.paragraphs):
    if para.text == 'Chapter 5 Evidence References':
        previous = para._p.getprevious()
        if previous is not None and not ''.join(previous.itertext()).strip():
            previous.getparent().remove(previous)
        remove = True
    if remove:
        para._p.getparent().remove(para._p)
        continue
    original = para.text
    revised = re.sub(r'\s*\[E\d+[^\]]*\]', '', original)
    revised = revised.replace('Evidence references E1–E10 identify the repository files supporting the discussion. ', '')
    additions = {
        'The implementation was organised': ' The project README documented the local setup, while the machine learning README recorded the experiment environment.',
        'The interface used Vue': ' These dependencies were documented in the frontend and backend package manifests, the AI service requirements file and the saved model manifest.',
        'The relational schema represented': ' The database schema and accompanying SQL migration scripts defined these entities and constraints.',
        'Authentication and profile management': ' The authentication and role middleware, together with the project README, documented these controls.',
        'The decision-model dataset contained': ' The machine learning README, generation configuration and dataset metadata recorded the composition and assumptions of the dataset.',
        'An RBF support vector machine': ' The training scripts and frozen experiment protocol recorded the parameter grid and cross-validation procedure.',
        'The model manifest recorded': ' The artifact manifest and SVM service implementation documented these loading and prediction checks.',
        'Table 5.6 links': ' The saved verification_checks.json file in the v3 experiment directory contained the suite outputs and exit codes.',
        'Both the saved v2 incumbent': ' The v3 experiment summary and improvement report contained the metrics presented in Tables 5.8–5.10.',
        'Liveness and face matching had': ' The saved permutation-importance results recorded the mean changes and variation across repeats.',
        'The retention implementation removed': ' The document-retention service and the README described this policy.',
    }
    for prefix, addition in additions.items():
        if revised.startswith(prefix): revised += addition
    if revised != original: para.text = revised
    if revised.startswith('Project repository: https://'):
        url = revised.split('Project repository: ',1)[1]
        para.clear()
        link = OxmlElement('w:hyperlink')
        link.set(qn('r:id'), para.part.relate_to(url, RT.HYPERLINK, is_external=True))
        run = OxmlElement('w:r'); props = OxmlElement('w:rPr')
        style = OxmlElement('w:rStyle'); style.set(qn('w:val'),'Hyperlink'); props.append(style)
        run.append(props); text=OxmlElement('w:t'); text.text='Project repository'; run.append(text); link.append(run); para._p.append(link)
for para in doc.paragraphs:
    if para.style.name == 'Caption': para.paragraph_format.keep_with_next = True
# Remove a final page-break paragraph left by the old evidence appendix.
while doc.paragraphs and not doc.paragraphs[-1].text.strip():
    elem=doc.paragraphs[-1]._p; elem.getparent().remove(elem)
content='\n'.join(p.text for p in doc.paragraphs)
assert not re.search(r'\bE\d+\b',content)
assert len(doc.tables)==11
assert all(f'5.{i} ' in content for i in range(1,8))
out=base/'Chapter_5.docx'
doc.save(out)
print(f'Saved {out}; 11 tables retained; evidence labels and reference appendix removed.')
