// Run through the repository's existing tsx loader. Reuses official exporter;
// this process gets a GET-only backend and cannot write the running library.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const work=import.meta.dirname,workspace=path.resolve(work,'../../..'),repo='C:/Users/PC/Desktop/OpenChatCut-main';
const state=JSON.parse(await fs.readFile(path.join(work,'state.json'),'utf8'));
assert.equal(state.phase,'final-hf-and-native-verified','Both complete formal timelines must be verified before package export');
const final=true;
const origin='http://127.0.0.1:5199';
const requests=[];
// Browser Blob streams normally chunk bounded media. Node 24 can emit a whole
// 17MB WAV at once, exceeding the official stream parser's 16MB JSON-line cap.
// This process-local Blob adapter changes only stream chunk boundaries; all
// format records and bytes still come from the unmodified official exporter.
class BoundedBlob extends Blob {
 stream(){let offset=0;const source=this;return new ReadableStream({async pull(c){if(offset>=source.size){c.close();return;}const end=Math.min(offset+65536,source.size);const bytes=await source.slice(offset,end).arrayBuffer();offset=end;c.enqueue(new Uint8Array(bytes));}});}
}
const nativeFetch=globalThis.fetch;
globalThis.fetch=async(input,init={})=>{
 const value=typeof input==='string'||input instanceof URL?String(input):input.url;
 const url=new URL(value,origin);
 const method=(init.method||(input instanceof Request?input.method:'GET')).toUpperCase();
 assert.equal(url.origin,origin,'Exporter may only fetch the running local service');
 assert.equal(method,'GET','Export adapter forbids network writes');
 assert(url.pathname==='/api/project-store/entry'||url.pathname.startsWith('/media/uploads/'),'Unexpected export endpoint');
 const headers=new Headers(init.headers);headers.set('Sec-Fetch-Site','none');
 requests.push({method,path:url.pathname+(url.pathname.startsWith('/api/')?url.search:'')});
 const response=await nativeFetch(url,{...init,method,headers});
 if(url.pathname.startsWith('/media/uploads/'))Object.defineProperty(response,'blob',{value:async()=>new BoundedBlob([await response.arrayBuffer()],{type:response.headers.get('content-type')||'application/octet-stream'})});
 return response;
};
const source=rel=>pathToFileURL(path.join(repo,rel)).href;
const kv=await import(source('src/persist/sharedKv.ts'));
const transfer=await import(source('src/persist/projectTransfer.ts'));
const forbid=async()=>{throw new Error('Export backend is read-only');};
kv.configureSharedKvBackend({
 async get(key){assert(key.includes(state.projectId),'Read outside the newly created project is forbidden');const res=await fetch(`${origin}/api/project-store/entry?key=${encodeURIComponent(key)}`);assert.equal(res.status,200);const e=await res.json();return e.found?e.value:undefined;},
 set:forbid,delete:forbid,keys:forbid,writeAgentRuntime:forbid,updateAgentRunLease:forbid,
});
const response=await fetch(`${origin}/api/project-store/entry?key=${encodeURIComponent('project:'+state.projectId)}`);const {found,value:doc}=await response.json();assert.equal(found,true);
assert(doc.timelines.some(t=>t.id===state.timelineId));
const tl=doc.timelines.find(t=>t.id===state.nativeTimelineId);assert(tl);assert.equal(tl.fps,25);assert.equal(Math.max(...tl.items.map(i=>i.startFrame+i.durationInFrames)),750);assert.equal(tl.items.filter(i=>i.kind==='audio').length,1);assert.equal(tl.items.filter(i=>i.kind==='video').length,32);
assert.equal(doc.timelines.length,2);assert.equal(doc.activeTimelineId,state.hfTimelineId);const hf=doc.timelines.find(t=>t.id===state.hfTimelineId);assert(hf);assert.equal(hf.items.length,16);assert.equal(tl.items.length,33);assert.equal(hf.fps,25);assert.equal(Math.max(...hf.items.map(i=>i.startFrame+i.durationInFrames)),750);assert.equal(hf.items.filter(i=>i.kind==='audio').length,1);assert(doc.assets.every(a=>a.src?.startsWith('/media/uploads/')&&a.durationInFrames>0),'All assets must be committed media');
const result=await transfer.buildProjectExport(state.projectId,state.name);
assert.equal(result.mediaMissing.length,0,'Official exporter reports missing media');
const bytes=Buffer.from(await result.blob.arrayBuffer());
const lines=bytes.toString('utf8').trimEnd().split('\n');
const manifest=JSON.parse(lines[0]);assert.equal(manifest.format,'openchatcut-project@2');assert.equal(manifest.type,'manifest');
assert(!JSON.stringify(manifest.doc).includes('originalFilePath'),'Portable Doc leaked desktop-only source paths');
assert.equal(manifest.doc.timelines.length,doc.timelines.length);
const allSrcs=transfer.collectUploadSrcs(manifest.doc);const carried=[];let current=null;const mediaChecks=[];
for(const line of lines.slice(1)){
 assert(line.length<=16*1024*1024,'Stream line too large');const row=JSON.parse(line);
 if(row.type==='media-start'){assert(!current);assert(row.bytes>0&&row.bytes<=512*1024*1024);current={...row,parts:[]};}
 else if(row.type==='media-chunk'){assert(current);current.parts.push(Buffer.from(row.data,'base64'));}
 else if(row.type==='media-end'){assert(current);assert.equal(row.src,current.src);const actual=Buffer.concat(current.parts);assert.equal(actual.length,current.bytes);const fetched=await fetch(origin+current.src);assert.equal(fetched.status,200);const canonical=Buffer.from(await fetched.arrayBuffer());assert(actual.equals(canonical),'Carried bytes differ from running service');carried.push(current.src);mediaChecks.push({src:current.src,name:current.name,mime:current.mime,bytes:actual.length,sha256:crypto.createHash('sha256').update(actual).digest('hex')});current=null;}
}
assert(!current);assert(allSrcs.every(src=>carried.includes(src)),'A ProjectDoc media reference was not carried');assert.equal(new Set(carried).size,carried.length);assert.equal(result.mediaTotal,carried.length);
const packagePath=final?path.join(workspace,'outputs/reference-replay-next/openchatcut',result.filename):null;
if(packagePath)await fs.writeFile(packagePath,bytes);
const report={method:'Official src/persist/projectTransfer.ts buildProjectExport(), via documented injected SharedKvBackend seam with GET-only local HTTP reads; no reimplemented package encoder',mode:final?'final':'preflight',projectId:state.projectId,nativeTimelineId:state.timelineId,hfTimelineId:state.hfTimelineId,activeTimelineId:manifest.doc.activeTimelineId,format:manifest.format,bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),timelines:manifest.doc.timelines.map(t=>({id:t.id,name:t.name,items:t.items.length,fps:t.fps,durationFrames:Math.max(...t.items.map(i=>i.startFrame+i.durationInFrames))})),mediaTotal:result.mediaTotal,mediaMissing:result.mediaMissing,mediaChecks,packagePath,writesToLibrary:0,uiImportVerified:false,readRequests:requests,verifiedAt:new Date().toISOString()};
await fs.writeFile(path.join(work,'occ-portable-verification.json'),JSON.stringify(report,null,2));
await fs.writeFile(path.join(workspace,'outputs/reference-replay-next/openchatcut/官方工程包验证.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({mode:report.mode,projectId:state.projectId,bytes:report.bytes,format:report.format,mediaTotal:result.mediaTotal,mediaMissing:result.mediaMissing,packagePath,uiImportVerified:false}));
