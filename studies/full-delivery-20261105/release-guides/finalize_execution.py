from pathlib import Path
import json,os,hashlib,re,zipfile,zlib,configparser,urllib.parse
r=Path('work/publish-all-20261105/projects').resolve()
exec((r/'package_projects.py').read_text(encoding='utf-8').split("projects=['openchatcut-local'")[0])
assets=json.loads((ST/'assets-manifest.json').read_text(encoding='utf-8'))
assets=[a for a in assets if a['asset']!='execution-and-research-sources.zip']
old=json.loads((MF/'execution-and-research-sources.zip.json').read_text(encoding='utf-8'))
files=[ROOT/e['path'] for e in old['files']];known=set(files);provenance=[]
for group in ('ai_editing','beat_montage','editable_templates','orchestrator'):
 for p in sorted((ROOT/'work'/group).iterdir()):
  if not p.is_dir():continue
  commit=p/'commit.json';meta=next((p/n for n in ('metadata.json','meta.json') if (p/n).exists()),None)
  if not commit.exists():continue
  c=json.loads(commit.read_text(encoding='utf-8-sig'));m=json.loads(meta.read_text(encoding='utf-8-sig')) if meta else {}
  ls=[]
  for d,ds,fs in os.walk(p):
   ds[:]=[x for x in ds if x not in EXDIR]
   for name in fs:
    if name.upper().startswith(('LICENSE','NOTICE','COPYING','AUTHORS')):
     q=Path(d)/name
     if q not in known:files.append(q);known.add(q)
     ls.append({'path':q.relative_to(ROOT).as_posix(),'sha256':hashfile(q)})
  provenance.append({'snapshot':p.relative_to(ROOT).as_posix(),'upstream_commit':c.get('sha'),'upstream_commit_url':c.get('html_url'),'repository':m.get('html_url',m.get('full_name')),'metadata_license':m.get('license'),'license_files':ls,'scope':'取证时已下载的局部快照，非上游完整克隆；如无许可文件，以同SHA上游许可和metadata为准'})
dump(DOC/'research-snapshot-provenance.json',provenance);files.append(DOC/'research-snapshot-provenance.json')
archive('execution-and-research-sources.zip',files,{'extract_to':'工作区根目录','note':'完整自写执行代码、OCC客户端、render-runner、取片脚本和上游取证局部快照；已保留所有已下载LICENSE/NOTICE及固定commit SHA，见research-snapshot-provenance.json。'})
mirror=json.loads((MF/'text-mirror-manifest.json').read_text(encoding='utf-8'));existing={e['source'] for e in mirror}
for q in files:
 rel=q.relative_to(ROOT).as_posix()
 if rel in existing:continue
 if q.stat().st_size>2*1024*1024:continue
 dest=TS/'execution-sources'/q.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(q,dest);mirror.append({'path':dest.relative_to(TS).as_posix(),'source':rel,'bytes':q.stat().st_size,'sha256':hashfile(q)})
dump(MF/'text-mirror-manifest.json',mirror)
print('EXECUTION FINAL',flush=True)
