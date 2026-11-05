from pathlib import Path
import csv,hashlib,json,subprocess,sys,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/reference-replay-next';HF=OUT/'hyperframes';WORK=ROOT/'work/reference-replay-v07';sys.path.insert(0,str(WORK/'python-deps'))
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';FP='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe';movie=OUT/'越界_V07复刻.mp4'
def cap(cmd):
    p=subprocess.run(cmd,capture_output=True)
    if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace'))
    return p.stdout
raw=cap([FF,'-v','error','-threads','2','-filter_threads','1','-i',str(movie),'-map','0:v:0','-an','-vf','crop=1920:800:0:140,scale=192:80','-pix_fmt','rgb24','-c:v','rawvideo','-threads','1','-f','rawvideo','pipe:1'])
pixels=np.frombuffer(raw,np.uint8).reshape(-1,80,192,3);assert len(pixels)==750
mean=pixels.mean(axis=(1,2,3));mx=pixels.max(axis=(1,2,3));assert np.all(mx[:691]>10),np.where(mx[:691]<=10)
def audio(p):return np.frombuffer(cap([FF,'-v','error','-threads','2','-i',str(p),'-map','0:a:0','-ac','2','-ar','48000','-f','f32le','pipe:1']),np.float32).reshape(-1,2)
master=audio(HF/'assets/audio/master.wav');encoded=audio(movie);assert len(master)==1440000 and len(encoded)>=len(master)
n=len(master);correlation=float(np.corrcoef(master.reshape(-1),encoded[:n].reshape(-1))[0,1]);assert correlation>.99,correlation
candidate=ROOT/'outputs/reference-library-20261105/audio/music-candidates/V07__music-candidate.m4a';copied=HF/'assets/audio/V07-library-original.m4a';digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert digest(candidate)==digest(copied)
plan=json.loads((HF/'edit.json').read_text(encoding='utf-8'));cursor=0
for s in plan['shots']:assert s['startFrame']==cursor;cursor+=s['frames']
assert cursor==750
portal=json.loads((HF/'motion/portal-matrices.json').read_text(encoding='utf-8'));last=portal['frames'][-1];assert np.allclose(last['targetQuad'],[[0,0],[1920,0],[1920,800],[0,800]])
checks={'file':movie.name,'sha256':digest(movie),'videoFramesDecoded':len(pixels),'pictureSize':[1920,1080],'fps':25,'durationSeconds':30,'cutCount':len(plan['shots']),'continuousCutTimeline':True,'libraryCopySha256':digest(copied),'libraryCopyByteIdentical':True,'masterSampleFrames':len(master),'aacDecodedSampleFrames':len(encoded),'sameTimeAudioCorrelation':correlation,'audioComparison':'At zero offset; AAC is lossy, correlation is not a bit-identical claim. No auditory listening was performed.','unexpectedFullyBlackFramesBeforeFinalGesture':np.where(mx[:691]<=10)[0].tolist(),'fullyBlackFrames':np.where(mx==0)[0].tolist(),'endingFrameMeanRGB':{str(f):float(mean[f]) for f in [691,705,715,725,735,736,737,749]},'portalLastTargetIsFullFrame':True,'checksScope':'All frames decoded at 192x80 active area; 6 effect sequences reviewed via rendered contact sheets; selected full-size frames visually inspected; not a full-resolution manual review of all 750 frames.'}
(OUT/'质量检查.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
with (HF/'镜头表.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.writer(f);writer.writerow(['镜头','说明','时间线起帧','帧数','开始秒','结束秒','源片编号','源入点秒','文件入帧','素材文件'])
    for s in plan['shots']:writer.writerow([s['id'],s['label'],s['startFrame'],s['frames'],s['startFrame']/25,(s['startFrame']+s['frames'])/25,s['film'],s['sourceIn'],s['assetStartFrame'],s['asset']])
ev=OUT/'evidence';(ev/'qc').mkdir(parents=True,exist_ok=True)
for name in ['scouting.md','scouting.json','source.json','contour-geometry.json','reference-keyframes.json','base-qc-repairs.json']:
    if (WORK/name).exists():shutil.copy2(WORK/name,ev/('参考拆解与配对.md' if name=='scouting.md' else name))
for pattern in ['T*-reference.jpg','*-outline-F*.png','P15-all-native.jpg','P16-all-native.jpg','P17-replacement-all.jpg']:
    for p in (WORK/'qc').glob(pattern):shutil.copy2(p,ev/'qc'/p.name)
render=WORK/'render/master-frames';ref=json.loads((ROOT/'outputs/reference-library-20261105/local-media-paths.json').read_text(encoding='utf-8'))['V07'];refcap=cv2.VideoCapture(ref)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
events=[('01 手部提前进入',[151,157,163]),('02 旋转轮胎擦镜',[191,201,211]),('03 手覆盖旧人脸',[237,244,251]),('04 换挡动作接力',[403,410,416]),('05 腾空车接力',[576,581,586]),('06 侧窗门户',[664,667,674])]
sheet=Image.new('RGB',(960,len(events)*414),(15,18,17));draw=ImageDraw.Draw(sheet)
for row,(title,frames) in enumerate(events):
    y=row*414;draw.text((8,y+5),title+'  上：V07参考 / 下：本次成片',font=font,fill='#c2f2a1')
    for col,f in enumerate(frames):
        refcap.set(cv2.CAP_PROP_POS_FRAMES,f);ok,im=refcap.read();assert ok
        im=Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB)).resize((320,180));sheet.paste(im,(col*320,y+32))
        result=Image.open(render/f'frame_{f+1:06}.png').convert('RGB').resize((320,180));sheet.paste(result,(col*320,y+212))
        draw.text((col*320+8,y+391),f'F{f} / {f/25:.2f}s',font=font,fill='#c1c4ba')
refcap.release();sheet.save(ev/'六组转场对照.jpg',quality=92)
Image.open(render/'frame_000202.png').convert('RGB').save(OUT/'封面.jpg',quality=95)
print(json.dumps({k:v for k,v in checks.items() if k not in ['fullyBlackFrames','endingFrameMeanRGB']},ensure_ascii=False,indent=2))
