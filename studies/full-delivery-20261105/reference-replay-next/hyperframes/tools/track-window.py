"""Track four real window landmarks, then make the two synchronized projective planes."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];WORKSPACE=ROOT.parents[2]
sys.path.insert(0,str(WORKSPACE/'work/reference-replay-v07/python-deps'))
import cv2,numpy as np
keys=json.loads((ROOT/'motion/window-keyframes.json').read_text(encoding='utf-8'))['keyframes']
asset=next(a for a in json.loads((ROOT/'edit.json').read_text(encoding='utf-8'))['assets'] if a['id']=='A06-sidewindow')
cap=cv2.VideoCapture(str(ROOT/asset['asset']));frames=[]
for n in range(52):
    ok,im=cap.read();assert ok
    if n>=12:frames.append(im[140:940])
cap.release()
actual=[];tracking=[]
for i,im in enumerate(frames):
    n=i+12;left=max((k for k in keys if k['fileFrame']<=n),key=lambda k:k['fileFrame']);right=min((k for k in keys if k['fileFrame']>=n),key=lambda k:k['fileFrame'])
    p=0 if left is right else (n-left['fileFrame'])/(right['fileFrame']-left['fileFrame'])
    guide=np.array(left['points'])*(1-p)+np.array(right['points'])*p
    gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY);kind='manual-anchor' if n in [k['fileFrame'] for k in keys] else 'manual-interpolation'
    if i and kind!='manual-anchor':
        previous=np.asarray(actual[-1],np.float32).reshape(-1,1,2)
        q,st,_=cv2.calcOpticalFlowPyrLK(prevgray,gray,previous,None,winSize=(45,45),maxLevel=3)
        back,bs,_=cv2.calcOpticalFlowPyrLK(gray,prevgray,q,None,winSize=(45,45),maxLevel=3)
        valid=(st[:,0]>0)&(bs[:,0]>0)&(np.linalg.norm(back[:,0]-previous[:,0],axis=1)<1.5)&(np.linalg.norm(q[:,0]-guide,axis=1)<6)
        guide[valid]=.65*q[valid,0]+.35*guide[valid];kind=f'LK+manual-guide {int(valid.sum())}/4'
    actual.append(guide);tracking.append({'assetFrame':n,'kind':kind,'points':guide.tolist()});prevgray=gray
def css(H):
    H=H/H[2,2];v=[H[0,0],H[1,0],0,H[2,0],H[0,1],H[1,1],0,H[2,1],0,0,1,0,H[0,2],H[1,2],0,1]
    return 'matrix3d('+','.join(f'{x:.12g}' for x in v)+')'
full=np.float32([[0,0],[1920,0],[1920,800],[0,800]])
result=[]
for f in range(665,674):
    q=np.float32(actual[f-639]);p=((f-665)/8)**2;t=np.float32(q*(1-p)+full*p)
    h_old=cv2.getPerspectiveTransform(q,t);h_new=cv2.getPerspectiveTransform(full,t)
    result.append({'frame':f,'assetFrame':12+f-639,'progress':p,'sourceQuad':q.tolist(),'targetQuad':t.tolist(),'outgoingCss':css(h_old),'incomingCss':css(h_new)})
report={'coordinateSpace':'active1920x800; fullCanvasY=activeY+140','manualAnchorFrames':[k['fileFrame'] for k in keys],'method':'Four-point Lucas-Kanade forward/backward rejection, constrained to manually inspected keyframes. Homography maps actual window patch to expanded target.','tracking':tracking,'frames':result}
(ROOT/'motion/portal-matrices.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('Tracked 40 source frames; 9 portal frames; final incoming transform is identity.')
