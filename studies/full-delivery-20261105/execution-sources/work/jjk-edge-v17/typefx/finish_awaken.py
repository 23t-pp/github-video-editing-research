from pathlib import Path
import sys,json
sys.path.insert(0,'D:/gpt/2026-11-04/ps-c-windows-system32-winget-install-2/work/reference-replay-v07/python-deps')
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[3];EV=ROOT/'outputs/jjk-edge-v17/evidence/alpha';OUT=ROOT/'outputs/jjk-edge-v17/hyperframes/assets/alpha/X-awaken'
samples=[];counts=[]
for f in range(72):
 p=OUT/f'{f:06}.png';im=cv2.imread(str(p),cv2.IMREAD_UNCHANGED);assert im is not None
 # Remove only yellow spill around white-hair tips. RGB remains untouched.
 b,g,r=[im[:,:,i].astype(np.float32) for i in range(3)];yy=np.indices(im.shape[:2])[0]
 yellow=(b<g*.72)&(g>125)&(r>g*.95)&(yy<340)
 im[yellow,3]=0
 ok,buf=cv2.imencode('.png',im);assert ok;p.write_bytes(buf.tobytes());counts.append(int((im[:,:,3]>127).sum()))
 if f in [0,12,24,36,48,59,71]:
  y,x=np.indices(im.shape[:2]);checker=np.repeat(np.where(((x//24+y//24)%2)[...,None],155,85),3,axis=2)
  a=im[:,:,3,None]/255.;comp=(im[:,:,:3]*a+checker*(1-a)).astype(np.uint8)
  row=np.concatenate([cv2.resize(im[:,:,:3],(640,360)),cv2.resize(comp,(640,360))],axis=1)
  cv2.putText(row,f'X-awaken fileF{f} / alpha{f:06}',(8,25),cv2.FONT_HERSHEY_SIMPLEX,.65,(255,255,255),1);samples.append(row)
  if f==12:
   bg=np.zeros_like(im[:,:,:3]);bg[:]=[212,187,123];compblue=(im[:,:,:3]*a+bg*(1-a)).astype(np.uint8);ok,buf=cv2.imencode('.jpg',compblue);(EV/'X-awaken-F12-blue.jpg').write_bytes(buf.tobytes())
ok,buf=cv2.imencode('.png',np.concatenate(samples,axis=0));(EV/'X-awaken-alpha-summary.png').write_bytes(buf.tobytes())
p=EV/'X-awaken-alpha-report.json';j=json.loads(p.read_text(encoding='utf-8'));j['alphaPixels']=counts;j['alphaIndexOffset']=0;j['formalAlphaRange']=[12,60];j['hairYellowSpillRemovedByAlphaOnly']=True;p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
print('X-awaken finalized 72 PNGs; source fileF12 => alpha000012.png')
