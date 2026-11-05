import sys,json,base64,pathlib
sys.path.insert(0,'work/reference-replay-v07/python-deps')
import cv2,numpy as np
for kind,nums,crop,scale in [('B02-wheel',[12,16,20,24,28],(650,140,1100,760),.9),('B05-aircar',[12,15,18],(825,530,230,170),3)]:
 for n in nums:
  p=pathlib.Path(f'work/reference-replay-v07/alpha-inspection/{kind}-F{n}.jpg')
  if not p.exists():p=pathlib.Path(f'work/reference-replay-v07/qc/{kind}-F{n}.png')
  im=cv2.imread(str(p));x,y,w,h=crop;im=im[y:y+h,x:x+w].copy()
  step=50 if kind=='B02-wheel' else 10
  for xx in range(((x+step-1)//step)*step,x+w,step):
   cv2.line(im,(xx-x,0),(xx-x,h),(80,120,80),1);cv2.putText(im,str(xx),(xx-x+2,18),0,.4,(80,255,255),1)
  for yy in range(((y+step-1)//step)*step,y+h,step):
   cv2.line(im,(0,yy-y),(w,yy-y),(80,120,80),1);cv2.putText(im,str(yy),(0,yy-y-2),0,.4,(80,255,255),1)
  im=cv2.resize(im,None,fx=scale,fy=scale)
  ok,b=cv2.imencode('.png',im);print(json.dumps({'name':f'{kind}-grid-F{n}.png','data':base64.b64encode(b).decode()}))
