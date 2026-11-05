from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,io,time,sys
from PIL import Image,ImageDraw,ImageFont

BASE=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent/'scout';OUT.mkdir(parents=True,exist_ok=True)
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
SRC=Path('D:/咒术回战/4K 内嵌简中字幕')
# New local source windows: retain the Hidden Inventory character arc.
times={1:[850,875,888,905,915,928,940,948,972,985,1010,1040,1070,1100,1130,1160,1190,1220,1250],
       2:[310,340,360,380,405,425,450,475,485,520,540,570,600,1145,1155,1180,1190,1200,1235,1248,1275,1300,1320],
       3:[420,430,465,480,510,540,570,600,680,700,720,740,760,785,800,815,830,845,860,875,900,910,940,950,960,975,990,1150,1160,1185,1200,1220],
       4:[190,220,240,260,280,300,315,340,350,365,380,395,410,435,445,460,475,490,505,765,775,800,805,815,825,835,845,850,865,880,890,905,920,935,950,960,980,1002,1020,1040,1055,1082,1090,1100,1110,1120,1270,1295,1320,1350],
       5:[265,295,325,355,385,415,445,475,505,535,565,595,625,655,685,715,745,775,805,835,865,895,925,950,990,1010,1050,1065,1095,1110,1130,1150]}
jobs=[dict(id=f'E{ep:02}-{t:07.2f}',episode=ep,time=t) for ep,ts in times.items() for t in ts]
def grab(j):
    p=OUT/(j['id']+'.jpg')
    if not p.exists():
        cmd=[FF,'-v','error','-threads','1','-filter_threads','1','-ss',str(j['time']),'-i',str(SRC/f'{j["episode"]:02}.mp4'),'-frames:v','1','-an','-vf','scale=384:216','-c:v','mjpeg','-threads','1','-q:v','3','-f','image2pipe','pipe:1']
        r=subprocess.run(cmd,capture_output=True,check=True);Image.open(io.BytesIO(r.stdout)).save(p,quality=90)
    return {**j,'file':str(p.relative_to(BASE))}
if __name__=='__main__':
    done=[]
    with ThreadPoolExecutor(max_workers=2) as ex:
        for i,j in enumerate(ex.map(grab,jobs)):
            done.append(j)
            if i%20==0:print('SCOUT',i+1,'/',len(jobs),flush=True)
    for ep in times:
        rows=[j for j in done if j['episode']==ep]
        for page,k in enumerate(range(0,len(rows),24),1):
            batch=rows[k:k+24];canvas=Image.new('RGB',(1536,242*((len(batch)+3)//4)),(12,14,20));d=ImageDraw.Draw(canvas)
            for i,j in enumerate(batch):
                x=(i%4)*384;y=(i//4)*242
                canvas.paste(Image.open(BASE/j['file']),(x,y));d.text((x+5,y+219),j['id'],fill='white')
            canvas.save(OUT/f'board-e{ep:02}-{page:02}.jpg',quality=91)
    (OUT/'index.json').write_text(json.dumps({'sampling':'single representative frame at stated source second; shortlisted motion windows require separate review','candidates':done},ensure_ascii=False,indent=2),encoding='utf8')
    print('SCOUT COMPLETE',len(done),flush=True)
