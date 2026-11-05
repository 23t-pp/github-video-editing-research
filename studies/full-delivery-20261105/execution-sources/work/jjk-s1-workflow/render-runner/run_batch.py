"""One coordinator owns canonical heartbeat; child render jobs get separate heartbeats."""
from pathlib import Path
import argparse,subprocess,sys,json,time,os,hashlib,shutil
BASE=Path(__file__).resolve().parents[3];ROOT=BASE/'outputs/jjk-s1-workflow';HF=ROOT/'hyperframes'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,r):
 p.parent.mkdir(exist_ok=True,parents=True);t=p.with_name(p.name+f'.{os.getpid()}.tmp');t.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
 for attempt in range(6):
  try:t.replace(p);return
  except PermissionError:
   if attempt==5:raise
   print(f'ATOMIC_JSON_RETRY {p.name} attempt={attempt+1}/6',file=sys.stderr,flush=True);time.sleep(.05*(2**attempt))
p=argparse.ArgumentParser();p.add_argument('--loop',type=int,required=True);p.add_argument('--plan',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--chunks',type=int,nargs='+');p.add_argument('--parallel',type=int,default=1);p.add_argument('--encode-only',action='store_true');p.add_argument('--freeze',type=Path);a=p.parse_args();plan=a.plan.resolve();work=a.work.resolve();work.mkdir(exist_ok=True,parents=True)
if a.freeze:
 freeze=json.loads(a.freeze.read_text(encoding='utf-8'));assert sha(plan)==freeze['planSha256']
 for name,digest in freeze['codeHashes'].items():assert sha(HF/name)==digest,(name,'code drift before capture')
 if a.chunks:assert set(a.chunks)<=set(freeze['allowedChunks'])
token=f'loop{a.loop}-{int(time.time())}';logs=work/'batch-logs'/token;logs.mkdir(parents=True);jobs=[];handles=[];plan_sha=sha(plan);codes={v.name:sha(v) for v in sorted(HF.glob('*.py'))};code_sha=hashlib.sha256(json.dumps(codes,sort_keys=True).encode()).hexdigest();canonical=ROOT/'workflow/render-heartbeat.json'
chunks=a.chunks or (freeze['allowedChunks'] if a.freeze else list(range(20)))
groups=[None] if a.encode_only else [chunks[i::a.parallel] for i in range(a.parallel)]
state={'state':'running','heartbeatUnix':time.time(),'loop':a.loop,'chunk':None,'framesCaptured':0,'planSha':plan_sha,'codeSha':code_sha,'executor':'/root/s1_render_execution','batch':token,'workers':[]}
def progress_counts():
 # Cache presence is deliberately separate from proofs bound to this immutable plan.
 fresh=[];reused=[]
 for chunk in range(20):
  proof=work/f'chunk-{chunk:02}'/'render-proof.json'
  if not proof.exists():continue
  try:r=json.loads(proof.read_text(encoding='utf-8'))
  except (ValueError,OSError):continue
  if r.get('planSha256')==plan_sha and r.get('codeSha256')==code_sha:fresh.append(chunk)
  elif r.get('currentValidationPlanSha256')==plan_sha and r.get('reuseHistory'):reused.append(chunk)
 return {'cacheFramesPresent':len(list((work/'master-frames').glob('frame_*.png'))),'newlyCapturedFrames':len(fresh)*72,'reusedValidatedFrames':len(reused)*72,'currentVersionProofFrames':(len(fresh)+len(reused))*72,'freshProofChunks':fresh,'reusedProofChunks':reused,'framesCapturedMeaning':'Legacy cache file count; may contain earlier versions. It is not current-version completion. CurrentVersionProofFrames is plan-bound proof count; encode-only additionally rechecks every payload/output byte and current render key.'}
last_key=None;last_progress=time.time()
for chunk in (list(range(20)) if a.encode_only else chunks):
 old=work/f'chunk-{chunk:02}'/'render-proof.json'
 if old.exists():
  prior=logs/'prior-proofs';prior.mkdir(exist_ok=True);shutil.copy2(old,prior/f'chunk-{chunk:02}.json')
try:
 for i,group in enumerate(groups):
  if group==[]:continue
  hb=logs/f'worker-{i}-heartbeat.json';log=logs/f'worker-{i}.log';handle=log.open('wb');handles.append(handle)
  command=[sys.executable,'-X','utf8',str(HF/'render.py'),'--loop',str(a.loop),'--plan',str(plan),'--work',str(work),'--heartbeat',str(hb)]
  if a.encode_only:command+=['--encode-only']
  elif group is not None:command+=['--chunks',*[str(x) for x in group]]
  proc=subprocess.Popen(command,stdout=handle,stderr=subprocess.STDOUT);jobs.append((proc,hb,log,command))
 while True:
  workers=[]
  for proc,hb,log,command in jobs:
   r=json.loads(hb.read_text(encoding='utf-8')) if hb.exists() else {'state':'starting','pid':proc.pid}
   if r.get('encodeOutputPath'):
    output=Path(r['encodeOutputPath'])
    if output.exists():
     stat=output.stat();r.update(encodedBytes=stat.st_size,encodedMtimeNs=stat.st_mtime_ns)
   r.update(exitCode=proc.poll(),log=str(log),command=command);workers.append(r)
  counts=progress_counts();state.update(heartbeatUnix=time.time(),framesCaptured=counts['cacheFramesPresent'],workers=workers,chunk=[r.get('chunk') for r in workers],phase=[r.get('phase') for r in workers],encodingOutputs=[{'path':r['encodeOutputPath'],'bytes':r.get('encodedBytes',0),'mtimeNs':r.get('encodedMtimeNs',0)} for r in workers if r.get('encodeOutputPath')],**counts)
  key=json.dumps([state['currentVersionProofFrames'],[(r.get('phase'),r.get('chunk'),r.get('framesCapturedInCurrentChunk'),r.get('encodedBytes'),r.get('encodedMtimeNs'),r.get('exitCode')) for r in workers]])
  if key!=last_key:last_progress=time.time();last_key=key
  state.update(lastProgressUnix=last_progress,progressStaleSeconds=time.time()-last_progress,stalled=time.time()-last_progress>180)
  failed=[r for r in workers if r['exitCode'] not in [None,0]]
  if failed:raise RuntimeError('render worker failed: '+str([(r['exitCode'],r['log']) for r in failed]))
  save(canonical,state)
  if all(r['exitCode']==0 for r in workers):break
  time.sleep(5)
 assert sha(plan)==plan_sha,'plan changed during batch'
 assert {v.name:sha(v) for v in sorted(HF.glob('*.py'))}==codes,'code changed during batch'
 state.update(state='complete',heartbeatUnix=time.time());save(canonical,state);save(logs/'batch-result.json',state);print(json.dumps({'state':'complete','loop':a.loop,'framesCaptured':state['framesCaptured'],'logs':str(logs),'planSha':plan_sha},ensure_ascii=False))
 if a.encode_only:
  loop=ROOT/'loops'/f'loop-{a.loop:02}';proofs=loop/'render-proofs';proofs.mkdir(exist_ok=True)
  for chunk in range(20):shutil.copy2(work/f'chunk-{chunk:02}'/'render-proof.json',proofs/f'chunk-{chunk:02}.json')
  code=loop/'frozen-source';code.mkdir(exist_ok=True)
  for file in HF.glob('*.py'):shutil.copy2(file,code/file.name)
  for name in ['barlow-glyphs.json','DESIGN.md','hyperframes.json']:shutil.copy2(HF/name,code/name)
except BaseException as e:
 for proc,*_ in jobs:
  if proc.poll() is None:proc.terminate()
 state.update(state='failed',error=str(e),heartbeatUnix=time.time());save(canonical,state);save(logs/'batch-result.json',state);raise
finally:
 for f in handles:f.close()
