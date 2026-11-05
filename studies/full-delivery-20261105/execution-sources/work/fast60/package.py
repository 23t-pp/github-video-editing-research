from pathlib import Path
import hashlib
import json
import zipfile
import os

root=Path(__file__).resolve().parents[2]/'outputs/fast60'
files=[root/'剪辑学习手册.md']
for sub in ('hyperframes','music'):
    folder=root/sub
    for path in sorted(folder.rglob('*')):
        parts=path.relative_to(folder).parts
        if path.is_file() and not any(p.startswith('.') or p=='__pycache__' for p in parts):
            files.append(path)
for name in ['镜头入点修订.json','片源实测.json','HyperFrames工程检查.txt']:
    p=root/'evidence'/name
    if p.is_file():files.append(p)
destination=root/'HyperFrames可编辑工程.zip'
temp=destination.with_suffix('.partial')
with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=2,allowZip64=True) as z:
    for p in files:
        method=zipfile.ZIP_STORED if p.suffix.lower() in {'.mp4','.npz','.jpg'} else zipfile.ZIP_DEFLATED
        z.write(p,p.relative_to(root),compress_type=method)
with zipfile.ZipFile(temp) as z:
    if z.testzip() is not None:raise ValueError('CRC error in package')
    plan=json.loads(z.read('hyperframes/edit.json'))
    referenced=[s['asset'] for s in plan['assets']]+list(plan['audio'].values())+[s['cue'] for s in plan['shots'] if s.get('cue')]
    names=set(z.namelist())
    if any('hyperframes/'+f not in names for f in referenced):raise ValueError('Missing embedded media')
os.replace(temp,destination)
print(f'{destination.name}: {len(files)} files, {destination.stat().st_size} bytes, CRC and {len(referenced)} references checked')
