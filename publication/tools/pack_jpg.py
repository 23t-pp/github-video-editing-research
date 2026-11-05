"""Read-only source packaging, explicit native JPEGs + safe tar hardlink aliases."""
import argparse, concurrent.futures, gzip, hashlib, json, os, pathlib, sqlite3, sys, tarfile, time, traceback

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2] if len(HERE.parents)>2 else HERE
SOURCE = ROOT / 'outputs/jjk-s1-workflow/素材集_60Hz_JPG'

def metadata_files(ep):
    # SQLite reader coordination files are volatile and are not library content.
    return {p.name:p for p in (SOURCE/ep).iterdir() if p.is_file() and p.suffix.lower()!='.jpg' and not p.name.endswith(('-wal','-shm','-journal'))}

def write_json(path, obj):
    tmp = path.with_suffix(path.suffix + f'.{os.getpid()}.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
    for retry in range(100):
        try: os.replace(tmp, path); return
        except PermissionError:
            if retry==99: raise
            time.sleep(0.1)

def sha_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(8*1024*1024), b''): h.update(b)
    return h.hexdigest()

def mark_ready(result,archive):
    ready=HERE/'ready';ready.mkdir(exist_ok=True)
    write_json(ready/f'{archive.name}.json',dict(state='verified',path=str(archive.resolve()),name=archive.name,bytes=result['archiveBytes'],sha256=result['archiveSha256'],release='jpg',jpgPaths=result['jpgPaths']))

def database(ep):
    return sqlite3.connect((SOURCE / ep / 'index.sqlite').as_uri() + '?mode=ro&immutable=1', uri=True)

def safe(name):
    p = pathlib.PurePosixPath(name)
    return not p.is_absolute() and all(x not in ('', '.', '..') for x in p.parts) and '\\' not in name and ':' not in name

def add_regular(tf, path, name, expected_bytes=None):
    stat = path.stat()
    if expected_bytes is not None and stat.st_size != expected_bytes: raise ValueError(f'Changed size: {path}')
    ti = tarfile.TarInfo(name); ti.size = stat.st_size; ti.mtime = int(stat.st_mtime); ti.mode = 0o644
    with path.open('rb') as f: tf.addfile(ti, f)

def pack(ep):
    if ep not in {f'S1E{n:02d}' for n in range(1,25)}:raise ValueError(f'Invalid episode ID: {ep}')
    start = time.time(); progress = HERE / f'{ep}.progress.json'
    archive = HERE / f'{ep}.tar.gz'; partial = archive.with_suffix('.gz.partial')
    report = HERE / f'{ep}.verified.json'
    if report.exists() and archive.exists():
        old = json.loads(report.read_text(encoding='utf-8'))
        if old.get('state') == 'pass' and archive.stat().st_size == old['archiveBytes'] and sha_file(archive) == old['archiveSha256']:
            mark_ready(old,archive)
            print(f'{ep} reuse verified archive', flush=True); return old
    try:
        if archive.exists():
            result=verify(ep,archive,progress,start)
            if result['archiveBytes']>=2*1024**3:raise ValueError('Archive exceeds 2GiB')
            write_json(report,result);write_json(progress,result);mark_ready(result,archive)
            print(f'{ep} existing archive verified PASS',flush=True);return result
        c = database(ep)
        native = {r[0]: r[1:] for r in c.execute('select frame,jpeg_sha256,bytes,first_path from native')}
        expected = c.execute('select count(*) from samples').fetchone()[0]
        database_paths = {r[0] for r in c.execute('select path from samples')}
        physical_paths = {p.relative_to(SOURCE / ep).as_posix() for p in (SOURCE / ep).rglob('*.jpg')}
        if physical_paths != database_paths: raise ValueError(f'Source JPG paths differ from SQLite: missing={len(database_paths-physical_paths)} extra={len(physical_paths-database_paths)}')
        write_json(progress, dict(id=ep,state='packing',done=0,total=expected,startedUnix=start))
        with partial.open('wb') as raw, gzip.GzipFile(filename='',mode='wb',compresslevel=1,fileobj=raw,mtime=0) as gz, tarfile.open(fileobj=gz,mode='w|',format=tarfile.GNU_FORMAT) as tf:
            root = tarfile.TarInfo(ep); root.type = tarfile.DIRTYPE; root.mode = 0o755; tf.addfile(root)
            for name,p in sorted(metadata_files(ep).items()):
                add_regular(tf,p,f'{ep}/{name}')
            dirs = set(); regular = links = 0
            for done, (sample, frame, duplicate, rel) in enumerate(c.execute('select sample,source_frame,duplicate,path from samples order by sample'),1):
                if sample != done-1 or not safe(rel): raise ValueError(f'Bad sample/path {sample} {rel}')
                digest, size, first = native[frame]
                directory = str(pathlib.PurePosixPath(rel).parent)
                if directory not in dirs:
                    ti=tarfile.TarInfo(f'{ep}/{directory}'); ti.type=tarfile.DIRTYPE; ti.mode=0o755; tf.addfile(ti); dirs.add(directory)
                if rel == first:
                    if duplicate: raise ValueError('Native marked duplicate')
                    add_regular(tf,SOURCE/ep/pathlib.Path(rel),f'{ep}/{rel}',size); regular += 1
                else:
                    if not duplicate: raise ValueError('Alias not marked duplicate')
                    ti=tarfile.TarInfo(f'{ep}/{rel}'); ti.type=tarfile.LNKTYPE; ti.linkname=f'{ep}/{first}'; ti.mode=0o644; tf.addfile(ti); links += 1
                if done%10000==0:
                    write_json(progress,dict(id=ep,state='packing',done=done,total=expected,regular=regular,hardlinks=links,elapsedSeconds=time.time()-start,updatedUnix=time.time()))
                    print(f'{ep} pack {done}/{expected}',flush=True)
        c.close()
        if partial.stat().st_size >= 2*1024**3: raise ValueError('Archive exceeds 2GiB release asset limit')
        os.replace(partial,archive)
        result = verify(ep,archive,progress,start)
        write_json(report,result)
        write_json(progress,result)
        mark_ready(result,archive)
        print(f'{ep} PASS bytes={result["archiveBytes"]} sha={result["archiveSha256"]}',flush=True)
        return result
    except Exception as e:
        write_json(progress,dict(id=ep,state='failed',error=str(e),traceback=traceback.format_exc(),updatedUnix=time.time()))
        raise

