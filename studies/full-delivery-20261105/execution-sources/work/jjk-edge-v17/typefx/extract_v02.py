from pathlib import Path
import subprocess,json,io
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'outputs/jjk-edge-v17/evidence/v02-type'; OUT.mkdir(parents=True,exist_ok=True)
src=json.loads((ROOT/'outputs/reference-library-20261105/local-media-paths.json').read_text(encoding='utf-8'))['V02']
frames=[0,2,3,26,35,53,106,109,113,120,124,137,152,165,167,174,190,193,201,207,208]
expr='+'.join('eq(n\\,%d)'%n for n in frames)
r=subprocess.run(['C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe','-v','error','-i',src,'-vf',f'select={expr}','-fps_mode','vfr','-f','image2pipe','-vcodec','mjpeg','pipe:1'],capture_output=True)
if r.returncode: raise RuntimeError(r.stderr.decode(errors='replace'))
raw=r.stdout; ims=[]
while raw:
 a=raw.find(b'\xff\xd8');b=raw.find(b'\xff\xd9',a)
 if a<0 or b<0:break
 ims.append(Image.open(io.BytesIO(raw[a:b+2])).convert('RGB'));raw=raw[b+2:]
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',22)
canvas=Image.new('RGB',(1920,((len(frames)+2)//3)*390),(18,18,18));d=ImageDraw.Draw(canvas)
for k,(f,im) in enumerate(zip(frames,ims)):
 im.save(OUT/f'V02-F{f:03}.jpg',quality=95)
 x=k%3*640;y=k//3*390;canvas.paste(im.resize((640,360)),(x,y));d.text((x+10,y+360),f'F{f}  {f/30:.6f}s',font=font,fill='white')
canvas.save(OUT/'V02-type-keyframes.jpg',quality=92)
print(OUT, len(ims))
