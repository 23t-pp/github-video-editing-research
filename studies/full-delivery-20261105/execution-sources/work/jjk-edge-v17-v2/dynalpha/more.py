from pathlib import Path
import sys
sys.path.insert(0,'work/reference-replay-v07/python-deps')
import cv2,numpy as np
root=Path.cwd();out=root/'work/jjk-edge-v17-v2/dynalpha'
for name,fs in [('C29',[12,14,16,18,20,22,24,26,28,30,32,34]),('C32',[28,30,32,34,36,38,40,42,44,46,48,50])]:
 cap=cv2.VideoCapture(str(root/'outputs/jjk-edge-v17/hyperframes/assets/shots'/f'{name}.mp4'));frames=[]
 while True:
  ok,im=cap.read()
  if not ok:break
  frames.append(im)
 cap.release();canvas=np.zeros((360*6,1280,3),np.uint8)
 for i,f in enumerate(fs):
  im=frames[f];ok,b=cv2.imencode('.png',im);(out/f'{name}-F{f}.png').write_bytes(b.tobytes());im=cv2.resize(im,(640,360));cv2.putText(im,f'{name} fileF{f}',(10,28),cv2.FONT_HERSHEY_SIMPLEX,.7,(0,240,255),1);canvas[i//2*360:(i//2+1)*360,i%2*640:(i%2+1)*640]=im
 ok,b=cv2.imencode('.jpg',canvas);(out/f'{name}-more.jpg').write_bytes(b.tobytes())
