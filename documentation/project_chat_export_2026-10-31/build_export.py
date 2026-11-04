from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import re
import subprocess
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SUPPORT = OUT / 'supporting'
SUPPORT.mkdir(exist_ok=True)

def clean(text):
    text = re.sub(r'\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,}\b', '[REDACTED TOKEN]', text)
    text = re.sub(r'\b(?:ghp_|github_pat_|hf_)[A-Za-z0-9_]{20,}\b', '[REDACTED TOKEN]', text)
    return text

def read(path):
    return clean(path.read_text(encoding='utf-8-sig', errors='replace'))

def write(path, text):
    path.write_text(clean(text), encoding='utf-8')

def section(title, body):
    return '\n\n---\n\n## ' + title + '\n\n' + body + '\n'

def docx_text(path):
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    lines = []
    def para(p):
        return ''.join(t.text or '' for t in p.findall('.//w:t', ns))
    for e in root.find('w:body', ns):
        tag = e.tag.rsplit('}', 1)[-1]
        if tag == 'p':
            text = para(e)
            if text:
                lines.append(text)
        elif tag == 'tbl':
            for row in e.findall('w:tr', ns):
                lines.append(' | '.join(' / '.join(para(p) for p in cell.findall('w:p', ns)) for cell in row.findall('w:tc', ns)))
            lines.append('')
    return clean('\n\n'.join(lines))

data = json.loads(read(OUT / 'retrieved_chats.json'))
chats = data['chats']
messages = [m for c in chats for t in c['turns'] for m in t['messages']]
chat_text = '# Retrieved project conversations\n\nHistorical messages follow. Earlier proposals and claims may be superseded by current source and later results. User/assistant text is preserved as retrieved, except ambient browser state and token-shaped secrets. No internal reasoning or tool command bodies are exported. Dates use Africa/Nairobi.\n'
coverage = ['# Export coverage and limitations', '', f"Chats: {len(chats)}. Turns: {sum(len(c['turns']) for c in chats)}. User/assistant messages: {len(messages)}.", '', 'All retrieved older-page cursors were exhausted. The app provides accessible conversation records, not an account-wide archival guarantee. Titles outside project scope were not exported. No archived Codex chats were returned. Unrelated data-governance coursework and vulnerability-assessment VM setup were inspected for relevance and excluded; unrelated wallet/service-matching turns from the early ideas chat were excluded.', '', '| Chat | Kind | Turns | Older pages remaining |', '|---|---|---:|---|']
truncation_notes = []
for c in chats:
    coverage.append(f"| {c['title']} | {c['kind']} | {len(c['turns'])} | {c['hasMore']} |")
    chat_text += section(c['title'], f"Chat ID: {c['id']}\n\nScope: {c['scope']}")
    for t in c['turns']:
        ts = t.get('startedAt')
        date = datetime.fromtimestamp(ts, ZoneInfo('Africa/Nairobi')).isoformat() if ts else 'Date not returned'
        chat_text += f"\n### Turn {t['id']}\n\nDate: {date}; recorded status: {t['status']}.\n"
        for m in t['messages']:
            label = m['role'].title() + (f" ({m['phase']})" if m.get('phase') else '')
            chat_text += f"\n**{label}**\n\n{m['text']}\n"
            if m.get('truncated'):
                chat_text += '\n[The retrieval service marked this message truncated.]\n'
                truncation_notes.append(f"Truncated message: {c['title']}, turn {t['id']}, {len(m['text'])} returned characters. The KYC implementation chat also contains the extended task and measured results.")
coverage.extend([''] + truncation_notes)
write(SUPPORT / 'CONVERSATIONS.md', chat_text)

current = ['Chapter_4_Revised.docx', 'Chapter_5_Aligned_Chapter_4.docx', 'Chapter_6_Conclusions_Recommendations_and_Future_Work.docx']
current_text = '# Current chapter text snapshots\n\nExtracted from saved DOCX files on 31 October 2026. Text and table-cell order are preserved; figures, image annotations and pagination are not reconstructed. These documents predate some latest capture/UI changes.\n'
versions = '# Other saved chapter versions\n\nHistorical variants are retained here for context. Prefer the current chapter snapshots and handoff for current documentation.\n'
for path in sorted((ROOT / 'documentation').glob('*.docx')):
    body = docx_text(path)
    if path.name in current:
        current_text += section(path.name, body)
    else:
        versions += section(path.name, body)
write(SUPPORT / 'CURRENT_CHAPTERS.md', current_text)
write(SUPPORT / 'HISTORICAL_CHAPTER_VERSIONS.md', versions)

attachment_paths = set()
for m in messages:
    for match in re.finditer(r'C:[\\/][^\r\n"<>]*?\.(?:txt|docx|pdf)', m['text'], re.I):
        value = match.group(0)
        if '.codex' in value and 'attachments' in value:
            attachment_paths.add(str(Path(value).resolve()))
