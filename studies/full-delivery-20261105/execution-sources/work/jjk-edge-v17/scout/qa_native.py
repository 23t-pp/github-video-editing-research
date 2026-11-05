from scout import *
import numpy as np,hashlib
PLAN=ROOT/'outputs/jjk-edge-v17/hyperframes/edit.json'; plan=json.loads(PLAN.read_text(encoding='utf-8'))
QA=ROOT/'outputs/jjk-edge-v17/evidence/原生选镜验收';QA.mkdir(exist_ok=True,parents=True)
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
shots=plan['shots'];groups={}
for s in shots:
 fs=[s['assetStartFrame'],s['assetStartFrame']+(s['frames']-1)//2,s['assetStartFrame']+s['frames']-1]
 s['_sampleFrames']=fs
 groups.setdefault(s['asset'],set()).update(fs)
def get(job):
 name,fs=job;fs=sorted(fs);p=PLAN.parent/name
 select='+'.join(f'eq(n,{f})' for f in fs)
 r=subprocess.run([FF,'-v','error','-threads','1','-filter_threads','1','-i',str(p),'-vf',f"select='{select}',scale=480:270",'-fps_mode','passthrough','-frames:v',str(len(fs)),'-threads','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],capture_output=True)
 if r.returncode:raise RuntimeError(name+' '+r.stderr.decode(errors='replace'))
 n=len(r.stdout)//(480*270*3)
 if n!=len(fs):raise RuntimeError(f'{name}: {n} != {len(fs)}')
 arr=np.frombuffer(r.stdout,np.uint8).reshape(n,270,480,3)
 return name,{f:Image.fromarray(a) for f,a in zip(fs,arr)}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:images=dict(pool.map(get,groups.items()))
stats=[]
for pg in range((len(shots)+7)//8):
 chunk=shots[pg*8:(pg+1)*8];can=Image.new('RGB',(1440,len(chunk)*300),(18,18,18));d=ImageDraw.Draw(can)
 for row,s in enumerate(chunk):
  st={'id':s['id'],'assetId':s['assetId'],'timelineStart':s['startFrame'],'timelineEndExclusive':s['startFrame']+s['frames'],'samples':[]}
  for col,f in enumerate(s['_sampleFrames']):
   im=images[s['asset']][f];can.paste(im,(col*480,row*300));im.save(QA/f"{s['id']}-a{f:03}.jpg",quality=90)
   a=np.array(im)[27:243]; st['samples'].append({'assetFrame':f,'meanRGB':float(a.mean()),'fractionBelow8':float((a.max(2)<8).mean())})
  d.text((5,row*300+273),f"{s['id']} {s['assetId']} T={s['startFrame']/24:.3f}-{(s['startFrame']+s['frames'])/24:.3f} assetF={s['_sampleFrames']}",font=font,fill='white')
  stats.append(st)
 can.save(QA/f'原生选镜-{pg+1:02}.jpg',quality=91)
(QA/'sample-index.json').write_text(json.dumps({'editSha256':hashlib.sha256(PLAN.read_bytes()).hexdigest(),'scope':'exact asset file frames; first/middle/final for each of67 native shots; no compositing/punch/rotation applied; no audio review','shots':stats},ensure_ascii=False,indent=2),encoding='utf-8')
print('QA sheets ready',len(shots),len(groups),flush=True)
