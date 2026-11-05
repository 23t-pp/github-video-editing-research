from pathlib import Path
import sys,json,importlib.util
sys.path.insert(0,'D:/gpt/2026-11-04/ps-c-windows-system32-winget-install-2/work/reference-replay-v07/python-deps')
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
ASSET=ROOT/'outputs/jjk-edge-v17/hyperframes/assets'
EV=ROOT/'outputs/jjk-edge-v17/evidence/alpha';EV.mkdir(parents=True,exist_ok=True)
cv2.setNumThreads(2)
spec=importlib.util.spec_from_file_location('previous_roto',ROOT/'outputs/reference-replay-next/hyperframes/tools/dynamic-alpha.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
# F12 observed outline: hair spikes, fingers, jacket, legs. No surrounding
# golden beams or rubble are part of this manual anchor.
AWAKEN=[(958,252),(961,269),(976,255),(975,275),(986,259),(989,275),(1008,274),(995,290),(1010,291),(1000,302),(1016,317),(997,316),(1005,329),(989,324),(987,345),(980,354),(990,365),(1047,378),(1060,391),(1090,410),(1130,426),(1218,452),(1224,463),
 (1242,458),(1250,448),(1254,449),(1251,463),(1261,469),(1283,474),(1286,478),(1281,481),(1260,479),(1279,491),(1283,497),(1277,499),(1255,487),(1269,506),(1271,513),(1264,513),(1250,496),(1258,516),(1252,518),(1241,500),(1225,491),(1215,484),
 (1206,489),(1108,460),(1062,445),(1072,479),(1090,510),(1099,530),(1094,544),(1075,551),(1034,556),(1030,579),(1029,595),(1045,685),(1060,756),(1090,827),(1108,919),(1117,948),(1111,963),(1119,972),(1073,972),(1066,947),(1061,921),(1031,855),(1017,801),(992,740),(959,632),(930,698),(913,753),(893,800),(872,861),(849,927),(846,954),(836,972),(799,972),(798,952),(810,904),(833,831),(848,781),(859,730),(870,665),(891,592),(879,581),(882,558),
 (859,552),(840,542),(819,527),(821,519),(845,501),(858,468),(873,446),(789,465),(707,490),(700,482),(690,494),(678,503),(670,516),(664,518),(664,513),(669,498),(652,513),(646,512),(647,506),(662,490),(644,502),(638,501),(640,496),(658,484),(640,485),(635,481),(637,477),(660,473),(673,463),(669,458),(665,451),(667,447),(672,449),(680,460),(696,466),(698,452),(755,437),(791,429),(807,421),(833,411),(846,401),(858,398),(868,384),(880,385),(885,376),(929,365),(936,351),(929,339),(923,325),(912,334),(917,316),(905,321),(915,305),(902,308),(914,294),(904,294),(921,280),(910,275),(938,278),(934,266),(947,276),(950,250)]

def load_frames(name):
 cap=cv2.VideoCapture(str(ASSET/'shots'/f'{name}.mp4'));ims=[]
 while True:
  ok,im=cap.read()
  if not ok:break
  ims.append(im)
 cap.release();return ims

def save_png(path,im):
 ok,b=cv2.imencode('.png',im);assert ok;path.write_bytes(b.tobytes())

def make(name):
 frames=load_frames(name);out=ASSET/'alpha'/name;out.mkdir(parents=True,exist_ok=True)
 base=np.array(AWAKEN,np.float64)
 anchors=[(0,5),(12,0),(24,8),(36,10),(48,5),(59,0),(71,4)]
 keys=[dict(frame=f,points=(base+[0,y]).tolist()) for f,y in anchors]
 prev_points=None;mask_counts=[];track=[];cells=[]
 for f,im in enumerate(frames):
  le=max((k for k in keys if k['frame']<=f),key=lambda k:k['frame']);ri=min((k for k in keys if k['frame']>=f),key=lambda k:k['frame']);t=0 if le is ri else (f-le['frame'])/(ri['frame']-le['frame'])
  p=(1-t)*np.array(le['points'])+t*np.array(ri['points']);detail={'mode':'manual-anchor' if f in [x[0] for x in anchors] else 'manual-linear'}
  if prev_points is not None and f not in [x[0] for x in anchors]:
   predicted,detail=mod.lk_predict(frames[f-1],im,prev_points)
   if predicted is not None and np.mean(np.linalg.norm(predicted-p,axis=1))<14:p=.65*predicted+.35*p
   else:detail['accepted']=False
  mask=mod.polygon_mask(p,im.shape)
  mask=mod.refine_grabcut(im,mask,8)
  mask=cv2.GaussianBlur(mask,(0,0),.65);mask[:108]=0;mask[972:]=0
  rgba=cv2.cvtColor(im,cv2.COLOR_BGR2BGRA);rgba[:,:,3]=mask;save_png(out/f'{f:06}.png',rgba)
  prev_points=p;mask_counts.append(int((mask>127).sum()));track.append(detail)
  if f%4==0 or f==len(frames)-1:
   # Crop around the actual foreground; checker, source and alpha in each row.
   y,x=np.indices(mask.shape);checker=np.repeat(np.where(((x//24+y//24)%2)[...,None],145,85),3,axis=2)
   a=mask[...,None]/255.;comp=(im*a+checker*(1-a)).astype(np.uint8)
   row=np.concatenate([cv2.resize(im[225:972,610:1310],(300,320)),cv2.resize(comp[225:972,610:1310],(300,320)),cv2.cvtColor(cv2.resize(mask[225:972,610:1310],(300,320)),cv2.COLOR_GRAY2BGR)],axis=1)
   cv2.putText(row,f'{name} fileF{f}  formal={12<=f<60}',(6,20),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,240,255),1);cells.append(row)
  if f%12==0:print(name,f,'/',len(frames),flush=True)
 evidence=np.concatenate(cells,axis=0);save_png(EV/f'{name}-alpha-contact.png',evidence)
 report=dict(id=name,fps=24,frames=len(frames),formalFirst=12,formalLastExclusive=60,sourceIn=989.0,clipSourceIn=988.5,sourceTimes=[988.5+f/24 for f in range(len(frames))],method='manual polygon anchors + constrained LK affine + 8px narrow-band GrabCut',manualKeys=keys,tracking=track,alphaPixels=mask_counts,featherPx=.65,noGeneratedRGB=True,rgbSource='same frame of prepared 1920x1080 clip',activeRect=[0,108,1920,864],limitation='shoe tips cut by requested crop at y972; no reconstruction; hair/fingers can retain 1-3px golden spill')
 (EV/f'{name}-alpha-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print('DONE',name,len(frames),flush=True)

if __name__=='__main__':make('X-awaken')
