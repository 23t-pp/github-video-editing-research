from pathlib import Path
import sys
sys.path.insert(0,'work/reference-replay-v07/python-deps')
import cv2,numpy as np
from PIL import Image,ImageDraw
root=Path.cwd();out=root/'work/jjk-edge-v17-v2/dynalpha'
for name,end in [('C20',59),('C03',47),('C29',43),('C32',43)]:
 cap=cv2.VideoCapture(str(root/'outputs/jjk-edge-v17/hyperframes/assets/shots'/f'{name}.mp4')); frames=[]
 while True:
  ok,im=cap.read()
  if not ok:break
  frames.append(im)
 cap.release()
 samples=[12,(12+end)//2,end]
 canv=Image.new('RGB',(960,570*3))
 for i,f in enumerate(samples):
  im=Image.fromarray(cv2.cvtColor(frames[f],cv2.COLOR_BGR2RGB));im.save(out/f'{name}-F{f}.png');im.thumbnail((960,540));canv.paste(im,(0,i*570));ImageDraw.Draw(canv).text((10,i*570+542),f'{name} fileF{f}',fill='white')
 canv.save(out/f'{name}-anchors.jpg',quality=95)
 print(name,len(frames),flush=True)
