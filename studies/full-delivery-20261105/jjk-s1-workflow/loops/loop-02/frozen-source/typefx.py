"""V02 native-frame typography replay, v2. Editable SVG and continuous outline warp.

Frame intervals are global [start,end). Parent owns fonts, tl and foreground alpha.
No media, network, asynchronous construction, callbacks or playback clock.
"""
import html
import json
import math
import re
from pathlib import Path
from functools import lru_cache

CSS = r'''
.v02-type{position:absolute;inset:0;overflow:hidden;pointer-events:none;isolation:isolate}
.v02-type svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.v02-type path,.v02-type use{paint-order:stroke fill;stroke-linejoin:round}
.v02-type text{font-family:"Barlow Condensed",sans-serif;font-weight:800;letter-spacing:-.018em;paint-order:stroke fill;stroke-linejoin:round}
.v02-type .tf-note{font-family:"JJK Heavy",sans-serif;font-size:31px;letter-spacing:.16em;font-weight:900;paint-order:stroke fill;stroke:#080b13;stroke-width:6px;fill:#fffaf0}
.v02-type .tf-credit{font-family:"Barlow Condensed",sans-serif;font-size:24px;letter-spacing:.20em;fill:#fffaf0;stroke:#080b13;stroke-width:3px}
'''

def _clamp(x):return min(1.,max(0.,x))
def _ease(x):return 1-(1-_clamp(x))**3
def _mix(a,b,p):return a+(b-a)*p
def _fmt(x):return f'{x:.5f}'
def _j(x):return json.dumps(x,separators=(',',':'))
def _esc(x):return html.escape(str(x),quote=True)
def _matrix(m):return 'matrix('+','.join(_fmt(x) for x in m)+')'

@lru_cache(maxsize=64)
def _outlines(text,width,size):
    """Preflattened original font, build-time only. No external Python package."""
    data=json.loads(Path(__file__).with_name('barlow-glyphs.json').read_text(encoding='utf-8'))
    glyphs=data['glyphs'];upem=data['unitsPerEm'];factor=size/upem
    if any(c not in glyphs for c in text):raise ValueError('Nonlinear modes require Barlow ASCII; place Chinese in subtitle')
    advance=sum(glyphs[c]['advance']*factor-size*.018 for c in text)+size*.018
    stretch=width/max(1,advance);pen=0;out=[]
    for c in text:
        glyph=glyphs[c]
        for contour in glyph['contours']:
            out.append([((pen+x*factor)*stretch,200-y*factor) for x,y in contour])
        pen+=glyph['advance']*factor-size*.018
    return out

def _warped_path(contours,mode,t,duration,e):
    w=float(e.get('width',1600));parts=[]
    for contour in contours:
        for i,(x,y) in enumerate(contour):
            # Continuous surface evaluated at every outline point; no clipping
            # seams. This is the same 32-strip surface sampled analytically.
            m,_=_pose(mode,t,duration,x/w*32-.5,32,0,e,y)
            parts.append(('M' if i==0 else 'L')+f'{m[4]:.2f},{m[5]:.2f}')
        parts.append('Z')
    return ''.join(parts)

def _source(uid,text,e,mode,path_ref=None):
    purple=mode in ('twin','orbit','cylinder')
    color=e.get('color','#34135f' if purple else '#fffaf0' if mode=='slam' else '#080b13')
    stroke=e.get('stroke','#e9f5fc' if mode=='twin' else '#ae0718' if mode=='orbit' else '#080b13')
    depth=e.get('depth','#b517c6' if purple else '#ab0716')
    size=float(e.get('font_size',560))
    # Width is an explicit art-direction value; SVG textLength remains editable.
    width=float(e.get('width',1600))
    font=e.get('font','Barlow Condensed')
    editable=f'<text x="0" y="200" textLength="{width}" lengthAdjust="spacingAndGlyphs" font-size="{size}" style="font-family:{_esc(font)}">{_esc(text)}</text>'
    txt=f'<use href="#{path_ref}"/>' if path_ref else editable
    p=[f'<g id="{uid}-source" aria-label="{_esc(text)}">']
    for k in range(9,0,-1):
        fill=depth if k>2 else '#f7d4ff' if purple else '#ed6471'
        p.append(f'<g transform="translate({k*2.4:.2f},{k*1.4:.2f})" fill="{fill}" stroke="{stroke}" stroke-width="{float(e.get("stroke_width",5))+3:.2f}">{txt}</g>')
    p.append(f'<g fill="{_esc(color)}" stroke="{_esc(stroke)}" stroke-width="{float(e.get("stroke_width",5))}">{txt}</g>')
    if mode=='ribbon':
        p.append(f'<g fill="url(#{uid}-stripe)" stroke="none">{txt}</g>')
    elif mode=='orbit':
        p.append(f'<g fill="url(#{uid}-dot)" stroke="none" opacity=".32">{txt}</g>')
    # Fine inset highlight, rather than one CSS shadow used as a fake extrusion.
    p.append(f'<g transform="translate(-1.2,-1.2)" fill="none" stroke="#fffaf0" stroke-width="1.2" opacity=".60">{txt}</g></g>')
    if path_ref:p.append(f'<g id="{uid}-editable-source">{editable}</g>')
    return ''.join(p),width

