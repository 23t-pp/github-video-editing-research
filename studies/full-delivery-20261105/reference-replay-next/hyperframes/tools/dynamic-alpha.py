"""Local real-footage roto. JSONL PNG bytes go to a Node file-writing host.
Manual polygon anchors are authoritative; optional LK only fills between them.
No learned model or network call. All frame indices are native decoded indices.
"""
import sys, json, base64, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'work/reference-replay-v07/python-deps'))
import cv2
import numpy as np

def emit_png(name, image, kind='png'):
    ok, data = cv2.imencode('.png', image)
    if not ok: raise RuntimeError('PNG encoding failed')
    print(json.dumps({'kind':kind, 'name':name, 'base64':base64.b64encode(data).decode('ascii')}), flush=True)

def polygon_mask(points, shape, holes=()):
    h,w = shape[:2]
    # 2x rasterization gives subpixel edges without inventing object motion.
    a=np.zeros((h*2,w*2),np.uint8)
    cv2.fillPoly(a,[np.rint(np.asarray(points)*2).astype(np.int32)],255)
    for hole in holes: cv2.fillPoly(a,[np.rint(np.asarray(hole)*2).astype(np.int32)],0)
    return cv2.resize(a,(w,h),interpolation=cv2.INTER_AREA)

def lk_predict(previous, current, previous_points):
    h,w=previous.shape[:2]; ratio=min(1.,640./w)
    a=cv2.resize(cv2.cvtColor(previous,cv2.COLOR_BGR2GRAY),None,fx=ratio,fy=ratio)
    b=cv2.resize(cv2.cvtColor(current,cv2.COLOR_BGR2GRAY),None,fx=ratio,fy=ratio)
    m=polygon_mask(np.asarray(previous_points)*ratio,a.shape)
    m=cv2.erode(m,np.ones((3,3),np.uint8))
    p=cv2.goodFeaturesToTrack(a,100,.01,5,mask=m)
    if p is None or len(p)<6:return None,{'accepted':False,'reason':'insufficient-features'}
    q,status,err=cv2.calcOpticalFlowPyrLK(a,b,p,None,winSize=(21,21),maxLevel=3)
    back,bs,_=cv2.calcOpticalFlowPyrLK(b,a,q,None,winSize=(21,21),maxLevel=3)
    valid=(status[:,0]>0)&(bs[:,0]>0)&(np.linalg.norm(back[:,0]-p[:,0],axis=1)<1.5)
    if valid.sum()<6:return None,{'accepted':False,'reason':'forward-backward-rejection','valid':int(valid.sum())}
    mat,inliers=cv2.estimateAffinePartial2D(p[valid,0],q[valid,0],method=cv2.RANSAC,ransacReprojThreshold=2.)
    if mat is None or inliers.sum()<6:return None,{'accepted':False,'reason':'ransac-rejection'}
    mat[:,2]/=ratio
    predicted=np.asarray(previous_points)@mat[:,:2].T+mat[:,2]
    return predicted,{'accepted':True,'inliers':int(inliers.sum()),'features':int(len(p))}

def refine_grabcut(frame, mask, band):
    ys,xs=np.where(mask>127)
    if not len(xs):return mask
    h,w=mask.shape;x0=max(0,int(xs.min())-band-4);x1=min(w,int(xs.max())+band+5);y0=max(0,int(ys.min())-band-4);y1=min(h,int(ys.max())+band+5)
    binary=(mask[y0:y1,x0:x1]>127).astype(np.uint8)
    outer=cv2.dilate(binary,np.ones((band*2+1,band*2+1),np.uint8))
    inner=cv2.erode(binary,np.ones((band*2+1,band*2+1),np.uint8))
    gc=np.full(binary.shape,cv2.GC_BGD,np.uint8)
    gc[outer>0]=cv2.GC_PR_BGD;gc[binary>0]=cv2.GC_PR_FGD;gc[inner>0]=cv2.GC_FGD
    cv2.grabCut(frame[y0:y1,x0:x1],gc,None,np.zeros((1,65),np.float64),np.zeros((1,65),np.float64),2,cv2.GC_INIT_WITH_MASK)
    result=np.zeros_like(mask);result[y0:y1,x0:x1]=np.where((gc==cv2.GC_FGD)|(gc==cv2.GC_PR_FGD),255,0).astype(np.uint8)
    return result

