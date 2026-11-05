"""Synthetic dispatcher fixtures only; no agent invocation, real UI or film pass claim."""
from pathlib import Path
import ast,json,hashlib,zipfile,subprocess,sys,difflib
D=Path(__file__).resolve().parent;R=D.parents[1];source=R/'scripts/workflow.py';tree=ast.parse(source.read_text(encoding='utf-8'));nodes=[]
for n in tree.body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='p' for t in n.targets):break
 nodes.append(n)
ns={'__file__':str(source),'__name__':'dispatch_fixture'};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),ns)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(r,name,value):
 p=r/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
def load(r,name):return json.loads((r/name).read_text(encoding='utf-8'))
def binding(r,names):return {n:sha(r/n) for n in names}
common=['咒力接力_一分钟.mp4','hyperframes/edit.json','openchatcut/工程包最终回读.json','data/hyperframes-package-verification.json'];ui_path='evidence/ui/最终交付界面验收.json';package='openchatcut/test.ccproj';loop_review='loops/loop-04/review.json'
def fixture(name):
 r=D/'fixtures'/name;r.mkdir(parents=True,exist_ok=True)
 for path,data in [('咒力接力_一分钟.mp4',b'SYNTHETIC_NOT_A_MOVIE'),('hyperframes/edit.json',b'{}'),('hyperframes/index.html',b'<html>fixture</html>\n'),('music/master.wav',b'SYNTHETIC_NOT_AUDIO'),(package,b'SYNTHETIC_PACKAGE'*800)]:
  p=r/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 execution={'sha256':sha(r/'咒力接力_一分钟.mp4'),'editSha256':sha(r/'hyperframes/edit.json'),'executor':'render-agent'}
 media={'assetId':'a','sha256':sha(r/'music/master.wav'),'bytes':(r/'music/master.wav').stat().st_size,'packageBytesMatch':True}
 seq={'frames':1440,'fps':24,'width':1920,'height':1080,'contiguousVideo':True,'allMediaLinked':True,'allVideoMuted':True,'allPreparedPlaybackRateOne':True}
 occ={'projectId':'source','importedProjectId':'imported','packageFilename':'test.ccproj','packageBytes':(r/package).stat().st_size,'packageSha256':sha(r/package),'packageFormat':'openchatcut-project@2','mediaAssets':1,'mediaAvailableAndByteVerified':1,'mediaMissing':[],'observed':[{'role':role,'id':id,'assets':1,'sequences':[seq,seq]} for role,id in [('source','source'),('officialImportedCopy','imported')]],'actualImportedMaster':{'sampleFrames':2880000,'sampleRate':48000,'sha256':sha(r/'music/master.wav')}}
 save(r,'openchatcut/工程包最终回读.json',occ);save(r,'openchatcut/官方工程包验证.json',{'sha256':occ['packageSha256'],'bytes':occ['packageBytes'],'mediaTotal':1,'format':'openchatcut-project@2','mediaChecks':[media]});save(r,'openchatcut/官方工程包导入回验.json',{'sourceProjectId':'source','importedProjectId':'imported','mediaRestored':1,'mediaMissing':[],'editStructureEqual':True,'sourceProjectUnchanged':True,'mediaChecks':[media]})
 members={n:{'sha256':sha(r/n),'bytes':(r/n).stat().st_size} for n in ['hyperframes/index.html','hyperframes/edit.json']}
 archive=r/'HyperFrames可编辑工程.zip'
 with zipfile.ZipFile(archive,'w') as z:
  for n in members:z.write(r/n,n)
 save(r,'data/hyperframes-package-verification.json',{'state':'pass','archive':archive.name,'archiveBytes':archive.stat().st_size,'archiveSha256':sha(archive),'movieSha256':execution['sha256'],'editSha256':execution['editSha256'],'crcPassed':True,'eachArchivedFileShaVerified':True,'files':members})
 save(r,'成片质量检查.json',{'fullDecodedFrames':1440,'decodedAudioSampleFrames':2880000,'width':1920,'height':1080,'sha256':execution['sha256'],'sameTimeCorrelation':.999})
 save(r,ui_path,{'state':'pass','moviePlaybackVerified':True,'hyperframesVerified':True,'openchatcutVerified':True,'noAuditoryClaim':True,'boundArtifacts':binding(r,common)})
 save(r,loop_review,{'status':'pass','reviewer':'audit-agent'})
 required=[*common,ui_path,archive.name,package,loop_review];save(r,'reviews/最终验收.json',{'status':'pass','reviewer':'audit-agent','boundArtifacts':binding(r,required)})
 return r,execution
rows=[]
def check(name,stage,mutate=lambda r,e:None,code=None):
 r,e=fixture(name);mutate(r,e);ns['ROOT']=r;actual=ns['_final_delivery_dispatch'](e,r/'loops/loop-04');assert actual['stage']==stage,(name,actual)
 if code:assert any(x['code']==code for a in actual['actions'] for x in a.get('reasons',[])),(name,actual)
 assert actual['actions'],name;rows.append({'case':name,'expectedStage':stage,'actual':actual,'pass':True})
def change(r,path,key,value):
 j=load(r,path);j[key]=value;save(r,path,j)
