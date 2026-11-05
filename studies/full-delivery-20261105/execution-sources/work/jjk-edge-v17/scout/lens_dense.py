from scout import *
import numpy as np
QA=ROOT/'outputs/jjk-edge-v17/evidence/原生选镜验收'
for name,fs,w in [('C07',[14,16,18,20,22],960),('C52',list(range(36,48)),384)]:
 select='+'.join(f'eq(n,{f})' for f in fs);h=w*9//16
 r=subprocess.run([FF,'-v','error','-threads','1','-filter_threads','1','-i',str(ROOT/f'outputs/jjk-edge-v17/hyperframes/assets/shots/{name}.mp4'),'-vf',f"select='{select}',scale={w}:{h}",'-fps_mode','passthrough','-frames:v',str(len(fs)),'-threads','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],capture_output=True);r.check_returncode();a=np.frombuffer(r.stdout,np.uint8).reshape(len(fs),h,w,3)
 if name=='C07':
  for f,arr in zip(fs,a):Image.fromarray(arr).save(QA/f'C07-lens-F{f:02}-960.jpg',quality=95)
 else:
  can=Image.new('RGB',(w*4,(h+26)*3),(18,18,18));d=ImageDraw.Draw(can)
  for k,(f,arr) in enumerate(zip(fs,a)):
   x=k%4*w;y=k//4*(h+26);can.paste(Image.fromarray(arr),(x,y));d.text((x+4,y+h),f'C52 assetF{f}',font=font,fill='white')
  can.save(QA/'C52-cut-F36-47.jpg',quality=92)
