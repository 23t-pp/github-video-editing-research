import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
export const work=import.meta.dirname;
export const root=path.resolve(work,'../../..');
export const output=path.join(root,'outputs/fast60/openchatcut');
export const repo='C:/Users/PC/Desktop/OpenChatCut-main';
export const node='C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe';
export const profileId='4bcb4e74-803a-4abe-8dbc-a4d40dea37c3';
export const dataDir=`C:/Users/PC/.openchatcut/dev-profiles/${profileId}`;
export const origin='http://127.0.0.1:5199';
fs.mkdirSync(output,{recursive:true});
export const statePath=path.join(work,'state.json');
export const save=(file,data)=>fs.writeFileSync(file,JSON.stringify(data,null,2));
export const read=file=>JSON.parse(fs.readFileSync(file,'utf8').replace(/^\uFEFF/,''));
export function occ(label,args){
 const stamp=new Date().toISOString().replace(/[:.]/g,'-');
 const argv=[path.join(repo,'node_modules/tsx/dist/cli.mjs'),path.join(repo,'cli/main.ts'),...args,'--data-dir',dataDir,'--json'];
 const r=spawnSync(node,argv,{cwd:repo,env:{...process.env,OPENCHATCUT_DEV_PROFILE_ID:profileId},encoding:'utf8',windowsHide:true,maxBuffer:128*1024*1024});
 const stem=path.join(work,`${stamp}-${label}`);
 save(stem+'.command.json',{executable:node,argv,cwd:repo,profileId,dataDir,exit:r.status,signal:r.signal});
 fs.writeFileSync(stem+'.stdout.json',r.stdout||'');fs.writeFileSync(stem+'.stderr.txt',r.stderr||'');
 assert.equal(r.status,0,`${label}: ${r.stderr}`);
 let parsed;try{parsed=JSON.parse(r.stdout);}catch{throw new Error(`${label}: stdout not JSON`);}
 for(const op of parsed.ops||[])assert(!op.result?.error,`${label}/${op.tool}: ${JSON.stringify(op.result)}`);
 return parsed;
}
export function argsFile(name,value){const f=path.join(work,`${name}.args.json`);save(f,value);return '@'+f;}
export function tool(label,name,args,projectId,{apply=true}={}){
 assert(projectId,'Explicit new projectId required');
 const state=read(statePath);assert.equal(projectId,state.projectId,'Only this task\'s project may be edited');
 const result=occ(label,['tools','call',name,'--project',projectId,'--args',argsFile(label,args),...(apply?['--apply']:[])]);
 if(apply)assert.equal(result.applied,true);
 return result.ops[0].result;
}
export async function httpEntry(key){const url=`${origin}/api/project-store/entry?key=${encodeURIComponent(key)}`;const r=await fetch(url,{headers:{'Sec-Fetch-Site':'none'},signal:AbortSignal.timeout(10000)});assert.equal(r.status,200,`HTTP entry ${key}: ${r.status}`);return r.json();}
export const doc=projectId=>occ('show-doc',['project','show',projectId,'--doc']).doc;
