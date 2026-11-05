"""Compare the encoded picture to its timeline and the AAC to its PCM master."""
import io
import json
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

scratch=Path(__file__).resolve().parent
out=scratch.parents[1]/'outputs/fast60'
project=out/'hyperframes'
plan=json.loads((project/'edit.json').read_text(encoding='utf-8'))
video=out/'弯心_APEX_60秒.mp4'
evidence=out/'evidence'; evidence.mkdir(exist_ok=True)
ff='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'

def run(args):
    p=subprocess.run([ff,'-v','error','-threads','2','-filter_threads','1',*args],capture_output=True)
    if p.returncode: raise RuntimeError(p.stderr.decode(errors='replace'))
    return p.stdout

def frame(path,index,width=320,height=180):
    args=['-i',str(path),'-an','-vf',f'select=eq(n\\,{index}),scale={width}:{height}:flags=area,format=rgb24','-frames:v','1','-c:v','rawvideo','-threads','1','-f','rawvideo','pipe:1']
    return np.frombuffer(run(args),np.uint8).reshape(height,width,3)

def ranges(mask):
    padded=np.r_[False,mask,False]
    edges=np.where(padded[1:]!=padded[:-1])[0]
    return [[int(a),int(b)] for a,b in zip(edges[::2],edges[1::2])]

# Read every frame for coverage and all 42 midpoints for source matching.
small=np.frombuffer(run(['-i',str(video),'-an','-vf','scale=192:108:flags=area,format=rgb24','-c:v','rawvideo','-threads','1','-f','rawvideo','pipe:1']),np.uint8).reshape(-1,108,192,3)
if len(small)!=1440:raise ValueError(f'Decoded {len(small)} frames')
active=small[:,14:94,:,:]
blacks=ranges(active.mean(axis=(1,2,3)) < 1)
if any(a<1418 for a,b in blacks):raise ValueError(f'Unexpected black run {blacks}')
effects={'title':plan['effects']['title'],'triptych':plan['effects']['triptych'],'end':plan['effects']['endFade']}
checks=[]
for shot in plan['shots']:
    f=shot['startFrame']+shot['frames']//2
    fx=next((key for key,r in effects.items() if r['startFrame']<=f<r['endFrame']),None)
    if fx:
        j=f-effects[fx]['startFrame']
        expected=frame(scratch/'render'/fx/'rendered'/f'frame_{j+1:06}.png',0,192,108)
    else:
        expected=frame(project/shot['asset'],shot['assetStartFrame']+f-shot['startFrame'],192,108)
    mae=float(np.abs(expected.astype('int16')-small[f].astype('int16')).mean())
    checks.append({'shot':shot['id'],'frame':f,'reference':fx or shot['id'],'rgbMeanAbsoluteError':round(mae,3)})
    if mae>6:raise ValueError(f'{shot["id"]} unexpected reference difference at {f}: {mae}')

labels=[(30,'片名入场'),(102,'开关'),(120,'氮气'),(131,'转速'),(153,'起跑'),(303,'贴车追拍'),(528,'窗框'),(640,'目光'),(701,'三联屏'),(738,'冲出烟尘'),(879,'冰水'),(1009,'双直升机'),(1072,'回头'),(1194,'腾空'),(1240,'爆炸'),(1270,'夕阳'),(1335,'交接'),(1381,'分岔')]
sheet=Image.new('RGB',(1080,6*175+70),'#111312');d=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
big=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',25)
d.text((12,14),'弯心 / APEX　｜　18 个成片时刻',font=big,fill='#eee9df')
for i,(f,label) in enumerate(labels):
    x=i%3*360;y=62+i//3*175
    pic=Image.fromarray(small[f,14:94,:,:]).resize((356,148),Image.Resampling.LANCZOS)
    sheet.paste(pic,(x,y))
    d.text((x+4,y+149),f'{f/24:05.2f}s　{label}',font=font,fill='#eee9df')
sheet.save(evidence/'成片分镜.jpg',quality=92)
poster=run(['-ss','1.3','-i',str(video),'-an','-frames:v','1','-q:v','2','-f','image2pipe','-c:v','mjpeg','pipe:1'])
(out/'封面.jpg').write_bytes(poster)

def pcm(path):
    return np.frombuffer(run(['-i',str(path),'-vn','-ac','2','-ar','48000','-c:a','pcm_f32le','-f','f32le','pipe:1']),'<f4').reshape(-1,2)

master=pcm(project/plan['audio']['master'])
decoded=pcm(video)
if not len(master)<=len(decoded)<len(master)+1024:raise ValueError(f'Unexpected decoded AAC length {len(decoded)}')
windows=[]
for sec in (2,12,25,39,49,57):
    i=sec*48000
    ref=master[i:i+48000].reshape(-1)
    actual=decoded[i:i+48000].reshape(-1)
    corr=float(np.corrcoef(ref,actual)[0,1])
    windows.append({'sec':sec,'same-time PCM correlation':round(corr,6)})
    if corr<.96: raise ValueError(f'Audio sync check failed at {sec}s: {corr}')
report={'framesDecoded':len(small),'blackRegionsInsidePicture_[first,last)':blacks,'comparedShotCount':len(checks),'shotComparisons':checks,'AACComparedAtSixTimes':windows,'inputPCMSampleFrames':len(master),'decodedAACSampleFramesIncludingCodecPadding':len(decoded)}
(evidence/'成片抽检.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frames':len(small),'black':blacks,'maxRgbMAE':max(s['rgbMeanAbsoluteError'] for s in checks),'minimumAudioCorrelation':min(s['same-time PCM correlation'] for s in windows)}))
