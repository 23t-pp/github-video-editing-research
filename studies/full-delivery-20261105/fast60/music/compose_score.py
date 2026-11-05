"""Original deterministic 128 BPM / 32-bar score. Python + numpy/scipy/soundfile.
No samples, recordings, external compositions or neural model are used.
Run from any working directory; output paths are relative to this source file.
"""
from pathlib import Path
import json, math, struct, hashlib
import numpy as np
from scipy import signal
import soundfile as sf

ROOT=Path(__file__).resolve().parent
SR=48000; BPM=128; BEAT=60/BPM; BAR=4*BEAT; N=2880000
RNG=np.random.default_rng(1283205)
BUSES={k:np.zeros((N,2),np.float32) for k in ['drums','bass','synths','atmosphere']}
EVENTS=[]; MIDI=[]
def hz(note): return 440*2**((note-69)/12)
def filt(x, cutoff, kind='lowpass', order=2):
    return signal.sosfilt(signal.butter(order,cutoff,kind,fs=SR,output='sos'),x).astype(np.float32)
def envelope(n,attack=.003,decay=.14,sustain=.18,release=.06):
    t=np.arange(n)/SR; dur=n/SR
    e=np.minimum(t/max(attack,1/SR),1)*(sustain+(1-sustain)*np.exp(-np.maximum(t-attack,0)/decay))
    return (e*np.minimum(np.maximum(dur-t,0)/release,1)).astype(np.float32)
def add(bus,x,t,amp=1,pan=0,name='',note=None,beats=None,velocity=90):
    start=round(t*SR)
    if start>=N:return
    if x.ndim==1:
        theta=(pan+1)*np.pi/4; x=np.column_stack([x*np.cos(theta),x*np.sin(theta)])
    length=min(len(x),N-start)
    if start<0:return
    BUSES[bus][start:start+length]+=x[:length]*amp
    if name:EVENTS.append({'instrument':name,'time_sec':round(t,6),'sample':start,'amplitude':amp,'note':note})
    if note is not None:MIDI.append({'track':bus,'channel':9 if bus=='drums' else {'bass':0,'synths':1,'atmosphere':2}[bus], 'note':note,'beat':t/BEAT,'duration_beats':beats or .2,'velocity':velocity})
def tonal(note,duration,voice='lead',brightness=1):
    n=round(duration*SR);t=np.arange(n)/SR; f=hz(note)
    if voice=='bass':
        phase=2*np.pi*f*(t+.0004*(1-np.exp(-t/.03)))
        x=np.sin(phase)*.8
        for k in range(2,10):x+=np.sin(phase*k)*(.35/k)*np.exp(-k*.13/brightness)
        x=np.tanh(x*1.45)*envelope(n,.002,.11,.18,.045)
        return filt(x,1200*brightness)
    if voice=='lead':
        x=np.zeros(n)
        for k in range(1,15):
            weight=np.exp(-k/(2.4+2.4*brightness))/k
            x+=weight*(np.sin(2*np.pi*f*2**(-3/1200)*k*t)+np.sin(2*np.pi*f*2**(3/1200)*k*t+.13))*.5
        x+=.13*np.sin(2*np.pi*f*t+1.1*np.sin(2*np.pi*f*2*t)*np.exp(-t/.035))
        return np.tanh(x*1.4)*envelope(n,.003,.10,.1,.07)
    x=np.sin(2*np.pi*f*t+1.5*np.sin(2*np.pi*f*2*t)*np.exp(-t/.08))
    return x*envelope(n,.002,.07,.025,.05)
def kick():
    t=np.arange(round(.42*SR))/SR
    f=47+100*np.exp(-t/.018)+23*np.exp(-t/.075)
    x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/ .115)
    click=filt(RNG.standard_normal(len(t)),3800,'highpass')*np.exp(-t/.0025)*.18
    return np.tanh((x+click)*1.35)*np.minimum(t/.0007,1)
def snare():
    t=np.arange(round(.27*SR))/SR;noise=filt(RNG.standard_normal(len(t)),[1300,11000],'bandpass')
    body=(np.sin(2*np.pi*185*t)+.35*np.sin(2*np.pi*330*t))*np.exp(-t/.043)*.5
    clap=np.zeros(len(t))
    for off in [0,.012,.023]:clap+=np.exp(-np.maximum(t-off,0)/.045)*(t>=off)
    x=noise*(np.exp(-t/.075)*.43+clap*.11)+body
    return np.tanh(x*1.3)*np.minimum(t/.0008,1)*np.minimum((.27-t)/.025,1)
