"""Independent full unique-JPEG decode/hash and every 60Hz alias/mapping audit."""
from pathlib import Path
from PIL import Image
from fractions import Fraction
import sqlite3,hashlib,json,os,time,argparse
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1];LIB=ROOT/'素材集_60Hz_JPG'
def save(p,r):
    q=p.with_suffix('.tmp');q.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');q.replace(p)
def verify(folder):
    raw=json.loads((folder/'progress.json').read_text(encoding='utf-8'));assert raw['state']=='complete'
    expected=raw['expectedSamples'];db=sqlite3.connect(folder/'index.sqlite');rows=db.execute('SELECT frame,pts,jpeg_sha256,first_path FROM native ORDER BY frame').fetchall();tb=Fraction(raw['sourceTimeBase']);native={};errors=[];start=time.time();last=0
    heartbeat=folder/'verification-progress.json'
    for f,pts,sha,path in rows:
        file=folder/path;blob=file.read_bytes();assert hashlib.sha256(blob).hexdigest()==sha,(path,'hash mismatch')
        with Image.open(file) as im:im.load();assert im.size==(640,360) and im.format=='JPEG'
        stat=file.stat();native[f]=(pts,stat.st_dev,stat.st_ino,path)
        if time.time()-last>5:save(heartbeat,{'state':'verifying-native','decoded':len(native),'expected':len(rows),'heartbeatUnix':time.time()});last=time.time()
    assert sorted(native)==list(range(raw['nativeFramesDecoded'])),'native not continuous'
    count,lo,hi=db.execute('SELECT COUNT(*),MIN(sample),MAX(sample) FROM samples').fetchone();assert count==expected and lo==0 and hi==expected-1
    aliases=0;copies=0;last=0
    with (folder/'samples.jsonl').open('w',encoding='utf-8') as export:
        for sample,seconds,f,duplicate,path in db.execute('SELECT sample,time_seconds,source_frame,duplicate,path FROM samples ORDER BY sample'):
            pts,dev,ino,primary=native[f];rel_pts=pts-raw['firstSourcePts'];assert sample*tb.denominator>=rel_pts*tb.numerator*60
            if f+1 in native:assert sample*tb.denominator<(native[f+1][0]-raw['firstSourcePts'])*tb.numerator*60
            file=folder/path;st=file.stat();same=(st.st_dev,st.st_ino)==(dev,ino)
            if not same:
                assert hashlib.sha256(file.read_bytes()).hexdigest()==rows[f][2],(path,'alias content changed');copies+=1
            if duplicate:assert path!=primary
            else:assert path==primary
            export.write(json.dumps({'id':f'{folder.name}-F{sample:07}','sample':sample,'sampleSeconds':seconds,'sourceFrame':f,'sourcePts':pts,'sourceTimeBase':str(tb),'normalizedSourceSeconds':float(rel_pts*tb),'duplicate':bool(duplicate),'repeatOf':None if not duplicate else primary,'storageMode':'hardlink' if duplicate and same else 'copy' if duplicate else 'unique','jpg':path},ensure_ascii=False,separators=(',',':'))+'\n');aliases+=1
            if time.time()-last>5:save(heartbeat,{'state':'verifying-aliases','checked':aliases,'expected':expected,'heartbeatUnix':time.time()});last=time.time()
    disk=sum(1 for p in folder.glob('minute-*') for e in os.scandir(p) if e.name.endswith('.jpg'));assert disk==expected
    db.close();report={'id':folder.name,'state':'pass','sourceSha256':raw['sourceSha256'],'configSha256':raw['configSha256'],'nativeJpegDecodedAndShaChecked':len(native),'allSamplePathsAndPtsChecked':aliases,'physicalJpgEntries':disk,'expected':expected,'missing':0,'extra':0,'corruptUniqueJpeg':0,'badAlias':0,'aliasCopyFallbackCount':copies,'fullJsonlExport':'samples.jsonl','fullJsonlSha256':hashlib.sha256((folder/'samples.jsonl').read_bytes()).hexdigest(),'elapsedSeconds':time.time()-start,'scope':'All unique JPEG full load+SHA, all sample fileID/content and rational PTS mapping; repeated aliases share verified bytes','verifiedAtUnix':time.time()}
    save(folder/'verification.json',report);save(heartbeat,{'state':'complete','heartbeatUnix':time.time()});return report
def main():
    p=argparse.ArgumentParser();p.add_argument('--watch',action='store_true');p.add_argument('--episodes',nargs='*');p.add_argument('--workers',type=int,default=4);args=p.parse_args()
    pool=ThreadPoolExecutor(max_workers=args.workers);pending={}
    while True:
        for folder in sorted(LIB.glob('S1E*')):
            if args.episodes and folder.name not in args.episodes:continue
            raw=folder/'progress.json';done=folder/'verification.json'
            if not raw.exists() or folder.name in pending:continue
            r=json.loads(raw.read_text(encoding='utf-8'))
            if done.exists():
                v=json.loads(done.read_text(encoding='utf-8'));assert v['configSha256']==r.get('configSha256') and v['sourceSha256']==r.get('sourceSha256'),'stale verification';continue
            if r.get('state')=='complete' and len(pending)<args.workers:pending[folder.name]=pool.submit(verify,folder)
        for eid,job in list(pending.items()):
            if job.done():print(json.dumps(job.result(),ensure_ascii=False),flush=True);del pending[eid]
        reports=[json.loads(x.read_text(encoding='utf-8')) for x in sorted(LIB.glob('*/verification.json'))]
        save(ROOT/'data/library-verification.json',{'state':'pass' if len(reports)==24 else 'partial','verifiedEpisodes':len(reports),'expectedEpisodes':24,'samples':sum(x['allSamplePathsAndPtsChecked'] for x in reports),'uniqueJpegFullDecode':sum(x['nativeJpegDecodedAndShaChecked'] for x in reports),'items':reports})
        if len(reports)==24 or (not args.watch and not pending):break
        time.sleep(5)
    pool.shutdown(wait=True)
if __name__=='__main__':main()
