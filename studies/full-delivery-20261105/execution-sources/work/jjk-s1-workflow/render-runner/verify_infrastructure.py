"""Fault-inject atomic writes without invoking capture, cache rebind or encode."""
from pathlib import Path
import importlib.util,json,hashlib,difflib,time
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[3];ROOT=BASE/'outputs/jjk-s1-workflow';HF=ROOT/'hyperframes';DEST=ROOT/'loops/loop-04/infrastructure';DEST.mkdir(exist_ok=True,parents=True)
spec=importlib.util.spec_from_file_location('s1_render',HF/'render.py');render=importlib.util.module_from_spec(spec);spec.loader.exec_module(render)
original=Path.replace;calls=[];target=DEST/'atomic-retry-success.json'
def transient(self,dest):
 calls.append(1)
 if len(calls)<3:raise PermissionError(13,'injected Windows sharing-lock failure')
 return original(self,dest)
with patch.object(Path,'replace',transient),patch.object(render.time,'sleep',lambda _:None):render.write_json(target,{'state':'test_success_after_two_transient_failures'})
assert len(calls)==3 and json.loads(target.read_text(encoding='utf-8'))['state'].startswith('test_success')
failed_calls=[]
def persistent(self,dest):failed_calls.append(1);raise PermissionError(13,'injected persistent sharing lock')
caught=False
with patch.object(Path,'replace',persistent),patch.object(render.time,'sleep',lambda _:None):
 try:render.write_json(target,{'state':'must_not_replace_existing_json'})
 except PermissionError:caught=True
assert caught and len(failed_calls)==6 and json.loads(target.read_text(encoding='utf-8'))['state'].startswith('test_success')
assert render.loop_number('5')==5 and render.loop_video_name(5)=='loop-05-high-quality.mp4'
invalid=False
try:render.loop_number('1')
except Exception:invalid=True
assert invalid
changes={};diffs=[]
for old,new in [(DEST/'render-before.py',HF/'render.py'),(DEST/'run_batch-before.py',BASE/'work/jjk-s1-workflow/render-runner/run_batch.py')]:
 old_text=old.read_text(encoding='utf-8');new_text=new.read_text(encoding='utf-8');changes[new.name]={'oldSha256':hashlib.sha256(old.read_bytes()).hexdigest(),'newSha256':hashlib.sha256(new.read_bytes()).hexdigest()};diffs.extend(difflib.unified_diff(old_text.splitlines(True),new_text.splitlines(True),fromfile=old.name,tofile=new.name))
(DEST/'operation-stability.diff').write_text(''.join(diffs),encoding='utf-8')
report={'state':'pass_operation_stability_only','executor':'/root/s1_render_execution','createdUnix':time.time(),'changedFiles':changes,'checks':{'pythonCompile':True,'atomicSuccessAfterTransientFailures':len(calls),'atomicPersistentFailureRaisesAfterAttempts':len(failed_calls),'existingTargetPreservedOnFailure':True,'loop5Accepted':True,'loopBelow2Rejected':True,'captureStarted':False,'cacheModified':False,'producerRebindStarted':False},'delta':['Atomic JSON replacement retries PermissionError at most 6 attempts with bounded backoff and logs; persistent heartbeat failure propagates to nonzero renderer exit.','Heartbeat phase plus real encoded bytes/mtime propagated to coordinator progress; PNG cache count no longer masquerades as encode progress.','Loop numbers >=2 accepted; loop5+ uses loop-NN-high-quality.mp4.','Loop4 no longer copies canonical root film. Publication is root-only after independent pass.'],'imagePayloadChange':'None intended: capture flags, extraction, encode arguments, composition, assets, HTML and runtime fingerprint are unchanged. Actual byte closure must still be proved against final R4 plan before reuse.'}
(DEST/'operation-stability-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
