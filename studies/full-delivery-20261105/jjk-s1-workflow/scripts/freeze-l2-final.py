"""Freeze the complete L2 baseline; preserve observed defects for independent audit."""
from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parent.parent;H=R/'hyperframes';L=R/'loops/loop-02'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((L/'plan-middle.json').read_text(encoding='utf-8'))
fresh=json.loads((R/'data/fresh-prepared-assets.json').read_text(encoding='utf-8'))
v=next(i for i in fresh['items'] if i['shot']=='S056');assert v['asset']['id']=='N056B' and v['candidateId']=='S1C047'
s=next(i for i in p['shots'] if i['id']=='S056')
for k in ['candidateId','sourceId','sourcePath','sourceInSeconds','sourceOutSeconds','playbackRate','characters','focus']:s[k]=v[k]
s.update(assetId=v['asset']['id'],asset=v['asset']['asset'],assetStartFrame=12,freshEvidence=v['evidence'])
p['assets'].append(v['asset'])
manifest=R/'evidence/alpha/XCHASE-final-manifest.json'
assert sha(manifest)=='8e340e952d3b7d8e239fa9dadeea240f88b4f315a480e932b42de9520f5e3bbc'
m=json.loads(manifest.read_text(encoding='utf-8'))
assert sha(H/'assets/shots/XCHASE.mp4')==m['preparedSha256']
for f in m['files']:assert sha(R/f['path'])==f['sha256']
p['assets'].append({'id':'XCHASE','asset':'assets/shots/XCHASE.mp4','frames':31,'usableFrames':26,'sha256':m['preparedSha256'],'sourceId':'S1E24','sourcePath':'D:/咒术回战/1080P 内嵌简中字幕/24.mp4','sourceIn':764.6,'actualFirstPtsSeconds':m['firstSourcePtsSeconds'],'sourceFps':'24000/1001','description':'第一季虎杖真实奔跑上半身，F2..27动态RGBA，腰切线固定在输出底框之外'})
p['foregrounds'].append({'id':'yuji-runs-ahead','alpha':'XCHASE','start':1360,'end':1386,'offset':2,'z':60,'scale':1.15,'restX':-350,'restY':25,'x':-120,'y':70,'inFrames':4,'outFrames':4,'clipActive':True,'glow':1.2,'glowColor':'#72c7ed','origin':'T06/V17 动态前景跨场景提前入场；不是同源连续动作handoff','alphaManifest':'evidence/alpha/XCHASE-final-manifest.json'})
p['version']='L2-C-complete-baseline';p['revision']='L2-C';p['status']='complete_baseline_pending_independent_review'
out=L/'plan-final.json';out.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
(L/'plan.json').write_bytes(out.read_bytes());(H/'edit.json').write_bytes(out.read_bytes())
sys.path.insert(0,str(H));from composition import build,save_editable
old=json.loads((L/'frozen-middle.json').read_text(encoding='utf-8'))
codes={n:sha(H/n) for n in old['codeHashes']};assert codes==old['codeHashes']
hashes={str(i):hashlib.sha256(build(p,i*72,(i+1)*72,True)[0].encode()).hexdigest() for i in range(20)}
assert all(hashes[str(i)]==old['chunkHtmlSha256'][str(i)] for i in range(18))
save_editable(build(p)[0])
(L/'frozen-final.json').write_text(json.dumps({'plan':'loops/loop-02/plan-final.json','planSha256':sha(out),'allowedChunks':list(range(20)),'newChunks':[18,19],'codeHashes':codes,'chunkHtmlSha256':hashes,'middleMatchesAll18':True,'alphaManifestSha256':sha(manifest),'knownIssuesNotPassed':['eye axis and scale mismatch','empty dark upper torn strip','heavy initial leaf shade','STRIKE partially obscured by palm'],'status':'complete L2 baseline, independent audit pending'},ensure_ascii=False,indent=2),encoding='utf-8')
(R/'data/retrieved-assets-loop2-final.json').write_text(json.dumps({'items':fresh['items'],'scope':'new L2-final sources only; earlier loop2-middle and L1 inputs retained'},ensure_ascii=False,indent=2),encoding='utf-8')
d=json.loads((L/'revision-diff.json').read_text(encoding='utf-8'));d['changes'].append({'findingId':'L2-TAIL','change':'S056闭眼保持改为C047抬腕/额头；真实XCHASE R4.0动态前景F1360..1385，腰切线贴底；0..17段HTML逐段完全相等'})
d['pending']=['independent complete L2 review','L3 close known eye/tear/leaf/text findings'];d['knownL2Issues']=['眼线与尺度未对齐，已留实际初图与测量方案，L3改','竖裂边上半黑空，L3结构改','七叶初始veil/shade偏暗，L3改','STRIKE受青掌遮挡，L3留完整可读窗口']
(L/'revision-diff.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'plan':str(out),'sha256':sha(out),'all18MiddleChunksEqual':True,'alphaFrames':m['alphaCount'],'manifestFilesVerified':len(m['files']),'newChunks':[18,19]},ensure_ascii=False))
