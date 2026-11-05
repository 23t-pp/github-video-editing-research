from pathlib import Path
import os,json,hashlib,zipfile,zlib,configparser,re,shutil
ROOT=Path.cwd().resolve();ST=ROOT/'work/publish-all-20261105/projects';AS=ST/'assets';MF=ST/'manifests';TS=ST/'text-staging';APP=Path('C:/Users/PC/Desktop/OpenChatCut-main')
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(4*1024*1024):h.update(b)
 return h.hexdigest()
exdirs={'.git','node_modules','dist','build','desktop-dist','cli-dist','release','release-packages','.cache','cache','.venv','venv','models','profiles','dev-profiles','__pycache__','playwright-report','test-results','coverage'}
exext={'.onnx','.pt','.pth','.bin','.gguf','.ggml','.safetensors','.tflite','.exe','.dll','.wasm','.pfx','.pem','.key','.sqlite','.sqlite3','.db','.log'}
files=[];excluded=[];hits=[];scanned=0
patterns=[('github-token',r'gh[pousr]_[A-Za-z0-9_]{30,}'),('openai-token',r'sk-(?:proj-)?[A-Za-z0-9_-]{30,}'),('private-key',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),('aws-key',r'AKIA[A-Z0-9]{16}'),('bearer-constant',r'Bearer\s+[A-Za-z0-9_\-\.]{30,}')]
for d,ds,fs in os.walk(APP):
 for n in ds[:]:
  if n in exdirs:excluded.append({'path':(Path(d)/n).relative_to(APP).as_posix(),'reason':'第三方依赖/构建/缓存/模型/真实profile目录'});ds.remove(n)
 for n in sorted(fs):
  q=Path(d)/n
  if n.startswith('.env') or q.suffix.lower() in exext or n in ('keyring.json','credentials.json','auth.json','token.json'):
   excluded.append({'path':q.relative_to(APP).as_posix(),'bytes':q.stat().st_size,'reason':'本机环境/凭证或第三方运行体/模型/数据库/日志'});continue
  files.append(q)
  if q.stat().st_size<20*1024*1024:
   try:t=q.read_text(encoding='utf-8')
   except UnicodeError:continue
   scanned+=1
   for name,pat in patterns:
    if re.search(pat,t):
     if name=='bearer-constant' and q.relative_to(APP).as_posix()=='src/agent/external-edit-session-projection.verify.ts' and 'Bearer must-not-cross-the-external-boundary' in t:continue
     hits.append({'path':q.relative_to(APP).as_posix(),'pattern':name})
dump(ST/'app-scan-hits-paths.json',hits)
assert not hits,'High confidence credential pattern found; inspect paths-only report before publishing'
head=(APP/'.git/HEAD').read_text().strip();commit=head
if head.startswith('ref: '):
 ref=head[5:];refp=APP/'.git'/ref
 if refp.exists():commit=refp.read_text().strip()
 elif (APP/'.git/packed-refs').exists():
  for line in (APP/'.git/packed-refs').read_text().splitlines():
   if line.endswith(' '+ref):commit=line.split()[0];break
 else:commit=None
cfg=configparser.ConfigParser();cfg.read(APP/'.git/config',encoding='utf-8');origin=cfg.get('remote "origin"','url',fallback='unknown')
# Never publish userinfo if a credentialed remote URL happens to exist.
origin=re.sub(r'(https?://)[^/@]+@',r'\1',origin)
package=json.loads((APP/'package.json').read_text());provenance={'source_directory':str(APP),'archive_prefix':'dependencies/OpenChatCut-main','upstream_origin':origin,'upstream_HEAD':commit,'upstream_ref':head,'application_version':package['version'],'license':package['license'],'license_sha256':sha(APP/'LICENSE'),'snapshot':'用户提供本机源码目录的当前原文件字节快照；本机.git为无提交初始化，upstream_HEAD为null时不推测上游SHA。逐文件SHA固定本快照，可与research OpenChatCut局部快照另行比较。','excluded':excluded,'credential_scan':{'state':'PASS','scanned_utf8_files':scanned,'patterns':[n for n,p in patterns],'high_confidence_hits':[],'reviewed_test_fixture':['src/agent/external-edit-session-projection.verify.ts: obvious sentence-shaped dummy Bearer fixture; no credential']},'install':'Node >=24 <25；npm ci，npm run sync:mediapipe，npm run sync:whisper-cli；具体启动见上游README与保留的Start-OpenChatCut.ps1。环境变量自行配置，不提供.env。'}
dump(ST/'docs/openchatcut-app-provenance.json',provenance)
name='openchatcut-app-source-snapshot.zip';out=AS/name;entries=[]
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
 for q in files:
  rel='dependencies/OpenChatCut-main/'+q.relative_to(APP).as_posix();info=zipfile.ZipInfo.from_file(q,arcname=rel);info.compress_type=zipfile.ZIP_STORED if q.suffix.lower() in {'.png','.jpg','.jpeg','.mp3','.woff2','.icns'} else zipfile.ZIP_DEFLATED
  h=hashlib.sha256();crc=0;n=0
  with q.open('rb') as src,z.open(info,'w',force_zip64=True) as dst:
   while b:=src.read(4*1024*1024):dst.write(b);h.update(b);crc=zlib.crc32(b,crc);n+=len(b)
  entries.append({'path':rel,'source':str(q),'bytes':n,'sha256':h.hexdigest(),'crc32':f'{crc&0xffffffff:08x}'})
 z.writestr('PUBLICATION-SOURCE-PROVENANCE.json',json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
with zipfile.ZipFile(out) as z:
 assert len(z.infolist())==len(entries)+1
 for e in entries:
  h=hashlib.sha256();crc=0;n=0
  with z.open(e['path']) as f:
   while b:=f.read(4*1024*1024):h.update(b);crc=zlib.crc32(b,crc);n+=len(b)
  assert (n,h.hexdigest(),f'{crc&0xffffffff:08x}')==(e['bytes'],e['sha256'],e['crc32'])
  assert z.getinfo(e['path']).CRC==crc&0xffffffff
result={'asset':name,'source':str(APP),'source_file_count':len(entries),'bytes':out.stat().st_size,'sha256':sha(out),'validation':'PASS: 全entry bytes/SHA256/CRC32与源读取一致；高置信凭据扫描零命中','entries_manifest':'manifests/'+name+'.json','restore':{'extract_to':'工作区根目录','archive_prefix':'dependencies/OpenChatCut-main'}}
assert result['bytes']<2**31
dump(MF/(name+'.json'),{'asset':result,'files':entries});assets=json.loads((ST/'assets-manifest.json').read_text(encoding='utf-8'));assets.append(result);dump(ST/'assets-manifest.json',assets)
# Small source mirror includes license and code, not binary runtime/media.
text={'.md','.txt','.py','.js','.mjs','.cjs','.json','.html','.css','.ps1','.sh','.ts','.tsx','.yaml','.yml','.toml','.svg','.mts','.jsonc'}
mirror=json.loads((MF/'text-mirror-manifest.json').read_text(encoding='utf-8'))
for q,e in zip(files,entries):
 if q.stat().st_size<=2*1024*1024 and (q.suffix.lower() in text or q.name.upper().startswith(('LICENSE','NOTICE','COPYING'))):
  dest=TS/e['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(q,dest);assert sha(dest)==e['sha256'];mirror.append({'path':dest.relative_to(TS).as_posix(),'source':str(q),'bytes':e['bytes'],'sha256':e['sha256']})
dump(MF/'text-mirror-manifest.json',mirror)
print(json.dumps(result,ensure_ascii=False),flush=True)
