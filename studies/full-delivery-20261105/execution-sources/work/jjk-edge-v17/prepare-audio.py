from pathlib import Path
import subprocess,json,hashlib,wave
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]/'outputs/jjk-edge-v17'
A=ROOT/'hyperframes/assets/audio';A.mkdir(parents=True,exist_ok=True)
R=ROOT/'hyperframes/audio-report';R.mkdir(parents=True,exist_ok=True)
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
source=Path('C:/Users/PC/Desktop/edge.mp3');start=147.0;duration=60;sr=48000
cmd=[FF,'-v','error','-ss',str(start),'-i',str(source),'-t',str(duration),'-ac','2','-ar',str(sr),'-f','f32le','pipe:1']
p=subprocess.run(cmd,capture_output=True,check=True);x=np.frombuffer(p.stdout,dtype='<f4').reshape(-1,2).copy()
assert len(x)==sr*duration,len(x)
gain=-3.0;fadein=.04;fadeout=.4
y=x*10**(gain/20);y[:round(sr*fadein)]*=np.linspace(0,1,round(sr*fadein))[:,None];y[-round(sr*fadeout):]*=np.linspace(1,0,round(sr*fadeout))[:,None]
assert abs(y).max()<1
pcm=np.round(np.clip(y,-1,1)*32767).astype('<i2').tobytes()
with wave.open(str(A/'master.wav'),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes(pcm)
(A/'edge-selected.wav').write_bytes((A/'master.wav').read_bytes())
mono=x.mean(1)[::3];rs=16000;hop=160;win=320
energy=np.array([np.sqrt(np.mean(mono[i:i+win]**2)+1e-15) for i in range(0,len(mono)-win,hop)])
flux=np.maximum(0,np.diff(np.log10(energy+1e-7),prepend=np.log10(energy[0]+1e-7)))
order=np.argsort(flux)[::-1];peaks=[]
for k in order:
    if flux[k]<.035:break
    if all(abs(int(k)-j)>=18 for j in peaks):peaks.append(int(k))
peaks.sort();events=[{'time':round(k*.01,4),'frame24':round(k*.01*24),'strength':round(float(flux[k]),5)} for k in peaks]
sec=[round(float(20*np.log10(np.sqrt(np.mean(x[i*sr:(i+1)*sr]**2))+1e-9)),2) for i in range(60)]
report={'sourceFile':'edge.mp3','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'selectedSourceStartSeconds':start,'selectedSourceEndSeconds':start+duration,'selectionReason':'选取中后段60秒：原片163秒附近低谷用于V17黑场/关系断裂，175秒附近能量提高用于觉醒高潮，202秒附近回落用于镜片收尾。依据能量与起音测量；未做听觉试听。','gainDb':gain,'fadeInSeconds':fadein,'fadeOutSeconds':fadeout,'sampleRate':sr,'channels':2,'sampleFrames':len(x),'durationSeconds':len(x)/sr,'musicSpeed':1,'rmsDbPerSecond':sec,'onsets':events,'command':cmd,'masterSha256':hashlib.sha256((A/'master.wav').read_bytes()).hexdigest(),'auditoryListeningPerformed':False}
(R/'selected-audio.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
im=Image.new('RGB',(1440,420),'#080b13');d=ImageDraw.Draw(im)
for s in range(0,61,5):
    px=40+s/60*1360;d.line((px,35,px,365),fill='#263044');d.text((px,380),str(s)+'s',fill='white')
for i,e in enumerate(energy):
    px=40+i/len(energy)*1360;level=min(1,float(e)/.5);d.line((px,205-level*160,px,205+level*160),fill='#8d79d9')
for s,label in [(16,'gap'),(28,'lift'),(55,'release')]:
    px=40+s/60*1360;d.line((px,25,px,365),fill='#eb4854',width=2);d.text((px+4,15),label,fill='#eb4854')
im.save(R/'music-window-waveform.png')
print(json.dumps({'selectedStart':start,'selectedEnd':start+duration,'samples':len(x),'onsetCount':len(events),'rmsPerSecond':sec},ensure_ascii=False))
