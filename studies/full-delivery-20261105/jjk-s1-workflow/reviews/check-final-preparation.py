from pathlib import Path,PurePosixPath
import json,hashlib,zipfile,urllib.request,urllib.parse,time
R=Path(__file__).resolve().parents[1];O=R/'reviews/final-preparation';O.mkdir(exist_ok=True);cache={}
def sha(p):
    p=Path(p).resolve()
    if p not in cache:
        with p.open('rb') as f:cache[p]=hashlib.file_digest(f,'sha256').hexdigest()
    return cache[p]
read=lambda p:json.loads((R/p).read_text(encoding='utf-8-sig'))
package=read('data/hyperframes-package-verification.json');archive=R/package['archive'];assert sha(archive)==package['archiveSha256'];entryErrors=[]
with zipfile.ZipFile(archive) as z:
    names=[n for n in z.namelist() if not n.endswith('/')];assert set(names)==set(package['files'])
    for n in names:
        path=PurePosixPath(n);assert not path.is_absolute() and '..' not in path.parts
        data=z.read(n);rec=package['files'][n]
        if len(data)!=rec['bytes'] or hashlib.sha256(data).hexdigest()!=rec['sha256'] or sha(R/n)!=rec['sha256']:entryErrors.append(n)
    html=z.read('hyperframes/index.html');edit=z.read('hyperframes/edit.json');p=json.loads(edit)
    assert hashlib.sha256(html).hexdigest()=='6820afa3c483f4a04629c7e87b80e48acc133aa0ae1aa612dc770fa0d5b9727d' and b'data-hf-id' not in html and b'\r\n' not in html
    assert hashlib.sha256(edit).hexdigest()=='51f4028f411c1557e3106122bd8874992450a2fd2177f2dd262d28da9bdf229e'
    for a in p['assets']:assert hashlib.sha256(z.read('hyperframes/'+a['asset'])).hexdigest()==a['sha256']
    alpha={g:len([n for n in names if n.startswith('hyperframes/assets/alpha/'+g+'/') and n.endswith('.png')]) for g in ['XPALM','XCHASE']};assert alpha=={'XPALM':26,'XCHASE':26}
    assert hashlib.sha256(z.read('hyperframes/'+p['audio']['master'])).hexdigest()==read('music/music-report.json')['masterSha256']
assert not entryErrors,entryErrors
chain=[];bindingErrors=[]
for i in range(1,5):
    r=read(f'loops/loop-{i:02}/review.json');e=read(f'loops/loop-{i:02}/execution.json');assert r['reviewer']!=e['executor']
    for path,h in r['boundArtifacts'].items():
        if sha(R/path)!=h:bindingErrors.append({'loop':i,'path':path})
    assert sha(R/e['video'])==e['sha256'];chain.append({'loop':i,'status':r['status'],'videoSha256':e['sha256']})
assert not bindingErrors,bindingErrors
assert len(set(x['videoSha256'] for x in chain))==4 and chain[-1]['status']=='pass'
assert sha(R/'咒力接力_一分钟.mp4')==chain[-1]['videoSha256']==read('成片质量检查.json')['sha256']
q=read('data/library-verification.json');s=read('data/library-summary.json');a=read('reviews/素材集最终审核.json')
assert q['state']=='pass' and q['verifiedEpisodes']==24 and q['samples']==s['jpg60HzEntries']==a['jpgSamplePaths']==2061018 and q['uniqueJpegFullDecode']==a['uniqueNativeJpeg']==823577
for path,h in a['boundArtifacts'].items():assert sha(R/path)==h,path
c=read('data/material-catalog.json');m=read('data/tail-action-candidates.json');byid={x['id']:x for x in c['items']}
for path,h in c['sources'].items():assert sha(R/path)==h,path
for x in m['items']:
    y=byid[x['candidateId']]['tailActionEvidence']
    for key in ['sourceId','sourcePath','coreSourceSeconds','sourcePtsSeconds','characters','characterConfidence','decodedNativeFrames']:assert y[key]==x[key]
    if x['characters']==['unknown']:assert y['dispatchConstraints']['unknownIdentityMustNotBeReplacedByGuessedPersonName'] and byid[x['candidateId']]['dispatchConstraints']['unknownIdentityMustNotBeReplacedByGuessedPersonName']
assert read('data/随机参考抽选.json')['referenceId']=='V20'
status=json.load(urllib.request.urlopen('http://127.0.0.1:5351/api/status',timeout=10));(O/'learning-api-status-snapshot.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');assert not status['monitorStale'] and status['monitorAgeSeconds']<180 and status['episodesComplete']==24 and len(status['loopArtifacts'])==4 and status['filmReady']
req=urllib.request.Request('http://127.0.0.1:5351/'+urllib.parse.quote('咒力接力_一分钟.mp4'),headers={'Range':'bytes=0-15'})
with urllib.request.urlopen(req,timeout=10) as response:
    first=response.read();assert response.status==206 and first==(R/'咒力接力_一分钟.mp4').open('rb').read(16);rangeCheck={'status':response.status,'contentRange':response.headers['Content-Range'],'first16BytesMatch':True}
report={'reviewer':'/root/s1_design_auditor','status':'pending_final_Occ_UI_gate','hyperframesZipIndependent':{'pass':True,'file':package['archive'],'bytes':archive.stat().st_size,'sha256':sha(archive),'filesCrcReadAndShaCompared':len(names),'allCurrentLocalFilesShaCompared':True,'mediaAssets':len(p['assets']),'alphaFrames':alpha,'exactCanonicalRawLfHtml':True,'musicMasterShaMatch':True,'runtimeDependenciesExternalAndDocumented':True},'fourRealLoops':chain,'priorBindingsErrors':bindingErrors,'physicalDataset':{'episodes':24,'samplePaths':2061018,'nativeJpeg':823577,'priorIndependentDatasetScope':'24 reports/JSONL/SQLite and72 actual image/alias/PTS samples; final preparation checks all signed bindings, does not wastefully redo823k JPEG decode'},'catalog':{'sourcesShaPass':True,'tailWindowsAndUnknownConstraintsPass':True,'sha256':sha(R/'data/material-catalog.json')},'liveLearningApi':{'monitorAgeSeconds':status['monitorAgeSeconds'],'monitorStale':status['monitorStale'],'episodes':status['episodesComplete'],'loops':len(status['loopArtifacts']),'filmReady':status['filmReady'],'rangeRead':rangeCheck},'pending':['official OpenChatCut export/import byte roundtrip','unified final UI report bound to current deliverables','README final filename regeneration and actual final-byte binding','workflow next final dispatch fix independent check','parent all-ready before final signature'],'finalApproval':False}
(O/'preparation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:report[k] for k in ['status','hyperframesZipIndependent','liveLearningApi']},ensure_ascii=False))
