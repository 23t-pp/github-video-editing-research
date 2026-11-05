"""Composition designer owns this plan; renderer consumes immutable snapshots."""
from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parent.parent;H=R/'hyperframes';L=R/'loops/loop-02';L.mkdir(parents=True,exist_ok=True)
p=json.loads((R/'loops/loop-01/hyperframes-edit.json').read_text(encoding='utf-8'));design=json.loads((R/'data/edit-plan.json').read_text(encoding='utf-8'))
assert json.loads((R/'loops/loop-01/review.json').read_text(encoding='utf-8'))['advanceToLoop2']
props=json.loads((R/'data/palm-focus-proposal.json').read_text(encoding='utf-8'))
for s in p['shots']:
 for m in props['measurements']:
  if s['id']==m['shot']:s['reframe']=m['transform']
 if s.get('candidateId')=='S1C038':s.update(characters=['三轮'],focus='三轮腾空跨步（纠正最初静帧人物标签）')
# Repoint Gojo's short pointing clip to the slightly earlier already-prepared variant.
s22=next(s for s in p['shots'] if s['id']=='S022');s53=next(s for s in p['shots'] if s['id']=='S053')
s22.update(assetId='S053',asset='assets/shots/S053.mp4',assetStartFrame=12,sourceInSeconds=s53['sourceInSeconds'],sourceOutSeconds=s53['sourceInSeconds']+s22['frames']/24*s53['playbackRate'],playbackRate=s53['playbackRate'])
report=json.loads((R/'evidence/alpha/XPALM-alpha-report.json').read_text(encoding='utf-8'))
movie=H/'assets/shots/XPALM.mp4';assert hashlib.sha256(movie.read_bytes()).hexdigest()==report['preparedSha256']
p['assets'].append({'id':'XPALM','asset':'assets/shots/XPALM.mp4','frames':31,'usableFrames':26,'sourcePath':'D:/咒术回战/1080P 内嵌简中字幕/05.mp4','sourceId':'S1E05','sourceIn':554.6,'sourceFps':'24000/1001','description':'第一季青掌，前景同号RGB用F2–27','sha256':report['preparedSha256']})
p['archiveScreen']={'id':'archive-screen','start':176,'end':312,'description':'original persistent archive monitor with changing source videos; no tracked anime phone claim'}
p['tailcard']={'start':1416,'end':1440,'text':'咒力接力'}
p['typeEvents']=[e.copy() for e in design['events'] if e['kind']=='type']
for t in p['typeEvents']:
 t['font']='Barlow Condensed'
 if t['id']=='opening-slam':t.update(y=180,font_size=220,width=1280,subtitle_y=345,stroke='#080b13')
 if t['id']=='limitless-type':t.update(x=1150,y=620,width=1400,font_size=410)
