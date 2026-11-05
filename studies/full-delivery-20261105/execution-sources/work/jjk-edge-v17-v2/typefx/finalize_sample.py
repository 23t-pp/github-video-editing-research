from pathlib import Path
import json,subprocess,os,re,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont,ImageChops
from typefx import type_layers,_pose
R=Path(__file__).resolve().parent
NODE='C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe';CLI='C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/bin/hyperframes.mjs';FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
env={**os.environ,'HYPERFRAMES_BROWSER_PATH':'C:/Program Files/Google/Chrome/Application/chrome.exe','HYPERFRAMES_FFMPEG_PATH':FF,'HYPERFRAMES_FFPROBE_PATH':'C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'}
events=json.loads((R/'sample-events.json').read_text(encoding='utf-8'))
# Same actual event starts at global F15; crop starts in its fifth motion frame.
a,b=19,27
body,css,js=type_layers(events,24,a,b)
project=R/'chunk-check-project';shutil.copytree(R/'sample-project',project,dirs_exist_ok=True)
doc=(R/'sample-project/index.html').read_text(encoding='utf-8')
prefix=doc.split('<body>')[0];new=prefix+f'<body><div data-composition-id="type-sample" data-start="0" data-duration="{(b-a)/24}" data-width="1920" data-height="1080">{body}</div><script src="assets/gsap.min.js"></script><script>const tl=gsap.timeline({{paused:true}});'+''.join(js)+'window.__timelines={"type-sample":tl};</script></body></html>'
(project/'index.html').write_text(new,encoding='utf-8')
with (R/'chunk-render.log').open('wb') as log:
    subprocess.run([NODE,CLI,'render',str(project),'--fps','24','--format','png-sequence','--workers','1','--low-memory-mode','--sdr','--experimental-fast-capture=false','--no-best-effort','--frames-cache-dir','off','--output',str(R/'chunk-frames')],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
diffs=[]
for i in range(b-a):
    x=Image.open(R/f'sample-frames/frame_{a+i+1:06}.png').convert('RGB');y=Image.open(R/f'chunk-frames/frame_{i+1:06}.png').convert('RGB')
    d=ImageChops.difference(x,y);bbox=d.getbbox()
    diffs.append({'globalFrame':a+i,'identical':bbox is None,'differenceBBox':bbox})
for name,args in [('lint',['lint',str(R/'sample-project'),'--json']),('validate',['validate',str(R/'sample-project'),'--json','--no-contrast'])]:
    p=subprocess.run([NODE,CLI,*args],env=env,capture_output=True)
    (R/f'{name}.json').write_bytes(p.stdout)
    print(name,p.returncode,flush=True)
with (R/'V02精细文字_3秒短样.mp4').open('wb') as f:
    subprocess.run([FF,'-v','error','-framerate','24','-i',str(R/'sample-frames/frame_%06d.png'),'-frames:v','72','-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p','-c:v','libx264','-threads','2','-preset','fast','-crf','17','-pix_fmt','yuv420p','-an','-movflags','frag_keyframe+empty_moov+default_base_moof','-f','mp4','pipe:1'],stdout=f,check=True)
keys=[0,2,5,15,17,20,24,33,34,38,44,52,58,61,65]
sheet=Image.new('RGB',(1920,5*390),'#080b13');draw=ImageDraw.Draw(sheet)
for n,k in enumerate(keys):
    img=Image.open(R/f'sample-frames/frame_{k+1:06}.png').convert('RGB');img.thumbnail((640,360));x=n%3*640;y=n//3*390;sheet.paste(img,(x,y));draw.text((x+12,y+365),f'F{k:03d} | {k/24:.3f}s',fill='white')
sheet.save(R/'V02精细文字_关键帧联系图.jpg',quality=94)
report={'fps':24,'frames':72,'duration':3,'chunkRange':[a,b],'chunkPixelComparison':diffs,'allChunkFramesIdentical':all(d['identical'] for d in diffs),'fonts':'Original local Barlow Condensed ExtraBold / JJK Heavy','geometry':'Continuous nonlinear SVG outline; editable source text retained in defs; 32x6 legacy slices available only with geometry=slices','sha256':hashlib.sha256((R/'V02精细文字_3秒短样.mp4').read_bytes()).hexdigest()}
(R/'短样验收.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False),flush=True)
