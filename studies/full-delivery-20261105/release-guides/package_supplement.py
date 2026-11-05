from pathlib import Path
import json,re,collections
r=Path('work/publish-all-20261105/projects').resolve()
exec((r/'package_projects.py').read_text(encoding='utf-8').split("projects=['openchatcut-local'")[0])
assets=json.loads((ST/'assets-manifest.json').read_text(encoding='utf-8'))
paths=json.loads((DOC/'nonsecret-name-filter-candidates.json').read_text(encoding='utf-8'));files=[];review=[];hits=[]
patterns=[('github-token',r'gh[pousr]_[A-Za-z0-9_]{30,}'),('openai-token',r'sk-(?:proj-)?[A-Za-z0-9_-]{30,}'),('private-key',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),('aws-key',r'AKIA[A-Z0-9]{16}')]
for rel in paths:
 q=ROOT/rel;assert q.is_file(),rel;category=''
 try:t=q.read_text(encoding='utf-8')
 except UnicodeError:t=None
 if q.suffix=='.key':assert t and re.fullmatch(r'[a-fA-F0-9]{64}\s*',t),rel;category='64位素材/渲染缓存SHA指纹，不是私钥'
 elif q.suffix.lower() in ('.png','.jpg','.jpeg'):category='人物profile侧脸图像证据，不是浏览器profile'
 elif q.suffix.lower() in ('.ts','.mts','.js','.mjs','.py'):category='profile/token/secret命名的实现或验证源码，不含实际账户凭据'
 elif q.suffix=='.json':
  data=json.loads(t.lstrip('\ufeff'));category='OCC命令、profile路径UUID或执行状态JSON证据，不含实际profile目录'
 elif q.suffix=='.txt':category='OCC执行stdout/stderr文本证据'
 else:category='非秘密制作证据/源码'
 if t:
  for n,pat in patterns:
   if re.search(pat,t):hits.append({'path':rel,'pattern':n})
 review.append({'path':rel,'bytes':q.stat().st_size,'sha256':hashfile(q),'classification':category});files.append(q)
assert not hits,hits
dump(DOC/'nonsecret-supplement-content-review.json',{'state':'PASS','unique_files':len(review),'high_confidence_secret_hits':hits,'files':review})
archive('publication-supplement.zip',files,{'extract_to':'工作区根目录','external_assets':[],'note':'补回先前仅因key/profile/token命名误排的169个非秘密源文件；原路径保留。64位.key是缓存指纹，profile角色图是侧脸证据，OCC profile是命令/路径日志。'})
x=json.loads((ST/'exclusions.json').read_text(encoding='utf-8'));supp=set(paths)
for e in x:
 if e['path'] in supp:e.update(reason='已内容实检为非秘密，已补回publication-supplement.zip；原先key/profile/token名称过滤误分类',publication='supplemented',supplement_asset='publication-supplement.zip')
dump(ST/'exclusions.json',x)
mirror=json.loads((MF/'text-mirror-manifest.json').read_text(encoding='utf-8'));seen={e['source'] for e in mirror}
for q in files:
 rel=q.relative_to(ROOT).as_posix()
 if q.suffix.lower() in ('.png','.jpg','.jpeg'):continue
 if q.stat().st_size>2*1024*1024 or rel in seen:continue
 dest=TS/'supplement'/q.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(q,dest);mirror.append({'path':dest.relative_to(TS).as_posix(),'source':rel,'bytes':q.stat().st_size,'sha256':hashfile(q)})
dump(MF/'text-mirror-manifest.json',mirror)
print('SUPPLEMENT COMPLETE',flush=True)
