from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,hashlib,re,io
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]/'outputs/jjk-edge-v17';FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';FP='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'
movie=ROOT/'挚友_EDGE_一分钟.mp4';HF=ROOT/'hyperframes';W=Path(__file__).resolve().parent
def run(args):return subprocess.run(args,capture_output=True,check=True)
def pcm(file):return np.frombuffer(run([FF,'-v','error','-i',str(file),'-vn','-ac','2','-ar','48000','-f','f32le','pipe:1']).stdout,dtype='<f4').reshape(-1,2)
def picture():return np.frombuffer(run([FF,'-v','error','-i',str(movie),'-an','-vf','scale=192:108','-pix_fmt','rgb24','-f','rawvideo','pipe:1']).stdout,dtype=np.uint8).reshape(-1,108,192,3)
with ThreadPoolExecutor(max_workers=3) as pool:
    future=[pool.submit(pcm,movie),pool.submit(pcm,HF/'assets/audio/master.wav'),pool.submit(picture)]
    audio,master,frames=[f.result() for f in future]
assert len(frames)==1440
n=min(len(audio),len(master));correlation=float(np.corrcoef(audio[:n].reshape(-1),master[:n].reshape(-1))[0,1])
means=frames[:,11:98].mean((1,2,3));dark=np.where(means<10)[0].tolist()
unexpected=[f for f in dark if not (384<=f<433 or f>=1416)]
edit=json.loads((HF/'edit.json').read_text(encoding='utf-8'))
assert len(edit['shots'])==67
assert all(a['startFrame']+a['frames']==b['startFrame'] for a,b in zip(edit['shots'],edit['shots'][1:]))
assert not unexpected,unexpected
assert correlation>.995,correlation
info=json.loads(run([FP,'-v','error','-show_streams','-show_format','-of','json',str(movie)]).stdout)
loud=run([FF,'-hide_banner','-i',str(movie),'-af','ebur128=peak=true','-f','null','-']).stderr.decode(errors='replace')
(ROOT/'evidence/声音响度实测.log').write_text(loud,encoding='utf-8')
report={'file':movie.name,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'framesDecoded':len(frames),'fps':24,'width':1920,'height':1080,'targetDurationSeconds':60,'formatDurationSeconds':float(info['format']['duration']),'videoStream':next(s for s in info['streams'] if s['codec_type']=='video'),'audioStream':next(s for s in info['streams'] if s['codec_type']=='audio'),'masterSampleFrames':len(master),'aacDecodedSampleFrames':len(audio),'sameTimeAudioCorrelation':correlation,'nearBlackFrameThreshold':'192x108整片缩略解码，active y11:98，RGB均值<10','nearBlackFrames':dark,'unexpectedNearBlackFrames':unexpected,'timelineContinuous':True,'selectedMusicSourceSeconds':[147,207],'auditoryListeningPerformed':False,'scope':'完整1440帧缩略解码与声音数值对照；67镜首中尾与修订尾帧人工查看，重点合成原尺寸抽查；不是对全部1440帧逐张全分辨率人工验收。'}
(ROOT/'质量检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
# Actual final-film frames against the two selected references.
local=json.loads((ROOT.parent/'reference-library-20261105/local-media-paths.json').read_text(encoding='utf-8'))
events=[('冷暖记忆窗','V17',10.9,11.2),('撕边人物','V17',5.0,19.1),('双半脸','V17',17.05,26.375),('伸掌提前入场','V17',15.2,32.54),('双排紫字与动态人物','V02',4.9,28.8),('镜片中的记忆','V17',25.3,56.66)]
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',25);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
canvas=Image.new('RGB',(1280,6*420),'#080b13');d=ImageDraw.Draw(canvas)
def frame(file,t):
    b=run([FF,'-v','error','-ss',str(t),'-i',str(file),'-frames:v','1','-vf','scale=640:360','-f','image2pipe','pipe:1']).stdout
    return Image.open(io.BytesIO(b)).convert('RGB')
for i,(label,ref,rt,nt) in enumerate(events):
    y=i*420;d.text((12,y+5),label,font=font,fill='#72c7ed');d.text((640,y+7),f'本片 {nt:.3f}s',font=small,fill='white')
    canvas.paste(frame(local[ref],rt),(0,y+40));canvas.paste(frame(movie,nt),(640,y+40));d.text((12,y+398),f'{ref}参考 {rt:.2f}s',font=small,fill='#d2c4e8')
canvas.save(ROOT/'evidence/六组参考对照.jpg',quality=91)
print(json.dumps({'frames':len(frames),'duration':info['format']['duration'],'masterSamples':len(master),'aacSamples':len(audio),'audioCorrelation':correlation,'unexpectedNearBlack':unexpected},ensure_ascii=False))
