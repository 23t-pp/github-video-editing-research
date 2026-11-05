from pathlib import Path
from datetime import datetime,timezone
import subprocess,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];L=R/'loops/loop-03';O=L/'reviewer-evidence';O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
v=L/'loop-03-high-quality.mp4';before=sha(v)
ff='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
raw=subprocess.run([ff,'-v','error','-i',str(v),'-vf','scale=320:180','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],capture_output=True,check=True).stdout
a=np.frombuffer(raw,np.uint8).reshape(-1,180,320,3);assert len(a)==1440,len(a);assert sha(v)==before
p=json.loads((L/'plan.json').read_text(encoding='utf-8-sig'))
def contact(indices,out,cols=5):
    h=204;rows=(len(indices)+cols-1)//cols;im=Image.new('RGB',(320*cols,h*rows),'#070d17');d=ImageDraw.Draw(im)
    for j,f in enumerate(indices):
        x=j%cols*320;y=j//cols*h;im.paste(Image.fromarray(a[f]),(x,y));d.text((x+4,y+185),f'actual MP4 F{f:04} {f/24:.3f}s',fill='#97d9ee')
    im.save(O/out,quality=94)
for i in range(2):contact(list(range(i*720,(i+1)*720,24)),f'actual-film-{i+1:02}.jpg')
layouts=p.get('layouts',[]);types=p.get('typeEvents',[]);fore=p.get('foregrounds',[])
fx=layouts+types+fore
rows=[]
for s in p['shots']:
    start=s['startFrame'];end=start+s['frames'];ar=a[start:end,10:170].astype(np.float32)
    dif=np.abs(ar[1:]-ar[:-1]).mean(axis=(1,2,3))
    overlap=[e['id'] for e in fx if e['start']<end and e['end']>start]
    rows.append({'shot':s['id'],'range':[start,end],'seconds':s['frames']/24,'medianFrameMAD':float(np.median(dif)) if len(dif) else 0,'meanFrameMAD':float(np.mean(dif)) if len(dif) else 0,'nearHoldFractionMADbelow05':float((dif<0.5).mean()) if len(dif) else 1,'overlayIds':overlap,'sourceId':s.get('sourceId'),'focus':s.get('focus')})
ranked=sorted([s for s in rows if s['seconds']>=.75 and not s['overlayIds'] and s.get('sourceId')],key=lambda s:s['medianFrameMAD'])
chosen=ranked[:12];indices=[]
for s in chosen:
    lo,hi=s['range'];indices += [lo,(lo+hi-1)//2,hi-1]
contact(indices,'low-motion-candidates-first-mid-last.jpg',cols=3)
inv=json.loads((R/'data/source-inventory.json').read_text(encoding='utf-8-sig'))['items'];byid={i['id']:i for i in inv};errors=[]
for s in p['shots']:
    if s.get('kind')!='video':continue
    src=byid[s['sourceId']];lo,hi=s['searchWindowSeconds']
    if s['episode']!=src['episodeNumber'] or Path(s['sourcePath'])!=Path(src['localPath']) or not(lo<=s['sourceInSeconds']<s['sourceOutSeconds']<=hi) or not(R/s['preflightEvidence']).exists():errors.append(s['id'])
report={'reviewer':'/root/s1_design_auditor','videoSha256':before,'planSha256':sha(L/'plan.json'),'decodedThumbnailFrames':len(a),'thumbnailSize':[320,180],'motionCriteria':'RGB mean absolute frame difference inside y10:170, excluding shot boundaries; median and <0.5 fraction are technical hold candidates, never automatic aesthetic fail. Source animation holds can be intentional. Actual images must be viewed.','perShot':rows,'lowestNoOverlayShots':chosen,'metadataErrors':errors,'contacts':{q.relative_to(R).as_posix():sha(q) for q in O.glob('*.jpg')}}
(O/'actual-film-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'videoSha256':before,'frames':len(a),'metadataErrors':errors,'lowMotion':[{'shot':s['shot'],'range':s['range'],'median':s['medianFrameMAD'],'hold':s['nearHoldFractionMADbelow05']} for s in chosen]},ensure_ascii=False))
