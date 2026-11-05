import fs from'node:fs';import path from'node:path';import{spawnSync}from'node:child_process';
const out=path.join(import.meta.dirname,'alpha-inspection');fs.mkdirSync(out,{recursive:true});const id=process.argv[2],file=path.resolve(process.argv[3]),numbers=process.argv.slice(4).map(Number);
const py='C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const code=`import sys,json,base64
sys.path.insert(0,sys.argv[1])
import cv2
c=cv2.VideoCapture(sys.argv[2]);want=json.loads(sys.argv[3]);f=0
while f<=max(want):
 ok,im=c.read()
 if not ok:raise RuntimeError(str(f))
 if f in want:
  ok,b=cv2.imencode('.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,96]);print(json.dumps({'frame':f,'b64':base64.b64encode(b).decode()}))
 f+=1
`;
const r=spawnSync(py,['-c',code,path.join(import.meta.dirname,'python-deps'),file,JSON.stringify(numbers)],{windowsHide:true,encoding:'utf8',maxBuffer:100*1024*1024});if(r.status!==0)throw new Error(r.stderr);
for(const line of r.stdout.trim().split('\n')){const row=JSON.parse(line),target=path.join(out,`${id}-F${row.frame}.jpg`);fs.writeFileSync(target,Buffer.from(row.b64,'base64'));console.log(target);}
