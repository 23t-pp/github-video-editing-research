"""Original archive monitor; the persistent outer plane follows V20 structure.
It is not a tracked physical phone from the anime source.
"""
import math
from html import escape
def tail_layers(plan,first,last,setat):
    if not plan.get('tailcard'):return '',''
    e=plan['tailcard'];st,en=e['start'],e['end'];a,b=max(first,st),min(last,en)
    if a>=b:return '',''
    html='<div id="tail-sign" class="plane" style="opacity:0;z-index:90"><div class="tail-shade"></div><div class="tail-chinese">'+escape(e['text'])+'</div><div class="tail-english">JUJUTSU KAISEN · SEASON 01</div></div><div id="tail-black" class="plane" style="background:#080b13;opacity:0;z-index:160"></div>'
    for f in range(a,b):
        setat('tail-sign',f,{'opacity':min(1,(f-st+1)/5),'y':10*(1-min(1,(f-st)/6))})
        setat('tail-black',f,{'opacity':max(0,min(1,(f-(en-12))/11))})
    css='.tail-shade{position:absolute;left:0;right:0;bottom:0;height:310px;background:linear-gradient(transparent,#080b13d9)}.tail-chinese{position:absolute;left:120px;top:835px;font:900 64px "JJK Heavy";letter-spacing:10px;color:#fff7de}.tail-english{position:absolute;left:125px;top:932px;font:800 29px "Barlow Condensed";letter-spacing:6px;color:#72c7ed}'
    return html,css
def screen_layers(plan,fps,first,last,media,setat):
    tail,tailcss=tail_layers(plan,first,last,setat)
    ev=plan.get('archiveScreen');css='';layers=[]
    if not ev:return tail,tailcss
    st,en=ev['start'],ev['end'];a,b=max(first,st),min(last,en)
    if a>=b:return tail,tailcss
    contents=[]
    for i,s in enumerate(plan['shots']):
        x,y=s['startFrame'],s['startFrame']+s['frames']
        if x>=st and y<=en:contents.append(media('archive-'+s['id'],s['assetId'],x,y,s['assetStartFrame'],450+i))
    layers.append('<div id="archive-scene" class="plane" style="opacity:0;z-index:40"><div class="archive-grid"></div><div id="archive-monitor" class="plane"><div class="archive-bezel"></div><div class="archive-window"><div class="archive-source">'+''.join(contents)+'</div></div><div class="archive-glass"></div><div class="archive-label">CURSED ARCHIVE <span>第一季 · 咒力档案</span></div><div class="archive-led"></div></div></div>')
    for f in range(a,b):
        p=(f-st)/(en-st-1);q=min(1,(f-st)/8);e=1-(1-q)**3
        setat('archive-scene',f,{'opacity':1})
        setat('archive-monitor',f,{'rotation':-4+2*p,'scale':.90+.1*e,'y':45*(1-e),'rotationY':-8+4*p,'transformPerspective':1800})
    if b<last:setat('archive-scene',b,{'opacity':0})
    css='''.archive-grid{position:absolute;inset:0;background:radial-gradient(ellipse at 75% 20%,#561a2b 0,transparent 60%),linear-gradient(110deg,#080b13,#17232f);border:35px solid #080b13}.archive-grid:after{content:"";position:absolute;inset:0;background-image:linear-gradient(#72c7ed14 1px,transparent 1px),linear-gradient(90deg,#72c7ed14 1px,transparent 1px);background-size:65px 65px}.archive-bezel{position:absolute;left:415px;top:155px;width:1090px;height:754px;background:linear-gradient(135deg,#3e4758,#0b1019 35%,#252a3a);border:5px solid #b9cbd26b;border-radius:30px;box-shadow:22px 35px 60px #000b}.archive-window{position:absolute;left:455px;top:250px;width:1010px;height:568px;overflow:hidden;background:#000;border:2px solid #080b13}.archive-source{position:absolute;left:0;top:0;width:1920px;height:1080px;transform:scale(.5260416667);transform-origin:0 0}.archive-glass{position:absolute;left:435px;top:174px;width:1050px;height:715px;background:linear-gradient(125deg,#ffffff13,transparent 34%,transparent 80%,#72c7ed10);border-radius:23px;pointer-events:none}.archive-label{position:absolute;left:459px;top:190px;color:#fff7de;font:800 27px "Barlow Condensed";letter-spacing:7px}.archive-label span{font:700 23px "JJK Heavy";letter-spacing:1px;margin-left:100px;color:#a6bdcb}.archive-led{position:absolute;left:1405px;top:858px;width:10px;height:10px;border-radius:50%;background:#72c7ed;box-shadow:0 0 17px #72c7ed}'''
    return ''.join(layers)+tail,css+tailcss
