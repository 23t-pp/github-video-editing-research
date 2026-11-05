"""Constrained color/contour correction for all formal palm frames. RGB unchanged."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from roto_fg import ROOT,ASSET,EV,cv2,np,save_png
out=ASSET/'alpha/X-palm';records=[];summary=[];detail=[]
for f in range(12,48):
 p=out/f'{f:06}.png';im=cv2.imread(str(p),cv2.IMREAD_UNCHANGED);old=im[:,:,3].copy()
 b,g,r=[im[:,:,i].astype(np.int16) for i in range(3)]
 # The whole near palm is warm (including warm gray shadows). Blue sky,
 # cool white roof and navy torso fail both red-dominance tests.
 warm=(r>b+22)&(r>g+15)
 inside=(old>16)&warm
 # Manual local exterior anchor under the near diagonal finger. It removes
 # the small distant hand attached to that contour, across the reviewed
 # 1.5s source window. The palm's actual thick finger stays above this line.
 yy,xx=np.indices(old.shape)
 exterior=(xx>1080)&(xx<1200)&(yy>530)&(yy<635)&(yy>1294-.65*xx)
 inside[exterior]=False
 n,labels,stats,centroids=cv2.connectedComponentsWithStats(inside.astype(np.uint8),8)
 largest=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);component=(labels==largest).astype(np.uint8)*255
 contours,_=cv2.findContours(component,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
 solid=np.zeros_like(component);cv2.drawContours(solid,contours,-1,255,-1)
 # Fill dark line-art holes inside the palm; finger gaps stay connected to
 # exterior, so they remain transparent. No spatial extension into new RGB.
 new=cv2.GaussianBlur(solid,(0,0),.45);new=np.minimum(old,new)
 im[:,:,3]=new;save_png(p,im)
 records.append(dict(frame=f,beforeArea=int((old>127).sum()),afterArea=int((new>127).sum()),removedOpaque=int(((old>127)&(new<16)).sum()),coolOpaquePixelsRemaining=int(((new>127)&(b>r)&(r<190)).sum())))
 yy,xx=np.indices(new.shape);checker=np.repeat(np.where(((xx//24+yy//24)%2)[...,None],155,85),3,axis=2)
 a=new[:,:,None]/255.;comp=(im[:,:,:3]*a+checker*(1-a)).astype(np.uint8)
 # Every formal frame gets a readable close-up of the offending edge/gap.
 crop=comp[215:665,770:1370];before=(im[:,:,:3]*(old[:,:,None]/255.)+checker*(1-old[:,:,None]/255.)).astype(np.uint8)[215:665,770:1370]
 row=np.concatenate([cv2.resize(before,(300,225)),cv2.resize(crop,(300,225))],axis=1)
 cv2.putText(row,f'F{f} before / after',(8,20),cv2.FONT_HERSHEY_SIMPLEX,.5,(255,255,255),1);detail.append(row)
 if f in [12,16,18,20,21,24,36,47]:
  row=np.concatenate([cv2.resize(im[:,:,:3],(640,360)),cv2.resize(comp,(640,360))],axis=1);cv2.putText(row,f'X-palm fileF{f} / alpha{f:06} corrected',(8,25),cv2.FONT_HERSHEY_SIMPLEX,.65,(255,255,255),1);summary.append(row)
 if f==18:
  bg=np.zeros_like(im[:,:,:3]);bg[:]=[15,15,180];red=(im[:,:,:3]*a+bg*(1-a)).astype(np.uint8);save_png(EV/'X-palm-F18-red-corrected.png',red)
for pg in range(3):
 canvas=np.zeros((1350,1200,3),np.uint8)
 for j,row in enumerate(detail[pg*12:(pg+1)*12]):canvas[j//2*225:(j//2+1)*225,j%2*600:(j%2+1)*600]=row
 save_png(EV/f'X-palm-gap-correction-{pg+1:02}.png',canvas)
save_png(EV/'X-palm-alpha-summary.png',np.concatenate(summary,axis=0))
(EV/'X-palm-color-correction.json').write_text(json.dumps(dict(method='warm-domain constrained largest palm contour, internal line-art holes filled; alpha only',formalFrames=[12,48],records=records),ensure_ascii=False,indent=2),encoding='utf-8')
print('Corrected 36 formal palm frames; cool opaque remaining:',sum(r['coolOpaquePixelsRemaining'] for r in records),flush=True)
