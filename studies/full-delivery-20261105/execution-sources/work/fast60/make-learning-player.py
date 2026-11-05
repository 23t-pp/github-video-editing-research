"""A local, self-contained navigation page for the finished MP4."""
from pathlib import Path
import json

root=Path(__file__).resolve().parents[2]/'outputs'/'fast60'
plan=json.loads((root/'hyperframes/edit.json').read_text(encoding='utf-8'))
films=json.loads(Path(__file__).with_name('inventory.json').read_text(encoding='utf-8-sig'))
data={'shots':plan['shots'],'films':{k:v['name'] for k,v in films.items()},'sections':plan['sections']}
page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>弯心 APEX · 一分钟混剪</title><style>
:root{color-scheme:dark;--bg:#101111;--line:#373734;--ivory:#eee9df;--muted:#b8b5ab;--red:#fb7958}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ivory);font-family:"Microsoft YaHei",Arial,sans-serif}
main{max-width:1330px;margin:auto;padding:34px clamp(16px,4vw,60px) 40px}header{display:flex;align-items:baseline;justify-content:space-between;gap:15px;border-bottom:1px solid var(--line);padding-bottom:18px;margin-bottom:22px}h1,h2,p{margin:0}h1{font-size:clamp(26px,4vw,48px);letter-spacing:-.06em}h1 em{font:italic 800 .54em Arial;letter-spacing:.08em;color:var(--red);margin-left:10px}header>span{font:13px/1.6 Consolas,monospace;color:var(--muted)}
.layout{display:grid;grid-template-columns:minmax(0,1fr) 226px;gap:28px;align-items:start}video{width:100%;display:block;background:#000;aspect-ratio:16/9}.inspect{display:flex;gap:8px;align-items:center;padding:14px 0;border-bottom:1px solid var(--line);font:14px Consolas,monospace}.counter{margin-right:auto}button{font:inherit;cursor:pointer;color:var(--ivory)}.step{background:transparent;border:1px solid var(--line);padding:6px 9px}.step:hover,.step:focus-visible{border-color:var(--red)}h2{font-size:16px;font-weight:600;margin:0 0 10px}.chapter{display:flex;align-items:center;gap:12px;width:100%;text-align:left;background:none;border:0;border-top:1px solid var(--line);padding:15px 3px;font-size:14px}.chapter span{font:12px Consolas,monospace;color:var(--muted)}.chapter[aria-current=true]{color:var(--red)}.details{margin-top:20px;color:var(--muted);line-height:1.75;font-size:14px}.details strong{display:block;color:var(--ivory);font-size:18px;line-height:1.4;margin-bottom:5px}.source{overflow-wrap:anywhere}.links{display:flex;gap:20px;flex-wrap:wrap;margin-top:24px}a{color:var(--ivory);text-decoration-color:#777;text-underline-offset:4px;font-size:14px}
@media(max-width:800px){.layout{grid-template-columns:1fr;gap:20px}main{padding-top:20px}.chapter{width:auto;display:inline-flex;padding:12px 10px}header{align-items:center}.details{margin-top:14px}}
</style></head><body><main><header><h1>弯心 <em>APEX</em></h1><span>60.00 s · 24 fps · 1080p</span></header>
<div class="layout"><section><video id="movie" controls playsinline preload="metadata" poster="封面.jpg" src="弯心_APEX_60秒.mp4"></video>
<div class="inspect"><span id="counter" class="counter">00:00.000 · F0000</span><button class="step" id="prev" aria-label="上一帧">上一帧</button><button class="step" id="next" aria-label="下一帧">下一帧</button></div>
<div class="details" aria-live="off"><strong id="shot"></strong><span id="source" class="source"></span></div></section>
<aside><h2>跳到段落</h2><div id="chapters"></div></aside></div>
<nav class="links"><a href="剪辑学习手册.md">中文学习手册</a><a href="hyperframes/镜头表.csv">42镜头表</a><a href="hyperframes/assets/audio/master.wav">单独听混音</a></nav></main>
<script>const data=__DATA__;const movie=document.getElementById('movie');const clock=n=>{return String(Math.floor(n/60)).padStart(2,'0')+':'+String((n%60).toFixed(3)).padStart(6,'0')};
function go(frame){movie.currentTime=Math.max(0,Math.min(1439,frame))/24+0.001}
const marks=[];for(const part of data.sections){const b=document.createElement('button');b.className='chapter';const stamp=document.createElement('span');stamp.textContent=clock(part.startFrame/24).slice(0,part.startFrame%24?7:5);b.append(stamp,part.name);b.addEventListener('click',()=>go(part.startFrame));document.getElementById('chapters').append(b);marks.push(b)}
function update(){const f=Math.min(1439,Math.max(0,Math.floor(movie.currentTime*24+1e-5)));const s=data.shots.find(s=>s.startFrame<=f&&f<s.startFrame+s.frames);document.getElementById('counter').textContent=clock(movie.currentTime)+' · F'+String(f).padStart(4,'0');document.getElementById('shot').textContent=s.id+'　'+s.label;document.getElementById('source').textContent=data.films[s.film]+'　｜　源入点 '+String(Math.floor(s.sourceIn/3600)).padStart(2,'0')+':'+clock(s.sourceIn%3600)+'　｜　使用 '+s.frames+' 帧';data.sections.forEach((s,i)=>marks[i].setAttribute('aria-current',s.startFrame<=f&&f<s.endFrame?'true':'false'))}
function step(n){movie.pause();go(Math.floor(movie.currentTime*24+1e-5)+n)}
document.getElementById('prev').onclick=()=>step(-1);document.getElementById('next').onclick=()=>step(1);movie.addEventListener('timeupdate',update);movie.addEventListener('seeked',update);movie.addEventListener('loadedmetadata',update);if(movie.requestVideoFrameCallback){const tick=()=>{update();movie.requestVideoFrameCallback(tick)};movie.requestVideoFrameCallback(tick)}update();
</script></body></html>'''
page=page.replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('</','<\\/'))
(root/'学习播放器.html').write_text(page,encoding='utf-8')
