from pathlib import Path
import subprocess,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
L=R/'loops/loop-02'; O=L/'reviewer-evidence'; O.mkdir(exist_ok=True)
v=L/'loop-02-composite-preview.mp4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cmd=['C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe','-v','error','-i',str(v),'-vf','select=not(mod(n\\,24)),scale=384:216','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1']
r=subprocess.run(cmd,capture_output=True,check=True)
a=np.frombuffer(r.stdout,np.uint8).reshape(-1,216,384,3)
assert len(a)==60,len(a)
pics=[]
for page in range(2):
    im=Image.new('RGB',(384*5,240*6),'#080e18');d=ImageDraw.Draw(im)
    for j in range(30):
        n=page*30+j;x=j%5*384;y=j//5*240
        im.paste(Image.fromarray(a[n]),(x,y));d.text((x+5,y+220),f'actual encoded MP4 F{n*24:04} / {n}.000s',fill='#8dd5ee')
    p=O/f'actual-video-{page+1:02}.jpg';im.save(p,quality=93);pics.append(p.relative_to(R).as_posix())
p=json.loads((R/'loops/loop-03/plan-proposal.json').read_text(encoding='utf-8-sig'))
inventory=json.loads((R/'data/source-inventory.json').read_text(encoding='utf-8-sig'))
inv=inventory['items'] if isinstance(inventory,dict) else inventory
byid={s.get('id',s.get('sourceId')):s for s in inv}
errors=[];rows=[]
for s in p['shots']:
    if s.get('kind')!='video':continue
    sid=s['sourceId'];ep=int(sid[-2:]);lo,hi=s['searchWindowSeconds']
    checks={'episode':s['episode']==ep,'sourcePath':Path(s['sourcePath']).stem==f'{ep:02}','windowContainsFormal':lo<=s['sourceInSeconds']<s['sourceOutSeconds']<=hi,'evidenceExists':(R/s['preflightEvidence']).exists()}
    if sid in byid:
        src=byid[sid];sp=src.get('path',src.get('sourcePath',src.get('absolutePath')))
        if sp:checks['inventoryPath']=Path(s['sourcePath'])==Path(sp)
    row={'shot':s['id'],'candidateId':s['candidateId'],'sourceId':sid,'episode':s['episode'],'checks':checks}
    rows.append(row)
    if not all(checks.values()):errors.append(row)
report={'reviewer':'/root/s1_design_auditor','actualL2VideoSha256':sha(v),'decodeCommand':cmd,'decodedPeriodicFrames':len(a),'contactSheets':{s:sha(R/s) for s in pics},'L3ProposalSha256':sha(R/'loops/loop-03/plan-proposal.json'),'proposalMetadataCheck':{'scope':'57 source shots episode/sourceId/file stem/containing search window/evidence path existence; no semantic re-certification','shotCount':len(rows),'errors':errors,'rows':rows}}
(O/'actual-video-and-proposal-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'actualPeriodicFrames':len(a),'videoSha256':sha(v),'proposalShotCount':len(rows),'proposalMetadataErrors':errors,'sheets':pics},ensure_ascii=False))