def main():
    spec=json.load(open(sys.argv[1],encoding='utf-8-sig'))
    assert spec['fps']==25
    cap=cv2.VideoCapture(spec['source']);assert cap.isOpened(),spec['source']
    fps=cap.get(cv2.CAP_PROP_FPS);assert abs(fps-25)<1e-6,(fps,'Expected native25fps')
    start=int(spec['assetStartFrame']);count=int(spec['frames']);keys=sorted(spec['keyframes'],key=lambda x:x['frame'])
    assert keys[0]['frame']==0 and keys[-1]['frame']==count-1
    point_count=len(keys[0]['points']);assert all(len(k['points'])==point_count for k in keys)
    frames=[];g=0
    while g<start+count:
        ok,im=cap.read();assert ok,('Decode ended at',g)
        if g>=start:frames.append(im)
        g+=1
    cap.release();h,w=frames[0].shape[:2];assert (w,h)==(1920,1080)
    actual=[];masks=[];tracks=[]
    for f,im in enumerate(frames):
        exact=next((k for k in keys if k['frame']==f),None)
        left=max((k for k in keys if k['frame']<=f),key=lambda k:k['frame']);right=min((k for k in keys if k['frame']>=f),key=lambda k:k['frame'])
        t=0 if left is right else (f-left['frame'])/(right['frame']-left['frame'])
        p=(1-t)*np.asarray(left['points'],np.float64)+t*np.asarray(right['points'],np.float64)
        track={'mode':'manual-anchor' if exact else 'manual-linear'}
        if not exact and f and spec.get('flow')=='lk':
            predicted,track=lk_predict(frames[f-1],im,actual[-1])
            if predicted is not None and np.mean(np.linalg.norm(predicted-p,axis=1))<w*.025:p=.5*predicted+.5*p
            else:track['accepted']=False
        holes=(exact or left).get('holes',[])
        mask=polygon_mask(p,im.shape,holes)
        if spec.get('mode','polygon')=='grabcut':mask=refine_grabcut(im,mask,int(spec.get('grabcutBandPx',5)))
        feather=float(spec.get('featherPx',1.))
        if feather>0:mask=cv2.GaussianBlur(mask,(0,0),feather)
        # Optional manually corrected clipping area, e.g. bottom black letterbox.
        active=spec.get('activeRect')
        if active:
            x,y,aw,ah=active; keep=np.zeros_like(mask);keep[y:y+ah,x:x+aw]=255;mask=cv2.min(mask,keep)
        if f in spec.get('emptyFrames',[]):mask[:]=0
        rgba=cv2.cvtColor(im,cv2.COLOR_BGR2BGRA);rgba[:,:,3]=mask
        emit_png(f'{f:06d}.png',rgba)
        actual.append(p);masks.append(mask);tracks.append(track)
    all_points=np.concatenate(actual);x0=max(0,int(all_points[:,0].min())-30);x1=min(w,int(all_points[:,0].max())+31);y0=max(0,int(all_points[:,1].min())-30);y1=min(h,int(all_points[:,1].max())+31)
    cells=[]
    for f,(im,mask) in enumerate(zip(frames,masks)):
        yy,xx=np.indices((h,w));checker=np.where(((xx//24+yy//24)%2)[...,None],150,95).astype(np.float32);checker=np.repeat(checker,3,axis=2)
        a=mask[:,:,None].astype(np.float32)/255;composite=np.clip(im*a+checker*(1-a),0,255).astype(np.uint8)
        original=cv2.resize(im[y0:y1,x0:x1],(320,200));cutout=cv2.resize(composite[y0:y1,x0:x1],(320,200));mono=cv2.cvtColor(cv2.resize(mask[y0:y1,x0:x1],(320,200)),cv2.COLOR_GRAY2BGR)
        row=np.concatenate([original,cutout,mono],axis=1)
        cv2.putText(row,f'{spec["id"]} localF{f} / assetF{start+f}',(8,20),cv2.FONT_HERSHEY_SIMPLEX,.55,(30,240,255),1,cv2.LINE_AA);cells.append(row)
    evidence=np.concatenate(cells,axis=0);emit_png('alpha-evidence.png',evidence,'evidence')
    report={'id':spec['id'],'fps':25,'width':w,'height':h,'sourceFilename':pathlib.Path(spec['source']).name,'assetStartFrame':start,'frames':count,'sourceFrameIndices':list(range(start,start+count)),'sourceTimesSeconds':[round(spec['sourceIn']+(start+f-12)/25,9) for f in range(count)],'mode':spec.get('mode','polygon'),'flow':spec.get('flow','none'),'manualKeyframes':[k['frame'] for k in keys],'emptyFrames':spec.get('emptyFrames',[]),'actualPolygons':[{ 'frame':f,'points':p.tolist()}for f,p in enumerate(actual)],'tracking':tracks,'featherPx':spec.get('featherPx',1.),'alphaPixelsPerFrame':[int((m>127).sum())for m in masks],'noGeneratedContent':True,'rgbPixelsFromExactDecodedSourceFrames':True}
    print(json.dumps({'kind':'report','name':'alpha-report.json','value':report}),flush=True)

if __name__=='__main__':main()
