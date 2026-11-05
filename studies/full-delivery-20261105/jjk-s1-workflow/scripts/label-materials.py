"""Deterministic appearance tags; these never infer people, action, or exact scene cuts."""
from pathlib import Path
import sqlite3,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
summary=json.loads((ROOT/'data/library-summary.json').read_text(encoding='utf-8'));assert summary['state']=='complete' and summary['completedEpisodes']==24
criteria={'sampling':'one metrics record per source video second at 60Hz sample n=60*second','brightnessMetric':'encoded RGB weighted mean .2126R+.7152G+.0722B, not linear-light luminance','dark':'weightedMean<=32','bright':'weightedMean>=190','warm':'R-B>=18','cool':'B-R>=18','appearanceChangeCandidate':'sum absolute channel mean changes versus previous second >=90','semantics':'unknown unless separate human-viewed candidate evidence; appearance change is not a confirmed cut'}
(ROOT/'data/automatic-label-criteria.json').write_text(json.dumps(criteria,ensure_ascii=False,indent=2),encoding='utf-8')
count=0;stats={};dest=ROOT/'data/automatic-tags.jsonl'
with dest.open('w',encoding='utf-8') as f:
    for folder in sorted((ROOT/'素材集_60Hz_JPG').glob('S1E*')):
        db=sqlite3.connect(folder/'index.sqlite');prev=None
        for second,source,y,r,g,b,old in db.execute('SELECT * FROM metrics ORDER BY second'):
            tags=[]
            if y<=32:tags.append('dark')
            if y>=190:tags.append('bright')
            if r-b>=18:tags.append('warm')
            if b-r>=18:tags.append('cool')
            rgb=(r,g,b);difference=None if prev is None else sum(abs(x-z) for x,z in zip(rgb,prev))
            if difference is not None and difference>=90:tags.append('appearance_change_candidate')
            prev=rgb
            for t in tags:stats[t]=stats.get(t,0)+1
            f.write(json.dumps({'episode':folder.name,'second':second,'sample60Hz':second*60,'nativeFrame':source,'weightedEncodedBrightness':round(y,4),'meanRGB':[round(v,4) for v in rgb],'differencePreviousSecond':None if difference is None else round(difference,4),'tags':tags,'person':'unknown','action':'unknown','motionDirection':'unknown','confirmedCut':False},ensure_ascii=False,separators=(',',':'))+'\n');count+=1
        db.close()
(ROOT/'data/automatic-label-report.json').write_text(json.dumps({'state':'complete','episodes':24,'perSecondRecords':count,'tags':stats,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'criteria':'data/automatic-label-criteria.json','scope':'全季每秒外观指标；没有用色彩指标伪造人物、动作、景别或切镜标签'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'records':count,'tags':stats},ensure_ascii=False))
