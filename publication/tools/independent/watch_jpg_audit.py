import time,json
from pathlib import Path
from audit_jpg_archive import audit,OUT,ROOT
done={};start=time.time()
for f in OUT.glob('S1E??-archive-audit.json'):
 r=json.loads(f.read_text(encoding='utf-8'))
 if r.get('pass'):done[r['episode']]=r
while len(done)<24:
 for i in range(1,25):
  ep=f'S1E{i:02}';archive=ROOT/'work/publish-all-20261105/jpg'/(ep+'.tar.gz')
  ready=ROOT/'work/publish-all-20261105/jpg/ready'/(archive.name+'.json')
  if ep in done or not archive.exists() or not ready.exists():continue
  try:r=audit(archive,ep,extract_full=(i==1))
  except Exception as e:
   r={'episode':ep,'pass':False,'exception':repr(e)}
   (OUT/(ep+'-archive-audit.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
   print(json.dumps(r),flush=True)
  done[ep]=r
  summary={'pass':len(done)==24 and all(r['pass'] for r in done.values()),'complete':len(done),'expected':24,'jpgEntries':sum(r.get('jpgEntries',0) for r in done.values()),'regularJpg':sum(r.get('regularJpg',0) for r in done.values()),'hardlinkJpg':sum(r.get('hardlinkJpg',0) for r in done.values()),'failed':[ep for ep,r in done.items() if not r['pass']],'elapsedSeconds':time.time()-start}
  (OUT/'jpg-independent-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
 time.sleep(5)
print('ALL 24 INDEPENDENT AUDITS FINISHED',flush=True)
