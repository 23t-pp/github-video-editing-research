"""Freeze actual HF pixel evidence before a later loop changes the render cache."""
from pathlib import Path
import argparse,json,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
A=argparse.ArgumentParser();A.add_argument('--loop',type=int,required=True);A.add_argument('--plan',required=True);args=A.parse_args()
R=Path(__file__).resolve().parent.parent;W=R.parents[1];C=W/'work/jjk-s1-workflow/render-cache/master-frames';L=R/f'loops/loop-{args.loop:02}';D=L/'evidence';D.mkdir(parents=True,exist_ok=True)
p=json.loads((R/args.plan).read_text(encoding='utf-8'));rows=[]
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',15)
def collect(name,frames):
 frames=list(dict.fromkeys(f for f in frames if 0<=f<p['durationFrames']));cols=4;tw,th=480,270;label=24
 im=Image.new('RGB',(cols*tw,((len(frames)+cols-1)//cols)*(th+label)),(8,11,19));draw=ImageDraw.Draw(im)
 refs=[]
 for i,f in enumerate(frames):
  src=C/f'frame_{f+1:06}.png';assert src.exists(),src
  tile=Image.open(src).convert('RGB');tile.thumbnail((tw,th));x=i%cols*tw;y=i//cols*(th+label);im.paste(tile,(x,y));draw.text((x+5,y+th+3),f'F{f:04}  {f/24:.3f}s',font=font,fill='#72c7ed')
  refs.append({'frame':f,'captureSha256':hashlib.sha256(src.read_bytes()).hexdigest()})
 dest=D/(name+'.jpg');im.save(dest,quality=91)
 rows.append({'event':name,'contactSheet':dest.relative_to(R).as_posix(),'samples':refs})
for e in [*p.get('typeEvents',[]),*p.get('layouts',[]),*p.get('foregrounds',[])]:
 st,en=e['start'],e['end'];n=en-st
 frames=list(range(max(0,st-1),min(p['durationFrames'],en+1))) if n<=60 else [round(st+(n-1)*i/15) for i in range(16)]
 collect(e['id'],frames)
 for f in [max(0,st-1),st,(st+en-1)//2,en-1,min(p['durationFrames']-1,en)]:
  src=C/f'frame_{f+1:06}.png';shutil.copyfile(src,D/f'F{f:04}.png')
e=p.get('archiveScreen');collect('archive-screen',[e['start']-1,*[round(e['start']+(e['end']-e['start']-1)*i/19) for i in range(20)],e['end']])
collect('same-source-handoff-1060-1076',range(1060,1077))
collect('native-cut-adjacency',[f for s in p['shots'][1:] for f in [s['startFrame']-1,s['startFrame']]])
if args.loop>=4:
 collect('eyes-return-action-815-843',range(815,844))
 for n,st in enumerate([1280,1308,1336],1):collect(f'tail-action-release-{n}',range(st,min(st+28,1363)))
 for f in [823,829,830,841,842,1281,1282,1289,1290,1294,1295,1311,1312,1335,1336,1359,1360,1362]:
  shutil.copyfile(C/f'frame_{f+1:06}.png',D/f'F{f:04}.png')
out=L/'capture-evidence.json';out.write_text(json.dumps({'scope':'actual HF master capture pixels, frame0based, before later-loop cache replacement; not an audit verdict','plan':args.plan,'planSha256':hashlib.sha256((R/args.plan).read_bytes()).hexdigest(),'items':rows},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'loop':args.loop,'contacts':len(rows),'frozenEvidence':str(out)},ensure_ascii=False))
