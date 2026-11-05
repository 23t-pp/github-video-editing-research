import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'../../outputs/fast60');
const types={'.html':'text/html; charset=utf-8','.mp4':'video/mp4','.jpg':'image/jpeg','.md':'text/plain; charset=utf-8','.csv':'text/csv; charset=utf-8','.wav':'audio/wav'};
http.createServer((req,res)=>{
  try {
    if (!['GET','HEAD'].includes(req.method)) {res.writeHead(405);return res.end();}
    const request=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);
    const local=path.resolve(root,'.'+(request==='/'?'/学习播放器.html':request));
    if (!local.startsWith(root+path.sep)) {res.writeHead(403);return res.end();}
    const stat=fs.statSync(local);
    if (!stat.isFile()) throw Error('Missing file');
    const headers={'Content-Type':types[path.extname(local)]||'application/octet-stream','Cache-Control':'no-cache','Accept-Ranges':'bytes'};
    let start=0,end=stat.size-1,status=200;
    if (req.headers.range) {
      const match=/^bytes=(\d+)-(\d*)$/.exec(req.headers.range);
      if (!match || +match[1]>end || (match[2] && +match[2]<+match[1])) {
        res.writeHead(416,{'Content-Range':'bytes */'+stat.size});return res.end();
      }
      start=+match[1];end=match[2]?Math.min(+match[2],end):end;status=206;
      headers['Content-Range']='bytes '+start+'-'+end+'/'+stat.size;
    }
    headers['Content-Length']=end-start+1;res.writeHead(status,headers);
    if (req.method==='HEAD') return res.end();
    fs.createReadStream(local,{start,end}).on('error',()=>res.destroy()).pipe(res);
  } catch {res.writeHead(404);res.end('File unavailable');}
}).listen(5214,'127.0.0.1',()=>console.log('APEX local player http://127.0.0.1:5214/'));
