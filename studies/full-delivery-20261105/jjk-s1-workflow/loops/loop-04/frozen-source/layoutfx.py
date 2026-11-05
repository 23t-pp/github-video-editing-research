"""Seekable V17 layout replay and explicitly original extra layouts.

All event times are absolute 24 fps output frames, end-exclusive. This module
owns geometry only: the caller owns source decoding, visibility and timeline.
Use layout_layers(events, plan, fps, first, last, media, setat) -> (html, css).
"""
from html import escape
import math

W,H=1920,1080

def clamp(v): return max(0.,min(1.,float(v)))
def out(v): return 1-(1-clamp(v))**3
def smooth(v):
    q=clamp(v)
    return q*q*(3-2*q)
def mix(a,b,p): return a+(b-a)*p
def rectpath(r):
    x,y,w,h=r
    return f'inset({y:.3f}px {W-x-w:.3f}px {H-y-h:.3f}px {x:.3f}px)'

def _tear_polygon(left,right,top,bottom,f,seed=17,rim=0):
    """Fine, asymmetric paper fibres; changes every 3 output frames, not noise."""
    points=[]
    # 92 short uneven edges replace the old 12 huge saw teeth.
    for side in (0,1):
        seq=range(93) if side==0 else range(92,-1,-1)
        for k in seq:
            y=mix(top,bottom,k/92)
            v=math.sin(k*7.17+seed)*2.2+math.sin(k*2.91+seed*.3)*2.7
            v+=math.sin(k*1.53+(f//3)*.23)*.65
            x=(left-rim-v) if side==0 else (right+rim+v*.83)
            points.append(f'{x:.2f}px {y:.2f}px')
    return 'polygon('+','.join(points)+')'

def _tear_edges(left,right,top,bottom,f,seed=17,rim=1.6):
    """Exactly the polygon's side samples, offset onto the visible paper rim."""
    edges=[]
    for side in (0,1):
        points=[]
        for k in range(93):
            y=mix(top,bottom,k/92)
            v=math.sin(k*7.17+seed)*2.2+math.sin(k*2.91+seed*.3)*2.7
            v+=math.sin(k*1.53+(f//3)*.23)*.65
            x=(left-rim-v) if side==0 else (right+rim+v*.83)
            points.append((x,y))
        edges.append(points)
    return edges

def _edge_path(edges):
    return ' '.join('M'+' L'.join(f'{x:.2f} {y:.2f}' for x,y in pts) for pts in edges)

def layout_layers(events,plan,fps,first,last,media,setat):
    """Return geometry markup and scoped CSS, emitting absolute-frame GSAP sets.

    Clip fields: assetId, offset (asset frame), optional start/end (global frame),
    transform={scale,x,y,rotation}. Offset always belongs to clip.start; chunk
    boundaries do not restart the source. Parent .plane/.source are supported.
    Event z is clamped to 10..35 so parent type/foreground ordering stays clear.
    """
    layers=[]
    def run(tag,st,en,fn):
        for f in range(max(first,st),min(last,en)):
            setat(tag,f,fn(f,(f-st)/max(1,en-st-1)))
    for index,e in enumerate(events):
        st,en=int(e['start']),int(e['end'])
        a,b=max(first,st),min(last,en)
        if a>=b: continue
        tag='layout-'+str(e.get('id',index));kind=e['kind']
        clips=e.get('clips',[]);z=max(10,min(35,int(e.get('z',20))))
        content=[]
        def source(j,extra='',class_name='',copy=None):
            c=clips[j];cs=int(c.get('start',st));ce=int(c.get('end',en))
            key=str(j) if copy is None else f'{j}-copy-{copy}'
            ct=f'{tag}-image-{key}';mt=f'{tag}-media-{key}'
            body=media(mt,c['assetId'],cs,ce,int(c.get('offset',12)),300+index*16+(j if copy is None else copy))
            transform=c.get('transform',{})
            if transform:
                run(ct,cs,ce,lambda f,p,t=transform:{
                    'scale':t.get('scale',1),'x':t.get('x',0),
                    'y':t.get('y',0),'rotation':t.get('rotation',0),
                    'transformOrigin':t.get('origin','50% 50%')})
            return f'<div id="{ct}" class="lf-plane {class_name}" style="{extra}">{body}</div>'
        if kind=='window_expand':
            # Content remains a full-size independent source. Only aperture grows.
            # This is deliberately not scale(.375)->scale(1) on a video card.
            content=[f'<div id="{tag}-aperture" class="lf-plane lf-aperture">'+source(0)+'</div>',
                     f'<div id="{tag}-frame" class="lf-frame"></div>']
            begin=e.get('rect',[100,610,440,280]);target=e.get('toRect',[0,0,W,H])
            r0=int(e.get('revealStart',st+3));r1=int(e.get('revealEnd',en-1))
            for f in range(a,b):
                p=smooth((f-r0)/max(1,r1-r0));r=[mix(x,y,p) for x,y in zip(begin,target)]
                setat(tag+'-aperture',f,{'clipPath':rectpath(r),'opacity':1})
                setat(tag+'-frame',f,{'left':r[0],'top':r[1],'width':r[2],
                    'height':r[3],'opacity':(1-p)*float(e.get('borderOpacity',.65))})
        elif kind=='tear_reveal':
            # Reference F154: strip ~17% width, x56..73%, y~16%..100%.
            left=float(e.get('left',1080));width=float(e.get('width',326))
            top=float(e.get('top',172));bottom=float(e.get('bottom',1080))
            content=[f'<div id="{tag}-rim" class="lf-plane lf-paper"></div>',
                     f'<div id="{tag}-tear" class="lf-plane">'+source(0)+'</div>']
            reveal=int(e.get('revealFrames',8));expand=int(e.get('expandStart',en))
            expandend=int(e.get('expandEnd',en));seed=int(e.get('seed',17))
            edge=e.get('edgeFx',False)
            edge_enabled=edge is not False and edge is not None
            if edge_enabled:
                edge=edge if isinstance(edge,dict) else {}
                cyan=escape(str(edge.get('cyan','#72c7ed')));violet=escape(str(edge.get('violet','#b517c6')))
                particles=max(0,min(24,int(edge.get('particles',14))))
                strength=float(edge.get('strength',1))
                content.append(f'''<svg class="lf-plane lf-edge-svg" viewBox="0 0 1920 1080" aria-hidden="true">
<defs><filter id="{tag}-wide" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="7"/></filter>
<filter id="{tag}-soft" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2"/></filter></defs>
<g id="{tag}-edge-energy" fill="none" stroke-linecap="round" stroke-linejoin="round">
<path id="{tag}-edge-violet" stroke="{violet}" stroke-width="16" filter="url(#{tag}-wide)" opacity=".7"/>
<path id="{tag}-edge-cyan" stroke="{cyan}" stroke-width="5" filter="url(#{tag}-soft)" opacity=".9"/>
<path id="{tag}-edge-core" stroke="#fffaf0" stroke-width="1" opacity=".9"/>
<path id="{tag}-edge-arc" stroke="{cyan}" stroke-width="2" stroke-dasharray="17 135 6 205"/>
<path id="{tag}-edge-white-arc" stroke="#e7fbff" stroke-width="2" stroke-dasharray="6 230 3 145" opacity=".8"/>
</g>''')
                for k in range(particles):
                    color='#fffaf0' if k%3 else cyan
                    length=6+(k%5)
                    content.append(f'<path id="{tag}-fiber-{k}" d="M{-length/2:.1f} 0L{length/2:.1f} -2" fill="none" stroke="{color}" stroke-width="{1+(k%3)*.3:.2f}"/>')
                content.append('</svg>')
            for f in range(a,b):
                q=out((f-st)/max(1,reveal));p=smooth((f-expand)/max(1,expandend-expand))
                center=left+width/2;half=width/2*q
                l=mix(center-half,0,p);r=mix(center+half,W,p)
                t=mix(top,0,p);bot=mix(bottom,H,p)
                setat(tag+'-tear',f,{'clipPath':_tear_polygon(l,r,t,bot,f,seed),
                    'opacity':q,'x':float(e.get('drift',0))*(1-q)})
                setat(tag+'-rim',f,{'clipPath':_tear_polygon(l,r,t-2.5,bot+2.5,f,seed,2.5),
                    'opacity':q*(1-p),'x':float(e.get('drift',0))*(1-q)})
                if edge_enabled:
                    # SVG takes the same polygon samples AND the same drift.
                    # Image and paper stay attached; energy alone moves along it.
                    edges=_tear_edges(l,r,t,bot,f,seed)
                    d=_edge_path(edges);drift=float(e.get('drift',0))*(1-q)
                    fade=q*(1-p)*clamp((en-1-f)/max(1,int(edge.get('exitFrames',5))))
                    pulse=.87+.13*math.sin(f*.71+seed)
                    for name in ('violet','cyan','core','arc','white-arc'):
                        setat(tag+'-edge-'+name,f,{'attr':{'d':d},'x':drift})
                    setat(tag+'-edge-energy',f,{'opacity':fade*pulse*strength})
                    setat(tag+'-edge-arc',f,{'strokeDashoffset':-(f-st)*float(edge.get('arcSpeed',17)),
                        'opacity':.65+.3*math.sin(f*1.23)**2})
                    setat(tag+'-edge-white-arc',f,{'strokeDashoffset':(f-st)*float(edge.get('arcSpeed',17))*.73,
                        'opacity':.7+.3*math.sin(f*.81+2)**2})
                    for k in range(particles):
                        side=k%2;life=((f-st+k*7)%23)/23
                        ix=(k*29+seed*11)%93;x,y=edges[side][ix]
                        # 6..10px fibres travel 30..60px outward, away from actors.
                        x+=(-1 if side==0 else 1)*life*(30+k%6*6)
                        y+=life*(-35+(k%7)*11)
                        alpha=math.sin(life*math.pi)*fade*.95*strength
                        setat(f'{tag}-fiber-{k}',f,{'x':x+drift,'y':y,
                            'rotation':(k*37+f*3)%180,'opacity':alpha,'scale':.6+.7*life})
        elif kind=='slit_eyes':
            if len(clips)<2: raise ValueError('slit_eyes needs left/right source clips')
            for j in range(2):
                content.append(f'<div id="{tag}-half-{j}" class="lf-plane">'+source(j)+'</div>')
            content.append(f'<div id="{tag}-seam" class="lf-seam"></div>')
            cx=float(e.get('seamX',960));openf=int(e.get('openFrames',7))
            zoomf=int(e.get('zoomFrames',4));tozoom=float(e.get('endZoom',1.0))
            for f in range(a,b):
                q=out((f-st)/max(1,openf));half=mix(9,W/2,q)
                setat(tag+'-half-0',f,{'clipPath':rectpath([max(0,cx-half),0,min(cx,half),H]),'opacity':1})
                setat(tag+'-half-1',f,{'clipPath':rectpath([cx,0,min(W-cx,half),H]),'opacity':1})
                setat(tag+'-seam',f,{'left':cx-2,'opacity':min(1,(f-st+1)/2),'height':H})
                # Optional final 4f push repeats F520 body -> F522 eye-scale.
                if tozoom!=1:
                    p=smooth((f-(en-zoomf))/max(1,zoomf-1))
                    setat(tag,f,{'scale':mix(1,tozoom,p),'transformOrigin':e.get('zoomOrigin','50% 48%')})
        elif kind=='filmstrip':
            # Original extra: unequal cards, offset in time, then diagonal peel.
            content.append('<div class="lf-plane lf-veil"></div>')
            defaults=[{'x':-650,'y':80,'scale':.34,'rotation':-8},
                      {'x':0,'y':-15,'scale':.47,'rotation':2},
                      {'x':666,'y':105,'scale':.30,'rotation':9}]
            cards=e.get('cards',defaults)
            for j in range(len(clips)):
                card=cards[j%len(cards)]
                content.append(f'<div id="{tag}-card-{j}" class="lf-plane lf-card">'+source(j)+
                    '<div class="lf-plane lf-film-edge"></div><div class="lf-perfs lf-perfs-top"></div><div class="lf-perfs lf-perfs-bottom"></div></div>')
                def pose(f,p,j=j,c=card):
                    q=out((f-st-j*3)/10);ex=smooth((f-(en-8)+j*1.4)/8)
                    return {'x':c.get('x',0)+mix((j-1)*190,0,q)+(-1 if j<1 else 1)*ex*220,
                        'y':c.get('y',0)+mix(180-j*90,0,q)-ex*160,
                        'scale':c.get('scale',.4)*mix(.86,1,q),
                        'rotation':c.get('rotation',0)+mix(14 if j%2 else -12,0,q)-ex*12,
                        'rotationY':mix(-24 if j%2 else 18,0,q),'transformPerspective':1800,
                        'opacity':q*(1-ex),'filter':f'blur({(1-q)*3:.2f}px)'}
                run(f'{tag}-card-{j}',st,en,pose)
        elif kind=='ribbon_flip':
            # Original extra: a continuous live image split into thin 3D leaves.
            # Each leaf plays the identical source clock, so joints align at rest.
            count=int(e.get('leaves',7));count=max(3,min(11,count))
            content.append(f'<div class="lf-plane lf-veil" style="opacity:{float(e.get("veilOpacity",1))}"></div>')
            aperture=e.get('aperture',[100,980]);reveal=max(1,float(e.get('revealFrames',10)));stagger=float(e.get('staggerFrames',1.5));shade=float(e.get('shadeStrength',.6))
            for j in range(count):
                x=W*j/count;w=W/count+1
                body=source(0,copy=j)
                content.append(f'<div id="{tag}-leaf-{j}" class="lf-plane lf-leaf" style="clip-path:{rectpath([x,float(aperture[0]),w,float(aperture[1])-float(aperture[0])])};transform-origin:{x+w/2}px 540px">'+body+
                    f'<div id="{tag}-shade-{j}" class="lf-plane lf-shade"></div></div>')
                def pose(f,p,j=j):
                    q=out((f-st-j*stagger)/reveal)
                    ex=0 if e.get('handoff',False) else smooth((f-(en-10)+j*.65)/10)
                    angle=mix(-82,0,q)+ex*78
                    return {'rotationY':angle,'rotationZ':mix(-6,0,q),
                        'transformPerspective':1500,'z':mix(110,0,q)+math.sin(ex*math.pi)*120,
                        'y':mix((j-count/2)*34,0,q)-ex*120,'opacity':q*(1-ex*.8)}
                run(f'{tag}-leaf-{j}',st,en,pose)
                run(f'{tag}-shade-{j}',st,en,lambda f,p,j=j:{'opacity':shade*(1-out((f-st-j*stagger)/reveal))+(0 if e.get('handoff',False) else .36*smooth((f-(en-10)+j*.65)/10))})
        elif kind=='depth_windows':
            # Original arrangement inspired by V17 foreground/background contrast.
            slots=e.get('slots',[{'x':-540,'y':100,'scale':.44,'rotation':-6,'blur':2.5},
                {'x':420,'y':-130,'scale':.48,'rotation':4,'blur':.3}])
            content.append('<div class="lf-plane lf-depth-veil"></div>')
            for j in range(len(clips)):
                slot=slots[j%len(slots)]
                content.append(f'<div id="{tag}-depth-{j}" class="lf-plane lf-depth">'+source(j)+'<div class="lf-plane lf-depth-edge"></div></div>')
                def pose(f,p,j=j,s=slot):
                    q=out((f-st-j*3)/10);ex=smooth((f-(en-6))/6)
                    return {'x':s.get('x',0)+(p-.5)*(-80 if j%2 else 140),
                        'y':s.get('y',0)+(1-q)*(70 if j%2 else -100),
                        'scale':s.get('scale',.45)+p*.025,'rotation':s.get('rotation',0)+p*(1 if j%2 else -1),
                        'filter':f'blur({float(s.get("blur",0)):.2f}px) saturate({.8 if j==0 else 1.1})',
                        'opacity':q*(1-ex),'zIndex':j+1}
                run(f'{tag}-depth-{j}',st,en,pose)
        else:
            raise ValueError('Unknown layout kind: '+str(kind))
        layers.append(f'<div id="{escape(tag)}" class="lf-root lf-plane" style="z-index:{z};opacity:0">'+''.join(content)+'</div>')
        setat(tag,a,{'opacity':1})
        if b<last: setat(tag,b,{'opacity':0})
    css='''
.lf-plane{position:absolute;inset:0;width:1920px;height:1080px;transform-origin:50% 50%;pointer-events:none}
.lf-root{pointer-events:none;perspective:1800px;isolation:isolate}
.lf-aperture{overflow:hidden}.lf-frame{position:absolute;border:2px solid #e3ad76;box-shadow:0 0 25px #080b1380;pointer-events:none}
.lf-paper{background:repeating-linear-gradient(7deg,#f5f1e9 0px,#f5f1e9 2px,#d8d2c6 3px,#f5f1e9 4px)}
.lf-seam{position:absolute;width:4px;top:0;background:#fffaf0;box-shadow:0 0 10px #e3ad76}
.lf-veil{background:#080b13d6}.lf-depth-veil{background:#080b1370;backdrop-filter:blur(3px)}
.lf-card{box-shadow:0 25px 95px #000b;overflow:hidden;background:#080b13}
.lf-film-edge{border:24px solid #080b13;border-top-width:72px;border-bottom-width:72px;box-shadow:inset 0 0 0 3px #e3ad76}
.lf-perfs{position:absolute;left:15px;right:15px;height:36px;background:repeating-linear-gradient(90deg,transparent 0,transparent 16px,#d8c9af 16px,#d8c9af 41px,transparent 41px,transparent 65px);opacity:.75}
.lf-perfs-top{top:18px}.lf-perfs-bottom{bottom:18px}.lf-leaf{backface-visibility:hidden;transform-style:flat}
.lf-shade{background:linear-gradient(90deg,#080b13c0,#e3ad7650,#080b13b0);mix-blend-mode:multiply}
.lf-depth{box-shadow:0 30px 100px #000a;overflow:hidden}.lf-depth-edge{border:5px solid #fffaf0a0}
.lf-edge-svg{overflow:visible;pointer-events:none;mix-blend-mode:normal}
'''
    # These children are animated explicitly. Initial hiding also makes the
    # standalone preview safe before its first seek into a later scene.
    css+='\n.lf-card,.lf-shade,.lf-paper{opacity:0}\n'
    return ''.join(layers),css
