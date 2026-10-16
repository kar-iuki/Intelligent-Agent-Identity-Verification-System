from pathlib import Path
from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table

base = Path(__file__).resolve().parent
doc = Document(base / 'Chapter_5_System_Implementation_Testing_and_Evaluation.docx')
lines = []
for block in doc.element.body:
    if block.tag.endswith('}p'):
        para = Paragraph(block, doc)
        text = para.text.strip()
        if not text:
            continue
        if text.startswith('Project repository: https:'):
            text = '[Project repository](https://github.com/kar-iuki/Intelligent-Agent-Identity-Verification-System)'
        if para.style.name == 'Title': text = '# ' + text
        elif para.style.name.startswith('Heading '): text = '#' * (int(para.style.name.split()[-1])+1) + ' ' + text
        elif para.style.name == 'Caption': text = '**' + text + '**'
        lines += [text, '']
    elif block.tag.endswith('}tbl'):
        table = Table(block, doc)
        for i, row in enumerate(table.rows):
            lines.append('| ' + ' | '.join(c.text.replace('\n',' ').replace('|','\\|') for c in row.cells) + ' |')
            if i == 0: lines.append('| ' + ' | '.join('---' for c in row.cells) + ' |')
        lines.append('')
result = '\n'.join(lines)
path = base / 'Chapter_5_System_Implementation_Testing_and_Evaluation.md'
path.write_text(result, encoding='utf-8')
assert all(f'5.{n} ' in result for n in range(1,8))
assert result.count('**Table 5.') == 11
assert '75.800%' in result and '227' in result and '14 passed' in result
print(f'Saved {path}; {len(result.split())} words; 11 tables; sections 5.1 to 5.7 verified.')
