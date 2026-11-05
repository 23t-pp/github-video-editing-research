import http from 'node:http';import fs from 'node:fs';import path from 'node:path';
const root=path.resolve(import.meta.dirname,'../../outputs/v05-six-panel');
const types={'.html':'text/html; charset=utf-8','.mp4':'video/mp4','.jpg':'image/jpeg','.png':'image/png','.md':'text/plain; charset=utf-8','.json':'application/json; charset=utf-8','.zip':'application/zip','.ccproj':'application/octet-stream'};
http.createServer((req,res)=>{try{
 if(!['GET','HEAD'].includes(req.method)){res.writeHead(405);return res.end()}
 const p=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);const file=path.resolve(root,'.'+(p==='/'?'/学习播放器.html':p));
 if(!file.startsWith(root+path.sep)){res.writeHead(403);return res.end()}
 const st=fs.statSync(file);if(!st.isFile())throw Error('not-file');
 const headers={'Content-Type':types[path.extname(file)]||'application/octet-stream','Accept-Ranges':'bytes','Cache-Control':'no-cache'};
 let start=0,end=st.size-1,status=200;
 if(req.headers.range){const m=/^bytes=(\d+)-(\d*)$/.exec(req.headers.range);if(!m){res.writeHead(416);return res.end()}start=+m[1];end=m[2]?Math.min(+m[2],end):end;if(start>end){res.writeHead(416);return res.end()}status=206;headers['Content-Range']=`bytes ${start}-${end}/${st.size}`}
 headers['Content-Length']=end-start+1;res.writeHead(status,headers);if(req.method==='HEAD')return res.end();fs.createReadStream(file,{start,end}).pipe(res);
 }catch{res.writeHead(404);res.end('Not found')}}).listen(5211,'127.0.0.1',()=>console.log('V05 learning player: http://127.0.0.1:5211/'));
