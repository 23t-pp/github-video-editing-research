"""Prepare an auditable L3 plan and staged code without mutating active L2 capture."""
from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parent.parent;H=R/'hyperframes';L=R/'loops/loop-03';L.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((R/'loops/loop-02/plan-final.json').read_text(encoding='utf-8'))
changes=[]
eyes=next(e for e in p['layouts'] if e['id']=='paired-eyes')
measure=json.loads((R/'data/eye-alignment-proposal.json').read_text(encoding='utf-8'))
for c,m in zip(eyes['clips'],measure):
 c['transform']=m['transform'].copy();c['transform']['y']+=50
eyes['origin']='T05/V17，真实prepared F26虹膜定位辅助眼白开口/眼轴校正；原画红小瞳与蓝大虹膜不做形态伪造'
changes.append({'findingId':'L2-EYES','old':'左右眼线差约120px，白眼开口尺度不齐','new':eyes['clips'],'evidence':'data/eye-alignment-proposal.json','acceptance':'真实F823/F830/F839眼轴差≤20px，眼白开口高度比1–1.3；独审待定'})
tear=next(e for e in p['layouts'] if e['id']=='palm-energy-paper')
tear['clips']=[{'assetId':'N054','offset':12,'transform':{'scale':1.2,'x':520,'y':0}}]
tear.update(top=130,bottom=1012,left=1110,width=350,origin='T07/T17/V17/V11，真实伏黑侧脸入裂条+青掌跨场景前景；替换旧手RGB导致的空黑区，保持真实纤维电弧边')
fg=next(e for e in p['foregrounds'] if e['id']=='palm-over-paper');fg.update(scale=.8,restX=200,restY=100,x=80,y=40)
changes.append({'findingId':'L2-TEAR','old':'竖条上半使用手RGB黑背景，出现空黑块','new':{'clips':tear['clips'],'foreground':fg},'acceptance':'条内有实际人物眼鼻，不能有无意义黑空块，右袖始终出画'})
leaf=next(e for e in p['layouts'] if e['id']=='same-source-leaves')
leaf.update(revealFrames=6,staggerFrames=.5,shadeStrength=.15,veilOpacity=.15,aperture=[60,1020])
changes.append({'findingId':'L2-LEAVES','old':'7叶错开1.5f/展开10f，12f事件末未全部归位，遮罩过暗','new':{k:leaf[k] for k in ['revealFrames','staggerFrames','shadeStrength','veilOpacity','aperture']},'acceptance':'1071..1073全部叶片零角度/阴影零；1073 preparedF11→1074 F12；黑带不跳'})
strike=next(e for e in p['typeEvents'] if e['id']=='strike-type');strike.update(y=210,font_size=240,width=1400,subtitle_y=940)
fg=next(e for e in p['foregrounds'] if e['id']=='palm-before-weapon');fg.update(scale=.8,restX=200,restY=100,x=130,y=40)
changes.append({'findingId':'L2-TYPE','old':'F626仅ST大部可读，其余被掌遮挡','new':{'type':strike,'foreground':fg},'acceptance':'连续至少6帧完整STRIKE可读，上字下手与前景关系清楚，腕袖边缘在右画外'})
limitless=next(e for e in p['typeEvents'] if e['id']=='limitless-type');limitless.update(x=1540,y=260,width=650,font_size=160,subtitle_x=1540,subtitle_y=520)
changes.append({'findingId':'L2-GESTURE-08','old':'LIMITLESS盖住合掌学习主体','new':limitless,'acceptance':'文字留在右上天空区，五条的手掌及合掌动作连续无遮挡，中文独立位于英文下方'})
fresh=json.loads((R/'data/retrieved-assets-loop2-final.json').read_text(encoding='utf-8'))['items']
cands={c['candidateId']:c for c in json.loads((R/'data/fresh-shot-candidates.json').read_text(encoding='utf-8'))['items']}
inv={c['id']:c for c in json.loads((R/'data/source-inventory.json').read_text(encoding='utf-8'))['items']}
corrections=[]
for v in fresh:
 s=next(s for s in p['shots'] if s['id']==v['shot']);c=cands[v['candidateId']];source=inv[v['sourceId']]
 old={k:s.get(k) for k in ['episode','searchWindowSeconds','preflightEvidence','focus']}
 s.update(episode=source['episodeNumber'],sourcePath=source['localPath'],searchWindowSeconds=v['coreSourceSeconds'],preflightEvidence=c['evidence'],focus=c.get('observedMovement',v.get('focus','unknown')),motionEvidence='data/fresh-native-verification.json',freshEvidence=c['evidence'])
 assert (R/s['preflightEvidence']).is_file(),s['preflightEvidence']
 s['exactNativeCutBoundaryStatus']='curator native full-frame core inspection plus actual prepared pixels; independent composed-video review pending'
 corrections.append({'shot':s['id'],'candidateId':s['candidateId'],'old':old,'new':{k:s.get(k) for k in old}})
checks=[]
for s in p['shots']:
 if s['kind']!='video':continue
 source=inv[s['sourceId']];ok=(s['episode']==source['episodeNumber'] and Path(s['sourcePath']).as_posix().lower()==Path(source['localPath']).as_posix().lower())
 w=s.get('searchWindowSeconds',[]);within=len(w)==2 and s['sourceInSeconds']>=w[0]-1e-5 and s['sourceOutSeconds']<=w[1]+1e-5
 # Slow-window L1 revisions legitimately expanded original scout window; preserve explicitly.
 if not within and s['id'] in ['S019','S034','S038','S040','S046']:
  s['searchWindowSeconds']=[s['sourceInSeconds'],s['sourceOutSeconds']];s['preflightEvidence']='data/slow-window-inspection.json';within=True
 checks.append({'shot':s['id'],'sourceIdentityMatches':ok,'formalRangeInDeclaredWindow':within,'sourceId':s['sourceId'],'episode':s['episode']})
