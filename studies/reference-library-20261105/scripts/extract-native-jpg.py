"""Save original decoded frames with no rate conversion, indexed by the source PTS."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parent.parent
ident, src = sys.argv[1], Path(sys.argv[2])
assert ident.startswith('V') and ident[1:].isdigit()
evidence = root / 'evidence' / ident
target = evidence / 'frames'
target.mkdir(parents=True, exist_ok=True)
info = json.loads((root/'data/frame-analysis'/f'{ident}.json').read_text('utf-8'))
pts = json.loads((root/'data/frame-analysis'/f'{ident}-pts.json').read_text('utf-8'))
with src.open('rb') as stream:
    assert hashlib.file_digest(stream, 'sha256').hexdigest() == info['sourceSha256']

cmd = ['ffmpeg','-nostdin','-v','error','-xerror','-threads','2','-i',str(src),
       '-map','0:v:0','-an','-fps_mode','passthrough','-c:v','mjpeg','-threads','2',
       '-q:v','4','-f','image2pipe','pipe:1']
process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
count = 0
buf = b''
assert process.stdout is not None
with process.stdout as pipe:
    for chunk in iter(lambda:pipe.read(131072), b''):
        buf += chunk
        while (end := buf.find(b'\xff\xd9')) >= 0:
            jpg, buf = buf[:end+2], buf[end+2:]
            assert jpg.startswith(b'\xff\xd8')
            (target/f'F{count:04d}.jpg').write_bytes(jpg)
            count += 1
assert process.wait() == 0 and not buf and count == len(pts) == info['nativeFrameCount']
with (root/'data/frame-analysis'/f'{ident}-jpg-map.csv').open('w',encoding='utf-8',newline='') as out:
    writer=csv.writer(out)
    writer.writerow(['native_frame','pts_seconds','relative_jpg'])
    for i,item in enumerate(pts):
        assert i==item['i']
        p=target/f'F{i:04d}.jpg'
        with Image.open(p) as im:
            assert im.size==(1920,1440) if ident=='V22' else im.width>0 and im.height>0
            im.verify()
        writer.writerow([i,f'{item["pts"]:.6f}',p.relative_to(root).as_posix()])

if ident=='V22':
    font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',15)
    def board(indices,name,columns):
        w,h=300,225
        rh=h+25
        img=Image.new('RGB',(columns*(w+6)+6,((len(indices)+columns-1)//columns)*(rh+4)+4),'#12151d')
        draw=ImageDraw.Draw(img)
        for j,i in enumerate(indices):
            x=6+(j%columns)*(w+6); y=4+(j//columns)*(rh+4)
            with Image.open(target/f'F{i:04d}.jpg') as p:
                img.paste(p.resize((w,h),Image.Resampling.LANCZOS),(x,y))
            draw.text((x+4,y+h+4),f'F{i:04d}  {pts[i]["pts"]:.3f}s',font=font,fill='#f7f9fc')
        img.save(evidence/name,quality=92)
    board(list(range(0,count,48)), 'overview.jpg', 4)
    board(list(range(0,count,60)), 'timeline-01.jpg', 5)
    board([107,108,112,117,118,137,138,144,199,200,206,210], 'V22-A_来镜提前与开窗.jpg', 4)
    board([410,426,428,429,438,439,462,463,620,621,647,648], 'V22-B_人物不动换背景.jpg',4)
    board([679,680,688,693,747,750,765,779,787,810,824,825], 'V22-C_斜卡与四格.jpg',4)
    board([863,864,887,888,925,926,955,956,972,974,990,1005,1035,1050,1078,1079], 'V22-D_扩窗回忆与尾卡.jpg',4)
print(json.dumps({'video':ident,'originalFrames':count,'output':str(target)},ensure_ascii=False))
