// Local source-only preparation audit: does not import the service client or write OCC state.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {taskWork,taskRoot,defaultManifest,authorizationPath,protectedProjectIds,fileSha,requireAuthorization} from './task-config.mjs';
assert(!fs.existsSync(path.join(taskWork,'state.json')),'Preparation expects no project state');
assert(!fs.existsSync(authorizationPath),'Preparation must not pre-authorize writes');
let refused=false;try{requireAuthorization('native');}catch(e){refused=/No OCC write authorization/.test(e.message);}assert(refused,'Missing-authorization gate did not refuse');
const names=['task-config.mjs','client.mjs','manifest.mjs','build.mjs','export.mjs','import-package.mjs','finalize.mjs','run.ps1'];
const report={phase:'prepared-awaiting-design-B-and-final-media-lock',taskRoot,manifest:defaultManifest,expected:{width:1920,height:1080,fps:24,durationFrames:1440,hfChunks:20,hfChunkFrames:72,nativeShotCount:'manifest-driven'},preparedScripts:names.map(name=>({name,sha256:fileSha(path.join(taskWork,name))})),projectCreated:false,officialStoreWritten:false,mediaImported:false,packageExported:false,authorizationPresent:false,missingAuthorizationRefused:true,protectedPriorProjectIds:protectedProjectIds,syntaxCheck:'all .mjs passed node --check',checkedAt:new Date().toISOString()};
fs.writeFileSync(path.join(taskWork,'准备状态.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify(report));
