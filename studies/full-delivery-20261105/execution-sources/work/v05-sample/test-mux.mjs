import fs from 'node:fs';import{spawnSync}from'node:child_process';
const root=process.cwd(),ff='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe',fp='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe';
const input=root+'/outputs/v05-six-panel/V05六格卡片_成片.mp4';
for(const [label,flags] of [['delay','frag_keyframe+delay_moov+default_base_moof'],['negative','frag_keyframe+empty_moov+negative_cts_offsets']]){
const r=spawnSync(ff,['-v','error','-i',input,'-c','copy','-movflags',flags,'-f','mp4','pipe:1'],{maxBuffer:256*1024*1024,windowsHide:true});if(r.status!==0)throw Error(r.stderr.toString());const file=root+'/work/v05-sample/'+label+'.mp4';fs.writeFileSync(file,r.stdout);const p=spawnSync(fp,['-v','error','-show_entries','format=duration:stream=index,start_time,duration','-of','json',file],{encoding:'utf8',windowsHide:true});console.log(label,p.stdout)}
