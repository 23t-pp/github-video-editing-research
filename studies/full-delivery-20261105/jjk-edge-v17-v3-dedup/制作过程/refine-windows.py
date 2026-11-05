from pathlib import Path
import importlib.util,json,subprocess,io
from PIL import Image,ImageDraw
W=Path(__file__).resolve().parent;B=W.parents[1]
spec=importlib.util.spec_from_file_location('prep',W/'prepare-new.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
updates={'N01':(3,738.6),'N21':(5,863.8),'N22':(3,720),'N23':(4,978.6),'N33':(4,862.5),'N34':(3,1183.5),'N37':(5,563.5),'N40':(1,946),'N15':(4,1020)}
rows={a['id']:a for a in json.loads((W/'new-assets.json').read_text(encoding='utf8'))};results=[]
for id,(ep,t) in updates.items():
 old=rows[id];out=m.HF/old['asset'];out.unlink()
 data,ims=m.task((id,ep,t,old['description']));rows[id]=data;results.append((data,ims));print('REFINED',id,t,flush=True)
(W/'new-assets.json').write_text(json.dumps(list(rows.values()),ensure_ascii=False,indent=2),encoding='utf8')
for pg,k in enumerate(range(0,len(results),6),1):
 batch=results[k:k+6];can=Image.new('RGB',(1536,len(batch)*242),(12,14,20));d=ImageDraw.Draw(can)
 for y,(a,ims) in enumerate(batch):
  for x,im in enumerate(ims):can.paste(im,(384*x,242*y))
  d.text((5,y*242+219),f"{a['id']} revised E{Path(a['sourcePath']).stem} {a['sourceIn']}s F12 F24 F47 F59",fill='white')
 can.save(m.EV/f'新素材窗口修订-{pg:02}.jpg',quality=92)
