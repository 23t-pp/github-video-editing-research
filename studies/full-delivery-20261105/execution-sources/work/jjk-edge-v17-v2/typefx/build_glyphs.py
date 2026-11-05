"""Build-time only: preserve original Barlow contours without browser libraries."""
from pathlib import Path
import sys,math,json
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R/'build-deps'),str(R.parents[1]/'jjk-edge-v17/font-deps')]
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
font=TTFont(R/'sample-project/assets/fonts/BarlowCondensed-ExtraBold.woff2')
gs=font.getGlyphSet();cmap=font.getBestCmap()
class FlatPen(BasePen):
    def __init__(self):super().__init__(gs);self.lines=[];self.cur=[];self.at=None
    def _moveTo(self,p):self.cur=[p];self.at=p
    def _lineTo(self,p):
        old=self.at;n=max(1,math.ceil(math.dist(old,p)/20))
        self.cur.extend((old[0]+(p[0]-old[0])*i/n,old[1]+(p[1]-old[1])*i/n) for i in range(1,n+1));self.at=p
    def _curveToOne(self,a,b,c):
        p=self.at;n=max(4,math.ceil((math.dist(p,a)+math.dist(a,b)+math.dist(b,c))/20))
        for i in range(1,n+1):
            t=i/n;v=1-t;self.cur.append((v**3*p[0]+3*v*v*t*a[0]+3*v*t*t*b[0]+t**3*c[0],v**3*p[1]+3*v*v*t*a[1]+3*v*t*t*b[1]+t**3*c[1]))
        self.at=c
    def _closePath(self):
        if self.cur:self._lineTo(self.cur[0]);self.lines.append(self.cur);self.cur=[]
    def _endPath(self):self._closePath()
out={'unitsPerEm':font['head'].unitsPerEm,'font':'Barlow Condensed ExtraBold','glyphs':{}}
for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -/.,!?:':
    name=cmap.get(ord(ch));p=FlatPen()
    if name:gs[name].draw(p)
    out['glyphs'][ch]={'advance':gs[name].width if name else 250,'contours':[[[round(x,3),round(y,3)] for x,y in c] for c in p.lines]}
(R/'barlow-glyphs.json').write_text(json.dumps(out,separators=(',',':')),encoding='utf-8')
print('wrote glyphs',len(out['glyphs']),(R/'barlow-glyphs.json').stat().st_size)
