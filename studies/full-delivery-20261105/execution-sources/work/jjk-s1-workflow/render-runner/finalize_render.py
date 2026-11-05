"""Freeze executor evidence only. Artistic approval remains with the independent auditor."""
from pathlib import Path
import argparse,json,hashlib,shutil,time,re
BASE=Path(__file__).resolve().parents[3]
ROOT=BASE/'outputs/jjk-s1-workflow'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
p=argparse.ArgumentParser();p.add_argument('--loop',type=int,required=True);p.add_argument('--frames',type=int,nargs='*',default=[]);a=p.parse_args()
loop=ROOT/'loops'/f'loop-{a.loop:02}'
e=json.loads((loop/'execution.json').read_text(encoding='utf-8'));assert e['executor']=='/root/s1_render_execution' and e['all20CurrentPayloadProofsVerified']
video=ROOT/e['video'];assert sha(video)==e['sha256']
proofs=sorted((loop/'render-proofs').glob('chunk-*.json'));assert len(proofs)==20
fresh=[];reused=[];logs=[];logdir=loop/'render-logs';logdir.mkdir(exist_ok=True)
for file in proofs:
 r=json.loads(file.read_text(encoding='utf-8'))
 if r.get('planSha256')==e['editSha256']:fresh.append(r['chunk'])
 else:assert r.get('currentValidationPlanSha256')==e['editSha256'];reused.append(r['chunk'])
 passes={re.match(r'pass-(\d+)/',name).group(1) for name in r['actualRenderPayloadFiles'] if re.match(r'pass-(\d+)/',name)};assert len(passes)==1
 source=Path(e['renderWork'])/f'chunk-{r["chunk"]:02}'/f'hyperframes-{passes.pop()}.log';assert source.is_file();dest=logdir/f'chunk-{r["chunk"]:02}-actual-cli.log';shutil.copy2(source,dest);logs.append({'source':str(source),'file':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest)})
for batch in sorted((Path(e['renderWork'])/'batch-logs').glob(f'loop{a.loop}-*')):
 for source in sorted(batch.iterdir()):
  if source.is_file() and (source.suffix in ['.log','.json']):
   dest=logdir/batch.name/source.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(source,dest);logs.append({'source':str(source),'file':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest)})
evidence=loop/'evidence'/'render-runner';evidence.mkdir(exist_ok=True,parents=True);images=[]
for frame in a.frames:
 name=f'frame_{frame+1:06}.png';source=Path(e['renderWork'])/'master-frames'/name;dest=evidence/name;shutil.copy2(source,dest)
 images.append({'globalFrameZeroBased':frame,'file':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest)})
report={'state':'rendered_awaiting_independent_review','executor':e['executor'],'loop':a.loop,'createdUnix':time.time(),'video':e['video'],'videoBytes':video.stat().st_size,'videoSha256':e['sha256'],'planSha256':e['editSha256'],'codeSha256':e['codeSha256'],'fps':e['fps'],'frames':e['frames'],'seconds':e['seconds'],'size':[e['width'],e['height']],'all20CurrentPayloadProofsVerified':True,'newlyCapturedChunks':fresh,'reusedAfterInputEquivalenceValidationChunks':reused,'newlyCapturedFrames':len(fresh)*72,'reusedValidatedFrames':len(reused)*72,'proofFiles':{v.name:sha(v) for v in proofs},'renderLogs':logs,'observedEvidence':images,'actualListeningPerformed':e['actualListeningPerformed'],'scope':'Technical execution proof, not artistic approval. Reused PNGs retain original capture provenance and explicit producer-rebind history.'}
(loop/'render-completion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['state','videoSha256','videoBytes','size','frames','newlyCapturedFrames','reusedValidatedFrames']},ensure_ascii=False))
