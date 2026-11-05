from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parent.parent;H=R/'hyperframes';L=R/'loops/loop-02';p=json.loads((L/'plan-early-r2.json').read_text(encoding='utf-8'));fresh=json.loads((R/'data/fresh-prepared-assets.json').read_text(encoding='utf-8'));assert fresh['prepared']==8
changes=[]
for v in fresh['items']:
 s=next(s for s in p['shots'] if s['id']==v['shot']);old={k:s.get(k) for k in ['candidateId','assetId','sourceInSeconds','sourceOutSeconds','characters']}
 for k in ['candidateId','sourceId','sourcePath','sourceInSeconds','sourceOutSeconds','playbackRate','characters','focus']:s[k]=v[k]
 if v['candidateId'] in ['S1C078','S1C088']:s['characters']=['unknown']
 s.update(assetId=v['asset']['id'],asset=v['asset']['asset'],assetStartFrame=12,reframe={'scale':1,'x':0,'y':0},freshEvidence=v['evidence'],exactNativeCutBoundaryStatus='prepared decoder all-frame machine check + four visual samples; independent L2 review pending')
 p['assets'].append(v['asset']);changes.append({'shot':s['id'],'old':old,'new':{k:s.get(k) for k in old},'reason':'不同原源区间替换不必要主线回放；不以镜像/调色假装新素材','evidence':v['evidence']})
p['version']='L2-B-middle-dedup';p['revision']='L2-B';p['status']='frames_0_1296_frozen_XCHASE_and_last2chunks_pending'
(L/'plan-middle.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8');(H/'edit.json').write_bytes((L/'plan-middle.json').read_bytes());(L/'plan.json').write_bytes((L/'plan-middle.json').read_bytes())
(R/'data/retrieved-assets-loop2.json').write_text(json.dumps({'items':fresh['items'],'scope':'new L2 sources only; L1 manifest and approved media not overwritten'},ensure_ascii=False,indent=2),encoding='utf-8')
sys.path.insert(0,str(H));from composition import build
old=json.loads((L/'frozen-early-r2.json').read_text(encoding='utf-8'));hashes={str(i):hashlib.sha256(build(p,i*72,(i+1)*72,True)[0].encode()).hexdigest() for i in range(18)};assert all(hashes[str(i)]==old['chunkHtmlSha256'][str(i)] for i in range(8))
frozen={'plan':'loops/loop-02/plan-middle.json','planSha256':hashlib.sha256((L/'plan-middle.json').read_bytes()).hexdigest(),'allowedChunks':list(range(18)),'newChunks':list(range(8,18)),'codeHashes':old['codeHashes'],'chunkHtmlSha256':hashes,'earlyR2Matches':True,'lateMutableOnly':'F1308+ main action refinement and F1360 XCHASE, no source/code mutation for rendered earlier chunks'}
(L/'frozen-middle.json').write_text(json.dumps(frozen,ensure_ascii=False,indent=2),encoding='utf-8')
d=json.loads((L/'revision-diff.json').read_text(encoding='utf-8'));d['mainSourceReplacements']=changes;d['intentionalMainReuse']=[{'first':'S014 inside original archive screen','second':'S049 full frame','candidateId':'S1C071','reason':'screen clue promoted to full-frame technique; frames contextualized differently'}];(L/'revision-diff.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('F0..1296 frozen, earlyR2 all8 equal; new8 assets actual prepared')
