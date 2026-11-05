import path from 'node:path';import assert from 'node:assert/strict';
import {work,output,read,save,statePath,tool,doc,httpEntry} from './client.mjs';
const state=read(statePath);assert.equal(state.phase,'hf-companion-verified');let p=doc(state.projectId);const hfBefore=structuredClone(p.timelines.find(t=>t.id===state.hfTimelineId));
tool('activate-native-for-clock-alignment','manage_timelines',{action:'switch',timelineId:state.timelineId},state.projectId);
p=doc(state.projectId);let tl=p.timelines.find(t=>t.id===state.timelineId);const updates=[];
for(let n=0;n<3;n++){const i=tl.items.find(i=>i.track===state.effectTracks.panels[n]);assert(i);updates.push({type:'video',itemId:i.id,fromFrame:675+n*5,sourceStartFrame:12,sourceDurationInFrames:45-n*5,clearKeyframes:'opacity'});}
tool('align-native-panel-clock','edit_item',{updates},state.projectId);
tool('restore-preferred-hf-timeline','manage_timelines',{action:'switch',timelineId:state.hfTimelineId},state.projectId);
p=doc(state.projectId);tl=p.timelines.find(t=>t.id===state.timelineId);assert.deepEqual(p.timelines.find(t=>t.id===state.hfTimelineId),hfBefore,'01 sequence changed during 02-only source clock fix');
const report=read(path.join(output,'原生特效验证.json'));
for(let n=0;n<3;n++){const i=tl.items.find(i=>i.track===state.effectTracks.panels[n]);assert.equal(i.startFrame,675+n*5);assert.equal(i.durationInFrames,45-n*5);assert.equal(i.srcInFrame,12);assert.equal(i.startFrame+i.durationInFrames,720);assert(!i.keyframes?.opacity?.length);assert.equal(i.transform?.opacity??1,1);Object.assign(report.panelChecks[n],{startFrame:i.startFrame,durationInFrames:i.durationInFrames,srcInFrame:i.srcInFrame,firstVisibleSourceFrame:12,sourceClockAlignedToHf:true});}
report.sourceClockAlignment={method:'Native delayed clip placement (675/680/685), common end720, source in12 at first visible frame',preferredHfSequenceUnchanged:true,verifiedAt:new Date().toISOString()};
assert.deepEqual((await httpEntry('project:'+state.projectId)).value,p);save(path.join(output,'原生特效验证.json'),report);save(path.join(output,'正式工程Doc.json'),p);console.log(JSON.stringify({nativePanelSpans:report.panelChecks.map(c=>({startFrame:c.startFrame,frames:c.durationInFrames,srcInFrame:c.srcInFrame})),hfUnchanged:true,activeTimelineId:p.activeTimelineId}));