def _board(uid,e,mode):
    cold=mode in ('twin','orbit','cylinder')
    base=e.get('board_color','#79b8d5' if cold else '#f0b72d')
    edge=e.get('edge_color','#34135f' if cold else '#cc1021')
    # Imperfect ink contours and slanted press-print dots follow the reference's
    # comic board; they are deliberately neither generic rounded cards nor grids.
    return f'''<g id="{uid}-board"><path fill="{base}" d="M0 0H1920V1080H0Z"/>
<path fill="url(#{uid}-paper)" opacity=".20" d="M0 0H1920V1080H0Z"/>
<path fill="{edge}" stroke="#080b13" stroke-width="8" d="M-12-10H1932V100L1620 96 1400 105 1160 98 940 107 680 99 430 110 200 101-12 111Z M-12 982L180 972 420 985 650 976 900 988 1160 978 1420 986 1680 974 1932 982V1090H-12Z"/>
<path fill="url(#{uid}-edge)" d="M0 0H1920V103L1500 100 1000 106 500 103 0 110Z M0 980L500 979 1000 984 1500 981 1920 979V1080H0Z"/>
<path d="M-40 167Q220 132 405 148M1550 911Q1715 897 1950 924" fill="none" stroke="#080b13" stroke-width="8"/>
<path d="M-40 178Q220 143 405 159M1550 900Q1715 886 1950 913" fill="none" stroke="#fffaf0" stroke-width="3" opacity=".75"/></g>'''

