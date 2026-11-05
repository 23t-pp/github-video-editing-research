import http from 'node:http';import fs from 'node:fs';import path from 'node:path';import{spawn}from'node:child_process';
const root=path.resolve(import.meta.dirname,'..'),port=Number(process.env.PORT||5212),host='127.0.0.1';
const realRoot=fs.realpathSync(root),media=new Map(),config=path.join(root,'local-media-paths.json');
const within=(a,b)=>{const r=path.relative(a,b);return !r||(!r.startsWith('..'+path.sep)&&r!=='..'&&!path.isAbsolute(r));};
if(fs.existsSync(config))for(const [id,p]of Object.entries(JSON.parse(fs.readFileSync(config,'utf8').replace(/^\uFEFF/,'')))){
 if(!/^V\d{2}$/.test(id)||typeof p!=='string')continue;try{const real=fs.realpathSync(p);if(fs.statSync(real).isFile()&&/\.mp4$/i.test(real))media.set(id,real);}catch{}
}
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.jpg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml','.mp4':'video/mp4','.m4a':'audio/mp4','.mp3':'audio/mpeg','.wav':'audio/wav','.mid':'audio/midi','.md':'text/plain; charset=utf-8','.csv':'text/csv; charset=utf-8','.zip':'application/zip'};
function end(res,status,body){res.writeHead(status,{'Content-Type':'text/plain; charset=utf-8'});res.end(body);}
function file(req,res,p){let stat;try{stat=fs.statSync(p);if(!stat.isFile())return end(res,404,'文件不存在');}catch{return end(res,404,'文件不存在');}
 let a=0,b=stat.size-1,status=200;const range=req.headers.range;
 if(range){const m=/^bytes=(\d*)-(\d*)$/.exec(range);if(!m||(!m[1]&&!m[2]))return end(res,416,'Range错误');if(!m[1]){const n=Number(m[2]);if(!Number.isSafeInteger(n)||n<=0)return end(res,416,'Range错误');a=Math.max(0,stat.size-n);}else{a=Number(m[1]);b=m[2]?Number(m[2]):b;}
 if(!Number.isSafeInteger(a)||!Number.isSafeInteger(b)||a>=stat.size||a<0||b<a)return end(res,416,'Range越界');b=Math.min(b,stat.size-1);status=206;}
 res.writeHead(status,{'Content-Type':mime[path.extname(p).toLowerCase()]||'application/octet-stream','Content-Length':b-a+1,'Accept-Ranges':'bytes','Cache-Control':'no-store',...(status===206?{'Content-Range':`bytes ${a}-${b}/${stat.size}`}:{})});if(req.method==='HEAD')return res.end();const s=fs.createReadStream(p,{start:a,end:b});res.on('close',()=>s.destroy());s.on('error',()=>res.destroy());s.pipe(res);
}
const frames=JSON.parse(fs.readFileSync(path.join(root,'data/media-index.json'),'utf8'));
const server=http.createServer((req,res)=>{
 res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Referrer-Policy','no-referrer');
 if(![`${host}:${port}`,`localhost:${port}`].includes(req.headers.host))return end(res,403,'仅本机访问');
 if(!['GET','HEAD'].includes(req.method))return end(res,405,'仅支持读取');
 let u;try{u=decodeURIComponent(new URL(req.url,`http://${host}:${port}`).pathname);}catch{return end(res,400,'URL错误');}
 if(u==='/health'){res.writeHead(200,{'Content-Type':'application/json'});return res.end(JSON.stringify({app:'native-frame-study',availableIds:[...media.keys()]}));}
 let m=/^\/media\/(V\d{2})$/.exec(u);if(m)return media.has(m[1])?file(req,res,media.get(m[1])):end(res,404,'原视频只保留在你的电脑；请配置local-media-paths.json');
 m=/^\/frame\/(V\d{2})\/(\d+)\.jpg$/.exec(u);
 if(m){const id=m[1],n=Number(m[2]),item=frames.find(v=>v.id===id);if(!media.has(id)||!item||n>=Number(item.frameCount))return end(res,404,'原帧不可用');
  const ff=process.env.FFMPEG_PATH||'C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';const child=spawn(ff,['-v','error','-nostdin','-threads','2','-i',media.get(id),'-an','-vf',`select=eq(n\\,${n})`,'-frames:v','1','-fps_mode','passthrough','-q:v','2','-f','image2pipe','pipe:1'],{windowsHide:true});
  const chunks=[];child.stdout.on('data',b=>chunks.push(b));child.stderr.resume();child.on('error',()=>{if(!res.writableEnded)end(res,500,'FFmpeg不可用');});res.on('close',()=>{if(child.exitCode===null)child.kill();});
  child.on('close',c=>{if(res.writableEnded||res.destroyed)return;if(c!==0)return end(res,500,'解码失败');const b=Buffer.concat(chunks);res.writeHead(200,{'Content-Type':'image/jpeg','Content-Length':b.length,'Cache-Control':'private, max-age=3600'});res.end(b);});return;
 }
 if(u==='/')u='/index.html';const parts=u.split('/');if(u.includes('\0')||u.includes('\\')||parts.some(p=>p==='..'||p.startsWith('.'))||parts.some(p=>/^(local-media-paths|manifest\.local)\.json$/i.test(p)))return end(res,403,'私有路径不可访问');
 const p=path.resolve(root,'.'+u);try{if(!within(realRoot,fs.realpathSync(p)))return end(res,403,'越界');}catch{return end(res,404,'文件不存在');}return file(req,res,p);
});
server.listen(port,host,()=>console.log(`学习页 http://${host}:${port}；已绑定${media.size}条本地原视频。Ctrl+C停止。`));
server.on('error',e=>{console.error(e.message);process.exitCode=1;});
