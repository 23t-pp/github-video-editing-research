import os,json,sqlite3,hashlib,re,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).parent
SKIP={'.git','node_modules','__pycache__','audio-env','python-deps','build-deps','models','numba-cache','render-cache','.cache','browser-profile','chrome-profile','chromium-profile','site-packages','Lib','Scripts'}
def walk(base):
 for d,ds,fs in os.walk(base):
  ds[:]=[x for x in ds if x not in SKIP and x!='素材集_60Hz_JPG']
  for f in fs: yield Path(d)/f
def rel(p):return p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def run(*args):return subprocess.check_output(args,cwd=ROOT,text=True,encoding='utf-8')
OUT.mkdir(parents=True,exist_ok=True)
projects=[]
for d in sorted((ROOT/'outputs').iterdir()):
 if not d.is_dir() or d.name=='github-video-editing-research':continue
 files=list(walk(d))
 projects.append({'project':d.name,'filesExcludingJpgLibrary':len(files),'bytesExcludingJpgLibrary':sum(p.stat().st_size for p in files),'topFiles':[p.name for p in d.iterdir() if p.is_file()]})
source=[];candidates=[];findings=[]
text_ext={'.py','.mjs','.js','.cjs','.ts','.tsx','.jsx','.vue','.svelte','.sh','.bat','.cmd','.ps1','.json','.jsonl','.md','.txt','.html','.css','.yaml','.yml','.toml','.log','.xml','.ini','.config','.env','.key','.pem','.properties','.lock'}
secret_re=re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{30,}\b|\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}\b|\bAIza[A-Za-z0-9_-]{30,}\b|\bAKIA[A-Z0-9]{16}\b')
for base in [ROOT/'outputs',ROOT/'work']:
 for p in walk(base):
  if 'github-video-editing-research' in p.parts or 'publish-all-20261105' in p.parts:continue
  if base.name=='work' and p.suffix.lower() in {'.py','.mjs','.cjs','.ps1','.js','.html','.css','.json','.md','.txt','.log'}:
   source.append({'path':rel(p),'bytes':p.stat().st_size})
  if p.name=='.env' or p.name.startswith('.env.') or p.name.lower() in {'login data','cookies','local state','keyring','credentials','credentials.json','id_rsa','id_ed25519'}:
   candidates.append({'path':rel(p),'reason':'credential-like filename; review before publishing'})
  if p.suffix.lower() in text_ext and p.stat().st_size<25_000_000:
   try:txt=p.read_text(encoding='utf-8',errors='replace')
   except OSError:continue
   for m in secret_re.finditer(txt):findings.append({'path':rel(p),'line':txt.count('\n',0,m.start())+1,'kind':'credential pattern','value_sha256':hashlib.sha256(m.group().encode()).hexdigest()})
episodes=[]
for i in range(1,25):
 ep=f'S1E{i:02}';d=ROOT/'outputs/jjk-s1-workflow/素材集_60Hz_JPG'/ep
 c=sqlite3.connect(f'file:{d.as_posix()}/index.sqlite?mode=ro&immutable=1',uri=True)
 native=c.execute('select count(*),sum(bytes) from native').fetchone();samples=c.execute('select count(*),sum(duplicate) from samples').fetchone()
 verification=json.loads((d/'verification.json').read_text(encoding='utf-8-sig'))
 episodes.append({'episode':ep,'native':native[0],'nativeBytes':native[1],'samples':samples[0],'duplicates':samples[1],'manifestSha256':sha(d/'samples.jsonl'),'verification':verification})
 c.close()
remote=json.loads(run('gh','release','view','reference-library-2026-11-05','--repo','23t-pp/github-video-editing-research','--json','tagName,url,assets'))
for a in remote['assets']:
 local=ROOT/'outputs/reference-library-release-20261105'/a['name'];a['localMatch']=local.exists() and local.stat().st_size==a['size'] and 'sha256:'+sha(local)==a['digest']
report={'projects':projects,'workEvidenceCount':len(source),'workEvidence':source,'excludedDirectoryNames':sorted(SKIP),'secretFilenameCandidates':candidates,'secretPatternFindings':findings,'episodes':episodes,'jpgTotal':sum(x['samples'] for x in episodes),'nativeTotal':sum(x['native'] for x in episodes),'existingRemote':remote}
(OUT/'inventory-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'projects':len(projects),'workEvidence':len(source),'secretFilenameCandidates':len(candidates),'secretPatternFindings':len(findings),'jpgTotal':report['jpgTotal'],'nativeTotal':report['nativeTotal'],'remoteAssetsMatch':all(x['localMatch'] for x in remote['assets'])},ensure_ascii=False))
