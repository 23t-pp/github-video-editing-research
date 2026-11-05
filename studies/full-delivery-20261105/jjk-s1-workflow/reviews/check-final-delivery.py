from pathlib import Path
from datetime import datetime,timezone,timedelta
import ast,base64,copy,hashlib,json,subprocess,urllib.request,collections
R=Path(__file__).resolve().parents[1];O=R/'reviews/final-preparation';cache={}
def sha(p):
    p=Path(p).resolve()
    if p not in cache:
        with p.open('rb') as f:cache[p]=hashlib.file_digest(f,'sha256').hexdigest()
    return cache[p]
read=lambda p:json.loads((R/p).read_text(encoding='utf-8-sig'))
occ=read('openchatcut/工程包最终回读.json');exp=read('openchatcut/官方工程包验证.json');imp=read('openchatcut/官方工程包导入回验.json');package=R/'openchatcut'/occ['packageFilename']
assert sha(package)==occ['packageSha256']==exp['sha256'] and package.stat().st_size==occ['packageBytes']==205861867
assert occ['mediaAssets']==occ['mediaAvailableAndByteVerified']==imp['mediaRestored']==85 and occ['mediaMissing']==imp['mediaMissing']==[] and imp['editStructureEqual'] and imp['sourceProjectUnchanged'] and imp['existingProjectDocumentsNotWritten']
active=None;records=[];runtime=None;types=collections.Counter()
with package.open('rb') as f:
    manifest=json.loads(f.readline());assert manifest['format']=='openchatcut-project@2' and manifest['type']=='manifest'
    for line in f:
        z=json.loads(line);kind=z['type'];types[kind]+=1
        if kind in ['media-start','agent-runtime-start']:
            assert active is None;active={'kind':kind,'header':z,'hash':hashlib.sha256(),'bytes':0}
        elif kind in ['media-chunk','agent-runtime-chunk']:
            assert active is not None;data=base64.b64decode(z['data'],validate=True);active['hash'].update(data);active['bytes']+=len(data)
        elif kind in ['media-end','agent-runtime-end']:
            assert active is not None;h=active['hash'].hexdigest();header=active['header'];assert active['bytes']==header['bytes'];assert z.get('sha256',h)==h
            if kind=='media-end':
                assert header['sourceRevision']=='source-sha256-'+h;records.append({'src':header['src'],'bytes':active['bytes'],'sha256':h})
            else:assert h==header['sha256'];runtime={'bytes':active['bytes'],'sha256':h}
            active=None
        elif kind=='media-missing':raise AssertionError(z)
assert active is None and len(records)==85 and runtime
expected=sorted((x['bytes'],x['sha256']) for x in imp['mediaChecks']);assert sorted((x['bytes'],x['sha256']) for x in records)==expected==sorted((x['bytes'],x['sha256']) for x in exp['mediaChecks'])
doc=manifest['doc'];assets={a['id']:a for a in doc['assets']};srcs={x['src']:x for x in records};assert len(assets)==85 and len(doc['timelines'])==2
for a in assets.values():assert srcs[a['src']]['sha256']==a['sourceContentHash']
plan=read('loops/loop-04/plan.json');assetPlan={a['id']:a for a in plan['assets']};timelineChecks=[]
for t in doc['timelines']:
    assert (t['fps'],t['width'],t['height'])==(24,1920,1080);video=sorted([x for x in t['items'] if x['kind']=='video'],key=lambda x:x['startFrame']);audio=[x for x in t['items'] if x['kind']=='audio'];pos=0
    for v in video:
        assert v['startFrame']==pos and v['playbackRate']==1 and v.get('volume')==0 and v['sourceAssetId'] in assets;pos+=v['durationInFrames']
    assert pos==1440 and len(audio)==1 and audio[0]['durationInFrames']==1440 and audio[0]['playbackRate']==1
    assert assets[audio[0]['sourceAssetId']]['sourceContentHash']==read('music/music-report.json')['masterSha256']
    if len(video)==59:
        for v,s in zip(video,plan['shots']):
            assert v['startFrame']==s['startFrame'] and v['durationInFrames']==s['frames'] and v['srcInFrame']==s.get('assetStartFrame',12)
            aid=s.get('assetId',s['id']);assert assets[v['sourceAssetId']]['name']==aid+'.mp4'
            if s.get('kind')=='video':assert v['sourceContentHash']==assetPlan[aid]['sha256']
            ref=s.get('reframe',{'scale':1,'x':0,'y':0});tr=v['transform'];assert abs(tr['scale']-ref.get('scale',1))<=.00051 and abs(tr['x']-ref.get('x',0)/1920*100)<=.0051 and abs(tr['y']-ref.get('y',0)/1080*100)<=.0051
    else:
        assert len(video)==20 and all(v['durationInFrames']==72 for v in video)
        for j,v in enumerate(video):
            proof=read(f'loops/loop-04/render-proofs/chunk-{j:02}.json');assert v['startFrame']==j*72 and v['srcInFrame']==0 and v['sourceContentHash']==proof['segmentSha256']
    timelineChecks.append({'name':t['name'],'videoClips':len(video),'frames':pos,'allPlaybackOne':True,'linked':True,'nativeTransformAndClockMatch':True if len(video)==59 else 'not_applicable_HF_segment','HF20SegmentShaMatchR4Proof':True if len(video)==20 else 'not_applicable_native'})
