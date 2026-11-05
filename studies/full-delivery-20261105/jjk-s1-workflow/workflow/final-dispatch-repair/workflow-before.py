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
    for n in range(1,max_loop+1):
        d=ROOT/'loops'/f'loop-{n:02}'
        if not (d/'plan.json').exists():actions.append({'role':'execution_agent','action':'prepare_next_loop','loop':n});break
        if not (d/'execution.json').exists():actions.append({'role':'orchestrator_monitor','action':'monitor_current_execution','loop':n});break
        if not (d/'review.json').exists():actions.append({'role':'independent_reviewer','action':'review_actual_artifact','loop':n,'execution':str((d/'execution.json').relative_to(ROOT))});break
        r=read(d/'review.json')
        if r.get('status',r.get('decision')) in ['revise','needs_revision']:
            if (ROOT/'loops'/f'loop-{n+1:02}'/'plan.json').exists():continue
            actions.append({'role':'execution_agent','action':'resolve_findings_in_next_revision','loop':n,'suggestedNextLoop':n+1,'findings':r.get('findings',[])});break
    v=ROOT/'data/library-verification.json';q=read(v) if v.exists() else {}
    if q.get('state')!='pass':actions.append({'role':'orchestrator_monitor','action':'monitor_full_dataset_verification','verifiedEpisodes':q.get('verifiedEpisodes',0)})
    print(json.dumps({'dispatchMode':'编排层据此调用对应代理，CLI不伪造代理执行或审核','actions':actions},ensure_ascii=False,indent=2))
p=argparse.ArgumentParser();p.add_argument('action',choices=['status','check-review','next','seal']);p.add_argument('--review');a=p.parse_args()
if a.action=='status':status()
elif a.action=='check-review':inspect_review(a.review)
elif a.action=='next':next_action()
else:seal()
