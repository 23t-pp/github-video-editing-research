from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest();p=json.loads((R/'loops/loop-04/plan.json').read_text(encoding='utf-8'));shots={s['id']:s for s in p['shots']};rows=[]
for e in p['events']:
    for clock in e['mediaClocks']:
        if 'outputRange' not in clock:continue
        lo,hi=clock['outputRange'];a,b=e['start'],e['end'];inter=[max(lo,a),min(hi,b)]
        inside=inter[0]<inter[1];role='inside_event' if inside else ('context_before_event' if hi<=a else 'context_after_event')
        s=shots[clock['shotId']];assert [lo,hi]==[s['startFrame'],s['startFrame']+s['frames']] and clock['assetId']==s['assetId']
        rows.append({'eventId':e['id'],'eventRange':[a,b],'shotId':clock['shotId'],'assetId':clock['assetId'],'actualShotRange':[lo,hi],'contextOnly':not inside,'role':role,'actualInsideRange':inter if inside else None,'insideFrameCount':inter[1]-inter[0] if inside else 0,'preparedStartFrameOfShot':clock['preparedStartFrame']})
r={'reviewer':'/root/s1_design_auditor','reviewedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),'status':'pass_with_explicit_context_clarification','boundArtifacts':{'loops/loop-04/plan.json':sha('loops/loop-04/plan.json'),'data/final-event-index.json':sha('data/final-event-index.json')},'policy':'0-based, half-open intervals; touching endpoint has zero interior frames. A match-cut needs the outgoing-shot context to explain the last frame before a cut. Do not count that context as event interior or FX coverage.','rows':rows,'contextOnlyCount':sum(x['contextOnly'] for x in rows),'correction':'clap-match的S048实际1152..1178，属于事件内部；S046的1100..1126才是前镜context。','frozenInputsModified':False}
(R/'reviews/event-clock-boundary-check.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md='''# 事件时钟补注：前镜上下文不计事件占时

本补注不修改已冻结R4计划、捕获代码或最终索引。帧号从0开始，区间右端不包含；两个区间只接触边界，交集为0帧。

匹配剪辑需要看切口前一帧，所以mediaClocks会同时列出前镜。前镜用于说明动作/形状如何接上，不代表它在该事件时间里仍显示，也不应计入特效覆盖秒数。

|事件|只作前镜上下文|事件内实际镜头|
|---|---|---|
|palm-match-a [13,31)|S001 [0,13)|S002 [13,31)|
|palm-match-b [31,45)|S002 [13,31)|S003 [31,45)|
|clap-match [1126,1178)|S046 [1100,1126)|S047 [1126,1152)、S048 [1152,1178)|
|tail-action-release [1282,1360)|S052/N052 [1256,1282)|S053/N053 [1282,1290)、T062 [1290,1312)、T091 [1312,1336)、T007 [1336,1360)|

特别纠正一个疑点：S048并非1178才开始，它从1152开始，因此确实位于clap-match内部。真正只接触起点的是S046。

对卡片、alpha、七叶等没有outputRange的mediaClocks，preparedFrameAtEventStart是事件开始时取哪张媒体帧，需结合实际layouts/foregrounds运行时钟读取；不要把asset ID直接当同名主镜头ID。例如S053媒体可保留旧prepared供记忆窗使用，主镜头S053实际绑定的是另一个N053。

机器逐条核对了上述带outputRange的时钟与实际shot范围及asset ID，全部一致。完整role/contextOnly/actualInsideRange和输入SHA见event-clock-boundary-check.json。
'''
(R/'reviews/event-clock-boundary-check.md').write_text(md,encoding='utf-8');print(json.dumps({'rows':len(rows),'contextOnly':r['contextOnlyCount'],'errors':0},ensure_ascii=False))
