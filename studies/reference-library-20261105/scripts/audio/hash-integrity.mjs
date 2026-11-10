import fs from 'node:fs';import path from 'node:path';import os from 'node:os';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
const project=path.resolve(import.meta.dirname,'../..'),workspace=path.resolve(project,'../..'),work=path.join(workspace,'work/reference-library-20261105'),data=path.join(project,'data/audio');
const manifest=JSON.parse(fs.readFileSync(process.env.REF_AUDIO_MANIFEST||path.join(work,'manifest.local.json'),'utf8').replace(/^\uFEFF/,''));
const selected=new Set(process.argv.slice(2).filter(x=>/^V\d+$/.test(x)));
const ff=process.env.FFMPEG_PATH||path.join(os.homedir(),'Apps/ffmpeg/bin/ffmpeg.exe');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function encoded(input){const p=spawnSync(ff,['-nostdin','-v','error','-i',input,'-map','0:a:0','-vn','-c:a','copy','-f','adts','pipe:1'],{windowsHide:true,maxBuffer:64*1024*1024,timeout:120000});if(p.status!==0)throw Error(p.stderr);return hash(p.stdout)}
function pcm(input){const p=spawnSync(ff,['-nostdin','-v','error','-i',input,'-map','0:a:0','-vn','-f','f32le','pipe:1'],{windowsHide:true,maxBuffer:128*1024*1024,timeout:120000});if(p.status!==0)throw Error(p.stderr);return hash(p.stdout)}
const records=[];
for(const item of manifest.filter(x=>!selected.size||selected.has(x.id))){const f=path.join(data,`${item.id}-mixed.json`),record=JSON.parse(fs.readFileSync(f,'utf8'));record.aac_adts_sha256=encoded(path.join(project,record.file));record.source_aac_adts_sha256=encoded(item.path);record.aac_bitstream_identical_to_source=record.aac_adts_sha256===record.source_aac_adts_sha256;record.native_pcm_sha256=pcm(path.join(project,record.file));record.source_native_pcm_sha256=pcm(item.path);record.native_pcm_format={sample_format:'f32le',channels:record.channels,sample_rate:record.sample_rate,resampled:false,note:'Native-rate decoded stereo PCM, not a perceptual fingerprint. Container edit lists and padding may affect the decoded boundary.'};fs.writeFileSync(f,JSON.stringify(record,null,2));records.push(record);console.log(item.id,record.aac_bitstream_identical_to_source)}
const index=path.join(data,'mixed-index.json');
const prior=selected.size&&fs.existsSync(index)?JSON.parse(fs.readFileSync(index,'utf8').replace(/^\uFEFF/,'')):[];
const updated=new Set(records.map(x=>x.id));
fs.writeFileSync(index,JSON.stringify([...prior.filter(x=>!updated.has(x.id)),...records].sort((a,b)=>a.id.localeCompare(b.id)),null,2));