p['layouts']=[
 {'id':'weapon-triptych','kind':'filmstrip','start':561,'end':585,'clips':[{'assetId':'S025','offset':12},{'assetId':'S026','offset':12},{'assetId':'S028','offset':12}],'z':25,'origin':'T05/T04/V16/V13，动态武器三联，缩短到24帧避免延展源窗'},
 {'id':'paired-eyes','kind':'slit_eyes','start':816,'end':842,'clips':[{'assetId':'S009','offset':12,'transform':{'scale':1.2,'x':-720,'y':-30}},{'assetId':'S055','offset':12,'transform':{'scale':1.2,'x':680,'y':95}}],'openFrames':7,'endZoom':1.05,'zoomFrames':4,'z':30,'origin':'T05/V17，两只原生眼部手工对位，待真实捕获确认'},
 {'id':'palm-energy-paper','kind':'tear_reveal','start':970,'end':996,'clips':[{'assetId':'XPALM','offset':2}],'left':1120,'width':320,'top':100,'bottom':980,'revealFrames':4,'z':30,'edgeFx':{'strength':.8,'particles':12,'cyan':'#72c7ed','violet':'#b517c6'},'origin':'T07/T17/V17/V11细裂口与同源青掌RGBA'},
 {'id':'same-source-leaves','kind':'ribbon_flip','start':1062,'end':1074,'clips':[{'assetId':'S045','offset':0}],'leaves':7,'handoff':True,'z':30,'origin':'T03/V05 同源七叶，fileF0–11接基础S045 fileF12，14帧源余量已实际看'},
 {'id':'memory-windows','kind':'depth_windows','start':1256,'end':1282,'clips':[{'assetId':'S053','offset':12},{'assetId':'S031','offset':12}],'slots':[{'x':-500,'y':-50,'scale':.48,'rotation':-6,'blur':.3},{'x':570,'y':100,'scale':.38,'rotation':8,'blur':2}],'z':20,'origin':'T04/V13 有意复用角色记忆片，独立于主线源重叠统计'}
]
p['foregrounds']=[
 {'id':'palm-before-weapon','alpha':'XPALM','start':612,'end':638,'offset':2,'z':60,'scale':1.1,'restX':120,'restY':-70,'x':160,'y':70,'inFrames':4,'outFrames':4,'clipActive':True,'glow':2,'glowColor':'#72c7ed'},
 {'id':'palm-over-paper','alpha':'XPALM','start':970,'end':996,'offset':2,'z':60,'scale':1,'restX':0,'restY':-70,'x':80,'y':40,'inFrames':4,'outFrames':4,'clipActive':True,'glow':2,'glowColor':'#72c7ed'}
]
ons=json.loads((R/'music/onsets.json').read_text(encoding='utf-8'))['items'];p['flashes']=[]
for f in [13,57,336,714,1022,1204,1386]:
 b=min(ons,key=lambda q:abs(q['frame24']-f))
 if abs(b['frame24']-f)<=3:p['flashes'].append({'frame':b['frame24'],'width':2,'amount':.13,'onsetSeconds':b['seconds'],'claim':'measured onset candidate, no auditory confirmation'})
p['nativeTexts']=[{'id':t['id'],'text':t.get('subtitle',''),'startFrame':t['start'],'frames':t['end']-t['start'],'fontSize':36,'color':'#fff7de','fontWeight':900,'align':'center'} for t in p['typeEvents']]+[{'id':'tail','text':'咒力接力','startFrame':1416,'frames':24,'fontSize':36,'color':'#fff7de','fontWeight':900,'align':'center'}]
p['version']='L2-A-stable-early';p['revision']='L2-A';p['status']='early_frames_0_576_frozen_late_retrieval_pending';p['title']='咒力接力 · CURSED FLOW'
(H/'edit.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8');(L/'plan-early.json').write_bytes((H/'edit.json').read_bytes());(L/'plan.json').write_bytes((H/'edit.json').read_bytes())
sys.path.insert(0,str(H));from composition import build,save_editable
save_editable(build(p)[0])
codes={n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in ['composition.py','typefx.py','layoutfx.py','screenfx.py','barlow-glyphs.json']}
chunkhash={str(i):hashlib.sha256(build(p,i*72,(i+1)*72,True)[0].encode()).hexdigest() for i in range(8)}
(L/'frozen-early.json').write_text(json.dumps({'plan':'loops/loop-02/plan-early.json','planSha256':hashlib.sha256((L/'plan-early.json').read_bytes()).hexdigest(),'allowedChunks':list(range(8)),'codeHashes':codes,'chunkHtmlSha256':chunkhash,'lateMutableOnly':'F588 onward main replacements/XCHASE, no edits to early code or media'},ensure_ascii=False,indent=2),encoding='utf-8')
(L/'revision-diff.json').write_text(json.dumps({'from':'LOOP1 focus-v2','changes':[{'findingId':'L1-SUBTITLE','change':'source-plane clip-path y68..1012 hides only8px fringe beyond prepared y60..1020; media unchanged'},{'findingId':'L1-TITLE','change':'opening title moved to y180/220px, subtitle345; hand focus around1070,800 stays clear'},{'findingId':'L1-SOURCE-GLITCH','change':'S022 uses earlier same-candidate prepared S053 first24formal frames, moves out source horizontal displacement'},{'findingId':'L2-NEW','change':'persistent original monitor, actualXPALM, eye slit,energy paper,same-source7leaves,continuousglyph text'}],'pending':['fresh late main clips','XCHASE canonical freeze','actual effects capture review']},ensure_ascii=False,indent=2),encoding='utf-8')
print('Frozen early0..576; assets',len(p['assets']),'layouts',len(p['layouts']),'types',len(p['typeEvents']))
