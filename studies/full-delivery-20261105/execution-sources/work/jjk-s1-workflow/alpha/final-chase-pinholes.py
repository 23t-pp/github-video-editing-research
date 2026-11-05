from pathlib import Path
from PIL import Image
import numpy as np,sys
B=Path(__file__).resolve().parents[3];sys.path.insert(0,str(B/'work/reference-replay-v07/python-deps'))
import cv2
O=B/'outputs/jjk-s1-workflow/hyperframes/assets/alpha/XCHASE'
for f in range(2,28):
 p=O/f'{f:06}.png';im=np.array(Image.open(p));a=(im[:,:,3]>127).astype(np.uint8)*255
 if f%12 in [1,2,3,4,5,6,7,8]:
  flood=a.copy();cv2.floodFill(flood,np.zeros((1082,1922),np.uint8),(0,0),255);a|=cv2.bitwise_not(flood)
 count,labels,stats,_=cv2.connectedComponentsWithStats(a);keep=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);a=(labels==keep).astype(np.uint8)*255;a=cv2.GaussianBlur(a,(0,0),.65);a[:60]=0;a[1008:]=0;im[:,:,3]=a;Image.fromarray(im).save(p)
print('final pinholes/component polish; no new source pixels')
