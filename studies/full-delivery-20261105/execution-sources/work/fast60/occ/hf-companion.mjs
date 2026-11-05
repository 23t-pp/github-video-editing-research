import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
import {root,work,output,read,save,statePath,doc,tool,httpEntry} from './client.mjs';
const state=read(statePath),edit=read(path.join(root,'outputs/fast60/hyperframes/edit.json'));
assert(['native-effects-verified-awaiting-ui','hf-companion-building','hf-companion-verified'].includes(state.phase));
const fx=[{id:'title',startFrame:7,frames:68},{id:'triptych',startFrame:675,frames:45},{id:'end',startFrame:1418,frames:22}].map(s=>({...s,file:path.join(root,`outputs/fast60/occ-effects/FX-${s.id}.mp4`)}));
for(const f of fx){
 const r=spawnSync('C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe',['-v','error','-count_frames','-show_streams','-of','json',f.file],{encoding:'utf8',windowsHide:true});assert.equal(r.status,0,r.stderr);const p=JSON.parse(r.stdout),v=p.streams.find(s=>s.codec_type==='video');assert.equal(v.width,1920);assert.equal(v.height,1080);assert.equal(v.avg_frame_rate,'24/1');assert.equal(Number(v.nb_read_frames||v.nb_frames),f.frames);assert(!p.streams.some(s=>s.codec_type==='audio'));
 f.sha256=crypto.createHash('sha256').update(fs.readFileSync(f.file)).digest('hex');
}
let p=doc(state.projectId);
const nativeBefore=structuredClone(p.timelines.find(t=>t.id===state.timelineId));assert(nativeBefore);
const missing=fx.filter(f=>!p.assets.some(a=>a.name===path.basename(f.file)&&a.sourceContentHash===f.sha256));
if(missing.length){const r=tool('import-hf-precise-clips','import_assets',{paths:missing.map(f=>f.file)},state.projectId);assert.equal(r.errors?.length||0,0);}
tool('rename-native-mother','manage_timelines',{action:'update',timelineId:state.timelineId,name:'02 原生可编辑 · 改字/分栏/42镜'},state.projectId);
if(!state.hfTimelineId){
 const result=tool('duplicate-hf-companion','manage_timelines',{action:'duplicate',timelineId:state.timelineId,name:'01 HF精确特效 · 42镜逐镜可剪',activate:true},state.projectId);
 state.hfTimelineId=result.duplicated.id;assert(state.hfTimelineId);state.phase='hf-companion-building';save(statePath,state);
}else tool('activate-hf-companion','manage_timelines',{action:'switch',timelineId:state.hfTimelineId},state.projectId);
p=doc(state.projectId);let tl=p.timelines.find(t=>t.id===state.hfTimelineId);assert.equal(p.activeTimelineId,tl.id);
const baseTrack=Object.entries(tl.tracks).find(([id,t])=>t.name==='V1 主画面 · 每镜独立')?.[0];assert(baseTrack);
let effectTrack=Object.entries(tl.tracks).find(([id,t])=>t.name==='HF 精确插片 · 可逐段替换')?.[0];
if(!effectTrack){tool('create-hf-companion-track','edit_track',{action:'create',json:JSON.stringify({trackType:'video',count:1,name:'HF 精确插片 · 可逐段替换'})},state.projectId);p=doc(state.projectId);tl=p.timelines.find(t=>t.id===state.hfTimelineId);effectTrack=Object.entries(tl.tracks).find(([id,t])=>t.name==='HF 精确插片 · 可逐段替换')?.[0];}assert(effectTrack);
const remove=tl.items.filter(i=>i.track!==baseTrack&&i.kind!=='audio'&&i.track!==effectTrack);
if(remove.length)tool('remove-native-overlays-from-hf-copy','edit_item',{deletes:remove.map(i=>({type:i.kind,itemId:i.id,ripple:false}))},state.projectId);
p=doc(state.projectId);tl=p.timelines.find(t=>t.id===state.hfTimelineId);
const adds=[];
for(const f of fx){
 const a=p.assets.find(a=>a.name===path.basename(f.file)&&a.sourceContentHash===f.sha256);assert(a);f.assetId=a.id;
 if(!tl.items.some(i=>i.track===effectTrack&&i.startFrame===f.startFrame))adds.push({type:'video',assetId:a.id,track:effectTrack,fromFrame:f.startFrame,sourceStartFrame:0,sourceDurationInFrames:f.frames});
}
if(adds.length)tool('add-precise-hf-overlays','edit_item',{adds},state.projectId);
p=doc(state.projectId);tl=p.timelines.find(t=>t.id===state.hfTimelineId);
tool('hf-copy-video-volumes-and-single-endfade','edit_item',{updates:tl.items.filter(i=>i.kind==='video').map(i=>({type:'video',itemId:i.id,volume:0,...(i.track===baseTrack&&i.startFrame===1350?{clearKeyframes:'opacity'}:{})}))},state.projectId);
p=doc(state.projectId);tl=p.timelines.find(t=>t.id===state.hfTimelineId);
const nativeAfter=p.timelines.find(t=>t.id===state.timelineId);assert.deepEqual({...nativeAfter,name:nativeBefore.name},nativeBefore,'HF integration changed native master edits');
assert.equal(tl.fps,24);assert.equal(tl.width,1920);assert.equal(tl.height,1080);assert.equal(Math.max(...tl.items.map(i=>i.startFrame+i.durationInFrames)),1440);assert.equal(tl.items.filter(i=>i.track===baseTrack).length,42);assert.equal(tl.items.filter(i=>i.kind==='audio').length,2);assert.equal(tl.items.filter(i=>i.track===effectTrack).length,3);assert(tl.items.filter(i=>i.kind==='video').every(i=>i.volume===0));
const shots=tl.items.filter(i=>i.track===baseTrack).sort((a,b)=>a.startFrame-b.startFrame).map(i=>{
 const a=p.assets.find(a=>a.id===i.sourceAssetId);assert(a);const id=/^(S\d{2})\.mp4$/.exec(a.name)?.[1];assert(id,`Not a formal shot: ${a.name}`);
 return {id,startFrame:i.startFrame,frames:i.durationInFrames,assetStartFrame:i.srcInFrame??0,itemId:i.id,sourceAssetId:a.id,assetFilename:a.name,sourceContentHash:a.sourceContentHash};
});
let cursor=0;for(const s of shots){assert.equal(s.startFrame,cursor);cursor+=s.frames;const e=edit.shots.find(x=>x.id===s.id);assert(e);for(const k of ['startFrame','frames','assetStartFrame'])assert.equal(s[k],e[k],`${s.id}.${k} actual native doc differs from edit`);}assert.equal(cursor,1440);
const report={title:edit.title,projectId:state.projectId,timelineId:tl.id,sequenceId:tl.id,sequenceName:tl.name,activeTimelineId:p.activeTimelineId,fps:24,width:1920,height:1080,durationFrames:1440,durationSeconds:60,units:'Read actual ProjectDoc native integer frames; timeline and all shot assets are 24fps; no seconds-to-frames inference.',shots,hfClips:tl.items.filter(i=>i.track===effectTrack).sort((a,b)=>a.startFrame-b.startFrame).map(i=>({name:p.assets.find(a=>a.id===i.sourceAssetId)?.name,startFrame:i.startFrame,frames:i.durationInFrames,assetStartFrame:i.srcInFrame??0,itemId:i.id})),nativeTimelineId:state.timelineId,source:'Official CLI project show --doc and running HTTP project store deep-equal readback',matchesEditJson:true,verifiedAt:new Date().toISOString()};
assert.deepEqual((await httpEntry('project:'+state.projectId)).value,p);save(path.join(output,'时间线核验.json'),report);save(path.join(output,'正式工程Doc.json'),p);save(path.join(output,'HF对照验证.json'),{projectId:state.projectId,nativeTimelineId:state.timelineId,hfTimelineId:state.hfTimelineId,activeTimelineId:p.activeTimelineId,fx:fx.map(({file,...f})=>f),baseShotCount:42,stereoStems:2,frames:1440,actualUiPlaybackVerified:false});
state.phase='hf-companion-verified';save(statePath,state);console.log(JSON.stringify({projectId:state.projectId,nativeTimelineId:state.timelineId,hfTimelineId:state.hfTimelineId,shots:shots.length,frames:cursor,verification:path.join(output,'时间线核验.json')}));
