"""Editable HyperFrames composition. All rendering uses the same layer geometry.
Preview uses videos; deterministic offline export substitutes same-frame PNGs.
"""
from pathlib import Path
from html import escape
import json, math, hashlib
ROOT=Path(__file__).resolve().parent
def load_edit():return json.loads((ROOT/'edit.json').read_text(encoding='utf-8'))
def save_editable(html):
    target=ROOT/'index.html';sig=ROOT/'generated-index.sha256'
    if target.exists() and sig.exists() and hashlib.sha256(target.read_bytes()).hexdigest()!=sig.read_text().strip():
        old=hashlib.sha256(target.read_bytes()).hexdigest()[:12]
        backups=ROOT/'.source-backups';backups.mkdir(exist_ok=True)
        (backups/f'index-studio-{old}.html.bak').write_bytes(target.read_bytes())
    target.write_text(html,encoding='utf-8');sig.write_text(hashlib.sha256(html.encode()).hexdigest())
def ease(p):return 1-(1-max(0,min(1,p)))**3
def build(plan,first=0,last=None,frame_mode=False):
    last=plan['durationFrames'] if last is None else last;fps=plan['fps'];needed=set();copies=set();anim=[];layers=[]
    A={a['id']:a for a in plan['assets']};sec=lambda f:f'{f/fps:.9f}'
    overlap=lambda a,b:a<last and b>first
    def media(tag,id,start,end,offset=12,track=0):
        a,b=max(first,start),min(last,end)
        if a>=b:return ''
        if frame_mode:
            out=[]
            for f in range(a,b):
                n=offset+f-start;needed.add((id,n))
                out.append(f'<img class="clip source" id="{tag}-{f}" src="assets/frames/{id}-{n:03}.png" data-start="{sec(f-first)}" data-duration="{sec(1)}" data-track-index="{track}" data-layout-allow-overlap="true">')
            return ''.join(out)
        return f'<video class="clip source" id="{tag}" src="{A[id]["asset"]}" muted playsinline preload="metadata" data-start="{sec(a-first)}" data-duration="{sec(b-a)}" data-media-start="{sec(offset+a-start)}" data-volume="0" data-track-index="{track}" data-layout-allow-overlap="true"></video>'
    def alpha(tag,id,start,end,count,track=2,freeze=False):
        items=[]
        for f in range(max(first,start),min(last,end)):
            n=min(count-1,f-start) if freeze else f-start
            uri=f'assets/alpha/{id}/{n:06}.png';copies.add(uri)
            items.append(f'<img class="clip source" id="{tag}-{f}" src="{uri}" data-start="{sec(f-first)}" data-duration="{sec(1)}" data-track-index="{track}" data-layout-allow-overlap="true">')
        return ''.join(items)
    def setat(id,f,props):anim.append(f'tl.set({json.dumps("#"+id)},{json.dumps(props)},{sec(f-first)});')
    base=''.join(media(s['id'],s['assetId'],s['startFrame'],s['startFrame']+s['frames'],s['assetStartFrame']) for s in plan['shots'])
    layers.append(f'<div id="footage" class="plane">{base}</div>')
    # Local camera accelerations: brief, directed toward the action, with no persistent blur.
    motions={16:(1.16,-1,1),45:(1.22,2,2),56:(1.18,-2,1),67:(1.52,4,4),97:(1.4,-4,3),119:(1.16,0,2),176:(1.12,-2,2),218:(1.35,0,2),256:(1.24,2,2),267:(1.22,-2,2),278:(1.2,0,2),294:(1.65,7,3),316:(1.38,-5,3),342:(1.2,1,3),378:(1.12,0,1),418:(1.18,-2,2),427:(1.25,3,2),451:(1.45,-6,4),477:(1.5,6,5),501:(1.45,-5,4),524:(1.55,7,4),550:(1.3,-3,3),617:(1.8,8,5),639:(1.3,-3,2)}
    for f in range(first,last):
        zoom=1;rot=0;blur=0;x=0;origin='50% 50%'
        if f<16:zoom=1.36-.36*ease(f/15);origin='50% 38%'
        for cut,(z,r,b) in motions.items():
            if cut<=f<cut+8:
                k=1-ease((f-cut)/7);zoom=max(zoom,1+(z-1)*k);rot=r*k;blur=b*k
        # Zoom into a turning wheel immediately before its movement matches the next front-facing car.
        if 308<=f<316:
            k=((f-308)/7)**2;zoom=1+.9*k;origin='48% 63%';blur=2*k
        setat('footage',f,{'scale':round(zoom,5),'rotation':round(rot,4),'filter':f'blur({blur:.3f}px)','transformOrigin':origin})
    # Eight film-image wedges spiral into the explosion; the identical source continues underneath.
    if overlap(67,87):
        for i in range(8):
            theta1=2*math.pi*i/8;theta2=2*math.pi*(i+1)/8
            pts=[(50,50),(50+150*math.cos(theta1),50+150*math.sin(theta1)),(50+150*math.cos(theta2),50+150*math.sin(theta2))]
            clip='polygon('+','.join(f'{x:.3f}% {y:.3f}%' for x,y in pts)+')'
            body=media(f'prism-{i}','P05',67,87,12,1)
            layers.append(f'<div id="wedge-{i}" class="plane wedge" style="clip-path:{clip}"><div id="shard-{i}" class="plane">{body}</div></div>')
            for f in range(max(first,67),min(last,87)):
                p=ease((f-67)/19)
                setat(f'shard-{i}',f,{'scale':1+.65*(1-p),'rotation':(i%2*2-1)*(40+i*12)*(1-p),'filter':f'blur({2*(1-p):.2f}px)'})
        for f in range(max(first,67),min(last,87)):
            for i in range(8):setat(f'wedge-{i}',f,{'visibility':'visible','opacity':1 if f<83 else (87-f)/4})
        if first<87<last:
            for i in range(8):setat(f'wedge-{i}',87,{'visibility':'hidden'})
    # Foreground-first transitions, real moving alpha with a strict shared source clock.
    alpha_dirs={'B01-steering':'B01-steering-hand','B02-wheel':'B02-wheel','B03-switch':'B03-switch-hand','B04-gear':'B04-gear-hand','B05-aircar':'B05-aircar'}
    for e in plan['effects']:
        if e['kind']!='alpha' or not overlap(e['start'],e['reveal']):continue
        tag='alpha-'+e['id'];body=alpha(tag,alpha_dirs[e['assetId']],e['start'],e['reveal'],A[e['assetId']]['frames'])
        layers.append(f'<div id="{tag}" class="plane foreground">{body}</div>')
        for f in range(max(first,e['start']),min(last,e['reveal'])):
            p=ease((f-e['start'])/max(1,e['reveal']-e['start']-1));q=1-p
            setat(tag,f,{'x':e['x']*q,'y':e['y']*q,'scale':1+(e['scale']-1)*q,'rotation':e['rotation']*q,'transformOrigin':'58% 0%' if e['id']=='wheel' else '50% 50%','filter':f'drop-shadow(0px 0px {2*q:.2f}px rgba(190,225,255,{.5*q:.3f}))'})
    # Four-corner tracked window portal. Matrices are calculated from the real side-window keyframes.
    portal_file=ROOT/'motion/portal-matrices.json'
    if overlap(665,674) and portal_file.exists():
        frames=json.loads(portal_file.read_text(encoding='utf-8'))['frames']
        old=media('window-old','A06-sidewindow',665,674,12+665-639,3)
        new=media('window-new','P23',665,674,12,4)
        layers.append(f'<div id="window-old-plane" class="plane projective">{old}</div><div id="window-new-plane" class="plane projective">{new}</div>')
        for m in frames:
            f=m['frame']
            if first<=f<last:
                # A general planar homography cannot safely pass through GSAP's
                # transform decomposition. A CSS custom property preserves all 16 entries.
                setat('window-old-plane',f,{'--portal-matrix':m['outgoingCss']})
                setat('window-new-plane',f,{'--portal-matrix':m['incomingCss']})
    # Brief light transitions at the matched action peaks, not a repeated cut preset.
    layers.append('<div id="light" class="plane light"></div>')
    for f in range(first,last):
        opacity=0
        for peak,span,amount in [(67,4,.23),(341,5,.33),(705,4,.55)]:
            opacity=max(opacity,amount*max(0,1-abs(f-peak)/span))
        setat('light',f,{'opacity':opacity})
    # Final hand continues the reference gesture motif, then becomes a glowing edge on black.
    if overlap(691,750):
        hand=alpha('closing','B04-gear-hand',691,737,13,5,True)
        layers.append(f'<div id="closing-hand" class="plane foreground">{hand}</div><div id="last-glint" class="glint"></div>')
        for f in range(max(first,691),min(last,750)):
            entry=ease((f-691)/12);tail=max(0,(f-705)/31);opacity=max(0,1-tail**1.4)
            setat('closing-hand',f,{'x':-150*(1-entry),'y':300*(1-entry)+100*tail,'rotation':-20*(1-entry)+10*tail,'scale':1.3-.3*entry+.1*tail,'opacity':opacity,'filter':f'brightness({1+max(0,1-abs(f-705)/3)*2:.3f}) drop-shadow(0 0 {2+8*tail:.2f}px rgba(170,210,255,.6))'})
            light=max(0,1-abs(f-723)/13)**3
            setat('last-glint',f,{'opacity':light*.65,'scale':.4+light*.6})
    if not frame_mode:layers.append(f'<audio id="library-music" src="{plan["audio"]["master"]}" data-start="0" data-duration="30" data-volume="1" data-track-index="8"></audio>')
    style='''*{box-sizing:border-box}html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:black}#root{position:relative;width:1920px;height:1080px;background:black}#active{position:absolute;left:0;top:140px;width:1920px;height:800px;overflow:hidden;background:black}.plane{position:absolute;inset:0;width:1920px;height:800px;transform-origin:50% 50%}.source{position:absolute;left:0;top:-140px;width:1920px;height:1080px;object-fit:fill}.wedge{visibility:hidden}.projective{transform-origin:0 0}.light{background:#d9e9ff;opacity:0;mix-blend-mode:screen;pointer-events:none}.glint{position:absolute;left:1030px;top:190px;width:260px;height:6px;opacity:0;background:radial-gradient(ellipse,#fff 0%,#94d8ff 9%,rgba(180,230,255,.2) 42%,transparent 75%);filter:blur(2px);transform-origin:center}.foreground{pointer-events:none}'''
    style+='#footage,.wedge>div,.projective{overflow:hidden}.projective{transform:var(--portal-matrix,matrix(1,0,0,1,0,0))}'
    doc=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>{escape(plan['title'])}</title><script src="assets/gsap.min.js"></script><style>{style}</style></head><body><main id="root" data-composition-id="v07" data-start="0" data-duration="{sec(last-first)}" data-width="1920" data-height="1080" data-fps="25" data-layout-allow-overlap="true"><div id="active">{''.join(layers)}</div></main><script>window.__timelines=window.__timelines||{{}};const tl=gsap.timeline({{paused:true}});{''.join(anim)}tl.to({{}},{{duration:{sec(last-first)}}},0);window.__timelines.v07=tl;</script></body></html>'''
    return doc,needed,copies
if __name__=='__main__':
    save_editable(build(load_edit())[0]);print('Updated editable HyperFrames index.html')
