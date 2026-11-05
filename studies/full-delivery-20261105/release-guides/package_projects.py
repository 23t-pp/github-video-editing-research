import os,re,json,hashlib,zipfile,shutil,zlib,time
from pathlib import Path
ROOT=Path.cwd().resolve(); ST=ROOT/'work/publish-all-20261105/projects'; AS=ST/'assets'; MF=ST/'manifests'; TS=ST/'text-staging'; DOC=ST/'docs'
for p in (AS,MF,TS,DOC):p.mkdir(parents=True,exist_ok=True)
LIMIT=2**31
EXDIR={'.git','node_modules','python-deps','__pycache__','素材集_60Hz_JPG','.venv','venv','audio-env','models','font-deps'}
TEXT={'.md','.txt','.py','.js','.mjs','.cjs','.json','.html','.css','.ps1','.sh','.ts','.tsx','.yaml','.yml','.toml','.csv','.svg'}
BLOCK=re.compile(r'(^\.env($|\.)|token|keyring|credential|secret|profile|\.pem$|\.pfx$|\.key$)',re.I)
assets=[];excluded=[];mirror=[];source_entries=[]
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def hashfile(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(4*1024*1024):h.update(b)
 return h.hexdigest()
def walk(p,work=False):
 for d,ds,fs in os.walk(p):
  keep=[]
  for x in ds:
   why=None
   if x in EXDIR:why='第三方依赖/模型/缓存/独立JPG库'
   elif work and (x in ('render','cache','render-cache','hf-rendered-frames','package-check','hf-package','audio-work','tail-native','tail-native-final') or 'cache' in x.lower()):why='work渲染产物/缓存/重复包'
   if why:excluded.append({'path':(Path(d)/x).relative_to(ROOT).as_posix(),'reason':why})
   else:keep.append(x)
  ds[:]=keep
  for f in sorted(fs):
   q=Path(d)/f
   if BLOCK.search(f):excluded.append({'path':q.relative_to(ROOT).as_posix(),'reason':'本机敏感配置/个人profile文件名过滤'});continue
   yield q

def archive(name,files,extra=None):
 out=AS/name;entries=[]
 print('BEGIN '+name,flush=True)
 with zipfile.ZipFile(out,'w',allowZip64=True,compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for q in files:
   rel=q.relative_to(ROOT).as_posix();info=zipfile.ZipInfo.from_file(q,arcname=rel)
   info.compress_type=zipfile.ZIP_STORED if q.suffix.lower() in {'.mp4','.m4a','.mp3','.jpg','.jpeg','.png','.webm','.zip','.ccproj','.woff','.woff2'} else zipfile.ZIP_DEFLATED
   h=hashlib.sha256();crc=0;n=0
   with q.open('rb') as src,z.open(info,'w',force_zip64=True) as dst:
    while b:=src.read(4*1024*1024):dst.write(b);h.update(b);crc=zlib.crc32(b,crc);n+=len(b)
   entries.append({'path':rel,'bytes':n,'sha256':h.hexdigest(),'crc32':f'{crc&0xffffffff:08x}'})
  if extra:z.writestr('PUBLICATION-ASSET-RESTORE.json',json.dumps(extra,ensure_ascii=False,indent=2)+'\n')
 # Real second pass: independently read each archive entry, recompute decompressed SHA/CRC/count vs bytes read from original source.
 with zipfile.ZipFile(out) as z:
  assert len(z.infolist())==len(entries)+(1 if extra else 0)
  for e in entries:
   h=hashlib.sha256();crc=0;n=0
   with z.open(e['path']) as f:
    while b:=f.read(4*1024*1024):h.update(b);crc=zlib.crc32(b,crc);n+=len(b)
   assert (n,h.hexdigest(),f'{crc&0xffffffff:08x}')==(e['bytes'],e['sha256'],e['crc32']),e['path']
   assert z.getinfo(e['path']).CRC==crc&0xffffffff
 assert out.stat().st_size<LIMIT
 result={'asset':name,'source_file_count':len(entries),'bytes':out.stat().st_size,'sha256':hashfile(out),'validation':'PASS: 每个entry解压内容bytes/SHA256/CRC32与原源读取逐字节一致；ZIP CRC一致','restore':extra,'entries_manifest':f'manifests/{name}.json'}
 dump(MF/(name+'.json'),{'asset':result,'files':entries});assets.append(result);dump(ST/'assets-manifest.json',assets)
 print('READY '+json.dumps(result,ensure_ascii=False),flush=True)
 return result

def standalone(q,name):
 out=AS/name;shutil.copyfile(q,out);hs=hashfile(q);assert hashfile(out)==hs
 result={'asset':name,'source':q.relative_to(ROOT).as_posix(),'bytes':out.stat().st_size,'sha256':hs,'validation':'PASS: 复制后源与资产SHA256一致','restore_path':q.relative_to(ROOT).as_posix()}
 assert out.stat().st_size<LIMIT
 if q.suffix=='.zip':
  with zipfile.ZipFile(out) as z:assert z.testzip() is None
  result['zip_crc']='PASS: 所有内层ZIP entries CRC'
 assets.append(result);dump(ST/'assets-manifest.json',assets);print('READY '+json.dumps(result,ensure_ascii=False),flush=True);return result

projects=['openchatcut-local','reference-editing-study','reference-library-20261105','v05-six-panel','fast60','reference-replay-next','jjk-edge-v17','jjk-edge-v17-v2','jjk-edge-v17-v3-dedup','jjk-s1-workflow','reference-library-release-20261105']
for project in projects:
 p=ROOT/'outputs'/project;files=list(walk(p));links=[]
 for q in files[:]:
  # Existing large nested HF ZIP is published exactly once and referenced for restoration.
  if q.name=='HyperFrames可编辑工程.zip' and q.parent==p:
   a=standalone(q,('jjk-s1' if project=='jjk-s1-workflow' else project)+'-hyperframes-editable.zip');links.append({'asset':a['asset'],'sha256':a['sha256'],'restore_path':a['restore_path']});files.remove(q)
 if project=='jjk-s1-workflow':
  q=next(x for x in files if x.suffix=='.ccproj');a=standalone(q,'jjk-s1-openchatcut.ccproj');links.append({'asset':a['asset'],'sha256':a['sha256'],'restore_path':a['restore_path']});files.remove(q)
  links.append({'asset':'另组JPG分卷资产（根发布总清单）','restore_path':'outputs/jjk-s1-workflow/素材集_60Hz_JPG','reason':'2,061,018 JPG路径不在本项目包重复存储'})
 archive(project+'-complete.zip',files,{'extract_to':'工作区根目录','external_assets':links,'note':'保持outputs冻结文件原字节；依restore_path放回独立资产即可还原完整项目。'} if links else {'extract_to':'工作区根目录','external_assets':[]})
 for q in files:
  if q.suffix.lower() in TEXT and q.stat().st_size<=2*1024*1024:
   dest=TS/'studies'/project/q.relative_to(p);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(q,dest);mirror.append({'path':dest.relative_to(TS).as_posix(),'source':q.relative_to(ROOT).as_posix(),'bytes':q.stat().st_size,'sha256':hashfile(q)})

# Work helpers: preserve scripts, argument/state evidence and research snapshots; omit generated render/cache and third party runtimes.
work_projects=['fast60','reference-replay-v07','jjk-edge-v17','jjk-edge-v17-v2','jjk-edge-v17-v3-dedup','jjk-s1-workflow','reference-library-20261105','reference-reverse','v05-sample','ai_editing','beat_montage','editable_templates','orchestrator','hyperframes-learning']
for project in work_projects:
 p=ROOT/'work'/project
 for q in walk(p,work=True):
  if q.suffix.lower() not in TEXT:continue
  # Only source/data text: logs/console dumps are preserved only when small, never massive frame analysis.
  if q.stat().st_size>16*1024*1024:excluded.append({'path':q.relative_to(ROOT).as_posix(),'reason':'work巨大生成分析文本；项目正式证据已在complete包'});continue
  source_entries.append(q)
for q in (ROOT/'work').iterdir():
 if q.is_file() and q.suffix.lower() in TEXT and not BLOCK.search(q.name):source_entries.append(q)
archive('execution-and-research-sources.zip',source_entries,{'extract_to':'工作区根目录','note':'自写执行脚本/OCC/render-runner/调研快照源码；第三方依赖需重新安装；本机profile/env/token不发布。'})
for q in source_entries:
 if q.stat().st_size<=2*1024*1024:
  dest=TS/'execution-sources'/q.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(q,dest);mirror.append({'path':dest.relative_to(TS).as_posix(),'source':q.relative_to(ROOT).as_posix(),'bytes':q.stat().st_size,'sha256':hashfile(q)})
dump(MF/'text-mirror-manifest.json',mirror);dump(ST/'exclusions.json',excluded)
# Independently validate staged text mirror exact bytes.
for e in mirror:assert hashfile(TS/e['path'])==e['sha256']
dump(ST/'validation-summary.json',{'status':'PASS','assets':len(assets),'asset_bytes':sum(a['bytes'] for a in assets),'text_mirror_files':len(mirror),'text_mirror_bytes':sum(e['bytes'] for e in mirror),'all_assets_below_2GiB':all(a['bytes']<LIMIT for a in assets),'source_outputs_modified':False,'excluded_jpg_library':'由专职JPG归档任务提供','validation':'archive entries checked with original-source streaming SHA256/bytes/CRC32; standalone source-copy hashes; text source-copy hashes'})
print('ALL COMPLETE',flush=True)
