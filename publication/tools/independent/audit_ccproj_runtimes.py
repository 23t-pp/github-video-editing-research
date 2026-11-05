import json,base64,zipfile,hashlib,re,io
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
PAT=re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{30,}\b|\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}\b|\bAIza[A-Za-z0-9_-]{30,}\b|\bAKIA[A-Z0-9]{16}\b|\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}')
KEY=re.compile(r'(?:api.?key|token|cookie|password|passwd|secret|private.?key|credential|authorization)',re.I)
PLACE=re.compile(r'^(?:|null|none|undefined|true|false|0|1|test|local|dummy|example|placeholder|changeme|your[_ -].*|<.*>|\$\{.*\}|process\.env\..*|env\..*)$',re.I)
def scalar_summary(v):
 if v is None or isinstance(v,(bool,int,float)):return {'classification':'empty-or-nonsecret-primitive','type':type(v).__name__}
 if not isinstance(v,str):return {'classification':'container','type':type(v).__name__}
 if PLACE.match(v):return {'classification':'placeholder-or-empty','length':len(v)}
 if len(v)<12 and not re.search('[A-Za-z]',v):return {'classification':'short-value','length':len(v)}
 return {'classification':'review-nonempty-value','length':len(v),'sha256':hashlib.sha256(v.encode()).hexdigest()}
def fields(v,path='$'):
 out=[]
 if isinstance(v,dict):
  for k,x in v.items():
   p=path+'.'+k
   if KEY.search(k) and not isinstance(x,(dict,list)):out.append({'field':p,**scalar_summary(x)})
   out.extend(fields(x,p))
 elif isinstance(v,list):
  for i,x in enumerate(v):out.extend(fields(x,path+f'[{i}]'))
 elif isinstance(v,str) and v.lstrip().startswith(('{','[')):
  try:out.extend(fields(json.loads(v),path+'::<embedded-json>'))
  except (json.JSONDecodeError,RecursionError):pass
 return out
reports=[]
for project in sorted((ROOT/'outputs').iterdir()):
 if not project.is_dir():continue
 occ=project/'openchatcut'
 if not occ.exists():continue
 for p in occ.glob('*.ccproj'):
  manifest=None;chunks=[];start=end=None;format_types={}
  with p.open(encoding='utf-8') as f:
   for line in f:
    d=json.loads(line);typ=d.get('type');format_types[typ]=format_types.get(typ,0)+1
    if typ=='manifest':manifest=d
    elif typ=='agent-runtime-start':start=d
    elif typ=='agent-runtime-chunk':chunks.append(base64.b64decode(d['data']))
    elif typ=='agent-runtime-end':end=d
  r={'project':project.name,'ccproj':str(p.relative_to(ROOT)),'ccprojBytes':p.stat().st_size,'recordTypeCounts':format_types,'manifestRuntimeSchema':manifest.get('agentRuntime') if manifest else None,'manifestSensitiveFields':fields(manifest),'runtimeEntries':[],'credentialPatterns':[],'sensitiveFilenames':[],'runtimePresent':bool(chunks)}
  if chunks:
   data=b''.join(chunks);dest=OUT/'runtimes'/project.name;dest.mkdir(parents=True,exist_ok=True)
   actual=hashlib.sha256(data).hexdigest();r['runtimeBytes']=len(data);r['runtimeSha256']=actual;r['startHashMatches']=actual==start['sha256'];r['endHashMatches']=actual==end['sha256'];r['startBytesMatch']=len(data)==start['bytes']
   if data.lstrip().startswith(b'{'):
    (dest/'agent-runtime.json').write_bytes(data);runtime=json.loads(data);r['runtimeFormat']='JSON';r['runtimeTopLevelKeys']=list(runtime);r['runtimeSensitiveFields']=fields(runtime)
    for m in PAT.finditer(data.decode('utf-8')):r['credentialPatterns'].append({'path':'agent-runtime.json','line':data[:m.start()].count(b'\n')+1,'sha256':hashlib.sha256(m.group().encode()).hexdigest()})
    r['runtimeEntries']=[{'path':'agent-runtime.json','bytes':len(data),'configSensitiveFields':r['runtimeSensitiveFields']}]
   else:
    (dest/'agent-runtime.zip').write_bytes(data);r['runtimeFormat']='ZIP'
    with zipfile.ZipFile(io.BytesIO(data)) as z:
     for info in z.infolist():
      name=info.filename;parts=PurePosixPath(name).parts
      if PurePosixPath(name).is_absolute() or '..' in parts or '\\' in name or ':' in name:raise ValueError('Unsafe runtime entry')
      er={'path':name,'bytes':info.file_size,'configSensitiveFields':[]};r['runtimeEntries'].append(er)
      if info.is_dir():continue
      body=z.read(info);target=dest/'extracted'/Path(*parts);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
      bn=Path(name).name.lower()
      if bn=='.env' or bn.startswith('.env.') or bn in {'cookies','login data','local state','keyring','credentials.json','id_rsa','id_ed25519'}:r['sensitiveFilenames'].append(name)
      if b'\0' in body[:1000]:continue
      text=body.decode('utf-8',errors='replace')
      for m in PAT.finditer(text):r['credentialPatterns'].append({'path':name,'line':text.count('\n',0,m.start())+1,'sha256':hashlib.sha256(m.group().encode()).hexdigest()})
      if bn.endswith('.json'):
       try:er['configSensitiveFields']=fields(json.loads(text))
       except json.JSONDecodeError:pass
      if bn=='.env' or bn.startswith('.env.'):
       er['envFields']=[{'field':line.split('=',1)[0].strip(),**scalar_summary(line.split('=',1)[1].strip())} for line in text.splitlines() if '=' in line and not line.strip().startswith('#')]
  r['highConfidenceSecretCount']=len(r['credentialPatterns']);reports.append(r)
result={'projects':reports,'ccprojCount':len(reports),'highConfidenceSecretCount':sum(x['highConfidenceSecretCount'] for x in reports),'sensitiveFilenameCount':sum(len(x['sensitiveFilenames']) for x in reports)}
(OUT/'ccproj-runtime-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'ccprojCount':len(reports),'highConfidenceSecretCount':result['highConfidenceSecretCount'],'sensitiveFilenameCount':result['sensitiveFilenameCount'],'runtimeEntries':[(r['project'],len(r['runtimeEntries'])) for r in reports]},ensure_ascii=False))
