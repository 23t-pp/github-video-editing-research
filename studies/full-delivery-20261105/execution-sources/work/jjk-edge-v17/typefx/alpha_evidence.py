from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from roto_fg import ROOT,ASSET,EV,cv2,np,save_png,load_frames
stats={}
for name,count in [('X-awaken',72),('X-palm',60)]:
 frames=load_frames(name);cells=[];hashes=[];bboxes=[];areas=[];nonzero=0;match=True
 for f in range(count):
  rgba=cv2.imread(str(ASSET/'alpha'/name/f'{f:06}.png'),cv2.IMREAD_UNCHANGED);assert rgba.shape==(1080,1920,4)
  assert np.array_equal(rgba[:,:,:3],frames[f]);a=rgba[:,:,3];areas.append(int((a>127).sum()))
  yy,xx=np.where(a>127);bboxes.append(None if not len(xx) else [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)])
  if len(xx):nonzero+=1
  y,x=np.indices(a.shape);checker=np.repeat(np.where(((x//24+y//24)%2)[...,None],155,85),3,axis=2);af=a[:,:,None]/255.;comp=(rgba[:,:,:3]*af+checker*(1-af)).astype(np.uint8)
  crop=(slice(225,972),slice(610,1310)) if name=='X-awaken' else (slice(108,972),slice(100,1450))
  cell=np.zeros((240,400,3),np.uint8);cell[:220,:200]=cv2.resize(frames[f][crop],(200,220));cell[:220,200:]=cv2.resize(comp[crop],(200,220));cv2.putText(cell,f'{name} fileF{f} = alpha{f:06}',(4,235),cv2.FONT_HERSHEY_SIMPLEX,.38,(255,255,255),1);cells.append(cell)
 for page in range((count+23)//24):
  canvas=np.zeros((1440,1600,3),np.uint8)
  for j,cell in enumerate(cells[page*24:(page+1)*24]):canvas[j//4*240:(j//4+1)*240,j%4*400:(j%4+1)*400]=cell
  save_png(EV/f'{name}-allframes-{page+1:02}.png',canvas)
 stats[name]=dict(pngCount=count,nonempty=nonzero,formalAlphaFirst=12,formalAlphaEndExclusive=60 if name=='X-awaken' else 48,sourceF12MapsTo='000012.png',allRGBExactPreparedFrame=True,bboxPerFrame=bboxes,alphaArea=areas)
(EV/'alpha-integrity.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8');print('Validated all132 PNGs RGB exact; wrote 6 every-frame evidence pages.')
