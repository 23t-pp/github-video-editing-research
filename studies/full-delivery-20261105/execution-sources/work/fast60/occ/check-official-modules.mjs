import {pathToFileURL} from 'node:url';
process.env.OPENCHATCUT_DATA_DIR='C:/Users/PC/.openchatcut/dev-profiles/4bcb4e74-803a-4abe-8dbc-a4d40dea37c3';
process.env.OPENCHATCUT_DEV_PROFILE_ID='4bcb4e74-803a-4abe-8dbc-a4d40dea37c3';
const repo='C:/Users/PC/Desktop/OpenChatCut-main',imported=[];
for(const p of ['src/persist/sharedKv.ts','src/persist/projectTransfer.ts','server/plugins/project-store.ts']){
 const m=await import(pathToFileURL(repo+'/'+p).href);imported.push({path:p,exports:Object.keys(m).filter(k=>/buildProjectExport|importProjectPackage|configureSharedKvBackend|getStoredEntry|setStoredEntry/.test(k))});
}
console.log(JSON.stringify({readOnlyModuleLoad:true,node:process.version,Blob:typeof Blob,File:typeof File,imported}));
