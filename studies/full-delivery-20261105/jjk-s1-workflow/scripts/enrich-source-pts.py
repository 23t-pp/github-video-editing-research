from pathlib import Path
from fractions import Fraction
import json,re
R=Path(__file__).resolve().parent.parent;p=R/'data/retrieved-assets.json';d=json.loads(p.read_text(encoding='utf-8'))
for a in d['assets']:
    if a['source'] is None:continue
    text=(R/'evidence/retrieval-logs'/f'{a["shot"]}.log').read_text(encoding='utf-8',errors='replace')
    tb_match=re.search(r'config in time_base:\s*(\d+)/(\d+)',text);assert tb_match,a['shot']
    tb=Fraction(int(tb_match[1]),int(tb_match[2]));rows=re.findall(r'\bn:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:',text)
    assert rows,a['shot']
    seek=Fraction(str(a['source']['decodeSeekSeconds']));seek_ticks=round(seek/tb)
    original=[(int(n),int(pts)) for n,pts in rows];assert all(x[1]<y[1] for x,y in zip(original,original[1:]))
    first=original[0][1]
    a['source'].update(firstActuallyDecodedSourcePts=seek_ticks+first,sourceTimeBase=f'{tb.numerator}/{tb.denominator}',firstActuallyDecodedSourceSeconds=float((seek_ticks+first)*tb),decodedNativeFramesObserved=len(original),ptsBasis='same retrieval FFmpeg showinfo integer PTS plus input seek converted to stream ticks; requested source in/out remain separately named',preparedSampling='setpts relative first decoded frame / recorded playbackRate, then FFmpeg fps=24 (near), without interpolation')
    a['source']['decodedNativePtsRelativeToSeek']=[pts for n,pts in original]
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');print('Enriched actual showinfo source PTS',len(d['assets'])-1)
