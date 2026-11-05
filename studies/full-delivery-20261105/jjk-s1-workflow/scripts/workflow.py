"""Artifact-bound workflow gates. Agents author/review; this CLI verifies evidence and seals state."""
from pathlib import Path
import json,hashlib,argparse,datetime
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def bound(review):
    for path,digest in review.get('boundArtifacts',{}).items():
        p=ROOT/path;assert p.is_file() and sha(p)==digest,('stale or missing reviewed artifact',path)
def status():
    r=read(ROOT/'workflow/monitor.json') if (ROOT/'workflow/monitor.json').exists() else {'state':'not monitored'}
    print(json.dumps(r,ensure_ascii=False,indent=2))
def seal():
    dataset=read(ROOT/'data/library-verification.json');assert dataset['state']=='pass' and dataset['verifiedEpisodes']==24
    for name in ['咒力接力_一分钟.mp4','HyperFrames可编辑工程.zip','README.md','docs/操作与学习.md','hyperframes/index.html','hyperframes/edit.json','成片质量检查.json','openchatcut/工程包最终回读.json']:
        p=ROOT/name;assert p.is_file() and p.stat().st_size>0,('missing deliverable',name)
    package=list((ROOT/'openchatcut').glob('*.ccproj'));assert package and all(p.stat().st_size>10000 for p in package)
    occ=read(ROOT/'openchatcut/工程包最终回读.json');assert not occ['mediaMissing'] and occ['mediaAvailableAndByteVerified']==occ['mediaAssets']
    film=read(ROOT/'成片质量检查.json');assert film['fullDecodedFrames']==1440 and film['decodedAudioSampleFrames']==2880000 and film['width']==1920 and film['height']==1080 and film['sameTimeCorrelation']>.995
    assert film['sha256']==sha(ROOT/'咒力接力_一分钟.mp4'),'final film changed since quality check'
    import zipfile
    with zipfile.ZipFile(ROOT/'HyperFrames可编辑工程.zip') as z:assert z.testzip() is None
    loops=[];videos=[]
    for directory in sorted((ROOT/'loops').glob('loop-*')):
        for n in ['plan.json','execution.json','review.json','revision-diff.json']:assert (directory/n).is_file(),(directory,n)
        execution=read(directory/'execution.json');review=read(directory/'review.json');bound(review)
        assert review.get('reviewer') and review['reviewer']!=execution.get('executor'),('review not independent',directory)
        assert review.get('status',review.get('decision')) in ['pass','revise','needs_revision'],('unsigned review',directory)
        artifact=execution.get('video',execution.get('artifact'))
        if isinstance(artifact,dict):artifact=artifact['path']
        assert artifact,('missing actual video',directory)
        movie=ROOT/artifact;assert movie.exists() and movie.stat().st_size>10000
        digest=sha(movie);videos.append(digest);loops.append({'loop':directory.name,'video':artifact,'sha256':digest,'reviewer':review['reviewer'],'status':review.get('status',review.get('decision'))})
    assert len(loops)>=4 and len(set(videos))>=4,'four genuinely distinct rendered loop artifacts required'
    assert loops[-1]['status']=='pass','latest loop has not passed'
    final=read(ROOT/'reviews/最终验收.json');bound(final);assert final.get('status')=='pass'
    deliver={'state':'delivered','time':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'loops':loops,'datasetSamples':dataset['samples'],'gate':'passed real artifacts, independent reviews, 4 distinct videos, 24 episode complete JPEG QA, final acceptance'}
    (ROOT/'workflow/delivered.json').write_text(json.dumps(deliver,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(deliver,ensure_ascii=False))
def inspect_review(path):
    r=read(ROOT/path);bound(r);print(json.dumps({'review':path,'status':r.get('status',r.get('decision')),'boundArtifactsValid':True,'allowedActions':r.get('allowedActions',[])},ensure_ascii=False))
def _report(path):
    file=ROOT/path
    if not file.is_file():return None,[{'code':'missing_report','path':path}]
    try:
        value=read(file)
        if not isinstance(value,dict):raise ValueError('report must be a JSON object')
        return value,[]
    except (OSError,ValueError) as e:return None,[{'code':'invalid_report','path':path,'detail':str(e)}]
def _binding_issues(report,path,required=()):
    links=report.get('boundArtifacts');issues=[]
    if not isinstance(links,dict) or not links:return [{'code':'empty_review_bindings','path':path}]
    for name in required:
        if name not in links:issues.append({'code':'required_binding_missing','path':path,'artifact':name})
    for name,digest in links.items():
        if not isinstance(name,str) or not isinstance(digest,str) or len(digest)!=64:
            issues.append({'code':'invalid_binding','path':path,'artifact':str(name)});continue
        file=ROOT/name
        try:
            if not file.is_file() or sha(file)!=digest:issues.append({'code':'stale_or_missing_binding','path':path,'artifact':name})
        except OSError as e:issues.append({'code':'binding_read_failed','path':path,'artifact':name,'detail':str(e)})
    return issues
def _artifact_issues(path,digest,size=None):
    file=ROOT/path
    try:
        if not file.is_file():return [{'code':'missing_artifact','path':path}]
        if (size is not None and file.stat().st_size!=size) or sha(file)!=digest:return [{'code':'artifact_hash_or_size_changed','path':path}]
    except OSError as e:return [{'code':'artifact_read_failed','path':path,'detail':str(e)}]
    return []
def _occ_delivery_issues():
    path='openchatcut/工程包最终回读.json';report,issues=_report(path)
    if report is None:return issues,None
    name=report.get('packageFilename');package='openchatcut/'+name if isinstance(name,str) and Path(name).name==name else None
    if not package:issues.append({'code':'invalid_occ_package_name','path':path})
    else:issues+=_artifact_issues(package,report.get('packageSha256'),report.get('packageBytes'))
    count=report.get('mediaAssets')
    if type(count) is not int or count<=0 or report.get('mediaMissing')!=[] or report.get('mediaAvailableAndByteVerified')!=count:
        issues.append({'code':'occ_missing_or_unverified_media','path':path})
    if report.get('packageFormat')!='openchatcut-project@2' or not report.get('projectId') or not report.get('importedProjectId') or report.get('projectId')==report.get('importedProjectId'):
        issues.append({'code':'occ_roundtrip_identity_or_format_invalid','path':path})
    observations=report.get('observed',[])
    for role,key in [('source','projectId'),('officialImportedCopy','importedProjectId')]:
        row=next((r for r in observations if isinstance(r,dict) and r.get('role')==role),{}) if isinstance(observations,list) else {}
        sequences=row.get('sequences',[])
        if not isinstance(sequences,list):sequences=[]
        if row.get('id')!=report.get(key) or row.get('assets')!=count or len(sequences)!=2 or any(not isinstance(s,dict) or any(s.get(k)!=v for k,v in [('frames',1440),('fps',24),('width',1920),('height',1080),('contiguousVideo',True),('allMediaLinked',True),('allVideoMuted',True),('allPreparedPlaybackRateOne',True)]) for s in sequences):
            issues.append({'code':'occ_project_readback_incomplete','path':path,'role':role})
    export,err=_report('openchatcut/官方工程包验证.json');issues+=err
    imported,err=_report('openchatcut/官方工程包导入回验.json');issues+=err
    if export and any(export.get(k)!=v for k,v in [('sha256',report.get('packageSha256')),('bytes',report.get('packageBytes')),('mediaTotal',count),('format','openchatcut-project@2')]):issues.append({'code':'occ_export_report_mismatch','path':'openchatcut/官方工程包验证.json'})
    if imported:
        if any(imported.get(k)!=v for k,v in [('sourceProjectId',report.get('projectId')),('importedProjectId',report.get('importedProjectId')),('mediaRestored',count),('mediaMissing',[]),('editStructureEqual',True),('sourceProjectUnchanged',True)]):issues.append({'code':'occ_import_roundtrip_failed','path':'openchatcut/官方工程包导入回验.json'})
        media=imported.get('mediaChecks',[])
        if not isinstance(media,list) or len(media)!=count or any(not isinstance(v,dict) or v.get('packageBytesMatch') is not True or not isinstance(v.get('sha256'),str) or len(v['sha256'])!=64 or type(v.get('bytes')) is not int or v['bytes']<=0 for v in media):issues.append({'code':'occ_per_media_hash_evidence_incomplete','path':'openchatcut/官方工程包导入回验.json'})
        elif export:
            exported=export.get('mediaChecks',[])
            if not isinstance(exported,list) or any(not isinstance(v,dict) or type(v.get('bytes')) is not int or not isinstance(v.get('sha256'),str) for v in exported) or sorted((v['bytes'],v['sha256']) for v in exported)!=sorted((v['bytes'],v['sha256']) for v in media):issues.append({'code':'occ_export_import_media_hashes_differ','path':'openchatcut/官方工程包导入回验.json'})
    master=report.get('actualImportedMaster',{});master=master if isinstance(master,dict) else {};master_path=ROOT/'music/master.wav'
    if master.get('sampleFrames')!=2880000 or master.get('sampleRate')!=48000 or not master_path.is_file() or master.get('sha256')!=sha(master_path):issues.append({'code':'occ_imported_master_not_current','path':path})
    return issues,package
def _hf_delivery_issues(execution):
    import zipfile
    path='data/hyperframes-package-verification.json';report,issues=_report(path)
    if report is None:return issues
    archive='HyperFrames可编辑工程.zip'
    if any(report.get(k)!=v for k,v in [('state','pass'),('archive',archive),('crcPassed',True),('eachArchivedFileShaVerified',True),('movieSha256',execution.get('sha256')),('editSha256',execution.get('editSha256'))]):issues.append({'code':'hf_package_report_not_current_pass','path':path})
    issues+=_artifact_issues(archive,report.get('archiveSha256'),report.get('archiveBytes'))
    if issues:return issues
    members=report.get('files',{})
    if not isinstance(members,dict) or not all(n in members for n in ['hyperframes/index.html','hyperframes/edit.json']):return [{'code':'hf_package_member_evidence_missing','path':path}]
    try:
        with zipfile.ZipFile(ROOT/archive) as z:
            if set(z.namelist())!=set(members):return [{'code':'hf_package_member_set_changed','path':archive}]
            for name,expected in members.items():
                if Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('unsafe archive member '+name)
                if not isinstance(expected,dict):raise ValueError('invalid member proof '+name)
                with z.open(name) as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
                if z.getinfo(name).file_size!=expected.get('bytes') or actual!=expected.get('sha256'):issues.append({'code':'hf_archived_member_changed','path':archive,'artifact':name})
                issues+=_artifact_issues(name,expected.get('sha256'),expected.get('bytes'))
    except (OSError,ValueError,KeyError,zipfile.BadZipFile) as e:issues.append({'code':'hf_zip_integrity_failed','path':archive,'detail':str(e)})
    return issues
def _film_delivery_issues(execution):
    path='成片质量检查.json';report,issues=_report(path)
    if report is None:return issues
    expected={'fullDecodedFrames':1440,'decodedAudioSampleFrames':2880000,'width':1920,'height':1080,'sha256':execution.get('sha256')}
    if any(report.get(k)!=v for k,v in expected.items()) or not isinstance(report.get('sameTimeCorrelation'),(int,float)) or report['sameTimeCorrelation']<=.995:issues.append({'code':'final_movie_quality_report_failed_or_stale','path':path})
    issues+=_artifact_issues('咒力接力_一分钟.mp4',execution.get('sha256'))
    issues+=_artifact_issues('hyperframes/edit.json',execution.get('editSha256'))
    return issues
def _final_delivery_dispatch(execution,loop_directory):
    common=['咒力接力_一分钟.mp4','hyperframes/edit.json','openchatcut/工程包最终回读.json','data/hyperframes-package-verification.json']
    issues,package=_occ_delivery_issues()
    if issues:return {'stage':'OCC_pending','actions':[{'role':'occ_export_agent','action':'OCC_export_roundtrip','reasons':issues,'scope':'官方导出→真实导入副本→逐媒体SHA及主音轨回读，不能用文件存在代替通过'}]}
    issues=_hf_delivery_issues(execution)+_film_delivery_issues(execution)
    ui_path='evidence/ui/最终交付界面验收.json';ui,err=_report(ui_path);issues+=err
    if ui:
        if any(ui.get(k)!=v for k,v in [('state','pass'),('moviePlaybackVerified',True),('hyperframesVerified',True),('openchatcutVerified',True),('noAuditoryClaim',True)]):issues.append({'code':'final_ui_evidence_not_pass','path':ui_path})
        issues+=_binding_issues(ui,ui_path,common)
    if issues:return {'stage':'UI_delivery_pending','actions':[{'role':'orchestrator_ui_verifier','action':'UI/media_delivery_verify','reasons':issues,'scope':'当前成片实际播放、HF/OCC实际工程、ZIP逐成员和真实媒体核验；不声称试听'}]}
    final_path='reviews/最终验收.json';final,issues=_report(final_path)
    required=[*common,ui_path,'HyperFrames可编辑工程.zip',package,(loop_directory/'review.json').relative_to(ROOT).as_posix()]
    if final:
        if final.get('status')!='pass' or not isinstance(final.get('reviewer'),str) or not final['reviewer'].strip() or final['reviewer']==execution.get('executor'):issues.append({'code':'final_acceptance_not_independent_pass','path':final_path})
        issues+=_binding_issues(final,final_path,required)
    if issues:return {'stage':'final_acceptance_pending','actions':[{'role':'independent_reviewer','action':'independent_final_acceptance','reasons':issues,'requiredBindings':required,'scope':'独立验收当前真实交付与SHA绑定；不能沿用影片局部pass当全项目pass'}]}
    delivered,err=_report('workflow/delivered.json')
    if delivered:
        loops=delivered.get('loops',[])
        if delivered.get('state')!='delivered' or not isinstance(loops,list) or len(loops)<4 or not isinstance(loops[-1],dict) or loops[-1].get('sha256')!=execution.get('sha256'):err.append({'code':'delivered_state_stale','path':'workflow/delivered.json'})
    if err:return {'stage':'seal_pending','actions':[{'role':'orchestrator','action':'seal','command':'scripts/workflow.py seal','reasons':err,'scope':'实际运行现有seal；next未写入delivered，也未代调用代理'}]}
    return {'stage':'complete','workflowComplete':True,'actions':[{'role':'orchestrator','action':'complete','evidence':['workflow/delivered.json',final_path],'scope':'所有当前交付门已验证，且既有seal已实际生成delivered'}]}
def next_action():
    actions=[]
    for gate in ['设计审核.json','剪辑设计审核.json']:
        file=ROOT/'reviews'/gate
        if not file.exists():actions.append({'role':'independent_reviewer','action':'review_design','input':str(file.relative_to(ROOT))});continue
        r=read(file)
        try:bound(r)
        except AssertionError as e:actions.append({'role':'orchestrator','action':'review_changed_dependencies','evidence':str(e)});continue
        if r.get('status')!='pass':actions.append({'role':'designer','action':'revise_design','findings':r.get('findings',[])})
    if actions:
        print(json.dumps({'dispatchMode':'设计依赖优先，当前只允许复审或修设计，不派执行','actions':actions},ensure_ascii=False,indent=2));return
    existing=[int(p.name.split('-')[-1]) for p in (ROOT/'loops').glob('loop-*') if p.is_dir() and p.name.split('-')[-1].isdigit()]
    max_loop=max([4,*existing])
    latest=None;last_directory=None;videos=[]
    for n in range(1,max_loop+1):
        d=ROOT/'loops'/f'loop-{n:02}'
        if not (d/'plan.json').exists():actions.append({'role':'execution_agent','action':'prepare_next_loop','loop':n});break
        if not (d/'execution.json').exists():actions.append({'role':'orchestrator_monitor','action':'monitor_current_execution','loop':n});break
        if not (d/'review.json').exists():actions.append({'role':'independent_reviewer','action':'review_actual_artifact','loop':n,'execution':str((d/'execution.json').relative_to(ROOT))});break
        r=read(d/'review.json')
        try:
            if not r.get('boundArtifacts'):raise AssertionError('empty loop review bindings')
            bound(r);execution=read(d/'execution.json');artifact=execution.get('video',execution.get('artifact'))
            if isinstance(artifact,dict):artifact=artifact.get('path')
            if not artifact or sha(ROOT/artifact)!=execution.get('sha256'):raise AssertionError('actual rendered movie changed or execution SHA missing')
            if not r.get('reviewer') or r['reviewer']==execution.get('executor'):raise AssertionError('loop review not independent')
        except (AssertionError,OSError,ValueError) as e:actions.append({'role':'orchestrator','action':'review_changed_dependencies','loop':n,'evidence':str(e)});break
        latest=execution;last_directory=d;videos.append(execution['sha256'])
        if r.get('status',r.get('decision')) not in ['pass','revise','needs_revision']:actions.append({'role':'independent_reviewer','action':'review_actual_artifact','loop':n,'reason':'review is not signed pass/revise'});break
        if r.get('status',r.get('decision')) in ['revise','needs_revision']:
            if (ROOT/'loops'/f'loop-{n+1:02}'/'plan.json').exists():continue
            actions.append({'role':'execution_agent','action':'resolve_findings_in_next_revision','loop':n,'suggestedNextLoop':n+1,'findings':r.get('findings',[])});break
    v=ROOT/'data/library-verification.json';q=read(v) if v.exists() else {}
    if q.get('state')!='pass' or q.get('verifiedEpisodes')!=24:actions.append({'role':'orchestrator_monitor','action':'monitor_full_dataset_verification','verifiedEpisodes':q.get('verifiedEpisodes',0)})
    if not actions and (len(videos)<4 or len(set(videos))<4):actions.append({'role':'execution_agent','action':'resolve_distinct_render_requirement','actualDistinctMovies':len(set(videos))})
    dispatch={'stage':'production_pending','actions':actions} if actions else _final_delivery_dispatch(latest,last_directory)
    print(json.dumps({'dispatchMode':'编排层据此实际调用对应代理；CLI只验证证据并派发，不伪造代理执行或审核',**dispatch},ensure_ascii=False,indent=2))
p=argparse.ArgumentParser();p.add_argument('action',choices=['status','check-review','next','seal']);p.add_argument('--review');a=p.parse_args()
if a.action=='status':status()
elif a.action=='check-review':inspect_review(a.review)
elif a.action=='next':next_action()
else:seal()
