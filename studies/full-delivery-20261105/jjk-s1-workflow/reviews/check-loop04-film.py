from pathlib import Path
import subprocess,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];L=R/'loops/loop-04';O=L/'reviewer-evidence';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
v=L/'loop-04-final.mp4';h=sha(v);ff='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
raw=subprocess.run([ff,'-v','error','-i',str(v),'-vf','scale=320:180','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],capture_output=True,check=True).stdout;a=np.frombuffer(raw,np.uint8).reshape(-1,180,320,3);assert len(a)==1440 and sha(v)==h
def contact(ids,out,cols=4):
    im=Image.new('RGB',(320*cols,204*((len(ids)+cols-1)//cols)),'#080e18');d=ImageDraw.Draw(im)
    for j,f in enumerate(ids):
        x=j%cols*320;y=j//cols*204;im.paste(Image.fromarray(a[f]),(x,y));d.text((x+4,y+184),f'actual MP4 F{f:04} {f/24:.3f}s',fill='#90d5ed')
    im.save(O/out,quality=96)
for j in range(2):contact(list(range(j*720,(j+1)*720,24)),f'actual-film-{j+1:02}.jpg',5)
contact(list(range(815,844)),'actual-eyes-815-843.jpg')
contact(list(range(611,639)),'actual-strike-611-638.jpg')
for j in range(3):contact(list(range(1280+j*28,min(1363,1280+(j+1)*28))),f'actual-tail-{j+1:02}.jpg')
p=json.loads((L/'plan.json').read_text(encoding='utf-8'));proof=[]
for c in [8,11,17,18]:
    pr=json.loads((L/f'render-proofs/chunk-{c:02}.json').read_text(encoding='utf-8')) if (L/f'render-proofs/chunk-{c:02}.json').exists() else None
    if pr:proof.append({'chunk':c,'planSha256':pr['planSha256'],'outputShaEntries':len(pr['outputFrameSha256'])})
tail=[]
for s in p['shots']:
    if 1282<=s['startFrame']<1360:
        lo=s['startFrame'];hi=lo+s['frames'];x=a[lo:hi,11:169].astype(np.float32);diff=np.abs(x[1:]-x[:-1]).mean(axis=(1,2,3));tail.append({'shot':s['id'],'assetId':s['assetId'],'range':[lo,hi],'medianRGBFrameDifference':float(np.median(diff)),'nearHoldFractionMADbelow05':float((diff<.5).mean())})
report={'reviewer':'/root/s1_design_auditor','videoSha256':h,'planSha256':sha(L/'plan.json'),'independentDecodedFrames':len(a),'thumbnailSize':[320,180],'scope':'actual complete encoded MP4 decoded, own contacts generated; frame-difference is localization, not automatic art pass. No listening.','contacts':{f.relative_to(R).as_posix():sha(f) for f in sorted(O.glob('actual-*.jpg'))},'freshChunkProofRows':proof,'tailShotMotionCandidates':tail}
(O/'actual-film-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'videoSha':h,'decoded':len(a),'tail':tail,'proofRows':proof},ensure_ascii=False))
