from pathlib import Path
import subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parents[3];R=B/'outputs/jjk-s1-workflow';E=R/'evidence/alpha';F='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
raw=subprocess.run([F,'-v','error','-threads','1','-i',str(R/'hyperframes/assets/shots/XCHASE.mp4'),'-an','-vf','scale=in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24','-f','rawvideo','pipe:1'],capture_output=True,check=True).stdout
frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,1080,1920,3);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18);sheet=Image.new('RGB',(1920,4*270),'#111111')
for k,f in enumerate(range(2,28,2)):
    im=Image.fromarray(frames[f]);im.save(E/f'XCHASE-source-F{f:02}.png');thumb=im.resize((480,270));d=ImageDraw.Draw(thumb);d.text((8,8),f'F{f}',font=font,fill='yellow');sheet.paste(thumb,((k%4)*480,(k//4)*270))
Image.fromarray(frames[27]).save(E/'XCHASE-source-F27.png');sheet.save(E/'XCHASE-source-motion.jpg',quality=94)
print('source inspection frames')
