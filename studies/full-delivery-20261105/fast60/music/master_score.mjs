// FFmpeg stdout -> writable Node, never a direct FFmpeg filesystem write.
import fs from 'node:fs';import path from 'node:path';import os from 'node:os';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
const root=import.meta.dirname,ff=process.env.FFMPEG_PATH||path.join(os.homedir(),'Apps/ffmpeg/bin/ffmpeg.exe');
const input=path.join(root,'score-premaster.wav'),output=path.resolve(root,'../hyperframes/assets/audio/score.wav');
function run(args){const r=spawnSync(ff,['-nostdin',...args],{windowsHide:true,maxBuffer:128*1024*1024});if(r.status!==0)throw Error(r.stderr?.toString()||r.error?.message);return r;}
function loudness(file){const r=run(['-hide_banner','-i',file,'-af','loudnorm=I=-16:TP=-2.2:LRA=9:print_format=json','-f','null','-']);return JSON.parse(r.stderr.toString().match(/\{\s*"input_i"[\s\S]*?\}/)[0]);}
const pre=loudness(input);
const filter=`loudnorm=I=-16:TP=-2.2:LRA=9:measured_I=${pre.input_i}:measured_TP=${pre.input_tp}:measured_LRA=${pre.input_lra}:measured_thresh=${pre.input_thresh}:offset=${pre.target_offset}:linear=true,aresample=48000,apad=whole_len=2880000,atrim=end_sample=2880000`;
const result=run(['-v','error','-i',input,'-af',filter,'-ar','48000','-ac','2','-c:a','pcm_s24le','-f','wav','pipe:1']);
fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,result.stdout);
// Streaming WAV uses unknown-length chunk sizes. Replace RIFF/data sizes with
// exact saved sizes so ordinary editors also read the 60-second file safely.
const wav=fs.readFileSync(output);wav.writeUInt32LE(wav.length-8,4);let offset=12;
while(offset+8<=wav.length){const name=wav.toString('ascii',offset,offset+4);const size=wav.readUInt32LE(offset+4);if(name==='data'){wav.writeUInt32LE(wav.length-offset-8,offset+4);break;}offset+=8+size+(size%2);}
fs.writeFileSync(output,wav);
const measured=loudness(output);
for(const [name,start,duration] of [['preview-street.wav',7.5,15],['preview-main.wav',30,22.5]]){
 const preview=run(['-v','error','-ss',String(start),'-i',output,'-t',String(duration),'-c:a','pcm_s16le','-f','wav','pipe:1']).stdout;
 preview.writeUInt32LE(preview.length-8,4);let pos=12;while(pos+8<=preview.length){const id=preview.toString('ascii',pos,pos+4),n=preview.readUInt32LE(pos+4);if(id==='data'){preview.writeUInt32LE(preview.length-pos-8,pos+4);break;}pos+=8+n+(n%2);}
 fs.writeFileSync(path.join(root,name),preview);
}
const report={title:'NIGHT RELAY / 夜行接力',duration_sec:60,sample_rate:48000,channels:2,sample_frames:2880000,pcm_bits:24,sha256:crypto.createHash('sha256').update(wav).digest('hex'),bytes:wav.length,mastering:{method:'FFmpeg two-pass loudnorm, then exact sample trim/pad',target_integrated_lufs:-16,target_true_peak_dbtp:-2.2,target_lra_lu:9,premaster_measurement:pre,final_measurement:measured},preview_files:['preview-street.wav','preview-main.wav'],listened:false,listening_quality_verified:false,limitations:['No actual listening was performed by the authoring agent. Preview WAVs are provided for human audition.','MIDI captures notes, drum triggers and phrase markers; synthesized timbres, processing and noise sweeps are defined in compose_score.py.','This is the music score only. Source engines/dialogue/SFX have not yet been mixed.']};
fs.writeFileSync(path.join(root,'mastering-report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({file:'hyperframes/assets/audio/score.wav',lufs:measured.input_i,true_peak_dbtp:measured.input_tp,lra_lu:measured.input_lra,bytes:wav.length}));
