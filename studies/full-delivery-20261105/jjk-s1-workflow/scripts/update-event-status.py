"""Versioned evidence state; does not edit a frozen plan or assign artistic pass."""
from pathlib import Path
import argparse,json,hashlib
A=argparse.ArgumentParser();A.add_argument('--loop',type=int,required=True);A.add_argument('--summary-only',action='store_true');a=A.parse_args()
R=Path(__file__).resolve().parent.parent;L=R/f'loops/loop-{a.loop:02}';out=R/'data/event-version-status-final.json' if a.summary_only else L/'event-version-status.json'
if not a.summary_only and out.exists() and (L/'review.json').exists():raise SystemExit('An audited status snapshot is immutable; create the next loop snapshot')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mapping=[('opening-slam','typeEvents','opening-slam',[]),('palm-match-a',None,None,[]),('palm-match-b',None,None,[]),('archive-screen','archiveScreen',None,[]),('triptych-weapon','layouts','weapon-triptych',[]),('palm-early','foregrounds','palm-before-weapon',['L2-TYPE-04']),('strike-type','typeEvents','strike-type',['L2-TYPE-04']),('eyes-slit','layouts','paired-eyes',['L2-EYE-01']),('energy-edge','layouts','palm-energy-paper',['L2-TEAR-02']),('leaves-to-technique','layouts','same-source-leaves',['L2-LEAF-03']),('limitless-type','typeEvents','limitless-type',['L2-GESTURE-08']),('clap-match',None,None,['L2-GESTURE-08']),('return-windows','layouts','memory-windows',[]),('final-title','tailcard',None,[]),('yuji-runs-ahead','foregrounds','yuji-runs-ahead',['L2-ALPHA-06'])]
mapping.append(('tail-action-release','events','tail-action-release',['L3-PACING-10']))
mapping=[(s,k,b,find+(['L3-CN-TYPE-09'] if s=='strike-type' else [])) for s,k,b,find in mapping]
versions=[]
for n in range(2,a.loop+1):
 d=R/f'loops/loop-{n:02}';plan=d/('plan-final.json' if n==2 else 'plan.json')
 if not plan.exists():continue
 p=json.loads(plan.read_text(encoding='utf-8'));execution=json.loads((d/'execution.json').read_text(encoding='utf-8')) if (d/'execution.json').exists() else None;review=json.loads((d/'review.json').read_text(encoding='utf-8')) if (d/'review.json').exists() else None
 events=[]
 for stable,kind,key,findings in mapping:
  if stable=='tail-action-release' and not any(e['id']==stable for e in p.get('events',[])):continue
  original=next((e for e in p.get('events',[]) if e['id']==stable),None)
  historical=next((e for e in p.get('designRevision',{}).get('events',p.get('events',[])) if e['id']==stable),None)
  actual=next((e for e in p.get(kind,[]) if e['id']==key),None) if key else (p.get(kind) if kind else original)
  assert actual is not None,(n,stable)
  affected=stable in ['palm-early','strike-type','eyes-slit','energy-edge','leaves-to-technique','limitless-type','clap-match']
  renderstate='rendered' if execution else ('planned_revision' if affected else 'L2_capture_exists_pending_current_payload_rebind')
  reportfindings=[f for f in (review or {}).get('findings',[]) if f['id'] in findings or stable in f.get('eventIds',[])]
  reviewstate='pending_review' if not review else ('independent_report_pass_with_stated_limits' if review['status']=='pass' else ('reviewed_revise' if any(str(f.get('severity','')).startswith('P1') and ('open' in f.get('status','') or 'new' in f.get('status','')) for f in reportfindings) else 'reviewed_see_independent_report'))
  events.append({'stableDesignEventId':stable,'addedAfterDesignB':stable in ['yuji-runs-ahead','tail-action-release'],'actualBinding':f'{kind}.{key}' if key else kind or 'native shot boundary','actualRangeFrames':[actual['start'],actual['end']],'frozenDesignRangeFrames':[historical['start'],historical['end']] if historical else None,'renderState':renderstate,'reviewState':reviewstate,'relatedFindings':findings,'reviewFindingStates':[{k:f.get(k) for k in ['id','severity','status']} for f in reportfindings],'video':execution['video'] if execution else None,'videoSha256':execution['sha256'] if execution else None})
 versions.append({'loop':n,'plan':plan.relative_to(R).as_posix(),'planSha256':sha(plan),'execution':f'loops/loop-{n:02}/execution.json' if execution else None,'review':f'loops/loop-{n:02}/review.json' if review else None,'globalReviewStatus':review.get('status') if review else 'pending','events':events})
data={'scope':'14 original design stable IDs + XCHASE + final tail action group. Older plan.events is historical intent; R4 plan.events normalized to actual binding. No artistic pass assigned by author.','snapshotLoop':a.loop,'versions':versions,'sharedMetadataFinding':'L2-META-05 and L3-EVENTS-11: actual source identity/window/evidence and active event binding; independent closure source in each review'}
out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');(R/'data/event-version-status.json').write_bytes(out.read_bytes())
lines=['# 逐事件版本状态','',data['scope'],'','|设计事件|实际绑定|L2|L3|L4|','|---|---|---|---|---|']
for stable,kind,key,findings in mapping:
 cells=[]
 for n in [2,3,4]:
  e=next((e for v in versions if v['loop']==n for e in v['events'] if e['stableDesignEventId']==stable),None)
  cells.append('—' if e is None else f"{e['renderState']} / {e['reviewState']} / F{e['actualRangeFrames'][0]}–{e['actualRangeFrames'][1]-1}")
 lines.append('|'+stable+'|'+(f'{kind}.{key}' if key else kind or '原生动作接力')+'|'+'|'.join(cells)+'|')
lines+=['','`rendered`表示该版完整视频已实际生成；`pending_review`表示尚未独立验收。`reviewed_see_independent_report`不等于无条件通过；局部结论和材料限制以独立报告为准。','',f'本表快照：`loops/loop-{a.loop:02}/event-version-status.json`。未来轮次另写快照，不修改已被签署的旧版。']
(out.with_suffix('.md') if a.summary_only else L/'event-version-status.md').write_text('\n'.join(lines),encoding='utf-8')
print('Versioned event state:',out,';16 IDs including2added')
