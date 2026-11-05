// Node writes encoded outputs; Python only reads footage and emits PNG bytes.
import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{spawn}from'node:child_process';
const tools=import.meta.dirname,project=path.resolve(tools,'..');const specPath=path.resolve(process.argv[2]);assert(specPath);const spec=JSON.parse(fs.readFileSync(specPath,'utf8').replace(/^\uFEFF/,''));
assert(/^[A-Za-z0-9_-]+$/.test(spec.id));assert(path.resolve(spec.source).startsWith(path.join(project,'assets','shots')+path.sep),'Source restricted to new replay project');
const target=path.join(project,'assets','alpha',spec.id);fs.mkdirSync(target,{recursive:true});fs.copyFileSync(specPath,path.join(target,'roto-keyframes.json'));
const py='C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const child=spawn(py,[path.join(tools,'dynamic-alpha.py'),specPath],{windowsHide:true,stdio:['ignore','pipe','pipe']});let pending='',stderr='',frames=0;
child.stdout.setEncoding('utf8');child.stdout.on('data',s=>{pending+=s;for(;;){const n=pending.indexOf('\n');if(n<0)break;const line=pending.slice(0,n);pending=pending.slice(n+1);if(!line.trim())continue;const r=JSON.parse(line);assert(path.basename(r.name)===r.name);if(r.kind==='report')fs.writeFileSync(path.join(target,r.name),JSON.stringify(r.value,null,2));else {fs.writeFileSync(path.join(target,r.name),Buffer.from(r.base64,'base64'));if(r.kind==='png')frames++;}}});
child.stderr.setEncoding('utf8');child.stderr.on('data',s=>stderr+=s);
const code=await new Promise((resolve,reject)=>{child.once('error',reject);child.once('exit',resolve);});fs.writeFileSync(path.join(target,'runtime-stderr.txt'),stderr);assert.equal(code,0,stderr);assert.equal(frames,spec.frames);console.log(JSON.stringify({id:spec.id,target,frames,fps:25,rgbaSize:'1920x1080',sourceStartFrame:spec.assetStartFrame,evidence:path.join(target,'alpha-evidence.png')}));
