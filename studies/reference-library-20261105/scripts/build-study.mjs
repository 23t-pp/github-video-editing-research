import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const write=(p,x)=>{fs.mkdirSync(path.dirname(path.join(root,p)),{recursive:true});fs.writeFileSync(path.join(root,p),JSON.stringify(x,null,2));};
const media=read('data/media-index.json');
const reviews=['V01-V10','V11-V15','V16-V20'].flatMap(x=>read(`reviews/${x}.json`));
const reviewedIds=new Set(reviews.map(r=>r.id));
for(const {id} of media)if(!reviewedIds.has(id))reviews.push(...read(`reviews/${id}.json`));
const nearest=(t,arr)=>arr.length?arr.reduce((a,b)=>Math.abs(b-t)<Math.abs(a-t)?b:a):null;
let frames=0,pages=0,humanPages=0,chapters=0;
const items=media.map(m=>{
 const review=reviews.find(r=>r.id===m.id),f=read(`data/frame-analysis/${m.id}.json`),audio=read(`data/audio/${m.id}.json`);
 if(!review)throw Error(`Missing review ${m.id}`);
 let hp=review.native_review?.humanReviewedPages?.length??review.sampling?.actually_viewed_atlas_pages??review.human_viewed?.native_pages?.length??0;
 frames+=f.nativeFrameCount;pages+=f.pages.length;humanPages+=hp;chapters+=review.segments.length;
 const events=review.verified_events?.map(e=>({frame:e.frame,time:e.time,claim:e.claim,kind:'人工查看的视觉事件'}))??review.segments.flatMap(s=>(s.evidence_frames??[]).map(e=>({frame:e.frame,time:e.pts,claim:e.description,kind:'人工查看的视觉事件'})));
 const onsets=audio.onset_events.map(e=>e.t),beats=audio.hyperframes?.beats?.times??[];
 const align=e=>{const o=nearest(e.time,onsets),b=nearest(e.time,beats);return {...e,nearestOnset:o,onsetDeltaMs:o===null?null:+((e.time-o)*1000).toFixed(2),nearestModelBeat:b,beatDeltaMs:b===null?null:+((e.time-b)*1000).toFixed(2)};};
 const sync={id:m.id,method:'视觉事件或机器变化候选与谱通量起音/模型拍点的最近邻。正误差=视觉晚于声音。未听辨来源，不把接近当因果或卡点成功。',humanVisualEvents:events.map(align),machineCandidates:f.cutOrEffectCandidates.map(e=>align({...e,kind:'机器切镜/闪光/运动候选'}))};
 const sampling60Hz=m.id==='V21'?read(`data/frame-analysis/${m.id}-60hz.json`):null;
 write(`data/sync-analysis/${m.id}.json`,sync);
 return {...m,review,frameAnalysis:f,audio:{tempoCandidate:audio.hyperframes?.tempo?.value,beatConfidence:audio.hyperframes?.beats?.confidence,beats,onsets:audio.onset_events,rms:audio.rms_250ms,caution:audio.caution},humanAtlasPagesViewed:hp,sync,...(sampling60Hz?{sampling60Hz}:{})};
});
const hashGroups=new Map();for(const m of media){if(!hashGroups.has(m.sha256))hashGroups.set(m.sha256,[]);hashGroups.get(m.sha256).push(m.id);}
const summary={date:'2026-11-05',videos:media.length,videoSeconds:media.reduce((s,m)=>s+m.duration,0),nativeFrames:frames,atlasPages:pages,humanAtlasPagesViewed:humanPages,learningChapters:chapters,policy:'保留原生帧与实际PTS；没有补成60fps；60帧/页仅是图谱排版。',reviewScope:'机器逐帧数据覆盖全部；人工看全片总览/逐秒图谱及明确记录的原生帧页。缩略图查看不等于全分辨率逐帧精读。',duplicateVideoGroups:[...hashGroups.values()].filter(a=>a.length>1),uniqueVideoSha256:hashGroups.size,claims:{allFramesDecoded:true,allFramesManuallyReadAtFullResolution:false,allReferencesRecreated:false,exactAuthorProjectRecovered:false}};
const sampling60Hz=items.find(m=>m.sampling60Hz)?.sampling60Hz;
if(sampling60Hz){
 summary.date='2026-11-06';
 summary.policy='原生帧保留实际 PTS，原生图谱每页最多 60 帧。V21 另有 60Hz 采样图谱，以相邻样本复用原帧，未做插帧。';
 summary.sampling60Hz={id:'V21',sampleRate:sampling60Hz.sampleRate,sampleCount:sampling60Hz.sampleCount,atlasPages:sampling60Hz.pages.length};
}
if(items.some(m=>m.id==='V22')){
 summary.date='2026-11-08';
 summary.policy+=' V22 为原生 60fps 播放流，逐帧保留实际 PTS 与单张 JPG。';
}
if(items.some(m=>m.id==='V23')){
 summary.date='2026-11-09';
 summary.policy+=' V23 按源 30fps 保存 PTS 和原尺寸 JPG。';
}
if(items.some(m=>m.id==='V24')){
 summary.date='2026-11-09';
 summary.policy+=' V24 按源 30fps 保存 459 张原尺寸 JPG 和 PTS。';
}
if(items.some(m=>m.id==='V25')){
 summary.date='2026-11-10';
 summary.policy+=' V25 按源 30fps 保存 637 张原尺寸 JPG 和 PTS。';
}
write('data/study.json',{summary,items});write('data/coverage.json',summary);
console.log(JSON.stringify(summary));
