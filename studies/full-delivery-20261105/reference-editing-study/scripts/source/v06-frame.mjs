import fs from 'node:fs/promises';
import path from 'node:path';
import {spawn} from 'node:child_process';
const root=import.meta.dirname;
const source=JSON.parse((await fs.readFile(path.join(root,'manifest.local.json'),'utf8')).replace(/^\uFEFF/,'')).find(x=>x.id==='V06');
const dir=path.join(root,'visuals','V06');
const windows=[
 {name:'frame-handshake-55.75-56.25',start:55.75,end:56.25,fps:24,cols:6,rows:2},
 {name:'frame-gun-81.5-82',start:81.5,end:82,fps:24,cols:6,rows:2},
 {name:'frame-impact-93.292-94.292',start:93.2916667,end:94.2916667,fps:24,cols:6,rows:4}
];
const stamp="drawtext=fontfile='C\\:/Windows/Fonts/consola.ttf':text='%{pts\\:hms}':fontsize=19:fontcolor=white:box=1:boxcolor=black@0.80:x=6:y=6";
const operations=[];
for(const w of windows){
 const filter=`select='gte(t,${w.start})*lt(t,${w.end})',fps=${w.fps}:start_time=${w.start},trim=end=${w.end},scale=384:216:force_original_aspect_ratio=decrease,pad=384:216:(ow-iw)/2:(oh-ih)/2:black,${stamp},tile=${w.cols}x${w.rows}:padding=3:margin=3:color=0x252525`;
 const args=['-hide_banner','-nostdin','-threads','2','-v','error','-i',source.path,'-an','-vf',filter,'-frames:v','1','-q:v','2','-f','image2pipe','pipe:1'];
 const r=await new Promise((resolve,reject)=>{const p=spawn('C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe',args,{windowsHide:true});const out=[];let err='';p.stdout.on('data',b=>out.push(b));p.stderr.on('data',b=>err+=b);p.on('error',reject);p.on('close',code=>code===0?resolve(Buffer.concat(out)):reject(new Error(err)));});
 await fs.writeFile(path.join(dir,w.name+'.jpg'),r);operations.push({...w,args,source_sha256:source.sha256,method:'FFmpeg decoded frame contact sheet; not REA Evidence'});console.log(w.name);
}
await fs.writeFile(path.join(dir,'frame-operations.json'),JSON.stringify(operations,null,2));
