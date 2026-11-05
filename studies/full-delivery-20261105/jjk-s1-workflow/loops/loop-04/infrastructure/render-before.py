"""Actual HyperFrames CLI capture in bounded chunks; loop artifacts stay separate."""
from pathlib import Path
import argparse,json,subprocess,os,sys,shutil,struct,hashlib,time,threading
ROOT=Path(__file__).resolve().parent;R=ROOT.parent;sys.path.insert(0,str(ROOT))
from composition import build,load_edit,save_editable
FF=os.environ.get('FFMPEG_PATH','C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe');FP=os.environ.get('FFPROBE_PATH','C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe')
NODE=os.environ.get('JJK_NODE','C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe');CLI=os.environ.get('HYPERFRAMES_CLI','C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/bin/hyperframes.mjs')
ENV={**os.environ,'HYPERFRAMES_BROWSER_PATH':os.environ.get('HYPERFRAMES_BROWSER_PATH','C:/Program Files/Google/Chrome/Application/chrome.exe'),'HYPERFRAMES_FFMPEG_PATH':FF,'HYPERFRAMES_FFPROBE_PATH':FP}
VOPTS=['-c:v','libx264','-threads','1','-preset','fast','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-bf','0']
CAPTURE_FLAGS=['--format','png-sequence','--workers','1','--low-memory-mode','--sdr','--experimental-fast-capture=false','--no-best-effort','--frames-cache-dir','off']
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write_json(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+f'.{os.getpid()}.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(path)
def runtime_fingerprint():
 chrome=Path(ENV['HYPERFRAMES_BROWSER_PATH']);cli=Path(CLI)
 version=subprocess.check_output(['powershell','-NoProfile','-Command',f"(Get-Item -LiteralPath '{str(chrome).replace(chr(39),chr(39)*2)}').VersionInfo.ProductVersion"],text=True).strip()
 return {'nodeVersion':subprocess.check_output([NODE,'--version'],text=True).strip(),'cliVersion':json.loads((cli.parent.parent/'package.json').read_text(encoding='utf-8'))['version'],'cliEntrySha256':sha(cli),'chromeVersion':version,'chromeExeSha256':sha(chrome),'ffmpegExeSha256':sha(FF),'captureFlags':CAPTURE_FLAGS,'fps':24,'size':[1920,1080],'color':'SDR PNG RGB full; encode BT709 tv','sourceExtraction':'trim source frame indices; scale bt709 tv to full; rgb24; native PNG; passthrough fps'}
def make_chunk(plan,first,last,runtime):
 assets={v['id']:v for v in plan['assets']};html,needed,copies=build(plan,first,last,True)
 deps=[ROOT/n for n in ['composition.py','typefx.py','barlow-glyphs.json','layoutfx.py','screenfx.py','render.py','assets/gsap.min.js']]+[ROOT/assets[v]['asset'] for v in sorted({v for v,n in needed})]+[ROOT/v for v in sorted(copies)]+sorted((ROOT/'assets/fonts').glob('*'))
 hashes={v.relative_to(ROOT).as_posix():sha(v) for v in deps};spec={'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'dependencies':hashes,'runtime':runtime,'neededSourceFrames':sorted([list(x) for x in needed]),'copiedAlpha':sorted(copies)}
 key=hashlib.sha256(json.dumps(spec,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 return html,needed,copies,key,spec
def cache_valid(folder,key,result,first,last,movie):
 proof=folder/'render-proof.json'
 if not proof.exists() or not movie.exists():return False
 saved=json.loads(proof.read_text(encoding='utf-8'))
 if saved['renderKey']!=key:return False
 for p,digest in saved['actualRenderPayloadFiles'].items():
  file=folder/p
  if not file.is_file() or sha(file)!=digest:return False
 for name,digest in saved['outputFrameSha256'].items():
  file=result/name
  if not file.is_file() or sha(file)!=digest:return False
 return len(saved['outputFrameSha256'])==last-first and sha(movie)==saved['segmentSha256']
def capture(cmd):
 p=subprocess.run(cmd,capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-3000:])
 return p.stdout
def extract(asset,indices,folder):
 first,last=min(indices),max(indices)+1;assert first>=0 and last<=asset['frames'],(asset['id'],first,last,asset['frames'])
 vf=f'trim=start_frame={first}:end_frame={last},scale=in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24'
 blob=capture([FF,'-v','error','-threads','1','-filter_threads','1','-i',str(ROOT/asset['asset']),'-an','-vf',vf,'-fps_mode','passthrough','-c:v','png','-threads','1','-compression_level','1','-f','image2pipe','pipe:1']);pos=0
 for n in range(first,last):
  assert blob[pos:pos+8]==b'\x89PNG\r\n\x1a\n',(asset['id'],n);end=pos+8
  while end<len(blob):
   size=struct.unpack_from('>I',blob,end)[0];kind=blob[end+4:end+8];end+=size+12
   if kind==b'IEND':break
  if n in indices:(folder/f'{asset["id"]}-{n:04}.png').write_bytes(blob[pos:end])
  pos=end
 assert pos==len(blob)
def encode(frames,start,count,output,fps,audio=None,preview=False):
 cmd=[FF,'-v','error','-threads','1','-filter_threads','1','-framerate',str(fps),'-start_number',str(start),'-i',str(frames/'frame_%06d.png')]
 if audio:cmd+=['-i',str(audio),'-map','0:v:0','-map','1:a:0']
 vf=('scale=960:540:in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p' if preview else 'scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p')
 cmd+=['-vf',vf,'-frames:v',str(count),*VOPTS]
 if audio:cmd+=['-c:a','aac','-b:a','256k','-ar','48000','-t',str(count/fps)]
 else:cmd+=['-an']
 cmd+=['-f','mp4']
 if not audio:cmd+=['-movflags','frag_keyframe+empty_moov+default_base_moof']
 cmd+=['-fd','1','fd:']
 with output.open('wb') as f:subprocess.run(cmd,stdout=f,check=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,default=R/'.render-cache');p.add_argument('--loop',type=int,required=True,choices=[2,3,4]);p.add_argument('--plan',type=Path);p.add_argument('--chunks',type=int,nargs='+');p.add_argument('--encode-only',action='store_true');p.add_argument('--force',action='store_true');p.add_argument('--heartbeat',type=Path);a=p.parse_args()
 plan_path=(a.plan or ROOT/'edit.json').resolve();plan=json.loads(plan_path.read_text(encoding='utf-8'));fps=plan['fps'];duration=plan['durationFrames'];assets={v['id']:v for v in plan['assets']};work=a.work.resolve();work.mkdir(parents=True,exist_ok=True)
 runtime=runtime_fingerprint();plan_sha=sha(plan_path);code_sha=hashlib.sha256(json.dumps({v.name:sha(v) for v in sorted(ROOT.glob('*.py'))},sort_keys=True).encode()).hexdigest()
 result=work/'master-frames';result.mkdir(exist_ok=True);fx=R/'occ-effects';fx.mkdir(exist_ok=True);loop=R/f'loops/loop-{a.loop:02}';loop.mkdir(exist_ok=True)
 progress={'state':'running','heartbeatUnix':time.time(),'loop':a.loop,'chunk':None,'framesCaptured':0,'planSha':plan_sha,'codeSha':code_sha,'executor':'/root/s1_render_execution','pid':os.getpid()};stop=threading.Event()
 def heartbeat():
  while not stop.is_set():
   progress.update(heartbeatUnix=time.time(),framesCaptured=len(list(result.glob('frame_*.png'))))
   if progress.get('captureOutputPath'):progress['framesCapturedInCurrentChunk']=len(list(Path(progress['captureOutputPath']).glob('frame_*.png')))
   if a.heartbeat:write_json(a.heartbeat,progress)
   stop.wait(5)
 ht=threading.Thread(target=heartbeat,daemon=True);ht.start()
 if not a.encode_only:
  for chunk,first in enumerate(range(0,duration,72)):
   if a.chunks is not None and chunk not in a.chunks:continue
   last=min(duration,first+72);html,needed,copies,key,spec=make_chunk(plan,first,last,runtime);progress['chunk']=chunk
   folder=work/f'chunk-{chunk:02}';folder.mkdir(exist_ok=True);cache=folder/'cache-key.txt';movie=fx/f'HF-{first:04}-{last:04}.mp4'
   if not a.force and cache_valid(folder,key,result,first,last,movie):
    print(f'CACHED [{first},{last})',flush=True);continue
   run=1
   while (folder/f'pass-{run}').exists():run+=1
   project=folder/f'pass-{run}';framefolder=project/'assets/frames';framefolder.mkdir(parents=True)
   (project/'index.html').write_text(html,encoding='utf-8')
   for name in ['hyperframes.json','DESIGN.md','assets/gsap.min.js',*copies,*[v.relative_to(ROOT).as_posix() for v in (ROOT/'assets/fonts').glob('*')]]:
    dest=project/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dest)
   for id in sorted({v for v,n in needed}):extract(assets[id],{n for v,n in needed if v==id},framefolder)
   output=folder/f'png-{run}';log=folder/f'hyperframes-{run}.log'
   cmd=[NODE,CLI,'render',str(project),'--fps',str(fps),*CAPTURE_FLAGS,'--output',str(output)]
   print(f'RENDER [{first},{last}) source={len(needed)} alpha={len(copies)}',flush=True)
   progress.update(captureOutputPath=str(output),framesCapturedInCurrentChunk=0)
   with log.open('wb') as f:x=subprocess.run(cmd,env=ENV,stdout=f,stderr=subprocess.STDOUT)
   if x.returncode:raise RuntimeError(log.read_text(encoding='utf-8',errors='replace')[-3500:])
   names=sorted(output.glob('frame_*.png'));assert len(names)==last-first,(chunk,len(names))
   for i,path in enumerate(names):shutil.copy2(path,result/f'frame_{first+i+1:06}.png')
   encode(result,first+1,last-first,movie,fps);cache.write_text(key)
   payload={v.relative_to(folder).as_posix():sha(v) for v in sorted(project.rglob('*')) if v.is_file()};payload_hash=hashlib.sha256(json.dumps({'files':payload,'runtime':runtime},sort_keys=True).encode()).hexdigest()
   write_json(folder/'render-proof.json',{'renderKey':key,'inputSpec':spec,'actualRenderPayloadFiles':payload,'actualPayloadSha256':payload_hash,'outputFrameSha256':{f'frame_{f+1:06}.png':sha(result/f'frame_{f+1:06}.png') for f in range(first,last)},'segmentSha256':sha(movie),'planSha256':plan_sha,'codeSha256':code_sha,'executor':'/root/s1_render_execution','chunk':chunk,'first':first,'last':last})
   assert sha(plan_path)==plan_sha,'frozen plan mutated during capture'
   assert make_chunk(plan,first,last,runtime)[3]==key,'capture dependencies mutated'
   print(f'DONE [{first},{last})',flush=True)
  if not a.plan:save_editable(build(plan)[0])
 if a.chunks is not None:
  progress.update(state='complete',heartbeatUnix=time.time(),framesCaptured=len(list(result.glob('frame_*.png'))));stop.set();ht.join()
  if a.heartbeat:write_json(a.heartbeat,progress)
  return
 for chunk,first in enumerate(range(0,duration,72)):
  last=min(duration,first+72);key=make_chunk(plan,first,last,runtime)[3];assert cache_valid(work/f'chunk-{chunk:02}',key,result,first,last,fx/f'HF-{first:04}-{last:04}.mp4'),('stale or mixed capture',chunk)
 assert all((result/f'frame_{f+1:06}.png').exists() for f in range(duration))
 name={2:'loop-02-composite-preview.mp4',3:'loop-03-high-quality.mp4',4:'loop-04-final.mp4'}[a.loop];final=loop/name
 if final.exists():
  old=hashlib.sha256(final.read_bytes()).hexdigest()[:12];history=loop/'history';history.mkdir(exist_ok=True);shutil.copy2(final,history/f'{final.stem}-{old}.mp4')
 encode(result,1,duration,final,fps,ROOT/plan['audio']['master'],a.loop==2)
 info=json.loads(capture([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(final)]));v=next(s for s in info['streams'] if s['codec_type']=='video');assert int(v['nb_read_frames'])==duration and v['avg_frame_rate']==f'{fps}/1'
 (loop/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
 execution={'executor':'/root/s1_render_execution','loop':a.loop,'video':final.relative_to(R).as_posix(),'sha256':hashlib.sha256(final.read_bytes()).hexdigest(),'frames':duration,'fps':fps,'seconds':duration/fps,'width':v['width'],'height':v['height'],'engine':'actual HyperFrames CLI 0.8.216 screenshot capture,72-frame chunks,exact same prepared source PNG clock','renderWork':str(work),'planPath':str(plan_path),'editSha256':plan_sha,'codeSha256':code_sha,'runtime':runtime,'all20CurrentPayloadProofsVerified':True,'actualListeningPerformed':False,'ffprobe':info}
 (loop/'execution.json').write_text(json.dumps(execution,ensure_ascii=False,indent=2),encoding='utf-8')
 if a.loop==4:shutil.copy2(final,R/'咒力接力_一分钟.mp4')
 progress.update(state='complete',heartbeatUnix=time.time(),framesCaptured=duration);stop.set();ht.join()
 if a.heartbeat:write_json(a.heartbeat,progress)
 print('VERIFIED',a.loop,execution['sha256'],flush=True)
if __name__=='__main__':main()