def hat(opened=False):
    dur=.25 if opened else .065;t=np.arange(round(dur*SR))/SR
    x=filt(RNG.standard_normal(len(t)),[6800,18000],'bandpass')
    metal=sum(np.sin(2*np.pi*f*t) for f in [7313,10313,11887])*.045
    return (x*.5+metal)*np.exp(-t/(.075 if opened else .017))*np.minimum(t/.0005,1)
def tom(note=43):
    t=np.arange(round(.33*SR))/SR;f=hz(note)*(1+.65*np.exp(-t/.025))
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/.085)*np.minimum(t/.001,1)
def impact(t,amp=.55):
    a=np.arange(round(1.3*SR))/SR
    noise=filt(RNG.standard_normal(len(a)),[1300,14000],'bandpass')*np.exp(-a/.28)*.18
    sub=np.sin(2*np.pi*(42*a+2*(1-np.exp(-a/.12))))*np.exp(-a/.25)*.65
    add('atmosphere',noise+sub,t,amp,name='section-impact')
def riser(t,dur,amp=.14):
    a=np.arange(round(dur*SR))/SR
    noise=filt(RNG.standard_normal(len(a)),[1600,13000],'bandpass')
    x=noise*(a/dur)**2*(.7+.3*np.sin(2*np.pi*(4*a+2*a*a/dur)))
    x+=np.sin(2*np.pi*(110*a+250*a*a/dur))*.06*(a/dur)**2
    add('atmosphere',x,t,amp,name='noise-riser')
def pad(notes,t,dur,amp=.12):
    n=round(dur*SR);a=np.arange(n)/SR;st=np.zeros((n,2))
    for note in notes:
        f=hz(note)
        for c,cents in enumerate([-7,7]):
            for k in [1,2,3,5]:st[:,c]+=np.sin(2*np.pi*f*2**(cents/1200)*k*a+.2*c)/k*np.exp(-k*.45)
    env=np.minimum(a/.35,1)*np.minimum((dur-a)/.6,1)
    st*=env[:,None]*(.9+.1*np.sin(2*np.pi*.25*a))[:,None]/len(notes)
    for c in [0,1]:st[:,c]=filt(filt(st[:,c],1800),180,'highpass')
    add('atmosphere',st,t,amp,name='minor-pad')
    for note_number in notes:MIDI.append({'track':'atmosphere','channel':2,'note':note_number,'beat':t/BEAT,'duration_beats':dur/BEAT,'velocity':45})
def note(bus,n,beat,length,amp,voice='lead',pan=0,brightness=1):
    add(bus,tonal(n,length*BEAT+.055,voice,brightness),beat*BEAT,amp,pan,name=voice,note=n,beats=length,velocity=min(120,int(65+amp*75)))

# Dark D-minor phrase: D–A–C–D / F–E–D–C–A. Relative intervals are
# reused over D, Bb, F and A, with a raised C# on the A turnaround.
motif=[(0,0,.50),(.75,7,.25),(1.5,10,.40),(2.5,12,.35),(3.25,7,.35),
       (4,15,.5),(4.75,14,.25),(5.5,12,.4),(6.25,10,.25),(7,7,.55)]
