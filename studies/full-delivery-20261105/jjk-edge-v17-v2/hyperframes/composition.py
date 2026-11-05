"""V17 visual structure with V02 typography. Preview and export share geometry."""
from pathlib import Path
from html import escape
import json,math,hashlib
ROOT=Path(__file__).resolve().parent
def load_edit():return json.loads((ROOT/'edit.json').read_text(encoding='utf-8'))
def save_editable(doc):
    target=ROOT/'index.html';sig=ROOT/'generated-index.sha256'
    if target.exists() and sig.exists() and hashlib.sha256(target.read_bytes()).hexdigest()!=sig.read_text().strip():
        backup=ROOT/'.source-backups';backup.mkdir(exist_ok=True)
        (backup/('studio-'+hashlib.sha256(target.read_bytes()).hexdigest()[:12]+'.html.bak')).write_bytes(target.read_bytes())
    target.write_text(doc,encoding='utf-8');sig.write_text(hashlib.sha256(doc.encode()).hexdigest())
def ease(p):return 1-(1-max(0,min(1,p)))**3
def build(plan,first=0,last=None,frame_mode=False):
    from typefx import type_layers
    from layoutfx import layout_layers
    last=plan['durationFrames'] if last is None else last;fps=plan['fps'];needed=set();copies=set();anim=[];layers=[]
    assets={a['id']:a for a in plan['assets']};sec=lambda f:f'{f/fps:.9f}'
    def overlap(a,b):return a<last and b>first
    def media(tag,assetId,start,end,offset=12,track=0):
        a,b=max(first,start),min(last,end)
        if a>=b:return ''
        if frame_mode:
            result=[]
            for f in range(a,b):
                n=offset+f-start;needed.add((assetId,n))
                result.append(f'<img id="{tag}-{f}" class="clip source" src="assets/frames/{assetId}-{n:04}.png" data-start="{sec(f-first)}" data-duration="{sec(1)}" data-track-index="{track}" data-layout-allow-overlap="true">')
            return ''.join(result)
        return f'<video id="{tag}" class="clip source" src="{escape(assets[assetId]["asset"])}" muted playsinline data-volume="0" preload="metadata" data-start="{sec(a-first)}" data-duration="{sec(b-a)}" data-media-start="{sec(offset+a-start)}" data-track-index="{track}" data-layout-allow-overlap="true"></video>'
    def setat(tag,f,props):anim.append(f'tl.set({json.dumps("#"+tag)},{json.dumps(props,separators=(",",":"))},{sec(f-first)});')
    def perframe(tag,start,end,pose):
        for f in range(max(first,start),min(last,end)):setat(tag,f,pose(f,(f-start)/max(1,end-start-1)))
    # Each native cut remains an independent media clip. Only its visual wrapper moves.
    for s in plan['shots']:
        st=s['startFrame'];end=st+s['frames']
        if not overlap(st,end):continue
        tag='base-'+s['id'];body=media(s['id'],s['assetId'],st,end,s['assetStartFrame'],0)
        layers.append(f'<div id="{tag}" class="plane shot">{body}</div>')
        punch=float(s.get('punch',.07));direction=s.get('motion',1)
        def pose(f,p,s=s,punch=punch,direction=direction,st=st,end=end):
            if s.get('cameraLocked'):return {'scale':1,'rotation':0,'x':0,'filter':'none'}
            q=1-ease(min(1,(f-st)/5));zoom=1+punch*q+.025*p
            r=(1 if direction>=0 else -1)*s.get('rotation',0)*q
            return {'scale':zoom,'rotation':r,'x':-direction*14*p,'filter':f'contrast(1.04) saturate(1.10) blur({1.2*q if punch>.13 else 0:.2f}px)'}
        perframe(tag,st,end,pose)
    # Timed overlay video clips use the same source clock as the native shots.
    for i,e in enumerate(plan.get('visuals',[])):
        start,end=e['start'],e['end'];a,b=max(first,start),min(last,end)
        if a>=b:continue
        tag='fx-'+e['id'];kind=e['kind'];z=e.get('z',20);body='';style='';inner=[]
        for j,clip in enumerate(e.get('clips',[])):
            ctag=f'{tag}-plane-{j}';cbody=media(f'{tag}-source-{j}',clip['assetId'],start,end,clip.get('offset',12),5+i*3+j)
            inner.append(f'<div id="{ctag}" class="plane">{cbody}</div>')
        if kind=='memory':
            style='left:170px;top:570px;width:720px;height:405px;inset:auto;border:3px solid #e8c39c;box-shadow:0 0 35px #080b13;overflow:hidden;'
            body=f'<div class="memory-source">{"".join(inner)}</div><div class="film-edge"></div>'
        elif kind=='tear':
            # Uneven hand-authored contours, with a paper rim outside the live video.
            poly='polygon(26% 0,74% 0,72% 6%,76% 14%,73% 22%,77% 31%,74% 40%,77% 48%,73% 57%,76% 65%,72% 74%,75% 82%,72% 90%,74% 100%,26% 100%,28% 92%,24% 83%,27% 73%,23% 64%,26% 56%,23% 46%,27% 36%,23% 27%,27% 18%,24% 9%)'
            body=f'<div class="paper-rim" style="clip-path:{poly}"></div><div class="plane torn-image" style="clip-path:{poly}">{"".join(inner)}</div>'
        elif kind=='halves':
            body=''.join(f'<div class="plane" style="clip-path:{"inset(0 50% 0 0)" if j==0 else "inset(0 0 0 50%)"}">{item}</div>' for j,item in enumerate(inner))
            style='overflow:hidden;'
        elif kind=='lens':
            body=f'<div class="plane" style="clip-path:inset(108px 0 108px 0)">{"".join(inner)}</div>'
            style='overflow:hidden;'
        elif kind=='circle':
            body=''.join(inner);style='border-radius:50%;overflow:hidden;'
        elif kind=='black':body='<div class="plane black"></div>'
        elif kind=='lightning':
            body='<svg width="1920" height="1080" viewBox="0 0 1920 1080"><path id="pulse-line" d="M0 540H470L510 510L550 585L590 460L625 650L680 395L725 590L770 515L815 540H1920" fill="none" stroke="#72c7ed" stroke-width="4" stroke-linejoin="round" stroke-dasharray="2600"/><path d="M0 540H1920" stroke="#72c7ed" stroke-width="1" opacity=".18"/></svg>'
        else:body=''.join(inner)
        layers.append(f'<div id="{tag}" class="plane fx fx-{kind}" style="z-index:{z};opacity:0;{style}">{body}</div>')
        setat(tag,a,{'opacity':1})
        if b<last:setat(tag,b,{'opacity':0})
        if kind=='memory':
            perframe(tag,start,end,lambda f,p:{'x':-90*(1-ease(p*5)),'y':80*(1-ease(p*5)),'rotation':-3+2*p,'opacity':min(1,p*8,(1-p)*10),'scale':.92+.08*ease(p*3)})
        elif kind=='tear':
            perframe(tag,start,end,lambda f,p:{'x':e.get('x',0)+180*(1-ease(p*5)),'scaleX':.05+.95*ease(p*6),'rotation':e.get('rotation',-4)*(1-p),'opacity':min(1,p*8,(1-p)*12)})
            for j in range(len(inner)):perframe(f'{tag}-plane-{j}',start,end,lambda f,p:{'scale':e.get('sourceScale',1.35),'x':e.get('sourceX',0),'y':e.get('sourceY',0)})
        elif kind=='halves':
            for j in range(min(2,len(inner))):
                transform=e.get('transforms',[{'scale':1},{'scale':2.6,'x':100,'y':-108}])[j]
                perframe(f'{tag}-plane-{j}',start,end,lambda f,p,j=j,t=transform:{'x':t.get('x',0)+(1 if j==0 else -1)*50*(1-ease(p*8)),'y':t.get('y',0),'scale':t.get('scale',1),'transformOrigin':'50% 50%','filter':'contrast(1.07)'})
        elif kind=='lens':
            keys=json.loads((ROOT/'motion/lens-keyframes.json').read_text(encoding='utf-8'))
            keys=keys.get('keyframes',keys.get('frames',[])) if isinstance(keys,dict) else keys
            # The source animation jumps pose when the spectacles swing.
            # This short memory flash uses the stable first lens, then fades.
            def lenspose(f,p):
                source_frame=12+f-start
                anchor=max((k for k in keys if k['assetFrame']<=source_frame),key=lambda k:k['assetFrame'])
                cx,cy,r=anchor['cx'],anchor['cy'],anchor['r']
                q=(f-start)/37;alpha=1 if source_frame<=19 else max(0,(23-source_frame)/4)
                return {'clipPath':f'circle({r}px at {cx}px {cy}px)','scale':1+.025*q,'x':14*q,'opacity':alpha}
            perframe(tag,start,end,lenspose)
            for j in range(len(inner)):perframe(f'{tag}-plane-{j}',start,end,lambda f,p:{'scale':1.15,'x':100,'y':100})
        elif kind=='circle':
            perframe(tag,start,end,lambda f,p:{'clipPath':f'circle({max(0,72*(1-ease(max(0,(p-.52)/.48)))):.3f}% at 66% 58%)','borderRadius':'0%','scale':1+.1*p,'opacity':1})
        elif kind=='lightning':
            perframe('pulse-line',start,end,lambda f,p:{'strokeDashoffset':2600*(1-ease(p*2)),'opacity':min(1,p*8,(1-p)*5)})
    layout_html,layout_css=layout_layers(plan.get('layouts',[]),plan,fps,first,last,media,setat)
    layers.append(layout_html)
    # Real moving foregrounds, before/behind ordering is explicit.
    for i,e in enumerate(plan.get('foregrounds',[])):
        start,end=e['start'],e['end'];a,b=max(first,start),min(last,end)
        if a>=b:continue
        tag='fg-'+e['id']
        echoes=e.get('echoes',[])
        for echo_index,echo in enumerate([*echoes,{}]):
            child=tag+f'-echo-{echo_index}' if echo else tag;body=[];lag=int(echo.get('lag',0))
            for f in range(a,b):
                n=max(e.get('minFrame',e.get('offset',0)),e.get('offset',0)+f-start-lag)
                path=f'assets/alpha/{e["alpha"]}/{n:06}.png';copies.add(path)
                body.append(f'<img id="{child}-{f}" class="clip source" src="{path}" data-start="{sec(f-first)}" data-duration="{sec(1)}" data-track-index="{100+i*3+echo_index}" data-layout-allow-overlap="true">')
            clipping='clip-path:inset(108px 0 108px 0);' if e.get('clipActive',False) else ''
            layers.append(f'<div class="plane" style="z-index:{e.get("z",60)};{clipping}"><div id="{child}" class="plane foreground">{"".join(body)}</div></div>')
            def fgpose(f,p,e=e,echo=echo):
                enter=ease((f-start)/max(1,e.get('inFrames',6)))
                exit=1 if not e.get('outFrames',0) else min(1,max(0,(end-1-f)/e['outFrames']))
                alpha=e.get('opacity',1)*echo.get('opacity',1)*exit
                glow=e.get('glow',2);rx=e.get('restX',0);ry=e.get('restY',0)
                return {'x':rx+e.get('x',0)*(1-enter)+echo.get('dx',0),'y':ry+e.get('y',0)*(1-enter)+echo.get('dy',0),
                    'scale':e.get('scale',1)+(e.get('enterScale',e.get('scale',1))-e.get('scale',1))*(1-enter),
                    'rotation':e.get('restRotation',0)+e.get('rotation',0)*(1-enter),'opacity':alpha,
                    'filter':f'drop-shadow(0 0 {glow}px {e.get("glowColor","#72c7ed")})'+(' blur(2px) saturate(.65)' if echo else '')}
            perframe(child,start,end,fgpose)
    types,css,tweens=type_layers(plan.get('typeEvents',[]),fps,first,last);layers.append(types);anim+=tweens
    layers.append('<div id="accent-light" class="plane accent-light"></div>')
    for f in range(first,last):
        amount=max([0,*[float(e.get('amount',.25))*max(0,1-abs(f-e['frame'])/e.get('width',3)) for e in plan.get('flashes',[])]])
        setat('accent-light',f,{'opacity':amount})
    if not frame_mode:layers.append(f'<audio id="edge-bgm" src="{plan["audio"]["master"]}" data-start="0" data-duration="{sec(last-first)}" data-track-index="200" data-volume="1"></audio>')
    style='''@font-face{font-family:"JJK Heavy";src:url("assets/fonts/heavy.ttf")}@font-face{font-family:"JJK Latin";src:url("assets/fonts/BarlowCondensed-ExtraBold.woff2")}@font-face{font-family:"Barlow Condensed";src:url("assets/fonts/BarlowCondensed-ExtraBold.woff2")}*{box-sizing:border-box}html,body{margin:0;width:1920px;height:1080px;background:#080b13;overflow:hidden}#root{position:relative;width:1920px;height:1080px;overflow:hidden;background:#080b13}.plane{position:absolute;inset:0;width:1920px;height:1080px;transform-origin:50% 50%}.source{position:absolute;inset:0;width:1920px;height:1080px;object-fit:fill}.shot{overflow:hidden}.fx{pointer-events:none}.fx .plane{overflow:hidden}.fx-memory .memory-source{position:absolute;inset:0;width:1920px;height:1080px;transform:scale(.375);transform-origin:0 0;filter:sepia(.25) saturate(1.15)}.film-edge{position:absolute;inset:0;border:8px solid rgba(8,11,19,.3)}.paper-rim{position:absolute;inset:0;background:#f0e8d9;transform:scaleX(1.012)}.torn-image{filter:contrast(1.08)}.black{background:#080b13}.fx-lightning{filter:drop-shadow(0 0 8px #72c7ed)}.accent-light{z-index:150;pointer-events:none;mix-blend-mode:screen;background:#c9e9ff;opacity:0}.foreground{pointer-events:none}'''+css+layout_css
    doc=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>{escape(plan['title'])}</title><script src="assets/gsap.min.js"></script><style>{style}</style></head><body><main id="root" data-composition-id="jjk-edge" data-start="0" data-duration="{sec(last-first)}" data-width="1920" data-height="1080" data-fps="{fps}" data-layout-allow-overlap="true">{''.join(layers)}</main><script>window.__timelines=window.__timelines||{{}};const tl=gsap.timeline({{paused:true}});{''.join(anim)}window.__timelines['jjk-edge']=tl;</script></body></html>'''
    return doc,needed,copies
if __name__=='__main__':save_editable(build(load_edit())[0]);print('Generated V17 + V02 editable composition')
