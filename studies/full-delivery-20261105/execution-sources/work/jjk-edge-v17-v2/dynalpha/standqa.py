import sys
sys.path.insert(0,'work/jjk-edge-v17-v2/dynalpha');from build import *
id='Y-stand';frames=load('C21');cells=[];rows=[]
for f in range(12,36):
 rgba=cv2.imread(str(OUT/id/f'{f:06}.png'),cv2.IMREAD_UNCHANGED);im=frames[f];mask=rgba[:,:,3];yy,xx=np.indices(mask.shape);checker=np.repeat(np.where(((xx//16+yy//16)%2)[...,None],160,85),3,axis=2);red=np.empty_like(im);red[:]=(50,50,205);a=mask[:,:,None]/255;comp=(im*a+checker*(1-a)).astype(np.uint8);rc=(im*a+red*(1-a)).astype(np.uint8)
 for arr,store in [(comp,cells),(rc,rows)]:
  c=cv2.resize(arr[160:640,1060:1280],(275,600));cv2.putText(c,f'Y-stand fileF{f}',(6,25),cv2.FONT_HERSHEY_SIMPLEX,.55,(0,240,255),1);store.append(c)
for typ,cs in [('checker',cells),('red',rows)]:
 for page,start in enumerate(range(0,24,8)):
  canvas=np.zeros((1200,1100,3),np.uint8)
  for i,c in enumerate(cs[start:start+8]):canvas[i//4*600:(i//4+1)*600,i%4*275:(i%4+1)*275]=c
  save(EV/f'Y-stand-zoom-{typ}-{page+1:02}.png',canvas)
