import fs from 'node:fs';import path from 'node:path';import {spawnSync}from'node:child_process';import {createRequire}from'node:module';
const out=import.meta.dirname,ff='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe',py='C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const run=(exe,args)=>{const r=spawnSync(exe,args,{encoding:'utf8',windowsHide:true,maxBuffer:8*1024*1024});return{executable:exe,args,status:r.status,stdout:r.stdout,stderr:r.stderr};};
const python=run(py,['-c',`import sys,importlib.util,json,numpy,PIL
names=['cv2','numpy','scipy','PIL','torch','torchvision','onnxruntime','rembg','mediapipe','ultralytics','segment_anything','sam2','moviepy','imageio','skimage']
print(json.dumps({'executable':sys.executable,'version':sys.version,'numpy':numpy.__version__,'Pillow':PIL.__version__,'modules':{x:bool(importlib.util.find_spec(x)) for x in names}},indent=2))`]);
const filters=run(ff,['-hide_banner','-filters']);fs.writeFileSync(path.join(out,'ffmpeg-filters.txt'),filters.stdout+filters.stderr);
const wanted=['maskedmerge','maskedthreshold','maskfun','alphaextract','alphamerge','geq','gblur','dilation','erosion','threshold','lut','zoompan','perspective','displace','remap','minterpolate','vidstabdetect','vidstabtransform','chromakey','colorkey','xfade'];
const lines=(filters.stdout+filters.stderr).split(/\r?\n/),present=Object.fromEntries(wanted.map(n=>[n,lines.some(l=>new RegExp('\\s'+n+'\\s').test(l))]));
const geqSmoke=run(ff,['-hide_banner','-loglevel','error','-f','lavfi','-i','color=s=64x64:r=25:d=0.12','-vf',"format=gray,geq=lum='if(lt(X,32),255,0)'",'-f','null','-']);
const maskSmoke=run(ff,['-hide_banner','-loglevel','error','-f','lavfi','-i','color=red:s=64x64:r=25:d=0.12','-f','lavfi','-i','color=blue:s=64x64:r=25:d=0.12','-f','lavfi','-i','color=white:s=64x64:r=25:d=0.12','-filter_complex','[0:v][1:v][2:v]maskedmerge','-f','null','-']);
const model='C:/Users/PC/.cache/hyperframes/background-removal/models/u2net_human_seg.onnx';
const packages={};for(const location of ['C:/Users/PC/Apps/hyperframes/package.json','C:/Users/PC/Desktop/OpenChatCut-main/package.json']){const req=createRequire(location);packages[location]={};for(const name of ['onnxruntime-node','@techstark/opencv-js','opencv4nodejs','sharp','@remotion/media'])try{packages[location][name]=req.resolve(name);}catch{packages[location][name]=null;}}
const report={checkedAt:new Date().toISOString(),scope:'Read-only tool/dependency audit plus synthetic FFmpeg null-output smoke tests; no installation/model download/user media processing',python,ffmpeg:{version:run(ff,['-version']).stdout.split('\n')[0],filterListExit:filters.status,present,geqSmoke,maskSmoke},hyperframes:{defaultRemovalModel:'u2net_human_seg',modelPath:model,modelCached:fs.existsSync(model),nodePackages:packages},portableNode:process.execPath};
fs.writeFileSync(path.join(out,'tool-probe.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
