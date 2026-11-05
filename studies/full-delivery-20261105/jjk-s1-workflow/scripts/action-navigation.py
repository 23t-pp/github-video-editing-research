from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];D=R/'evidence/source-overviews/action-navigation';D.mkdir(parents=True,exist_ok=True)
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';SOURCE=Path('D:/咒术回战/1080P 内嵌简中字幕')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
sets=[(4,990),(5,320),(5,520),(7,240),(7,1100),(17,100),(17,420),(19,880),(20,200),(20,1100),(23,200),(24,350),(24,650)]
index=[]
for ep,start in sets:
    group=f'E{ep:02}-{start:04}';folder=D/group;folder.mkdir(exist_ok=True);sheet=Image.new('RGB',(1920,930),'#10131a');draw=ImageDraw.Draw(sheet);draw.text((15,4),f'S1 {group} | 5秒稀疏导航，未作运动方向验收',font=font,fill='#72c7ed');samples=[]
    for i in range(24):
        t=start+5*i;p=folder/f'{t:07.2f}.jpg'
        if not p.exists():
            b=subprocess.run([FF,'-v','error','-threads','1','-ss',str(t),'-i',str(SOURCE/f'{ep:02}.mp4'),'-frames:v','1','-an','-vf','scale=640:360','-q:v','3','-f','image2pipe','pipe:1'],capture_output=True,check=True).stdout;p.write_bytes(b)
        image=Image.open(p).convert('RGB');x=(i%6)*320;y=40+(i//6)*220;sheet.paste(image.resize((320,180)),(x,y));draw.text((x+7,y+184),f'{t}s',font=small,fill='white');samples.append({'targetSeconds':t,'jpg':p.relative_to(R).as_posix()})
    out=D/f'{group}.jpg';sheet.save(out,quality=92);index.append({'episode':ep,'start':start,'contactSheet':out.relative_to(R).as_posix(),'samples':samples,'viewed':False});print(group,flush=True)
(R/'data/action-navigation-index.json').write_text(json.dumps({'scope':'13组×24帧，每5秒单张导航，非全帧/非运动方向验收','items':index},ensure_ascii=False,indent=2),encoding='utf-8')
