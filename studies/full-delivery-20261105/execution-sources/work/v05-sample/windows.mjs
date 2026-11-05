import fs from 'node:fs';import {spawnSync} from 'node:child_process';
for(const start of [7048,7067]){
 const vf="fps=4,zscale=w=384:h=160:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,drawtext=fontfile='C\\:/Windows/Fonts/consola.ttf':text='%{pts\\:hms}':fontsize=17:fontcolor=white:box=1:boxcolor=black@0.8:x=4:y=4,tile=5x4:padding=2:margin=2";
 const r=spawnSync('C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe',['-v','error','-threads','2','-ss',String(start),'-i','D:/速度与激情/11 速度与激情10（2023）4K.mp4','-an','-t','5','-vf',vf,'-frames:v','1','-q:v','3','-f','image2pipe','pipe:1'],{windowsHide:true,maxBuffer:10*1024*1024});if(r.status!==0)throw Error(r.stderr.toString());fs.writeFileSync(`${import.meta.dirname}/window-${start}.jpg`,r.stdout);console.log(start);
}