attachments_text = '# Available project attachment text\n\nThese are the guideline/reference files explicitly referenced in retrieved project messages. Image-only attachments and inaccessible files cannot be reconstructed from chat text.\n'
attachment_inventory = []
for value in sorted(attachment_paths):
    path = Path(value)
    if not path.is_file():
        attachment_inventory.append({'path': value, 'status': 'Not available at referenced path'})
        continue
    if path.suffix.lower() == '.txt':
        body = read(path)
    elif path.suffix.lower() == '.docx':
        body = docx_text(path)
    else:
        attachment_inventory.append({'path': value, 'status': 'PDF reference only; not text-extracted in this text export'})
        continue
    attachments_text += section(value, body)
    attachment_inventory.append({'path': value, 'status': 'Text included', 'characters': len(body)})
write(SUPPORT / 'ATTACHED_GUIDELINES_AND_REFERENCES.md', attachments_text)
write(SUPPORT / 'attachment_inventory.json', json.dumps(attachment_inventory, indent=2))

evidence_paths = [ROOT/'README.md', ROOT/'frontend/COLORS.md', ROOT/'documentation/deployment_checks_2026-10-27.json']
for folder in ['ai-service/ml/reports', 'ai-service/ml/experiments/v3', 'ai-service/ml/models', 'ai-service/ml/legacy_v1', 'documentation/final_draft_evidence']:
    for path in (ROOT/folder).glob('*'):
        if path.suffix.lower() in {'.md', '.json', '.txt'} and path.name not in {'threshold_predictions.json'}:
            evidence_paths.append(path)
for name in ['ai-service/ml/README.md', 'ai-service/ml/generation_config.json', 'ai-service/ml/data/kyc_synthetic_dataset_10000.metadata.json', 'ai-service/ml/requirements-experiment.lock.txt', 'ai-service/requirements.txt', 'documentation/chapter4_wireframes/README.md', 'documentation/chapter4_wireframes/manifest.json']:
    evidence_paths.append(ROOT/name)
evidence = '# Saved evidence and configuration descriptions\n\nThese are retained source records, not new test runs. The top-level ml/reports folder describes the original v2 experiment; experiments/v3 and models/artifact_manifest.json identify the v3 comparison and installed bundle. Failed commands and later retests are preserved where present.\n'
for path in dict.fromkeys(evidence_paths):
    if path.is_file():
        body = read(path)
        if path.suffix != '.md':
            body = '```' + path.suffix.lstrip('.') + '\n' + body + '\n```'
        evidence += section(path.relative_to(ROOT).as_posix(), body)
write(SUPPORT / 'SAVED_EVIDENCE.md', evidence)

git = r'C:\Users\ikari\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe'
def gitrun(*args):
    return subprocess.check_output([git, *args], cwd=ROOT).decode('utf-8', 'replace')
files = subprocess.check_output(['rg', '--files', '-g', '!node_modules', '-g', '!.venv*', '-g', '!venv', '-g', '!documentation/project_chat_export_2026-10-31/**'], cwd=ROOT).decode('utf-8', 'replace').splitlines()
index = '# Repository files and Git history\n\nSnapshot date: 31 October 2026. Paths are repository-relative. This is the visible project-file inventory excluding dependency environments and this export; it is not a list of private .env values.\n'
index += section('Commit history', '```text\n' + gitrun('log', '--reverse', '--format=%h | %ad | %s', '--date=iso-strict') + '\n```')
index += section('Commit change summaries', '```text\n' + gitrun('log', '--reverse', '--stat', '--format=%h | %ad | %s', '--date=short') + '\n```')
index += section('File inventory', '\n'.join('- ' + name.replace('\\', '/') for name in files))
write(SUPPORT / 'FILE_AND_COMMIT_INDEX.md', index)

source = '# Current application and experiment source snapshot\n\nText source only, as of local commit 7bd4632. This appendix is for exact implementation lookup. It is not a deployment archive. Dependencies, model binaries, raw data rows, private environment files and generated QA images are omitted.\n'
selected = []
extensions = {'.py', '.js', '.mjs', '.vue', '.css', '.sql', '.json', '.md', '.txt', '.yml'}
for name in files:
    path = ROOT/name
    rel = path.relative_to(ROOT).as_posix()
    if path.suffix.lower() not in extensions:
        continue
    if 'package-lock.json' in rel or '/reports/' in rel or '/experiments/' in rel or '/legacy_' in rel or '/ml/data/' in rel:
        continue
    if rel.startswith('documentation/'):
        continue
    if rel.startswith(('frontend/', 'backend/', 'database/', 'ai-service/')) or rel in {'package.json', 'README.md'}:
        if '.env' in path.name:
            continue
        selected.append(path)
env_names = set()
for path in sorted(selected):
    body = read(path)
    env_names.update(re.findall(r'process\.env\.([A-Z][A-Z0-9_]*)', body))
    env_names.update(re.findall(r'(?:getenv|environ\.get|_env_float|intEnv)\([\'\"]([A-Z][A-Z0-9_]*)', body))
    source += section(path.relative_to(ROOT).as_posix(), '````' + path.suffix.lstrip('.') + '\n' + body + '\n````')
source += section('Referenced environment variable names', '\n'.join('- '+name for name in sorted(env_names)))
write(SUPPORT / 'SOURCE_SNAPSHOT.md', source)