check('01_missing_occ','OCC_pending',lambda r,e:(r/'openchatcut/工程包最终回读.json').unlink(),'missing_report')
check('02_occ_missing_media_even_count_claims_pass','OCC_pending',lambda r,e:change(r,'openchatcut/工程包最终回读.json','mediaMissing',['lost']),'occ_missing_or_unverified_media')
check('03_occ_empty_per_media_hashes','OCC_pending',lambda r,e:change(r,'openchatcut/官方工程包导入回验.json','mediaChecks',[]),'occ_per_media_hash_evidence_incomplete')
check('04_occ_package_changed','OCC_pending',lambda r,e:(r/package).write_bytes(b'CHANGED'),'artifact_hash_or_size_changed')
check('05_occ_malformed_master','OCC_pending',lambda r,e:change(r,'openchatcut/工程包最终回读.json','actualImportedMaster',None),'occ_imported_master_not_current')
check('06_missing_zip_report','UI_delivery_pending',lambda r,e:(r/'data/hyperframes-package-verification.json').unlink(),'missing_report')
def changed_zip(r,e):
 archive=r/'HyperFrames可编辑工程.zip'
 with zipfile.ZipFile(archive,'w') as z:z.writestr('hyperframes/index.html',b'altered');z.write(r/'hyperframes/edit.json','hyperframes/edit.json')
 report=load(r,'data/hyperframes-package-verification.json');report.update(archiveBytes=archive.stat().st_size,archiveSha256=sha(archive));save(r,'data/hyperframes-package-verification.json',report)
check('07_zip_member_changed_even_new_archive_hash','UI_delivery_pending',changed_zip,'hf_archived_member_changed')
check('08_ui_exists_true_but_empty_bindings','UI_delivery_pending',lambda r,e:change(r,ui_path,'boundArtifacts',{}),'empty_review_bindings')
check('09_ui_boolean_failure','UI_delivery_pending',lambda r,e:change(r,ui_path,'moviePlaybackVerified',False),'final_ui_evidence_not_pass')
def stale_ui(r,e):
 j=load(r,ui_path);j['boundArtifacts']['咒力接力_一分钟.mp4']='0'*64;save(r,ui_path,j)
check('10_ui_stale_binding','UI_delivery_pending',stale_ui,'stale_or_missing_binding')
check('11_quality_report_wrong_frame_count','UI_delivery_pending',lambda r,e:change(r,'成片质量检查.json','fullDecodedFrames',1439),'final_movie_quality_report_failed_or_stale')
check('12_final_status_pass_empty_bindings','final_acceptance_pending',lambda r,e:change(r,'reviews/最终验收.json','boundArtifacts',{}),'empty_review_bindings')
check('13_final_not_independent','final_acceptance_pending',lambda r,e:change(r,'reviews/最终验收.json','reviewer','render-agent'),'final_acceptance_not_independent_pass')
def stale_final(r,e):
 j=load(r,'reviews/最终验收.json');j['boundArtifacts'][package]='0'*64;save(r,'reviews/最终验收.json',j)
check('14_final_stale_package_binding','final_acceptance_pending',stale_final,'stale_or_missing_binding')
check('15_all_reviews_pass_but_not_sealed','seal_pending',code='missing_report')
def delivered(r,e):save(r,'workflow/delivered.json',{'state':'delivered','loops':[{'sha256':str(i)} for i in range(3)]+[{'sha256':e['sha256']}]})
check('16_sealed_current_complete','complete',delivered)
check('17_delivered_file_is_not_completion','seal_pending',lambda r,e:save(r,'workflow/delivered.json',{'state':'not_delivered','loops':[]}),'delivered_state_stale')
before=(D/'workflow-before.py').read_text(encoding='utf-8');current=source.read_text(encoding='utf-8');oldfunctions={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(before).body if isinstance(n,ast.FunctionDef)};newfunctions={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(current).body if isinstance(n,ast.FunctionDef)};changed=[n for n in oldfunctions if oldfunctions[n]!=newfunctions[n]];assert changed==['next_action'],changed
(D/'workflow.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),current.splitlines(True),fromfile='workflow-before.py',tofile='scripts/workflow.py')),encoding='utf-8')
run=subprocess.run([sys.executable,'-X','utf8',str(source),'next'],capture_output=True);assert run.returncode==0,run.stderr;(D/'next-after.stdout.json').write_bytes(run.stdout);(D/'next-after.stderr.txt').write_bytes(run.stderr)
real=json.loads(run.stdout);assert real['actions'] and real.get('stage') in ['OCC_pending','UI_delivery_pending','final_acceptance_pending','seal_pending','complete'],real
report={'scope':'17 isolated synthetic dispatch fixtures only; no real agent called/UI passed/seal executed by these fixtures. Real current next captured separately.','fixtures':rows,'pass':True,'changedExistingFunctions':changed,'sealAstUnchanged':oldfunctions['seal']==newfunctions['seal'],'workflowSha256':sha(source),'realCurrentDispatch':real,'realNextExitCode':run.returncode};(D/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'fixturesPassed':len(rows),'changedExistingFunctions':changed,'sealAstUnchanged':True,'realStage':real.get('stage'),'workflowSha256':sha(source)},ensure_ascii=False))
