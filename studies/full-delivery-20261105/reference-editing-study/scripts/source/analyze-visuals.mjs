import fs from 'node:fs/promises';
import path from 'node:path';
import { spawn } from 'node:child_process';

const root = path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/, '$1'));
const manifest = JSON.parse((await fs.readFile(path.join(root, 'manifest.local.json'), 'utf8')).replace(/^\uFEFF/, ''));
const ffmpeg = 'C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';
const out = path.join(root, 'visuals');
await fs.mkdir(out, {recursive: true});
const stamp = "drawtext=fontfile='C\\:/Windows/Fonts/consola.ttf':text='%{pts\\:hms}':fontsize=18:fontcolor=white:box=1:boxcolor=black@0.75:x=6:y=6";
const fit = 'scale=320:180:force_original_aspect_ratio=decrease,pad=320:180:(ow-iw)/2:(oh-ih)/2:black';
async function run(args) {
  return new Promise((resolve, reject) => {
    const child = spawn(ffmpeg, ['-hide_banner','-nostdin','-threads','2',...args], {windowsHide: true});
    let log = ''; const chunks=[];
    child.stdout.on('data', b => chunks.push(b));
    child.stderr.on('data', b => {log += b.toString();});
    child.on('error', reject);
    child.on('close', code => code === 0 ? resolve({log,data:Buffer.concat(chunks)}) : reject(new Error(log.slice(-5000))));
  });
}
async function inspect(item) {
  const dir = path.join(out,item.id);
  await fs.mkdir(dir,{recursive:true});
  const overview=await run(['-v','error','-i',item.path,'-an','-vf',`fps=${24/item.duration},${fit},${stamp},tile=4x6:padding=3:margin=3:color=0x252525`,'-frames:v','1','-q:v','2','-f','image2pipe','pipe:1']);
  await fs.writeFile(path.join(dir,'overview.jpg'),overview.data);
  const sampleFps = item.duration > 60 ? 1 : 2;
  const timelines=await run(['-v','error','-i',item.path,'-an','-vf',`fps=${sampleFps},${fit},${stamp},tile=5x6:padding=3:margin=3:color=0x252525`,'-fps_mode','vfr','-q:v','2','-f','image2pipe','pipe:1']);
  let cursor=0,page=1;
  while(cursor<timelines.data.length){const start=timelines.data.indexOf(Buffer.from([255,216]),cursor);if(start<0)break;const end=timelines.data.indexOf(Buffer.from([255,217]),start+2);if(end<0)throw new Error('Incomplete JPEG stream');await fs.writeFile(path.join(dir,`timeline-${String(page++).padStart(2,'0')}.jpg`),timelines.data.subarray(start,end+2));cursor=end+2;}
  const {log} = await run(['-v','info','-i',item.path,'-an','-vf',"scale=320:180,select='gt(scene,0.10)',metadata=print,showinfo",'-fps_mode','vfr','-f','null','-']);
  const points=[];
  let current=null;
  for(const line of log.split(/\r?\n/)) {
    const t=line.match(/frame:\s*(\d+)\s+pts:.*pts_time:([\d.]+)/);
    if(t) current={time:Number(t[2])};
    const s=line.match(/lavfi.scene_score=([\d.]+)/);
    if(s && current) {points.push({...current,score:Number(s[1])});current=null;}
  }
  const record={id:item.id,method:'FFmpeg select scene at 320x180, threshold >0.10. Candidates include flashes, camera moves and effects; not confirmed shot boundaries.',threshold:0.10,candidates:points,timelineSampleFps:sampleFps};
  await fs.writeFile(path.join(dir,'scene-candidates.json'),JSON.stringify(record,null,2));
  console.log(JSON.stringify({id:item.id,seconds:item.duration,candidates:points.length,overview:path.join(dir,'overview.jpg')}));
}
let next=0;
await Promise.all(Array.from({length:2},async()=>{while(next<manifest.length){const item=manifest[next++];await inspect(item);}}));
