import sys,json,base64,pathlib
sys.path.insert(0,'work/reference-replay-v07/python-deps')
import cv2,numpy as np
root=pathlib.Path('work/reference-replay-v07'); data=json.loads((root/'contour-geometry.json').read_text(encoding='utf-8'))
for r in data['rows']:
    im=cv2.imread(str(root/r['source_image']));p=np.array(r['points'],dtype=np.int32)
    cv2.polylines(im,[p],True,(50,255,50),2,cv2.LINE_AA)
    for i,(x,y) in enumerate(p):
        cv2.circle(im,(int(x),int(y)),4,(20,40,255),-1)
        cv2.putText(im,str(i),(int(x)+5,int(y)-4),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,255,255),1,cv2.LINE_AA)
    cv2.putText(im,f"{r['id']} FILE F{r['fileFrame']} - MANUAL INITIAL CONTOUR - full 1920x1080",(16,65),cv2.FONT_HERSHEY_SIMPLEX,.8,(255,255,255),2,cv2.LINE_AA)
    ok,png=cv2.imencode('.png',im)
    if not ok:raise RuntimeError('encode')
    print(json.dumps({'name':r['qc_overlay'],'data':base64.b64encode(png).decode()}),flush=True)
