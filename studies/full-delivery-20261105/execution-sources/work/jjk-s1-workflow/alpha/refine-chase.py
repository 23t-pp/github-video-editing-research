from pathlib import Path
import subprocess,sys,json,hashlib,numpy as np
from PIL import Image
B=Path(__file__).resolve().parents[3];R=B/'outputs/jjk-s1-workflow';E=R/'evidence/alpha';O=R/'hyperframes/assets/alpha/XCHASE';sys.path.insert(0,str(B/'work/reference-replay-v07/python-deps'))
import cv2
cv2.setNumThreads(1)
F='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';raw=subprocess.run([F,'-v','error','-threads','1','-i',str(R/'hyperframes/assets/shots/XCHASE.mp4'),'-an','-vf','scale=in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24','-f','rawvideo','pipe:1'],capture_output=True,check=True).stdout;rgb=np.frombuffer(raw,np.uint8).reshape(-1,1080,1920,3);yy,xx=np.indices((1080,1920));red=np.full((1080,1920,3),(190,38,38),np.uint8)
checks=[]
for f in (range(2,28) if '--all' in sys.argv else [2,10]):
    old=np.array(Image.open(O/f'{f:06}.png'));m=old[:,:,3];support=cv2.dilate(m,np.ones((201,201),np.uint8));core=cv2.erode(m,np.ones((151,151),np.uint8));gc=np.full(m.shape,cv2.GC_BGD,np.uint8);gc[support>127]=cv2.GC_PR_BGD;gc[m>127]=cv2.GC_PR_FGD;gc[core>127]=cv2.GC_FGD
    rr,gg,bb=[rgb[f,:,:,k].astype(np.int16) for k in range(3)];hair=(xx>520)&(xx<1210)&(yy>65)&(yy<510)&(rr>60)&(rr>gg*1.16)&(rr>bb*1.08);gc[hair]=cv2.GC_FGD
    nearhair=cv2.dilate(hair.astype(np.uint8),np.ones((13,13),np.uint8))>0
    pavement=(xx>1020)&(xx<1260)&(yy>120)&(yy<520)&(rr>35)&(rr<150)&(np.abs(rr-bb)<17)&(np.abs(rr-gg)<38)&(~nearhair)
    gc[pavement]=cv2.GC_BGD;gc[:60]=cv2.GC_BGD;gc[1008:]=cv2.GC_BGD
    cv2.grabCut(rgb[f,:,:,::-1].copy(),gc,None,np.zeros((1,65),float),np.zeros((1,65),float),4,cv2.GC_INIT_WITH_MASK)
    mat=((gc==1)|(gc==3)).astype(np.uint8)*255;n,lab,stats,_=cv2.connectedComponentsWithStats(mat);keep=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);mat=(lab==keep).astype(np.uint8)*255;mat=cv2.GaussianBlur(mat,(0,0),.65);mat[:60]=0;mat[1008:]=0
    rgba=np.dstack((rgb[f],mat));assert np.array_equal(rgba[:,:,:3],rgb[f]);assert not mat[:60].any() and not mat[1008:].any()
    a=mat[:,:,None]/255
    if '--all' in sys.argv:
        p=O/f'{f:06}.png';Image.fromarray(rgba).save(p);checks.append({'frame':f,'rgbSame':True,'bandsZero':True,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    else:Image.fromarray(rgba).save(E/f'XCHASE-r3-test-F{f:02}.png')
    if f in [2,4,6,10,12,27]:Image.fromarray((rgb[f]*a+red*(1-a)).astype(np.uint8)).save(E/f'XCHASE-r3-test-red-F{f:02}.png')
    print(f,flush=True)
if '--all' in sys.argv:
    j=json.loads((E/'XCHASE-alpha-report.json').read_text(encoding='utf-8'));j.update(revision='R3_source_colour_narrow_shadow_cleanup_and_wide_boundary_refine',refineMethod='201px support/151px core bounded recomputation from R2 contours, source hair/pavement constraints,4-iteration GrabCut; RGB unchanged',finalPerFrameChecks=checks,all26RgbExact=True)
    (E/'XCHASE-alpha-report.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
