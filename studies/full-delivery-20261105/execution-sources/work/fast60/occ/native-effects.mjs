import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {root,work,output,read,save,statePath,doc,tool,httpEntry} from './client.mjs';
const state=read(statePath),editPath=path.join(root,'outputs/fast60/hyperframes/edit.json'),edit=read(editPath),baseDir=path.dirname(editPath);
assert.equal(state.phase,'formal-shots-and-stems-verified','Assemble final locked shots and stereo stems first');
let project=doc(state.projectId),tl=project.timelines.find(t=>t.id===state.timelineId);assert.equal(project.activeTimelineId,tl.id);
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const trip=edit.effects.triptych;assert.equal(trip.startFrame,675);assert.equal(trip.endFrame,720);
const panels=trip.panels.map((p,index)=>{
 const item=edit.assets.find(a=>a.id===p.assetId)||edit.shots.find(a=>a.id===p.assetId);assert(item);
 return {...p,index,file:path.resolve(baseDir,item.asset),assetStartFrame:item.assetStartFrame??12};
});
const missing=panels.filter(p=>!project.assets.some(a=>a.name===path.basename(p.file)&&a.sourceContentHash===hash(p.file)));
if(missing.length){const r=tool('import-native-panel-assets','import_assets',{paths:[...new Set(missing.map(p=>p.file))]},state.projectId);assert.equal(r.errors?.length||0,0);}
project=doc(state.projectId);tl=project.timelines.find(t=>t.id===state.timelineId);
state.effectTracks??={panels:[]};
async function track(name){
 let existing=Object.entries(tl.tracks).find(([id,t])=>t.name===name)?.[0];
 if(!existing){tool('track-'+name.replace(/[^a-z0-9]/gi,'_'),'edit_track',{action:'create',json:JSON.stringify({trackType:'video',name,count:1})},state.projectId);project=doc(state.projectId);tl=project.timelines.find(t=>t.id===state.timelineId);existing=Object.entries(tl.tracks).find(([id,t])=>t.name===name)?.[0];}
 assert(existing);return existing;
}
state.effectTracks.latin=await track('V4 APEX · editable text');
for(let n=0;n<3;n++)state.effectTracks.panels[n]=await track(`V${n+5} Triptych ${n+1} · editable crop`);
save(statePath,state);
const adds=[];
if(!tl.items.some(i=>i.track===state.tracks.hfInsert&&i.startFrame===675))adds.push({type:'solid',track:state.tracks.hfInsert,fromFrame:675,durationInFrames:45,color:'#090b0c',name:'三联底色 · 可编辑'});
if(!tl.items.some(i=>i.kind==='text'&&i.track===state.tracks.titles))adds.push({type:'text',track:state.tracks.titles,fromFrame:7,durationInFrames:68,text:'弯心',name:'片名 弯心 · 可改文字',fontSize:120,fontWeight:900,align:'left',color:'#eee9df'});
if(!tl.items.some(i=>i.kind==='text'&&i.track===state.effectTracks.latin))adds.push({type:'text',track:state.effectTracks.latin,fromFrame:7,durationInFrames:68,text:'APEX',name:'英文 APEX · 可改文字',fontSize:34,fontWeight:900,align:'left',color:'#e75733'});
for(const p of panels){
 const matches=project.assets.filter(a=>a.name===path.basename(p.file)&&a.sourceContentHash===hash(p.file));assert.equal(matches.length,1);const a=matches[0];assert(a.durationInFrames>=p.assetStartFrame+45);
 if(!tl.items.some(i=>i.track===state.effectTracks.panels[p.index]&&i.startFrame===675+p.delay))adds.push({type:'video',assetId:a.id,track:state.effectTracks.panels[p.index],fromFrame:675+p.delay,sourceStartFrame:p.assetStartFrame,sourceDurationInFrames:45-p.delay});
}
if(adds.length)tool('add-native-title-and-panels','edit_item',{adds},state.projectId);
project=doc(state.projectId);tl=project.timelines.find(t=>t.id===state.timelineId);
const title=tl.items.find(i=>i.kind==='text'&&i.track===state.tracks.titles),latin=tl.items.find(i=>i.kind==='text'&&i.track===state.effectTracks.latin);assert(title&&latin);
const updates=[
 {type:'text',itemId:title.id,props:{...title.props,fontFamily:'Microsoft YaHei',lineHeight:1.2,letterSpacing:-3,textShadow:'none'},transform:{x:1.875,y:15.5556},keyframes:{opacity:[{frame:0,value:0},{frame:5,value:1}],x:[{frame:0,value:2.6,easing:'easeOut'},{frame:10,value:1.875}] }},
 {type:'text',itemId:latin.id,props:{...latin.props,fontFamily:'Arial',fontStyle:'italic',lineHeight:1.2,letterSpacing:4,textShadow:'none'},transform:{x:2.1875,y:24.1111},keyframes:{opacity:[{frame:0,value:0},{frame:5,value:1}] }},
];
const windows=[{x:0,width:638,focusX:.61},{x:642,width:636,focusX:.49},{x:1282,width:638,focusX:.39}];
const panelChecks=[];
for(const p of panels){
 const i=tl.items.find(i=>i.track===state.effectTracks.panels[p.index]&&i.startFrame===675+p.delay);assert(i);const w=windows[p.index],left=Math.round(w.focusX*1920-w.width/2),right=1920-left-w.width,x=(w.x-left)/1920*100;
 const opacity=[{frame:0,value:1}];
 updates.push({type:'video',itemId:i.id,volume:0,transform:{x,y:0,crop:{left,right,top:140,bottom:140}},keyframes:{opacity}});
 panelChecks.push({assetId:p.assetId,itemId:i.id,startFrame:675+p.delay,durationInFrames:45-p.delay,srcInFrame:p.assetStartFrame,delay:p.delay,firstVisibleSourceFrame:p.assetStartFrame,window:{...w,y:140,height:800},sourceCrop:{left,right,top:140,bottom:140},translationXPercent:x});
}
const end=tl.items.find(i=>i.track===state.tracks.base&&i.startFrame===1350);assert(end);updates.push({type:'video',itemId:end.id,keyframes:{opacity:[{frame:0,value:1},{frame:68,value:1},{frame:89,value:0}]}});
tool('style-native-title-panels-end','edit_item',{updates},state.projectId);
project=doc(state.projectId);tl=project.timelines.find(t=>t.id===state.timelineId);
assert.equal(Math.max(...tl.items.map(i=>i.startFrame+i.durationInFrames)),1440);assert.equal(tl.items.filter(i=>i.track===state.tracks.base).length,42);assert.equal(tl.items.filter(i=>i.kind==='text').length,2);assert.equal(tl.items.filter(i=>i.kind==='audio').length,2);assert(tl.items.filter(i=>i.kind==='video').every(i=>i.volume===0));
assert.deepEqual((await httpEntry('project:'+state.projectId)).value,project);
save(path.join(output,'正式工程Doc.json'),project);
save(path.join(output,'原生特效验证.json'),{projectId:state.projectId,timelineId:tl.id,durationFrames:1440,fps:24,baseShotCount:42,textClips:[title.id,latin.id],titleScreenBoundsApprox:{chinese:{left:132,top:636,fontSize:120},latin:{left:138,top:780,fontSize:34}},titleFrames:[7,75],panelChecks,endFade:{globalStartFrame:1418,globalLastBlackFrame:1439},nativeEditable:true,limitations:['原生标题使用短促透明度/位移入场，HF的斜向mask并非OpenChatCut普通文本字段。','字体为本机微软雅黑/Arial；跨机需安装对应字体或在文字检查器更换。','位置按官方TextLayer的96px左内边距及1.2行高换算；仍须桌面查看字体实际字面框。'],actualUiFrameVerification:false,verifiedAt:new Date().toISOString()});
state.phase='native-effects-verified-awaiting-ui';save(statePath,state);console.log(JSON.stringify({projectId:state.projectId,baseShotCount:42,textClips:2,panelVideoClips:3,stereoStems:2,frames:1440}));
