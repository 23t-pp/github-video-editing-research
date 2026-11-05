"""Normalize actual metadata before immutable R4 capture; never edit it afterwards."""
from pathlib import Path
import json,hashlib,sys,copy
R=Path(__file__).resolve().parent.parent;H=R/'hyperframes';L=R/'loops/loop-04';B=R/'loops/loop-03'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((L/'prepared-review.json').read_text(encoding='utf-8'))['captureAuthorized']
assert not (L/'execution.json').exists(),'Preserve executed loop, make an explicit later revision'
assert sha(H/'render.py')=='135ba209d87df98d6dd0d7fb7196aac8a52f9c66ffb1e1629cf6c3148af81b9d'
p=json.loads((B/'plan.json').read_text(encoding='utf-8'));m=json.loads((R/'data/retrieved-assets-loop4.json').read_text(encoding='utf-8'));original_events=copy.deepcopy(p['events'])
p['designRevision']={k:p.pop(k) for k in ['events','loopDeliverables','mustResolveBeforeRender','observedDesignEvidence'] if k in p}
p['designRevision']['source']='data/edit-plan.json and signed loops1..3; historical intent only'
eye=next(e for e in p['layouts'] if e['id']=='paired-eyes');eye.update(end=830,endZoom=1,origin='T05/V17，真实preparedF12..25稳定眼相位；无冻结/插帧，830回基础微笑，842接前冲');eye['clips'][1]['transform']['y']+=10
strike=next(e for e in p['typeEvents'] if e['id']=='strike-type');strike.update(subtitle_x=430,subtitle_y=820)
s53=next(s for s in p['shots'] if s['id']=='S053');s53.update(frames=8,sourceOutSeconds=s53['sourceInSeconds']+8/24*s53['playbackRate'])
p['shots']=[s for s in p['shots'] if s['id'] not in ['S054','S055']]
inv={s['id']:s for s in json.loads((R/'data/source-inventory.json').read_text(encoding='utf-8'))['items']};onsets=json.loads((R/'music/onsets.json').read_text(encoding='utf-8'))['items']
for index,v in enumerate(m['items']):
 asset=v['asset'];assert sha(H/asset['asset'])==asset['sha256'];p['assets'].append(asset);st=v['outputStartFrame'];N=v['outputFrames'];peak={ 'T062':1295,'T091':1314,'T007':1346}[asset['id']];onidx=min(range(len(onsets)),key=lambda i:abs(onsets[i]['frame24']-st));on=onsets[onidx]
 shot={'id':f'R4A{index+1:02}','kind':'video','candidateId':v['candidateId'],'sourceId':v['sourceId'],'sourcePath':v['sourcePath'],'episode':v['episode'],'startFrame':st,'frames':N,'sourceInSeconds':v['sourceCoreSeconds'][0],'sourceOutSeconds':v['sourceCoreSeconds'][1],'playbackRate':v['nominalCoreWindowRate'],'effectiveNativeFirstLastPtsRate':v['effectiveFirstLastPtsRate'],'searchWindowSeconds':v['sourceCoreSeconds'],'exactNativeCutBoundaryStatus':'65native full-frame core inspected;70prepared independent material gate pass; per-output actual PTS mapping explicit','focus':v['observedMovement'],'characters':v['characters'],'characterConfidence':v['characterConfidence'],'sourceVFX':'original anime motion/energy, not newly authored CG','preflightEvidence':v['evidence']['allNativeContactSheet'],'motionEvidence':'data/tail-action-candidates.json','sourceSampleMappingEvidence':f'evidence/tail-retrieval/{asset["id"]}.json','assetId':asset['id'],'asset':asset['asset'],'assetStartFrame':0,'cameraLocked':True,'reframe':{'scale':1,'x':0,'y':0},'punch':0,'rotation':0,'actionPeak':{'frame':peak,'basis':'prepared all-frame contact observation; fist/shoulder change, energy size onset, environment wave rise respectively; not an auditory beat claim'},'beatId':f'ONSET-{onidx:03}','beatCandidate':{'seconds':on['seconds'],'frame24':on['frame24'],'cutDeltaFrames':st-on['frame24'],'peakDeltaFromThisCutCandidateFrames':peak-on['frame24'],'status':'spectral onset candidate, not aurally confirmed; cut and action peak are separate'},'cropping':{'original':v['cropOriginal'],'padTop':v['padTop'],'loss':'lower136original rows/outer energy arc cropped; central swirl retained' if asset['id']=='T091' else 'lower120original rows cropped, plus common source-plane8px safety'}}
 p['shots'].append(shot)