# Preserve relevant packaging text from the separate deployment task, if present.
deploy_root = Path(r'C:\Users\ikari\Documents\Codex\2026-10-22\referenced-chatgpt-conversation-this-is-an\outputs')
deployment = '# Separate deployment package text\n\nThese artifacts were produced in the hosting chat outside the main repository. A local package does not prove its exact bytes are the currently deployed image.\n'
deployment_inventory = []
if deploy_root.is_dir():
    for path in sorted(deploy_root.iterdir()):
        deployment_inventory.append({'name': path.name, 'bytes': path.stat().st_size if path.is_file() else None})
        if path.is_file() and (path.name == 'Dockerfile' or path.suffix.lower() in {'.md', '.py', '.yml', '.yaml'}):
            deployment += section(str(path), read(path))
    archive = deploy_root/'verity-github-build-fixed.zip'
    if not archive.is_file():
        archive = deploy_root/'verity-github-build.zip'
    if archive.is_file():
        with zipfile.ZipFile(archive) as z:
            wanted = {'Dockerfile', '.dockerignore', 'requirements.txt', 'app.py', 'wsgi.py', 'validate_models.py', 'download_models.py', 'README.md', 'build.yml', 'gunicorn.conf.py'}
            for name in z.namelist():
                if Path(name).name in wanted and not name.endswith('/'):
                    deployment += section(archive.name+': '+name, clean(z.read(name).decode('utf-8', 'replace')))
write(SUPPORT / 'DEPLOYMENT_PACKAGE_TEXT.md', deployment)
write(SUPPORT / 'deployment_artifact_inventory.json', json.dumps(deployment_inventory, indent=2))

coverage += ['', 'The original .env files, authentication/session tokens, raw identity images, unrelated conversations, internal reasoning and tool command bodies are intentionally excluded. Binary model weights, notebook output images, original diagrams and screenshots are indexed rather than reproduced as text. The complete project repository remains the authority for those binary assets.', '', 'Current chapter text was extracted from actual saved DOCX files. Attached plain text/DOCX references were included when their exact referenced local path was available. No source Word/PDF files were edited and no new DOCX was created.', '', 'This export does not revalidate old provider pricing, legal statements, hosted status or test outcomes. It preserves historical discussions and labels the important differences in the handoff.', '', 'Potentially missing content: unavailable image attachment contents; inaccessible external linked message bodies; original Chapters 1–3 unless provided in an included attachment; any chats not exposed by the available listing/retrieval service; one explicitly truncated KYC prompt answer.']
write(SUPPORT / 'COVERAGE.md', '\n'.join(coverage))

handoff = read(OUT/'PROJECT_HANDOFF.md')
full = handoff + '\n\n# Appendix A — Retrieval coverage\n\n' + read(SUPPORT/'COVERAGE.md')
full += '\n\n# Appendix B — Project conversations\n\n' + chat_text
full += '\n\n# Appendix C — Current documentation chapters\n\n' + current_text
full += '\n\n# Appendix D — Supplied guidelines and references\n\n' + attachments_text
full += '\n\n# Appendix E — Saved model and test evidence\n\n' + evidence
full += '\n\n# Appendix F — Separate deployment packaging\n\n' + deployment
full += '\n\n# Appendix G — Repository history and file inventory\n\n' + index
full += '\n\n# Additional supporting files\n\nThe ZIP also contains SOURCE_SNAPSHOT.md (full selected application/database/ML text source), HISTORICAL_CHAPTER_VERSIONS.md and machine-readable retrieved_chats.json. These are separate to keep this main text export manageable.\n'
write(OUT/'FULL_PROJECT_CHAT_EXPORT.md', full)
write(OUT/'FULL_PROJECT_CHAT_EXPORT.txt', full)

manifest = []
for path in sorted(OUT.rglob('*')):
    if path.is_file() and path.suffix not in {'.zip', '.py'} and path.name != 'manifest.json':
        payload = path.read_bytes()
        manifest.append({'path': path.relative_to(OUT).as_posix(), 'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest()})
write(OUT/'manifest.json', json.dumps({'date': '2026-10-31', 'repository_revision': gitrun('rev-parse', 'HEAD').strip(), 'chats': len(chats), 'turns': sum(len(c['turns']) for c in chats), 'messages': len(messages), 'source_files': len(selected), 'files': manifest}, indent=2))
with zipfile.ZipFile(OUT/'PROJECT_DOCUMENTATION_EXPORT.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for path in sorted(OUT.rglob('*')):
        if path.is_file() and path.suffix not in {'.zip', '.py'}:
            z.write(path, path.relative_to(OUT))
print(json.dumps({'chats': len(chats), 'turns': sum(len(c['turns']) for c in chats), 'messages': len(messages), 'source_files': len(selected), 'attachment_files': len(attachment_inventory), 'full_export_words': len(full.split()), 'full_export_bytes': (OUT/'FULL_PROJECT_CHAT_EXPORT.md').stat().st_size, 'zip_bytes': (OUT/'PROJECT_DOCUMENTATION_EXPORT.zip').stat().st_size}, indent=2))
