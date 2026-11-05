from pathlib import Path
import subprocess,json,re,numpy as np,hashlib
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parents[3];R=B/'outputs/jjk-s1-workflow';E=R/'evidence/tail-action-preflight';E.mkdir(exist_ok=True);ff='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15)
spec=[('C090-PUNCH',24,655.25,657.95),('C090-IMPACT',24,652.15,653.1),('C091-NAIL',24,665.0,667.5),('C007-WAVE',4,1087.5,1088.65),('C062-SPAR',20,285.0,285.95),('C090-BLOOD',24,657.95,658.95)]
items=[]
for id,ep,a,b in spec:
 source=f'D:/咒术回战/1080P 内嵌简中字幕/{ep:02}.mp4';p=subprocess.run([ff,'-v','info','-threads','1','-ss',str(a),'-i',source,'-t',str(b-a),'-an','-vf','scale=320:180,showinfo','-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],capture_output=True,check=True);raw=p.stdout;f=np.frombuffer(raw,np.uint8).reshape(-1,180,320,3);pts=[a+float(x) for x in re.findall(r' n:\s*\d+ pts:\s*[-\d]+ pts_time:([-\d.]+)',p.stderr.decode('utf-8',errors='replace'))][:len(f)];assert len(pts)==len(f);sheets=[]
 for page,start in enumerate(range(0,len(f),36)):
  selected=f[start:start+36];s=Image.new('RGB',(1920,((len(selected)+5)//6)*200),'#111')
  for k,arr in enumerate(selected):
   x=k%6*320;y=k//6*200;s.paste(Image.fromarray(arr),(x,y));ImageDraw.Draw(s).text((x+4,y+181),f'{id} F{start+k} {pts[start+k]:.5f}s',font=font,fill='white')
  sp=E/f'{id}-native-{page+1:02}.jpg';s.save(sp,quality=95);sheets.append(sp.relative_to(R).as_posix())
 np.savez_compressed(E/f'{id}-decode.npz',rgb=f,pts=np.array(pts))
 items.append({'searchId':id,'sourceId':f'S1E{ep:02}','sourcePath':source,'requestedSearchSeconds':[a,b],'nativeFps':'24000/1001','decodedNativeFrames':len(f),'sourcePtsSeconds':pts,'sheets':sheets,'humanViewedAllFrames':False})
 print(id,len(f),flush=True)
(R/'data/tail-action-search-preflight.json').write_text(json.dumps({'version':'TAIL-SEARCH-0.1','items':items},ensure_ascii=False,indent=2),encoding='utf-8')
