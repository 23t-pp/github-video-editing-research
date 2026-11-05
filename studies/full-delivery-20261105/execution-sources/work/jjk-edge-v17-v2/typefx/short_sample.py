from pathlib import Path
import sys,shutil,json,subprocess,os
from typefx import type_layers
ROOT=Path(__file__).resolve().parent
V1=ROOT.parents[2]/'outputs/jjk-edge-v17/hyperframes'
PROJECT=ROOT/'sample-project';PROJECT.mkdir(exist_ok=True)
for f in ['assets/gsap.min.js','assets/fonts/BarlowCondensed-ExtraBold.woff2','assets/fonts/heavy.ttf','DESIGN.md','hyperframes.json']:
    dst=PROJECT/f;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(V1/f,dst)
events=[dict(id='slam',start=0,end=15,text='THE STRONGEST',subtitle='最强 · 五条悟',mode='slam',font_size=560,board=True),dict(id='ring',start=15,end=34,text='NO LIMIT',subtitle='无下限',mode='orbit',font_size=570,board=True),dict(id='twin',start=34,end=58,text=['GOJO GETO','ONLY FRIEND'],subtitle='唯一的挚友',mode='twin',font_size=450,board=True),dict(id='ribbon',start=58,end=72,text='PURPLE',subtitle='虚式 · 茈',mode='ribbon',font_size=600,board=True)]
body,css,js=type_layers(events,24,0,72)
doc=f'''<!doctype html><html><head><meta charset="utf-8"><style>@font-face{{font-family:"Barlow Condensed";src:url("assets/fonts/BarlowCondensed-ExtraBold.woff2") format("woff2");font-weight:800}}@font-face{{font-family:"JJK Heavy";src:url("assets/fonts/heavy.ttf")}}html,body{{margin:0;background:#080b13;width:1920px;height:1080px;overflow:hidden}}[data-composition-id]{{position:relative;width:1920px;height:1080px;overflow:hidden}}{css}</style></head><body><div data-composition-id="type-sample" data-start="0" data-duration="3" data-width="1920" data-height="1080">{body}</div><script src="assets/gsap.min.js"></script><script>const tl=gsap.timeline({{paused:true}});{''.join(js)}window.__timelines={{"type-sample":tl}};</script></body></html>'''
(PROJECT/'index.html').write_text(doc,encoding='utf-8')
(ROOT/'sample-events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8')
print(PROJECT,flush=True)
if '--render' in sys.argv:
    node='C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
    cli='C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/bin/hyperframes.mjs'
    env={**os.environ,'HYPERFRAMES_BROWSER_PATH':'C:/Program Files/Google/Chrome/Application/chrome.exe','HYPERFRAMES_FFMPEG_PATH':'C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe','HYPERFRAMES_FFPROBE_PATH':'C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'}
    with (ROOT/'sample-render.log').open('wb') as log:
        p=subprocess.run([node,cli,'render',str(PROJECT),'--fps','24','--format','png-sequence','--workers','1','--low-memory-mode','--sdr','--experimental-fast-capture=false','--no-best-effort','--frames-cache-dir','off','--output',str(ROOT/'sample-frames')],env=env,stdout=log,stderr=subprocess.STDOUT)
    print('render exit',p.returncode,flush=True)
    print((ROOT/'sample-render.log').read_text(encoding='utf-8',errors='replace')[-2500:])
