from pathlib import Path
import json
from typefx import type_layers,_states
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'outputs/jjk-edge-v17/evidence/v02-type'; OUT.mkdir(parents=True,exist_ok=True)
events=[dict(id='unique',start=0,end=72,mode='twin',text=['唯一','挚友'],board=True,font_size=285),
        dict(id='strong',start=0,end=48,mode='slam',text='最强',board=True,font_size=440),
        dict(id='infinity',start=0,end=48,mode='orbit',text='无下限',board=True,font_size=340),
        dict(id='lost',start=0,end=72,mode='ribbon',text='失控',board=True,font_size=560)]
for e in events:
 h,c,j=type_layers([e],24,0,72)
 (OUT/f'preview-{e["mode"]}.html').write_text('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#0c1220;width:1920px;height:1080px;overflow:hidden}'+c+'</style></head><body>'+h+'<script src="file:///D:/gpt/tools/agent-skills/herk-edit-kit/repo/node_modules/gsap/dist/gsap.min.js"></script><script>const tl=gsap.timeline({paused:true});'+''.join(j)+';window.tl=tl;</script></body></html>',encoding='utf-8')
# Verify clipping matches full-event analytic pose, no negative local timeline.
h,c,j=type_layers([dict(start=120,end=216,mode='twin',text=['唯一','挚友'])],24,144,192)
assert 'data-start="0.000000000"' in h and 'data-duration="2.000000000"' in h
assert json.loads(j[0].split(',',1)[1].rsplit(',0.000000000',1)[0])==_states('twin',1,4)[0]
assert not type_layers(events,24,100,120)[0]
print('Generated four previews; passed global-frame clipping pose assertions.')
