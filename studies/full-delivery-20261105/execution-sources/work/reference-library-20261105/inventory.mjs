import fs from 'node:fs';import path from 'node:path';import{spawnSync}from'node:child_process';import{createHash}from'node:crypto';
const cwd=process.cwd(),work=path.join(cwd,'work/reference-library-20261105'),out=path.join(cwd,'outputs/reference-library-20261105');
fs.mkdirSync(work,{recursive:true});for(const p of ['data','data/frame-analysis','evidence','reviews','scripts'])fs.mkdirSync(path.join(out,p),{recursive:true});
const old=JSON.parse(fs.readFileSync(path.join(cwd,'outputs/reference-editing-study/local-config.json'),'utf8').replace(/^\uFEFF/,''));
const names=[
'复制人的灵魂会是什么颜色_银翼杀手2049_重返暑假计划_经典重温计划_了不起的混剪团.mp4',
'盛夏已去如约而至的是落叶卫衣晚风和烟花_江南_剪辑_镜头下的西湖_机位天才已就位_氛围感.mp4',
'山野向晚落日归山海所有疲惫随暮色散开手机摄影手机摄影_Angel._OK.mp4',
'画面总是惊人的相似..第三期_看了不烧心_被选召的漫剪团_国漫_充能计划_转场_抖音精选App次元季.mp4',
'只要有以太的存在人类就能够飞翔关于莉莉周的一切_岩井俊二_电影美学_了不起的混剪团_抖音精选.mp4',
'一路上遇到的每个角色都有他的意义_国漫_灵笼_抖音世界书共创计划_世界书共创人_国漫美学.mp4',
'你我都是对方唯一的挚友_夏油杰_五条悟_咒术回战_被选召的漫剪团_青年创作者成长计划.mp4',
'复仇者们集结_了不起的混剪团_一步秒入漫威宇宙_我的观影后遗症漫威剪刀手_复仇者联盟5.mp4',
'Is_it_better_to_speak_or_die_edit.mp4',
'什么蜘蛛侠是彼得帕克_被选召的漫剪团_了不起的混剪团_蜘蛛侠_抖音精选_青年创作者成长计划.mp4'];
const sources=[...Object.entries(old.media).map(([id,file])=>({id,path:file})),...names.map((name,i)=>({id:`V${i+11}`,path:path.join('C:/Users/PC/Downloads',name)}))];
const manifest=[];
for(const s of sources){const stat=fs.statSync(s.path);const r=spawnSync('C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe',['-v','error','-show_streams','-show_format','-of','json',s.path],{encoding:'utf8',windowsHide:true,maxBuffer:16*1024*1024});if(r.status!==0)throw Error(r.stderr);const meta=JSON.parse(r.stdout),v=meta.streams.find(x=>x.codec_type==='video'),a=meta.streams.find(x=>x.codec_type==='audio');const [n,d]=v.avg_frame_rate.split('/').map(Number);manifest.push({...s,name:path.basename(s.path),bytes:stat.size,sha256:createHash('sha256').update(fs.readFileSync(s.path)).digest('hex'),duration:Number(v.duration||meta.format.duration),containerDuration:Number(meta.format.duration),width:v.width,height:v.height,fps:v.avg_frame_rate,nominalFps:v.r_frame_rate,fpsValue:n/d,frameCount:v.nb_frames,videoCodec:v.codec_name,audioCodec:a?.codec_name,audioSampleRate:a?.sample_rate,audioChannels:a?.channels,batch:Number(s.id.slice(1))<=10?1:2});}
fs.writeFileSync(path.join(work,'manifest.local.json'),JSON.stringify(manifest,null,2));fs.writeFileSync(path.join(out,'data/media-index.json'),JSON.stringify(manifest.map(({path,...x})=>x),null,2));fs.writeFileSync(path.join(out,'local-media-paths.json'),JSON.stringify(Object.fromEntries(manifest.map(m=>[m.id,m.path])),null,2));console.log(JSON.stringify({count:manifest.length,duration:manifest.reduce((a,b)=>a+b.duration,0),bytes:manifest.reduce((a,b)=>a+b.bytes,0),videos:manifest.map(m=>({id:m.id,duration:m.duration,fps:m.fps,size:`${m.width}x${m.height}`}))},null,2));
