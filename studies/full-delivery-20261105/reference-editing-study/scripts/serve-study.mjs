import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const HOST='127.0.0.1',PORT=5208;
const IDS=new Set(Array.from({length:10},(_,i)=>`V${String(i+1).padStart(2,'0')}`));
const readJSON=file=>JSON.parse(fs.readFileSync(file,'utf8').replace(/^\uFEFF/,''));
const within=(root,file)=>{const rel=path.relative(root,file);return rel===''||(!rel.startsWith(`..${path.sep}`)&&rel!=='..'&&!path.isAbsolute(rel));};

function parseRange(header,size){
 if(header===undefined)return null;
 const match=/^bytes=(\d*)-(\d*)$/.exec(header);
 if(!match||(!match[1]&&!match[2])||size<=0)return false;
 let start,end;
 if(!match[1]){const suffix=Number(match[2]);if(!Number.isSafeInteger(suffix)||suffix<=0)return false;start=Math.max(0,size-suffix);end=size-1;}
 else {start=Number(match[1]);end=match[2]?Number(match[2]):size-1;if(!Number.isSafeInteger(start)||!Number.isSafeInteger(end)||start>=size||end<start)return false;end=Math.min(end,size-1);}
 return {start,end};
}

function staticPath(urlPath){
 let decoded;try{decoded=decodeURIComponent(urlPath)}catch{return null}
 if(decoded.includes('\0')||decoded.includes('\\'))return null;
 if(decoded==='/')decoded='/index.html';
 const parts=decoded.split('/').filter(Boolean);
 if(parts.some(part=>part==='..'||part.startsWith('.')||part.toLowerCase()==='local-config.json')||parts[0]==='scripts')return null;
 const file=path.resolve(ROOT,`.${decoded}`);
 return within(ROOT,file)?file:null;
}

if(process.argv.includes('--self-test')){
 assert.deepEqual(parseRange('bytes=0-9',100),{start:0,end:9});
 assert.deepEqual(parseRange('bytes=90-',100),{start:90,end:99});
 assert.deepEqual(parseRange('bytes=-10',100),{start:90,end:99});
 assert.deepEqual(parseRange('bytes=0-999',100),{start:0,end:99});
 assert.deepEqual(parseRange('bytes=-999',100),{start:0,end:99});
 for(const range of ['bytes=100-','bytes=7-3','bytes=-0','bytes=-','bytes=1-2,4-5','bytes=NaN-'])assert.equal(parseRange(range,100),false);
 for(const url of ['/../secret','/%2e%2e/secret','/local-config.json','/LOCAL-CONFIG.JSON','/data/../local-config.json','/scripts/serve-study.mjs','/%00'])assert.equal(staticPath(url),null);
 assert.ok(staticPath('/data/manifest.json'));assert.ok(staticPath('/evidence/V01/overview.jpg'));
 console.log('Self-check passed: byte ranges, traversal rejection, private config and script protection. No HTTP server started.');
 process.exit(0);
}

