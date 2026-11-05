// Official draft commands + official saveProject/renameProject over a restricted
// process-local SharedKv backend. CLI 0.2.17 does not expose manage_media_pool.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {pathToFileURL} from 'node:url';
const work=import.meta.dirname,root=path.resolve(work,'../../..'),state=JSON.parse(fs.readFileSync(path.join(work,'state.json'),'utf8')),repo='C:/Users/PC/Desktop/OpenChatCut-main';
process.env.OPENCHATCUT_DATA_DIR=state.dataDir;process.env.OPENCHATCUT_DEV_PROFILE_ID=state.profileId;
const load=rel=>import(pathToFileURL(path.join(repo,rel)).href);
const storage=await load('server/plugins/project-store.ts'),kv=await load('src/persist/sharedKv.ts'),projects=await load('src/persist/projectStore.ts'),editor=await load('src/editor/store.ts');
const before=(await storage.getStoredEntry('project:'+state.projectId)).value,index=(await storage.getStoredEntry('projects')).value;
assert(before.timelines.every(t=>t.items.length===0),'Only unused staging pool can be refreshed');
fs.writeFileSync(path.join(work,'before-staged-refresh.doc.json'),JSON.stringify(before,null,2));fs.writeFileSync(path.join(work,'before-staged-refresh.index.json'),JSON.stringify(index,null,2));
const forbid=async()=>{throw new Error('Unsupported persistence operation');};
kv.configureSharedKvBackend({async get(key){assert(key==='projects'||key.includes(state.projectId));const r=await storage.getStoredEntry(key);return r.found?r.value:undefined;},async set(key,value){assert(key==='projects'||key==='project:'+state.projectId);if(key==='projects')for(const m of index.filter(x=>x.id!==state.projectId))assert.deepEqual(value.find(x=>x.id===m.id),m);await storage.setStoredEntry(key,value);},delete:forbid,keys:forbid,writeAgentRuntime:forbid,updateAgentRunLease:forbid});
const editPath=path.join(root,'outputs/fast60/hyperframes/edit.json'),edit=JSON.parse(fs.readFileSync(editPath,'utf8')),base=path.dirname(editPath),hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const stale=before.assets.filter(a=>edit.shots.some(s=>a.name===path.basename(s.asset)&&a.sourceContentHash!==hash(path.resolve(base,s.asset))));
const draft=editor.makeDraft(before);if(stale.length)draft.commands.removeMediaAssets(stale.map(a=>a.id));
assert.deepEqual(draft.getDoc().timelines,before.timelines);const saved=await projects.saveProject(state.projectId,draft.getDoc());assert.equal(saved.saved,true);
state.name='弯心 APEX · 速度与激情一分钟混剪';await projects.renameProject(state.projectId,state.name);fs.writeFileSync(path.join(work,'state.json'),JSON.stringify(state,null,2));
const actual=(await storage.getStoredEntry('project:'+state.projectId)).value;assert.equal(actual.assets.length,before.assets.length-stale.length);
const report={method:'official makeDraft.commands.removeMediaAssets + saveProject + renameProject via guarded injected SharedKvBackend',removedUnusedStaleAssets:stale.map(a=>({id:a.id,name:a.name,oldHash:a.sourceContentHash})),projectId:state.projectId,name:state.name,allExistingTimelinesPreserved:true,oldProjectsNotWritten:true};fs.writeFileSync(path.join(work,'staged-refresh.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
