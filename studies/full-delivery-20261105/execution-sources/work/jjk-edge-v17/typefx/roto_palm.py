from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from roto_fg import ROOT,ASSET,EV,cv2,np,mod,load_frames,save_png
P=[(510,108),(642,108),(680,249),(706,363),(744,466),(775,518),(806,532),(865,530),(939,498),(1029,449),(1095,401),(1141,328),(1199,266),(1239,241),(1279,240),(1308,268),(1324,311),(1321,355),(1307,397),(1282,443),(1253,482),(1214,520),(1175,542),(1131,568),(1090,599),(1058,631),(1045,667),(1041,691),(1083,719),(1135,749),(1177,775),(1198,812),(1214,866),(1252,912),(1333,972),(1111,972),(1087,921),(1058,871),(1019,853),(968,850),(917,851),(874,850),(830,855),(790,879),(746,897),(700,892),(654,882),(613,879),(574,873),(558,897),(545,940),(539,972),(465,972),(472,917),(479,865),(503,825),(528,785),(551,750),(520,758),(474,767),(423,773),(373,774),(331,766),(287,752),(249,731),(213,695),(186,661),(170,627),(164,600),(172,573),(199,552),(235,555),(303,583),(397,609),(511,616),(614,610),(666,590),(646,555),(611,499),(596,438),(566,390),(541,349),(526,296),(516,233)]
frames=load_frames('X-palm');out=ASSET/'alpha/X-palm';out.mkdir(parents=True,exist_ok=True)
prev=None;counts=[];tracking=[];samples=[]
for f,im in enumerate(frames):
 p=np.array(P,dtype=np.float64);detail={'mode':'manual-anchor' if f==12 else 'manual-hold'}
 mask=np.zeros(im.shape[:2],np.uint8)
 if 12<=f<48:
  if prev is not None:
   q,detail=mod.lk_predict(frames[f-1],im,prev)
   if q is not None and np.mean(np.linalg.norm(q-p,axis=1))<16:p=.8*q+.2*p
  mask=mod.polygon_mask(p,im.shape);mask=mod.refine_grabcut(im,mask,7);mask=cv2.GaussianBlur(mask,(0,0),.65);mask[:108]=0;mask[972:]=0;prev=p
 rgba=cv2.cvtColor(im,cv2.COLOR_BGR2BGRA);rgba[:,:,3]=mask;save_png(out/f'{f:06}.png',rgba);counts.append(int((mask>127).sum()));tracking.append(detail)
 if f in [12,16,20,21,24,36,47]:
  y,x=np.indices(mask.shape);checker=np.repeat(np.where(((x//24+y//24)%2)[...,None],155,85),3,axis=2);a=mask[:,:,None]/255.;comp=(im*a+checker*(1-a)).astype(np.uint8)
  row=np.concatenate([cv2.resize(im,(640,360)),cv2.resize(comp,(640,360))],axis=1);cv2.putText(row,f'X-palm fileF{f} / alpha{f:06}',(8,25),cv2.FONT_HERSHEY_SIMPLEX,.65,(255,255,255),1);samples.append(row)
 if f%6==0:print('X-palm',f,'/',len(frames),flush=True)
save_png(EV/'X-palm-alpha-summary.png',np.concatenate(samples,axis=0))
report=dict(id='X-palm',fps=24,frames=len(frames),formalFirst=12,formalLastExclusive=48,sourceIn=1259.5,clipSourceIn=1259.,alphaIndexOffset=0,formalAlphaRange=[12,48],sourceTimes=[1259+f/24 for f in range(len(frames))],method='manual palm-only silhouette + constrained LK + 7px narrow-band GrabCut',manualPolygonF12=P,tracking=tracking,alphaPixels=counts,noGeneratedRGB=True,rgbSource='same frame of prepared 1920x1080 clip',emptyAlphaFrames=list(range(12))+list(range(48,60)),limitation='Only near palm retained; Gojo torso/head and girl intentionally excluded; hand meets top/bottom crop; native cut in preroll and blur in postroll not used.')
(EV/'X-palm-alpha-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('DONE X-palm 60 PNG, formal12..47',flush=True)