p['shots'].sort(key=lambda s:s['startFrame']);assert p['shots'][0]['startFrame']==0
for a,b in zip(p['shots'],p['shots'][1:]):assert a['startFrame']+a['frames']==b['startFrame']
assert p['shots'][-1]['startFrame']+p['shots'][-1]['frames']==1440
for e in p['foregrounds']:
 e['techniqueIds']=['T07'];e['status']='frozen_input_execution_state_external'
 if e['id']=='yuji-runs-ahead':e['origin']='T07/V17，真实第一季动态alpha跨场景领先入场；不是T06形状门户，也不是同源handoff'
for e in p['layouts']:
 e['techniqueIds']={'weapon-triptych':['T04','T05'],'paired-eyes':['T05'],'palm-energy-paper':['T05','T07','T17'],'same-source-leaves':['T03'],'memory-windows':['T04']}[e['id']];e['status']='frozen_input_execution_state_external'
 if e['id']=='palm-energy-paper':e['origin']='T05/T07/T17，N054侧脸RGB在裂条，XPALM同号动态RGBA在条前；92段纤维与附着电弧边，原创组合'
for e in p['typeEvents']:e.update(techniqueIds=['T10'],status='frozen_input_execution_state_external')
events=[]
def add(stable,kind,binding,tech,refs,description,override=None):
 obj=next(e for e in p[kind] if e['id']==binding) if isinstance(p.get(kind),list) else p.get(kind)
 if override:obj=override
 clocks=[]
 for c in (obj or {}).get('clips',[]):clocks.append({'assetId':c['assetId'],'preparedFrameAtEventStart':c.get('offset',12)})
 if kind=='foregrounds':clocks=[{'assetId':obj['alpha'],'rgbaPattern':f'assets/alpha/{obj["alpha"]}/%06d.png','preparedFrameAtEventStart':obj['offset']}]
 if kind in ['native_match','tailActions']:
  clocks=[{'shotId':s['id'],'assetId':s['assetId'],'preparedStartFrame':s['assetStartFrame'],'outputRange':[s['startFrame'],s['startFrame']+s['frames']]} for s in p['shots'] if s['startFrame']<obj['end'] and s['startFrame']+s['frames']>obj['start']-1]
 if kind=='archiveScreen':clocks=[{'shotId':s['id'],'assetId':s['assetId'],'preparedStartFrame':s['assetStartFrame']} for s in p['shots'] if s['startFrame']<obj['end'] and s['startFrame']+s['frames']>obj['start']]
 event={'id':stable,'kind':kind,'actualBinding':binding or kind,'start':obj['start'],'end':obj['end'],'techniqueIds':tech,'referenceIds':refs,'description':description,'mediaClocks':clocks,'status':'frozen_input_execution_state_external','executionEvidence':'loops/loop-04/execution.json','independentReviewEvidence':'loops/loop-04/review.json'};events.append(event)
