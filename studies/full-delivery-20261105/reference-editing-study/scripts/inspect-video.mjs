import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8').replace(/^\uFEFF/,''));
const [id,startArg,endArg]=process.argv.slice(2),start=Number(startArg),end=Number(endArg);
const item=read(path.join(root,'data/manifest.json')).find(v=>v.id===id);
if(!item||!Number.isFinite(start)||!Number.isFinite(end)||start<0||end<=start||end>item.duration||end-start>5){
 console.error('用法：node scripts/inspect-video.mjs V10 6.4 8.9（区间最长5秒，需在原片范围内）');process.exit(1);
}
const media=read(path.join(root,'local-config.json')).media[id];
const [num,den]=item.fps.split('/').map(Number),fps=num/(den||1),step=3;
const count=Math.floor(end*fps/step)-Math.ceil(start*fps/step)+1;
const rows=Math.max(1,Math.ceil(count/4));
const vf=`select='between(t,${start},${end})*not(mod(n,${step}))',scale=400:226:force_original_aspect_ratio=decrease:force_divisible_by=2,pad=400:226:(ow-iw)/2:(oh-ih)/2:black,drawtext=fontfile='C\\:/Windows/Fonts/consola.ttf':text='%{pts\\:hms}':fontsize=19:fontcolor=white:box=1:boxcolor=black@0.8:x=5:y=5,tile=4x${rows}:padding=3:margin=3`;
const args=['-v','error','-nostdin','-threads','2','-i',media,'-an','-vf',vf,'-frames:v','1','-q:v','2','-f','image2pipe','pipe:1'];
const result=spawnSync('C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe',args,{windowsHide:true,maxBuffer:64*1024*1024});
if(result.error||result.status!==0){console.error(result.error?.message||result.stderr.toString());process.exit(1)}
const out=path.join(root,'evidence',id,`recheck-${start.toFixed(3)}-${end.toFixed(3)}.jpg`);
fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,result.stdout);
fs.writeFileSync(out+'.json',JSON.stringify({id,start,end,source_fps:fps,every_nth_source_frame:step,timestamp:'source PTS',source_sha256:item.sha256,ffmpeg_args:args},null,2));
console.log(`已保存：${out}\n每${step}个源帧取1张；时间戳保留源PTS。原视频未改变。`);
