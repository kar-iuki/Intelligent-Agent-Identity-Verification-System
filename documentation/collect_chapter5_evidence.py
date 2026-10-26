from pathlib import Path
import subprocess,json,concurrent.futures,datetime
root=Path(__file__).resolve().parents[1]
out=root/'documentation'/'final_draft_evidence'; out.mkdir(exist_ok=True)
node=r'C:\Users\ikari\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
py=str(root/'.venv-kyc/Scripts/python.exe')
jobs=[(name,[py,'-X','utf8',f'ai-service/tests/{name}.py']) for name in ['test_svm','test_kyc_experiment','test_kyc_improvement']]
jobs += [('backend',[node,'--test','backend/tests/kycDecision.test.js','backend/tests/documentRetention.test.js','backend/tests/passkeys.test.js','backend/tests/passkeyRoutes.test.js','backend/tests/passkeyDatabase.test.js']),('frontend',[node,'frontend/node_modules/vitest/vitest.mjs','run','--config','vitest.config.js'])]
def run(job):
 name,cmd=job
 try:
  r=subprocess.run(cmd,cwd=root/'frontend' if name=='frontend' else root,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
  result={'suite':name,'command':cmd,'exit_code':r.returncode,'output':r.stdout+r.stderr}
 except Exception as e: result={'suite':name,'error':str(e)}
 (out/f'{name}.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 return {'suite':name,'exit_code':result.get('exit_code'),'tail':result.get('output',result.get('error',''))[-1500:]}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 for result in ex.map(run,jobs): print(json.dumps(result),flush=True)
