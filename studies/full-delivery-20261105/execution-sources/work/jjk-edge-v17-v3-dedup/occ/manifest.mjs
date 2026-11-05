import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {root,read} from './client.mjs';
export const manifestPath=path.resolve(process.env.OCC_EDIT_MANIFEST||path.join(root,'outputs/jjk-edge-v17-v3-dedup/hyperframes/edit.json'));
export const base=path.dirname(manifestPath);
export const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
export const fileFor=asset=>path.resolve(base,asset);
export function loadManifest({hf=false,probe=false}={}){
 const m=read(manifestPath);for(const k of ['width','height','fps','durationFrames'])assert(Number.isSafeInteger(m[k])&&m[k]>0,k);
 assert.equal(m.width,1920);assert.equal(m.height,1080);assert.equal(m.fps,24);assert.equal(m.durationFrames,1440);assert(m.title);
 const videos=new Map();
 function sequence(rows,name){assert(Array.isArray(rows)&&rows.length>0,name);let cursor=0;for(const [n,s] of rows.entries()){
  assert.equal(s.startFrame,cursor,`${name}[${n}] gap/overlap`);for(const k of ['startFrame','frames','assetStartFrame'])assert(Number.isSafeInteger(s[k]??(k==='assetStartFrame'?0:undefined))&&(s[k]??0)>=0,`${name}[${n}].${k}`);assert(s.frames>0);cursor+=s.frames;
  const f=fileFor(s.asset);assert(fs.existsSync(f),f);if(!videos.has(f))videos.set(f,{file:f,sha256:hash(f)});
 }assert.equal(cursor,m.durationFrames,`${name} total`);}
 sequence(m.shots,'shots');if(hf)sequence(m.hfChunks,'hfChunks');
 // Keep every declared source available in the independent V2 media pool,
 // including editorial alternates that are not currently placed on a track.
 for(const asset of m.assets||[]){const f=fileFor(asset.asset);assert(fs.existsSync(f),f);if(!videos.has(f))videos.set(f,{file:f,sha256:hash(f)});}
 if(probe){for(const [f,p] of videos){const r=spawnSync('C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe',['-v','error','-count_frames','-show_streams','-of','json',f],{encoding:'utf8',windowsHide:true});assert.equal(r.status,0,r.stderr);const d=JSON.parse(r.stdout),v=d.streams.find(x=>x.codec_type==='video');assert(v,f);assert.equal(v.width,m.width,f);assert.equal(v.height,m.height,f);assert.equal(v.avg_frame_rate,`${m.fps}/1`,f);assert(!d.streams.some(x=>x.codec_type==='audio'),`Video must be silent: ${f}`);p.frames=Number(v.nb_read_frames||v.nb_frames);}
 for(const s of [...m.shots,...(hf?m.hfChunks:[])])assert(videos.get(fileFor(s.asset)).frames>=(s.assetStartFrame??0)+s.frames,`${s.id||s.asset} source overflow`);}
 const master=fileFor(m.audio.master);assert(fs.existsSync(master),master);
 if(probe){const r=spawnSync('C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe',['-v','error','-show_streams','-show_format','-of','json',master],{encoding:'utf8',windowsHide:true});assert.equal(r.status,0,r.stderr);const d=JSON.parse(r.stdout),a=d.streams.find(x=>x.codec_type==='audio');assert.equal(a.channels,2);assert.equal(Number(a.sample_rate),48000);assert(Math.abs(Number(a.duration||d.format.duration)-m.durationFrames/m.fps)<1/48000);}
 for(const t of m.nativeTexts||[]){assert(t.id&&t.text);assert(Number.isSafeInteger(t.startFrame)&&Number.isSafeInteger(t.frames));assert(t.startFrame>=0&&t.frames>0&&t.startFrame+t.frames<=m.durationFrames);}
 const nativeManifestSha256=crypto.createHash('sha256').update(JSON.stringify({title:m.title,width:m.width,height:m.height,fps:m.fps,durationFrames:m.durationFrames,audio:m.audio,shots:m.shots,nativeTexts:m.nativeTexts||[]})).digest('hex');
 return {...m,master,videos,manifestSha256:hash(manifestPath),nativeManifestSha256};
}
if(process.argv.includes('--validate')){const m=loadManifest({hf:process.argv.includes('--hf'),probe:true});console.log(JSON.stringify({manifestPath,fps:m.fps,durationFrames:m.durationFrames,shots:m.shots.length,chunks:m.hfChunks?.length||0,texts:m.nativeTexts?.length||0,videos:m.videos.size,manifestSha256:m.manifestSha256}));}
