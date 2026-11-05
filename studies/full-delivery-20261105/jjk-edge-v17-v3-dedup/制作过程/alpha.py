from pathlib import Path
import sys,json,importlib.util
BASE=Path(__file__).resolve().parents[2];WORK=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'work/reference-replay-v07/python-deps'))
import cv2,numpy as np
cv2.setNumThreads(2)
spec=importlib.util.spec_from_file_location('roto',BASE/'outputs/reference-replay-next/hyperframes/tools/dynamic-alpha.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
HF=BASE/'outputs/jjk-edge-v17-v3-dedup/hyperframes';EV=HF.parent/'evidence/alpha';EV.mkdir(parents=True,exist_ok=True)
# Visible actor silhouettes annotated in 384x216 prepared-media coordinates.
# Points follow the same anatomical contour order across each temporal anchor.
S={
'N34':[(81,194),(116,181),(152,170),(158,147),(156,131),(151,115),(155,110),(156,97),(161,83),(166,67),(178,58),(180,51),(187,49),(199,52),(210,65),(215,76),(218,96),(225,105),(224,124),(217,139),(214,147),(219,168),(251,181),(280,194)],
'N35':[(183,194),(186,163),(190,137),(200,122),(203,113),(202,104),(210,99),(215,90),(214,85),(207,81),(207,74),(215,67),(218,56),(222,49),(235,47),(242,43),(251,45),(258,47),(265,44),(268,48),(276,48),(270,55),(278,58),(269,60),(267,70),(259,83),(251,91),(254,106),(268,118),(278,132),(281,153),(279,194)],
'N36':[(71,194),(70,168),(76,152),(88,143),(94,138),(96,127),(95,115),(98,103),(107,98),(118,97),(129,101),(135,112),(138,127),(138,138),(148,147),(160,154),(169,169),(167,194)],
'N37':[(144,194),(151,174),(162,163),(162,154),(170,150),(164,145),(159,136),(157,129),(154,124),(158,116),(155,105),(157,95),(156,83),(162,72),(170,65),(187,62),(199,66),(208,74),(212,90),(213,108),(209,121),(209,135),(218,147),(219,163),(227,180),(245,194)],
'N39':[(44,194),(54,181),(61,165),(66,147),(72,135),(83,120),(98,115),(109,105),(123,101),(134,84),(145,79),(154,75),(163,80),(170,79),(178,70),(185,62),(196,55),(206,55),(205,63),(200,71),(192,80),(185,93),(186,112),(210,124),(240,128),(280,127),(312,121),(346,120),(375,114),(384,117),(384,135),(360,141),(326,150),(290,158),(250,167),(228,180),(215,194)],
}
G33a=[(148,194),(151,150),(142,138),(136,118),(140,92),(157,76),(166,71),(164,58),(162,47),(166,42),(165,35),(173,37),(174,27),(180,30),(185,23),(189,32),(196,29),(197,37),(203,38),(198,46),(202,49),(196,60),(194,69),(191,74),(203,80),(208,106),(216,132),(207,138),(198,118),(198,194)]
G33b=[(127,194),(135,156),(119,147),(116,126),(127,105),(153,85),(164,75),(161,60),(155,48),(157,40),(153,31),(163,34),(168,22),(175,27),(181,22),(189,24),(198,23),(202,31),(213,32),(206,44),(212,47),(205,60),(203,77),(194,85),(207,91),(217,121),(229,158),(221,174),(209,142),(208,194)]
G33c=[(111,194),(119,162),(115,137),(126,116),(142,116),(157,118),(162,105),(158,88),(155,73),(157,60),(150,55),(159,49),(153,40),(165,41),(167,30),(174,35),(181,23),(186,28),(199,25),(201,33),(214,30),(211,40),(220,43),(212,52),(216,62),(207,73),(203,93),(215,105),(224,138),(252,171),(248,185),(229,175),(221,158),(222,194)]
# Dynamic N33 uses torso anchors; resampling gives corresponding contour lengths.
def resample(poly,n=64):
 p=np.asarray(poly,float);q=np.roll(p,-1,axis=0);length=np.linalg.norm(q-p,axis=1);cum=np.r_[0,np.cumsum(length)];t=np.linspace(0,cum[-1],n,endpoint=False);out=[]
 for v in t:
  i=min(np.searchsorted(cum,v,side='right')-1,len(p)-1);out.append(p[i]+(q[i]-p[i])*((v-cum[i])/length[i]))
 return np.asarray(out)
S['N33']=[(12,resample(G33a)),(27,resample(G33b)),(59,resample(G33c))]
HEAD21=[(55,22),(82,28),(104,24),(129,22),(150,22),(178,22),(202,22),(222,28),(245,24),(265,31),(285,24),(284,37),(299,40),(291,50),(300,59),(287,65),(297,75),(282,78),(275,95),(268,108),(261,122),(247,138),(241,154),(224,172),(211,190),(208,194),(102,194),(92,178),(84,165),(82,145),(76,129),(71,107),(64,91),(48,82),(59,77),(45,67),(63,62),(49,52),(67,47)]
S['N21']=HEAD21
S['N40']=[(0,22),(46,22),(87,22),(131,22),(166,22),(197,22),(220,25),(228,39),(244,46),(253,52),(270,57),(259,62),(263,75),(274,82),(282,94),(297,103),(286,111),(269,113),(267,122),(255,126),(266,137),(255,146),(244,153),(239,166),(228,180),(217,194),(0,194)]
S['N38']=[(95,194),(104,164),(126,147),(149,140),(159,132),(160,117),(157,105),(155,94),(156,83),(150,78),(155,65),(147,59),(158,56),(151,47),(166,43),(162,35),(175,33),(180,22),(187,28),(199,22),(209,31),(223,28),(222,39),(235,42),(227,53),(237,57),(227,66),(229,79),(221,90),(218,108),(212,126),(216,141),(232,145),(243,145),(244,128),(240,115),(249,103),(254,93),(263,92),(270,101),(284,105),(290,118),(286,133),(275,144),(282,163),(295,181),(309,194)]
def save(path,im):
 ok,b=cv2.imencode('.png',im);assert ok;path.write_bytes(b.tobytes())
def main(job):
 id=job['id'];asset=job['assetId'];cap=cv2.VideoCapture(str(HF/'assets/shots'/f'{asset}.mp4'));frames=[]
 if (EV/f'{id}.json').exists():
  cap.release();print('ALPHA CACHED',id,flush=True);return
 while True:
  ok,im=cap.read()
  if not ok:break
  frames.append(im)
 cap.release();first,last=job['first'],job['last'];assert len(frames)>=last
 source=S[asset]
 keys=source if asset=='N33' else [(first,np.asarray(source,float)),(last-1,np.asarray(source,float))]
 keys=[(f,np.asarray(p)*5) for f,p in keys];out=HF/'assets/alpha'/id;out.mkdir(parents=True,exist_ok=True);rows=[];prev=None;report=[]
 yy,xx=np.indices((1080,1920));checker=np.repeat(np.where(((xx//28+yy//28)%2)[...,None],150,85),3,axis=2).astype(np.uint8)
 for f in range(first,last):
  im=frames[f];left=max((k for k in keys if k[0]<=f),key=lambda k:k[0]);right=min((k for k in keys if k[0]>=f),key=lambda k:k[0]);t=0 if left is right else (f-left[0])/(right[0]-left[0]);p=(1-t)*left[1]+t*right[1]
  if prev is not None and f not in [k[0] for k in keys]:
   prediction,tr=r.lk_predict(frames[f-1],im,prev)
   if prediction is not None and np.mean(np.linalg.norm(prediction-p,axis=1))<36:p=.65*prediction+.35*p
  # Infer only alpha at half size; retain exact 1920x1080 source RGB.
  small=cv2.resize(im,(960,540),interpolation=cv2.INTER_AREA)
  mask=r.polygon_mask(p/2,small.shape);mask=r.refine_grabcut(small,mask,7 if asset!='N33' else 11)
  mask=cv2.resize(mask,(1920,1080),interpolation=cv2.INTER_LINEAR);mask=cv2.GaussianBlur(mask,(0,0),.7);mask[:108]=0;mask[972:]=0
  rgba=cv2.cvtColor(im,cv2.COLOR_BGR2BGRA);rgba[:,:,3]=mask;save(out/f'{f:06}.png',rgba)
  assert np.array_equal(rgba[:,:,:3],im)
  ys,xs=np.where(mask>127);report.append({'fileFrame':f,'pixels':len(xs),'bounds':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]})
  if f in {first,(first+last)//2,last-1}:
   a=mask[:,:,None]/255;red=np.full_like(im,(40,40,200));row=np.concatenate([cv2.resize(im,(480,270)),cv2.resize((im*a+checker*(1-a)).astype(np.uint8),(480,270)),cv2.resize((im*a+red*(1-a)).astype(np.uint8),(480,270))],axis=1)
   cv2.putText(row,f'{id} {asset} F{f}',(8,22),cv2.FONT_HERSHEY_SIMPLEX,.65,(20,240,255),1);rows.append(row)
  prev=p
 save(EV/f'{id}-源帧与透明核对.png',np.concatenate(rows,axis=0))
 (EV/f'{id}.json').write_text(json.dumps({'id':id,'assetId':asset,'first':first,'endExclusive':last,'frames':last-first,'method':'manual silhouette anchors + constrained LK + narrow-band GrabCut; 0.7px feather; visible crop only','rgbExactPreparedFrame':True,'sourceNativeFps':'24000/1001','preparedFps':24,'noGeneratedRGB':True,'limitations':'人工轮廓近似，细发丝和制服边可能有窄边残留；不恢复原片裁切以外的人体。','samples':report},ensure_ascii=False,indent=2),encoding='utf8')
 print('ALPHA',id,last-first,flush=True)
if __name__=='__main__':
 jobs=json.loads((WORK/'foreground-jobs.json').read_text(encoding='utf8'))
 for j in jobs:main(j)
