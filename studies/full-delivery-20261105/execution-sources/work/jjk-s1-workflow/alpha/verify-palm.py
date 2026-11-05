from pathlib import Path
import sys,subprocess,json,hashlib
BASE=Path(__file__).resolve().parents[3];R=BASE/'outputs/jjk-s1-workflow';EV=R/'evidence/alpha';O=R/'hyperframes/assets/alpha/XPALM'
sys.path.insert(0,str(BASE/'work/reference-replay-v07/python-deps'))
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';MOV=R/'hyperframes/assets/shots/XPALM.mp4'
raw=subprocess.run([FF,'-v','error','-threads','1','-i',str(MOV),'-an','-vf','scale=in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24','-f','rawvideo','pipe:1'],capture_output=True,check=True).stdout
src=np.frombuffer(raw,dtype=np.uint8).reshape(-1,1080,1920,3);yy,xx=np.indices((1080,1920));checker=np.repeat(np.where(((xx//32+yy//32)%2)[...,None],155,80),3,axis=2).astype(np.uint8);red=np.full((1080,1920,3),(190,38,38),np.uint8)
cells={'checker':[],'red':[]};font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19);checks=[]
for f in range(2,28):
    p=O/f'{f:06}.png';rgba=np.array(Image.open(p));alpha=rgba[:,:,3];n,labels,stats,_=cv2.connectedComponentsWithStats((alpha>127).astype(np.uint8))
    keep=1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA]));area=stats[keep,cv2.CC_STAT_AREA];other=sum(stats[1:,cv2.CC_STAT_AREA])-area
    if other>0:
        alpha=cv2.GaussianBlur((labels==keep).astype(np.uint8)*255,(0,0),.65);alpha[:60]=0;alpha[1020:]=0;rgba[:,:,3]=alpha;Image.fromarray(rgba).save(p)
    assert np.array_equal(rgba[:,:,:3],src[f]);assert not alpha[:60].any() and not alpha[1020:].any()
    checks.append({'preparedFrame':f,'rgbSameAsPrepared':True,'bandsAlphaZero':True,'largestComponentArea':int(area),'removedDetachedOpaquePixels':int(other),'pngSha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    a=alpha[:,:,None]/255
    for kind,bg in [('checker',checker),('red',red)]:
        comp=Image.fromarray((src[f]*a+bg*(1-a)).astype(np.uint8))
        if f in [2,15,27]:comp.save(EV/f'XPALM-{kind}-F{f:02}.png')
        thumb=comp.resize((480,270));d=ImageDraw.Draw(thumb);d.text((7,5),f'XPALM F{f:02}',font=font,fill='yellow');cells[kind].append(thumb)
for kind,ims in cells.items():
    for page,start in enumerate(range(0,len(ims),16)):
        selected=ims[start:start+16];sheet=Image.new('RGB',(1920,270*((len(selected)+3)//4)),'black')
        for k,im in enumerate(selected):sheet.paste(im,((k%4)*480,(k//4)*270))
        sheet.save(EV/f'XPALM-{kind}-{page+1:02}.jpg',quality=94)
small=src[:,60:1020:10,::10].astype(np.int16);deltas=np.abs(np.diff(small,axis=0)).mean((1,2,3)).tolist()
report=json.loads((EV/'XPALM-alpha-report.json').read_text(encoding='utf-8'));report.update(perFrameChecks=checks,method=report['method']+'; remove detached alpha components, preserve largest connected hand/forearm',allRgbExactlyEqualsPreparedDecodedFrame=True,all26FrameSourceContinuityMeanRgbDeltas=deltas,sourceContinuityCheck='全31帧缩略RGB相邻差异+F2/15/27实际源帧查看，未发现原切；手姿多数hold、源青焰变化，未补造手指运动',dynamicClaim='26张同号真实RGBA；手姿主要为动画hold，源青焰有变化；不是26个大幅不同姿态',limitations='Source wrist/sleeve exits right edge, bottom source120px cropped; a few top subtitle pixels remain near preparedy1015 but excluded from alpha support. Cyan ink/glow 1–3px residual and manual outline approximations; no offscreen arm reconstruction.')
(EV/'XPALM-alpha-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'frames':26,'maxAdjacentMeanDelta':max(deltas),'maxDetachedRemoved':max(x['removedDetachedOpaquePixels'] for x in checks),'rgbAllExact':True},ensure_ascii=False))
