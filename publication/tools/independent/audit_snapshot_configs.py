import zipfile,json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
KEY=re.compile(r'(?:api.?key|token|cookie|password|passwd|secret|private.?key|credential|authorization)',re.I)
PLACE=re.compile(r'^(?:|null|none|undefined|true|false|0|1|test|local|dummy|example|placeholder|changeme|your[_ -].*|<.*>|\$\{.*\}|process\.env\..*|env\..*)$',re.I)
def fields(v,path='$'):
 out=[]
 if isinstance(v,dict):
  for k,x in v.items():
   p=path+'.'+k
   if KEY.search(k) and not isinstance(x,(dict,list)):
    if x is None or isinstance(x,(int,float,bool)):cl='noncredential-primitive'
    elif isinstance(x,str) and PLACE.fullmatch(x):cl='empty-or-placeholder'
    elif isinstance(x,str) and re.fullmatch(r'[~^<>= ]*[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.]+)?',x):cl='dependency-semver'
    elif k=='authorizationBasis' and isinstance(x,str) and hashlib.sha256(x.encode()).hexdigest()=='2d18751b022848fbde8ddd9af835c2d0414092d76dcd8533e8cb9c207b5e25f0':cl='manually-reviewed-authorization-prose'
    else:cl='review-nonempty-string'
    out.append({'field':p,'type':type(x).__name__,'classification':cl,**({'length':len(x),'sha256':hashlib.sha256(x.encode()).hexdigest()} if isinstance(x,str) else {})})
   out+=fields(x,p)
 elif isinstance(v,list):
  for i,x in enumerate(v):out+=fields(x,path+f'[{i}]')
 return out
reports=[]
for name in ['openchatcut-app-source-snapshot.zip','execution-and-research-sources.zip','publication-supplement.zip']:
 p=ROOT/'work/publish-all-20261105/projects/assets'/name
 if not p.exists():continue
 r={'archive':name,'parsedJsonFiles':0,'fields':[]}
 with zipfile.ZipFile(p) as z:
  for t in z.infolist():
   if not t.filename.lower().endswith('.json') or t.file_size>5_000_000:continue
   try:d=json.loads(z.read(t).decode('utf-8-sig'))
   except (UnicodeDecodeError,json.JSONDecodeError):continue
   r['parsedJsonFiles']+=1
   for finding in fields(d):r['fields'].append({'entry':t.filename,**finding})
 reports.append(r)
(OUT/'snapshot-config-fields-audit.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{'archive':r['archive'],'parsedJsonFiles':r['parsedJsonFiles'],'sensitiveKeyFields':len(r['fields']),'nonemptyReviewFields':[f for f in r['fields'] if f['classification']=='review-nonempty-string']} for r in reports],ensure_ascii=False))