def verify(ep,archive,progress,start=None):
    return _verify_stream(ep,archive,progress,start or time.time())

def _verify_stream(ep,archive,progress,start):
    c=database(ep)
    native={r[0]:r[1:] for r in c.execute('select frame,jpeg_sha256,bytes,first_path from native')}
    rows=iter(c.execute('select sample,source_frame,duplicate,path from samples order by sample'))
    expected=c.execute('select count(*) from samples').fetchone()[0]
    expected_meta=metadata_files(ep)
    count=regular=links=0; seen_native={}; names=set(); metadata={}
    with tarfile.open(archive,'r|gz') as tf:
        for ti in tf:
            if not safe(ti.name) or not (ti.name==ep or ti.name.startswith(ep+'/')): raise ValueError(f'Unsafe path {ti.name}')
            if ti.name in names: raise ValueError(f'Duplicate entry {ti.name}')
            names.add(ti.name)
            if ti.isdir(): continue
            if not ti.name.endswith('.jpg'):
                rel=ti.name[len(ep)+1:]
                if rel not in expected_meta or not ti.isreg(): raise ValueError(f'Unexpected metadata {ti.name}')
                h=hashlib.sha256()
                with tf.extractfile(ti) as f:
                    for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
                digest=h.hexdigest()
                if digest!=sha_file(expected_meta[rel]): raise ValueError(f'Metadata differs {rel}')
                metadata[rel]={'bytes':ti.size,'sha256':digest}; continue
            try: sample,frame,duplicate,rel=next(rows)
            except StopIteration: raise ValueError('Too many JPGs')
            if sample!=count or rel!=f'minute-{sample//3600:03d}/F{sample:07d}.jpg' or ti.name!=f'{ep}/{rel}':raise ValueError(f'Noncontinuous/unexpected JPG {ti.name} at {count}')
            digest,size,first=native[frame]
            if ti.isreg():
                if rel!=first or duplicate or ti.size!=size:raise ValueError(f'Wrong regular JPEG {ti.name}')
                data=tf.extractfile(ti).read()
                if hashlib.sha256(data).hexdigest()!=digest:raise ValueError(f'JPEG SHA mismatch {ti.name}')
                seen_native[ti.name]=(frame,digest); regular+=1
            elif ti.islnk():
                if not safe(ti.linkname) or ti.linkname!=f'{ep}/{first}' or ti.linkname not in seen_native or seen_native[ti.linkname]!=(frame,digest) or not duplicate:raise ValueError(f'Invalid hardlink {ti.name} -> {ti.linkname}')
                links+=1
            else: raise ValueError(f'Invalid JPG entry type {ti.name}')
            count+=1
            if count%10000==0:
                write_json(progress,dict(id=ep,state='verifying',done=count,total=expected,regular=regular,hardlinks=links,updatedUnix=time.time(),elapsedSeconds=time.time()-start))
                print(f'{ep} verify {count}/{expected}',flush=True)
    if next(rows,None) is not None or count!=expected or regular!=len(native) or set(metadata)!=set(expected_meta):raise ValueError(f'Incomplete archive: paths={count}/{expected}, native={regular}/{len(native)}, metadata={set(metadata)}/{set(expected_meta)}')
    c.close()
    return dict(id=ep,state='pass',archive=archive.name,archiveBytes=archive.stat().st_size,archiveSha256=sha_file(archive),jpgPaths=count,regularJpegs=regular,hardlinkJpegs=links,sourceFrameIds=len(native),continuousSamples=True,allRegularJpegSha256MatchIndex=True,allHardlinksPointToEarlierNative=True,safeRelativePaths=True,metadata=metadata,elapsedSeconds=time.time()-start,verifiedUnix=time.time())

def pack_job(job):
    global HERE,SOURCE
    ep,source,output=job;SOURCE=pathlib.Path(source);HERE=pathlib.Path(output);HERE.mkdir(parents=True,exist_ok=True)
    return pack(ep)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--episodes',nargs='+',default=[f'S1E{i:02d}' for i in range(1,25)]);ap.add_argument('--workers',type=int,default=2);ap.add_argument('--source',type=pathlib.Path,default=SOURCE);ap.add_argument('--output',type=pathlib.Path,default=HERE);a=ap.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    with (a.output/'commands.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(argv=getattr(sys,'orig_argv',[sys.executable]+sys.argv),cwd=os.getcwd(),startedUnix=time.time()),ensure_ascii=False)+'\n')
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as pool:
        results=list(pool.map(pack_job,[(ep,str(a.source.resolve()),str(a.output.resolve())) for ep in a.episodes]))
    write_json(a.output/'last-run.json',{'state':'pass','episodes':results,'jpgPaths':sum(x['jpgPaths'] for x in results),'sourceFrameIds':sum(x['sourceFrameIds'] for x in results)})
