from pathlib import Path
import shutil,os,json,hashlib,collections
BASE=Path(__file__).resolve().parents[2]
OLD=BASE/'outputs/jjk-edge-v17-v2';NEW=BASE/'outputs/jjk-edge-v17-v3-dedup'
NEW.mkdir(parents=True,exist_ok=True)
HF=NEW/'hyperframes';HF.mkdir(exist_ok=True)
def link_or_copy(src,dst):
    try:os.link(src,dst)
    except OSError:shutil.copy2(src,dst)
    return dst
if not (HF/'assets').exists():shutil.copytree(OLD/'hyperframes/assets',HF/'assets',copy_function=link_or_copy)
if not (HF/'motion').exists():shutil.copytree(OLD/'hyperframes/motion',HF/'motion')
for name in ['composition.py','typefx.py','layoutfx.py','barlow-glyphs.json','hf.mjs','hyperframes.json','DESIGN.md','beats.json']:
    if not (HF/name).exists():shutil.copy2(OLD/'hyperframes'/name,HF/name)
if not (HF/'render.py').exists():
    text=(OLD/'hyperframes/render.py').read_text(encoding='utf8').replace('挚友_EDGE_精修V2.mp4','挚友_EDGE_画面去重V3.mp4')
    (HF/'render.py').write_text(text,encoding='utf8')
for folder in ['evidence','制作过程','openchatcut']:(NEW/folder).mkdir(exist_ok=True)
guard={str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [OLD/'挚友_EDGE_精修V2.mp4',OLD/'hyperframes/edit.json',BASE/'outputs/jjk-edge-v17/挚友_EDGE_一分钟.mp4']}
(NEW/'evidence/V1-V2保留指纹.json').write_text(json.dumps(guard,ensure_ascii=False,indent=2),encoding='utf8')
plan=json.loads((OLD/'hyperframes/edit.json').read_text(encoding='utf8'))
c=collections.Counter(s['assetId'] for s in plan['shots']);g=collections.Counter(x['alpha'] for x in plan['foregrounds'])
(NEW/'evidence/V2重复使用基线.json').write_text(json.dumps({'shots':len(plan['shots']),'uniqueAssetIds':len(c),'repeatPlacements':sum(v-1 for v in c.values()),'repeatedAssetFamilies':{k:v for k,v in c.items() if v>1},'foregroundEvents':len(plan['foregrounds']),'foregroundGroups':len(g),'foregroundRepeatPlacements':sum(v-1 for v in g.values()),'scope':'素材ID重复的诊断基线；不将同一转场的前景/背景配合算作独立重复，最终另核对源集数时间范围'},ensure_ascii=False,indent=2),encoding='utf8')
print('INIT',NEW)
