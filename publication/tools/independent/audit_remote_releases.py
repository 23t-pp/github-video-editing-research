import json,subprocess,time,argparse,urllib.request,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;BASE=ROOT/'work/publish-all-20261105'
ap=argparse.ArgumentParser();ap.add_argument('--require-public',action='store_true');args=ap.parse_args()
remote={};errors=[];comparisons=[];anonymous={}
def anonymous_bytes(req,limit=5_000_000):
 for attempt in range(4):
  try:
   url=req.full_url+('&' if '?' in req.full_url else '?')+'_independent_audit='+str(time.time_ns())
   request=urllib.request.Request(url,headers=dict(req.header_items()))
   with urllib.request.urlopen(request,timeout=30) as response:return response.read(limit)
  except Exception:
   if attempt==3:raise
   time.sleep(2**attempt)
for kind,rid in [('projects',435246066),('jpg',435246093)]:
 api=f'repos/23t-pp/github-video-editing-research/releases/{rid}'
 for attempt in range(4):
  try:d=json.loads(subprocess.check_output(['gh','api',api],cwd=ROOT,text=True,encoding='utf-8'));break
  except Exception:
   if attempt==3:raise
   time.sleep(2)
 remote[kind]=d;assets={a['name']:a for a in d['assets']}
 markers=list((BASE/kind/'ready').glob('*.json'))
 for marker in (BASE/'uploads/ready').glob('*.json'):
  if json.loads(marker.read_text(encoding='utf-8')).get('release')==kind:markers.append(marker)
 for marker in sorted(markers):
  expected=json.loads(marker.read_text(encoding='utf-8'));name=expected['name'];actual=assets.get(name)
  row={'release':kind,'releaseId':rid,'name':name,'expectedBytes':expected['bytes'],'expectedSha256':expected['sha256'],'remoteExists':actual is not None}
  if actual:
   row.update(remoteBytes=actual['size'],remoteDigest=actual.get('digest'),remoteState=actual['state'],browserDownloadUrl=actual['browser_download_url'],match=actual['size']==expected['bytes'] and actual.get('digest')=='sha256:'+expected['sha256'] and actual['state']=='uploaded')
  else:row['match']=False
  if not row['match']:errors.append(kind+'/'+name+' missing/mismatch')
  comparisons.append(row)
 if args.require_public:
  if d['draft'] or not d['published_at']:errors.append(kind+' not public/published')
  try:
   req=urllib.request.Request('https://api.github.com/repos/23t-pp/github-video-editing-research/releases/tags/'+d['tag_name'],headers={'User-Agent':'independent-publication-audit','Accept':'application/vnd.github+json'})
   public=json.loads(anonymous_bytes(req))
   anonymous[kind]={'success':True,'id':public['id'],'draft':public['draft'],'publishedAt':public['published_at'],'assetCount':len(public['assets'])}
   if public['id']!=rid or public['draft'] or len(public['assets'])!=len(d['assets']):errors.append(kind+' anonymous release mismatch')
   small_name='restore_projects.py' if kind=='projects' else 'restore_jpg.py'
   asset=next(a for a in public['assets'] if a['name']==small_name)
   if asset['size']>2_000_000:raise ValueError('Public smoke asset unexpectedly large')
   req=urllib.request.Request(asset['browser_download_url'],headers={'User-Agent':'independent-publication-audit'})
   body=anonymous_bytes(req,2_000_001)
   smoke={'name':small_name,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'match':len(body)==asset['size'] and 'sha256:'+hashlib.sha256(body).hexdigest()==asset['digest']}
   anonymous[kind]['actualAnonymousDownload']=smoke
   if not smoke['match']:errors.append(kind+' anonymous downloaded asset digest mismatch')
  except Exception as e:anonymous[kind]={'success':False,'error':repr(e)};errors.append(kind+' anonymous public read failed')
jpg_payloads=[x for x in comparisons if x['release']=='jpg'];jpg=[x for x in jpg_payloads if re.fullmatch(r'S1E\d{2}\.tar\.gz',x['name'])];project=[x for x in comparisons if x['release']=='projects']
if len(jpg)!=24:errors.append('JPG ready count is '+str(len(jpg))+' rather than 24')
known={x['name'] for x in jpg}
if known!={f'S1E{i:02}.tar.gz' for i in range(1,25)}:errors.append('JPG names not exact E01-E24 set')
for i in range(1,25):
 f=OUT/f'S1E{i:02}-archive-audit.json'
 if not f.exists():errors.append('independent JPG audit missing E'+str(i));continue
 a=json.loads(f.read_text(encoding='utf-8'))
 if not a.get('pass'):errors.append('independent JPG audit failed E'+str(i))
 for x in jpg:
  if x['name']==f'S1E{i:02}.tar.gz' and (x['expectedSha256']!=a['archiveSha256'] or x['expectedBytes']!=a['archiveBytes']):errors.append('independent/local manifest mismatch E'+str(i))
result={'state':'PASS' if not errors else 'PENDING_OR_FAILED','requirePublic':args.require_public,'checkedUnix':time.time(),'readyAssets':len(comparisons),'jpgAssets':len(jpg_payloads),'jpgArchives':len(jpg),'projectAssets':len(project),'matchedAssets':sum(x['match'] for x in comparisons),'remoteDrafts':{k:v['draft'] for k,v in remote.items()},'anonymousPublicChecks':anonymous,'comparisons':comparisons,'errors':errors}
(OUT/'remote-independent-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'remote-independent-api-snapshot.json').write_text(json.dumps(remote,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['comparisons','errors']},ensure_ascii=False));print(json.dumps(errors,ensure_ascii=False))
