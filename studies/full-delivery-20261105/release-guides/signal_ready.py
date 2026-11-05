import json
from pathlib import Path
r=Path('work/publish-all-20261105/projects').resolve();ready=r/'ready';ready.mkdir(exist_ok=True)
n=0
for a in json.loads((r/'assets-manifest.json').read_text(encoding='utf-8')):
 if a['asset'].startswith('jjk-s1-workflow-'):continue
 out=ready/(a['asset']+'.json')
 if out.exists():continue
 v={'state':'verified','path':str(r/'assets'/a['asset']),'name':a['asset'],'bytes':a['bytes'],'sha256':a['sha256'],'release':'projects'}
 tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(out);n+=1
print(n,'assets ready')
