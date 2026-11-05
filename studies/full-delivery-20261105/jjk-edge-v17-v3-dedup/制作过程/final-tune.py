from pathlib import Path
import importlib.util,json,subprocess,io
from PIL import Image,ImageDraw
W=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('prep',W/'prepare-new.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows={a['id']:a for a in json.loads((W/'new-assets.json').read_text(encoding='utf8'))}
for id,ep,t,desc in [('N33',2,1144.5,'五条伸手护住少女'),('N37',3,1149.5,'夏油侧脸礼堂回应')]:
 (m.HF/rows[id]['asset']).unlink();data,_=m.task((id,ep,t,desc));rows[id]=data;print('FINAL TUNE',id,flush=True)
(W/'new-assets.json').write_text(json.dumps(list(rows.values()),ensure_ascii=False,indent=2),encoding='utf8')
ids=['N33','N34','N35','N36','N37','N38','N39','N40','N21']
for pg,k in enumerate(range(0,len(ids),5),1):
 batch=ids[k:k+5];can=Image.new('RGB',(1536,len(batch)*242),(12,14,20));d=ImageDraw.Draw(can)
 for y,id in enumerate(batch):
  data=rows[id];file=m.HF/data['asset'];vf="select='eq(n,12)+eq(n,24)+eq(n,35)+eq(n,47)',scale=384:216"
  r=subprocess.run([m.FF,'-v','error','-threads','1','-filter_threads','1','-i',str(file),'-vf',vf,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],capture_output=True,check=True)
  for x in range(4):can.paste(Image.frombytes('RGB',(384,216),r.stdout[x*384*216*3:(x+1)*384*216*3]),(384*x,242*y))
  d.text((5,y*242+219),f'{id} FINAL F12 F24 F35 F47',fill='white')
 can.save(m.EV/f'新前景最终源帧-{pg:02}.jpg',quality=94)
