from pathlib import Path
import sys
sys.path.insert(0,'work/reference-replay-v07/python-deps')
import cv2,numpy as np
root=Path.cwd();out=root/'work/jjk-edge-v17-v2/dynalpha';cap=cv2.VideoCapture(str(root/'outputs/jjk-edge-v17/hyperframes/assets/shots/C21.mp4'));frames=[]
while True:
 ok,im=cap.read()
 if not ok:break
 frames.append(im)
cap.release();canvas=np.zeros((800,1200,3),np.uint8)
for i,f in enumerate([12,23,35]):
 im=frames[f];ok,b=cv2.imencode('.png',im);(out/f'C21-F{f}.png').write_bytes(b.tobytes());crop=im[140:620,1040:1310];crop=cv2.resize(crop,(400,720));canvas[:720,i*400:(i+1)*400]=crop;cv2.putText(canvas,f'C21 F{f}',(i*400+10,760),cv2.FONT_HERSHEY_SIMPLEX,.9,(255,255,255),1)
ok,b=cv2.imencode('.jpg',canvas);(out/'C21-anchors.jpg').write_bytes(b.tobytes())
print(len(frames))
