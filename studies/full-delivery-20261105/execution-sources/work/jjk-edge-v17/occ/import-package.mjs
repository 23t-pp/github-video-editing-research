// Run using the official repository's tsx loader. No package codec is reimplemented.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {loadManifest} from './manifest.mjs';
const edit=loadManifest({hf:true});
const work=import.meta.dirname,root=path.resolve(work,'../../..'),out=path.join(root,'outputs/jjk-edge-v17/openchatcut');
const read=async f=>JSON.parse(await fs.readFile(f,'utf8'));
const state=await read(path.join(work,'state.json')),portable=await read(path.join(work,'occ-portable-verification.json'));
assert(!state.importedProjectId,'Official package already imported; use existing copy rather than make duplicates');
process.env.OPENCHATCUT_DATA_DIR=state.dataDir;
process.env.OPENCHATCUT_DEV_PROFILE_ID=state.profileId;
const repo='C:/Users/PC/Desktop/OpenChatCut-main',origin=state.origin;
const source=rel=>pathToFileURL(path.join(repo,rel)).href;
const requests=[],nativeFetch=globalThis.fetch;
globalThis.fetch=async(input,init={})=>{
 const url=new URL(typeof input==='string'||input instanceof URL?String(input):input.url,origin);
 const method=(init.method||(input instanceof Request?input.method:'GET')).toUpperCase();
 assert.equal(url.origin,origin,'Only this running local OCC service may be accessed');
 assert((['GET','HEAD'].includes(method)&&url.pathname.startsWith('/media/uploads/'))||(['POST','DELETE'].includes(method)&&url.pathname==='/upload'),'Unexpected official import endpoint');
 const headers=new Headers(init.headers);headers.set('Sec-Fetch-Site','same-origin');headers.set('Origin',origin);requests.push({method,path:url.pathname});
 return nativeFetch(url,{...init,method,headers});
};
const store=await import(source('server/plugins/project-store.ts'));
const kv=await import(source('src/persist/sharedKv.ts'));
const transfer=await import(source('src/persist/projectTransfer.ts'));
const projects=await import(source('src/persist/projectStore.ts'));
const validation=await import(source('shared/project-store-validation.ts'));
const failedPath=path.join(work,'failed-import-ids.json');
let failedIds=[];try{failedIds=await read(failedPath);}catch{}
for(const id of failedIds){assert.notEqual(id,state.projectId);const row=await store.getStoredEntry('project:'+id);if(row.found){assert(row.value.timelines.some(t=>t.id===state.hfTimelineId),'Not this task failed import');await store.deleteStoredEntry('project:'+id);}}
const index=await store.getStoredEntry('projects');assert(index.found);const oldIds=new Set(index.value.map(x=>x.id));
const original=(await store.getStoredEntry('project:'+state.projectId)).value;
const hash=value=>crypto.createHash('sha256').update(JSON.stringify(value)).digest('hex');
const originalHash=hash(original),newIds=new Set(),writes=[];
function guard(key){
 assert(key!=='projects','Index guarded separately');
 const id=validation.projectIdFromProjectStoreKey(key);assert(id);assert(!oldIds.has(id),'Import backend refuses to change any existing project');
 if(key.startsWith('project:'))newIds.add(id);
 assert(newIds.has(id),'Only this import new-project sidecars can be written');
}
const forbid=async()=>{throw new Error('Runtime writes and store enumeration are not needed for this no-chat project import');};
kv.configureSharedKvBackend({
 async get(key){assert(key==='projects'||newIds.has(validation.projectIdFromProjectStoreKey(key))||key.startsWith('project:'),'Unexpected import backend read');const row=await store.getStoredEntry(key);return row.found?row.value:undefined;},
 async set(key,value){
  if(key==='projects'){
   assert(Array.isArray(value));for(const prior of index.value)assert.deepEqual(value.find(x=>x.id===prior.id),prior,'Existing project metadata changed');
   assert(value.some(x=>newIds.has(x.id)),'Index must add imported copy');
  }else guard(key);
  writes.push({operation:'set',key});await store.setStoredEntry(key,value);
 },
 async delete(key){guard(key);writes.push({operation:'delete',key});await store.deleteStoredEntry(key);},
 keys:forbid,async writeAgentRuntime(request){guard(request.key);writes.push({operation:'official-runtime-write',key:request.key});return store.writeAgentRuntime(request);},async updateAgentRunLease(request){guard(request.key);return store.updateStoredAgentRunLease(request);},
});
const bytes=await fs.readFile(portable.packagePath);assert.equal(bytes.length,portable.bytes);assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),portable.sha256);
const firstNewline=bytes.indexOf(10);assert(firstNewline>0);const manifest=JSON.parse(bytes.subarray(0,firstNewline).toString('utf8'));
let imported;
try{
 imported=await transfer.importProjectPackage(new Blob([bytes],{type:'application/octet-stream'}),{async publish(staged){
  const meta=await projects.createProject(staged.name+' · 工程包重开验证',staged.doc);
  // Server owns session generations. Initialize through its official rotation
  // function before the importer adopts the new generation and restores runtime.
  await store.rotateAgentSession(meta.id);
  if(staged.chat)await projects.saveChat(meta.id,staged.chat);
  if(staged.creativeMode)await projects.saveCreativeMode(meta.id,staged.creativeMode);
  return meta;
 }});
}catch(error){
 await fs.writeFile(failedPath,JSON.stringify([...newIds],null,2));
 for(const id of newIds)await store.deleteStoredEntry('project:'+id);
 throw error;
}
state.importedProjectId=imported.meta.id;state.importedProjectUrl=`${origin}/#/editor/${imported.meta.id}`;state.phase='official-import-created-audit-pending';await fs.writeFile(path.join(work,'state.json'),JSON.stringify(state,null,2));
assert(!oldIds.has(imported.meta.id));assert.equal(imported.mediaMissing.length,0);assert.equal(imported.mediaRestored,portable.mediaTotal);
const copy=(await store.getStoredEntry('project:'+imported.meta.id)).value;assert(copy);assert.equal(copy.timelines.length,2);const native=copy.timelines.find(t=>t.id===state.nativeTimelineId);assert.equal(native.items.filter(i=>i.kind==='video').length,edit.shots.length);assert(copy.assets.every(a=>a.src?.startsWith('/media/uploads/')&&a.durationInFrames>0));for(const tl of copy.timelines){assert.equal(tl.fps,edit.fps);assert.equal(Math.max(...tl.items.map(i=>i.startFrame+i.durationInFrames)),edit.durationFrames);assert.equal(tl.items.filter(i=>i.kind==='audio').length,1);}
assert.equal(hash((await store.getStoredEntry('project:'+state.projectId)).value),originalHash,'Source project changed during round trip');
const srcFree=value=>{const clone=structuredClone(value);for(const a of clone.assets){delete a.src;delete a.originalFilePath;}for(const t of clone.timelines)for(const i of t.items){delete i.src;delete i.originalFilePath;}return clone;};
assert.deepEqual(srcFree(copy),srcFree(manifest.doc),'Official import changed packaged edit structure');
const mediaChecks=[];
for(const a of copy.assets){
 const old=original.assets.find(x=>x.id===a.id);assert(old);const expected=portable.mediaChecks.find(m=>m.src===old.src);assert(expected);
 const r=await fetch(a.src);assert.equal(r.status,200);const b=Buffer.from(await r.arrayBuffer());const sha=crypto.createHash('sha256').update(b).digest('hex');assert.equal(sha,expected.sha256);assert.equal(b.length,expected.bytes);
 mediaChecks.push({assetId:a.id,name:a.name,bytes:b.length,sha256:sha,packageBytesMatch:true});
}
state.importedProjectId=imported.meta.id;state.importedProjectUrl=`${origin}/#/editor/${imported.meta.id}`;state.phase='official-package-roundtrip-verified';await fs.writeFile(path.join(work,'state.json'),JSON.stringify(state,null,2));
const report={method:'Official importProjectPackage(Blob,{publish}) host seam invokes official createProject and server.rotateAgentSession, then importer restores runtime through official server.writeAgentRuntime. Process-local guarded SharedKvBackend delegates ordinary reads/writes to official get/setStoredEntry. Official media uploader handles content-addressed media.',sourceProjectId:state.projectId,importedProjectId:imported.meta.id,importedProjectUrl:state.importedProjectUrl,format:'openchatcut-project@2',frames:edit.durationFrames,fps:edit.fps,durationSeconds:edit.durationFrames/edit.fps,mediaTotal:imported.mediaTotal,mediaRestored:imported.mediaRestored,mediaMissing:imported.mediaMissing,editStructureEqual:true,sourceProjectUnchanged:true,existingProjectDocumentsNotWritten:true,mediaChecks,requests,writes,actualUiPlaybackVerified:false,actualUiDragVerified:false,actualUiAudioAuditionVerified:false,verifiedAt:new Date().toISOString()};
await fs.writeFile(path.join(out,'官方工程包导入回验.json'),JSON.stringify(report,null,2));
await fs.writeFile(path.join(out,'导入副本Doc.json'),JSON.stringify(copy,null,2));
console.log(JSON.stringify({importedProjectId:imported.meta.id,url:state.importedProjectUrl,mediaRestored:imported.mediaRestored,editStructureEqual:true,uiPlaybackVerified:false}));
