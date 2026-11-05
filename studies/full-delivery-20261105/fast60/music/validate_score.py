"""Signal/file validation, not a claim of hearing or artistic approval."""
from pathlib import Path
import json,hashlib,struct
import numpy as np
from scipy import signal
import soundfile as sf
R=Path(__file__).resolve().parent
p=R.parent/'hyperframes/assets/audio/score.wav'
x,sr=sf.read(p,dtype='float32',always_2d=True)
markers=json.loads((R/'beat-markers.json').read_text(encoding='utf-8'))
mono=x.mean(axis=1);hop=240;frame=1024
_,tt,z=signal.stft(mono,sr,nperseg=frame,noverlap=frame-hop,boundary=None,padded=False)
mag=np.abs(z);flux=np.maximum(np.diff(np.log1p(mag*80),axis=1),0).mean(axis=0)
ft=tt[1:];threshold=np.median(flux)+np.std(flux)*.35
peaks,properties=signal.find_peaks(flux,height=threshold,distance=round(.065*sr/hop),prominence=np.std(flux)*.15)
onsets=[]
for i in peaks:
    t=float(ft[i]);near=min(markers['events'],key=lambda e:abs(e['time_sec']-t))
    onsets.append({'time_sec':round(t,6),'spectral_flux':round(float(flux[i]),6),'nearest_composed_event':near['instrument'],'nearest_event_time_sec':near['time_sec'],'offset_ms':round((t-near['time_sec'])*1000,3)})
sections=[]
for s in markers['sections']:
    w=x[round(s['start']*sr):round(s['end']*sr)]
    sections.append({**s,'rms_dbfs':round(float(20*np.log10(np.sqrt(np.mean(w*w))+1e-12)),2),'sample_peak_dbfs':round(float(20*np.log10(np.max(np.abs(w))+1e-12)),2)})
kick_attacks=[]
drums,dsr=sf.read(R/'stems/drums.wav',dtype='float32',always_2d=True)
for e in markers['events']:
    if e['instrument']!='kick':continue
    i=e['sample'];part=drums[i:i+round(.045*sr)];energy=np.mean(part*part,axis=1)
    sample=i+int(np.argmax(energy))
    kick_attacks.append({'scheduled_sec':e['time_sec'],'measured_drum_peak_sec':round(sample/sr,6),'offset_ms':round((sample-i)/sr*1000,3),'definition':'Maximum stereo sample energy in first 45ms of drum stem; may include simultaneous percussion.'})
# Read the standard MIDI structure and all event delta times to confirm the
# exported type-1 file is internally valid and reaches the 128-beat boundary.
b=(R/'night-relay-128.mid').read_bytes();fmt,ntracks,ppq=struct.unpack('>HHH',b[8:14]);offset=14;ends=[];messages=0
for _ in range(ntracks):
    assert b[offset:offset+4]==b'MTrk';n=struct.unpack('>I',b[offset+4:offset+8])[0];d=b[offset+8:offset+8+n];i=0;tick=0
    def vlq():
        global i
        value=0
        while True:
            z=d[i];i+=1;value=(value<<7)|(z&127)
            if not z&128:return value
    while i<len(d):
        tick+=vlq();status=d[i];i+=1
        if status==255:
            i+=1
            length=vlq()
            i+=length
        elif status&240 in [128,144]:i+=2;messages+=1
        else:raise ValueError('Unsupported MIDI status')
    ends.append(tick);offset+=8+n
passed=sr==48000 and x.shape==(2880000,2) and np.isfinite(x).all() and np.max(np.abs(x))<1 and abs(float(x[-1].max()))<1e-6 and max(ends)==128*ppq
report={'passed':bool(passed),'sample_rate':sr,'sample_frames':len(x),'channels':x.shape[1],'duration_sec':len(x)/sr,'pcm_subtype':sf.info(p).subtype,'finite_samples':bool(np.isfinite(x).all()),'sample_peak_dbfs':float(20*np.log10(np.max(np.abs(x)))),'last_sample_channels':x[-1].tolist(),'stereo_correlation':float(np.corrcoef(x[:,0],x[:,1])[0,1]),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'midi':{'format':fmt,'tracks':ntracks,'ppq':ppq,'note_messages':messages,'maximum_end_tick':max(ends),'duration_beats':max(ends)/ppq,'passed':True},'section_measurements':sections,'audible_onset_candidates':onsets,'kick_attack_measurements':kick_attacks,'method':{'onsets':'Positive log-STFT spectral flux, 1024 samples / 240-hop (5ms), separated by >=65ms. STFT timestamps are window centers and not sample-accurate attack starts.','kick':'Independent drum-stem waveform peak after each scheduled kick; musical grid is not inferred from these peaks.','listening':'Not listened to by the authoring agent. Signal QA cannot certify musical taste, timbre or the final interaction with engine/dialogue audio.'}}
(R/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':report['passed'],'frames':len(x),'onset_candidates':len(onsets),'kick_events':len(kick_attacks),'midi_notes':messages//2,'sections':sections},ensure_ascii=False))
assert passed
