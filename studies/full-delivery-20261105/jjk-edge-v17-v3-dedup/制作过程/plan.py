from pathlib import Path
import json,csv,collections,hashlib
BASE=Path(__file__).resolve().parents[2];WORK=Path(__file__).resolve().parent
OLD=BASE/'outputs/jjk-edge-v17-v2';ROOT=BASE/'outputs/jjk-edge-v17-v3-dedup';HF=ROOT/'hyperframes'
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=json.loads((OLD/'hyperframes/edit.json').read_text(encoding='utf8'))
new=json.loads((WORK/'new-assets.json').read_text(encoding='utf8'))
replacements={'S02':'N01','S09':'N02','S19':'N03','S20':'N04','S21':'N05','S22':'N06','S23':'N07','S39':'N08','S40':'N09','S42':'N10','S43':'N11','S55':'N12','S56':'N13','S57':'N14','S58':'N15','S59':'N16','S60':'N17','S61':'N18','S62':'N19','S63':'N20','S64':'N21'}
log=[]
for s in p['shots']:
 if s['id'] in replacements:
  id=replacements[s['id']];a=next(a for a in new if a['id']==id)
  log.append({'shot':s['id'],'startFrame':s['startFrame'],'frames':s['frames'],'before':{'assetId':s['assetId'],'offset':s['assetStartFrame']},'after':{'assetId':id,'offset':12,'source':a['sourcePath'],'sourceIn':a['sourceIn'],'description':a['description']}})
  s.update(assetId=id,asset=a['asset'],assetStartFrame=12)
  # The late portrait enters as alpha first, then becomes its own native shot.
  if s['id']=='S64':s['assetStartFrame']=29;log[-1]['after']['offset']=29
for e in p['layouts']:
 if e['id']=='opening-depth':e['clips'][1]={'assetId':'N31','offset':12}
 if e['id']=='friend-film':e['clips']=[{'assetId':id,'offset':12} for id in ['N27','N28','N29']]
 if e['id']=='warm-depth':e['clips'][1]={'assetId':'N30','offset':12}
 if e['id']=='knife-eye-depth':e['clips'][1]={'assetId':'N22','offset':12}
 if e['id']=='purple-depth':e['clips']=[{'assetId':'N14','offset':12},{'assetId':'N23','offset':12}]
 if e['id']=='final-actions':e['clips']=[{'assetId':id,'offset':12} for id in ['N24','N25','N26']]
fgmap={'cold-face-over-warm':('Z-gojo-calm','N33',12),'cold-return':('Z-gojo-profile','N40',12),'geto-crosses-hall':('Z-geto-smile','N34',12),'geto-over-action':('Z-geto-phone','N35',12),'geto-memory-action':('Z-geto-white','N36',12),'geto-hero':('Z-geto-shadow','N37',12),'awaken-purple':('Z-gojo-grin','N38',12),'blue-last-hit':('Z-hand','N39',12),'cold-final-memory':('Z-gojo-last','N21',12)}
for e in p['foregrounds']:
 if e['id'] in fgmap:
  alpha,src,off=fgmap[e['id']];e.update(alpha=alpha,offset=off)
  e['sourceAssetId']=src
  # These new silhouettes were selected for their own geometry, not stretched
  # to imitate the old giant head. Native crop endings stay behind the bars.
  if e['id'] in ['cold-face-over-warm','cold-return','geto-crosses-hall','geto-over-action','geto-memory-action','geto-hero','cold-final-memory']:
   e.update(scale=1.0,restX=280 if 'gojo' in alpha else -400,restY=0,clipActive=True)
  if e['id']=='awaken-purple':e.update(scale=1.0,restX=260,restY=0,clipActive=True)
  if e['id']=='blue-last-hit':e.update(scale=1.05,restX=-150,restY=0,clipActive=True)
  if e['id']=='cold-final-memory':e.update(restX=0,restY=0,scale=1,glow=0,x=0,y=0,inFrames=1)
# Two fast pose-changing takes are kept as live spatial windows instead of
# shipping a torn silhouette. The remaining dynamic foregrounds stay separate.
for eid,aid in [('cold-face-over-warm','N33'),('cold-return','N40'),('awaken-purple','N38'),('blue-last-hit','N39')]:
 e=next(e for e in p['foregrounds'] if e['id']==eid)
 p['layouts'].append({'id':'dedup-'+eid,'kind':'depth_windows','start':e['start'],'end':e['end'],'clips':[{'assetId':aid,'offset':12}],'slots':[{'x':480,'y':50,'scale':.62,'rotation':-4,'blur':0}],'z':35,'origin':'V3新素材空间窗口：取代重复冷脸；运动边缘不可靠时不冒充完整alpha'})
p['foregrounds']=[e for e in p['foregrounds'] if e['id'] not in ['cold-face-over-warm','cold-return','awaken-purple','blue-last-hit','cold-final-memory']]
for e in p['foregrounds']:
 if e['id']=='geto-over-action':e['end']=508
p['assets']+=new;p.update(title='挚友 · EDGE · 画面去重V3',revision='V3-dedup')
p['dedupPolicy']={'source':'V2','preserveCutFrames':True,'preserveMusic':True,'newNativeReplacements':len(log),'sameEventCompositionIsNotReplay':True,'note':'同步图层/转场接力保留；不同时间反复用同一镜头或人物动作应更换。镜头/前景去重以源内容和时间范围复查，不能只换ID。'}
used={s['assetId'] for s in p['shots']}
for key in ['layouts','visuals']:
 for e in p[key]:used.update(c['assetId'] for c in e.get('clips',[]))
used.update(x.get('sourceAssetId') for x in p['foregrounds'] if x.get('sourceAssetId'))
p['assets']=[a for a in p['assets'] if a['id'] in used]
c=collections.Counter(s['assetId'] for s in p['shots']);g=collections.Counter(e['alpha'] for e in p['foregrounds'])
assert len(c)==67 and max(c.values())==1
assert len(g)==11 and max(g.values())==1
write(HF/'edit.json',p);write(ROOT/'evidence/主镜头替换清单.json',log)
write(WORK/'foreground-jobs.json',[{'id':alpha,'assetId':asset,'first':off,'last':off+next(e['end']-e['start'] for e in p['foregrounds'] if e['alpha']==alpha)} for alpha,asset,off in fgmap.values() if any(e['alpha']==alpha for e in p['foregrounds'])])
write(ROOT/'evidence/V3去重统计.json',{'nativeShots':67,'nativeUniqueAssetIds':len(c),'nativeRepeatPlacementsById':0,'foregroundEvents':len(g),'foregroundUniqueGroups':len(g),'foregroundRepeatPlacementsByGroup':0,'mainReplacements':log,'limits':'ID统计只是结构检查；新素材来源已逐项记录并做四帧观察，最终还要核对源时间区间及成片。同期同源图层/动画原片内部保持画面不是跨段重复。'})
with (HF/'镜头表.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['镜头ID','素材ID','成片起始帧','镜头帧数','素材入帧','源片','源入点'])
 assets={a['id']:a for a in p['assets']}
 for s in p['shots']:
  a=assets[s['assetId']];w.writerow([s['id'],s['assetId'],s['startFrame'],s['frames'],s['assetStartFrame'],a.get('sourcePath','预处理'),a.get('sourceIn','')])
print('PLANNED',len(log),'new main shots;',len(p['assets']),'media;',len(g),'unique foregrounds')