def _pose(mode,t,duration,index,count,line,e,row_y=0):
    """Affine tangent patches of a genuinely nonlinear 2D surface.

    Source strip center x is mapped independently; a single rotationY is never
    used. Matrix columns are surface derivatives at each strip center.
    """
    w=float(e.get('width',1600)); sw=w/count
    u=(index+.5)/count; q=2*u-1; src=q*w*.5
    p=_ease(t/.17)
    cx=float(e.get('x',960));cy=float(e.get('y',525))
    sx=float(e.get('scale_x',1));sy=float(e.get('scale_y',1))
    if mode=='slam':
        # F0 tall/thin, F2 wide, F3 tall again: intentional ratio snap.
        if t<2/24:compress=_mix(.21,1.07,_ease(t/(2/24)))
        elif t<4/24:compress=_mix(1.07,.94,_ease((t-2/24)/(2/24)))
        else:compress=.94
        stretch=_mix(1.72,1.08,p)
        bend=.16*(1-p)
        theta=q*.9
        m=[compress*math.cos(theta*bend), .10*q*(1-p),0,stretch,cx+src*compress,cy+36*q*q*(1-p)]
    elif mode=='twin':
        delay=float(e.get('line_delay',.125))*line
        pp=_ease((t-delay)/.21)
        direction=1 if line==0 else -1
        xx=direction*450*(1-pp)+direction*(-32)*_clamp(t/max(duration,.001))
        yy=(-204 if line==0 else 207)
        compress=_mix(.55,.97,pp)
        m=[compress,0,0,_mix(1.5,.91,pp),cx+src*compress+xx,cy+yy]
        if t<delay:return m,0
    elif mode=='ribbon':
        compress=_mix(.45,1.04,p)
        drift=-140*_clamp(t/max(duration,.001))
        theta=q*.8
        m=[compress*(.88+.12*math.cos(theta)),.11*math.sin(theta),0,1.58-.18*math.cos(theta),cx+src*compress+260*(1-p)+drift,cy-20*math.cos(theta)]
    else:
        # Full ring at the hit -> five-frame unroll -> tall, compressed cylinder.
        ring=1-_ease(t/(5/24)) if mode=='orbit' else .0
        if e.get('ring_exit',True) and mode=='orbit':
            ring=max(ring,_ease((t-duration+4/24)/(4/24)))
        theta=q*1.15
        narrow=_mix(.58,1.02,p)
        # Front face is wider than the ends. Bow + local shear bends glyphs.
        dy=1.24-.22*math.cos(theta)
        linear=[narrow*math.cos(theta),(89+.22*row_y)*math.sin(theta)*1.15/(w*.5),0,dy,cx+math.sin(theta)*(w*.5*narrow/1.15),cy+89*(1-math.cos(theta))+dy*row_y]
        ang=(u-.5)*math.tau*.95 + float(e.get('ring_phase',0))
        rx=float(e.get('ring_radius_x',570));ry=float(e.get('ring_radius_y',330))
        da=math.tau*.95/w
        # Ring local y follows the outward normal, local x follows the tangent.
        circ=[(rx+.53*row_y)*math.cos(ang)*da,(ry+.53*row_y)*math.sin(ang)*da,math.sin(ang)*.53,-math.cos(ang)*.53,cx+(rx+.53*row_y)*math.sin(ang),cy-(ry+.53*row_y)*math.cos(ang)]
        m=[_mix(a,b,ring) for a,b in zip(linear,circ)]
    if mode not in ('orbit','cylinder'):
        m[4]+=m[2]*row_y;m[5]+=m[3]*row_y
    m[0]*=sx;m[1]*=sy;m[2]*=sx;m[3]*=sy
    m[4]=cx+(m[4]-cx)*sx;m[5]=cy+(m[5]-cy)*sy
    if e.get('pulse',True):
        pulse=0.;jitter=0.
        for frac,amp in ((.40,.025),(.73,.018)):
            age=t-duration*frac
            if 0<=age<.24:
                pulse+=amp*math.sin(age/.24*math.pi*2)*math.exp(-age*7)
                jitter+=5*math.sin(age*math.pi*24)*math.exp(-age*13)
        for n in (0,2):m[n]*=1+pulse
        for n in (1,3):m[n]*=1-pulse*.45
        m[4]=cx+(m[4]-cx)*(1+pulse)+jitter
        m[5]=cy+(m[5]-cy)*(1-pulse*.45)
    # An explicit finite hold survives arbitrary 72-frame render chunk starts.
    return m,1

