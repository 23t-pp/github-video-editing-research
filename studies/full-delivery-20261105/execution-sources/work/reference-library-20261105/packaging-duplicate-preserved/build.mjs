import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';import {spawnSync} from 'node:child_process';
const root=import.meta.dirname,c=JSON.parse(fs.readFileSync(path.join(root,'sample-config.json'),'utf8'));
const ff='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';
const compat=path.join(root,'.render-source');fs.mkdirSync(compat,{recursive:true});
const gsap='C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/dist/vendor/npm/gsap@3.15.0/dist/gsap.min.js';
fs.copyFileSync(gsap,path.join(root,'assets/gsap.min.js'));
function run(args){const r=spawnSync(ff,args,{windowsHide:true,maxBuffer:256*1024*1024});if(r.error||r.status!==0)throw Error(r.error?.message||r.stderr.toString());return r.stdout}
function extractFrames(asset,key,count){const dir=path.join(root,'assets/frames',key);fs.mkdirSync(dir,{recursive:true});const cacheKey=JSON.stringify({sha256:createHash('sha256').update(fs.readFileSync(path.join(root,asset))).digest('hex'),count,fps:c.fps});const meta=path.join(dir,'cache-key.json');if(fs.existsSync(meta)&&fs.readFileSync(meta,'utf8')===cacheKey&&fs.existsSync(path.join(dir,`${String(count-1).padStart(4,'0')}.jpg`)))return;
 const b=run(['-v','error','-threads','2','-i',path.join(root,asset),'-an','-vf',`fps=${c.fps}`,'-frames:v',String(count),'-c:v','mjpeg','-q:v','2','-f','image2pipe','pipe:1']);
 let start=0,n=0;for(let i=1;i<b.length;i++)if(b[i-1]===255&&b[i]===217){const frame=b.subarray(start,i+1);if(frame[0]!==255||frame[1]!==216)throw Error('JPEG frame boundary');fs.writeFileSync(path.join(dir,`${String(n++).padStart(4,'0')}.jpg`),frame);start=i+1;}
 if(n!==count)throw Error(`expected ${count} frames, got ${n}`);fs.writeFileSync(meta,cacheKey);console.log(`Extracted ${key}: ${n} frames`);
}
extractFrames(c.background,'A',c.gridEndFrame);
extractFrames(c.incoming,'B',c.durationFrames-c.gridStartFrame);
// Sound is mixed once. Six visual windows never duplicate source sound.
const wavA=run(['-v','error','-i',path.join(root,c.background),'-vn','-ac','1','-ar','48000','-f','f32le','pipe:1']);
const wavB=run(['-v','error','-i',path.join(root,c.incoming),'-vn','-ac','1','-ar','48000','-f','f32le','pipe:1']);
const samples=new Float32Array(Math.round(c.durationFrames/c.fps*48000));
const sample=(buf,n)=>n>=0&&(n+1)*4<=buf.length?buf.readFloatLE(n*4):0;
for(let i=0;i<samples.length;i++){const t=i/48000,bt=t-c.gridStartFrame/c.fps;const aGain=Math.max(0,Math.min(1,(c.gridEndFrame/c.fps-t)/.16))*.52;const bGain=Math.max(0,Math.min(1,bt/.16))*.52;
 samples[i]=sample(wavA,i)*aGain+sample(wavB,Math.floor(bt*48000))*bGain;
}
// Self-authored short percussive accents mark the six entries; no downloaded music.
for(let k=0;k<6;k++){const t=(c.gridStartFrame+k*c.staggerFrames)/c.fps,base=Math.round(t*48000);for(let j=0;j<2400&&base+j<samples.length;j++){const q=j/48000;const click=Math.sin(2*Math.PI*(1400+110*k)*q)*Math.exp(-q*105)*.08;const low=k===0?Math.sin(2*Math.PI*(100*q-220*q*q))*Math.exp(-q*35)*.1:0;samples[base+j]+=click+low;}}
for(let i=0;i<samples.length;i++){const tail=Math.min(1,(samples.length-i)/(48000*.15));samples[i]=Math.tanh(samples[i])*tail*.9}
const wav=Buffer.alloc(44+samples.length*2);wav.write('RIFF',0);wav.writeUInt32LE(wav.length-8,4);wav.write('WAVEfmt ',8);wav.writeUInt32LE(16,16);wav.writeUInt16LE(1,20);wav.writeUInt16LE(1,22);wav.writeUInt32LE(48000,24);wav.writeUInt32LE(96000,28);wav.writeUInt16LE(2,32);wav.writeUInt16LE(16,34);wav.write('data',36);wav.writeUInt32LE(samples.length*2,40);for(let i=0;i<samples.length;i++)wav.writeInt16LE(Math.round(Math.max(-1,Math.min(1,samples[i]))*32767),44+i*2);fs.writeFileSync(path.join(root,c.audio),wav);
const sec=n=>(n/c.fps).toFixed(9),duration=sec(c.durationFrames);
function media(id,key,asset,start,end,sourceStart,track,mode){
 if(mode==='video')return `<video id="${id}" class="clip source" src="${asset}" data-start="${sec(start)}" data-duration="${sec(end-start)}" data-media-start="${sec(sourceStart)}" data-track-index="${track}" muted playsinline preload="auto" data-volume="0"></video>`;
 return Array.from({length:end-start},(_,i)=>`<img id="${id}-f${i}" class="clip source" src="assets/frames/${key}/${String(sourceStart+i).padStart(4,'0')}.jpg" data-start="${sec(start+i)}" data-duration="${sec(1)}" data-track-index="${track}" alt="" data-layout-allow-overlap="true">`).join('\n');
}
function html(mode){const cells=Array.from({length:6},(_,i)=>{const col=i%3,row=Math.floor(i/3);return `<div id="cell-${i}" class="tile" style="left:${col*640}px;top:${row*540}px"><div class="tile-source" style="left:${-col*640}px;top:${-row*540}px">${media('tile-video-'+i,'B',c.incoming,c.gridStartFrame,c.gridEndFrame,0,i+1,mode)}</div></div>`}).join('\n');
 const tweens=c.order.map((id,k)=>`tl.fromTo('#cell-${id}',{opacity:0},{opacity:1,duration:${sec(c.fadeInFrames)},ease:'none'},${sec(c.gridStartFrame+k*c.staggerFrames)});\ntl.fromTo('#cell-${id}',{y:${Math.floor(id/3)===0?-c.slidePx:c.slidePx}},{y:0,duration:${sec(c.slideFrames)},ease:'power3.out'},${sec(c.gridStartFrame+k*c.staggerFrames)});`).join('\n');
 return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080"><title>${c.title}</title><script src="assets/gsap.min.js"></script><style>*{box-sizing:border-box}html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#090c0e}#root{position:relative;width:1920px;height:1080px;overflow:hidden;background:#090c0e}.plane{position:absolute;inset:0;width:1920px;height:1080px}.source{position:absolute;inset:0;width:1920px;height:1080px;max-width:none;object-fit:fill}.tile{position:absolute;width:640px;height:540px;overflow:hidden;will-change:opacity,transform}.tile-source{position:absolute;width:1920px;height:1080px}.cards{position:absolute;left:0;top:0;width:1920px;height:1080px;transform:scale(${c.gridScale});transform-origin:50% 50%;z-index:2}.full-incoming{z-index:3}</style></head><body>
 <div id="root" data-composition-id="v05-six-panel" data-start="0" data-duration="${duration}" data-width="1920" data-height="1080" data-fps="${c.fps}" data-layout-allow-overlap="true">
 <div class="plane" id="background-plane">${media('background','A',c.background,0,c.gridEndFrame,0,0,mode)}</div>
 <div id="cards" class="cards" data-layout-allow-overlap="true">${cells}</div>
 <div class="plane full-incoming" id="incoming-plane">${media('incoming-full','B',c.incoming,c.gridEndFrame,c.durationFrames,c.gridEndFrame-c.gridStartFrame,7,mode)}</div>
 ${mode==='video'?`<audio id="master-audio" src="${c.audio}" data-start="0" data-duration="${duration}" data-track-index="8" data-volume="1"></audio>`:''}
 </div><script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});${tweens}\ntl.to('#incoming-plane',{opacity:0,duration:${sec(c.endFadeFrames)},ease:'power1.in'},${sec(c.durationFrames-c.endFadeFrames)});window.__timelines['v05-six-panel']=tl;</script></body></html>`;
}
fs.writeFileSync(path.join(root,'index.html'),html('video'));
fs.writeFileSync(path.join(compat,'index.html'),html('frames'));
fs.mkdirSync(path.join(compat,'assets'),{recursive:true});fs.copyFileSync(path.join(root,'assets/gsap.min.js'),path.join(compat,'assets/gsap.min.js'));
fs.cpSync(path.join(root,'assets/frames'),path.join(compat,'assets/frames'),{recursive:true});
fs.copyFileSync(path.join(root,'DESIGN.md'),path.join(compat,'DESIGN.md'));
fs.copyFileSync(path.join(root,'hyperframes.json'),path.join(compat,'hyperframes.json'));
console.log('Generated editable video composition, image-frame render equivalent, and one mixed audio track.');
