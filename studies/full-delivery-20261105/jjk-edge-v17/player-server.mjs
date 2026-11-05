import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const root=import.meta.dirname;
const local=JSON.parse(fs.readFileSync(path.join(root,'../reference-library-20261105/local-media-paths.json'),'utf8'));
const types={'.html':'text/html; charset=utf-8','.md':'text/plain; charset=utf-8','.json':'application/json; charset=utf-8','.mp4':'video/mp4','.wav':'audio/wav','.jpg':'image/jpeg','.png':'image/png','.zip':'application/zip','.ccproj':'application/octet-stream'};
http.createServer((req,res)=>{
  const uri=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  let file=uri==='/V17.mp4'?local.V17:uri==='/V02.mp4'?local.V02:path.resolve(root,'.'+(uri==='/'?'/观看与学习.html':uri));
  if(!['/V17.mp4','/V02.mp4'].includes(uri)&&file!==root&&!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}
  if(!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404);res.end('File not ready');return;}
  const size=fs.statSync(file).size;const mime=types[path.extname(file)]||'application/octet-stream';const range=req.headers.range;
  if(range){const m=/bytes=(\d+)-(\d*)/.exec(range);if(!m){res.writeHead(416);res.end();return;}const start=Number(m[1]),end=m[2]?Math.min(size-1,Number(m[2])):size-1;if(start>=size){res.writeHead(416);res.end();return;}res.writeHead(206,{'Content-Type':mime,'Accept-Ranges':'bytes','Content-Range':`bytes ${start}-${end}/${size}`,'Content-Length':end-start+1});fs.createReadStream(file,{start,end}).pipe(res);}
  else{res.writeHead(200,{'Content-Type':mime,'Accept-Ranges':'bytes','Content-Length':size});fs.createReadStream(file).pipe(res);}
}).listen(5231,'127.0.0.1',()=>console.log('观看与学习：http://127.0.0.1:5231'));