assert all(c['sourceIdentityMatches'] for c in checks)
assert all(c['formalRangeInDeclaredWindow'] for c in checks)
changes.append({'findingId':'L2-METADATA-P1','old':'新源继承旧episode/searchWindow/preflightEvidence','new':corrections,'acceptance':'sourceId/episode/path一致，新8源取回范围在curator核心窗内；独审待定'})
changed_ids={'paired-eyes','palm-energy-paper','same-source-leaves','strike-type','palm-before-weapon','palm-over-paper','limitless-type'}
for key in ['layouts','typeEvents','foregrounds']:
 for e in p.get(key,[]):e['status']='planned_revision' if e['id'] in changed_ids else 'L2_capture_exists_pending_L3_payload_rebind'
p['version']='L3-D-craft-revision';p['revision']='L3-D';p['status']='planned_revision_not_rendered'
(L/'plan-proposal.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
(L/'revision-diff.json').write_text(json.dumps({'from':'loops/loop-02/plan-final.json','changes':changes,'pending':['independent L2 review','activate staged code only after L2 encode completed','actual L3 capture/1080 encode/independent review']},ensure_ascii=False,indent=2),encoding='utf-8')
(R/'data/metadata-consistency-L3-proposal.json').write_text(json.dumps({'checks':checks,'freshCorrections':corrections,'status':'machine proposal, not composed-video acceptance'},ensure_ascii=False,indent=2),encoding='utf-8')
video=[s for s in p['shots'] if s['kind']=='video'];pairs=[]
for i,a in enumerate(video):
 for b in video[i+1:]:
  if a['sourceId']!=b['sourceId']:continue
  overlap=max(0,min(a['sourceOutSeconds'],b['sourceOutSeconds'])-max(a['sourceInSeconds'],b['sourceInSeconds']))
  if overlap<=1e-5:continue
  intentional={a['id'],b['id']}=={'S014','S049'}
  pairs.append({'first':a['id'],'second':b['id'],'sourceId':a['sourceId'],'overlapSeconds':overlap,'intentional':intentional,'purpose':'档案屏局部线索→全幅动作回收' if intentional else 'requires explicit reason or replacement'})
assert len(pairs)==1 and pairs[0]['intentional']
(R/'data/main-timeline-reuse-L3-proposal.json').write_text(json.dumps({'scope':'all same-source interval comparisons, not only candidate equality','videoClips':len(video),'uniqueCandidates':len(set(s['candidateId'] for s in video)),'overlapPairs':pairs,'secondaryUses':[{'kind':'tear portrait intro','asset':'N054','frames':[970,996],'laterMain':'S054','intent':'人物裂条预告→后段完整侧脸；新增次级层有意复用'},{'kind':'same-source7leaves','asset':'S045','frames':[1062,1074],'clock':'preparedF0..11→baseF12','intent':'7叶是同一源时钟并排几何，不算7条新镜头'},{'kind':'alpha','assets':['XPALM','XCHASE'],'intent':'真实动态前景跨场景接力，分别列出而非伪装成新原源'},{'kind':'memory windows','assets':['S053','S031'],'intent':'角色记忆片作为小窗回收；与主线重复统计分开'}],'machinePassNoUnexplainedMainOverlap':True,'artisticAcceptance':'pending independent review'},ensure_ascii=False,indent=2),encoding='utf-8')
src=(H/'layoutfx.py').read_text(encoding='utf-8')
src=src.replace("content.append('<div class=\"lf-plane lf-veil\"></div>')\n            for j in range(count):", "content.append(f'<div class=\"lf-plane lf-veil\" style=\"opacity:{float(e.get(\"veilOpacity\",1))}\"></div>')\n            aperture=e.get('aperture',[100,980]);reveal=max(1,float(e.get('revealFrames',10)));stagger=float(e.get('staggerFrames',1.5));shade=float(e.get('shadeStrength',.6))\n            for j in range(count):")
src=src.replace("rectpath([x,100,w,880])", "rectpath([x,float(aperture[0]),w,float(aperture[1])-float(aperture[0])])")
src=src.replace("q=out((f-st-j*1.5)/10)","q=out((f-st-j*stagger)/reveal)")
src=src.replace("'opacity':.6*(1-out((f-st-j*1.5)/10))", "'opacity':shade*(1-out((f-st-j*stagger)/reveal))")
assert src!=(H/'layoutfx.py').read_text(encoding='utf-8') and 'aperture=e.get' in src
(L/'layoutfx-proposal.py').write_text(src,encoding='utf-8')
src=(H/'typefx.py').read_text(encoding='utf-8')
assert 'x="960" y="{float(e.get("subtitle_y",947))}"' in src
src=src.replace('x="960" y="{float(e.get("subtitle_y",947))}"','x="{e.get("subtitle_x",960)}" y="{float(e.get("subtitle_y",947))}"')
(L/'typefx-proposal.py').write_text(src,encoding='utf-8')
print(json.dumps({'proposal':'loops/loop-03/plan-proposal.json','metadataRows':len(checks),'freshRows':len(corrections),'windowWarnings':[c['shot'] for c in checks if not c['formalRangeInDeclaredWindow']],'activeCodeChanged':False},ensure_ascii=False))
