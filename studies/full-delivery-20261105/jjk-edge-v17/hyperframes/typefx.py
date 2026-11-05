"""V02-observed type vocabulary, adapted for 1920x1080 JJK edit.

type_layers(events, fps, first, last) returns (HTML, CSS, GSAP statement list).
All frame intervals are [start, end), global output frames; first/last crop a
render chunk. Returned times are local to first. Parent owns `tl`, registration,
font bundling and foreground alpha. No media is embedded.
"""
import html
import json
import math
import re

CSS = r'''
.v02-type{position:absolute;inset:0;overflow:hidden;pointer-events:none;isolation:isolate}
.v02-type .tf-stage{position:relative;z-index:1;display:flex;width:100%;height:100%;padding:110px 120px;box-sizing:border-box;align-items:center;justify-content:center;flex-direction:column;gap:5px}
.v02-type .tf-line{flex-shrink:0;white-space:nowrap;text-align:center;line-height:.96;font-family:"JJK Heavy",sans-serif;font-weight:900;letter-spacing:-.055em;transform-origin:50% 50%;paint-order:stroke fill;will-change:transform,opacity}
.v02-type .tf-board{position:absolute;inset:0;z-index:0;background:var(--board)}
.v02-type .tf-board:before,.v02-type .tf-board:after{content:"";position:absolute;left:0;right:0;height:92px;background-color:var(--edge);background-image:radial-gradient(#100d19 1.5px,transparent 1.8px);background-size:9px 9px}
.v02-type .tf-board:before{top:0}.v02-type .tf-board:after{bottom:0}
.v02-type .tf-plain{color:var(--ink);-webkit-text-stroke:var(--stroke-width) var(--stroke);text-shadow:9px 6px 0 var(--depth)}
.v02-type .tf-slam .tf-line{font-size:330px}
.v02-type .tf-twin .tf-line{font-size:252px}
.v02-type .tf-ribbon .tf-line{font-size:480px;letter-spacing:-.065em}
.v02-type .tf-striped{color:var(--ink);-webkit-text-stroke:8px var(--stroke);text-shadow:9px 6px 0 var(--depth)}
@supports (-webkit-background-clip:text){.v02-type .tf-striped{background:repeating-linear-gradient(110deg,var(--ink) 0,var(--ink) 5px,var(--stripe) 5px,var(--stripe) 8px);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}}
.v02-type .tf-orbit .tf-line{font-size:390px}
.v02-type .tf-ghost{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;opacity:.33;transform-origin:50% 50%;will-change:transform,opacity}
.v02-type .tf-orbit-body{position:relative;display:flex;align-items:center;justify-content:center;perspective:1100px}
'''

def _ease(p):
    p=max(0.0,min(1.0,p)); return 1-(1-p)**3

def _mix(a,b,p): return a+(b-a)*p

def _states(mode, elapsed, duration):
    """Analytic poses sampled at output frame boundaries: seek/chunk independent."""
    entrance=min(.20,duration*.25)
    exit_d=min(.125,duration*.20)
    p=_ease(elapsed/entrance)
    out=max(0.0,min(1.0,(elapsed-duration+exit_d)/exit_d))
    alpha=1-out
    if mode=='twin':
        q=_ease((elapsed-.125)/entrance)
        return [dict(x=_mix(310,0,p)-out*100,y=-8,scaleX=_mix(.78,1,p),scaleY=_mix(1.5,1,p),opacity=alpha),
                dict(x=_mix(-420,0,q)+out*100,y=8,scaleX=_mix(.72,1,q),scaleY=_mix(1.45,1,q),opacity=alpha*min(1,max(0,(elapsed-.125)*24)))]
    if mode=='ribbon':
        drift=(elapsed/max(.001,duration))*(-180)
        return [dict(x=_mix(420,0,p)+drift,y=0,scaleX=_mix(.58,.9,p),scaleY=_mix(1.5,1,p),opacity=alpha)]
    if mode=='orbit':
        # CSS 3D squeeze and finite ghost arcs are an equivalent adaptation,
        # not a claim to reconstruct the source's nonlinear glyph warp.
        return [dict(x=0,y=0,scaleX=_mix(2.0,.78,p),scaleY=_mix(1.75,1,p),rotationY=_mix(58,0,p),rotation=_mix(-9,0,p),opacity=alpha),
                dict(x=_mix(-260,-14,p),y=0,scaleX=_mix(1.6,1,p),rotation=_mix(-24,0,p),opacity=(1-p)*.5),
                dict(x=_mix(260,14,p),y=0,scaleX=_mix(1.6,1,p),rotation=_mix(24,0,p),opacity=(1-p)*.5)]
    # white on black/red extruded condensed first beat in F0-F3 vocabulary.
    # Small overshoot then settle instead of a loop.
    sx=_mix(.22,1.08,_ease(elapsed/.083333)) if elapsed<.083333 else _mix(1.08,1,_ease((elapsed-.083333)/.083333))
    return [dict(x=out*220,y=0,scaleX=sx,scaleY=_mix(1.65,1,p),rotation=0,opacity=alpha)]

