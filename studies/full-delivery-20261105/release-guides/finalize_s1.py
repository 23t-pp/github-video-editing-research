from pathlib import Path
import json
p=Path('work/publish-all-20261105/projects/package_projects.py')
exec(p.read_text(encoding='utf-8').split("projects=['openchatcut-local'")[0])
assets=json.loads((ST/'assets-manifest.json').read_text(encoding='utf-8'))
assets=[a for a in assets if not a['asset'].startswith('jjk-s1-workflow-')]
excluded=json.loads((ST/'exclusions.json').read_text(encoding='utf-8'))
p=ROOT/'outputs/jjk-s1-workflow';files=list(walk(p));links=[]
for q,name in [(p/'HyperFrames可编辑工程.zip','jjk-s1-hyperframes-editable.zip'),(p/'openchatcut/咒力接力 · CURSED FLOW.ccproj','jjk-s1-openchatcut.ccproj')]:
 a=standalone(q,name);files.remove(q);links.append({'asset':a['asset'],'sha256':a['sha256'],'restore_path':a['restore_path']})
links.append({'release':'jjk-s1-jpg-60hz-2026-11-05','restore_path':'outputs/jjk-s1-workflow/素材集_60Hz_JPG','reason':'2,061,018 JPG路径由独立JPG release交付，不在工程包重复存储'})
archive('jjk-s1-workflow-complete.zip',files,{'extract_to':'工作区根目录','external_assets':links,'note':'只将项目根级HF ZIP及正式OCC工程拆出；测试fixture ZIP原字节保留于本包。'})
for name in ('jjk-s1-workflow-hyperframes-editable.zip','jjk-s1-workflow-openchatcut.ccproj'):
 (AS/name).unlink(missing_ok=True)
dump(ST/'exclusions.json',excluded)
summary=json.loads((ST/'validation-summary.json').read_text(encoding='utf-8'));summary.update(assets=len(assets),asset_bytes=sum(a['bytes'] for a in assets));dump(ST/'validation-summary.json',summary)
print('S1 FIX COMPLETE',flush=True)
