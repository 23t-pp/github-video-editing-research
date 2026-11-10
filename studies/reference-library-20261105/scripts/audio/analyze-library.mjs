import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import os from 'node:os';
import {spawnSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
const ROOT=path.resolve(import.meta.dirname,'../../data/audio');
const WORK=path.resolve(process.env.REF_AUDIO_WORK||path.resolve(import.meta.dirname,'../../../../work/reference-library-20261105/audio-work'));
fs.mkdirSync(ROOT,{recursive:true});fs.mkdirSync(WORK,{recursive:true});
const HF=path.join(process.env.HYPERFRAMES_INSTALL||path.join(os.homedir(),'Apps/hyperframes/node_modules/hyperframes'),'dist/chunk-NOH32H42.js');
const MONTAGE=path.join(os.homedir(),'.codex/skills/montage/assets/dsh-montage/lib/analyze.js');
const hf=await import(pathToFileURL(HF));
const montage=await import(pathToFileURL(MONTAGE));
const manifest=JSON.parse(fs.readFileSync(path.resolve(process.env.REF_AUDIO_MANIFEST||path.resolve(import.meta.dirname,'../../../../work/reference-library-20261105/manifest.local.json')),'utf8').replace(/^\uFEFF/,''));
const selected=process.argv.slice(2);
const round=(n,p=3)=>Number(n.toFixed(p));
const mean=a=>a.reduce((s,v)=>s+v,0)/(a.length||1);
const median=a=>{const s=[...a].sort((a,b)=>a-b);return s.length?s[s.length>>1]:0};
const quantile=(a,q)=>{const s=[...a].sort((a,b)=>a-b);return s[Math.floor((s.length-1)*q)]||0};
const operations=[];
function wavPCM(file){
 const b=fs.readFileSync(file);let offset=12,sr=0,data;
 while(offset+8<=b.length){const id=b.toString('ascii',offset,offset+4),n=b.readUInt32LE(offset+4);
  if(id==='fmt '){if(b.readUInt16LE(offset+8)!==1||b.readUInt16LE(offset+22)!==16)throw Error('Expected 16 bit PCM');sr=b.readUInt32LE(offset+12)}
  if(id==='data')data=b.subarray(offset+8,Math.min(b.length,offset+8+n));
  offset+=8+n+(n%2);
 }
 if(!data||!sr)throw Error('Invalid WAV');
 return {sampleRate:sr,channels:[Float32Array.from({length:data.length/2},(_,i)=>data.readInt16LE(i*2)/32768)]};
}
function onsetFlux(frames){
 const raw=new Float64Array(frames.bands.length),low=new Float64Array(raw.length);
 // The first approximately 11 log bands cover the lowest musical attack region.
 for(let i=1;i<raw.length;i++)for(let b=0;b<frames.bands[i].length;b++){const v=Math.max(0,frames.bands[i][b]-frames.bands[i-1][b]);raw[i]+=v;if(b<11)low[i]+=v;}
 const sums=new Float64Array(raw.length+1);for(let i=0;i<raw.length;i++)sums[i+1]=sums[i]+raw[i];
 const env=Float64Array.from(raw,(v,i)=>{const a=Math.max(0,i-40),z=Math.min(raw.length,i+41);return Math.max(0,v-(sums[z]-sums[a])/(z-a))});
 return {raw,env,low};
}
function periodicity(env,fps=100){
 if(env.length<200)return {candidates:[],best:null};
 const m=mean(env),center=Float64Array.from(env,v=>v-m),energy=center.reduce((s,v)=>s+v*v,0)||1;
 const ac=new Float64Array(302);
 for(let lag=1;lag<ac.length&&lag<center.length;lag++){let sum=0;for(let i=lag;i<center.length;i++)sum+=center[i]*center[i-lag];ac[lag]=sum/energy;}
 const peaks=[];
 for(let lag=25;lag<=150;lag++)if(ac[lag]>ac[lag-1]&&ac[lag]>=ac[lag+1]&&ac[lag]>0){
  const ca=ac[lag-1],cb=ac[lag],cc=ac[lag+1],den=ca-2*cb+cc;
  const shift=den?Math.max(-.5,Math.min(.5,.5*(ca-cc)/den)):0;
  peaks.push({bpm:round(60*fps/(lag+shift),1),autocorrelation:round(ac[lag]),lagSec:round((lag+shift)/fps)});
 }
 peaks.sort((a,b)=>b.autocorrelation-a.autocorrelation);
 const distinct=[];for(const p of peaks)if(distinct.every(q=>Math.abs(q.bpm-p.bpm)>3))distinct.push(p);
 return {candidates:distinct.slice(0,7),best:distinct[0]||null};
}
function rmsBins(signal,step=.25){const x=signal.channels[0],n=Math.round(signal.sampleRate*step),out=[];
 for(let i=0;i<x.length;i+=n){let p=0,z=Math.min(x.length,i+n);for(let j=i;j<z;j++)p+=x[j]*x[j];out.push({start:round(i/signal.sampleRate),end:round(z/signal.sampleRate),dbFS:round(10*Math.log10(p/(z-i)+1e-12),1)});}return out;
}
function strongestDistributed(onsets,duration){
 const selected=[];
 for(let a=0;a<duration;a+=Math.max(2,duration/8)){
  const local=onsets.filter(v=>v.t>=a&&v.t<a+Math.max(2,duration/8)&&v.t>.08&&v.t<duration-.08).sort((a,b)=>b.strength-a.strength);
  for(const e of local)if(selected.every(q=>Math.abs(q.t-e.t)>.18)){selected.push(e);if(selected.filter(q=>q.t>=a&&q.t<a+Math.max(2,duration/8)).length>=2)break;}
 }return selected.sort((a,b)=>a.t-b.t);
}
function transitions(bins,duration){
 const candidates=[];
 for(let i=4;i<bins.length-4;i++){
  const before=mean(bins.slice(i-4,i).map(b=>b.dbFS)),after=mean(bins.slice(i,i+4).map(b=>b.dbFS));
  const delta=after-before;if(Math.abs(delta)>=3.5)candidates.push({t:bins[i].start,beforeDbFS:round(before,1),afterDbFS:round(after,1),deltaDb:round(delta,1),kind:delta>0?'响度上升候选':'响度下降候选'});
 }
 candidates.sort((a,b)=>Math.abs(b.deltaDb)-Math.abs(a.deltaDb));const kept=[];
 for(const c of candidates)if(kept.every(q=>Math.abs(q.t-c.t)>1.5)&&c.t>1&&c.t<duration-1)kept.push(c);
 return kept.slice(0,Math.max(5,Math.ceil(duration/12))).sort((a,b)=>a.t-b.t);
}
for(const item of manifest.filter(i=>!selected.length||selected.includes(i.id))){
 const started=Date.now(),wav=path.join(WORK,`${item.id}.mono.wav`),args=['-nostdin','-y','-v','error','-i',item.path,'-map','0:a:0','-vn','-ac','1','-ar','22050','-c:a','pcm_s16le','-f','wav','pipe:1'];
 const ff=spawnSync((process.env.FFMPEG_PATH||path.join(os.homedir(),'Apps/ffmpeg/bin/ffmpeg.exe')),args,{windowsHide:true,maxBuffer:512*1024*1024});
 operations.push({id:item.id,command:'ffmpeg',args,exit_code:ff.status,stderr:ff.stderr?.toString(),stdout_saved_by:'Node fs.writeFileSync',output:wav,at:new Date().toISOString()});
 if(ff.status!==0)throw Error(`${item.id} ffmpeg ${ff.stderr}`);
 fs.writeFileSync(wav,ff.stdout);
 const signal=wavPCM(wav),duration=signal.channels[0].length/signal.sampleRate;
 const frames=hf.bandFramesOf(signal),flux=onsetFlux(frames),periodic=periodicity(flux.env,frames.fps);
 const rhythm=hf.rhythm(signal),tempo=hf.tempoOf(rhythm.beats.times);
 const onsetResult=await hf.signalProvider.analyze('onsets',signal,{method:'spectral-flux',hopMs:10,minGapMs:100,threshold:.15});
 const sections=await hf.signalProvider.analyze('sections',signal,{minSeconds:4});
 const silence=await hf.signalProvider.analyze('silence',signal,{thresholdDb:-50,minMs:200,hopMs:5});
 const bins=rmsBins(signal),energyChanges=transitions(bins,duration),windowTempos=[];
 for(let start=0;start<duration-5;start+=4){const end=Math.min(duration,start+8);const p=periodicity(flux.env.subarray(Math.round(start*100),Math.round(end*100)));windowTempos.push({start,end:round(end),...p});}
 let baseline;try{baseline=await montage.analyze({audio:wav,window:Math.min(30,Math.floor(duration)),count:2})}catch(e){baseline={error:String(e)}}
 const localBeatEvidence=rhythm.beats.times.length?hf.localBeatEvidence(signal,rhythm.beats.times):[];
 const interval=rhythm.beats.times.slice(1).map((b,i)=>b-rhythm.beats.times[i]);
 const report={
  id:item.id,source_name:item.name,source_sha256:item.sha256,created_at:new Date().toISOString(),duration_sec:round(duration),
  actual_execution:{decoded:true,ffmpeg_exit_code:ff.status,listened:false,uploaded_to_analysis_service:false,installed_models:false,elapsed_ms:Date.now()-started},
  method:{primary:'HyperFrames 0.8.216本地signal provider：log-frequency band spectral flux、自相关tempo、DP beat tracking；sections为音色/chroma结构新颖度。直接调用本地库，无API和模型。',secondary:'本分析脚本：对HF频带的正谱差做±0.4s局部均值去趋势，自相关寻找40–240 BPM局部峰；0.25s RMS只用于响度变化。',baseline:'montage 0.4.1：20ms log-RMS正差、10ms hop的自相关/comb启发式；不是独立听觉确认。',timing:'onsets=谱通量局部峰(10ms hop)，beats=周期模型推断网格(含HF的15ms经验偏置)；均是原视频从0秒起的时间，未对人工感知确认。'},
  hyperframes:{beats:rhythm.beats,downbeats:rhythm.downbeats,tempo,interval_median_sec:round(median(interval)),interval_mad_sec:round(median(interval.map(v=>Math.abs(v-median(interval))))),local_beat_evidence:localBeatEvidence},
  spectral_autocorrelation:periodic,window_tempos:windowTempos,
  onset_events:onsetResult.events,strong_onset_examples:strongestDistributed(onsetResult.events,duration),
  structure_candidates:sections,silence_below_minus50dbfs_200ms:silence,energy_changes:energyChanges,rms_250ms:bins,
  montage_baseline:{bpm:baseline.bpm,beat_sec:baseline.beat,candidates:baseline.candidates,error:baseline.error},
  caution:['这是已混合的最终音轨，起音可能来自对白音节、打击声、whoosh、引擎声或音乐，算法没有分离来源。','谱通量起音不等同音乐节拍；响度上升/下降不等同副歌/drop/段落标签。','BPM有半倍/倍速、切段和tempo漂移歧义；本轮没有实际监听，所有BPM及强拍位置均为候选。','结构边界由音色/chroma统计而非歌词/听觉语义确定，4秒最短段也会忽略更快变化。'],
  provenance:{hyperframes_source_sha256:crypto.createHash('sha256').update(fs.readFileSync(HF)).digest('hex'),montage_source_sha256:crypto.createHash('sha256').update(fs.readFileSync(MONTAGE)).digest('hex')}
 };
 fs.writeFileSync(path.join(ROOT,`${item.id}.json`),JSON.stringify(report,null,2));
 console.log(JSON.stringify({id:item.id,duration:round(duration),hf_bpm:tempo.value,hf_confidence:rhythm.beats.confidence,hf_reason:rhythm.beats.reason,onsets:onsetResult.events.length,ac_candidates:periodic.candidates.slice(0,4),baseline:baseline.bpm,sections:sections.spans,elapsed_ms:Date.now()-started}));
 fs.writeFileSync(path.join(WORK,'analysis-operations.local.json'),JSON.stringify(operations,null,2));
}