const configFile=path.join(ROOT,'local-config.json');
const manifestFile=path.resolve(ROOT,'../../work/reference-reverse/manifest.local.json');
let source,sourceBase;
try{
 if(fs.existsSync(configFile)){source=readJSON(configFile);sourceBase=ROOT;}
 else {source=readJSON(manifestFile);sourceBase=path.dirname(manifestFile);}
}catch{
 console.error('无法读取本地视频白名单。请保留工作区内的 manifest.local.json，或在学习页目录创建不公开的 local-config.json（{"media":{"V01":"视频绝对路径"}}）。');
 process.exit(1);
}
const entries=Array.isArray(source)?source:Array.isArray(source.videos)?source.videos:Object.entries(source.media??source).map(([id,value])=>({id,path:typeof value==='string'?value:value?.path}));
const media=new Map();
for(const entry of entries){
 if(!IDS.has(entry.id)||typeof entry.path!=='string')continue;
 const resolved=path.resolve(sourceBase,entry.path);
 if(path.extname(resolved).toLowerCase()!=='.mp4')continue;
 try{const real=fs.realpathSync(resolved),stat=fs.statSync(real);if(stat.isFile())media.set(entry.id,{path:real,size:stat.size,modified:stat.mtime.toUTCString()});}catch{}
}
if(media.size===0){console.error('白名单中的视频均不可读取。请检查本地路径；未启动服务。');process.exit(1);}
const rootReal=fs.realpathSync(ROOT);
const MIME={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.webp':'image/webp','.svg':'image/svg+xml','.md':'text/plain; charset=utf-8','.pdf':'application/pdf','.ico':'image/x-icon'};
function respond(res,status,message,headers={}){res.writeHead(status,{'Content-Type':'text/plain; charset=utf-8',...headers});res.end(message);}
function json(res,status,value){res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'});res.end(JSON.stringify(value));}
function streamFile(req,res,file,start,end){const stream=fs.createReadStream(file,{start,end});req.on('aborted',()=>stream.destroy());res.on('close',()=>stream.destroy());stream.on('error',()=>{if(!res.headersSent)respond(res,500,'文件读取失败');else res.destroy();});stream.pipe(res);}

const server=http.createServer((req,res)=>{
 res.setHeader('X-Content-Type-Options','nosniff');
 res.setHeader('Referrer-Policy','no-referrer');
 res.setHeader('Cross-Origin-Resource-Policy','same-origin');
 res.setHeader('Content-Security-Policy',"default-src 'self'; img-src 'self' data:; media-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'");
 if(!['127.0.0.1:5208','localhost:5208'].includes(req.headers.host)){respond(res,403,'仅允许本机学习页访问');return;}
 if(!['GET','HEAD'].includes(req.method)){respond(res,405,'仅支持读取',{'Allow':'GET, HEAD'});return;}
 let pathname;try{pathname=new URL(req.url,`http://${HOST}:${PORT}`).pathname}catch{respond(res,400,'地址格式不正确');return;}
 if(pathname==='/health'){json(res,200,{app:'reference-editing-study',media_count:media.size,available_ids:[...media.keys()]});return;}
 const mediaMatch=/^\/media\/(V\d{2})$/.exec(pathname);
 if(mediaMatch){
  const item=media.get(mediaMatch[1]);if(!item){respond(res,404,'此视频不在本地白名单，或源文件不可读取');return;}
  const range=parseRange(req.headers.range,item.size);
  if(range===false){respond(res,416,'请求的字节范围无效',{'Content-Range':`bytes */${item.size}`});return;}
  const start=range?.start??0,end=range?.end??item.size-1;
  res.writeHead(range?206:200,{'Content-Type':'video/mp4','Content-Length':end-start+1,'Accept-Ranges':'bytes','Last-Modified':item.modified,'Cache-Control':'private, no-store',...(range?{'Content-Range':`bytes ${start}-${end}/${item.size}`}:{})});
  if(req.method==='HEAD'){res.end();return;}streamFile(req,res,item.path,start,end);return;
 }
 const evidenceMatch=/^\/api\/evidence\/(V\d{2})$/.exec(pathname);
 if(evidenceMatch&&IDS.has(evidenceMatch[1])){
  const id=evidenceMatch[1],dir=path.join(ROOT,'evidence',id);let files=[];
  try{if(within(rootReal,fs.realpathSync(dir)))files=fs.readdirSync(dir,{withFileTypes:true}).filter(f=>f.isFile()&&/\.(jpg|jpeg|png|webp)$/i.test(f.name)).map(f=>`evidence/${id}/${f.name}`).sort((a,b)=>a.localeCompare(b,undefined,{numeric:true}));}catch{}
  json(res,200,{id,files});return;
 }
 const file=staticPath(pathname);if(!file){respond(res,403,'此路径不可访问');return;}
 const type=MIME[path.extname(file).toLowerCase()];if(!type){respond(res,404,'未找到静态资源');return;}
 try{
  const real=fs.realpathSync(file),stat=fs.statSync(real);
  if(!within(rootReal,real)||!stat.isFile()){respond(res,403,'此路径不可访问');return;}
  res.writeHead(200,{'Content-Type':type,'Content-Length':stat.size,'Cache-Control':'no-store'});
  if(req.method==='HEAD'){res.end();return;}streamFile(req,res,real,0,stat.size-1);
 }catch{respond(res,404,'此资源尚未生成，稍后刷新即可');}
});
server.on('error',error=>{console.error(error.code==='EADDRINUSE'?'5208端口已被占用。请关闭占用它的本地服务后重试。':`服务启动失败：${error.message}`);process.exitCode=1;});
server.listen(PORT,HOST,()=>console.log(`本地学习页：http://${HOST}:${PORT} · ${media.size}/10条视频可用 · 不复制、不上传视频。按Ctrl+C关闭。`));
