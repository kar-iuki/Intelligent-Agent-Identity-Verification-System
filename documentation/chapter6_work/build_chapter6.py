from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

root = Path(__file__).resolve().parents[1]
source = root / 'Chapter_6_Conclusions_Recommendations_and_Future_Work.md'
doc = Document()
section = doc.sections[0]
section.page_width, section.page_height = Inches(8.5), Inches(11)
section.top_margin = section.bottom_margin = section.left_margin = section.right_margin = Inches(1)
for name, size in [('Normal',11),('Title',16),('Heading 1',13),('Heading 2',12)]:
    style = doc.styles[name]
    style.font.name = 'Times New Roman'
    style.font.size = Pt(size)
    style.font.color.rgb = RGBColor(0,0,0)
    style.font.bold = name != 'Normal'
    style.paragraph_format.widow_control = True
    style.paragraph_format.keep_with_next = name != 'Normal'
    style.paragraph_format.space_after = Pt(5 if name in ['Normal','Heading 1'] else 4)
    style.paragraph_format.space_before = Pt({'Normal':0,'Title':18,'Heading 1':14,'Heading 2':12}[name])
doc.styles['Normal'].paragraph_format.line_spacing = 1.05
for style in doc.styles:
    for border in list(style.element.iter(qn('w:pBdr'))):
        border.getparent().remove(border)
    for fonts in style.element.iter(qn('w:rFonts')):
        for attr in list(fonts.attrib):
            if 'Theme' in attr:
                del fonts.attrib[attr]
for line in source.read_text(encoding='utf-8').splitlines():
    if not line.strip(): continue
    if line.startswith('# '): doc.add_paragraph(line[2:], 'Title')
    elif line.startswith('## '): doc.add_paragraph(line[3:], 'Heading 1')
    elif line.startswith('### '): doc.add_paragraph(line[4:], 'Heading 2')
    else: doc.add_paragraph(line)
for p in doc.paragraphs:
    for r in p.runs:
        r.font.name = 'Times New Roman'
        r.font.color.rgb = RGBColor(0,0,0)
    if p.text in ['6.2.4 Development of the Identity Verification System', '6.3 Recommendations', '6.4 Future Work']:
        p.paragraph_format.page_break_before = True
doc.core_properties.title = 'Chapter 6 Conclusions Recommendations and Future Work'
doc.core_properties.subject = 'Intelligent Agent Identity Verification System'
doc.core_properties.author = ''
doc.core_properties.comments = ''
out=root/'Chapter_6_Conclusions_Recommendations_and_Future_Work.docx'
doc.save(out)
print(out)
print('Words:',len(source.read_text(encoding='utf-8').split()))
