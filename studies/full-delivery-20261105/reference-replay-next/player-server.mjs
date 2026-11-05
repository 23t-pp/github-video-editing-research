import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const root=import.meta.dirname,port=Number(process.env.V07_PLAYER_PORT||5216);
let reference=null;
try{const local=path.join(root,'reference-source.local.json');reference=fs.existsSync(local)?JSON.parse(fs.readFileSync(local,'utf8')).path:JSON.parse(fs.readFileSync(path.join(root,'../reference-library-20261105/local-media-paths.json'),'utf8')).V07;}catch{}
const types={'.html':'text/html; charset=utf-8','.mp4':'video/mp4','.m4a':'audio/mp4','.wav':'audio/wav','.png':'image/png','.jpg':'image/jpeg','.json':'application/json; charset=utf-8','.md':'text/plain; charset=utf-8','.csv':'text/csv; charset=utf-8','.zip':'application/zip'};
http.createServer((req,res)=>{
  try{
    const url=new URL(req.url,'http://127.0.0.1');const name=decodeURIComponent(url.pathname);
    let file=name==='/reference.mp4'?reference:path.resolve(root,'.'+(name==='/'?'/观看与对照.html':name));
    if(name!=='/reference.mp4'){const rel=path.relative(root,file);if(rel.startsWith('..')||path.isAbsolute(rel)){res.writeHead(403);res.end();return;}}
    if(!file||!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404);res.end('File not found');return;}
    const size=fs.statSync(file).size;let start=0,end=size-1,status=200;const range=req.headers.range;
    if(range){const m=/^bytes=(\d+)-(\d*)$/.exec(range);if(!m){res.writeHead(416);res.end();return;}start=Number(m[1]);end=m[2]?Math.min(Number(m[2]),size-1):size-1;if(start>end||start>=size){res.writeHead(416,{'Content-Range':`bytes */${size}`});res.end();return;}status=206;}
    const headers={'Content-Type':types[path.extname(file).toLowerCase()]||'application/octet-stream','Accept-Ranges':'bytes','Content-Length':end-start+1,'Cache-Control':'no-cache'};
    if(status===206)headers['Content-Range']=`bytes ${start}-${end}/${size}`;
    res.writeHead(status,headers);if(req.method==='HEAD'){res.end();return;}const stream=fs.createReadStream(file,{start,end});stream.on('error',()=>res.destroy());req.on('close',()=>stream.destroy());stream.pipe(res);
  }catch{res.writeHead(500);res.end('Local player error');}
}).listen(port,'127.0.0.1',()=>console.log(`V07 player: http://127.0.0.1:${port}`));
