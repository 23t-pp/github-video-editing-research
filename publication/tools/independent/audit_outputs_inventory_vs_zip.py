"""Independent source path/byte coverage, using actual ZIP directories (not packager manifests)."""
import os,zipfile,json,hashlib,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;ASSETS=ROOT/'work/publish-all-20261105/projects/assets'
SKIP={'.git','node_modules','__pycache__','github-video-editing-research','素材集_60Hz_JPG'}
expected={}
for d,ds,fs in os.walk(ROOT/'outputs'):
 ds[:]=[x for x in ds if x not in SKIP]
 for n in fs:
  p=Path(d)/n;expected[p.relative_to(ROOT).as_posix()]=p.stat().st_size
coverage={};duplicates=[];extra=[];checks=[]
packages=list(ASSETS.glob('*-complete.zip'))+[ASSETS/'publication-supplement.zip']
small_candidates=[]
for p in packages:
 with zipfile.ZipFile(p) as z:
  for t in z.infolist():
   if not t.filename.startswith('outputs/') or t.is_dir():continue
   if t.filename in coverage and coverage[t.filename]['bytes']!=t.file_size:duplicates.append(t.filename)
   coverage[t.filename]={'bytes':t.file_size,'archive':p.name,'entry':t.filename}
   if t.file_size<250000:small_candidates.append((p.name,t.filename))
  if 'PUBLICATION-ASSET-RESTORE.json' in z.namelist():
   m=json.loads(z.read('PUBLICATION-ASSET-RESTORE.json'))
   for e in m.get('external_assets',[]):
    if not e.get('asset') or not e.get('restore_path','').startswith('outputs/'):continue
    q=ASSETS/e['asset'];coverage[e['restore_path']]={'bytes':q.stat().st_size,'standalone':q.name,'expectedSha256':e['sha256']}
missing=sorted(set(expected)-set(coverage));extra=sorted(set(coverage)-set(expected));bad_sizes=[p for p in expected if p in coverage and expected[p]!=coverage[p]['bytes']]
rng=random.Random('all-output-inventory-20261105');sample=rng.sample(sorted(set(small_candidates)),min(80,len(set(small_candidates))))
for archive,name in sample:
 with zipfile.ZipFile(ASSETS/archive) as z:data=z.read(name)
 same=hashlib.sha256(data).digest()==hashlib.sha256((ROOT/name).read_bytes()).digest();checks.append({'path':name,'archive':archive,'shaMatches':same})
r={'expectedOutputFiles':len(expected),'actualArchiveAndExternalSourcePaths':len(coverage),'missing':missing,'extra':extra,'byteSizeMismatches':bad_sizes,'conflictingDuplicateSizes':duplicates,'actualSmallFileShaSamples':checks,'pass':not missing and not extra and not bad_sizes and not duplicates and all(c['shaMatches'] for c in checks),'scope':'All output source relative paths and byte counts against actual ZIP directories/external physical assets, plus 80 deterministic small-file SHA samples. Packager separately full-byte verified all files; this report does not claim independent full SHA of all 5579 files.'}
(OUT/'outputs-independent-coverage-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in r.items() if k not in ['actualSmallFileShaSamples','scope']},ensure_ascii=False))