add('opening-slam','typeEvents','opening-slam',['T10'],['V02'],'连续轮廓与九层厚度原创主标题，中文独立成行')
add('palm-match-a','native_match',None,['T01'],['V20'],'裸切掌心焦点接力，宏观手势裁切取舍已披露',{'start':13,'end':31})
add('palm-match-b','native_match',None,['T01'],['V20'],'掌心落点延续至第三镜，效果不能替代焦点匹配',{'start':31,'end':45})
add('archive-screen','archiveScreen',None,['T13'],['V20'],'原创档案监视器外壳保持，真实内片切换；不冒称跟踪动画实体手机')
add('triptych-weapon','layouts','weapon-triptych',['T04','T05'],['V16','V13'],'独立动态卡片三联，实际24帧，不沿用旧51帧意图')
add('palm-early','foregrounds','palm-before-weapon',['T07'],['V17'],'青掌真动态RGBA在漫画字前，右袖保持出画')
add('strike-type','typeEvents','strike-type',['T10'],['V02'],'上方英文、左下中文、下方青掌，完整阅读窗口待新片验收')
add('eyes-slit','layouts','paired-eyes',['T05'],['V17'],'前14帧真实稳定眼相位，蓝侧+10；830回基础微笑、842接动作')
add('energy-edge','layouts','palm-energy-paper',['T05','T07','T17'],['V17','V11'],'裂条实际N054侧脸，另有XPALM前景与附着纤维电弧；不是空黑手RGB条')
events[-1]['mediaClocks'].append({'assetId':'XPALM','rgbaPattern':'assets/alpha/XPALM/%06d.png','preparedFrameAtEventStart':2,'zOrder':'foreground over N054 strip'})
add('leaves-to-technique','layouts','same-source-leaves',['T03'],['V05'],'同源7叶共钟F0..11，1071起全归位，1074接F12')
add('limitless-type','typeEvents','limitless-type',['T10'],['V02'],'右上天空柱面轮廓字，给五条合掌让位')
add('clap-match','native_match',None,['T01'],['V20'],'手指/合掌动作组织，字幕不盖学习主体',{'start':1126,'end':1178})
add('return-windows','layouts','memory-windows',['T04'],['V13'],'小窗记忆片回收，独立于主线重复统计')
add('final-title','tailcard',None,['T18'],['V20'],'原创小字尾卡与最后12帧渐黑，非大字替代动作收尾')
add('yuji-runs-ahead','foregrounds','yuji-runs-ahead',['T07'],['V17'],'真实跑动上半身跨场景入场，腰线贴底；不称门户或同源连续handoff')
add('tail-action-release','tailActions',None,['T01','T16'],['V20'],'8f眼神→真换拳/扭肩→原生红钉旋转→环境冲击浪→真实奔跑；原CG不冒称本轮制作',{'start':1282,'end':1360})
p['events']=events
p['loopDeliverables']=[{'loop':n,'artifact':f'loops/loop-{n:02}/'+{1:'loop-01-rough-focus-v2.mp4',2:'loop-02-composite-preview.mp4',3:'loop-03-high-quality.mp4',4:'loop-04-final.mp4'}[n],'execution':f'loops/loop-{n:02}/execution.json','review':f'loops/loop-{n:02}/review.json','stateSource':'external actual execution/review files, no status inferred from intent'} for n in [1,2,3,4]]
p['imageProcessing']={'color':'BT709 SDR; capture RGB full, encode709 limited','defaultPrepared':'crop original1920x960 y0..959, padTop60','T091Prepared':'crop original1920x944 y0..943, padTop68; lower136 rows lost, central energy preserved','sourcePlaneSafety':'clip y68..1012','foregroundParentSafety':'clip y60..1020','dimensionsPreserved':True}
p['structure']=[{'frames':[0,168],'name':'掌心/武器/腾空接力'},{'frames':[168,176],'name':'明确停顿'},{'frames':[176,312],'name':'档案屏内角色换片'},{'frames':[312,714],'name':'手势/武器群像与漫画字'},{'frames':[714,1048],'name':'冲击/眼缝/人物裂条'},{'frames':[1048,1282],'name':'同源七叶、合掌与记忆小窗'},{'frames':[1282,1386],'name':'短眼神、近战、能量、冲击浪与奔跑前景'},{'frames':[1386,1440],'name':'橙眼与紫色能量收束/小字尾卡'}]
p['nativeTexts']=[{'id':t['id'],'text':t.get('subtitle',''),'startFrame':t['start'],'frames':t['end']-t['start'],'fontSize':31,'x':t.get('subtitle_x',960),'y':t.get('subtitle_y',947),'color':'#fff7de','fontWeight':900,'align':'center'} for t in p['typeEvents']]+[{'id':'tail','text':'咒力接力','startFrame':1416,'frames':24,'fontSize':36,'color':'#fff7de','fontWeight':900,'align':'center'}]
needed={s['assetId'] for s in p['shots']}
for group in ['layouts','visuals']:
 for e in p.get(group,[]):needed.update(c['assetId'] for c in e.get('clips',[]))
