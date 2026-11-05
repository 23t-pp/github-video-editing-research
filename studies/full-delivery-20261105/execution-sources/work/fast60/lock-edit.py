from pathlib import Path
import csv,json,math

project=Path('outputs/fast60/hyperframes')
# (film, source seconds, beats, image, source-sound level before mastering)
sequence=[
('03',5780.24,4,'夜间车聚，红色尾灯与人群',0),('11',3869.17,4,'起跑线前的脚步和车灯',0),('11',3929.25,2,'手指打开红色氮气开关',.22),('11',3930.613333,1,'氮气瓶响应开关',.22),('11',3931.576667,1,'转速表指针',.16),('11',3932.20,4,'彩色跑车并排射出',.34),
('06',7309.21,4,'橙色跑车冲过夜间人群',.32),('03',5340.08,2,'两车沿灯带山路并行',.25),('03',5349.021667,1,'漂移车尾收正',.31),('11',1710.085,1,'脚踩踏板',.15),('10',4684.37,4,'贴车门追拍，蓝车向前掠出',.32),('02',1611.08,2,'黄紫两台改装车横向掠过',.20),('11',2249.78,4,'街口转弯接到迎面公路',.31),('11',1949.70,2,'换挡手部动作',.23),('08',4485.91,4,'黑车擦过施工架，钢管倒下',.31),('04',5863.27,4,'三车穿过起伏公路',.26),('05',2737.10,4,'透过咖啡馆窗框看车驶过',0),
('09',2805.14,2,'静下来的拱形车库',0),('02',1613.19,4,'从黄色敞篷横摇至红色跑车',0),('05',7232.40,2,'人低下头轻轻笑',0),('04',5866.16,4,'布莱恩从挡风玻璃后看向前方',0),('11',6961.49,4,'驾驶者目光与三联窗口',0),
('07',7066.14,4,'黑车从烟尘和碎石中迎面冲出',.42),('05',6686.56,4,'腾起的车身落地，悬挂压低',.32),('11',6060.95,2,'车轮摩擦路面，烟尘升起',.35),('08',6973.86,2,'冰水中的轮胎，沿用上一镜圆形轮廓',.31),('08',6976.98,4,'车辆穿过冰水向镜头驶来',.31),('04',346.10,4,'油罐车沿悬崖公路横移',.27),('11',1889.583333,2,'车身擦过，火花落地',.37),('11',2131.50,2,'贴地车轮掠过石阶',.31),('11',7038.51,4,'双直升机与高速公路平行追逐',.32),('11',7037.39,2,'驾驶者抬眼看向侧面',0),('11',7099.586667,2,'孩子回头看向窗外',0),('11',7078.94,2,'牵引索从车身延伸到天空',.24),('11',7077.71,2,'仪表与握紧方向盘的手',.22),('11',7070.54,2,'俯视桥面，车辆与直升机对位',.30),('11',7049.81,2,'黑车迎向镜头，车头迅速变大',.35),('11',7097.52,4,'车辆跃起，在两架直升机之间悬空',.33),('11',7110.143333,4,'车辆逃出爆炸，火焰在车后追来',.40),
('07',7641.32,4,'两位驾驶者相视，夕阳下微笑',0),('07',7661.06,4,'递出钥匙，双人镜头停留',0),('07',7724.62,8,'金色山坡，两台车驶向不同方向',.045)]

def frame_at(beat):return math.floor(beat*24*60/128+.5)
sections=[(0,16,'起跑'),(16,48,'街途'),(48,64,'回忆与目光'),(64,112,'追逐'),(112,128,'分道')]
shots=[];assets=[];beat=0
for number,(film,source,beats,label,gain) in enumerate(sequence,1):
    sid=f'S{number:02}';start=frame_at(beat);end=frame_at(beat+beats)
    take={'id':sid,'film':film,'asset':f'assets/shots/{sid}.mp4','sourceIn':source,'frames':end-start,'assetStartFrame':12,'tailFrames':12,'label':label}
    if gain:take['cue']=f'assets/cues/{sid}.wav'
    assets.append(take)
    shots.append({**take,'beat':beat,'beats':beats,'startFrame':start,'sourceGain':gain,'section':next(name for a,b,name in sections if a<=beat<b)})
    beat+=beats
assert beat==128 and sum(s['frames'] for s in shots)==1440
trip=next(s for s in shots if s['label']=='驾驶者目光与三联窗口')
assets.append({'id':'P03','film':'04','asset':'assets/shots/P03.mp4','sourceIn':5870.98,'frames':35,'assetStartFrame':12,'tailFrames':12,'label':'三联右侧女性驾驶员'})
plan={'title':'弯心 / APEX','width':1920,'height':1080,'fps':24,'durationFrames':1440,'bpm':128,'sections':[{'name':name,'startFrame':frame_at(a),'endFrame':frame_at(b)} for a,b,name in sections],'assets':assets,'shots':shots,'effects':{'title':{'startFrame':7,'endFrame':75,'text':'弯心','latin':'APEX'},'triptych':{'startFrame':trip['startFrame'],'endFrame':trip['startFrame']+trip['frames'],'panels':[{'assetId':'S21','delay':0,'focusX':.61},{'assetId':'S22','delay':5,'focusX':.49},{'assetId':'P03','delay':10,'focusX':.39}]},'endFade':{'startFrame':1418,'endFrame':1440}},'audio':{'scoreMix':'assets/audio/score-mix.wav','sourceMix':'assets/audio/source-mix.wav','master':'assets/audio/master.wav'}}
(project/'edit.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
with (project/'镜头表.csv').open('w',newline='',encoding='utf-8-sig') as out:
    w=csv.writer(out);w.writerow(['镜号','段落','时间线入帧','时间线出帧（不含）','时间线入秒','时长秒','源文件编号','源入点秒','源出点秒','影像','素材内入帧','源声设计增益']);
    for s in shots:w.writerow([s['id'],s['section'],s['startFrame'],s['startFrame']+s['frames'],round(s['startFrame']/24,6),round(s['frames']/24,6),s['film'],s['sourceIn'],round(s['sourceIn']+s['frames']/24,6),s['label'],s['assetStartFrame'],s['sourceGain']])
print(f'{len(shots)} slots, {len(assets)} assets, {beat} beats, {frame_at(beat)} frames, triptych at {trip["startFrame"]}')
