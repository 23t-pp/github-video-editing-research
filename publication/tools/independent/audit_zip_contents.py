import zipfile,json,re,hashlib,os,argparse,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
SKIP={'.git','node_modules','素材集_60Hz_JPG','github-video-editing-research'}
PAT=re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{30,}\b|\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}\b|\bAIza[A-Za-z0-9_-]{30,}\b|\bAKIA[A-Z0-9]{16}\b')
ap=argparse.ArgumentParser();ap.add_argument('--base',default='outputs');ap.add_argument('--extra-base');ap.add_argument('--out',default='zip-content-audit.json');ap.add_argument('--ready-only',action='store_true');args=ap.parse_args()
reports=[]
for d,ds,fs in itertools.chain.from_iterable(os.walk(ROOT/base) for base in [args.base,args.extra_base] if base):
 ds[:]=[x for x in ds if x not in SKIP]
 for n in fs:
  if not n.endswith('.zip'):continue
  p=Path(d)/n
  if args.ready_only and not any((base/'ready'/(p.name+'.json')).exists() for base in [p.parent,p.parent.parent]):continue
  r={'archive':str(p.relative_to(ROOT)),'entries':0,'textEntriesScanned':0,'sensitiveCandidates':[],'credentialPatterns':[],'nestedZips':[]}
  with zipfile.ZipFile(p) as z:
   for t in z.infolist():
    r['entries']+=1;base=Path(t.filename).name.lower()
    if base=='.env' or base.startswith('.env.') or base in {'cookies','login data','local state','keyring','credentials.json','id_rsa','id_ed25519'}:r['sensitiveCandidates'].append(t.filename)
    if base.endswith('.zip'):r['nestedZips'].append(t.filename)
    if Path(base).suffix in {'.py','.mjs','.js','.cjs','.ts','.tsx','.jsx','.vue','.svelte','.sh','.bat','.cmd','.ps1','.json','.jsonl','.md','.txt','.html','.css','.toml','.yaml','.yml','.env','.ini','.config','.key','.pem','.properties','.lock'} and t.file_size<2_000_000:
     r['textEntriesScanned']+=1;txt=z.read(t).decode('utf-8',errors='replace')
     for m in PAT.finditer(txt):r['credentialPatterns'].append({'entry':t.filename,'line':txt.count('\n',0,m.start())+1,'sha256':hashlib.sha256(m.group().encode()).hexdigest()})
  reports.append(r)
out={'archives':reports,'archiveCount':len(reports),'sensitiveCandidateCount':sum(len(x['sensitiveCandidates']) for x in reports),'credentialPatternCount':sum(len(x['credentialPatterns']) for x in reports)}
(OUT/args.out).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k!='archives'}))
