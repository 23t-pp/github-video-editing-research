from scout import *
import numpy as np,hashlib
PLAN=ROOT/'outputs/jjk-edge-v17/hyperframes/edit.json'; p=json.loads(PLAN.read_text(encoding='utf-8'))
QA=ROOT/'outputs/jjk-edge-v17/evidence/原生选镜验收';old=json.loads((QA/'sample-index.json').read_text(encoding='utf-8'));oldmap={s['id']:s for s in old['shots']}
delta=[];font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
for s in p['shots']:
 prior=oldmap[s['id']];newfs=[s['assetStartFrame'],s['assetStartFrame']+s['frames']-1]
 if prior['assetId']!=s['assetId'] or [prior['samples'][0]['assetFrame'],prior['samples'][-1]['assetFrame']]!=newfs:delta.append(s)
def get(s):
 fs=[s['assetStartFrame'],s['assetStartFrame']+s['frames']-1];select='+'.join(f'eq(n,{f})' for f in fs)
 r=subprocess.run([FF,'-v','error','-threads','1','-filter_threads','1','-i',str(PLAN.parent/s['asset']),'-vf',f"select='{select}',scale=480:270",'-fps_mode','passthrough','-frames:v','2','-threads','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],capture_output=True);r.check_returncode()
 arr=np.frombuffer(r.stdout,np.uint8).reshape(2,270,480,3);ims=[Image.fromarray(a) for a in arr]
 for f,im in zip(fs,ims):im.save(QA/f"修订-{s['id']}-a{f:03}.jpg",quality=93)
 return s,ims
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(get,delta))
for pg in range((len(results)+7)//8):
 chunk=results[pg*8:(pg+1)*8];can=Image.new('RGB',(1440,len(chunk)*300),(18,18,18));d=ImageDraw.Draw(can)
 for row,(s,ims) in enumerate(chunk):
  prior=oldmap[s['id']];of=prior['samples'][-1]['assetFrame'];oldim=Image.open(QA/f"{s['id']}-a{of:03}.jpg")
  can.paste(oldim,(0,row*300));can.paste(ims[0],(480,row*300));can.paste(ims[1],(960,row*300))
  d.text((4,row*300+273),f"{s['id']} {prior['assetId']} old-tailF{of} | {s['assetId']} NEW firstF{s['assetStartFrame']} tailF{s['assetStartFrame']+s['frames']-1}",font=font,fill='white')
 can.save(QA/f'修订边界-{pg+1:02}.jpg',quality=92)
(QA/'delta-index.json').write_text(json.dumps({'editSha256':hashlib.sha256(PLAN.read_bytes()).hexdigest(),'changedShots':delta},ensure_ascii=False,indent=2),encoding='utf-8')
print('delta',len(delta),[s['id'] for s in delta])
