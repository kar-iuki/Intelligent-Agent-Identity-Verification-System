import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { finalizePresentation } from '/Users/test/.codex/plugins/cache/openai-primary-runtime/presentations/26.1123.11515/skills/presentations/container_tools/artifact_tool_utils.mjs';
const workspaceDir='/Users/test/Desktop/Personal Projects/Intelligent-Agent-Identity-Verification-System';
const build=path.join(workspaceDir,'.verity-cover-build');
const skill='/Users/test/.codex/plugins/cache/openai-primary-runtime/presentations/26.1123.11515/skills/presentations';
const source='/private/var/folders/yz/chz0y66d46g01g89dx2l4vrh0000gp/T/codex-file-preview-Dcdnks/Verity_Proposal_Final.pptx';
const result=await finalizePresentation({
  workspaceDir,candidatePath:path.join(build,'candidate.pptx'),
  finalPath:path.join(workspaceDir,'output/verity-cover/Verity_Proposal_Final_Fingerprint.pptx'),
  explicitTotalSlideCount:13,
  pythonExecutable:'/Users/test/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',
  integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],
  fontPolicy:{basis:'reference',families:['Aptos'],referencePath:source,referenceSha256:createHash('sha256').update(await fs.readFile(source)).digest('hex')},
  verifyArtifactToolImport:true,
  receiptPath:path.join(build,'validation.json'),
});
console.log(JSON.stringify(result,null,2));
