"""Create the actual frame plan; locked incoming assets stay untouched."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/reference-replay-next/hyperframes'
existing=json.loads((OUT/'assets/shots/source.json').read_text(encoding='utf-8'))['assets']
assets=[]
for a in existing:
    assets.append({**a,'asset':'assets/shots/'+a['asset']})
new=[
('P01','04',5866.16,32,'布莱恩眼神'),
('P02','03',5780.24,29,'红色尾灯与夜间车聚'),
('P03','11',3930.613333,11,'氮气瓶细节'),
('P04','11',3931.576667,11,'转速表圆心'),
('P05','11',7110.143333,30,'黑车冲出金色爆炸'),
('P06','02',720.05,22,'蓝色霓虹车尾'),
('P07','04',5863.27,44,'起伏公路三车接力'),
('P08','03',5340.08,34,'双车山路灯带'),
('P10','11',3932.20,16,'跑车并排起步'),
('P11','08',6973.86,22,'车轮切开冰水'),
('P12','08',6976.98,26,'车辆迎面穿过冰水'),
('P13','08',4485.91,36,'黑车冲过施工架'),
('P14','04',5870.98,37,'女车手凝视前路'),
('P15','11',1710.085,9,'脚踩踏板'),
('P16','11',2249.78,24,'街角侧滑转弯'),
('P17','06',7309.21,26,'橙色跑车掠过人群'),
('P18','11',1889.583333,24,'金色火花掠过路面'),
('P19','11',2131.5,23,'低机位车轮冲过石阶'),
('P20','04',346.1,26,'悬崖油罐车横移'),
('P23','07',7066.14,40,'黑车从烟尘中迎面冲出'),
('BLACK',None,0,45,'末段黑底，承接真实手部前景')]
for id,film,sourceIn,frames,label in new:
    assets.append(dict(id=id,film=film,sourceIn=sourceIn,frames=frames,label=label,asset=f'assets/shots/{id}.mp4',assetStartFrame=12,width=1920,height=1080))
M={a['id']:a for a in assets}
cuts=[(0,16,'P01',0),(16,45,'P02',0),(45,56,'P03',0),(56,67,'P04',0),(67,97,'P05',0),(97,119,'P06',0),(119,162,'P07',0),(162,176,'B01-steering',9),(176,210,'P08',0),(210,218,'B02-wheel',17),(218,250,'P01',0),(250,256,'B03-switch',11),(256,267,'P03',0),(267,278,'P04',0),(278,294,'P10',0),(294,316,'P11',0),(316,342,'P12',0),(342,378,'P13',0),(378,415,'P14',0),(415,418,'B04-gear',10),(418,427,'P15',0),(427,451,'P16',0),(451,477,'P17',0),(477,501,'P18',0),(501,524,'P19',0),(524,550,'P20',0),(550,585,'P07',0),(585,617,'B05-aircar',7),(617,639,'P11',0),(639,674,'A06-sidewindow',0),(674,705,'P23',9),(705,750,'BLACK',0)]
shots=[]
for n,(s,e,id,skip) in enumerate(cuts):
    a=M[id]
    assert skip+e-s<=a['frames'],(id,skip+e-s,a['frames'])
    shots.append(dict(id=f'S{n+1:02}',assetId=id,asset=a['asset'],film=a['film'],sourceIn=a['sourceIn']+skip/25,startFrame=s,frames=e-s,assetStartFrame=12+skip,label=a.get('label',a.get('role'))))
effects=[
 dict(id='steering',kind='alpha',start=153,reveal=162,end=176,assetId='B01-steering',alpha='B01-steering',x=480,y=180,rotation=-18,scale=1.35),
 dict(id='wheel',kind='alpha',start=193,reveal=210,end=218,assetId='B02-wheel',alpha='B02-wheel',x=900,y=-300,rotation=-25,scale=1.4),
 dict(id='switch',kind='alpha',start=239,reveal=250,end=256,assetId='B03-switch',alpha='B03-switch',x=0,y=450,rotation=-12,scale=1.35),
 dict(id='gear',kind='alpha',start=405,reveal=415,end=418,assetId='B04-gear',alpha='B04-gear',x=-300,y=220,rotation=-32,scale=1.3),
 dict(id='aircar',kind='alpha',start=578,reveal=585,end=617,assetId='B05-aircar',alpha='B05-aircar',x=-500,y=100,rotation=-8,scale=4.5),
 dict(id='window',kind='portal',start=665,reveal=674,end=679,assetId='P23',outgoing='A06-sidewindow',outStart=639),
 dict(id='closing-hand',kind='ending',start=691,reveal=705,end=750,assetId='B04-gear',alpha='B04-gear')]
plan=dict(title='越界 · V07 动作接力复刻',reference='V07',width=1920,height=1080,activeRect=[0,140,1920,800],fps=25,durationFrames=750,audio={'master':'assets/audio/master.wav','libraryOriginal':'assets/audio/V07-library-original.m4a','durationSource':30.0001814059,'sampleRate':48000,'samples':1440000},assets=assets,shots=shots,effects=effects,notes=['原片不足25fps的转为25fps仅为交付采样，不使用光流补帧；参考V07原生25fps。','alpha先入与底图同源同帧；复杂合成参数在本文件和motion.json。'])
(OUT/'edit.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print('750 frames / 32 cuts / 7 effects. Timeline locked.')
