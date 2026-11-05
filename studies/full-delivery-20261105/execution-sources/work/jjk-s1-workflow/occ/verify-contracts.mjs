// Local tests only, using the installed official parser and index merge code.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {reframeToOcc} from './native-reframe.mjs';
import {assertTaskWriteTarget,classifyPriorProjectHashes} from './project-protection.mjs';
import {defaultManifest,protectedProjectIds,taskWork} from './task-config.mjs';
const repo='C:/Users/PC/Desktop/OpenChatCut-main';
const source=rel=>pathToFileURL(path.join(repo,rel)).href;
const {parseTransformArg}=await import(source('src/agent/tools/edit-item-visual.ts'));
const {mergeProjectIndex}=await import(source('server/plugins/project-store-entries.ts'));
const plan=JSON.parse(fs.readFileSync(defaultManifest,'utf8'));let maxTranslationError=0,maxPointError=0;
const reframes=[];
for(const s of plan.shots){
 const input=s.reframe||{x:0,y:0,scale:1},transform=reframeToOcc(input,plan.width,plan.height);
 const parsed=parseTransformArg(transform,{width:plan.width,height:plan.height});assert(!parsed.error,parsed.error);assert.deepEqual(parsed.transform,transform);
 const dx=transform.x/100*plan.width-(input.x||0),dy=transform.y/100*plan.height-(input.y||0);maxTranslationError=Math.max(maxTranslationError,Math.abs(dx),Math.abs(dy));
 for(const [x,y] of [[0,0],[960,540],[1920,1080],[350,710]]){
  const hf=[960+(x-960)*(input.scale??1)+(input.x||0),540+(y-540)*(input.scale??1)+(input.y||0)];
  const occ=[960+(x-960)*parsed.transform.scale+parsed.transform.x/100*plan.width,540+(y-540)*parsed.transform.scale+parsed.transform.y/100*plan.height];
  const err=Math.max(Math.abs(hf[0]-occ[0]),Math.abs(hf[1]-occ[1]));maxPointError=Math.max(maxPointError,err);assert(err<=.6,'Reframe unit/quantization error exceeds .6 canvas px');
 }
 reframes.push({id:s.id,pixels:input,occTransform:transform,translationQuantizationErrorPixels:{x:dx,y:dy}});
}
for(const bad of [{x:NaN},{y:Infinity},{scale:0},{x:1920*5}])assert.throws(()=>reframeToOcc(bad));
const prior=Object.fromEntries([...protectedProjectIds.map(id=>[id,'fixed-hash']),['external-v3','v3-before']]);
assertTaskWriteTarget('new-s1-uuid','new-s1-uuid',prior,protectedProjectIds);
for(const id of [...protectedProjectIds,'external-v3'])assert.throws(()=>assertTaskWriteTarget(id,id,prior,protectedProjectIds));
assert.throws(()=>assertTaskWriteTarget('external-v3','new-s1-uuid',prior,protectedProjectIds));
const drift=classifyPriorProjectHashes(prior,{...prior,'external-v3':'v3-after'},protectedProjectIds);assert.equal(drift.externalConcurrentChanges.length,1);assert.equal(drift.externalConcurrentChanges[0].action,'record_only_no_restore_no_overwrite');
assert.throws(()=>classifyPriorProjectHashes(prior,{...prior,[protectedProjectIds[0]]:'unexpected-change'},protectedProjectIds));
const currentIndex=[{id:'external-v3',name:'合法并行新版',updatedAt:500},{id:protectedProjectIds[0],name:'固定旧工程',updatedAt:100}];
const ownOnly=[{id:'new-import-uuid',name:'S1验证副本',updatedAt:600}];
const merged=mergeProjectIndex(currentIndex,ownOnly);for(const row of currentIndex)assert.deepEqual(merged.find(r=>r.id===row.id),row);assert.deepEqual(merged.find(r=>r.id==='new-import-uuid'),ownOnly[0]);
assert(!fs.existsSync(path.join(taskWork,'state.json')));assert(!fs.existsSync(path.join(taskWork,'authorization.json')));
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const sources=['src/agent/tools/edit-item-visual.ts','src/geometry/placement.ts','server/plugins/project-store.ts','server/plugins/project-store-entries.ts'];
const result={status:'pass_local_contract_only',checkedAt:new Date().toISOString(),manifestSha256:sha(defaultManifest),reframeCount:reframes.length,nonIdentityReframes:reframes.filter(r=>r.pixels.scale!==1||r.pixels.x!==0||r.pixels.y!==0).length,maxTranslationQuantizationErrorPixels:maxTranslationError,maxProjectedAnchorErrorPixels:maxPointError,officialParserAcceptedAll:true,invalidTransformInputsRejected:true,oldProjectUUIDReuseRejected:true,externalConcurrentDriftRecordedOnly:true,fixedProtectedDriftStopsWithoutRestore:true,officialIndexOwnOnlyMergePreservesExternalEntries:true,sourceProof:sources.map(rel=>({file:path.join(repo,rel),sha256:sha(path.join(repo,rel))})),reframes,serviceCalls:0,serviceWrites:0,projectCreated:false,authorizationCreated:false,pending:'Actual official edit_item write/readback and imported-copy readback await root final media lock.'};
fs.writeFileSync(path.join(taskWork,'本地reframe与保护契约验证.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify({status:result.status,reframes:result.reframeCount,nonIdentityReframes:result.nonIdentityReframes,maxProjectedAnchorErrorPixels:maxPointError,protectedTests:'passed',officialIndexMerge:'passed',serviceWrites:0}));
