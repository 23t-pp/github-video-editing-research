from pathlib import Path
import json,subprocess,io
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent.parent;P=json.loads((R/'data/edit-plan.json').read_text(encoding='utf-8'))
F='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';O=R/'evidence/slow-window-inspection';O.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17);records=[]
for s in P['shots']:
    if s.get('playbackRate',1)>=.5:continue
    a=max(0,s['searchWindowSeconds'][0]-.9);duration=2.5
    cmd=[F,'-v','error','-threads','1','-ss',str(a),'-t',str(duration),'-i',s['sourcePath'],'-an','-vf','fps=24,scale=320:180','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
    x=subprocess.run(cmd,capture_output=True,check=True).stdout;arr=np.frombuffer(x,dtype=np.uint8).reshape(-1,180,320,3)
    sheet=Image.new('RGB',(1600,6*206),'#080b13');d=ImageDraw.Draw(sheet)
    for i in range(min(len(arr),60)):
        px=(i%5)*320;py=(i//5)*103
        im=Image.fromarray(arr[i]).resize((320,180))
    # 10 columns by 6 rows, each source frame is visible at half size.
    sheet=Image.new('RGB',(1920,6*132),'#080b13');d=ImageDraw.Draw(sheet)
    for i in range(min(len(arr),60)):
        px=(i%10)*192;py=(i//10)*132
        sheet.paste(Image.fromarray(arr[i]).resize((192,108)),(px,py));d.text((px+3,py+109),f'{i:02} {a+i/24:.3f}',font=font,fill='white')
    name=s['id']+'-'+s['candidateId']+'.jpg';sheet.save(O/name,quality=92)
    changes=np.abs(arr[1:].astype(float)-arr[:-1].astype(float)).mean((1,2,3))
    records.append({'shot':s['id'],'candidate':s['candidateId'],'sourceStart':a,'fpsSample':24,'frames':len(arr),'contact':str((O/name).relative_to(R)).replace('\\','/'),'largeFrameDiffs':[{'frame':int(i+1),'seconds':a+(i+1)/24,'meanAbsoluteDiff':float(changes[i])} for i in np.where(changes>30)[0]]})
(R/'data/slow-window-inspection.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8');print('Inspected',len(records),'slow source windows')
