from pathlib import Path
from PIL import Image
import numpy as np,sys
B=Path(__file__).resolve().parents[3];sys.path.insert(0,str(B/'work/reference-replay-v07/python-deps'))
import cv2
cv2.setNumThreads(1)
O=B/'outputs/jjk-s1-workflow/hyperframes/assets/alpha/XCHASE';yy,xx=np.indices((1080,1920))
for f in range(2,28):
 p=O/f'{f:06}.png';im=np.array(Image.open(p));r,g,b=[im[:,:,k].astype(float) for k in range(3)];a=im[:,:,3];support=cv2.dilate((a>127).astype(np.uint8),np.ones((101,101),np.uint8))>0
 navy=(b>r*1.40)&(b>g*1.25)&(b>20)&(xx>1000)&(xx<1360)&(yy>245)&(yy<570)&support
 a[navy]=255
 # Source navy clothing is continuous. Close only the bounded shoulder island, preserving outer edge.
 closed=cv2.morphologyEx((a>127).astype(np.uint8),cv2.MORPH_CLOSE,np.ones((7,7),np.uint8));region=(xx>1070)&(xx<1350)&(yy>420)&(yy<570)
 a[region&(closed>0)]=255
 binary=(a>127).astype(np.uint8)*255;flood=binary.copy();cv2.floodFill(flood,np.zeros((1082,1922),np.uint8),(0,0),255);holes=cv2.bitwise_not(flood);binary[(xx>1010)&(xx<1350)&(yy>245)&(yy<570)&(holes>0)]=255;elbow=(xx>1100)&(xx<1380)&(yy>760)&(yy<980)&(r>18)&(r<b*1.4)&(r>b*.65)&(g>r*.5)&(abs(r-b)<55);binary[elbow]=0;a=cv2.GaussianBlur(binary,(0,0),.65);a[:60]=0;a[1008:]=0;im[:,:,3]=a;Image.fromarray(im).save(p)
print('26 shoulder navy source-mask repairs; RGB unchanged')
