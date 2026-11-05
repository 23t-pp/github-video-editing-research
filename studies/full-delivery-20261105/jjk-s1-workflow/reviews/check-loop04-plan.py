from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
R=Path(__file__).resolve().parents[1];L=R/'loops/loop-04';sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
p=json.loads((L/'plan.json').read_text(encoding='utf-8'));f=json.loads((L/'frozen.json').read_text(encoding='utf-8'));idx=json.loads((R/'data/final-event-index.json').read_text(encoding='utf-8'));inv={x['id']:x for x in json.loads((R/'data/source-inventory.json').read_text(encoding='utf-8'))['items']}
errors=[];pos=0;assets={a['id']:a for a in p['assets']};assetRows=[];sourceRows=[]
for a in p['assets']:
    rel='hyperframes/'+a['asset'];h=sha(rel);assetRows.append({'id':a['id'],'sha256':h,'declaredShaMatch':h==a['sha256']})
    if h!=a['sha256']:errors.append('assetSHA:'+a['id'])
for q in p['shots']:
    if q['startFrame']!=pos:errors.append('continuity:'+q['id'])
    pos+=q['frames']
    if q.get('kind')=='video':
        a=assets[q['assetId']];s=inv[q['sourceId']];lo,hi=q['searchWindowSeconds']
        ok=q['assetStartFrame']>=0 and q['assetStartFrame']+q['frames']<=a['frames'] and q['episode']==s['episodeNumber'] and Path(q['sourcePath'])==Path(s['localPath']) and lo<=q['sourceInSeconds']<q['sourceOutSeconds']<=hi and (R/q['preflightEvidence']).exists()
        sourceRows.append({'id':q['id'],'sourceId':q['sourceId'],'assetId':q['assetId'],'structuralPass':ok})
        if not ok:errors.append('shotSourceOrAsset:'+q['id'])
if pos!=1440:errors.append('end1440')
if len(set(q['id'] for q in p['shots']))!=len(p['shots']):errors.append('duplicateShotId')
if idx['planSha256']!=sha('loops/loop-04/plan.json') or idx['events']!=p['events']:errors.append('finalEventIndexPlan')
if len(p['events'])!=16 or len(set(e['id'] for e in p['events']))!=16:errors.append('eventCountOrId')
eventRows=[]
for e in p['events']:
    kind=e['kind'];binding=e['actualBinding'];matched=True
    if kind in ['layouts','foregrounds','typeEvents']:
        actual=[z for z in p[kind] if z['id']==binding];matched=len(actual)==1 and actual[0]['start']==e['start'] and actual[0]['end']==e['end']
    elif kind in ['archiveScreen','tailcard']:
        z=p[kind];matched=z['start']==e['start'] and z['end']==e['end']
    elif kind=='tailActions':matched=[q['startFrame'] for q in p['shots'] if q['id'] in ['S053','R4A01','R4A02','R4A03']]==[1282,1290,1312,1336]
    eventRows.append({'id':e['id'],'kind':kind,'actualBinding':binding,'range':[e['start'],e['end']],'structurePass':matched})
    if not matched:errors.append('eventBinding:'+e['id'])
eye=next(x for x in p['layouts'] if x['id']=='paired-eyes');cn=next(x for x in p['typeEvents'] if x['id']=='strike-type')
assert eye['end']==830 and eye['endZoom']==1 and cn['subtitle_x']==430 and cn['subtitle_y']==820
for name,h in f['codeHashes'].items():
    if sha('loops/loop-04/code/'+name)!=h:errors.append('code:'+name)
assert f['newChunks']==[8,11,17,18] and len(f['unchangedChunks'])==16
assert sha('loops/loop-04/prepared-review.json')==f['preparedReviewSha256']
assert not errors,errors
files=['loops/loop-04/plan.json','loops/loop-04/frozen.json','loops/loop-04/prepared-review.json','loops/loop-04/revision-spec.json','data/final-event-index.json']+['hyperframes/'+a['asset'] for a in p['assets']]+['loops/loop-04/code/'+k for k in f['codeHashes']]
r={'reviewer':'/root/s1_design_auditor','reviewedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),'status':'pass','reviewLevel':'frozen_R4_plan_structure_only','captureAuthorized':True,'approvedPlanSha256':sha('loops/loop-04/plan.json'),'finalApproval':False,'wholeFilmPass':False,'boundArtifacts':{x:sha(x) for x in files},'checks':{'shotCount':len(p['shots']),'sourceShots':len(sourceRows),'endFrame':pos,'uniqueShotIds':True,'preparedMediaCount':len(assetRows),'allDeclaredMediaShaMatch':True,'finalEvents':eventRows,'sourceRows':sourceRows,'eyeRange':[eye['start'],eye['end']],'ChineseAnchor':[cn['subtitle_x'],cn['subtitle_y']],'changedChunks':f['newChunks'],'unchangedChunks':f['unchangedChunks'],'frozenCodeHashesPass':True,'errors':errors},'scope':'允许此SHA正式捕获。16段复用仍须执行代理逐段重解码源PNG/HTML/环境/输出SHA严格绑定；本结构审未替代该执行证明，也未预签新像素。','remainingGate':'新完整R4视频与局部全帧实际图、切口邻帧、技术QA和工程验收；眼/中文/尾能量P1尚待成片关闭。'}
(L/'plan-precheck.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'pass','planSHA':r['approvedPlanSha256'],'shots':len(p['shots']),'sourceShots':len(sourceRows),'assets':len(assetRows),'events':len(eventRows),'errors':errors},ensure_ascii=False))