roots=[38,38,34,34,41,41,33,33]
kick_wave=kick();snare_wave=snare();ch=hat();oh=hat(True)
for bar in range(32):
    b=bar*4;start=b*BEAT
    intro=bar<4; street=4<=bar<12; danger=12<=bar<16; power=16<=bar<28; outro=bar>=28
    strongest=24<=bar<28
    if intro:level=[.18,.25,.42,.58][bar];root=38
    elif street:level=.78;root=roots[(bar-4)%8]
    elif danger:level=[.42,.3,.12,.38][bar-12];root=[34,33,33,33][bar-12]
    elif power:level=.92 if not strongest else 1.12;root=roots[(bar-16)%8]
    else:level=[.55,.38,.22,.65][bar-28];root=38
    # Long harmony layers are introduced at phrase boundaries, with an actual
    # open space around 27 seconds before the 30-second main entry.
    if bar in [0,2,4,6,8,10,12,16,18,20,22,24,26,28]:
        third=3 if root==38 else 4
        pad([root+12,root+12+third,root+19],start,3.7,.15 if power else .105)
    # Bass anticipations leave the kick transient separate, and avoid a wall
    # of continuous midrange during the strongest source-engine section.
    bass_pattern=[(.0,0,.42),( .75,0,.20),(1.5,0,.36),(2.25,12,.22),(2.75,0,.30),(3.5,7,.24)]
    if intro:bass_pattern=[] if bar==0 else [(0,0,.7),(2.5,0,.45)]
    if danger:bass_pattern=[(0,0,.7),(2,0,.4)] if bar<14 else ([(3.5,0,.23)] if bar==15 else [])
    if outro:bass_pattern=[(0,0,.65),(2,0,.35)] if bar<30 else ([(0,0,.7)] if bar==31 else [])
    for off,interval,length in bass_pattern:note('bass',root+interval,b+off,length,.42*level,'bass',brightness=.75 if intro else 1)
    # Main 2-bar melodic hook. Harmonic roots transpose the same recognizable
    # contour; bar 24 onwards adds selected octave replies, not a new tune.
    if bar%2==0 and bar not in [14,30]:
        leadroot=root+24
        for off,interval,length in motif:
            if intro and off not in [0,1.5,4,5.5]:continue
            if danger and off>2:continue
            if outro and off>4:continue
            n=leadroot+interval
            if root==33 and interval==15:n+=1
            note('synths',n,b+off,length,.175*level,'lead',pan=(-.16 if int(off*4)%2 else .16),brightness=.55 if intro else 1)
            if strongest and off in [1.5,4,6.25]:note('synths',n+12,b+off+.5,.22,.055,'bell',pan=.4)
    # Quiet interlocking eighths occupy the side field, with a deliberate hole
    # at 26.25–28.125 seconds and less coverage in the outro.
    if street or power or bar in [2,3,12,13,28]:
        arp=[0,7,12,10,7,3,7,10]
        for j,iv in enumerate(arp):
            if strongest and j in [2,6]:continue
            if root==33 and iv==3:iv=4
            note('synths',root+36+iv,b+j*.5+.25,.16,.035*level,'bell',pan=.55 if j%2 else -.55)
    if intro:kicks=[] if bar==0 else ([0] if bar<3 else [0,2.5])
    elif danger:kicks=[0,2.5] if bar<14 else ([3.5] if bar==15 else [])
    elif outro:kicks=[0,2] if bar<30 else ([0] if bar==31 else [])
    else:kicks=[0,1.5,2,2.75,3.5] if bar%2 else [0,1,2,3.25]
    for off in kicks:add('drums',kick_wave,(b+off)*BEAT,.73*max(level,.45),name='kick',note=36,beats=.2)
    if street or power:sn=[1,3]
    elif danger:sn=[2] if bar<14 else []
    elif intro:sn=[3] if bar==3 else []
    else:sn=[2] if bar==28 else []
    for off in sn:add('drums',snare_wave,(b+off)*BEAT,.34*level,name='snare-clap',note=38,beats=.2)
    if street or power or bar in [2,3,12,13,28,29]:
        step=.25 if strongest else .5
        for j,off in enumerate(np.arange(0,4,step)):
            # Humanized amplitude and tiny offbeat delay, not timing drift.
            delay=.008 if j%2 else 0
            amp=.065*level*(.6 if j%2 else 1)*(1+RNG.uniform(-.13,.13))
            add('drums',ch,(b+off)*BEAT+delay,amp,pan=.3 if j%2 else -.25,name='closed-hat',note=42,beats=.1)
        if not danger:
            for off in [1.5,3.5]:add('drums',oh,(b+off)*BEAT,.052*level,pan=.35,name='open-hat',note=46,beats=.25)
    if bar in [7,11,19,23,27]:
        for j,off in enumerate([3,3.25,3.5,3.75]):
            add('drums',tom(48-j*3),(b+off)*BEAT,.16+.025*j,pan=-.4+j*.26,name='tom-fill',note=48-j*3,beats=.2)
    if bar==15:
        for j,off in enumerate([2,2.5,3,3.25,3.5,3.75]):add('drums',snare_wave,(b+off)*BEAT,.06+j*.022,pan=0,name='build-snare',note=38,beats=.12)
    if bar in [4,16,24]:impact(start,.46 if bar!=16 else .64)
    if bar in [3,11,15,23]:riser(start,1.8,.07 if bar==3 else .12)

# The final one-bar hit has a low root and sparse fifth; its entire decay fits
# the last 1.875 seconds and fades before the exact 60-second boundary.
for n,a in [(38,.34),(50,.15),(57,.09)]:note('synths',n,124,1.7,a,'lead',brightness=.5)
impact(58.125,.44)

# Shared sidechain envelope: lower synth/bass for about 140 ms after each kick.
duck=np.ones(N,np.float32)
for e in EVENTS:
    if e['instrument']=='kick':
        i=e['sample'];length=min(round(.18*SR),N-i);t=np.arange(length)/SR
        duck[i:i+length]=np.minimum(duck[i:i+length],1-.44*np.exp(-t/.052))
BUSES['bass']*=duck[:,None];BUSES['synths']*=duck[:,None]
# Stereo dotted-eighth cross-delay with two quiet repeats; all tails are
# truncated only after they have been faded into the final silence.
dry=BUSES['synths'].copy()
for beats,amount in [(.75,.19),(1.5,.075)]:
    shift=round(beats*BEAT*SR)
    BUSES['synths'][shift:]+=dry[:-shift,::-1]*amount
