import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {read,save,statePath,output,httpEntry} from './client.mjs';
const state=read(statePath);assert.equal(state.phase,'official-package-roundtrip-verified');
const portable=read(path.join(output,'官方工程包验证.json'));
const imported=read(path.join(output,'官方工程包导入回验.json'));
assert.equal(imported.mediaRestored,portable.mediaTotal);assert.equal(imported.mediaMissing.length,0);
const mediaById=new Map(imported.mediaChecks.map(m=>[m.assetId,m]));
const observed=[];
for(const [role,id] of [['source',state.projectId],['officialImportedCopy',state.importedProjectId]]){
 const row=await httpEntry('project:'+id);assert(row.found);const doc=row.value;
 assert.equal(doc.timelines.length,2);assert.equal(doc.assets.length,45);
 const sequences=[];
 for(const tl of doc.timelines){
  assert.equal(tl.fps,25);assert.equal(tl.width,1920);assert.equal(tl.height,1080);
  const videos=tl.items.filter(i=>i.kind==='video').sort((a,b)=>a.startFrame-b.startFrame),audio=tl.items.filter(i=>i.kind==='audio');
  assert.equal(audio.length,1);assert.equal(audio[0].startFrame,0);assert.equal(audio[0].durationInFrames,750);assert.equal(audio[0].volume,1);
  assert.equal(videos.length,tl.id===state.nativeTimelineId?32:15);
  let cursor=0;for(const i of videos){assert.equal(i.startFrame,cursor);cursor+=i.durationInFrames;assert.equal(i.volume,0);}
  assert.equal(cursor,750);
  for(const i of tl.items){const a=doc.assets.find(a=>a.id===i.sourceAssetId);assert(a);assert.equal(i.src,a.src);assert(a.durationInFrames>=(i.srcInFrame??0)+i.durationInFrames);}
  sequences.push({id:tl.id,name:tl.name,fps:tl.fps,width:tl.width,height:tl.height,frames:cursor,seconds:cursor/tl.fps,videoClips:videos.length,audioClips:audio.length,contiguousVideo:true,allMediaLinked:true,allVideoMuted:true});
 }
 if(role==='officialImportedCopy')for(const a of doc.assets){assert(mediaById.get(a.id)?.packageBytesMatch,`No successful media read/hash for ${a.name}`);}
 observed.push({role,id,assets:doc.assets.length,sequences});
}
const report={projectId:state.projectId,importedProjectId:state.importedProjectId,packageFilename:path.basename(portable.packagePath),packageBytes:portable.bytes,packageSha256:portable.sha256,packageFormat:portable.format,mediaAssets:45,mediaAvailableAndByteVerified:45,mediaMissing:[],observed,method:'Live HTTP ProjectDoc readback plus official exporter/importer SHA256 per-media byte verification. Media readiness means upload URLs are readable and package bytes match; subjective UI playback and audio audition are recorded separately.',actualUiPlaybackVerified:false,actualUiDragVerified:false,actualUiAudioAuditionVerified:false,verifiedAt:new Date().toISOString()};
save(path.join(output,'工程包最终回读.json'),report);
for(const name of ['原生时间线核验.json','时间线核验.json']){const f=path.join(output,name),r=read(f);r.exactHfSequencePending=false;r.officialPackagePending=false;r.officialPackageRoundTripVerified=true;r.importedProjectId=state.importedProjectId;save(f,r);}
const readme=path.join(output,'README_工程说明.md');let text=fs.readFileSync(readme,'utf8');
text=text.replace('## 打开工程',`## 已核验的工程包\n\n- 文件：${path.basename(portable.packagePath)}\n- 大小：${portable.bytes.toLocaleString('en-US')}字节；格式：${portable.format}。\n- 45项媒体全部随包并已通过官方导入器恢复，缺失0项；导入后逐媒体SHA256与导出源一致。\n- [当前原工程](${state.url}) · [工程包真实导入的验证副本](${state.importedProjectUrl})。这两个地址需要本机5199服务正在运行；跨机器请使用ccproj导入。\n\n## 打开工程`);
fs.writeFileSync(readme,text);
console.log(JSON.stringify({sourceProjectId:state.projectId,importedProjectId:state.importedProjectId,mediaAssets:45,mediaMissing:0,sequences:observed[1].sequences,report:path.join(output,'工程包最终回读.json')}));
