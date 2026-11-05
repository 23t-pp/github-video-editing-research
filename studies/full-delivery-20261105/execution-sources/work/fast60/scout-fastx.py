from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import io, subprocess
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent / 'fastx-windows'
root.mkdir(parents=True, exist_ok=True)
movie = next(Path('D:/速度与激情').glob('11 *.mp4'))
ffmpeg = 'C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
starts = [1708, 1888, 1948, 2128, 2248, 3867, 3928, 5997, 6058, 6960, 7037, 7048, 7067, 7078, 7097, 7108, 7158, 7198, 7278, 7318]

def inspect(start):
    filters = 'fps=2,zscale=w=300:h=126:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=rgb24'
    args = [ffmpeg, '-v', 'error','-threads','2','-filter_threads','1','-ss',str(start),'-i',str(movie),'-map','0:v:0','-an','-frames:v','12','-vf',filters,'-f','rawvideo','pipe:1']
    data = subprocess.run(args,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
    width, height = 300,126
    stride = width*height*3
    assert len(data) == stride*12
    sheet = Image.new('RGB',(width*4,(height+19)*3),(19,20,21)); draw=ImageDraw.Draw(sheet)
    for i in range(12):
        im=Image.frombytes('RGB',(width,height),data[i*stride:(i+1)*stride]);x=i%4*width;y=i//4*(height+19)
        sheet.paste(im,(x,y));draw.text((x+4,y+height+2),f'{start+i*.5:.1f}s',fill='white')
    sheet.save(root/f'x-{start}.jpg',quality=85)
    return start

with ThreadPoolExecutor(max_workers=2) as pool:
    for index in pool.map(inspect,starts): print(index,flush=True)