def type_layers(events, fps, first, last):
    """Render 4 finite modes: slam, twin, ribbon, orbit.

    Event schema: start/end (integer global frames), text (string or 2-item
    list), mode, id (optional), color/stroke/depth/stripe, font_size,
    board (bool), board_color/edge_color, z (default 40), track (default 80+i).
    Parent should place matching moving foreground alpha at z > event.z.
    Fonts are a single explicit bold Chinese family, configurable `font`.
    """
    if fps<=0 or last<=first: raise ValueError('fps>0 and last>first required')
    parts=[]; js=[]
    for i,e in enumerate(events):
        start=int(e.get('start',e.get('first',0))); end=int(e.get('end',e.get('last',0)))
        a=max(start,int(first)); b=min(end,int(last))
        if b<=a: continue
        mode=e.get('mode','slam')
        if mode not in ('slam','twin','ribbon','orbit'): raise ValueError('unknown type mode: '+mode)
        uid='v02-'+re.sub('[^a-zA-Z0-9_-]','_',str(e.get('id',i)))
        raw=e.get('text','最强')
        lines=list(raw) if isinstance(raw,(list,tuple)) else [str(raw)]
        if mode=='twin': lines=(lines+[lines[0]])[:2]
        else:lines=lines[:1]
        defaults=({'color':'#34135f','stroke':'#f5f3f0','depth':'#a800c8'} if mode in ('twin','orbit') else
                  {'color':'#fffaf0','stroke':'#100d19','depth':'#bb141a'} if mode=='slam' else
                  {'color':'#100d19','stroke':'#b30918','depth':'#100d19'})
        v={k:str(e.get(k,x)) for k,x in defaults.items()}
        v['stripe']=str(e.get('stripe','#e2253a'))
        board_color=str(e.get('board_color','#7bbbd4' if mode in ('twin','orbit') else '#efb62e'))
        edge_color=str(e.get('edge_color','#34135f' if mode in ('twin','orbit') else '#c61120'))
        # All style values are trusted project events, escaped for safe HTML.
        style=';'.join([f'--ink:{v["color"]}',f'--stroke:{v["stroke"]}',f'--depth:{v["depth"]}',f'--stripe:{v["stripe"]}',
                        f'--stroke-width:{float(e.get("stroke_width",5))}px',f'--board:{board_color}',f'--edge:{edge_color}',f'z-index:{int(e.get("z",40))}'])
        parts.append(f'<div id="{uid}" class="clip v02-type" data-start="{(a-first)/fps:.9f}" data-duration="{(b-a)/fps:.9f}" data-track-index="{int(e.get("track",80+i))}" style="{html.escape(style,quote=True)}">')
        if e.get('board',False):parts.append('<div class="tf-board"></div>')
        parts.append(f'<div class="tf-stage tf-{mode}">')
        selectors=[]
        for j,line in enumerate(lines):
            child=f'{uid}-line{j}';selectors.append('#'+child)
            # Deterministic conservative CJK width estimate; final letterform
            # remains the local bold font. Normal titles stay inside x=120..1800.
            # Ribbon can intentionally crop only with crop=True.
            units=sum(1 if ord(ch)>127 else .66 for ch in str(line))
            default_size={'slam':330,'twin':252,'ribbon':480,'orbit':390}[mode]
            size=float(e.get('font_size',default_size))
            if not e.get('crop',False):size=min(size,1500/max(1,units))
            opt=f'font-size:{size}px;'
            if e.get('font'):opt+='font-family:'+str(e['font'])+';'
            cls='tf-striped' if mode=='ribbon' else 'tf-plain'
            if mode=='orbit':parts.append('<div class="tf-orbit-body">')
            parts.append(f'<div id="{child}" class="tf-line {cls}" style="{html.escape(opt,quote=True)}">{html.escape(str(line))}</div>')
            if mode=='orbit':
                for g in (1,2):
                    gid=f'{uid}-ghost{g}';selectors.append('#'+gid)
                    parts.append(f'<div id="{gid}" class="tf-ghost"><div class="tf-line {cls}" aria-hidden="true">{html.escape(str(line))}</div></div>')
                parts.append('</div>')
        parts.append('</div></div>')
        # Finite one-frame linear tweens capture the analytic cubic motion.
        # Starts inside an event use its true global elapsed pose, never restart.
        for f in range(a,b):
            states=_states(mode,(f-start)/fps,(end-start)/fps)
            t=(f-first)/fps
            for selector,state in zip(selectors,states):
                if f==a:
                    js.append(f'tl.set({json.dumps(selector)},{json.dumps(state,separators=(",",":"))},{t:.9f});')
                if f+1<b:
                    nxt=_states(mode,(f+1-start)/fps,(end-start)/fps)[selectors.index(selector)]
                    nxt.update(duration=1/fps,ease='none',immediateRender=False)
                    js.append(f'tl.to({json.dumps(selector)},{json.dumps(nxt,separators=(",",":"))},{t:.9f});')
    return '\n'.join(parts),CSS,js
