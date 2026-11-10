import fs from 'node:fs/promises';import path from 'node:path';import{spawn}from'node:child_process';
const project=path.resolve(import.meta.dirname,'..');
const manifestFile=process.argv[2]||path.resolve(project,'../../work/reference-library-20261105/manifest.local.json');
const manifest=JSON.parse((await fs.readFile(manifestFile,'utf8')).replace(/^\uFEFF/,''));
const selectIds=process.argv.slice(3),ff=process.env.FFMPEG_PATH||'ffmpeg',fp=process.env.FFPROBE_PATH||'ffprobe';
const font=process.env.ANALYSIS_FONT||'C\\:/Windows/Fonts/consola.ttf';
const stamp=`drawtext=fontfile='${font}':text='F%{n} %{pts\\:hms}':fontsize=11:fontcolor=white:box=1:boxcolor=black@0.75:x=3:y=3`;
function exec(exe,args){return new Promise((resolve,reject)=>{const p=spawn(exe,args,{windowsHide:true});const b=[];let log='';p.stdout.on('data',x=>b.push(x));p.stderr.on('data',x=>log+=x.toString());p.on('error',reject);p.on('close',c=>c===0?resolve({data:Buffer.concat(b),log}):reject(Error(`${exe} exit ${c}: ${log.slice(-3500)}`)))})}
const run=args=>exec(ff,['-hide_banner','-nostdin','-threads','2',...args]);
const fit=(w,h)=>`scale=${w}:${h}:force_original_aspect_ratio=decrease,pad=${w}:${h}:(ow-iw)/2:(oh-ih)/2:black`;
function splitJPEG(b){const frames=[];let offset=0;while(offset<b.length){const start=b.indexOf(Buffer.from([255,216]),offset);if(start<0)break;const end=b.indexOf(Buffer.from([255,217]),start+2);if(end<0)throw Error('Incomplete JPEG');frames.push(b.subarray(start,end+2));offset=end+2}return frames}
const r=(n,p=5)=>Number(n.toFixed(p));
async function analyze(item){
 const start=Date.now(),dir=path.join(project,'evidence',item.id),dataDir=path.join(project,'data/frame-analysis');await fs.mkdir(dir,{recursive:true});await fs.mkdir(dataDir,{recursive:true});
 const ptsData=await exec(fp,['-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time,pkt_duration_time,pict_type,key_frame','-of','json',item.path]);
 const native=JSON.parse(ptsData.data.toString()).frames.map((f,i)=>({i,pts:Number(f.best_effort_timestamp_time),keyFrame:!!f.key_frame,type:f.pict_type}));
 const raw=(await run(['-v','error','-i',item.path,'-map','0:v:0','-an','-vf','scale=96:54','-pix_fmt','rgb24','-fps_mode','passthrough','-f','rawvideo','pipe:1'])).data;
 const stride=96*54*3,count=raw.length/stride;if(!Number.isInteger(count)||count!==native.length)throw Error(`${item.id} frames decoded=${count}, pts=${native.length}`);
 const rows=[],candidates=[];let previous=null,previousHist=null,previousMean=0,duplicates=0;
 for(let i=0;i<count;i++){const frame=raw.subarray(i*stride,(i+1)*stride),hist=new Float64Array(24);let sum=0,mad=0,edge=0;for(let j=0;j<stride;j+=3){hist[frame[j]>>5]++;hist[8+(frame[j+1]>>5)]++;hist[16+(frame[j+2]>>5)]++;sum+=.2126*frame[j]+.7152*frame[j+1]+.0722*frame[j+2];if(previous)mad+=Math.abs(frame[j]-previous[j])+Math.abs(frame[j+1]-previous[j+1])+Math.abs(frame[j+2]-previous[j+2]);if(j>=3&&j%(96*3))edge+=Math.abs(frame[j+1]-frame[j-2]);}
 const mean=sum/(stride/3),duplicate=!!previous&&frame.equals(previous);if(duplicate)duplicates++;
 let hdiff=0;if(previousHist)for(let j=0;j<24;j++)hdiff+=Math.abs(hist[j]-previousHist[j]);hdiff/=2*stride;
 const record={frame:i,pts:native[i].pts,dt:i?native[i].pts-native[i-1].pts:0,mad:mad/(stride*255),histDelta:hdiff,luma:mean,edge:edge/((stride/3)*255),duplicate,flashCandidate:i>0&&Math.abs(mean-previousMean)>35};
 rows.push(record);if(i>0&&(record.histDelta>.23&&record.mad>.11||record.mad>.30))candidates.push({frame:i,time:r(record.pts),score:r(record.mad*.6+record.histDelta*.4),kind:record.flashCandidate?'cut-or-flash':'cut-or-motion'});
 previous=frame;previousHist=hist;previousMean=mean;
 }
 const csv=['frame,pts_seconds,delta_seconds,rgb_mad_0to1,histogram_delta_0to1,luma_0to255,edge_strength,identical_thumbnail_to_previous,flash_candidate',...rows.map(x=>[x.frame,r(x.pts,6),r(x.dt,6),r(x.mad),r(x.histDelta),r(x.luma,2),r(x.edge),+x.duplicate,+x.flashCandidate].join(','))].join('\n');await fs.writeFile(path.join(dataDir,item.id+'.csv'),csv);
 const reduced=candidates.filter((x,i,a)=>!i||x.time-a[i-1].time>.08||x.score>a[i-1].score*1.3);
 const atlas=(await run(['-v','error','-i',item.path,'-an','-vf',`${fit(160,90)},${stamp},tile=10x6:padding=2:margin=2:color=0x202020`,'-fps_mode','passthrough','-c:v','mjpeg','-q:v','3','-f','image2pipe','pipe:1'])).data;
 const sheets=splitJPEG(atlas),pages=[];for(let j=0;j<sheets.length;j++){const file=`native-${String(j+1).padStart(3,'0')}.jpg`;await fs.writeFile(path.join(dir,file),sheets[j]);const a=j*60,z=Math.min(count-1,a+59);pages.push({file,firstFrame:a,lastFrame:z,start:native[a].pts,end:native[z].pts,count:z-a+1});}
 if(sheets.length!==Math.ceil(count/60))throw Error(`${item.id} atlas pages ${sheets.length} should ${Math.ceil(count/60)}`);
 const ovStep=Math.max(1,Math.ceil(count/24));const overview=(await run(['-v','error','-i',item.path,'-an','-vf',`select=not(mod(n\\,${ovStep})),${fit(320,180)},${stamp},tile=4x6:padding=3:margin=3:color=0x202020`,'-frames:v','1','-fps_mode','passthrough','-c:v','mjpeg','-q:v','2','-f','image2pipe','pipe:1'])).data;await fs.writeFile(path.join(dir,'overview.jpg'),overview);
 const step=Math.max(1,Math.round(item.fpsValue));const timeline=(await run(['-v','error','-i',item.path,'-an','-vf',`select=not(mod(n\\,${step})),${fit(320,180)},${stamp},tile=5x6:padding=3:margin=3:color=0x202020`,'-fps_mode','passthrough','-c:v','mjpeg','-q:v','2','-f','image2pipe','pipe:1'])).data;
 const tl=splitJPEG(timeline);for(let j=0;j<tl.length;j++)await fs.writeFile(path.join(dir,`timeline-${String(j+1).padStart(2,'0')}.jpg`),tl[j]);
 const ds=rows.slice(1).map(x=>x.dt).filter(x=>x>0),min=Math.min(...ds),max=Math.max(...ds);const report={id:item.id,sourceSha256:item.sha256,nativeFrameCount:count,fps:item.fps,firstPts:native[0].pts,lastPts:native.at(-1).pts,ptsDeltaMin:r(min,8),ptsDeltaMax:r(max,8),variableFrameRateObserved:max-min>.0001,policy:'Decode native frames, preserve source PTS. No fps conversion, duplication or interpolation. 60 native frames per atlas page is a page size, not 60fps.',machineCoverage:{decodedFrames:count,metricsRows:count,atlasFrames:pages.reduce((s,p)=>s+p.count,0),atlasPages:sheets.length},thumbnailIdenticalAdjacentCount:duplicates,thumbnailIdenticalCaution:'Exact identity only at the decoded 96x54 RGB analysis representation; not proof of identical full-resolution source frames.',candidateMethod:'96x54 RGB temporal MAD and 8-bin-per-channel histogram change. Candidates also include fast movement, flashes, composite changes; not verified cuts.',cutOrEffectCandidates:reduced,pages,timelineSheets:tl.length,elapsedMs:Date.now()-start};
 await fs.writeFile(path.join(dataDir,item.id+'.json'),JSON.stringify(report,null,2));await fs.writeFile(path.join(dataDir,item.id+'-pts.json'),JSON.stringify(native));console.log(JSON.stringify({id:item.id,nativeFrames:count,pages:sheets.length,candidates:reduced.length,elapsedMs:Date.now()-start,ready:dir}));
}
const targets=manifest.filter(m=>!selectIds.length||selectIds.includes(m.id));let next=0;await Promise.all(Array.from({length:2},async()=>{while(next<targets.length)await analyze(targets[next++])}));
