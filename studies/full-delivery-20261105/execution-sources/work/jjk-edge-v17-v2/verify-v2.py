from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,hashlib,io
import numpy as np
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parents[2]
ROOT=BASE/'outputs/jjk-edge-v17-v2';HF=ROOT/'hyperframes'
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';FP='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'
MOV=ROOT/'挚友_EDGE_精修V2.mp4';V1=BASE/'outputs/jjk-edge-v17/挚友_EDGE_一分钟.mp4'
def run(a):return subprocess.run(a,capture_output=True,check=True)
def pcm(file):return np.frombuffer(run([FF,'-v','error','-i',str(file),'-vn','-ac','2','-ar','48000','-f','f32le','pipe:1']).stdout,dtype='<f4').reshape(-1,2)
def pictures():return np.frombuffer(run([FF,'-v','error','-i',str(MOV),'-an','-vf','scale=192:108','-pix_fmt','rgb24','-f','rawvideo','pipe:1']).stdout,dtype=np.uint8).reshape(-1,108,192,3)
with ThreadPoolExecutor(max_workers=3) as p:
    jobs=[p.submit(pcm,MOV),p.submit(pcm,HF/'assets/audio/master.wav'),p.submit(pictures)]
    audio,master,frames=[j.result() for j in jobs]
assert len(frames)==1440 and len(master)==2880000 and len(audio)==2880000
corr=float(np.corrcoef(audio.reshape(-1),master.reshape(-1))[0,1]);assert corr>.995
dark=np.where(frames[:,11:98].mean((1,2,3))<10)[0].tolist()
unexpected=[f for f in dark if not (384<=f<433 or f>=1416)]
assert not unexpected,unexpected
edit=json.loads((HF/'edit.json').read_text(encoding='utf-8'))
assert len(edit['shots'])==67 and edit['shots'][0]['startFrame']==0
assert all(a['startFrame']+a['frames']==b['startFrame'] for a,b in zip(edit['shots'],edit['shots'][1:]))
assert edit['shots'][-1]['startFrame']+edit['shots'][-1]['frames']==1440
v1_sha=hashlib.sha256(V1.read_bytes()).hexdigest()
baseline=json.loads((ROOT/'evidence/V1基线与精修目标.json').read_text(encoding='utf-8'))
assert v1_sha==baseline['sha256'],'V1 master changed'
info=json.loads(run([FP,'-v','error','-show_streams','-show_format','-of','json',str(MOV)]).stdout)
loud=run([FF,'-hide_banner','-i',str(MOV),'-af','ebur128=peak=true','-f','null','-']).stderr.decode(errors='replace')
(ROOT/'evidence/声音响度实测.log').write_text(loud,encoding='utf-8')
report={'file':MOV.name,'sha256':hashlib.sha256(MOV.read_bytes()).hexdigest(),'bytes':MOV.stat().st_size,'framesDecoded':len(frames),'fps':24,'width':1920,'height':1080,'durationSeconds':float(info['format']['duration']),'masterSampleFrames':len(master),'aacDecodedSampleFrames':len(audio),'sameTimeAudioCorrelation':corr,'nearBlackFrames':dark,'unexpectedNearBlackFrames':unexpected,'timelineContinuous':True,'nativeShots':67,'layoutEvents':len(edit['layouts']),'foregroundEvents':len(edit['foregrounds']),'foregroundGroups':sorted({v['alpha'] for v in edit['foregrounds']}),'typeEvents':len(edit['typeEvents']),'sourceMusicSeconds':[147,207],'audioUnchangedFromV1':hashlib.sha256((HF/'assets/audio/master.wav').read_bytes()).digest()==hashlib.sha256((V1.parent/'hyperframes/assets/audio/master.wav').read_bytes()).digest(),'v1MovieSha256After':v1_sha,'auditoryListeningPerformed':False,'verificationScope':'完整1440帧192x108缩略解码、音频采样与对齐、67镜连续性；重点合成帧和衔接联系表人工查看。未对1440帧逐帧全分辨率人工验收。'}
(ROOT/'质量检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
def pic(file,f,w=640,h=360):
    b=run([FF,'-v','error','-ss',str(f/24),'-i',str(file),'-frames:v','1','-vf',f'scale={w}:{h}','-f','image2pipe','pipe:1']).stdout
    return Image.open(io.BytesIO(b)).convert('RGB')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
events=[(100,'4.17秒｜动态冷脸跨暖景'),(252,'10.50秒｜七叶展开接同源'),(460,'19.17秒｜能量撕边＋人物前景'),(630,'26.25秒｜窄缝展开双半脸'),(690,'28.75秒｜大字挤出＋动态遮挡'),(850,'35.42秒｜连续曲面大字＋术式手'),(980,'40.83秒｜夏油手势与黄色曲字'),(1110,'46.25秒｜环绕紫字＋多层人物')]
sheet=Image.new('RGB',(1280,len(events)*410),'#080b13');d=ImageDraw.Draw(sheet)
for i,(f,title) in enumerate(events):
    y=i*410;d.text((12,y+4),title,font=font,fill='#72c7ed');d.text((13,y+377),'V1',font=small,fill='white');d.text((653,y+377),'精修V2',font=small,fill='white')
    sheet.paste(pic(V1,f),(0,y+36));sheet.paste(pic(MOV,f),(640,y+36))
sheet.save(ROOT/'evidence/V1-V2八组对照.jpg',quality=92)
# Source-clock boundaries: the screenshots include both sides of each handoff.
boundaries=[('翻叶→受伤脸',[262,263,264,265]),('记忆窗→礼堂',[289,290,291,292]),('大掌→全画面',[781,782,783,784]),('电弧裂口→同源',[886,887,888,889])]
sheet=Image.new('RGB',(1280,len(boundaries)*232),'#080b13');d=ImageDraw.Draw(sheet)
for i,(title,fs) in enumerate(boundaries):
    y=i*232;d.text((12,y),title,font=small,fill='#72c7ed')
    for j,f in enumerate(fs):
        sheet.paste(pic(MOV,f,320,180),(j*320,y+25));d.text((j*320+8,y+207),f'F{f} · {f/24:.3f}s',font=small,fill='white')
sheet.save(ROOT/'evidence/四处衔接逐帧检查.jpg',quality=92)
pic(MOV,690,1280,720).save(ROOT/'封面.jpg',quality=92)
print(json.dumps({k:report[k] for k in ['framesDecoded','durationSeconds','aacDecodedSampleFrames','sameTimeAudioCorrelation','unexpectedNearBlackFrames','audioUnchangedFromV1']},ensure_ascii=False))
