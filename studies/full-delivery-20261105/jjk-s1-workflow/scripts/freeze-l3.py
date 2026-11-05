"""Stage proof by default; --activate only after the independent L2 review exists."""
from pathlib import Path
import argparse,json,hashlib,sys,importlib.util,shutil
A=argparse.ArgumentParser();A.add_argument('--activate',action='store_true');a=A.parse_args()
R=Path(__file__).resolve().parent.parent;H=R/'hyperframes';L=R/'loops/loop-03';B=R/'loops/loop-02'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((L/'plan-proposal.json').read_text(encoding='utf-8'))
if a.activate:
 assert not (L/'execution.json').exists(),'Do not overwrite an executed loop; make an explicit revision snapshot'
 review=json.loads((B/'review.json').read_text(encoding='utf-8'));execution=json.loads((B/'execution.json').read_text(encoding='utf-8'))
 assert review['reviewer']=='/root/s1_design_auditor' and review['status'] in ['revise','pass']
 assert review['boundArtifacts'][execution['video']]==execution['sha256']
 for n in ['layoutfx','typefx']:shutil.copyfile(L/f'{n}-proposal.py',H/f'{n}.py')
 p['status']='frozen_revision_pending_actual_capture'
 target=L/'plan.json';target.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8');(H/'edit.json').write_bytes(target.read_bytes())
sys.path.insert(0,str(H))
for n in ['layoutfx','typefx']:
 path=H/f'{n}.py' if a.activate else L/f'{n}-proposal.py';s=importlib.util.spec_from_file_location(n,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.__file__=str(H/f'{n}.py');sys.modules[n]=m
from composition import build,save_editable
old=json.loads((B/'frozen-final.json').read_text(encoding='utf-8'))
hashes={str(i):hashlib.sha256(build(p,i*72,(i+1)*72,True)[0].encode()).hexdigest() for i in range(20)}
changed=[i for i in range(20) if hashes[str(i)]!=old['chunkHtmlSha256'][str(i)]]
assert changed==[8,11,13,14,15,16],changed
proof={'onlyChangedChunks':changed,'unchangedChunks':[i for i in range(20) if i not in changed],'chunkHtmlSha256':hashes,'activeCodeChanged':a.activate,'scope':'chunkHTML proof, actual reused PNG payloads must be reverified by independent renderer'}
(L/'staged-chunk-impact.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
if a.activate:
 code={n:sha(H/n) for n in ['composition.py','typefx.py','layoutfx.py','screenfx.py','barlow-glyphs.json']};dest=L/'code';dest.mkdir(exist_ok=True)
 for n in code:shutil.copyfile(H/n,dest/n)
 frozen={**proof,'plan':'loops/loop-03/plan.json','planSha256':sha(L/'plan.json'),'allowedChunks':list(range(20)),'newChunks':changed,'codeHashes':code,'baseVideoSha256':execution['sha256'],'l2ReviewSha256':sha(B/'review.json'),'status':'approved L2 findings→frozen L3 revision; actual capture and independent audit pending'}
 (L/'frozen.json').write_text(json.dumps(frozen,ensure_ascii=False,indent=2),encoding='utf-8');save_editable(build(p)[0])
 d=json.loads((L/'revision-diff.json').read_text(encoding='utf-8'));d['pending']=['independent renderer actual changed chunks','unchanged14 pixel payload rebind','1080 encode and independent L3 review'];d['inputL2ReviewSha256']=sha(B/'review.json');(L/'revision-diff.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'activated':a.activate,'changed':changed,'unchanged14':proof['unchangedChunks'],'planSha256':sha(L/'plan.json') if a.activate else None},ensure_ascii=False))
