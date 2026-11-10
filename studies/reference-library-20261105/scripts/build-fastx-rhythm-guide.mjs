// Original deterministic rhythm guide for planning: not a finished soundtrack.
import fs from'node:fs';import path from'node:path';import{spawnSync}from'node:child_process';
const out=path.resolve(import.meta.dirname,'../fastx-120');fs.mkdirSync(out,{recursive:true});
const sr=48000,bpm=128,beat=60/bpm,duration=120,samples=new Float32Array(sr*duration),events=[],markers=[];let seed=20261105;
const noise=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296*2-1};
const sections=[{name:'冷开场：危险先到',start:0,end:7.5,energy:.25},{name:'人物与威胁建立',start:7.5,end:22.5,energy:.45},{name:'第一轮追逐',start:22.5,end:52.5,energy:.72},{name:'短暂呼吸与情绪理由',start:52.5,end:67.5,energy:.23},{name:'高速主高潮',start:67.5,end:112.5,energy:1},{name:'最后一次兑现与收尾',start:112.5,end:120,energy:.65}];
const event=(tick,ch,note,velocity,length)=>{events.push({t:tick,b:[0x90|ch,note,velocity]},{t:tick+length,b:[0x80|ch,note,0]})};
function add(t,len,fn,gain){const a=Math.round(t*sr),n=Math.min(Math.round(len*sr),samples.length-a);for(let i=0;i<n;i++)samples[a+i]+=fn(i/sr,i/n)*gain;}
const notes=[38,34,41,36],hz=n=>440*Math.pow(2,(n-69)/12);
for(let b=0;b<256;b++){const t=b*beat,sec=sections.find(s=>t>=s.start&&t<s.end),bar=Math.floor(b/4)+1;markers.push({beat:b+1,bar,beatInBar:b%4+1,timeSeconds:t,frame24:Math.round(t*24),quantizationErrorMs:(Math.round(t*24)/24-t)*1000,section:sec.name});
 if(sec.energy>.4||b%4===0){add(t,.25,q=>Math.sin(2*Math.PI*(48*q+5.6*(1-Math.exp(-q*32))))*Math.exp(-q*18),.38*sec.energy);event(b*480,9,36,Math.round(95*sec.energy),90);}
 if(b%4===1||b%4===3){add(t,.14,q=>(noise()*.68+Math.sin(2*Math.PI*180*q)*.32)*Math.exp(-q*32),.17*sec.energy);event(b*480,9,38,Math.round(80*sec.energy),60);}
 if(sec.energy>.4)for(let h=0;h<2;h++){add(t+h*beat/2,.045,q=>noise()*Math.exp(-q*100),.055*sec.energy);event(b*480+h*240,9,42,Math.round(42*sec.energy),40);}
 if(b%2===0){const note=notes[Math.floor(b/32)%4],f=hz(note);add(t,beat*1.85,(q,x)=>(Math.sin(2*Math.PI*f*q)+.15*Math.sin(2*Math.PI*2*f*q))*Math.min(1,q/.02)*Math.min(1,(1-x)/.2),.11*sec.energy);event(b*480,0,note,Math.round(65*sec.energy),850);}
}
for(let i=0;i<samples.length;i++){const t=i/sr,fade=Math.min(1,t/.03,(duration-t)/.4);samples[i]=Math.tanh(samples[i])*fade*.8}
const wav=Buffer.alloc(44+samples.length*2);wav.write('RIFF',0);wav.writeUInt32LE(wav.length-8,4);wav.write('WAVEfmt ',8);wav.writeUInt32LE(16,16);wav.writeUInt16LE(1,20);wav.writeUInt16LE(1,22);wav.writeUInt32LE(sr,24);wav.writeUInt32LE(sr*2,28);wav.writeUInt16LE(2,32);wav.writeUInt16LE(16,34);wav.write('data',36);wav.writeUInt32LE(samples.length*2,40);for(let i=0;i<samples.length;i++)wav.writeInt16LE(Math.round(Math.max(-1,Math.min(1,samples[i]))*32767),44+i*2);
const ff=process.env.FFMPEG_PATH||'ffmpeg';const enc=spawnSync(ff,['-v','error','-f','wav','-i','pipe:0','-c:a','aac','-b:a','160k','-movflags','frag_keyframe+delay_moov+default_base_moof','-f','mp4','pipe:1'],{input:wav,maxBuffer:64*1024*1024,windowsHide:true});if(enc.status!==0)throw Error(enc.stderr.toString());fs.writeFileSync(path.join(out,'128BPM_120秒_原创节奏导轨.m4a'),enc.stdout);
function vlq(n){const a=[n&127];while(n>>=7)a.unshift((n&127)|128);return a}
events.push({t:0,b:[255,81,3,7,39,14]},{t:0,b:[255,88,4,4,2,24,8]},{t:0,b:[192,38]}); // 468750 μs / quarter = 128 BPM
events.sort((a,b)=>a.t-b.t||(a.b[0]&0xf0)-(b.b[0]&0xf0));let previous=0,track=[];for(const e of events){track.push(...vlq(e.t-previous),...e.b);previous=e.t}track.push(...vlq(256*480-previous),255,47,0);const header=Buffer.from([77,84,104,100,0,0,0,6,0,0,0,1,1,224]),chunk=Buffer.alloc(8);chunk.write('MTrk');chunk.writeUInt32BE(track.length,4);fs.writeFileSync(path.join(out,'128BPM_120秒_可编辑节奏.mid'),Buffer.concat([header,chunk,Buffer.from(track)]));
fs.writeFileSync(path.join(out,'beat-markers.csv'),['beat,bar,beat_in_bar,time_seconds,frame_at_24fps,rounding_error_ms,section',...markers.map(x=>[x.beat,x.bar,x.beatInBar,x.timeSeconds,x.frame24,x.quantizationErrorMs.toFixed(4),x.section].join(','))].join('\n'));
fs.writeFileSync(path.join(out,'music-design.json'),JSON.stringify({status:'original rhythm guide, not final soundtrack',bpm,measuredOrDesigned:'designed',durationSeconds:duration,bars:64,beats:256,timeSignature:'4/4',sampleRate:sr,sections,frameGrid:'24fps; rounding to nearest frame, up to 20.834ms',availableReferenceAudio:'Extracted short references are comparison material; do not pretend a 10s excerpt is a complete coherent 120s song.'},null,2));console.log(JSON.stringify({duration,bpm,bars:64,audioBytes:enc.stdout.length,midiEvents:events.length}));
