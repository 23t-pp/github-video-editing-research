from pathlib import Path
import subprocess,os,json,hashlib
import numpy as np
import soundfile as sf
from scipy import signal,ndimage
ROOT=Path(__file__).resolve().parent
LIB=ROOT.parents[2]/'outputs/reference-library-20261105'
FF=os.environ.get('FFMPEG_PATH',str(Path.home()/'Apps/ffmpeg/bin/ffmpeg.exe'))
SR=44100
def db(x):return 20*np.log10(np.maximum(x,1e-12))
def decode(p):
    r=subprocess.run([FF,'-nostdin','-v','error','-i',str(p),'-map','0:a:0','-ac','2','-ar',str(SR),'-f','f32le','pipe:1'],capture_output=True)
    assert r.returncode==0,r.stderr
    return np.frombuffer(r.stdout,dtype='<f4').reshape(-1,2).copy()
def loudness(p):
    r=subprocess.run([FF,'-nostdin','-hide_banner','-i',str(p),'-af','loudnorm=I=-16:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True)
    assert r.returncode==0
    text=r.stderr.decode(errors='replace');m,_=json.JSONDecoder().raw_decode(text[text.rfind('{'):])
    return {'integrated_lufs':float(m['input_i']),'true_peak_dbtp':float(m['input_tp']),'lra_lu':float(m['input_lra'])}
paths={'candidate':LIB/'audio/music-candidates/V07__music-candidate.m4a','mixed':LIB/'audio/mixed/V07__mixed.m4a'}
audio={k:decode(p) for k,p in paths.items()}
results={}
features={}
for name,x in audio.items():
    mono=x.mean(axis=1);power=np.mean(x*x,axis=1)
    rms=np.sqrt(ndimage.uniform_filter1d(power,size=882,mode='constant'))
    active=np.flatnonzero(rms>10**(-55/20));active40=np.flatnonzero(rms>10**(-40/20));nz=np.flatnonzero(np.max(np.abs(x),axis=1)>1e-7)
    freqs,times,Z=signal.stft(mono,SR,nperseg=1024,noverlap=896,boundary=None,padded=False)
    mag=np.abs(Z);logmag=np.log1p(mag*50)
    flux=np.maximum(np.diff(logmag,axis=1),0).mean(axis=0);ft=times[1:]
    low=(freqs>=30)&(freqs<250);lf=np.maximum(np.diff(logmag[low],axis=1),0).mean(axis=0)
    strength=flux/(np.percentile(flux,95)+1e-12)
    peaks,_=signal.find_peaks(strength,height=.5,prominence=.20,distance=round(.12*SR/128))
    fast=np.sqrt(ndimage.uniform_filter1d(power,size=88,mode='constant'))
    rise=np.maximum(np.diff(fast,prepend=fast[0]),0)
    events=[]
    for i in peaks:
        center=int(round(ft[i]*SR));a=max(1,center-600);b=min(len(x),center+500)
        # Waveform-rise anchor is measured separately from the STFT center.
        anchor=a+int(np.argmax(rise[a:b]));end=min(len(x),anchor+int(.08*SR))
        v=x[anchor:end]
        events.append({'time_sec':round(anchor/SR,6),'sample_44100':anchor,'spectral_peak_time_sec':round(float(ft[i]),6),'flux_strength_p95_units':round(float(strength[i]),4),'low_flux':round(float(lf[i]),6),'next_80ms_rms_dbfs':round(float(db(np.sqrt(np.mean(v*v)))),2),'type':'onset candidate; waveform RMS-rise anchor, not a confirmed beat','output_frame_25fps':round(anchor/SR*25),'frame_time_sec':round(round(anchor/SR*25)/25,6),'frame_error_ms':round((round(anchor/SR*25)/25-anchor/SR)*1000,3)})
    blocks=[]
    for a in np.arange(0,len(x)/SR,.1):
        w=x[round(a*SR):min(len(x),round((a+.1)*SR))]
        if len(w):blocks.append({'start':round(float(a),3),'rms_dbfs':round(float(db(np.sqrt(np.mean(w*w)))),3),'peak_dbfs':round(float(db(np.max(abs(w)))),3)})
    bands=np.array([np.sqrt(np.mean(mag[(freqs>=lo)&(freqs<hi)]**2,axis=0)) for lo,hi in [(30,120),(120,500),(500,2000),(2000,6000),(6000,16000)]])
    # Broad statistics around 0.6 seconds each side, deliberately excluding
    # fast percussive subdivisions from structural-change candidates.
    feat=np.log(np.maximum(bands,1e-6));sm=ndimage.uniform_filter1d(feat,size=round(.4*SR/128),axis=1)
    lag=round(.6*SR/128);nov=np.linalg.norm(sm[:,2*lag:]-sm[:,:-2*lag],axis=0);nt=times[lag:-lag]
    npks,_=signal.find_peaks(nov,distance=round(1.8*SR/128),prominence=.4)
    changes=sorted([{'time_sec':round(float(nt[i]),4),'novelty':round(float(nov[i]),4)} for i in npks],key=lambda v:v['novelty'],reverse=True)[:10]
    changes.sort(key=lambda v:v['time_sec'])
    periodic=[]
    detrend=flux-ndimage.uniform_filter1d(flux,size=round(.8*SR/128));ac=signal.correlate(detrend,detrend,mode='full',method='fft')[len(detrend)-1:];ac/=ac[0]
    lo=round(.25*SR/128);hi=round(1.5*SR/128);pp,_=signal.find_peaks(ac[lo:hi])
    for i in sorted(pp+lo,key=lambda j:ac[j],reverse=True)[:5]:periodic.append({'period_sec':round(float(i*128/SR),6),'bpm_if_interpreted_as_beat':round(float(60/(i*128/SR)),3),'autocorrelation':round(float(ac[i]),4)})
    results[name]={'source':str(paths[name].relative_to(LIB)),'source_sha256':hashlib.sha256(paths[name].read_bytes()).hexdigest(),'sample_rate':SR,'channels':2,'decoded_sample_frames':len(x),'decoded_duration_sec':len(x)/SR,'nearest_25fps_frames':round(len(x)/SR*25),'quantized_video_duration_sec':round(len(x)/SR*25)/25,'audio_tail_outside_quantized_video_samples':len(x)-round(len(x)/SR*25)/25*SR,'sample_peak_dbfs':float(db(np.max(abs(x)))),'samples_above_full_scale_count':int(np.count_nonzero(np.abs(x)>1)),'active_above_minus55_dbfs':{'first_sample':int(active[0]),'last_sample_inclusive':int(active[-1]),'last_sec':float(active[-1]/SR),'trailing_sec':float((len(x)-1-active[-1])/SR),'method':'centered 20ms stereo RMS, -55dBFS'},'active_above_minus40_dbfs_last_sec':float(active40[-1]/SR),'last_nonzero_above_1e_minus7_sec':float(nz[-1]/SR),'onsets':events,'structural_change_candidates':changes,'periodicity_candidates':periodic,'rms_100ms':blocks}
    features[name]=(times,bands)
    # Audition copies only, level-matched by the previously measured LUFS.
    measured=-9.6 if name=='candidate' else -7.02
    gain_db=min(-16-measured,-1-float(db(np.max(abs(x)))))
    sf.write(ROOT/f'V07-{name}-audition-minus16.wav',x*10**(gain_db/20),SR,subtype='PCM_24')
    results[name]['audition_copy']={'file':f'V07-{name}-audition-minus16.wav','linear_gain_db':gain_db,'target_lufs_approx':-16,'no_time_stretch':True}
    results[name]['loudness']=loudness(paths[name])
    results[name]['audition_copy']['measured_loudness']=loudness(ROOT/f'V07-{name}-audition-minus16.wav')
common=min(len(audio['candidate']),len(audio['mixed']));a=audio['candidate'][:common];b=audio['mixed'][:common]
ratio=[]
for start in np.arange(0,29.4,.3):
    i=round(start*SR);j=min(common,i+round(.3*SR));ca=np.sqrt(np.mean(a[i:j]**2));mi=np.sqrt(np.mean(b[i:j]**2));ratio.append({'start':round(float(start),3),'end':round(float(start+.3),3),'mixed_minus_candidate_rms_db':round(float(db(mi)-db(ca)),2)})
out={'updated_scope':'Use original V07 library music duration. No extension, looping, new composition or 128-BPM retiming.','listened':False,'method_notes':['Decoded float32 native 44100Hz stereo; >0dBFS AAC decoded values are preserved for measurement.','Onset candidates are positive log-STFT changes refined by waveform RMS-rise; not downbeats or heard musical beats.','Structural changes are broad band-energy statistics, not heard verse/drop labels.','Nearest 25fps frame creates <=20ms event quantization; timestamps retain native-audio samples.'],'tracks':results,'mixed_minus_candidate_300ms_rms':ratio}
(ROOT/'analysis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
events=results['candidate']['onsets']
(ROOT/'candidate-onsets.csv').write_text('time_sec,sample_44100,frame_25fps,frame_time_sec,frame_error_ms,flux_strength_p95_units,next_80ms_rms_dbfs\n'+''.join(f"{e['time_sec']},{e['sample_44100']},{e['output_frame_25fps']},{e['frame_time_sec']},{e['frame_error_ms']},{e['flux_strength_p95_units']},{e['next_80ms_rms_dbfs']}\n" for e in events),encoding='utf-8')
# Standalone SVG for waveform envelope comparison; no external plotting dep.
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="600" viewBox="0 0 1500 600"><rect width="1500" height="600" fill="#101820"/>']
for row,name in enumerate(['candidate','mixed']):
    y0=65+row*250;parts.append(f'<text x="70" y="{y0-25}" fill="white" font-family="sans-serif" font-size="20">V07 {name}: 100ms RMS / onset candidates</text>')
    for sec in range(31):
        px=70+sec*45;parts.append(f'<path d="M {px} {y0} v 190" stroke="#263746"/><text x="{px}" y="{y0+210}" fill="#b6c5d1" font-size="12">{sec}s</text>')
    points=' '.join(f"{70+v['start']*45:.2f},{y0+190-min(190,max(0,(v['rms_dbfs']+55)*190/55)):.2f}" for v in results[name]['rms_100ms'])
    parts.append(f'<polyline points="{points}" fill="none" stroke="{("#64e0c4" if row==0 else "#ffb66b")}" stroke-width="2"/>')
    for ev in sorted(results[name]['onsets'],key=lambda v:v['flux_strength_p95_units'],reverse=True)[:24]:
        px=70+ev['time_sec']*45;parts.append(f'<path d="M {px} {y0} v 185" stroke="#c8b9ff" opacity=".5"/>')
parts.append('</svg>');(ROOT/'signal-overview.svg').write_text(''.join(parts),encoding='utf-8')
print(json.dumps({k:{'samples':v['decoded_sample_frames'],'duration':v['decoded_duration_sec'],'frame_count':v['nearest_25fps_frames'],'active_end':v['active_above_minus55_dbfs']['last_sec'],'periodicity':v['periodicity_candidates'],'changes':v['structural_change_candidates'],'strongest_onsets':sorted(v['onsets'],key=lambda e:e['flux_strength_p95_units'],reverse=True)[:15]} for k,v in results.items()}))
