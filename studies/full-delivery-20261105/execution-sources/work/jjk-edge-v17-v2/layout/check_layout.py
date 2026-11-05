from pathlib import Path
import importlib.util,json,re
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('layoutfx',HERE/'layoutfx.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
events=[]
for i,kind in enumerate(['window_expand','tear_reveal','slit_eyes','filmstrip','ribbon_flip','depth_windows']):
    n=3 if kind=='filmstrip' else 2 if kind in ('slit_eyes','depth_windows') else 1
    events.append({'id':kind,'kind':kind,'start':40,'end':88,
        'edgeFx':True if kind=='tear_reveal' else False,
        'clips':[{'assetId':'C03','offset':12,'transform':{'scale':1.1,'x':10}} for j in range(n)]})
def build(first,last):
    calls=[];sets=[]
    def media(tag,assetId,start,end,offset=12,track=0):
        a,b=max(first,start),min(last,end)
        calls.append({'tag':tag,'asset':assetId,'frames':[offset+a-start,offset+b-start],
            'track':track,'global':[a,b]})
        return f'<video id="{tag}"></video>'
    def setat(tag,frame,props):sets.append((tag,frame,props))
    html,css=m.layout_layers(events,{'assets':[]},24,first,last,media,setat)
    ids=re.findall(r'\bid="([^\"]+)"',html)
    assert len(ids)==len(set(ids)), 'Duplicate DOM IDs'
    assert len(calls)==len({c['track'] for c in calls}), 'Overlapping media track IDs'
    for tag,f,p in sets:
        assert tag in ids,(tag,'missing animation target')
        assert first<=f<=last,(f,'outside chunk')
    return html,css,calls,sets
full=build(0,144);chunk=build(72,144)
geo=lambda sets:{(tag,f):props for tag,f,props in sets if f>=72 and tag not in {'layout-'+e['id'] for e in events}}
assert geo(full[3])==geo(chunk[3]),'Chunk geometry differs from full composition'
assert all(c['frames']==[44,60] for c in chunk[2]),'Media clock restarted at chunk boundary'
handoff=[]
m.layout_layers([{'id':'handoff','kind':'ribbon_flip','start':244,'end':264,
    'handoff':True,'clips':[{'assetId':'C20','offset':12}]}],{},24,216,288,
    lambda *args:'',lambda tag,f,p:handoff.append((tag,f,p)))
leaf_final=[p for tag,f,p in handoff if f==263 and re.fullmatch('layout-handoff-leaf-[0-9]+',tag)]
assert len(leaf_final)==7 and all(p['rotationY']==0 and p['y']==0 and p['opacity']==1 for p in leaf_final)
assert all(p['opacity']==0 for tag,f,p in handoff if f==263 and 'shade' in tag)
report={'status':'passed','fps':24,'checks':['all six effect branches build',
    'unique DOM IDs including 3D leaves','unique media tracks','all animation targets exist',
    'mid-event chunk geometry matches full run','source frame 44 continues at global frame 72',
    '20-frame ribbon handoff ends with all 7 leaves flat, opaque, stationary and unshaded'],
    'mediaInstances':len(full[2]),'geometryFrameSets':len(full[3]),
    'note':'Structural and clock validation only; rendered visual QA belongs to parent compositor.'}
(HERE/'layout-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
