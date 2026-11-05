import contextlib,io,json,tempfile,zipfile,stat
from pathlib import Path
import restore_projects as tool
R=Path(__file__).resolve().parent
results=[]
def check(name,f):
 f();results.append({'test':name,'state':'PASS'})
def tiny_tests():
 with tempfile.TemporaryDirectory(prefix='restore-tests-',dir=R) as tmp:
  d=Path(tmp);downloads=d/'downloads';downloads.mkdir();root=d/'workspace'
  def write(name,member,content=b'ok',meta=None,mode=None):
   with zipfile.ZipFile(downloads/name,'w') as z:
    if mode:
     i=zipfile.ZipInfo(member);i.create_system=3;i.external_attr=mode<<16;z.writestr(i,content)
    else:z.writestr(member,content)
    if meta:z.writestr(tool.META,json.dumps(meta))
  write('bad-complete.zip','../escape.txt')
  try:tool.restore(downloads,root,['bad']);raise AssertionError('traversal accepted')
  except ValueError:pass
  assert not (d/'escape.txt').exists()
  write('symlink-complete.zip','link',b'outside',mode=stat.S_IFLNK|0o777)
  try:tool.restore(downloads,root,['symlink']);raise AssertionError('symlink accepted')
  except ValueError:pass
  write('missing-complete.zip','outputs/x/a.txt',meta={'external_assets':[{'asset':'missing.zip','sha256':'0'*64,'restore_path':'outputs/x/missing.zip'}]})
  try:tool.restore(downloads,root,['missing']);raise AssertionError('missing asset accepted')
  except FileNotFoundError:pass
  assert not root.exists(),'missing assets should fail before extraction'
  write('safe-complete.zip','outputs/x/a.txt',b'ok')
  first=tool.restore(downloads,root,['safe']);second=tool.restore(downloads,root,['safe'])
  assert first['written']==1 and second['same']==1
  (root/'outputs/x/a.txt').write_bytes(b'keep me')
  try:tool.restore(downloads,root,['safe']);raise AssertionError('different content overwritten')
  except FileExistsError:pass
  assert (root/'outputs/x/a.txt').read_bytes()==b'keep me'
check('越界拒绝/ZIP符号链接拒绝/缺独立资产预检/同SHA跳过/不同内容不覆盖',tiny_tests)
# Actual S1 archive and real independent HF/OCC, restored to a new staging workspace.
real=R/'restore-smoke-workspace'
first=tool.restore(R/'assets',real,['jjk-s1-workflow'])
manifest=json.loads((R/'manifests/jjk-s1-workflow-complete.zip.json').read_text(encoding='utf-8'))
for entry in manifest['files']:
 q=tool.disk_path(real/entry['path']);assert q.stat().st_size==entry['bytes'] and tool.digest(q)==entry['sha256'],entry['path']
for asset in json.loads((R/'assets-manifest.json').read_text(encoding='utf-8')):
 if asset['asset'] in ('jjk-s1-hyperframes-editable.zip','jjk-s1-openchatcut.ccproj'):
  assert tool.digest(real/asset['restore_path'])==asset['sha256']
supp=json.loads((R/'manifests/publication-supplement.zip.json').read_text(encoding='utf-8'))
for entry in supp['files']:
 if tool.selected_entry(R/'assets/publication-supplement.zip',entry['path'],['jjk-s1-workflow']):
  q=tool.disk_path(real/entry['path']);assert q.stat().st_size==entry['bytes'] and tool.digest(q)==entry['sha256'],entry['path']
second=tool.restore(R/'assets',real,['jjk-s1-workflow']);assert second['written']==0 and second['same']==first['written']+first['same']
results.append({'test':'真实S1 2217源entry+正式HF/OCC+137补包文件，全部逐源SHA复核，第二次2356文件同SHA跳过','state':'PASS','first':first,'second':second})
(R/'restore-tests.json').write_text(json.dumps({'state':'PASS','results':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RESTORE TESTS PASS',flush=True)
