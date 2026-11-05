from pathlib import Path
import subprocess,io
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
SRC='D:/咒术回战/4K 内嵌简中字幕/04.mp4'
times=list(range(1200,1281,5))
sheet=Image.new('RGB',(5*384,4*240),'#080b13');d=ImageDraw.Draw(sheet)
for i,t in enumerate(times):
    cmd=[FF,'-v','error','-threads','2','-ss',str(t),'-i',SRC,'-frames:v','1','-vf','scale=384:216','-f','image2pipe','-c:v','png','pipe:1']
    data=subprocess.run(cmd,capture_output=True,check=True).stdout
    im=Image.open(io.BytesIO(data));x=i%5*384;y=i//5*240
    sheet.paste(im,(x,y));d.text((x+5,y+218),f'e04 {t}.000s',fill='white')
sheet.save(HERE/'e04-standing-1200-1280.jpg',quality=92)
