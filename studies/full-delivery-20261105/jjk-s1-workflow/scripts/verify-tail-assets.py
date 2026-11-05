"""Read actual encoded R4 clips; freeze all-frame geometry and source-clock evidence."""
from pathlib import Path
import json,subprocess,sys,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent.parent;W=R.parents[1]/'work/jjk-s1-workflow/tail-native-final';D=R/'evidence/tail-retrieval';FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
m=json.loads((R/'data/retrieved-assets-loop4.json').read_text(encoding='utf-8'));font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',15);rows=[]
for item in m['items']:
 asset=item['asset'];N=item['outputFrames'];rgb=subprocess.run([FF,'-v','error','-threads','1','-filter_threads','1','-i',str(R/'hyperframes'/asset['asset']),'-an','-vf','scale=in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24','-fps_mode','passthrough','-f','rawvideo','pipe:1'],capture_output=True,check=True).stdout
 assert len(rgb)==N*1920*1080*3
 a=np.frombuffer(rgb,dtype=np.uint8).reshape(N,1080,1920,3);canvas=Image.new('RGB',(1920,((N+3)//4)*294),'#080b13');draw=ImageDraw.Draw(canvas);bottom=Image.new('RGB',(1920,((N+2)//3)*84),'#080b13');bd=ImageDraw.Draw(bottom);diff=[]
 for f in range(N):
  frame=Image.fromarray(a[f]);x=f%4*480;y=f//4*294;canvas.paste(frame.resize((480,270)),(x,y));sample=item['sourceSampleMapping'][f];draw.text((x+5,y+272),f'F{f:02} PTS{sample["sourcePtsSeconds"]:.6f} src{sample["nativeCoreIndex"]:02}',font=font,fill='#72c7ed')
  x=f%3*640;y=f//3*84;bottom.paste(frame.crop((0,900,1920,1080)).resize((640,60)),(x,y));bd.text((x+5,y+63),f'prepared F{f:02} y900..1079',font=font,fill='#72c7ed')
  if f in [0,N//2,N-1]:frame.save(D/f'{asset["id"]}-F{f:02}.png')
  source=Image.open(W/asset['id']/'native'/f'native_{sample["nativeCoreIndex"]:06}.png').convert('RGB');expected=Image.new('RGB',(1920,1080));expected.paste(source.crop(tuple([0,0,1920,item['cropOriginal'][3]])),(0,item['padTop']));mad=float(np.abs(a[f].astype(np.int16)-np.asarray(expected).astype(np.int16)).mean());diff.append(mad)
 assert max(diff)<8,(asset['id'],max(diff))
 full=D/f'{asset["id"]}-all-prepared.jpg';canvas.save(full,quality=94);strip=D/f'{asset["id"]}-all-bottom-strips.jpg';bottom.save(strip,quality=96)
 rows.append({'assetId':asset['id'],'frames':N,'frameCountPass':True,'sourceOrderPixelComparisonMAD':diff,'maxMAD':max(diff),'cropOriginal':item['cropOriginal'],'padTop':item['padTop'],'contactSheet':full.relative_to(R).as_posix(),'bottomStripContact':strip.relative_to(R).as_posix(),'assetSha256':asset['sha256'],'scope':'all actual encoded output frames compared to explicit selected native source pixels; human subtitle/action/cut review separate'})
out=R/'data/tail-prepared-check.json';out.write_text(json.dumps({'items':rows,'count':sum(x['frames'] for x in rows),'machinePass':True,'humanAcceptance':'pending independent all-frame review'},ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'all70FramesDecoded':True,'maxMADs':{r['assetId']:r['maxMAD'] for r in rows},'report':str(out)},ensure_ascii=False))
