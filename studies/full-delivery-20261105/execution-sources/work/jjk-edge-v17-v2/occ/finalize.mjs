import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {read,save,statePath,output,httpEntry} from './client.mjs';
import {loadManifest} from './manifest.mjs';
const m=loadManifest({hf:true}),state=read(statePath);assert.equal(state.phase,'official-package-roundtrip-verified');
const portable=read(path.join(output,'官方工程包验证.json')),imported=read(path.join(output,'官方工程包导入回验.json'));
assert.equal(imported.mediaRestored,portable.mediaTotal);assert.equal(imported.mediaMissing.length,0);
const mediaById=new Map(imported.mediaChecks.map(x=>[x.assetId,x])),observed=[];
for(const [role,id] of [['source',state.projectId],['officialImportedCopy',state.importedProjectId]]){
 const row=await httpEntry('project:'+id);assert(row.found);const p=row.value;assert.equal(p.timelines.length,2);const sequences=[];
 for(const tl of p.timelines){
  assert.equal(tl.fps,m.fps);assert.equal(tl.width,m.width);assert.equal(tl.height,m.height);
  const native=tl.id===state.nativeTimelineId,videos=tl.items.filter(i=>i.kind==='video').sort((a,b)=>a.startFrame-b.startFrame),audio=tl.items.filter(i=>i.kind==='audio'),texts=tl.items.filter(i=>i.kind==='text');
  assert.equal(videos.length,native?m.shots.length:m.hfChunks.length);assert.equal(texts.length,native?(m.nativeTexts?.length||0):0);assert.equal(audio.length,1);assert.equal(audio[0].startFrame,0);assert.equal(audio[0].durationInFrames,m.durationFrames);assert.equal(audio[0].volume,1);
  let cursor=0;for(const i of videos){assert.equal(i.startFrame,cursor);cursor+=i.durationInFrames;assert.equal(i.volume,0);}assert.equal(cursor,m.durationFrames);
  for(const i of [...videos,...audio]){const a=p.assets.find(a=>a.id===i.sourceAssetId);assert(a);assert.equal(i.src,a.src);assert(a.durationInFrames>=(i.srcInFrame??0)+i.durationInFrames);}
  sequences.push({id:tl.id,name:tl.name,fps:tl.fps,width:tl.width,height:tl.height,frames:cursor,seconds:cursor/tl.fps,videoClips:videos.length,audioClips:audio.length,textClips:texts.length,contiguousVideo:true,allMediaLinked:true,allVideoMuted:true});
 }
 if(role==='officialImportedCopy')for(const a of p.assets)assert(mediaById.get(a.id)?.packageBytesMatch,`Missing hash readback: ${a.name}`);
 observed.push({role,id,assets:p.assets.length,sequences});
}
const report={projectId:state.projectId,importedProjectId:state.importedProjectId,packageFilename:path.basename(portable.packagePath),packageBytes:portable.bytes,packageSha256:portable.sha256,packageFormat:portable.format,mediaAssets:portable.mediaTotal,mediaAvailableAndByteVerified:imported.mediaRestored,mediaMissing:[],observed,method:'Live HTTP ProjectDoc readback and official exporter/importer SHA256 per-media verification; UI playback and audition recorded separately.',actualUiPlaybackVerified:false,actualUiDragVerified:false,actualUiAudioAuditionVerified:false,verifiedAt:new Date().toISOString()};save(path.join(output,'工程包最终回读.json'),report);
for(const name of ['原生时间线核验.json','时间线核验.json']){const f=path.join(output,name),r=read(f);r.officialPackagePending=false;r.officialPackageRoundTripVerified=true;r.importedProjectId=state.importedProjectId;save(f,r);}
const text=`# ${m.title} · OpenChatCut 工程说明

本工程是《挚友 · EDGE》V2独立精修版，为${m.width}×${m.height}、${m.fps}fps、${m.durationFrames}帧，即${m.durationFrames/m.fps}秒。沿用edge原曲147–207秒，精修方向扩展到真实人物抠像、SVG文字排版、撕边、发光电弧和粒子。V1项目与交付保留。工程包使用官方导出器制作，再通过官方导入器真实重开；${portable.mediaTotal}项媒体全部恢复，missing 0，逐媒体SHA256一致。

- 工程包：${path.basename(portable.packagePath)}（${portable.bytes.toLocaleString('en-US')}字节）。
- [原工程](${state.url}) · [官方导入验证副本](${state.importedProjectUrl})。本机链接需要5199服务；跨机器使用ccproj导入。

## 打开与修改

1. 在OpenChatCut项目首页选择“导入项目”，打开本目录ccproj。
2. 默认序列“01 HF完整效果”包含${m.hfChunks.length}段效果预合成视频和独立master.wav，可移动、裁切、替换每段视频。
3. 切换至“02 原生逐镜”可编辑${m.shots.length}个独立镜头${m.nativeTexts?.length?`及${m.nativeTexts.length}个原生文字片段`:''}的顺序、入点和时长。
4. 两条序列各有一条独立master音乐；视频全部静音，不叠加原片声音。
5. 人物抠像、SVG文字、撕边、发光电弧、粒子及复杂空间合成在旁边HyperFrames工程保留源码；修改后重新渲染对应HF片段并在OpenChatCut替换。原生逐镜用于换镜头，HF序列用于完整视觉预览。实际执行效果与剩余差异以主交付参考对照说明为准。

原生序列的${m.nativeTexts?.length||0}个文字片段采用最大36号字、画布下方安全区，作为学习标签。复杂SVG文字与HF字效保留在HyperFrames工程内，OpenChatCut原生序列没有展开这些复杂字效。

## 核验记录

- 原生时间线核验.json、时间线核验.json：实际时间线逐镜回读。
- 官方工程包验证.json：官方导出、包格式和媒体SHA256。
- 官方工程包导入回验.json：真实导入、missing 0、结构与媒体一致性。
- 工程包最终回读.json：导入前后两套工程的最终活跃数据核对。
- 工程Doc.json、导入副本Doc.json：原工程与导入副本快照。

后端媒体与结构核验不代替主观观感试听，实际UI播放、拖动与试听由主验收记录说明。
`;
fs.writeFileSync(path.join(output,'README_工程说明.md'),text);console.log(JSON.stringify({sourceProjectId:state.projectId,importedProjectId:state.importedProjectId,mediaAssets:portable.mediaTotal,missing:0,packagePath:portable.packagePath,sequences:observed[1].sequences}));
