from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3]/'outputs/jjk-s1-workflow';E=R/'evidence/source-overviews/fresh-candidates';spec=[('C047新窗',17,[444.85+i*1.2/7 for i in range(8)]),('C076新窗',20,[1214.4+i*1.1/7 for i in range(8)]),('C088人物上下文',24,[440,442,444,446,448,450,452,454])];font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18);sheet=Image.new('RGB',(1920,3*175+30),'#111620');d=ImageDraw.Draw(sheet)
for row,(label,ep,ts) in enumerate(spec):
    y=30+row*175;d.text((8,y),label,font=font,fill='white')
    for k,t in enumerate(ts):
        f=round(t*60);p=R/'素材集_60Hz_JPG'/f'S1E{ep:02}'/f'minute-{f//3600:03}'/f'F{f:07}.jpg';im=Image.open(p).convert('RGB').resize((240,135));sheet.paste(im,(k*240,y+27));d.text((k*240+6,y+153),f'{f/60:.3f}',font=font,fill='white')
sheet.save(E/'fresh-extra-proof.jpg',quality=94)
