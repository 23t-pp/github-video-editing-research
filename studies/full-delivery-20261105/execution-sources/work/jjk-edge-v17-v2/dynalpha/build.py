from pathlib import Path
import sys,json,importlib.util
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'work/reference-replay-v07/python-deps'))
import cv2,numpy as np
cv2.setNumThreads(2)
spec=importlib.util.spec_from_file_location('roto',ROOT/'outputs/reference-replay-next/hyperframes/tools/dynamic-alpha.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
OUT=ROOT/'outputs/jjk-edge-v17-v2/hyperframes/assets/alpha';EV=ROOT/'outputs/jjk-edge-v17-v2/evidence/alpha'
GETO=[(594,972),(685,930),(750,883),(750,806),(763,796),(779,789),(776,711),(763,670),(754,691),(737,694),(724,687),(716,671),(716,622),(707,593),(702,564),(704,543),(711,523),(722,516),(734,518),(734,489),(732,465),(736,422),(746,381),(761,348),(781,317),(804,290),(829,272),(854,263),(882,257),(913,250),(909,233),(913,220),(929,208),(947,199),(975,196),(1006,197),(1031,204),(1047,218),(1060,239),(1061,258),(1092,255),(1112,248),(1124,241),(1117,254),(1100,265),(1078,271),(1103,282),(1126,298),(1139,314),(1108,304),(1127,330),(1142,343),(1153,349),(1130,347),(1144,380),(1153,415),(1157,453),(1156,488),(1150,525),(1138,559),(1135,574),(1146,575),(1154,584),(1158,603),(1152,623),(1137,648),(1121,673),(1114,715),(1109,729),(1096,738),(1084,739),(1074,734),(1068,720),(1047,756),(1038,807),(1055,816),(1064,826),(1059,901),(1071,903),(1099,931),(1209,972)]
HURT12=[(322,108),(257,131),(203,141),(153,141),(111,134),(148,155),(204,174),(263,183),(318,183),(359,173),(339,203),(307,240),(265,275),(211,309),(163,331),(112,343),(170,341),(226,330),(279,310),(324,279),(372,231),(349,278),(310,329),(259,380),(206,424),(162,451),(116,472),(172,471),(229,464),(288,450),(340,426),(391,384),(441,335),(407,389),(365,445),(317,497),(270,543),(221,580),(172,603),(226,599),(279,582),(330,555),(372,526),(337,579),(304,620),(272,653),(324,623),(356,594),(383,550),(370,604),(345,653),(299,720),(349,694),(387,663),(441,622),(444,676),(436,744),(459,697),(479,658),(490,698),(501,725),(524,757),(541,771),(554,775),(546,854),(560,800),(575,852),(596,913),(610,972),(1311,972),(1338,905),(1357,835),(1365,908),(1374,829),(1390,753),(1425,737),(1450,699),(1468,658),(1470,748),(1488,812),(1477,727),(1470,666),(1511,695),(1559,720),(1609,730),(1572,691),(1536,646),(1507,597),(1542,626),(1592,655),(1642,675),(1680,676),(1634,633),(1601,595),(1571,551),(1630,578),(1680,586),(1735,589),(1799,588),(1744,563),(1693,528),(1645,486),(1600,439),(1573,425),(1617,444),(1660,462),(1710,477),(1764,486),(1722,460),(1685,431),(1646,395),(1611,354),(1570,322),(1614,357),(1667,394),(1725,424),(1778,445),(1828,455),(1776,422),(1730,386),(1686,345),(1646,300),(1616,261),(1599,228),(1643,251),(1690,267),(1743,275),(1804,271),(1755,249),(1710,224),(1662,193),(1617,164),(1575,149),(1625,156),(1677,156),(1730,145),(1771,130),(1810,113),(1813,108)]
HURT35=[(261,108),(208,125),(160,136),(113,139),(70,135),(129,147),(183,153),(239,153),(298,141),(344,120),(327,154),(301,193),(270,230),(228,271),(175,313),(113,345),(171,334),(228,313),(285,282),(334,243),(383,180),(347,237),(310,288),(266,341),(221,390),(179,430),(99,472),(160,468),(218,460),(276,443),(332,417),(392,380),(456,327),(421,375),(385,425),(351,475),(307,526),(255,567),(201,594),(255,576),(309,551),(352,524),(387,496),(370,544),(349,586),(322,631),(357,599),(380,560),(401,510),(393,566),(366,630),(313,701),(359,680),(402,644),(447,600),(450,658),(456,734),(476,677),(485,647),(504,679),(519,706),(541,730),(552,736),(563,739),(548,865),(557,757),(585,838),(608,915),(629,972),(1310,972),(1340,906),(1359,814),(1367,908),(1371,818),(1390,734),(1420,719),(1446,684),(1465,642),(1470,727),(1482,785),(1474,699),(1468,637),(1512,662),(1557,691),(1607,710),(1569,667),(1536,620),(1507,571),(1554,604),(1597,627),(1642,641),(1685,645),(1644,607),(1606,561),(1572,516),(1630,547),(1684,568),(1732,581),(1785,590),(1738,552),(1696,510),(1650,464),(1612,420),(1583,400),(1623,418),(1667,436),(1718,453),(1765,464),(1721,430),(1682,391),(1648,351),(1616,309),(1586,277),(1627,317),(1677,354),(1724,386),(1775,414),(1821,439),(1774,397),(1731,353),(1690,309),(1654,265),(1628,238),(1608,220),(1646,255),(1694,282),(1746,307),(1857,327),(1804,307),(1757,277),(1712,242),(1663,197),(1604,126),(1645,135),(1692,140),(1741,139),(1794,129),(1849,118),(1852,108)]
# All C20 silhouette anchors use a fixed anatomical contour order.
assert len(HURT12)==len(HURT35),(len(HURT12),len(HURT35))
SPECS={
 'Y-geto':dict(shot='C03',first=12,last=48,keys=[(12,GETO),(29,GETO),(47,GETO)],band=5,limitation='Full smile, bun, ears and visible upper uniform. Bottom uniform meets native active-image crop y972; no missing torso reconstruction. Fine black hair tips may retain 1-2px warm spill.'),
 'Y-hurt':dict(shot='C20',first=12,last=60,keys=[(12,HURT12),(35,HURT35),(59,HURT35)],band=5,limitation='Native giant close-up: crown and chin extend beyond active crop. Fine side-hair gaps are manual contour approximations with narrow-band correction; blue-white edge spill remains up to 1-3px. No invented neck or torso.')}
def save(path,im):
 ok,b=cv2.imencode('.png',im);assert ok;path.write_bytes(b.tobytes())
def load(shot):
 cap=cv2.VideoCapture(str(ROOT/'outputs/jjk-edge-v17/hyperframes/assets/shots'/f'{shot}.mp4'));frames=[]
 while True:
  ok,im=cap.read()
  if not ok:break
  frames.append(im)
 cap.release();return frames

def make(id):
 s=SPECS[id];frames=load(s['shot']);out=OUT/id;out.mkdir(parents=True,exist_ok=True);keys=s['keys'];prev=None;tracks=[];counts=[];bounds=[];small=[];reds=[];summary=[]
 yy,xx=np.indices((1080,1920));checker=np.repeat(np.where(((xx//24+yy//24)%2)[...,None],150,85),3,axis=2).astype(np.uint8);red=np.empty((1080,1920,3),np.uint8);red[:]=(40,40,205)
 for f in range(s['first'],s['last']):
  im=frames[f];le=max((k for k in keys if k[0]<=f),key=lambda k:k[0]);ri=min((k for k in keys if k[0]>=f),key=lambda k:k[0]);t=0 if le is ri else (f-le[0])/(ri[0]-le[0]);p=(1-t)*np.asarray(le[1],float)+t*np.asarray(ri[1],float);detail={'mode':'manual-anchor' if any(k[0]==f for k in keys) else 'manual-interpolation'}
  if prev is not None and not any(k[0]==f for k in keys):
   q,tr=mod.lk_predict(frames[f-1],im,prev);detail.update(tr)
   if q is not None and np.mean(np.linalg.norm(q-p,axis=1))<10:p=.4*q+.6*p
   else:detail['accepted']=False
  mask=mod.polygon_mask(p,im.shape)
  if s.get('skinSegment'):
   support=np.zeros_like(mask)
   for key in keys:support=cv2.max(support,mod.polygon_mask(key[1],im.shape))
   support=cv2.dilate(support,np.ones((101,101),np.uint8))
   support[:800,930:]=0
   b,g,r=[im[:,:,i].astype(np.int16) for i in range(3)]
   skin=((r>110)&(g>65)&(b>30)&((r-g)>18)&((r-g)<95)&((g-b)>12)&((g-b)<85)&(support>127)).astype(np.uint8)*255
   skin=cv2.morphologyEx(skin,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
   contours,_=cv2.findContours(skin,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);mask=np.zeros_like(mask)
   if contours:cv2.drawContours(mask,[max(contours,key=cv2.contourArea)],-1,255,-1)
  else:
   mask=mod.refine_grabcut(im,mask,s['band'])
   if s.get('paleSegment'):
    b,g,r=[im[:,:,i].astype(np.int16) for i in range(3)]
    skin=(((r+g)>405)&(r>180)&(g>170)&(b>150)&(mask>127)).astype(np.uint8)*255
    skin=cv2.morphologyEx(skin,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    contours,_=cv2.findContours(skin,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);mask=np.zeros_like(mask)
    for c in contours:
     if cv2.contourArea(c)>3000:cv2.drawContours(mask,[c],-1,255,-1)
  mask=cv2.GaussianBlur(mask,(0,0),.6);mask[:108]=0;mask[972:]=0
  rgba=cv2.cvtColor(im,cv2.COLOR_BGR2BGRA);rgba[:,:,3]=mask;save(out/f'{f:06}.png',rgba)
  assert np.array_equal(rgba[:,:,:3],im)
  a=mask[:,:,None]/255;comp=(im*a+checker*(1-a)).astype(np.uint8);rc=(im*a+red*(1-a)).astype(np.uint8)
  for arr,store in [(comp,small),(rc,reds)]:
   cell=cv2.resize(arr,(480,270));cv2.putText(cell,f'{id} fileF{f}',(8,22),cv2.FONT_HERSHEY_SIMPLEX,.6,(20,240,255),1,cv2.LINE_AA);store.append(cell)
  if f in [k[0] for k in keys]:
   row=np.concatenate([cv2.resize(im,(640,360)),cv2.resize(comp,(640,360)),cv2.resize(rc,(640,360))],axis=1);cv2.putText(row,f'{id} fileF{f} / exact prepared RGB',(8,25),cv2.FONT_HERSHEY_SIMPLEX,.7,(0,240,255),1);summary.append(row)
  ys,xs=np.where(mask>127);counts.append(len(xs));bounds.append([int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]);tracks.append(dict(fileFrame=f,polygon=p.tolist(),**detail));prev=p
  if f%8==0:print(id,f,flush=True)
 for name,cells in [('checker',small),('red',reds)]:
  for page,start in enumerate(range(0,len(cells),16)):
   cs=cells[start:start+16];canvas=np.zeros((270*((len(cs)+3)//4),1920,3),np.uint8)
   for i,c in enumerate(cs):canvas[i//4*270:(i//4+1)*270,i%4*480:(i%4+1)*480]=c
   save(EV/f'{id}-{name}-allframes-{page+1:02}.png',canvas)
 save(EV/f'{id}-anchors-summary.png',np.concatenate(summary,axis=0))
 report=dict(id=id,shot=s['shot'],fps=24,firstFileFrame=s['first'],lastFileFrameExclusive=s['last'],count=s['last']-s['first'],filenameIndex='same prepared source file frame; 000012.png = fileF12',width=1920,height=1080,activeRect=[0,108,1920,864],method='Manual visible silhouette anchors, constrained LK affine between anchors; 5px narrow-band GrabCut; 0.6px feather; RGB exact same decoded prepared frame',manualAnchors=[{'fileFrame':k[0],'points':k[1]} for k in keys],noGeneratedRGB=True,exactDecodedRGBVerified=True,alphaZeroInBlackBars=True,limitation=s['limitation'],alphaPixelCounts=counts,bounds=bounds,tracking=tracks)
 (EV/f'{id}-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('DONE',id,s['first'],s['last'],flush=True)
if __name__=='__main__':
 for id in sys.argv[1:] or SPECS:make(id)





