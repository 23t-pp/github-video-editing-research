import fs from 'node:fs/promises';
import path from 'node:path';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
const manifest=JSON.parse((await fs.readFile(path.join(root,'manifest.local.json'),'utf8')).replace(/^\uFEFF/,''));
const specs=[['V01',20.6,22.5,10,'circle'],['V01',23.1,24.15,16,'face-portal'],['V04',9.6,10.8,12,'cutout'],['V04',11.65,13.15,12,'eye-portal'],['V04',20.7,21.5,12,'loop-end'],['V04',0,0.8,12,'loop-start'],['V08',7.2,8.65,12,'silhouette'],['V09',4.2,6.25,8,'light-travel'],['V10',6.4,8.9,8,'round-portal'],['V10',9.4,10.8,12,'wheel-portal']];
await fs.mkdir(path.join(root,'details'),{recursive:true});
for(const [id,start,end,fps,label] of specs){
 const item=manifest.find(v=>v.id===id);const [num,den]=item.fps.split('/').map(Number);const nativeFps=num/den;const step=Math.max(1,Math.round(nativeFps/fps));const rows=Math.ceil((Math.floor(end*nativeFps/step)-Math.ceil(start*nativeFps/step)+1)/4);
 const vf=`select='between(t,${start},${end})*not(mod(n,${step}))',scale=400:226:force_original_aspect_ratio=decrease:force_divisible_by=2,pad=400:226:(ow-iw)/2:(oh-ih)/2:black,drawtext=fontfile='C\\:/Windows/Fonts/consola.ttf':text='%{pts\\:hms}':fontsize=19:fontcolor=white:box=1:boxcolor=black@0.8:x=5:y=5,tile=4x${rows}:padding=3:margin=3`;
 const data=await new Promise((resolve,reject)=>{const p=spawn('C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe',['-v','error','-nostdin','-threads','2','-i',item.path,'-an','-vf',vf,'-frames:v','1','-q:v','2','-f','image2pipe','pipe:1'],{windowsHide:true});const chunks=[];let error='';p.stdout.on('data',b=>chunks.push(b));p.stderr.on('data',b=>error+=b);p.on('close',c=>c===0?resolve(Buffer.concat(chunks)):reject(new Error(error)));});
 const file=`${id}-${label}.jpg`;await fs.writeFile(path.join(root,'details',file),data);console.log(file);
}
await fs.writeFile(path.join(root,'details','windows.json'),JSON.stringify(specs.map(([id,start,end,fps,label])=>({id,start,end,fps,label})),null,2));
