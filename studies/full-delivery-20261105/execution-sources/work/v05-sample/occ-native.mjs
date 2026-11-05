import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';

const work=import.meta.dirname;
const workspace=path.resolve(work,'../..');
const repo='C:/Users/PC/Desktop/OpenChatCut-main';
const node='C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe';
const profileId='4bcb4e74-803a-4abe-8dbc-a4d40dea37c3';
const dataDir=`C:/Users/PC/.openchatcut/dev-profiles/${profileId}`;
const out=path.join(workspace,'outputs/v05-six-panel/openchatcut');
fs.mkdirSync(work,{recursive:true});fs.mkdirSync(out,{recursive:true});
let sequence=0;
function occ(label,args){
 const argv=[path.join(repo,'node_modules/tsx/dist/cli.mjs'),path.join(repo,'cli/main.ts'),...args,'--data-dir',dataDir,'--json'];
 const r=spawnSync(node,argv,{cwd:repo,env:{...process.env,OPENCHATCUT_DEV_PROFILE_ID:profileId},encoding:'utf8',windowsHide:true,maxBuffer:64*1024*1024});
 const stem=`${String(++sequence).padStart(2,'0')}-${label}`;
 fs.writeFileSync(path.join(work,`${stem}.command.json`),JSON.stringify({executable:node,argv,cwd:repo,profileId,dataDir,exit:r.status,signal:r.signal},null,2));
 fs.writeFileSync(path.join(work,`${stem}.stdout.json`),r.stdout||'');
 fs.writeFileSync(path.join(work,`${stem}.stderr.txt`),r.stderr||'');
 assert.equal(r.status,0,`${label}: ${r.stderr}`);
 let data;try{data=JSON.parse(r.stdout);}catch{throw new Error(`${label}: stdout not JSON`);}
 for(const op of data.ops||[])assert(!op.result?.error,`${label}/${op.tool}: ${JSON.stringify(op.result)}`);
 return data;
}
function argsFile(name,value){const file=path.join(work,`${name}.json`);fs.writeFileSync(file,JSON.stringify(value,null,2));return `@${file}`;}
function tool(label,name,args,id){const r=occ(label,['tools','call',name,'--project',id,'--args',argsFile(label,args),'--apply']);assert.equal(r.applied,true,`${label}: not applied`);return r.ops[0].result;}
const stateFile=path.join(work,'occ-native-state.json');
assert(!fs.existsSync(stateFile),'State exists; refuse to create a second project. Resume explicitly using its recorded UUID.');
const where=occ('profile',['where']);assert.equal(where.profileId,profileId);assert.equal(where.mode,'isolated-dev');
const meta=JSON.parse(fs.readFileSync(path.join(repo,'.git/openchatcut-dev-profile.json'),'utf8'));assert.equal(meta.profileId,profileId);
const before=occ('projects-before',['project','list']);
const http=await fetch('http://127.0.0.1:5199/api/project-store/entry?key=projects',{headers:{'Sec-Fetch-Site':'none'}});assert.equal(http.status,200);
const httpProjects=(await http.json()).value.filter(x=>!x.deletedAt);
assert.deepEqual(before.map(x=>x.id).sort(),httpProjects.map(x=>x.id).sort(),'CLI and running service target different libraries');
const name=`V05六格卡片学习小样-${new Date().toISOString().replace(/[:.]/g,'-')}`;
const project=occ('create',['project','new',name,'--size','1920x1080','--fps','24']);
assert(!before.some(x=>x.id===project.id));
const state={projectId:project.id,name,profileId,dataDir,createdAt:new Date().toISOString(),phase:'created',nativeTimelineId:null};
function saveState(){fs.writeFileSync(stateFile,JSON.stringify(state,null,2));}
saveState();console.log(JSON.stringify({created:project.id,name}));
const a=path.join(workspace,'outputs/v05-six-panel/hyperframes/assets/shot-a-road.mp4');
const b=path.join(workspace,'outputs/v05-six-panel/hyperframes/assets/shot-b-driver-aerial.mp4');
for(const f of [a,b])assert(fs.statSync(f).size>0);
const imported=tool('import-shots','import_assets',{paths:[a,b]},project.id);assert.equal(imported.errors?.length||0,0);assert.equal(imported.imported.length,2);
state.assets=imported.imported;state.phase='imported';saveState();
tool('rename-native','manage_timelines',{action:'update',name:'01 OCC原生六格教学 · 24fps'},project.id);
tool('create-panel-tracks','edit_track',{action:'create',json:JSON.stringify({trackType:'video',count:6,name:'六格独立片段'})},project.id);
let snapshot=occ('empty-doc',['project','show',project.id,'--doc']);
let timeline=snapshot.doc.timelines.find(x=>x.id===snapshot.doc.activeTimelineId);
state.nativeTimelineId=timeline.id;state.trackOrder=timeline.trackOrder;saveState();
assert.equal(timeline.fps,24);assert.equal(timeline.trackOrder.length,7);
const base='track_v1';assert(timeline.trackOrder.includes(base));
const panels=timeline.trackOrder.filter(x=>x!==base);
const aAsset=snapshot.doc.assets.find(x=>x.name==='shot-a-road.mp4');
const bAsset=snapshot.doc.assets.find(x=>x.name==='shot-b-driver-aerial.mp4');
assert(aAsset&&bAsset);
const adds=[{type:'video',assetId:aAsset.id,track:base,fromFrame:0,sourceStartFrame:0,sourceDurationInFrames:48},...panels.map(track=>({type:'video',assetId:bAsset.id,track,fromFrame:30,sourceStartFrame:0,sourceDurationInFrames:18})),{type:'video',assetId:bAsset.id,track:base,fromFrame:48,sourceStartFrame:18,sourceDurationInFrames:60}];
tool('add-native-items','edit_item',{adds},project.id);
snapshot=occ('added-doc',['project','show',project.id,'--doc']);timeline=snapshot.doc.timelines.find(x=>x.id===state.nativeTimelineId);
assert.equal(timeline.items.length,8);
const cueForCell=[0,4,8,2,6,10];
const updates=timeline.items.map(item=>{
 if(item.track===base)return {type:'video',itemId:item.id,volume:0,...(item.startFrame===48?{fadeOutSeconds:6/24}:{})};
 const cell=panels.indexOf(item.track);assert(cell>=0);
 const col=cell%3,row=Math.floor(cell/3),cue=cueForCell[cell];
 const opacity=[{frame:0,value:0}];if(cue>0)opacity.push({frame:cue,value:0});opacity.push({frame:cue+2,value:1});
 const shift=row===0?-0.8:0.8;
 const y=[{frame:0,value:shift,easing:'easeOut'}];if(cue>0)y.push({frame:cue,value:shift,easing:'easeOut'});y.push({frame:cue+3,value:0});
 return {type:'video',itemId:item.id,volume:0,transform:{scale:0.72,x:0,y:0,crop:{left:col*640,right:(2-col)*640,top:row*540,bottom:(1-row)*540}},keyframes:{opacity,y}};
});
tool('style-native-items','edit_item',{updates},project.id);
snapshot=occ('native-doc-final',['project','show',project.id,'--doc']);timeline=snapshot.doc.timelines.find(x=>x.id===state.nativeTimelineId);
assert.equal(timeline.items.length,8);assert.equal(timeline.width,1920);assert.equal(timeline.height,1080);assert.equal(timeline.fps,24);
assert.equal(Math.max(...timeline.items.map(i=>i.startFrame+i.durationInFrames)),108);
const checks=[];
for(let cell=0;cell<6;cell++){
 const item=timeline.items.find(i=>i.track===panels[cell]);assert(item);const c=cell%3,r=Math.floor(cell/3),cue=cueForCell[cell];
 assert.equal(item.startFrame,30);assert.equal(item.durationInFrames,18);assert.equal(item.srcInFrame||0,0);assert.equal(item.volume,0);assert.equal(item.transform.scale,0.72);
 const crop=item.transform.crop;for(const [key,n]of Object.entries({left:c/3,right:(2-c)/3,top:r/2,bottom:(1-r)/2}))assert(Math.abs((crop[key]||0)-n)<1e-8);
 assert.equal(item.keyframes.opacity.at(-1).frame,cue+2);assert.equal(item.keyframes.opacity.at(-1).value,1);assert.equal(item.keyframes.y.at(-1).frame,cue+3);assert.equal(item.keyframes.y.at(-1).value,0);
 checks.push({cell,track:item.track,itemId:item.id,cueLocalFrame:cue,crop,keyframes:item.keyframes});
}
const full=timeline.items.find(i=>i.track===base&&i.startFrame===48);assert.equal(full.srcInFrame,18);assert.equal(full.durationInFrames,60);assert.equal(full.fadeOutFrames,6);assert(timeline.items.every(i=>i.volume===0));
fs.writeFileSync(path.join(out,'原生工程Doc.json'),JSON.stringify(snapshot.doc,null,2));
fs.writeFileSync(path.join(out,'原生工程读取快照.json'),JSON.stringify(snapshot,null,2));
const verification={projectId:project.id,nativeTimelineId:timeline.id,fps:24,durationInFrames:108,itemCount:8,panelCount:6,checks,allNativeMediaMuted:true,fullBLastFadeFrames:full.fadeOutFrames,openedInUI:false,rendered:false,audioPending:true,hfIntegrationPending:true,portablePending:true,verifiedAt:new Date().toISOString()};
fs.writeFileSync(path.join(work,'occ-native-verification.json'),JSON.stringify(verification,null,2));
state.phase='native-verified';state.nativeChecks=verification;saveState();
console.log(JSON.stringify({projectId:project.id,timelineId:timeline.id,nativeVerified:true,doc:path.join(out,'原生工程Doc.json')}));
