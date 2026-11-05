from pathlib import Path
import json,argparse,subprocess,hashlib
from concurrent.futures import ThreadPoolExecutor
R=Path(__file__).resolve().parent.parent;H=R/'hyperframes';FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';FP='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'
ap=argparse.ArgumentParser();ap.add_argument('--only',nargs='*');args=ap.parse_args()
f=json.loads((R/'data/fresh-shot-candidates.json').read_text(encoding='utf-8'));fresh={v['candidateId']:v for v in f['items']};p=json.loads((R/'loops/loop-02/plan-early.json').read_text(encoding='utf-8'));shots={s['id']:s for s in p['shots']}
mapping={'S026':'S1C041','S037':'S1C054','S052':'S1C028','S053':'S1C078','S054':'S1C080','S056':'S1C047','S057':'S1C088','S058':'S1C076'}
designerViewedStable={'S1C041':[179.4,180.6],'S1C076':[1214.4,1215.35],'S1C078':[239.4,240.6],'S1C081':[289.4,290.6],'S1C088':[449.4,450.6],'S1C028':[254.10,255.15],'S1C080':[265.15,266.35]}
original={v['id']:v for v in json.loads((R/'data/shot-candidates.json').read_text(encoding='utf-8'))['items']}
for cid in mapping.values():
 if cid not in fresh:
  t=original[cid];fresh[cid]={'candidateId':cid,'sourceId':t['sourceId'],'sourcePath':t['sourcePath'],'characters':['unknown'] if cid in ['S1C078','S1C088'] else t['characters'],'evidence':'evidence/source-overviews/fresh-candidates/fresh-02.jpg','observedMovement':'紫瞳眼部保持，身份不确认' if cid=='S1C078' else '取回动作，见curator扩查','coreSourceSeconds':designerViewedStable.get(cid)}
jobs=[(sid,cid) for sid,cid in mapping.items() if not args.only or cid in args.only]
logdir=R/'evidence/fresh-retrieval';logdir.mkdir(exist_ok=True)
def one(job):
 sid,cid=job;t=fresh[cid];s=shots[sid];core=t.get('coreSourceSeconds')
 if cid=='S1C028':core=[254.14,255.14]
 if cid=='S1C076':core=[1214.4,1215.35]
 if not core:
  assert cid in designerViewedStable,(cid,'curator core still pending')
  core=designerViewedStable[cid];proofScope='execution designer also viewed all8 library-grid images; final retrieved native frames still need review'
 else:proofScope='curator reviewed core, final retrieved frames need execution review'
 duration=s['frames']/24;available=core[1]-core[0];rate=min(1,available*.92/duration);assert rate>=.65,(cid,available,rate)
 start=core[0]+(available-duration*rate)/2;decodeStart=max(0,start-.5*rate);count=s['frames']+24;span=count/24*rate+.15;name='N'+sid[1:]+('B' if cid=='S1C047' else '');target=H/f'assets/shots/{name}.mp4'
 command=[FF,'-v','info','-threads','1','-filter_threads','1','-ss',f'{decodeStart:.9f}','-t',f'{span:.9f}','-i',t['sourcePath'],'-an','-vf',f'showinfo,setpts=(PTS-STARTPTS)/{rate:.9f},fps=24,crop=1920:960:0:0,pad=1920:1080:0:60:black','-frames:v',str(count),'-c:v','libx264','-threads','1','-preset','fast','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-bf','0','-movflags','frag_keyframe+empty_moov+default_base_moof','-f','mp4','pipe:1']
 key=hashlib.sha256(json.dumps(command,ensure_ascii=False).encode()).hexdigest();marker=target.with_suffix('.key')
 if not(target.exists() and marker.exists() and marker.read_text()==key):
  q=subprocess.run(command,capture_output=True);(logdir/f'{name}.log').write_bytes(q.stderr)
  if q.returncode:raise RuntimeError(q.stderr.decode(errors='replace')[-1500:])
  target.write_bytes(q.stdout)
 info=json.loads(subprocess.run([FP,'-v','error','-count_frames','-show_streams','-of','json',str(target)],capture_output=True,check=True).stdout)['streams'][0];assert int(info['nb_read_frames'])==count
 marker.write_text(key);digest=hashlib.sha256(target.read_bytes()).hexdigest()
 result={'shot':sid,'asset':{'id':name,'asset':f'assets/shots/{name}.mp4','frames':count,'usableFrames':s['frames'],'sha256':digest,'sourcePath':t['sourcePath'],'sourceId':t['sourceId'],'sourceIn':start,'sourceFps':'24000/1001','description':t.get('observedMovement','fresh source')},'candidateId':cid,'sourceId':t['sourceId'],'sourcePath':t['sourcePath'],'sourceInSeconds':start,'sourceOutSeconds':start+duration*rate,'playbackRate':rate,'characters':t.get('characters',['unknown']),'focus':t.get('observedMovement','unknown'),'coreSourceSeconds':core,'proofScope':proofScope,'evidence':t['evidence'],'command':command,'ffprobe':info}
 (logdir/f'{name}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print('FRESH',sid,cid,flush=True);return result
with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(one,jobs))
alljobs=[json.loads(v.read_text(encoding='utf-8')) for v in sorted(logdir.glob('N*.json'))];latest={v['shot']:v for v in alljobs};allresults=list(latest.values())
(R/'data/fresh-prepared-assets.json').write_text(json.dumps({'prepared':len(allresults),'expected':len(mapping),'items':allresults,'oldMediaUnchanged':True,'sourcePolicy':'distinct original S1 source windows, no mirror or recolor counted as new footage'},ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared',len(allresults),'/',len(mapping))
