from pathlib import Path
import json,csv
BASE=Path(__file__).resolve().parents[2];ROOT=BASE/'outputs/jjk-edge-v17-v2';HF=ROOT/'hyperframes'
e=json.loads((HF/'edit.json').read_text(encoding='utf-8'))
e['title']='挚友 · EDGE · 精修V2';e['revision']='V2'
for a in e['assets']:
    if a['id']=='C21':a['description']='红夕阳夏油全身远景（纠正V1人物标注）'
for s in e['shots']:
    if s['id']=='S11':s.update(assetId='C20',asset='assets/shots/C20.mp4',assetStartFrame=32,cameraLocked=True,punch=0,rotation=0)
    if s['id']=='S12':s.update(assetId='C54',asset='assets/shots/C54.mp4',assetStartFrame=24,cameraLocked=True,punch=0,rotation=0)
    if s['id']=='S35':s.update(cameraLocked=True,punch=0,rotation=0)
    if s['id']=='S38':s.update(cameraLocked=True,punch=0,rotation=0)
e['visuals']=[v for v in e['visuals'] if v['kind'] in ('black','lightning','lens','circle')]
def clip(a,offset=12,**kw):return dict(assetId=a,offset=offset,**kw)
e['layouts']=[
 {'id':'opening-depth','kind':'depth_windows','start':0,'end':36,'clips':[clip('C38'),clip('C20')],'slots':[{'x':-540,'y':20,'scale':.72,'rotation':-5,'blur':3},{'x':440,'y':120,'scale':.44,'rotation':7,'blur':.2}],'z':20,'origin':'原创延伸：受伤脸记忆的视差空间'},
 {'id':'friend-film','kind':'filmstrip','start':120,'end':156,'clips':[clip('C05'),clip('C03'),clip('C16')],'z':20,'origin':'原创延伸：双人关系错位三连片'},
 {'id':'warm-depth','kind':'depth_windows','start':180,'end':216,'clips':[clip('C16'),clip('C17')],'z':20,'origin':'V17冷暖关系层次的延伸'},
 {'id':'fold-to-hurt','kind':'ribbon_flip','start':244,'end':264,'clips':[clip('C20')],'handoff':True,'leaves':7,'z':30,'origin':'原创七叶展开，严格接C20同源帧32'},
 {'id':'hall-expand','kind':'window_expand','start':280,'end':292,'clips':[clip('C54')],'rect':[60,600,470,330],'toRect':[0,0,1920,1080],'revealStart':282,'revealEnd':291,'z':35,'origin':'V17矩形窗扩为新空间'},
 {'id':'knife-eye-depth','kind':'depth_windows','start':336,'end':360,'clips':[clip('C14'),clip('C46')],'slots':[{'x':-480,'y':120,'scale':.55,'rotation':-5,'blur':0},{'x':550,'y':-80,'scale':.44,'rotation':5,'blur':1}],'z':20,'origin':'原创刀刃与六眼双景深'},
 {'id':'energy-paper','kind':'tear_reveal','start':451,'end':480,'clips':[clip('C21',12,transform={'scale':2.2,'x':-179,'y':426})],'left':1080,'width':326,'top':172,'bottom':1080,'revealFrames':5,'drift':70,'z':30,'edgeFx':{'strength':1,'particles':14,'arcSpeed':17,'cyan':'#72c7ed','violet':'#b517c6'},'origin':'V17细人物条结构＋用户要求新增渲染燃边'},
 {'id':'eye-slit','kind':'slit_eyes','start':618,'end':648,'clips':[clip('C20',20,transform={'scale':1}),clip('C03',12,transform={'scale':2.6,'x':100,'y':-108})],'openFrames':9,'endZoom':1.10,'zoomFrames':4,'z':30,'origin':'V17窄缝展至双半脸，眼线手工对位'},
 {'id':'action-triptych','kind':'filmstrip','start':720,'end':744,'clips':[clip('C39'),clip('C43'),clip('C40')],'cards':[{'x':-610,'y':-70,'scale':.38,'rotation':-12},{'x':55,'y':30,'scale':.50,'rotation':3},{'x':680,'y':-90,'scale':.32,'rotation':12}],'z':25,'origin':'原创动作三连版面'},
 {'id':'blue-tear','kind':'tear_reveal','start':864,'end':888,'clips':[clip('C29',17)],'left':270,'width':780,'top':108,'bottom':972,'revealFrames':4,'expandStart':877,'expandEnd':887,'z':32,'edgeFx':{'strength':.8,'particles':10,'cyan':'#72c7ed','violet':'#b517c6'},'origin':'原创同源术式手势电弧裂口，末源帧40接下一帧41'},
 {'id':'geto-depth','kind':'depth_windows','start':984,'end':1020,'clips':[clip('C32'),clip('C33')],'slots':[{'x':450,'y':-110,'scale':.52,'rotation':6,'blur':0},{'x':-520,'y':160,'scale':.4,'rotation':-8,'blur':3}],'z':20,'origin':'原创人物前景与术式后景'},
 {'id':'gold-leaves','kind':'ribbon_flip','start':1056,'end':1080,'clips':[clip('C47')],'leaves':7,'z':25,'origin':'原创金色动作翻叶'},
 {'id':'purple-depth','kind':'depth_windows','start':1200,'end':1230,'clips':[clip('C51'),clip('C46')],'slots':[{'x':-480,'y':90,'scale':.53,'rotation':-5,'blur':0},{'x':570,'y':-120,'scale':.40,'rotation':8,'blur':1.5}],'z':20,'origin':'原创术式与六眼视差版式'},
 {'id':'final-actions','kind':'filmstrip','start':1248,'end':1272,'clips':[clip('C55'),clip('C48'),clip('C49')],'z':25,'origin':'原创三段动作记忆回钩'}
]
def fg(id,alpha,start,end,offset=12,**kw):return dict(id=id,alpha=alpha,start=start,end=end,offset=offset,z=60,**kw)
hurt=dict(scale=1.18,restX=410,restY=-70,x=180,y=20,inFrames=5,outFrames=4,clipActive=True,glow=2,echoes=[{'lag':3,'opacity':.16,'dx':-20,'dy':5}])
geto=dict(scale=1.5,restX=-500,restY=-80,x=-130,y=30,inFrames=5,outFrames=4,clipActive=True,glow=2)
e['foregrounds']=[
 fg('cold-face-over-warm','Y-hurt',79,127,**hurt),
 fg('geto-over-depth','Y-geto',156,192,**geto),
 fg('cold-return','Y-hurt',204,252,**hurt),
 fg('face-before-hall','Y-hurt',264,292,32,scale=1,x=0,y=0,inFrames=1,outFrames=4,clipActive=True,glow=0),
 fg('geto-crosses-hall','Y-geto',300,336,**geto),
 fg('paper-character','Y-stand',451,475,12,scale=2.2,restX=-179,restY=426,x=0,y=0,inFrames=1,outFrames=3,clipActive=False,glow=2),
 fg('geto-over-action','Y-geto',480,516,**geto),
 fg('awaken','X-awaken',669,717,12,x=-100,y=120,enterScale=1.1,scale=.95,glow=3,clipActive=False,inFrames=5,echoes=[{'lag':3,'opacity':.16,'dx':-26,'dy':7}]),
 fg('palm','X-palm',774,783,12,x=-120,y=120,enterScale=1.18,scale=1,inFrames=5,glow=1,clipActive=True),
 fg('blue-hit','Y-blue',849,857,12,scale=1,restX=170,restY=0,x=-150,y=70,inFrames=3,outFrames=2,glow=5,clipActive=True),
 fg('geto-memory-action','Y-geto',924,960,**geto),
 fg('geto-hand-hit','Y-getopalm',972,985,38,scale=1.1,restX=180,restY=-30,x=80,y=150,inFrames=3,outFrames=2,clipActive=True,glow=3),
 fg('geto-hero','Y-geto',990,1026,**geto),
 fg('awaken-purple','X-awaken',1080,1128,12,scale=.9,restX=270,restY=35,x=120,y=90,enterScale=1.08,inFrames=5,outFrames=4,glow=3,clipActive=False),
 fg('blue-last-hit','Y-blue',1256,1264,12,scale=1.08,restX=-100,restY=-30,x=160,y=120,inFrames=3,outFrames=2,glow=4,clipActive=True),
 fg('cold-final-memory','Y-hurt',1296,1332,24,**hurt)
]
e['typeEvents']=[
 {'id':'opening','mode':'slam','text':'THE STRONGEST','subtitle':'最强 · 五条悟','start':15,'end':48,'font_size':550,'width':1640,'x':960,'y':510,'color':'#fffaf0','stroke':'#080b13','depth':'#bb141a','font':'Barlow Condensed','z':45,'pulse':True},
 {'id':'bond','mode':'twin','text':['GOJO SATORU','GETO SUGURU'],'subtitle':'唯一 / 挚友','start':120,'end':156,'font_size':390,'width':1570,'y':525,'color':'#fffaf0','stroke':'#080b13','depth':'#72c7ed','font':'Barlow Condensed','z':45},
 {'id':'strongest','mode':'slam','text':'BEYOND','subtitle':'最强','start':432,'end':456,'font_size':570,'width':1610,'board':False,'color':'#fffaf0','stroke':'#080b13','depth':'#bb141a','font':'Barlow Condensed','z':45},
 {'id':'awake','mode':'twin','text':['THE STRONGEST','AWAKEN'],'subtitle':'最强 / 觉醒','start':669,'end':717,'font_size':450,'width':1620,'board':True,'color':'#34135f','stroke':'#f5f3f0','depth':'#b517c6','board_color':'#7bbbd4','edge_color':'#34135f','font':'Barlow Condensed','z':45},
 {'id':'limitless','mode':'cylinder','text':'NO LIMIT','subtitle':'无下限','start':840,'end':864,'font_size':560,'width':1620,'board':True,'color':'#34135f','stroke':'#f5f3f0','depth':'#b517c6','board_color':'#7bbbd4','edge_color':'#34135f','z':45},
 {'id':'geto','mode':'ribbon','text':'GETO SUGURU','subtitle':'夏油杰','start':966,'end':996,'font_size':560,'width':1610,'board':True,'color':'#080b13','stroke':'#b30918','depth':'#080b13','board_color':'#efb62e','edge_color':'#c61120','z':45},
 {'id':'purple','mode':'orbit','text':'PURPLE','subtitle':'茈','start':1098,'end':1134,'font_size':560,'width':1600,'board':True,'color':'#34135f','stroke':'#f5f3f0','depth':'#b517c6','board_color':'#7bbbd4','edge_color':'#34135f','z':45},
 {'id':'edge','mode':'cylinder','text':'EDGE','subtitle':'觉醒','start':1200,'end':1224,'font_size':560,'width':1580,'board':False,'color':'#fffaf0','stroke':'#34135f','depth':'#b517c6','z':45}
]
e['nativeTexts']=[{'id':t['id'],'text':t['subtitle'],'startFrame':t['start'],'frames':t['end']-t['start'],'fontSize':36,'color':'#fffaf0','fontWeight':900,'align':'center'} for t in e['typeEvents']]
e['artDirection']='用户最新要求：不局限V17/V02，效果与流畅度优先；更多动态抠像/版式；撕边带实际能量、纤维、电弧渲染。参考结构与原创延伸分别标注。'
(HF/'edit.json').write_text(json.dumps(e,ensure_ascii=False,indent=2),encoding='utf-8')
groups={k:sorted({f for v in e[k] for f in range(v['start'],v['end'])}) for k in ['layouts','foregrounds','typeEvents']}
union=sorted(set().union(*(set(v) for v in groups.values())))
report={'definition':'按有效事件帧并集统计；普通基础推拉与短闪光未计入。渲染后还需确认实际可见，不把声明时长等同验收。','declaredCoverage':{k:len(v)/24 for k,v in groups.items()},'combinedSeconds':len(union)/24,'combinedPercent':len(union)/1440*100,'foregroundGroups':sorted({v['alpha'] for v in e['foregrounds']}),'layouts':len(e['layouts']),'typeEvents':len(e['typeEvents']),'v1BaselineForegroundSeconds':(48+9)/24}
(ROOT/'evidence/附加层覆盖计划.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
with (HF/'镜头表.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['ID','素材','起始帧','结束帧不含','素材入帧','锁定几何']);w.writerows([[s['id'],s['assetId'],s['startFrame'],s['startFrame']+s['frames'],s['assetStartFrame'],s.get('cameraLocked',False)] for s in e['shots']])
print(json.dumps(report,ensure_ascii=False))
