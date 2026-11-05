from pathlib import Path
import subprocess,numpy as np,json,hashlib,wave
ROOT=Path(__file__).resolve().parents[1];src=ROOT.parent/'reference-library-20261105/audio/music-candidates/V20__music-candidate.m4a';FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';out=ROOT/'music';out.mkdir(exist_ok=True)
x=np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(src),'-ac','2','-ar','48000','-f','f32le','pipe:1']),dtype='<f4').reshape(-1,2).copy();n=len(x);target=2880000;overlap=2*n-target;assert 0<overlap<n
u=np.linspace(0,np.pi/2,overlap)[:,None];y=np.concatenate([x[:-overlap],x[-overlap:]*np.cos(u)+x[:overlap]*np.sin(u),x[overlap:]])*10**(-3/20);assert len(y)==target
peak=np.max(np.abs(y));limiter=min(1,.97/peak);y*=limiter;y[:1920]*=np.linspace(0,1,1920)[:,None];y[-19200:]*=np.linspace(1,0,19200)[:,None]
with wave.open(str(out/'master.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes((np.clip(y,-1,1)*32767).astype('<i2').tobytes())
mono=y.mean(1);hop=480;win=2048;spec=np.array([np.abs(np.fft.rfft(mono[i:i+win]*np.hanning(win))) for i in range(0,len(mono)-win,hop)]);flux=np.maximum(0,np.diff(np.log1p(spec*10),axis=0)).mean(1);flux=np.r_[0,flux];power=np.array([np.sqrt(np.mean(mono[i:i+win]**2)+1e-12) for i in range(0,len(mono)-win,hop)]);score=flux/(np.max(flux)+1e-9)
candidates=[i for i in range(1,len(score)-1) if score[i]>=score[i-1] and score[i]>score[i+1] and score[i]>np.percentile(score,70)]
selected=[]
for i in sorted(candidates,key=lambda i:score[i],reverse=True):
    if all(abs(i-j)>=24 for j in selected):selected.append(i)
onsets=[{'seconds':i*.01,'frame24':round(i*.01*24),'strength':float(score[i]),'quantizationMs':(round(i*.01*24)/24-i*.01)*1000} for i in sorted(selected)]
(out/'onsets.json').write_text(json.dumps({'method':'10ms hop log spectral positive flux peaks, percentile70 threshold, minimum240ms separation; musical beat candidates not auditory-confirmed','fps':24,'items':onsets},ensure_ascii=False,indent=2),encoding='utf-8')
r={'source':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'sourceDecodedSamples48000':n,'sourceDecodedSeconds':n/48000,'outputSamples':len(y),'outputSeconds':60,'musicTitle':None,'libraryReference':'V20','adaptation':'same library phrase repeated twice, equal-power overlap, fixed gain and final fades','overlapSamples':overlap,'overlapSeconds':overlap/48000,'overlapOutputSeconds':[(n-overlap)/48000,n/48000],'fixedGainDb':-3,'additionalPeakScale':float(limiter),'auditoryListeningPerformed':False,'separationResidualReview':'music-candidate separation output; residual voices/effects and perceived phrase seam not confirmed by listening','frameBoundaryQuantizationSeconds':0,'onsetCount':len(onsets),'masterSha256':hashlib.sha256((out/'master.wav').read_bytes()).hexdigest()}
(out/'music-report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(r,ensure_ascii=False))
