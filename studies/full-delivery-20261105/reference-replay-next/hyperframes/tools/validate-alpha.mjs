import fs from'node:fs';import path from'node:path';import crypto from'node:crypto';import assert from'node:assert/strict';import{spawnSync}from'node:child_process';
const tools=import.meta.dirname,project=path.resolve(tools,'..'),root=path.resolve(project,'../../..'),target=path.join(project,'assets/alpha'),ids=['B04-gear-hand','B03-switch-hand','B01-steering-hand'];
const code=`import sys,json,pathlib
sys.path.insert(0,sys.argv[1]);import cv2,numpy as np
root=pathlib.Path(sys.argv[2]);ids=json.loads(sys.argv[3]);checks=[]
for id in ids:
 d=root/id;s=json.load(open(d/'roto-keyframes.json',encoding='utf-8-sig'));r=json.load(open(d/'alpha-report.json'));c=cv2.VideoCapture(s['source']);start=s['assetStartFrame'];count=s['frames'];rows=[]
 for g in range(start+count):
  ok,bgr=c.read();assert ok
  if g<start:continue
  f=g-start;p=cv2.imread(str(d/f'{f:06d}.png'),cv2.IMREAD_UNCHANGED);assert p.shape==(1080,1920,4)
  assert np.array_equal(p[:,:,:3],bgr),(id,f,'RGB differs from actual exact source frame')
  assert not p[:140,:,3].any() and not p[940:,:,3].any()
  if f in s.get('emptyFrames',[]):assert not p[:,:,3].any()
  rows.append({'localFrame':f,'assetFrame':g,'rgba':True,'rgbExactlyEqualsSource':True,'nonzeroAlphaPixels':int((p[:,:,3]>0).sum())})
 c.release();checks.append({'id':id,'frames':count,'assetStartFrame':start,'allRgbSourceFramesExact':True,'letterboxAlphaZero':True,'emptyFrames':s.get('emptyFrames',[]),'checks':rows})
print(json.dumps(checks))
`;
const py='C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const r=spawnSync(py,['-c',code,path.join(root,'work/reference-replay-v07/python-deps'),target,JSON.stringify(ids)],{encoding:'utf8',windowsHide:true,maxBuffer:4*1024*1024});assert.equal(r.status,0,r.stderr);const checks=JSON.parse(r.stdout);
const manifest=checks.map(c=>{const report=JSON.parse(fs.readFileSync(path.join(target,c.id,'alpha-report.json'),'utf8'));const filename=report.sourceFilename;const file=path.join(project,'assets/shots',filename);return{id:c.id,directory:`assets/alpha/${c.id}`,pattern:'%06d.png',width:1920,height:1080,fps:25,frames:c.frames,sourceAsset:filename,assetStartFrame:c.assetStartFrame,sourceAssetFrameInclusive:[c.assetStartFrame,c.assetStartFrame+c.frames-1],emptyLocalFrames:c.emptyFrames,sourceSha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),rgbExactlyEqualsSource:true,freezeLastFrameAllowed:false,evidence:`assets/alpha/${c.id}/alpha-evidence.png`,editableRoto:`assets/alpha/${c.id}/roto-keyframes.json`};});
fs.writeFileSync(path.join(target,'alpha-manifest.json'),JSON.stringify({fps:25,method:'Manual contour keyframes + local LK/GrabCut only; no AI content generation',clips:manifest},null,2));fs.writeFileSync(path.join(target,'validation.json'),JSON.stringify({verifiedAt:new Date().toISOString(),allSourceRgbFramesExactlyMatch:true,noBlackLetterboxInAlpha:true,checks},null,2));console.log(JSON.stringify({clips:manifest,allSourceRgbFramesExactlyMatch:true}));
