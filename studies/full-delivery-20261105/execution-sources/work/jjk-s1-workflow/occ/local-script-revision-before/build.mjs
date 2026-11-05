import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {root,work,output,read,save,statePath,profileId,dataDir,origin,occ,tool,doc,httpEntry} from './client.mjs';
import {loadManifest,fileFor,hash,manifestPath} from './manifest.mjs';
import {requireAuthorization} from './task-config.mjs';
const withHf=process.argv.includes('--hf'),reviseNative=process.argv.includes('--revise-native'),m=loadManifest({hf:withHf,probe:true});
requireAuthorization(withHf?'hf':'native',manifestPath);
let state;
if(fs.existsSync(statePath)){state=read(statePath);if(!reviseNative)assert.equal(state.nativeManifestSha256,m.nativeManifestSha256,'Native manifest changed after import; review and explicitly revise this project with --revise-native');}
else{
 const where=occ('profile',['where']);assert.equal(where.profileId,profileId);
 const list=occ('projects-before',['project','list']),prior={};for(const old of list){const e=await httpEntry('project:'+old.id);assert(e.found);prior[old.id]=hashJson(e.value);}save(path.join(work,'prior-project-hashes.json'),prior);
 const p=occ('create-s1-project',['project','new',m.title,'--size',`${m.width}x${m.height}`,'--fps',String(m.fps)]);assert(!list.some(x=>x.id===p.id));state={projectId:p.id,name:m.title,profileId,dataDir,origin,url:`${origin}/#/editor/${p.id}`,phase:'created',manifestPath,manifestSha256:m.manifestSha256,nativeManifestSha256:m.nativeManifestSha256,createdAt:new Date().toISOString()};save(statePath,state);
}
function hashJson(v){return crypto.createHash('sha256').update(JSON.stringify(v)).digest('hex');}
let project=doc(state.projectId);
const wanted=[...m.videos.keys(),m.master],missing=wanted.filter(f=>!project.assets.some(a=>a.name===path.basename(f)&&a.sourceContentHash===hash(f)));
if(missing.length){const r=tool('import-manifest-media','import_assets',{paths:missing},state.projectId);assert.equal(r.errors?.length||0,0);}
async function sequence(role,rows,name){
 project=doc(state.projectId);
 const idKey=role+'TimelineId',tracksKey=role+'Tracks';
 if(!state[idKey]){
  if(role==='native'){state[idKey]=project.activeTimelineId;tool('name-native-sequence','manage_timelines',{action:'update',timelineId:state[idKey],name},state.projectId);}
  else{const r=tool('create-hf-sequence','manage_timelines',{action:'create',name,width:m.width,height:m.height,activate:true},state.projectId);state[idKey]=r.created[0].id;}
  save(statePath,state);
 }
 tool('activate-'+role,'manage_timelines',{action:'switch',timelineId:state[idKey]},state.projectId);
 project=doc(state.projectId);let tl=project.timelines.find(t=>t.id===state[idKey]);assert.equal(tl.fps,m.fps);
 state[tracksKey]??={base:tl.trackOrder.find(id=>tl.tracks[id].kind==='video')};const tracks=state[tracksKey];assert(tracks.base);
 if(!tracks.master){tool('create-'+role+'-master','edit_track',{action:'create',json:JSON.stringify({trackType:'audio',count:1,name:'A1 曲库V20 · 独立master'})},state.projectId);project=doc(state.projectId);tl=project.timelines.find(t=>t.id===state[idKey]);tracks.master=Object.entries(tl.tracks).find(([id,t])=>t.kind==='audio'&&t.name==='A1 曲库V20 · 独立master')?.[0];assert(tracks.master);save(statePath,state);}
 tool('name-'+role+'-base','edit_track',{action:'update',trackId:tracks.base,json:JSON.stringify({name:role==='native'?`V1 原生逐镜 · ${rows.length}镜`:`V1 HF效果预合成 · ${rows.length}段`,muted:false,locked:false})},state.projectId);
 project=doc(state.projectId);tl=project.timelines.find(t=>t.id===state[idKey]);
 const assetFor=f=>{const a=project.assets.filter(a=>a.name===path.basename(f)&&a.sourceContentHash===hash(f));assert.equal(a.length,1,f);return a[0];};
 const adds=[],revisions=[],revisionChanges=[];for(const s of rows){const a=assetFor(fileFor(s.asset)),old=tl.items.find(i=>i.track===tracks.base&&i.startFrame===s.startFrame);if(old){assert.equal(old.durationInFrames,s.frames,'Revision must preserve cut duration');if(old.sourceAssetId!==a.id||(old.srcInFrame??0)!==(s.assetStartFrame??0)){assert(role==='native'&&reviseNative,'Revision requires --revise-native and native role');revisions.push({type:'video',itemId:old.id,assetId:a.id,sourceStartFrame:s.assetStartFrame??0,sourceDurationInFrames:s.frames});revisionChanges.push({id:s.id,itemId:old.id,before:{assetFilename:project.assets.find(a=>a.id===old.sourceAssetId)?.name,assetStartFrame:old.srcInFrame??0},after:{assetFilename:a.name,assetStartFrame:s.assetStartFrame??0},startFrame:s.startFrame,frames:s.frames});}}else adds.push({type:'video',assetId:a.id,track:tracks.base,fromFrame:s.startFrame,sourceStartFrame:s.assetStartFrame??0,sourceDurationInFrames:s.frames});}
 if(!tl.items.some(i=>i.track===tracks.master))adds.push({type:'audio',assetId:assetFor(m.master).id,track:tracks.master,fromFrame:0,sourceStartFrame:0,sourceDurationInFrames:m.durationFrames});
 if(adds.length)tool('place-'+role+'-clips-and-master','edit_item',{adds},state.projectId);
 if(revisions.length)tool('apply-final-native-revisions','edit_item',{updates:revisions},state.projectId);
 project=doc(state.projectId);tl=project.timelines.find(t=>t.id===state[idKey]);tool(role+'-volumes','edit_item',{updates:tl.items.filter(i=>['video','audio'].includes(i.kind)).map(i=>({type:i.kind,itemId:i.id,volume:i.kind==='audio'?1:0}))},state.projectId);
 if(role==='native'&&(m.nativeTexts||[]).length){
  if(!tracks.text){tool('create-native-text-track','edit_track',{action:'create',json:JSON.stringify({trackType:'video',count:1,name:'V2 原生可编辑文字'})},state.projectId);project=doc(state.projectId);tl=project.timelines.find(t=>t.id===state[idKey]);tracks.text=Object.entries(tl.tracks).find(([id,t])=>t.name==='V2 原生可编辑文字')?.[0];assert(tracks.text);save(statePath,state);}
  project=doc(state.projectId);tl=project.timelines.find(t=>t.id===state[idKey]);const textAdds=[];
  for(const t of m.nativeTexts){if(!tl.items.some(i=>i.track===tracks.text&&i.startFrame===t.startFrame&&i.props?.text===t.text)){const row={type:'text',track:tracks.text,fromFrame:t.startFrame,durationInFrames:t.frames,name:t.id,text:t.text};for(const k of ['fontSize','color','fontWeight','align'])if(t[k]!==undefined)row[k]=t[k];row.fontSize=Math.min(row.fontSize||36,36);textAdds.push(row);}}
  if(textAdds.length)tool('place-native-texts','edit_item',{adds:textAdds},state.projectId);
  project=doc(state.projectId);tl=project.timelines.find(t=>t.id===state[idKey]);const updates=[];for(const t of m.nativeTexts){const i=tl.items.find(i=>i.track===tracks.text&&i.startFrame===t.startFrame&&i.props?.text===t.text);assert(i);const u={type:'text',itemId:i.id,durationInFrames:t.frames,transform:{x:0,y:42,...(t.transform||{})}};for(const k of ['keyframes','props'])if(t[k]!==undefined)u[k]=t[k];updates.push(u);}if(updates.length)tool('animate-native-texts','edit_item',{updates},state.projectId);
  project=doc(state.projectId);tl=project.timelines.find(t=>t.id===state[idKey]);for(const t of m.nativeTexts){const i=tl.items.find(i=>i.track===tracks.text&&i.startFrame===t.startFrame&&i.props?.text===t.text);assert(i);assert.equal(i.durationInFrames,t.frames,`${t.id} text duration`);assert.equal(i.props?.fontSize,Math.min(t.fontSize||36,36));}
 }
 project=doc(state.projectId);tl=project.timelines.find(t=>t.id===state[idKey]);const videos=tl.items.filter(i=>i.kind==='video').sort((a,b)=>a.startFrame-b.startFrame),audio=tl.items.filter(i=>i.kind==='audio');assert.equal(videos.length,rows.length);assert.equal(audio.length,1);assert.equal(audio[0].volume,1);assert.equal(audio[0].startFrame,0);assert.equal(audio[0].durationInFrames,m.durationFrames);let cursor=0;const clips=videos.map((i,n)=>{const s=rows[n];assert.equal(i.startFrame,cursor);assert.equal(i.durationInFrames,s.frames);assert.equal(i.srcInFrame??0,s.assetStartFrame??0);assert.equal(i.volume,0);cursor+=i.durationInFrames;return {id:s.id||`${role}-${n}`,asset:s.asset,assetFilename:project.assets.find(a=>a.id===i.sourceAssetId).name,itemId:i.id,startFrame:i.startFrame,frames:i.durationInFrames,assetStartFrame:i.srcInFrame??0};});assert.equal(cursor,m.durationFrames);assert.equal(tl.width,m.width);assert.equal(tl.height,m.height);
 return {timelineId:tl.id,name:tl.name,clips,revisionChanges,textClips:tl.items.filter(i=>i.kind==='text').length,textItems:tl.items.filter(i=>i.kind==='text').map(i=>({itemId:i.id,text:i.props?.text,startFrame:i.startFrame,frames:i.durationInFrames,fontSize:i.props?.fontSize,transform:i.transform})),nativeTextPolicy:'基础文字最大36px，下方安全区y=42%；复杂SVG文字、抠像及HF合成保留于HyperFrames',audio:{clips:1,volume:1,startFrame:0,frames:m.durationFrames,asset:'master.wav'}};
}
const native=await sequence('native',m.shots,`02 原生逐镜 · ${m.shots.length}镜 · 第一季`);state.timelineId=state.nativeTimelineId;state.nativeCount=m.shots.length;state.nativeTextCount=m.nativeTexts?.length||0;save(statePath,state);
save(path.join(output,'原生时间线核验.json'),{title:m.title,projectId:state.projectId,url:state.url,...native,shots:native.clips,width:m.width,height:m.height,fps:m.fps,durationFrames:m.durationFrames,durationSeconds:m.durationFrames/m.fps,manifestSha256:m.manifestSha256,officialPackagePending:true});
let hf;
if(withHf){const nativeBefore=structuredClone(doc(state.projectId).timelines.find(t=>t.id===state.nativeTimelineId));hf=await sequence('hf',m.hfChunks,`01 HF完整效果 · ${m.hfChunks.length}段可替换`);project=doc(state.projectId);assert.deepEqual(project.timelines.find(t=>t.id===state.nativeTimelineId),nativeBefore);assert.equal(project.timelines.length,2);state.hfCount=m.hfChunks.length;state.phase='final-hf-and-native-verified';}else state.phase='native-verified-awaiting-hf';
project=doc(state.projectId);assert.deepEqual((await httpEntry('project:'+state.projectId)).value,project);state.manifestSha256=m.manifestSha256;state.nativeManifestSha256=m.nativeManifestSha256;
const prior=read(path.join(work,'prior-project-hashes.json'));for(const [id,h]of Object.entries(prior)){assert.equal(hashJson((await httpEntry('project:'+id)).value),h,`Existing project ${id} changed`);}
save(path.join(output,'工程Doc.json'),project);save(path.join(output,'时间线核验.json'),{title:m.title,projectId:state.projectId,activeTimelineId:project.activeTimelineId,nativeTimelineId:state.nativeTimelineId,hfTimelineId:state.hfTimelineId,nativeCount:m.shots.length,hfCount:m.hfChunks?.length||0,native,hf,width:m.width,height:m.height,fps:m.fps,durationFrames:m.durationFrames,durationSeconds:m.durationFrames/m.fps,mediaAssets:project.assets.length,oldProjectsPreserved:Object.keys(prior).length,officialPackagePending:true,verifiedAt:new Date().toISOString()});save(statePath,state);console.log(JSON.stringify({projectId:state.projectId,url:state.url,phase:state.phase,nativeCount:state.nativeCount,hfCount:state.hfCount,fps:m.fps,frames:m.durationFrames}));
