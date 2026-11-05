import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {pathToFileURL} from 'node:url';
const work=import.meta.dirname,state=JSON.parse(fs.readFileSync(path.join(work,'state.json'),'utf8'));
process.env.OPENCHATCUT_DATA_DIR=state.dataDir;process.env.OPENCHATCUT_DEV_PROFILE_ID=state.profileId;
const store=await import(pathToFileURL('C:/Users/PC/Desktop/OpenChatCut-main/server/plugins/project-store.ts').href);
const id='1d4f864c-09e1-4937-882c-66ebe421aa57';assert.notEqual(id,state.projectId);assert.notEqual(id,state.importedProjectId);
const e=await store.getStoredEntry('project:'+id);
if(e.found){assert.equal(e.value.activeTimelineId,state.hfTimelineId);assert.equal(e.value.timelines.length,2);assert.equal(e.value.assets.length,48);await store.deleteStoredEntry('project:'+id);}
assert.equal((await store.getStoredEntry('project:'+id)).found,false);
fs.writeFileSync(path.join(work,'failed-import-cleanup.json'),JSON.stringify({failedImportId:id,sourceAndSuccessfulImportNotTouched:true,removedFromActiveLibrary:true,method:'official server.deleteStoredEntry(project:new-failed-id)',verifiedAt:new Date().toISOString()},null,2));
console.log(JSON.stringify({removedFailedImport:id,successfulImport:state.importedProjectId}));
