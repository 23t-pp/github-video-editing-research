import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {work,repo,output,origin,profileId,dataDir,statePath,save,read,occ,tool,httpEntry,doc} from './client.mjs';
const hash=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
const report={createdAt:new Date().toISOString(),phase:'read-only-preflight',browserOpened:false,cuaUsed:false};
const marker=read(path.join(repo,'.git/openchatcut-dev-profile.json'));assert.equal(marker.profileId,profileId);
const where=occ('profile',['where']);assert.equal(where.profileId,profileId);assert.equal(where.mode,'isolated-dev');
report.profile=where;
const local=occ('projects-before',['project','list']);
const remote=(await httpEntry('projects')).value.filter(x=>!x.deletedAt);
assert.deepEqual(local.map(x=>x.id).sort(),remote.map(x=>x.id).sort(),'CLI/service project libraries differ; do not edit');
report.service={origin,status:200,cliHttpSameLibrary:true,projectCountBefore:local.length};
report.repoSha=spawnSync('git',['rev-parse','HEAD'],{cwd:repo,encoding:'utf8',windowsHide:true}).stdout.trim();
const catalog=occ('tools-catalog',['tools','ls']);
report.catalog=catalog.filter(x=>['import_assets','manage_timelines','edit_track','edit_item','update_item_props','manage_markers'].includes(x.name));
for(const name of ['import_assets','manage_timelines','edit_track','edit_item'])assert(catalog.some(x=>x.name===name&&x.headless),`Required headless tool unavailable: ${name}`);
let state;
if(fs.existsSync(statePath)){
 state=read(statePath);report.resume=true;
 assert(local.some(p=>p.id===state.projectId),'Recorded project disappeared');
}else{
 const beforeHashes={};for(const p of local){const entry=await httpEntry('project:'+p.id);assert(entry.found);beforeHashes[p.id]=hash(entry.value);}
 save(path.join(work,'prior-project-hashes.json'),beforeHashes);
 const name='速度与选择 · FAST60 · 逐镜可编辑 · 24fps';
 const created=occ('create-project',['project','new',name,'--size','1920x1080','--fps','24','--description','正式60秒作品工程；等待逐镜素材，保留独立scoreMix/sourceMix与HF替换层。']);
 assert(!local.some(p=>p.id===created.id));
 state={projectId:created.id,name,profileId,dataDir,origin,createdAt:new Date().toISOString(),phase:'created-empty',timelineId:null,tracks:{},assets:[]};
 save(statePath,state);
}
tool('name-timeline','manage_timelines',{action:'update',name:'01 正式剪辑 · 60秒 · 24fps'},state.projectId);
let snapshot=doc(state.projectId);let timeline=snapshot.timelines.find(t=>t.id===snapshot.activeTimelineId);
assert.equal(timeline.width,1920);assert.equal(timeline.height,1080);assert.equal(timeline.fps,24);
state.timelineId=timeline.id;
assert(timeline.items.length===0,'Preflight may not repopulate a project after media insertion');
const definitions=[
 ['base','video','V1 主画面 · 每镜独立'],
 ['hfInsert','video','V2 HF特效插片 · 可替换'],
 ['titles','video','V3 标题/图形 · 可替换'],
 ['score','audio','A1 原创配乐 · scoreMix'],
 ['source','audio','A2 源片声音 · sourceMix']
];
for(const [key,kind,name] of definitions){
 let found=Object.entries(timeline.tracks||{}).find(([id,cfg])=>cfg.name===name);
 if(!found&&key==='base'){
  const candidate=timeline.trackOrder.find(id=>timeline.tracks[id]?.kind==='video'&&!timeline.tracks[id]?.name);assert(candidate);
  tool('name-base','edit_track',{action:'update',trackId:candidate,json:JSON.stringify({name,muted:false,locked:false})},state.projectId);
 }else if(!found){tool('track-'+key,'edit_track',{action:'create',json:JSON.stringify({trackType:kind,name,count:1})},state.projectId);}
 snapshot=doc(state.projectId);timeline=snapshot.timelines.find(t=>t.id===state.timelineId);
 found=Object.entries(timeline.tracks||{}).find(([id,cfg])=>cfg.name===name);assert(found,`Track missing: ${name}`);state.tracks[key]=found[0];save(statePath,state);
}
const httpDoc=await httpEntry('project:'+state.projectId);assert.deepEqual(httpDoc.value,snapshot);
const previous=read(path.join(work,'prior-project-hashes.json'));const preserved=[];
for(const [id,prior] of Object.entries(previous)){const entry=await httpEntry('project:'+id);assert(entry.found);const now=hash(entry.value);assert.equal(now,prior,`Old project ${id} changed during task`);preserved.push(id);}
state.phase='tracks-ready-awaiting-formal-media';state.url=`${origin}/#/editor/${state.projectId}`;save(statePath,state);
report.phase=state.phase;report.projectId=state.projectId;report.projectUrl=state.url;report.timelineId=timeline.id;report.tracks=Object.entries(timeline.tracks).map(([id,t])=>({id,...t}));
report.timeline={width:timeline.width,height:timeline.height,fps:timeline.fps,items:timeline.items.length,durationVerified:false,reason:'正式素材尚未加入；不把空工程称为60秒验证通过'};
report.previousProjectDocsUnchanged=preserved;report.cliHttpDocEqual=true;
report.officialPackaging={exportFunction:'src/persist/projectTransfer.ts buildProjectExport()',importFunction:'src/persist/projectTransfer.ts importProjectPackage()',plannedFormat:'openchatcut-project@2',willUseOfficialCodec:true,exported:false,importVerified:false};
save(path.join(work,'preflight.json'),report);save(path.join(output,'工程准备状态.json'),report);
console.log(JSON.stringify({phase:report.phase,projectId:state.projectId,url:state.url,tracks:Object.keys(state.tracks),previousProjectsPreserved:preserved.length,cliHttpDocEqual:true,waiting:'outputs/fast60/hyperframes/edit.json and final media'}));
