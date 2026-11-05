import fs from 'node:fs';import path from 'node:path';import {spawn} from 'node:child_process';
const root=import.meta.dirname, ff='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';
const input='D:/速度与激情/11 速度与激情10（2023）4K.mp4';
const entries=process.argv.slice(2).length?process.argv.slice(2).map(Number):Array.from({length:30},(_,i)=>120+i*270);
const dir=path.join(root,'scout');fs.mkdirSync(dir,{recursive:true});
const run=args=>new Promise((ok,bad)=>{const p=spawn(ff,args,{windowsHide:true});let e='';const chunks=[];p.stdout.on('data',b=>chunks.push(b));p.stderr.on('data',b=>e+=b);p.on('error',bad);p.on('close',c=>c===0?ok(Buffer.concat(chunks)):bad(new Error(e)))});
let cursor=0;async function worker(){while(cursor<entries.length){const t=entries[cursor++],vf="zscale=w=480:h=200:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p";const data=await run(['-v','error','-nostdin','-threads','2','-ss',String(t),'-i',input,'-an','-frames:v','1','-vf',vf,'-q:v','3','-f','image2pipe','pipe:1']);fs.writeFileSync(path.join(dir,`t-${String(t).padStart(5,'0')}.jpg`),data);console.log(t)}}await Promise.all([worker(),worker()]);
const list=entries.map(t=>({t,file:`t-${String(t).padStart(5,'0')}.jpg`}));fs.writeFileSync(path.join(dir,'latest.json'),JSON.stringify(list,null,2));
