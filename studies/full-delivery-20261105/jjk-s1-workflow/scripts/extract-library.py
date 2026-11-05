"""60Hz JPG material library; real decoded PTS, explicit duplicated samples, resumable by episode."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from PIL import Image
import subprocess,threading,queue,re,json,sqlite3,hashlib,os,time,math,shutil,io,argparse
ROOT=Path(__file__).resolve().parents[1];FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';FP='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'
LIB=ROOT/'素材集_60Hz_JPG';LIB.mkdir(exist_ok=True)
CONFIG_SHA=hashlib.sha256((ROOT/'data/run-config.json').read_bytes()).hexdigest()
def save(p,x):
    q=p.with_suffix('.tmp');q.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');q.replace(p)
def stream_jpg(f):
    b=b''
    while c:=f.read(65536):
        b+=c
        while (end:=b.find(b'\xff\xd9'))>=0:
            v,b=b[:end+2],b[end+2:];assert v[:2]==b'\xff\xd8';yield v
    assert not b,'incomplete jpeg'
def episode(item):
    eid=item['id'];out=LIB/eid;out.mkdir(exist_ok=True);status=out/'progress.json'
    source=Path(item['localPath']);source_stat=source.stat();started=time.time()
    if status.exists() and json.loads(status.read_text(encoding='utf-8')).get('state')=='complete':
        cached=json.loads(status.read_text(encoding='utf-8'));assert cached.get('configSha256')==CONFIG_SHA,'cached config mismatch'
        with source.open('rb') as sf:assert hashlib.file_digest(sf,'sha256').hexdigest()==cached['sourceSha256'],'cached source changed'
        check=sqlite3.connect(out/'index.sqlite');actual,low,high=check.execute('SELECT COUNT(*),MIN(sample),MAX(sample) FROM samples').fetchone();assert actual==cached['expectedSamples'] and low==0 and high==actual-1
        disk_count=sum(1 for folder in out.glob('minute-*') for entry in os.scandir(folder) if entry.name.endswith('.jpg'));assert disk_count==actual,'cached jpg count mismatch'
        for n in cached['jpgDecodeCheckedSampleIndices']:
            path=check.execute('SELECT path FROM samples WHERE sample=?',(n,)).fetchone()[0]
            with Image.open(out/path) as im:im.load();assert im.size==(640,360)
        check.close();return {'id':eid,'state':'cached-verified'}
    probe=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_streams','-of','json',str(source)]));tb=Fraction(probe['streams'][0]['time_base'])
    stream=probe['streams'][0];exact_duration=int(stream['duration_ts'])*tb;exact_samples=exact_duration*60;total=(exact_samples.numerator+exact_samples.denominator-1)//exact_samples.denominator
    db=sqlite3.connect(out/'index.sqlite');db.executescript('PRAGMA journal_mode=WAL;CREATE TABLE IF NOT EXISTS native(frame INTEGER PRIMARY KEY,pts INTEGER,pts_seconds REAL,jpeg_sha256 TEXT,bytes INTEGER,first_path TEXT);CREATE TABLE IF NOT EXISTS samples(sample INTEGER PRIMARY KEY,time_seconds REAL,source_frame INTEGER,duplicate INTEGER,path TEXT);CREATE TABLE IF NOT EXISTS metrics(second INTEGER PRIMARY KEY,source_frame INTEGER,luma REAL,r REAL,g REAL,b REAL,label TEXT);')
    db.execute('DELETE FROM native');db.execute('DELETE FROM samples');db.execute('DELETE FROM metrics');db.commit()
    q=queue.Queue();errors=[]
    cmd=[FF,'-hide_banner','-threads','2','-i',str(source),'-map','0:v:0','-an','-vf','showinfo,scale=640:360','-fps_mode','passthrough','-c:v','mjpeg','-q:v','6','-threads','2','-f','image2pipe','pipe:1']
    p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);log=(out/'ffmpeg-errors.log').open('w',encoding='utf-8')
    def stderr():
        for raw in iter(p.stderr.readline,b''):
            line=raw.decode(errors='replace');m=re.search(r'\bn:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:',line)
            if m:q.put((int(m[1]),int(m[2])))
            elif 'error' in line.lower() or 'invalid' in line.lower():errors.append(line);log.write(line)
        q.put(None)
    t=threading.Thread(target=stderr,daemon=True);t.start();sn=0;count=0;prev=None;first_pts=None;stored=0;last_report=0;fallback=0
    def flush_prev(end_pts):
        nonlocal sn,stored,fallback
        if prev is None:return
        i,pts,data=prev;primary=None;rows=[];sha=hashlib.sha256(data).hexdigest()
        while sn<total and (end_pts is None or sn*tb.denominator<end_pts*tb.numerator*60):
            folder=out/f'minute-{sn//3600:03}';folder.mkdir(exist_ok=True);dest=folder/f'F{sn:07}.jpg'
            if dest.exists():dest.unlink() # only replace this task-owned exact JPG on an unfinished episode resume
            if primary is None:dest.write_bytes(data);primary=dest;stored+=len(data)
            else:
                try:os.link(primary,dest)
                except OSError:shutil.copyfile(primary,dest);fallback+=1;stored+=len(data)
            rel=dest.relative_to(out).as_posix();rows.append((sn,sn/60,i,int(dest!=primary),rel))
            if sn%60==0:
                im=Image.open(io.BytesIO(data)).convert('RGB').resize((32,18));rgb=[sum(v[c] for v in im.getdata())/(32*18) for c in range(3)];luma=sum(a*b for a,b in zip(rgb,[.2126,.7152,.0722]));db.execute('INSERT OR REPLACE INTO metrics VALUES(?,?,?,?,?,?,?)',(sn//60,i,luma,*rgb,'unknown_semantics'))
            sn+=1
        if primary:db.execute('INSERT OR REPLACE INTO native VALUES(?,?,?,?,?,?)',(i,pts,float(pts*tb),sha,len(data),primary.relative_to(out).as_posix()))
        db.executemany('INSERT OR REPLACE INTO samples VALUES(?,?,?,?,?)',rows)
    try:
        for data in stream_jpg(p.stdout):
            point=q.get(timeout=120);assert point is not None,'missing decoded PTS';i,pts=point;assert i==count,(i,count);count+=1
            if first_pts is None:first_pts=pts
            normalized_pts=pts-first_pts
            if prev is not None:assert pts>prev[1],'non-monotonic decoded PTS'
            flush_prev(normalized_pts);prev=(i,pts,data)
            if count%480==0:
                db.commit()
                if shutil.disk_usage(ROOT).free<80*1024**3:raise RuntimeError('disk reserve below 80GiB')
                now=time.time()
                if now-last_report>5:
                    save(status,{'id':eid,'state':'running','nativeFramesDecoded':count,'samplesWritten':sn,'expectedSamples':total,'elapsedSeconds':now-started,'heartbeatUnix':now,'pid':os.getpid(),'estimatedUniqueJpegBytes':stored});last_report=now
        flush_prev(None);rc=p.wait();t.join();assert rc==0,(rc,errors[-3:]);assert sn==total
        declared=int(item.get('declaredFrames',item.get('nativeFrames',probe['streams'][0].get('nb_frames',count))))
        assert count==declared,(eid,count,declared)
        db.commit();assert db.execute('SELECT COUNT(*) FROM samples').fetchone()[0]==total
        # Every minute: independent JPEG decoding of first, middle and last entries.
        qa=[]
        for minute in range((total+3599)//3600):
            a=minute*3600;b=min(total,a+3600)
            for n in sorted({a,(a+b-1)//2,b-1}):
                rel=db.execute('SELECT path FROM samples WHERE sample=?',(n,)).fetchone()[0]
                with Image.open(out/rel) as im:im.load();assert im.size==(640,360) and im.format=='JPEG'
                qa.append(n)
        with source.open('rb') as sf:source_hash=hashlib.file_digest(sf,'sha256').hexdigest()
        assert (source.stat().st_size,source.stat().st_mtime_ns)==(source_stat.st_size,source_stat.st_mtime_ns),'source mutated during extraction'
        disk_count=sum(1 for folder in out.glob('minute-*') for entry in os.scandir(folder) if entry.name.endswith('.jpg'));assert disk_count==total
        r={'id':eid,'state':'complete','nativeFramesDecoded':count,'uniqueJpegFiles':db.execute('SELECT COUNT(*) FROM native').fetchone()[0],'samplesWritten':sn,'expectedSamples':total,'duplicateEntries':db.execute('SELECT COUNT(*) FROM samples WHERE duplicate=1').fetchone()[0],'elapsedSeconds':time.time()-started,'heartbeatUnix':time.time(),'sourceSha256':source_hash,'firstSourcePts':first_pts,'sourceTimeBase':str(tb),'physicalBytesEstimate':stored,'hardlinkFallbackCopies':fallback,'jpgDecodeCheckedSampleIndices':qa,'allSourcePtsStrictlyIncreasing':True,'sampling':'t=n/60 normalized to first decoded PTS; hold nearest preceding decoded source frame; last source held to ceil(duration*60); NO interpolation','resolution':[640,360],'jpegQuality':6,'semanticScope':'per-second machine color/luma metrics; unknown_semantics by default; human candidate tags separate'}
        r.update(configSha256=CONFIG_SHA,sourceBytes=source_stat.st_size,sourceMtimeNs=source_stat.st_mtime_ns,streamDurationRational=str(exact_duration),sampleCountFromRationalDuration=total,physicalJpgEntryCount=disk_count,missing=0,extra=0,decodeCheckScope='每分钟首中尾抽检；不是所有JPG逐张解码',samplingComparison='integer rational sn*tb.denominator < relative_pts*tb.numerator*60')
        save(status,r);db.execute('PRAGMA wal_checkpoint(TRUNCATE)');db.close();return r
    except BaseException as ex:
        p.terminate();db.commit();db.close();save(status,{'id':eid,'state':'failed','error':str(ex),'nativeFramesDecoded':count,'samplesWritten':sn,'heartbeatUnix':time.time()});raise
    finally:log.close()
def main():
    a=argparse.ArgumentParser();a.add_argument('--workers',type=int,default=2);a.add_argument('--episodes',nargs='*');a.add_argument('--require-design-pass',action='store_true');args=a.parse_args()
    if args.require_design_pass:
        r=json.loads((ROOT/'reviews/设计审核.json').read_text(encoding='utf-8'));assert r.get('status') in ['pass','approved'] or r.get('decision') in ['pass','approved'],'design not approved'
    inv=json.loads((ROOT/'data/source-inventory.json').read_text(encoding='utf-8'));items=[x for x in inv['items'] if not args.episodes or x['id'] in args.episodes]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(episode,items):print(json.dumps(result,ensure_ascii=False),flush=True)
    statuses=[json.loads(p.read_text(encoding='utf-8')) for p in sorted(LIB.glob('*/progress.json'))];complete=[s for s in statuses if s['state']=='complete']
    save(ROOT/'data/library-summary.json',{'state':'complete' if len(complete)==24 else 'partial','completedEpisodes':len(complete),'expectedEpisodes':24,'nativeFramesDecoded':sum(x['nativeFramesDecoded'] for x in complete),'jpg60HzEntries':sum(x['samplesWritten'] for x in complete),'duplicateEntries':sum(x['duplicateEntries'] for x in complete),'items':statuses})
if __name__=='__main__':main()
