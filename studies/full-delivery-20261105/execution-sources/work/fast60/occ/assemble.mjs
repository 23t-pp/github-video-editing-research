// Formal media only. Re-runnable: pool entries and exact timeline slots are reused.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {root,work,output,statePath,save,read,tool,doc,httpEntry} from './client.mjs';
const editPath=path.resolve(process.argv.slice(2).find(a=>!a.startsWith('--'))||path.join(root,'outputs/fast60/hyperframes/edit.json'));
const edit=read(editPath), baseDir=path.dirname(editPath), state=read(statePath);
assert.equal(edit.width,1920);assert.equal(edit.height,1080);assert.equal(edit.fps,24);assert.equal(edit.durationFrames,1440);
const ffprobe='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe';
const hashes=new Map();const hashFor=file=>{if(!hashes.has(file))hashes.set(file,crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'));return hashes.get(file);};
function ensureAssets(files){
 let current=doc(state.projectId);
 const stale=current.assets.filter(a=>files.some(f=>a.name===path.basename(f)&&a.sourceContentHash!==hashFor(f)));
 if(stale.length){
  for(const a of stale)assert(!current.timelines.some(t=>t.items.some(i=>i.sourceAssetId===a.id)),'Stale staged pool asset is already used; explicit clip replacement required');
  throw new Error('Unused stale staged assets found. Run refresh-staged-pool.mjs through official tsx before formal assembly; current CLI does not expose manage_media_pool.');
 }
 const missing=files.filter(f=>!current.assets.some(a=>a.name===path.basename(f)&&a.sourceContentHash===hashFor(f)));
 if(missing.length){const imported=tool('import-formal-media','import_assets',{paths:missing},state.projectId);assert.equal(imported.errors?.length||0,0);}
 return doc(state.projectId);
}
function probe(file){
 assert(fs.existsSync(file),`Formal media not ready: ${file}`);
 const r=spawnSync(ffprobe,['-v','error','-count_frames','-show_streams','-show_format','-of','json',file],{encoding:'utf8',windowsHide:true,maxBuffer:32*1024*1024});
 assert.equal(r.status,0,r.stderr);return JSON.parse(r.stdout);
}
let cursor=0;const ids=new Set(),checks=[],media=new Map();
for(const shot of edit.shots){
 assert(!ids.has(shot.id),'Duplicate shot ID');ids.add(shot.id);
 for(const k of ['startFrame','frames','assetStartFrame'])assert(Number.isSafeInteger(shot[k])&&shot[k]>=0,`${shot.id}.${k}`);
 assert(shot.frames>0);assert.equal(shot.startFrame,cursor,`${shot.id} gap/overlap`);cursor+=shot.frames;
 const file=path.resolve(baseDir,shot.asset);assert(file.startsWith(baseDir+path.sep),'Asset escapes edit directory');
 if(!media.has(file))media.set(file,probe(file));
 const p=media.get(file),v=p.streams.find(s=>s.codec_type==='video');assert(v);
 assert.equal(v.width,1920);assert.equal(v.height,1080);assert.equal(v.avg_frame_rate,'24/1');
 const count=Number(v.nb_read_frames||v.nb_frames);assert(Number.isSafeInteger(count)&&count>=shot.assetStartFrame+shot.frames,`${shot.id}: source trim exceeds actual frames`);
 assert(!p.streams.some(s=>s.codec_type==='audio'),`${shot.id}: formal shot expected muted/no audio stream`);
 checks.push({id:shot.id,startFrame:shot.startFrame,frames:shot.frames,assetStartFrame:shot.assetStartFrame,actualAssetFrames:count,asset:shot.asset,film:shot.film,sourceIn:shot.sourceIn,label:shot.label});
}
assert.equal(cursor,1440);
save(path.join(work,'formal-shot-validation.json'),{editPath,shots:checks,frames:1440,fps:24,duration:60,validatedAt:new Date().toISOString()});
if(process.argv.includes('--stage-footage')){
 ensureAssets([...media.keys()]);
 state.phase='formal-footage-validated-in-pool-awaiting-stems';save(statePath,state);
 console.log(JSON.stringify({projectId:state.projectId,formalShotFiles:media.size,shots:checks.length,timelineFrames:cursor,placedOnTimeline:false}));process.exit(0);
}
const stems=['scoreMix','sourceMix'].map((name,index)=>{
 assert(edit.audio?.[name],`${name} path missing`);const file=path.resolve(baseDir,edit.audio[name]),p=probe(file),a=p.streams.find(s=>s.codec_type==='audio');assert(a);assert.equal(a.channels,2);
 const duration=Number(a.duration||p.format.duration);assert(Math.abs(duration-60)<1/48000,`${name}: WAV must be exactly 60s, got ${duration}`);
 return {name,file,track:state.tracks[index?'source':'score'],duration,sampleRate:Number(a.sample_rate),channels:a.channels};
});
save(path.join(work,'formal-media-validation.json'),{editPath,shots:checks,stems,frames:1440,fps:24,duration:60,validatedAt:new Date().toISOString()});
let project=doc(state.projectId),timeline=project.timelines.find(t=>t.id===state.timelineId);assert(timeline);
assert.equal(project.activeTimelineId,state.timelineId,'Formal assembly only targets the active native master; do not rerun after switching to its HF copy');
const files=[...media.keys(),...stems.map(s=>s.file)];
project=ensureAssets(files);timeline=project.timelines.find(t=>t.id===state.timelineId);
const assetFor=file=>{const matches=project.assets.filter(a=>a.name===path.basename(file)&&a.sourceContentHash===hashFor(file));assert.equal(matches.length,1,`Ambiguous/stale asset ${file}`);return matches[0];};
const adds=[];
for(const shot of edit.shots){
 const asset=assetFor(path.resolve(baseDir,shot.asset)),existing=timeline.items.filter(i=>i.track===state.tracks.base&&i.startFrame===shot.startFrame);
 if(existing.length){assert.equal(existing.length,1);assert.equal(existing[0].sourceAssetId,asset.id);assert.equal(existing[0].durationInFrames,shot.frames);assert.equal(existing[0].srcInFrame||0,shot.assetStartFrame);}
 else adds.push({type:'video',assetId:asset.id,track:state.tracks.base,fromFrame:shot.startFrame,sourceStartFrame:shot.assetStartFrame,sourceDurationInFrames:shot.frames});
}
for(const stem of stems){
 const asset=assetFor(stem.file),existing=timeline.items.filter(i=>i.track===stem.track);
 if(existing.length){assert.equal(existing.length,1);assert.equal(existing[0].sourceAssetId,asset.id);assert.equal(existing[0].startFrame,0);assert.equal(existing[0].durationInFrames,1440);}
 else adds.push({type:'audio',assetId:asset.id,track:stem.track,fromFrame:0,sourceStartFrame:0,sourceDurationInFrames:1440});
}
if(adds.length)tool('add-formal-clips','edit_item',{adds},state.projectId);
project=doc(state.projectId);timeline=project.timelines.find(t=>t.id===state.timelineId);
tool('formal-volumes','edit_item',{updates:timeline.items.filter(i=>['video','audio'].includes(i.kind)).map(i=>({type:i.kind,itemId:i.id,volume:i.kind==='video'?0:1}))},state.projectId);
project=doc(state.projectId);timeline=project.timelines.find(t=>t.id===state.timelineId);
assert.equal(Math.max(...timeline.items.map(i=>i.startFrame+i.durationInFrames)),1440);
assert.equal(timeline.items.filter(i=>i.track===state.tracks.base).length,edit.shots.length);
assert.equal(timeline.items.filter(i=>i.kind==='audio').length,2);
assert(timeline.items.filter(i=>i.kind==='video').every(i=>i.volume===0));
assert(timeline.items.filter(i=>i.kind==='audio').every(i=>i.volume===1&&i.startFrame===0&&i.durationInFrames===1440));
const remote=await httpEntry('project:'+state.projectId);assert(remote.found);assert.deepEqual(remote.value,project);
save(path.join(output,'正式工程Doc.json'),project);
const report={projectId:state.projectId,timelineId:state.timelineId,url:state.url,frames:1440,fps:24,durationSeconds:60,independentShotClips:edit.shots.length,shots:checks.map(s=>({...s,itemId:timeline.items.find(i=>i.track===state.tracks.base&&i.startFrame===s.startFrame).id})),stereoStems:stems.map(s=>({name:s.name,track:s.track,duration:s.duration,sampleRate:s.sampleRate})),allVideosMuted:true,audioClipsVolume:1,cliHttpDocEqual:true,hfIntegrationPending:true,officialPackagePending:true,actualUiPlaybackVerified:false,verifiedAt:new Date().toISOString()};
save(path.join(output,'逐镜装配验证.json'),report);state.phase='formal-shots-and-stems-verified';state.assets=project.assets.map(a=>({id:a.id,name:a.name,src:a.src}));save(statePath,state);
console.log(JSON.stringify({projectId:state.projectId,shots:edit.shots.length,stems:2,frames:1440,hfIntegrationPending:true}));
