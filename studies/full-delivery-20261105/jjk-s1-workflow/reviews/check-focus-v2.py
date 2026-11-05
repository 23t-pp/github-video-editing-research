from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,hashlib,json,io
import numpy as np
R=Path(__file__).resolve().parents[1];V=R/'loops/loop-01/loop-01-rough-focus-v2.mp4';FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
blob=subprocess.run([FF,'-v','error','-i',str(V),'-frames:v','45','-an','-vf','scale=384:216','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],capture_output=True,check=True).stdout
frames=np.frombuffer(blob,dtype=np.uint8).reshape(-1,216,384,3);assert len(frames)==45
indices=[0,3,6,9,12,13,17,21,25,30,31,34,38,42,44]
im=Image.new('RGB',(1920,3*246),'#080b13');d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
for j,f in enumerate(indices):
    x=(j%5)*384;y=(j//5)*246;im.paste(Image.fromarray(frames[f]),(x,y));d.text((x+6,y+218),f'F{f} · {f/24:.3f}s',font=font,fill='white')
im.save(R/'reviews/L1-focus-v2-实际前45帧抽查.jpg',quality=94)
print('Decoded first45 frames; saved selected15-frame motion contact')
