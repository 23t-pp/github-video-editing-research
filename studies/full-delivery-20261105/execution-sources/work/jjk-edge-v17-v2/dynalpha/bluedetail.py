from pathlib import Path
import sys
sys.path.insert(0,'work/reference-replay-v07/python-deps');import cv2,numpy as np
p=Path('outputs/jjk-edge-v17-v2/hyperframes/assets/alpha/Y-blue/000020.png');im=cv2.imread(str(p),-1);a=im[:,:,3:]/255;red=np.empty(im[:,:,:3].shape,np.uint8);red[:]=(40,40,205);c=(im[:,:,:3]*a+red*(1-a)).astype(np.uint8);crop=np.concatenate([im[108:410,800:1450,:3],c[108:410,800:1450]],axis=0);ok,b=cv2.imencode('.png',crop);Path('work/jjk-edge-v17-v2/dynalpha/blue20detail.png').write_bytes(b.tobytes())