needed.update(e['alpha'] for e in p['foregrounds']);p['assets']=[a for a in p['assets'] if a['id'] in needed]
p.update(version='L4-F-actual-binding-final-input',revision='L4-F',status='frozen_input_execution_and_review_state_external',executionStateSource='loops/loop-04/execution.json',reviewStateSource='loops/loop-04/review.json',actualSourceEvidence=['data/retrieved-assets.json','data/retrieved-assets-loop2-final.json','data/retrieved-assets-loop4.json','loops/loop-04/prepared-review.json'])
target=L/'plan.json';target.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8');(H/'edit.json').write_bytes(target.read_bytes())
sys.path.insert(0,str(H));from composition import build,save_editable
hashes={str(i):hashlib.sha256(build(p,i*72,(i+1)*72,True)[0].encode()).hexdigest() for i in range(20)};base=json.loads((B/'frozen.json').read_text(encoding='utf-8'));changed=[i for i in range(20) if hashes[str(i)]!=base['chunkHtmlSha256'][str(i)]];assert changed==[8,11,17,18],changed
codes={n:sha(H/n) for n in ['composition.py','typefx.py','layoutfx.py','screenfx.py','barlow-glyphs.json','render.py']};(L/'code').mkdir(exist_ok=True)
for n in codes:(L/'code'/n).write_bytes((H/n).read_bytes())
frozen={'plan':'loops/loop-04/plan.json','planSha256':sha(target),'allowedChunks':list(range(20)),'newChunks':changed,'unchangedChunks':[i for i in range(20) if i not in changed],'chunkHtmlSha256':hashes,'codeHashes':codes,'preparedReviewSha256':sha(L/'prepared-review.json'),'baseVideoSha256':'4f43ad583e57d0cd454cd660f8f67fa96be590c17bd6b42d52959bb935aa125b','status':'frozen R4 input; independent final-plan precheck then actual capture/review required'}
(L/'frozen.json').write_text(json.dumps(frozen,ensure_ascii=False,indent=2),encoding='utf-8');save_editable(build(p)[0])
index={'plan':'loops/loop-04/plan.json','planSha256':sha(target),'eventCount':len(events),'scope':'16 actual bindings, state read from external execution/review; original14 stable IDs plusXCHASE and tail group','events':events};(R/'data/final-event-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8');(L/'final-event-index.json').write_bytes((R/'data/final-event-index.json').read_bytes())
d={'from':'loops/loop-03/plan.json','inputIndependentReviewSha256':sha(B/'review.json'),'changes':[{'findingId':'L2-EYE-01','change':'真实眼相位缩816..830，蓝+10，endZoom1；830回微笑12f→842蓄势，待全事件像素审'},{'findingId':'L3-CN-TYPE-09','change':'STRIKE中文改x430/y820，留左下空白；待26f真实阅读审'},{'findingId':'L3-PACING-10','change':'原78f凝视组改8f眼+22f真换拳+24f红钉+24f冲击浪；65native→70output映射公开，主体位移由原动画提供'},{'findingId':'L3-EVENTS-11','change':'actual events16/技法ID/媒体时钟/真实loop路径规范；旧意图移designRevision；不在捕获后改计划状态字节'}],'changedChunks':changed,'sourceMaterialsGate':'loops/loop-04/prepared-review.json','pending':['frozen plan independent consistency precheck','actual4changed capture+16payload rebind','1080 full encode','independent final artistic/technical review']};(L/'revision-diff.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'planSha256':sha(target),'changedChunks':changed,'unchanged16':frozen['unchangedChunks'],'shots':len(p['shots']),'assets':len(p['assets']),'actualEvents':len(events)},ensure_ascii=False))
