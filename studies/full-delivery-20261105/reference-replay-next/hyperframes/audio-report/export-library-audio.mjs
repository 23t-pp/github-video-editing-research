// Only transforms: fixed -6.4 dB gain, trim 8 silent-tail native samples,
// normal sample-rate conversion. No new notes, looping or tempo processing.
import fs from 'node:fs';import path from 'node:path';import os from 'node:os';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
const reportRoot=import.meta.dirname,project=path.resolve(reportRoot,'..'),workspace=path.resolve(project,'../../..');
const audioRoot=path.join(project,'assets/audio');fs.mkdirSync(audioRoot,{recursive:true});
const ff=process.env.FFMPEG_PATH||path.join(os.homedir(),'Apps/ffmpeg/bin/ffmpeg.exe');
const args=process.argv.slice(2),sourceOption=args.indexOf('--source');
const library=path.join(workspace,'outputs/reference-library-20261105/audio/music-candidates/V07__music-candidate.m4a');
const originalCopy=path.join(audioRoot,'V07-library-original.m4a');
const source=sourceOption>=0?path.resolve(args[sourceOption+1]):fs.existsSync(library)?library:originalCopy;
const expectedSHA='ab3f9d2cba177aa62d7d3bc3fd63d06ae17607ac5b9ee4f37e3655a709163654';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const original=fs.readFileSync(source);if(hash(original)!==expectedSHA)throw Error('V07 candidate SHA256 mismatch; source must be the approved library candidate.');
fs.writeFileSync(originalCopy,original);
function run(argv,maxBuffer=64*1024*1024){const r=spawnSync(ff,['-nostdin',...argv],{windowsHide:true,maxBuffer});if(r.status!==0)throw Error(r.stderr?.toString()||r.error?.message||'FFmpeg failed');return r;}
function repairWav(b){b.writeUInt32LE(b.length-8,4);let pos=12;while(pos+8<=b.length){const id=b.toString('ascii',pos,pos+4),size=b.readUInt32LE(pos+4);if(id==='data'){b.writeUInt32LE(b.length-pos-8,pos+4);return b;}pos+=8+size+(size%2);}throw Error('Missing WAV data');}
function dataBytes(b){let pos=12;while(pos+8<=b.length){const id=b.toString('ascii',pos,pos+4),n=b.readUInt32LE(pos+4);if(id==='data')return n;pos+=8+n+(n%2);}throw Error('Missing WAV data');}
function loudness(file){const r=run(['-hide_banner','-i',file,'-af','loudnorm=I=-16:TP=-1:LRA=11:print_format=json','-f','null','-']);const m=JSON.parse(r.stderr.toString().match(/\{\s*"input_i"[\s\S]*?\}/)[0]);return {integrated_lufs:Number(m.input_i),true_peak_dbtp:Number(m.input_tp),lra_lu:Number(m.input_lra)};}
const native=run(['-v','error','-i',originalCopy,'-map','0:a:0','-f','f32le','pipe:1']).stdout;
const nativeFrames=native.length/(4*2);if(nativeFrames!==1323008)throw Error(`Unexpected native V07 sample count ${nativeFrames}`);
const filter='atrim=end_sample=1323000,volume=-6.4dB,aresample=48000,atrim=end_sample=1440000';
const bgm=repairWav(run(['-v','error','-i',originalCopy,'-map','0:a:0','-af',filter,'-ac','2','-ar','48000','-c:a','pcm_s24le','-f','wav','pipe:1']).stdout);
if(dataBytes(bgm)!==1440000*2*3)throw Error('Incorrect PCM24 output sample count');
fs.writeFileSync(path.join(audioRoot,'bgm.wav'),bgm);fs.writeFileSync(path.join(audioRoot,'master.wav'),bgm);
const markerFile=path.join(reportRoot,'priority-onsets.json'),workMarkers=path.join(workspace,'work/reference-replay-v07/audio/editing-markers.json');
let markers;
if(fs.existsSync(markerFile))markers=JSON.parse(fs.readFileSync(markerFile,'utf8'));
else{
 const studied=JSON.parse(fs.readFileSync(workMarkers,'utf8'));
 markers={source_id:'V07',source_sha256:expectedSHA,timing:'Original library candidate from zero, no tempo or start-offset change. Native waveform RMS-rise anchors, not confirmed beats/downbeats. STFT/window placement uncertainty about 10–20ms; video-frame quantization is separately recorded.',fps:25,duration_frames:750,events:studied.priority_onsets};
 fs.writeFileSync(markerFile,JSON.stringify(markers,null,2));
}
if(markers.events.length!==24||markers.source_sha256!==expectedSHA)throw Error('Wrong V07 priority markers');
fs.writeFileSync(path.join(reportRoot,'priority-onsets.csv'),'time_sec,sample_44100,frame_25fps,frame_time_sec,frame_error_ms,flux_strength_p95_units\n'+markers.events.map(e=>[e.time_sec,e.sample_44100,e.output_frame_25fps,e.frame_time_sec,e.frame_error_ms,e.flux_strength_p95_units].join(',')).join('\n')+'\n');
const measured=loudness(path.join(audioRoot,'bgm.wav'));
const finalDecode=run(['-v','error','-xerror','-i',path.join(audioRoot,'bgm.wav'),'-f','f32le','pipe:1']);
if(finalDecode.stdout.length!==1440000*2*4)throw Error('Full-decode sample count differs');
const samples=new Float32Array(finalDecode.stdout.buffer.slice(finalDecode.stdout.byteOffset,finalDecode.stdout.byteOffset+finalDecode.stdout.byteLength));
let peak=0,finite=true;for(const s of samples){finite&&=Number.isFinite(s);peak=Math.max(peak,Math.abs(s));}
const bgmHash=hash(bgm),masterHash=hash(fs.readFileSync(path.join(audioRoot,'master.wav')));
const report={passed:finite&&peak<1&&bgmHash===masterHash,source:{id:'V07',music_title:null,music_title_status:'Unknown; no song identification performed.',library_path:'outputs/reference-library-20261105/audio/music-candidates/V07__music-candidate.m4a',library_candidate_sha256:expectedSHA,original_reference_video_basename:'国漫无缝转场帅是一种感觉_不良人_光阴之外_仙逆_国漫_混剪.mp4',original_reference_video_sha256:'42f64677eef7f21a940661e7646be0a864bfcd87a80294afa4c4df38de5566cc',copied_asset:'assets/audio/V07-library-original.m4a',copy_bit_identical:true,content:'Previously generated local UVR Instrumental candidate from V07; not a certified vocal-free master and not the original mixed video audio.'},processing:{native_sample_rate:44100,native_channels:2,native_sample_frames:nativeFrames,native_decoded_duration_sec:nativeFrames/44100,kept_native_sample_frames:1323000,removed_tail_sample_frames:8,removed_tail_sec:8/44100,fixed_gain_db:-6.4,filter,sample_rate_conversion_only:true,time_stretch:false,loop:false,new_composition:false,loudnorm_used_as_effect:false},output:{bgm:'assets/audio/bgm.wav',preview_master:'assets/audio/master.wav',sample_rate:48000,channels:2,pcm_bits:24,sample_frames:1440000,duration_sec:30,bytes:bgm.length,bgm_sha256:bgmHash,master_sha256:masterHash,master_byte_identical_to_bgm:bgmHash===masterHash,loudness:measured,sample_peak_dbfs:20*Math.log10(peak),all_samples_finite:finite,full_decode_passed:true},video_timing:{fps:25,frame_count:750,last_frame_zero_based:749,last_frame_interval_sec:[29.96,30],end_exclusive_sec:30},onsets:{count:24,json:'audio-report/priority-onsets.json',csv:'audio-report/priority-onsets.csv',kind:'Measured onset candidates, not confirmed beats.'},listened:false,limitations:['No actual authoring-agent listening; quality and residual vocals/SFX require human audition.','Preview master has no additional car-source effects yet; it is exactly bgm.wav.','Approximately 100/50 BPM periodicity remains ambiguous; no fixed tempo grid was imposed.']};
fs.writeFileSync(path.join(reportRoot,'export-report.json'),JSON.stringify(report,null,2));
let md='# V07库内原音乐：来源与30秒导出\n\n本次直接使用音乐库内V07的音乐主体候选，不另作曲、不循环、不拉伸，不沿用旧作128 BPM。曲名**未知**，没有根据视频标题猜歌名。\n\n来源为`outputs/reference-library-20261105/audio/music-candidates/V07__music-candidate.m4a`，对应用户参考视频`国漫无缝转场帅是一种感觉_不良人_光阴之外_仙逆_国漫_混剪.mp4`（V07）。该库文件是此前真实本地UVR处理得到的Instrumental候选，可能保留人声/SFX或损伤音乐，不能称为保证纯净的原版伴奏。\n\n';
md+=`库内M4A已原样复制到\`assets/audio/V07-library-original.m4a\`，SHA256：\`${expectedSHA}\`，逐字节一致。\n\n`;
md+='## 实际处理\n\n原生解码1,323,008帧、44.1kHz双声道，30.000181406秒；只去除末尾8个极低电平采样帧（0.181406ms），保留1,323,000帧，再正常重采样到48kHz。固定线性降6.4dB，没有动态响度滤镜、音符生成或节奏变换。`loudnorm`只用于测量，未作用到成品。\n\n';
md+=`成品\`assets/audio/bgm.wav\`为48kHz立体声PCM24，**1,440,000采样帧、30.000秒**。实测综合响度 **${measured.integrated_lufs.toFixed(2)} LUFS**、真峰值 **${measured.true_peak_dbtp.toFixed(2)} dBTP**、LRA **${measured.lra_lu.toFixed(2)} LU**。完整解码、采样数、有限值和无采样削波检查通过。SHA256：\`${bgmHash}\`。\n\n`;
md+='预览用`assets/audio/master.wav`与bgm字节完全一致，尚未叠加汽车动作原声；后续加入源声必须另混并重新测总声，不能同时播放bgm和master。\n\n25fps输出750帧；最后显示帧编号749，覆盖29.960–30.000秒，30.000为结束边界。原参考视频751帧的末画面帧不要求保留，因为当前剪辑长度由库内音乐决定。原有约29.424秒后的低电平收尾被保留，不能称为数学全零。\n\n## 24个画面对齐起音\n\n起音来自原候选的谱变化与波形RMS上升锚点；未做听觉确认，**不是beat/downbeat**。原生波形定位约有10–20ms窗口不确定性，25fps就近帧位另有最多20ms量化误差。不要把小数位当听觉精度保证，也不要机械地每个事件都切镜。\n\n|音频秒|原生采样编号|25fps零基帧|画面秒|量化误差ms|\n|---:|---:|---:|---:|---:|\n';
for(const e of markers.events)md+=`|${e.time_sec.toFixed(6)}|${e.sample_44100}|${e.output_frame_25fps}|${e.frame_time_sec.toFixed(2)}|${e.frame_error_ms.toFixed(3)}|\n`;
md+='\n## 重建与验收范围\n\n在工程根（有assets与audio-report的目录）运行：\n\n```powershell\nnode .\\audio-report\\export-library-audio.mjs\n```\n\n脚本优先读取工作区的库文件；独立工程中缺少旧库时读取已经校验的`assets/audio/V07-library-original.m4a`。也可用`--source`指定同SHA的库文件。需要Node与FFmpeg；后者可用`FFMPEG_PATH`指定。遇Node写入限制时改用已有可写Node运行时。所有二进制由FFmpeg stdout返回给Node保存，不更改系统设置。\n\n完整参数、实际响度、SHA、采样数和检查结果见`export-report.json`；起音数据见`priority-onsets.json/csv`。制作代理未实际监听，没有宣称听感、曲名、人声/SFX清除率或最终汽车声混音已验收。\n';
fs.writeFileSync(path.join(reportRoot,'README.md'),md);
if(!report.passed)throw Error('Export validation failed');
console.log(JSON.stringify({passed:report.passed,sample_frames:report.output.sample_frames,duration_sec:30,original_sha256:expectedSHA,bgm_sha256:bgmHash,master_identical:report.output.master_byte_identical_to_bgm,loudness:measured,onsets:24}));
