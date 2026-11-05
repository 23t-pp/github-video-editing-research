from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,sys,collections,hashlib
BASE=Path(__file__).resolve().parents[2];ROOT=BASE/'outputs/jjk-edge-v17-v3-dedup';HF=ROOT/'hyperframes'
sys.path.insert(0,str(BASE/'work/reference-replay-v07/python-deps'))
import numpy as np,cv2
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
p=json.loads((HF/'edit.json').read_text(encoding='utf8'));assets={a['id']:a for a in p['assets']}
physical=[]
for s in p['shots']:
 a=assets[s['assetId']];src=a.get('sourcePath')
 if not src and a['id'] in ['X-awaken','X-palm']:src='D:/咒术回战/4K 内嵌简中字幕/'+('04.mp4' if a['id']=='X-awaken' else '02.mp4')
 if not src:continue
 start=a.get('preparedSourceStart',a['sourceIn']-.5)+s['assetStartFrame']/24
 physical.append({'id':s['id'],'assetId':a['id'],'sourcePath':src.replace('\\','/'),'sourceStartSeconds':round(start,6),'sourceEndExclusiveSeconds':round(start+s['frames']/24,6)})
overlaps=[]
for i,a in enumerate(physical):
 for b in physical[i+1:]:
  length=min(a['sourceEndExclusiveSeconds'],b['sourceEndExclusiveSeconds'])-max(a['sourceStartSeconds'],b['sourceStartSeconds'])
  if a['sourcePath']==b['sourcePath'] and length>.05:overlaps.append({'a':a['id'],'b':b['id'],'seconds':length})
assert not overlaps,overlaps
def sample(s):
 a=assets[s['assetId']];points=sorted({s['assetStartFrame']+int(s['frames']*t) for t in [.15,.5,.85]})
 filt='+'.join(f'eq(n,{f})' for f in points)
 cmd=[FF,'-v','error','-threads','1','-filter_threads','1','-i',str(HF/a['asset']),'-vf',f"select='{filt}',crop=1920:864:0:108,scale=64:32,format=gray",'-fps_mode','passthrough','-f','rawvideo','pipe:1']
 r=subprocess.run(cmd,capture_output=True,check=True);images=np.frombuffer(r.stdout,np.uint8).reshape(-1,32,64)
 out=[]
 for im in images:
  d=cv2.dct(cv2.resize(im,(32,32)).astype(np.float32))[:8,:8].reshape(-1)[1:];bits=d>np.median(d);out.append((im,bits))
 return s,out
with ThreadPoolExecutor(max_workers=2) as ex:rows=list(ex.map(sample,[s for s in p['shots'] if s['assetId']!='BLACK']))
near=[]
for i,(a,aa) in enumerate(rows):
 for b,bb in rows[i+1:]:
  best=min((int(np.count_nonzero(x[1]!=y[1])),float(np.mean(np.abs(x[0].astype(float)-y[0].astype(float))))) for x in aa for y in bb)
  if best[0]<=6:near.append({'a':a['id'],'b':b['id'],'phashHamming':best[0],'grayMAE':round(best[1],3)})
report={'physicalSourceRanges':physical,'nativeSourceIntervalOverlaps':overlaps,'similarityCandidates':near,'similarityScope':'每个主镜头15/50/85%三帧、64x32灰度及63位pHash；只能筛疑似相似，不代表语义全自动识别。动画原片内部重复和相似姿势需人工复看。','nativeUniqueAssetIds':len({s['assetId'] for s in p['shots']}),'nativeShots':len(p['shots']),'alphaUnique':len({e['alpha'] for e in p['foregrounds']}),'audioMasterMatchesV2':hashlib.sha256((HF/'assets/audio/master.wav').read_bytes()).digest()==hashlib.sha256((BASE/'outputs/jjk-edge-v17-v2/hyperframes/assets/audio/master.wav').read_bytes()).digest()}
(ROOT/'evidence/源片区间与画面相似筛查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:report[k] for k in ['nativeSourceIntervalOverlaps','similarityCandidates','nativeUniqueAssetIds','nativeShots','alphaUnique','audioMasterMatchesV2']},ensure_ascii=False))
