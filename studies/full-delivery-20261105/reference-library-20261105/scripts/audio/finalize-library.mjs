import fs from 'node:fs';import path from 'node:path';import os from 'node:os';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
const project=path.resolve(import.meta.dirname,'../..'),workspace=path.resolve(project,'../..'),work=path.join(workspace,'work/reference-library-20261105'),data=path.join(project,'data/audio'),out=path.join(project,'audio/music-candidates');
fs.mkdirSync(out,{recursive:true});
const read=file=>JSON.parse(fs.readFileSync(file,'utf8').replace(/^\uFEFF/,''));
const ff=process.env.FFMPEG_PATH||path.join(os.homedir(),'Apps/ffmpeg/bin/ffmpeg.exe'),fp=process.env.FFPROBE_PATH||path.join(os.homedir(),'Apps/ffmpeg/bin/ffprobe.exe');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const mixes=read(path.join(data,'mixed-index.json'));
const hf=await import(pathToFileURL(path.join(process.env.HYPERFRAMES_INSTALL||path.join(os.homedir(),'Apps/hyperframes/node_modules/hyperframes'),'dist/chunk-NOH32H42.js')));
const override={V01:[139.9,69.9],V02:[128,64],V03:[88.5,177],V04:[123.9,61.9],V05:[140,93.4,56,96.9],V06:[105.9,53,212],V07:[100.2,50],V08:[140,70],V09:[109.3,54.9],V10:[80.1,160.2,40],V11:[140.1,70.1],V12:[135.2,102.2,51],V13:[112.9,56.5],V14:[149.9,75,99.8],V15:[122,81.2],V16:[58.1],V17:[80.3,160.6],V18:[82.1,164.2],V19:[137.3,141.3],V20:[139.8,69.9]};
const warnings={V05:'频谱周期56/93.4、HF96.9与能量基线139.5明显冲突，不给唯一曲速。',V06:'130秒长音轨须分段；87.4–88.46秒低电平区里模型仍外推beat，不能把网格当真实声响。',V12:'片段很短，HF102.2与135.2/51等周期峰冲突，不能确定曲速。',V15:'122与81.2呈3:2节奏型歧义，不是简单倍半速；不可仅用HF较高分数下结论。',V16:'HF拒绝稳定拍点；局部约58周期只可作为人工试听起点。',V17:'HF拒绝稳定拍点；80/160与局部其他周期并存。',V19:'HF拒绝稳定拍点且confidence很低，137/141只为弱周期候选。',V20:'HF刚过门槛，局部约134–146变化明显；不宜整片固定140网格。'};
function run(program,args,maxBuffer=256*1024*1024){const p=spawnSync(program,args,{windowsHide:true,maxBuffer,timeout:180000});if(p.status!==0)throw Error((p.stderr?.toString()||p.error?.message||'Process failed').slice(-2000));return p;}
function tagsFor(r){if(!r.hyperframes.beats.times.length||warnings[r.id])return ['手工起音锚点','先听辨再定拍','局部节奏练习'];const bpm=r.hyperframes.tempo.value;return bpm>=120?['汽车/动作/运动素材建议','快切与半拍标记','能量起伏分段']:bpm<85?['人物/旅拍/氛围素材建议','长镜头与倍速细分','整拍推进']:['人物/旅行/动作素材建议','整拍镜头切换','段落推进'];}
const checkpoint=path.join(work,'audio-work/separation-results.local.json');
const ready=new Set(fs.existsSync(checkpoint)?read(checkpoint).map(r=>r.id):[]);
let completed=0;const index=[];
for(const mix of mixes){
 const r=read(path.join(data,`${mix.id}.json`)),stemName=`${mix.id}.stereo_(Instrumental)_UVR_MDXNET_KARA_2.wav`,stem=path.join(work,'audio-work/stems',stemName),candidateFile=path.join(out,`${mix.id}__music-candidate.m4a`),metadataFile=path.join(data,`${mix.id}-candidate.json`);
 let candidate=null;
 if(ready.has(mix.id)&&fs.existsSync(stem)&&fs.statSync(stem).size>44){
  const sourceHash=hash(fs.readFileSync(stem));
  if(fs.existsSync(metadataFile)){const old=read(metadataFile);if(old.source_stem_sha256===sourceHash&&old.encoding_profile==='aac192k-relative-fragments-1s-v1'&&fs.existsSync(candidateFile))candidate=old;}
  if(!candidate){
   const result=run(ff,['-nostdin','-v','error','-i',stem,'-map','0:a:0','-vn','-c:a','aac','-b:a','192k','-movflags','frag_keyframe+delay_moov+default_base_moof','-frag_duration','1000000','-f','mp4','pipe:1']);fs.writeFileSync(candidateFile,result.stdout);
   const probe=JSON.parse(run(fp,['-v','error','-show_entries','stream=codec_name,sample_rate,channels','-show_entries','format=duration','-of','json',candidateFile],8*1024*1024).stdout.toString());
   const p=run(ff,['-nostdin','-hide_banner','-i',candidateFile,'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],8*1024*1024);const measured=JSON.parse(p.stderr.toString().match(/\{\s*"input_i"[\s\S]*?\}/)[0]);
   const decoded=run(ff,['-nostdin','-v','error','-i',candidateFile,'-map','0:a:0','-vn','-f','f32le','pipe:1']).stdout;
   const sr=Number(probe.streams[0].sample_rate),channels=probe.streams[0].channels;
   candidate={id:mix.id,file:`audio/music-candidates/${mix.id}__music-candidate.m4a`,bytes:result.stdout.length,sha256:hash(result.stdout),source_stem_sha256:sourceHash,native_pcm_sha256:hash(decoded),native_pcm_format:{sample_format:'f32le',sample_rate:sr,channels,resampled:false},duration_sec:decoded.length/(4*sr*channels),encoded_container_duration_sec:Number(probe.format.duration),codec:probe.streams[0].codec_name,sample_rate:sr,channels,loudness:{integrated_lufs:Number(measured.input_i),true_peak_dbtp:Number(measured.input_tp),loudness_range_lu:Number(measured.input_lra)},separation:{tool:'audio-separator',version:'0.48.0',model:'UVR_MDXNET_KARA_2.onnx',provider:'CPUExecutionProvider',threads:2,stem:'Instrumental',output_normalization:{peak_threshold:0.95,amplification_threshold:0.0},aac_reencoded:true},status:'真实本地模型分离后的音乐主体候选；未听辨确认，可能残留人声、对白、和声或SFX，也可能损伤音乐。不是纯BGM保证。',listened:false,vocal_removal_verified:false,sfx_removal_verified:false};
   candidate.encoding_profile='aac192k-relative-fragments-1s-v1';
   fs.writeFileSync(metadataFile,JSON.stringify(candidate,null,2));
  }
  if(!candidate.rhythm){
   const pcm=run(ff,['-nostdin','-v','error','-i',candidateFile,'-ac','1','-ar','22050','-f','f32le','pipe:1']).stdout;
   const samples=new Float32Array(pcm.buffer.slice(pcm.byteOffset,pcm.byteOffset+pcm.byteLength));
   const signal={sampleRate:22050,channels:[samples]},rhythm=hf.rhythm(signal),tempo=hf.tempoOf(rhythm.beats.times);
   candidate.rhythm={scope:'模型分离后的候选音轨，未做听觉确认',method:'HyperFrames 0.8.216 local signal spectral flux + autocorrelation + DP',bpm:tempo.value,confidence:rhythm.beats.confidence,reason:rhythm.beats.reason??null,beat_times:rhythm.beats.times};
   fs.writeFileSync(metadataFile,JSON.stringify(candidate,null,2));
  }
  completed++;
 }
 const bpmCandidates=override[mix.id]||[r.hyperframes.tempo.value,...r.spectral_autocorrelation.candidates.slice(0,2).map(x=>x.bpm)].filter((v,i,a)=>v&&a.indexOf(v)===i);
 const c=r.hyperframes.beats.confidence,conf=warnings[mix.id]?'低/存在冲突':!r.hyperframes.beats.times.length?'低/无稳定拍点':c>=.35?'较高周期线索；未听辨确认':'中等周期线索；未听辨确认';
 const row={id:mix.id,title:`${mix.id} · 未识别曲名`,source_video_name:mix.source_video_name,music_name:null,music_name_status:mix.music_name_status,duration_sec:mix.duration_sec,mix_path:mix.file,no_vocals_candidate_path:candidate?.file??null,music_candidate_path:candidate?.file??null,separation_status:candidate?'complete':'pending',bpm_candidates:bpmCandidates,confidence:conf,tempo_scope:'bpm_candidates来自原始混合轨；分离候选另见candidate.rhythm',tempo_basis:{hf_bpm:r.hyperframes.tempo.value,hf_internal_confidence:c,hf_beat_count:r.hyperframes.beats.times.length,warning:warnings[mix.id]||'半倍/倍速与切分节奏歧义仍需试听。'},tags:tagsFor(r),tag_basis:'按原始混合轨的信号周期、时长和能量起伏给出的剪辑适用素材建议；不是已听辨的乐器、风格或已识别歌曲。',mix,candidate,analysis_path:`data/audio/${mix.id}.json`,listened:false};
 mix.separation_status=row.separation_status;mix.no_vocals_candidate_path=row.no_vocals_candidate_path;
 fs.writeFileSync(path.join(data,`${mix.id}-mixed.json`),JSON.stringify(mix,null,2));
 index.push(row);
 if(r.actual_execution){delete r.actual_execution.uploaded;r.actual_execution.uploaded_to_analysis_service=false;}
 const report={...r,music_library:{mix_path:mix.file,no_vocals_candidate_path:candidate?.file??null,bpm_candidates:bpmCandidates,confidence:conf,tags:row.tags,warning:row.tempo_basis.warning}};
 fs.writeFileSync(path.join(data,`${mix.id}.json`),JSON.stringify(report,null,2));
}
fs.writeFileSync(path.join(data,'music-index.json'),JSON.stringify(index,null,2));fs.writeFileSync(path.join(data,'index.json'),JSON.stringify(index,null,2));
fs.writeFileSync(path.join(data,'mixed-index.json'),JSON.stringify(mixes,null,2));
function groups(records,get){const map=new Map();for(const r of records){const key=get(r);if(!key)continue;if(!map.has(key))map.set(key,[]);map.get(key).push(r.id)}return [...map].filter(([,ids])=>ids.length>1).map(([sha256,ids])=>({sha256,ids}));}
const dedup={method:'Only exact SHA256 equality; no fingerprint or musical-similarity inference.',mixed_files:groups(index,r=>r.mix.sha256),mixed_aac_adts:groups(index,r=>r.mix.aac_adts_sha256),mixed_native_decoded_pcm:groups(index,r=>r.mix.native_pcm_sha256),source_native_decoded_pcm:groups(index,r=>r.mix.source_native_pcm_sha256),candidate_files:groups(index,r=>r.candidate?.sha256),candidate_native_decoded_pcm:groups(index,r=>r.candidate?.native_pcm_sha256),counts:{mixed:index.length,candidates:completed,aac_bitstream_preserved:index.filter(r=>r.mix.aac_bitstream_identical_to_source).length},note:'No exact duplicate means only these whole mixed tracks/PCM differ. It does not prove different underlying BGM; speech, SFX, gain, trims and encoding can change hashes.'};
fs.writeFileSync(path.join(data,'dedup.json'),JSON.stringify(dedup,null,2));
const summary={updated_at:new Date().toISOString(),mixed_count:index.length,candidate_count:completed,complete:completed===index.length,source_audio_decoded_seconds:index.reduce((s,r)=>s+r.mix.source_decoded_duration_sec,0),mixed_bytes:index.reduce((s,r)=>s+r.mix.bytes,0),candidate_bytes:index.reduce((s,r)=>s+(r.candidate?.bytes||0),0),music_names_identified:0,automatic_listening_performed:false,cloud_audio_processing_uploads:false,index:'data/audio/music-index.json'};fs.writeFileSync(path.join(data,'library-summary.json'),JSON.stringify(summary,null,2));
let md='# 参考音轨与音乐主体候选库\n\n原始混合音轨20条；真实本地模型分离候选'+completed+'条。所有曲名未识别，尚未实际听辨。候选可能残留对白、人声或SFX，也可能损伤音乐，不能当纯BGM保证。\n\nBPM为信号分析候选；素材适用标签是剪辑建议，不是歌曲/乐器识别。原始混合轨适合研究原片音画关系；音乐主体候选需试听后再决定是否用来重新配画面。\n\n|ID|原混合轨时长|BPM候选|周期信度|原混合轨|音乐主体候选|\n|---|---:|---|---|---|---|\n';
for(const r of index)md+=`|${r.id}|${r.mix.duration_sec.toFixed(2)}s|${r.bpm_candidates.join(' / ')}|${r.confidence}|[M4A](mixed/${r.id}__mixed.m4a)|${r.candidate?`[M4A](music-candidates/${r.id}__music-candidate.m4a)`:'生成中'}|\n`;
md+='\n完整元数据、SHA256、响度与分离说明见 [music-index.json](../data/audio/music-index.json)，方法见 [processing-notes.md](../data/audio/processing-notes.md)。\n\n精确去重按文件、AAC编码内容和原生双声道PCM分别记录。无精确重复不代表不同BGM；未使用声纹相似当同曲确证。\n';
fs.writeFileSync(path.join(project,'audio/README.md'),md);
console.log(JSON.stringify(summary));

