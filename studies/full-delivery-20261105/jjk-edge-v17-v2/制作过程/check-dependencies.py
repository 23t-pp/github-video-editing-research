from pathlib import Path
import sys,json,hashlib,shutil
BASE=Path(__file__).resolve().parents[2];R=BASE/'outputs/jjk-edge-v17-v2';H=R/'hyperframes';sys.path.insert(0,str(H))
from composition import load_edit,build
e=load_edit();_,needed,copies=build(e,frame_mode=True);assets={a['id']:a for a in e['assets']}
assert all(0<=n<assets[a]['frames'] for a,n in needed)
assert all((H/p).is_file() for p in copies)
asset_checks=[]
for a in assets.values():
    actual=hashlib.sha256((H/a['asset']).read_bytes()).hexdigest()
    prior=hashlib.sha256((BASE/'outputs/jjk-edge-v17/hyperframes'/a['asset']).read_bytes()).hexdigest()
    assert actual==prior,(a['id'],'V1 prepared media changed')
    if a.get('sha256'):assert actual==a['sha256'],(a['id'],'recorded sha mismatch')
    asset_checks.append({'asset':a['id'],'sha256':actual,'matchesV1PreparedMedia':True,'matchesRecordedSha':True if a.get('sha256') else None})
s={s['id']:s for s in e['shots']};l={l['id']:l for l in e['layouts']}
checks=[{'transition':'七叶→受伤脸','lastLayoutSourceFrame':l['fold-to-hurt']['clips'][0]['offset']+l['fold-to-hurt']['end']-l['fold-to-hurt']['start']-1,'firstNativeSourceFrame':s['S11']['assetStartFrame']},
{'transition':'窗扩屏→礼堂','lastLayoutSourceFrame':23,'firstNativeSourceFrame':s['S12']['assetStartFrame']},
{'transition':'手掌→全景','lastLayoutSourceFrame':20,'firstNativeSourceFrame':s['S35']['assetStartFrame']},
{'transition':'裂口→同源','lastLayoutSourceFrame':l['blue-tear']['clips'][0]['offset']+l['blue-tear']['end']-l['blue-tear']['start']-1,'nextBaseSourceFrame':s['S38']['assetStartFrame']+888-s['S38']['startFrame']}]
assert all((c.get('firstNativeSourceFrame',c.get('nextBaseSourceFrame')))==c['lastLayoutSourceFrame']+1 for c in checks)
r={'preparedSourceAssets':len(assets),'preparedAssetHashesMatch':True,'sourceFramesReferenced':len(needed),'allSourceFrameIndicesInRange':True,'uniqueAlphaFilesReferenced':len(copies),'allAlphaFilesExist':True,'handoffs':checks,'cameraLockedShots':[x['id'] for x in e['shots'] if x.get('cameraLocked')],'note':'逐源帧时钟连续核验；几何/运动衔接另见实际MP4联系表，不把时钟通过等同视觉完美。'}
r['assetChecks']=asset_checks
(R/'evidence/源帧与衔接检查.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
for src,dst in [(BASE/'work/jjk-edge-v17-v2/layout/布局模块与原生参考复核.md',R/'evidence/布局与参考复核.md'),(BASE/'outputs/jjk-edge-v17/evidence/V17主参考与选镜.md',R/'evidence/V17主参考与选镜.md'),(BASE/'outputs/jjk-edge-v17/evidence/V02文字参考.md',R/'evidence/V02文字参考.md')]:
    if src.exists():shutil.copy2(src,dst)
print(json.dumps(r,ensure_ascii=False))
