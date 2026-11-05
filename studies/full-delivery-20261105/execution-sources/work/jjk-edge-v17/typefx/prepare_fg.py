from pathlib import Path
import subprocess,sys,json,io
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'outputs/jjk-edge-v17/hyperframes/assets/shots';OUT.mkdir(parents=True,exist_ok=True)
EV=ROOT/'outputs/jjk-edge-v17/evidence/alpha';EV.mkdir(parents=True,exist_ok=True)
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',20)
for name,ep,t,count in [('X-awaken','04',989.,72),('X-palm','02',1259.5,60)]:
 src=Path('D:/咒术回战/4K 内嵌简中字幕')/(ep+'.mp4')
 cmd=[FF,'-v','error','-ss',str(t-.5),'-i',str(src),'-vf','fps=24,crop=iw:ih*0.8:0:ih*0.045,scale=1920:864,pad=1920:1080:0:108,setpts=PTS-STARTPTS','-frames:v',str(count),'-an','-c:v','libx264','-preset','fast','-crf','18','-bf','0','-pix_fmt','yuv420p','-movflags','frag_keyframe+empty_moov','-f','mp4','pipe:1']
 r=subprocess.run(cmd,capture_output=True)
 if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace'))
 target=OUT/(name+'.mp4');target.write_bytes(r.stdout)
 samples=sorted(set([0,12,24,36,48,count-1]))
 cells=[]
 for f in samples:
  r=subprocess.run([FF,'-v','error','-i',str(target),'-vf',f'select=eq(n\\,{f}),scale=640:360','-frames:v','1','-f','image2pipe','-vcodec','mjpeg','pipe:1'],capture_output=True)
  im=Image.open(io.BytesIO(r.stdout)).convert('RGB');cell=Image.new('RGB',(640,390));cell.paste(im);ImageDraw.Draw(cell).text((10,361),f'{name} fileF{f} source {t+(f-12)/24:.4f}',font=font,fill='white');cells.append(cell)
 canvas=Image.new('RGB',(1280,390*((len(cells)+1)//2)))
 for i,cell in enumerate(cells):canvas.paste(cell,(i%2*640,i//2*390))
 canvas.save(EV/(name+'-source.jpg'),quality=94)
 print(name, len(r.stdout), target,flush=True)