# Broad midrange pocket for future source engines/dialogue; no full-band
# limiting pump. Low-frequency bass remains centered.
for bus in ['synths','atmosphere']:
    x=BUSES[bus]
    mid=(x[:,0]+x[:,1])*.5;side=(x[:,0]-x[:,1])*.5
    pocket=filt(mid,[650,2300],'bandpass')*.21
    mid-=pocket
    x[:,0]=mid+side;x[:,1]=mid-side
fade=np.ones(N,np.float32);fade[:480]=np.linspace(0,1,480)
fade[-24000:]=np.linspace(1,0,24000)**1.5
for key,x in BUSES.items():x*=fade[:,None]
master=sum(BUSES.values())
# Global peak-safe gain is shared by the stems, so summing them reproduces
# the premaster. Mastering true-peak/loudness is measured in master_score.mjs.
gain=min(.88/max(np.max(np.abs(master)),1e-9),1.5)
master*=gain
ROOT.mkdir(parents=True,exist_ok=True)
(ROOT/'stems').mkdir(exist_ok=True)
for key,x in BUSES.items():sf.write(ROOT/'stems'/f'{key}.wav',x*gain,SR,subtype='PCM_16')
sf.write(ROOT/'score-premaster.wav',master,SR,subtype='PCM_24')
sections=[(0,7.5,'夜间上车 / 启动'),(7.5,22.5,'街头主律动 / 加速'),(22.5,30,'危险 / 短抽空 / 回升'),(30,45,'高速主段'),(45,52.5,'最强段 / 引擎留白'),(52.5,58.125,'减法尾声'),(58.125,60,'有力尾音 / 收束')]
markers={'title':'NIGHT RELAY / 夜行接力','original_composition':True,'bpm':BPM,'time_signature':'4/4','bars':32,'sample_rate':SR,'sample_frames':N,'duration_sec':60,'timing_basis':'Deterministic composed score clock; not an inferred tempo from a mixed recording. Not every grid beat has an audible attack.','sections':[{'start':a,'end':b,'label':c} for a,b,c in sections], 'beats':[{'index':i,'bar':i//4+1,'beat_in_bar':i%4+1,'time_sec':i*BEAT,'sample':round(i*BEAT*SR)} for i in range(128)],'events':EVENTS}
(ROOT/'beat-markers.json').write_text(json.dumps(markers,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'beat-markers.csv').write_text('beat_index,bar,beat_in_bar,time_sec,sample\n'+''.join(f"{i},{i//4+1},{i%4+1},{i*BEAT:.6f},{round(i*BEAT*SR)}\n" for i in range(128)),encoding='utf-8')
(ROOT/'note-events.json').write_text(json.dumps(MIDI,ensure_ascii=False,indent=2),encoding='utf-8')
def vlq(n):
    b=[n&127];n>>=7
    while n:b.insert(0,(n&127)|128);n>>=7
    return bytes(b)
def chunk(data):return b'MTrk'+struct.pack('>I',len(data))+data
tracks=[];tempo=round(60000000/BPM)
meta=b'\x00\xff\x51\x03'+tempo.to_bytes(3,'big')+b'\x00\xff\x58\x04\x04\x02\x18\x08'
for start,end,label in sections:
    text=label.encode('utf-8');meta+=vlq(round(start/BEAT*960)-(round(sections[sections.index((start,end,label))-1][0]/BEAT*960) if start else 0))+b'\xff\x06'+vlq(len(text))+text
meta+=b'\x00\xff\x2f\x00';tracks.append(chunk(meta))
for track in BUSES:
    events=[];name=track.encode();data=b'\x00\xff\x03'+vlq(len(name))+name
    for e in MIDI:
        if e['track']!=track:continue
        tick=round(e['beat']*960);end=round((e['beat']+e['duration_beats'])*960);ch=e['channel']
        events.extend([(tick,1,bytes([0x90|ch,e['note'],e['velocity']])),(end,0,bytes([0x80|ch,e['note'],0]))])
    previous=0
    for tick,_,msg in sorted(events):data+=vlq(tick-previous)+msg;previous=tick
    data+=vlq(max(0,128*960-previous))+b'\xff\x2f\x00';tracks.append(chunk(data))
(ROOT/'night-relay-128.mid').write_bytes(b'MThd'+struct.pack('>IHHH',6,1,len(tracks),960)+b''.join(tracks))
print(json.dumps({'samples':len(master),'sample_rate':SR,'channels':2,'event_count':len(EVENTS),'notes':len(MIDI),'premaster_peak_dbfs':float(20*np.log10(np.max(np.abs(master)))),'shared_stem_gain':float(gain)}))
