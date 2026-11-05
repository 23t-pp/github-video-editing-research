from pathlib import Path
import subprocess,json,io,concurrent.futures
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('D:/gpt/2026-11-04/ps-c-windows-system32-winget-install-2')
OUT=ROOT/'outputs/jjk-edge-v17/evidence/scout'; OUT.mkdir(parents=True,exist_ok=True)
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
FP='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
def probe(p):
 return json.loads(subprocess.check_output([FP,'-v','error','-show_streams','-show_format','-of','json',str(p)]))
def frame(p,t,w=384):
 r=subprocess.run([FF,'-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-vf',f'scale={w}:-1','-f','image2pipe','-vcodec','mjpeg','pipe:1'],capture_output=True)
 if r.returncode or not r.stdout: raise RuntimeError(r.stderr.decode(errors='replace'))
 return Image.open(io.BytesIO(r.stdout)).convert('RGB')
def sheet(p,times,label):
 def get(t):
  try:return t,frame(p,t)
  except:return t,Image.new('RGB',(384,216))
 ims=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(get,times))
 h=242; canvas=Image.new('RGB',(384*4,h*((len(ims)+3)//4)),(15,15,15));d=ImageDraw.Draw(canvas)
 for k,(t,im) in enumerate(ims):
  x=k%4*384;y=k//4*h;canvas.paste(im,(x,y)); d.text((x+4,y+217),f'{label}  {t:.3f}s',font=font,fill='white')
 target=OUT/f'{label}.jpg';canvas.save(target,quality=87)
 return str(target)
if __name__=='__main__':
 base=Path('D:/咒术回战/1080P 内嵌简中字幕')
 ps=[(f'e{i:02}',base/f'{i:02}.mp4') for i in [1,2,4,5,7,9]]+[('movie',Path('D:/咒术回战/4K 内嵌简中字幕.mp4')),('4k-e01',Path('D:/咒术回战/4K 内嵌简中字幕/01.mp4'))]
 info=[]
 for label,p in ps:
  pr=probe(p);v=next(s for s in pr['streams'] if s['codec_type']=='video');dur=float(pr['format']['duration'])
  print(label, dur,v['width'],v['height'],v.get('r_frame_rate'),flush=True)
  info.append({'id':label,'path':str(p),'duration':dur,'video':v})
  ts=[180,360,540,720,900,1080,1200,1320] if dur<2000 else [600,1200,1800,2400,3000,3600,4200,4800]
  print(sheet(p,ts,label),flush=True)
 (OUT/'source-probes.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