def type_layers(events,fps,first,last):
    """Return HTML,CSS,GSAP-list. Modes: slam,twin,ribbon,orbit,cylinder.

    Core keys: id,start,end,text,mode,font_size,width,subtitle,board,z,track.
    x/y move the center; scale_x/y art-direct local glyph dimensions. Continuous
    nonlinear outline is default (optional geometry=slices is a legacy mesh).
    English main text + small Chinese semantic subtitle.
    The parent places moving character alpha at z > event.z.
    """
    if fps<=0 or last<=first:raise ValueError('fps>0 and last>first required')
    out=[];anim=[]
    for i,e in enumerate(events):
        start=int(e.get('start',e.get('first',0)));end=int(e.get('end',e.get('last',0)))
        a=max(start,int(first));b=min(end,int(last))
        if b<=a:continue
        mode=e.get('mode','slam')
        if mode not in ('slam','twin','ribbon','orbit','cylinder'):raise ValueError(mode)
        uid='v02v2-'+re.sub('[^a-zA-Z0-9_-]','_',str(e.get('id',i)))
        raw=e.get('text','THE STRONGEST')
        lines=list(raw) if isinstance(raw,(list,tuple)) else [str(raw)]
        lines=(lines+[lines[0]])[:2] if mode=='twin' else lines[:1]
        count=int(e.get('slices',32));count=max(24,min(40,count))
        if mode in ('slam','twin'):count=1
        rows=6 if mode in ('orbit','cylinder') else 1
        body=[];defs=[f'''<pattern id="{uid}-paper" patternUnits="userSpaceOnUse" width="9" height="9" patternTransform="rotate(-12)"><circle cx="2" cy="2" r="1.25" fill="#080b13"/></pattern>
<pattern id="{uid}-edge" patternUnits="userSpaceOnUse" width="13" height="13" patternTransform="rotate(36)"><rect x="0" y="0" width="5" height="5" fill="#080b13"/></pattern>''']
        selectors=[]
        path_selectors=[]
        for li,line in enumerate(lines):
            lid=f'{uid}-l{li}'
            continuous=mode in ('orbit','cylinder','ribbon') and e.get('geometry','outline')=='outline'
            if continuous:
                contours=_outlines(str(line),float(e.get('width',1600)),float(e.get('font_size',560)))
                pid=f'{lid}-warp'
                d=_warped_path(contours,mode,(a-start)/fps,(end-start)/fps,e)
                defs.append(f'<path id="{pid}" d="{d}"/>')
                source,w=_source(lid,line,e,mode,pid)
                path_selectors.append((pid,contours))
            else:source,w=_source(lid,line,e,mode)
            defs.append(source)
            defs.append(f'<pattern id="{lid}-stripe" patternUnits="userSpaceOnUse" width="12" height="12" patternTransform="rotate(22)"><path d="M0 0V12M6 0V12" stroke="#d51b2d" stroke-width="2.2"/></pattern><pattern id="{lid}-dot" patternUnits="userSpaceOnUse" width="11" height="11"><circle cx="3" cy="3" r="2.5" fill="#080b13"/></pattern>')
            if continuous:
                body.append(f'<use href="#{lid}-source"/>')
                continue
            sw=w/count
            for row in range(rows):
                rh=600/rows;ry=-300+(row+.5)*rh if rows>1 else 0
                for n in range(count):
                    cid=f'{lid}-clip{n}r{row}';sid=f'{lid}-s{n}r{row}'
                    # Three source pixels of overlap suppress SVG clip AA seams.
                    defs.append(f'<clipPath id="{cid}" clipPathUnits="userSpaceOnUse"><rect x="{-sw/2-3:.5f}" y="{-rh/2-3 if rows>1 else -390:.5f}" width="{sw+6:.5f}" height="{rh+6 if rows>1 else 800:.5f}"/></clipPath>')
                    m,alpha=_pose(mode,(a-start)/fps,(end-start)/fps,n,count,li,e,ry)
                    body.append(f'<g id="{sid}" transform="{_matrix(m)}" opacity="{alpha}"><g clip-path="url(#{cid})"><use href="#{lid}-source" transform="translate({-(n+.5)*sw:.5f},{-ry:.5f})"/></g></g>')
                    selectors.append((sid,n,li,ry))
        subtitle=e.get('subtitle',{'slam':'最强 · 五条悟','twin':'唯一的挚友','ribbon':'失控的边缘','orbit':'无下限','cylinder':'无下限'}.get(mode,''))
        if subtitle:body.append(f'<text id="{uid}-note" class="tf-note" opacity="{_ease((a-start)/4):.5f}" transform="translate(0,{18*(1-_ease((a-start)/4)):.5f})" x="960" y="{float(e.get("subtitle_y",947))}" text-anchor="middle">{_esc(subtitle)}</text>')
        out.append(f'<div id="{uid}" class="clip v02-type" data-start="{(a-first)/fps:.9f}" data-duration="{(b-a)/fps:.9f}" data-track-index="{int(e.get("track",80+i))}" style="z-index:{int(e.get("z",40))}"><svg viewBox="0 0 1920 1080" aria-label="{_esc(" / ".join(lines))}" xmlns="http://www.w3.org/2000/svg"><defs>{"".join(defs)}</defs>{_board(uid,e,mode) if e.get("board",False) else ""}{"".join(body)}</svg></div>')
        for sid,n,li,ry in selectors:
            prev=None
            for f in range(a,b):
                m,alpha=_pose(mode,(f-start)/fps,(end-start)/fps,n,count,li,e,ry)
                state={'attr':{'transform':_matrix(m)},'opacity':alpha}
                # Exact frame states use set rather than clocks/callbacks. At
                # 24fps this also avoids interpolation crossing singular matrices.
                if prev!=state:anim.append(f'tl.set("#{sid}",{_j(state)},{(f-first)/fps:.9f});')
                prev=state
        for pid,contours in path_selectors:
            for f in range(a,b):
                d=_warped_path(contours,mode,(f-start)/fps,(end-start)/fps,e)
                anim.append(f'tl.set("#{pid}",{_j({"attr":{"d":d}})},{(f-first)/fps:.9f});')
        if subtitle:
            for f in range(a,min(b,start+5)):
                if f==a:continue # exact initial state is already authored in SVG
                pp=_ease((f-start)/4)
                anim.append(f'tl.set("#{uid}-note",{_j({"opacity":pp,"y":18*(1-pp)})},{(f-first)/fps:.9f});')
            if a>=start+5:anim.append(f'tl.set("#{uid}-note",{{"opacity":1,"y":0}},{(a-first)/fps:.9f});')
    return '\n'.join(out),CSS,anim
