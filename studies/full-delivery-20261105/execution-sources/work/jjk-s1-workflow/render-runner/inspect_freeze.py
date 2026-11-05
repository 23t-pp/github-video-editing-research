"""Read-only executor verification of immutable plan/code/actual chunk HTML."""
from pathlib import Path
import argparse,json,hashlib,sys,time
BASE=Path(__file__).resolve().parents[3];ROOT=BASE/'outputs/jjk-s1-workflow';HF=ROOT/'hyperframes';sys.path.insert(0,str(HF))
from composition import build
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
p=argparse.ArgumentParser();p.add_argument('--loop',type=int,required=True);a=p.parse_args();folder=ROOT/'loops'/f'loop-{a.loop:02}';freeze_path=folder/'frozen.json';freeze=json.loads(freeze_path.read_text(encoding='utf-8'));plan_path=ROOT/freeze['plan'];assert sha(plan_path)==freeze['planSha256'];plan=json.loads(plan_path.read_text(encoding='utf-8'))
for name,digest in freeze['codeHashes'].items():assert sha(HF/name)==digest,(name,'frozen code mismatch')
changed=[];checks=[]
for chunk in range(20):
 html=build(plan,chunk*72,(chunk+1)*72,True)[0];actual=hashlib.sha256(html.encode()).hexdigest();assert actual==freeze['chunkHtmlSha256'][str(chunk)],(chunk,'HTML differs from frozen')
 old_path=ROOT/'loops'/f'loop-{a.loop-1:02}'/'render-proofs'/f'chunk-{chunk:02}.json';old=json.loads(old_path.read_text(encoding='utf-8'));different=old['inputSpec']['htmlSha256']!=actual
 if different:changed.append(chunk)
 checks.append({'chunk':chunk,'htmlSha256':actual,'htmlChanged':different})
assert changed==freeze['newChunks'],(changed,freeze['newChunks']);assert sorted(set(range(20))-set(changed))==freeze['unchangedChunks']
assert sha(plan_path)==freeze['planSha256']
for name,digest in freeze['codeHashes'].items():assert sha(HF/name)==digest,(name,'code drift during inspection')
report={'state':'pass_frozen_execution_inputs_only','executor':'/root/s1_render_execution','loop':a.loop,'createdUnix':time.time(),'planSha256':freeze['planSha256'],'frozenSha256':sha(freeze_path),'codeHashes':freeze['codeHashes'],'actualChangedChunks':changed,'htmlChecks':checks,'scope':'Read-only generated HTML and producer freeze verification. This does not replace the independent frozen-plan gate or actual payload re-decode reuse proof; no capture/rebind performed.'}
(folder/'executor-frozen-input-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:report[k] for k in ['state','planSha256','actualChangedChunks']},ensure_ascii=False))
