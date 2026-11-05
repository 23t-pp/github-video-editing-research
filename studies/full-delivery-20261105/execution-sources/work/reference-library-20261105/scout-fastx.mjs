import fs from'node:fs';import path from'node:path';import{spawn}from'node:child_process';
const out=path.resolve('outputs/reference-library-20261105/fastx-120/evidence');fs.mkdirSync(out,{recursive:true});
const times=[1650,1710,1770,1830,1890,1950,2010,2070,2130,2190,2250,2310,3630,3690,3750,3810,3870,3930,6960,7000,7040,7080,7120,7160,7200,7240,7280,7320,7360,7400];
const ff='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe',source='D:/速度与激情/11 速度与激情10（2023）4K.mp4';
const vf="zscale=w=480:h=200:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p";
async function get(t){return new Promise((ok,bad)=>{const p=spawn(ff,['-v','error','-threads','2','-ss',String(t),'-i',source,'-an','-frames:v','1','-vf',vf,'-c:v','mjpeg','-q:v','3','-f','image2pipe','pipe:1'],{windowsHide:true});const a=[];let e='';p.stdout.on('data',b=>a.push(b));p.stderr.on('data',b=>e+=b);p.on('error',bad);p.on('close',c=>c===0?ok(Buffer.concat(a)):bad(Error(e)))})}
let n=0;await Promise.all([0,1].map(async()=>{while(n<times.length){const t=times[n++];fs.writeFileSync(path.join(out,`source-${t}.jpg`),await get(t))}}));
fs.writeFileSync(path.join(out,'scout-index.json'),JSON.stringify(times.map(t=>({t,file:`source-${t}.jpg`,scope:'single observed source frame; surrounding usable shot boundaries require later trim review'})),null,2));console.log('FastX 30 candidate stills extracted; not final in/out selection.');