assert len(occ['reframeChecks'])==118 and occ['actualImportedMaster']['sampleFrames']==2880000 and occ['actualImportedMaster']['sha256']==sha(R/'music/master.wav')
ui=read('evidence/ui/最终交付界面验收.json');assert all(ui[k] for k in ['moviePlaybackVerified','hyperframesVerified','openchatcutVerified','noAuditoryClaim']) and not ui['auditoryListeningPerformed']
for path,h in ui['boundArtifacts'].items():assert sha(R/path)==h,path
hf=read('data/hyperframes-package-verification.json');prep=read('reviews/final-preparation/preparation.json');assert sha(R/'HyperFrames可编辑工程.zip')==prep['hyperframesZipIndependent']['sha256']==hf['archiveSha256']
for path,rec in hf['files'].items():assert sha(R/path)==rec['sha256'],path
for i in range(1,5):
    review=read(f'loops/loop-{i:02}/review.json')
    for path,h in review['boundArtifacts'].items():assert sha(R/path)==h,(i,path)
source=(R/'scripts/workflow.py').read_text(encoding='utf-8');old=(R/'workflow/final-dispatch-repair/workflow-before.py').read_text(encoding='utf-8');mod=ast.parse(source);oldMod=ast.parse(old)
get=lambda tree,name:next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
assert ast.dump(get(mod,'seal'),include_attributes=False)==ast.dump(get(oldMod,'seal'),include_attributes=False)
vr=read('workflow/final-dispatch-repair/verification.json');assert vr['pass'] and len(vr['fixtures'])==17 and all(x['pass'] for x in vr['fixtures']) and vr['workflowSha256']==sha(R/'scripts/workflow.py')
proc=subprocess.run(['C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe','-X','utf8',str(R/'scripts/workflow.py'),'next'],capture_output=True,check=True);dispatch=json.loads(proc.stdout.decode('utf-8'));assert dispatch['stage']=='final_acceptance_pending' and dispatch['actions'][0]['role']=='independent_reviewer';(O/'next-before-final-sign.json').write_bytes(proc.stdout)
mr=read('workflow/monitor-repair/validation.json');assert mr['monitorSourceSha256']==sha(R/'scripts/monitor.py') and mr['serverSourceSha256']==sha(R/'scripts/serve-learning.py') and mr['persistentLockRaisesAfterAttempts']==6 and mr['lastCommittedStatePreserved']
status=json.load(urllib.request.urlopen('http://127.0.0.1:5351/api/status',timeout=10));assert not status['monitorStale'] and status['monitorAgeSeconds']<180 and status['episodesComplete']==24 and len(status['loopArtifacts'])==4 and not status['alerts'];(O/'learning-api-final-snapshot.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report={'reviewer':'/root/s1_design_auditor','status':'all_ready_checks_pass_awaiting_own_final_signature','checkedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),'OCCIndependentPackageRead':{'packageSha256':sha(package),'bytes':package.stat().st_size,'mediaStreamsIndependentlyBase64DecodedShaCompared':85,'runtimeHashVerifiedWithoutInspectingContent':True,'timelines':timelineChecks,'allExportImportMediaHashesEqual':True,'118ReframeReportRows':True,'masterSamples':2880000,'perceptualAudioListening':False},'UIEvidence':{'currentBindingsPass':len(ui['boundArtifacts']),'screenshotImagesActuallyViewed':5,'scope':'Parent performed actual playback/seek/selection. Auditor viewed 5 current screenshots and verified13 bindings; did not pretend to replay UI actions or auditory audition.'},'HFZip':{'unchangedSinceIndependent216EntryRead':True,'sha256':sha(R/'HyperFrames可编辑工程.zip'),'currentPackagedLocalFileMatches':len(hf['files']),'exactRawIndex':sha(R/'hyperframes/index.html')},'workflowFix':{'codeSha256':sha(R/'scripts/workflow.py'),'sealAstUnchanged':True,'syntheticDispatchCasesReviewed':17,'actualCurrentStage':dispatch['stage'],'noPrematureComplete':True},'monitorRepair':{'sourceAndFaultEvidenceHashesPass':True,'terminalAttempts':6,'liveAgeSeconds':status['monitorAgeSeconds'],'stale':status['monitorStale'],'alerts':status['alerts']},'frozenFilmReviewBindingsAllPass':True,'finalReadmeSha256':sha(R/'README.md'),'finalApprovalWrittenByThisScript':False}
(O/'all-ready-independent-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
