import path from 'node:path';
import { finalizePresentation } from '/Users/test/.codex/plugins/cache/openai-primary-runtime/presentations/26.1123.11515/skills/presentations/container_tools/artifact_tool_utils.mjs';
const workspaceDir='/Users/test/Desktop/Personal Projects/Intelligent-Agent-Identity-Verification-System';
const build=path.join(workspaceDir,'.verity-balanced-build');
const skill='/Users/test/.codex/plugins/cache/openai-primary-runtime/presentations/26.1123.11515/skills/presentations';
const tables=[4,6,7];
const result=await finalizePresentation({
 workspaceDir,candidatePath:path.join(build,'draft.pptx'),
 finalPath:path.join(workspaceDir,'output/verity-defence/Verity_Final_Defence_Expanded.pptx'),
 explicitTotalSlideCount:11,
 requiredNativeTableOwnerSlides:tables,
 requiredNativeChartOwnerSlides:[7],
 materializeLiteralChartWorkbooks:true,
 pythonExecutable:'/Users/test/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...tables.flatMap(n=>['--require-native-table-slide',String(n)])],
 fontPolicy:{basis:'design',families:['Aptos']},
 verifyArtifactToolImport:true,
 receiptPath:path.join(build,'validation.json'),
});
console.log(JSON.stringify({path:result.finalPath,passed:true,receipt:path.join(build,'validation.json')}));
