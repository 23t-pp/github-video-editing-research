import argparse,subprocess,json,hashlib,os,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;BASE=ROOT/'work/publish-all-20261105';REPO='23t-pp/github-video-editing-research'
ap=argparse.ArgumentParser();ap.add_argument('--commit',required=True);args=ap.parse_args()
def gh(*a):
 for i in range(4):
  try:return json.loads(subprocess.check_output(['gh',*a],cwd=ROOT,text=True,encoding='utf-8'))
  except Exception:
   if i==3:raise
   time.sleep(2**i)
tags=['editing-projects-2026-11-05','jjk-s1-jpg-60hz-2026-11-05']
refs=subprocess.check_output(['git','ls-remote','https://github.com/'+REPO+'.git','refs/heads/main',*['refs/tags/'+t for t in tags]],cwd=ROOT,text=True,encoding='utf-8')
refmap={line.split()[1]:line.split()[0] for line in refs.splitlines()};ref_pass=len(refmap)==3 and all(v==args.commit for v in refmap.values())
tree=gh('api',f'repos/{REPO}/git/trees/{args.commit}?recursive=1');blobs={e['path']:e['sha'] for e in tree['tree'] if e['type']=='blob'}
staging=BASE/'projects/text-staging';checked=0;missing=[];different=[]
walk_root=Path('\\\\?\\'+str(staging)) if os.name=='nt' else staging
for d,_,fs in os.walk(walk_root):
 for n in fs:
  disk=Path(d)/n;p=Path(str(disk)[4:]) if os.name=='nt' else disk;rel=p.relative_to(staging).as_posix();body=disk.read_bytes();blob=hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest();checked+=1
  if rel not in blobs:missing.append(rel)
  elif blobs[rel]!=blob:different.append(rel)
legacy=gh('release','view','reference-library-2026-11-05','--repo',REPO,'--json','tagName,url,isDraft,publishedAt,assets')
initial=json.loads((OUT/'inventory-audit.json').read_text(encoding='utf-8'))['existingRemote'];oldexpected={a['name']:(a['size'],a['digest']) for a in initial['assets']};oldactual={a['name']:(a['size'],a['digest']) for a in legacy['assets']}
legacy_pass=oldactual==oldexpected and not legacy['isDraft'] and bool(legacy['publishedAt'])
result={'expectedSourceCommit':args.commit,'gitRefs':refmap,'refsPass':ref_pass,'gitTreeTruncated':tree.get('truncated'),'textMirrorBlobsCompared':checked,'textMissing':missing,'textBlobShaMismatches':different,'legacyRelease':{'tag':legacy['tagName'],'draft':legacy['isDraft'],'publishedAt':legacy['publishedAt'],'assetsCompared':len(oldactual),'namesDigestSizeMatchOriginal':legacy_pass},'pass':ref_pass and not tree.get('truncated') and checked==5966 and not missing and not different and legacy_pass}
(OUT/'public-source-and-legacy-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
