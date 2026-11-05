"""Python 3.9+, standard library only. Restore every 60-Hz sample path safely."""
import argparse, hashlib, json, os, pathlib, shutil, sqlite3, tarfile, time

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

def safe(name):
    p=pathlib.PurePosixPath(name)
    return bool(name) and not p.is_absolute() and all(x not in ('','..','.') for x in p.parts) and '\\' not in name and ':' not in name

def under(root,name):
    if not safe(name):raise ValueError(f'Unsafe archive path: {name}')
    p=root.joinpath(*pathlib.PurePosixPath(name).parts)
    if not p.resolve().is_relative_to(root):raise ValueError(f'Path escapes output: {name}')
    current=p
    while current!=root:
        if current.is_symlink():raise ValueError(f'Symlink in output path: {current}')
        current=current.parent
    return p

def restore(archive,destination,manifest,resume=False,force_copy=False):
    ep=archive.name.removesuffix('.tar.gz')
    if len(ep)!=5 or not ep.startswith('S1E') or not ep[3:].isdigit():raise ValueError(f'Unexpected episode archive name: {archive.name}')
    if manifest is not None:
        entry=next((x for x in manifest['episodes'] if x['archive']==archive.name),None)
        if not entry:raise ValueError('Archive absent from manifest')
        if archive.stat().st_size!=entry['archiveBytes'] or digest(archive)!=entry['archiveSha256']:raise ValueError('Archive SHA/size mismatch')
    destination.mkdir(parents=True,exist_ok=True);root=destination.resolve()
    epdir=under(root,ep)
    if epdir.exists() and not resume:raise FileExistsError(f'{epdir} exists; use --resume to validate and resume')
    seen=set();native_hashes={};link_targets={};jpg_names=set();links=copies=regular=0;start=time.time()
    with tarfile.open(archive,'r|gz') as tf:
        for ti in tf:
            if not (ti.name==ep or ti.name.startswith(ep+'/')) or ti.name in seen:raise ValueError(f'Unexpected/duplicate entry {ti.name}')
            target=under(root,ti.name)
            if ti.isdir():target.mkdir(parents=True,exist_ok=True);seen.add(ti.name);continue
            target.parent.mkdir(parents=True,exist_ok=True)
            if ti.isreg():
                h=hashlib.sha256();temporary=target.with_name(target.name+'.restoring')
                if temporary.is_symlink():raise ValueError('Unsafe temporary path')
                with tf.extractfile(ti) as source, temporary.open('wb') as out:
                    for b in iter(lambda:source.read(1024*1024),b''):h.update(b);out.write(b)
                os.replace(temporary,target)
                if target.stat().st_size!=ti.size:raise ValueError(f'Truncated file {ti.name}')
                if ti.name.endswith('.jpg'):native_hashes[ti.name]=(h.hexdigest(),ti.size);regular+=1
            elif ti.islnk():
                if ti.linkname not in native_hashes:raise ValueError(f'Hardlink must point to preceding regular JPEG: {ti.name}')
                source=under(root,ti.linkname)
                if not ti.name.endswith('.jpg') or not ti.linkname.startswith(ep+'/'):raise ValueError('Invalid hardlink scope')
                link_targets[ti.name]=ti.linkname
                if target.exists():
                    if not resume:raise FileExistsError(target)
                    if digest(target)!=native_hashes[ti.linkname][0]:target.unlink()
                if not target.exists():
                    try:
                        if force_copy:raise OSError('copy requested')
                        os.link(source,target);links+=1
                    except OSError:shutil.copyfile(source,target);copies+=1
            else:raise ValueError(f'Unsupported archive member type {ti.name}')
            if ti.name.endswith('.jpg'):jpg_names.add(ti.name)
            seen.add(ti.name)
            if len(jpg_names) and len(jpg_names)%10000==0:print(f'{ep}: restored {len(jpg_names)} JPEG paths',flush=True)
    c=sqlite3.connect((epdir/'index.sqlite').as_uri()+'?mode=ro&immutable=1',uri=True)
    native={r[0]:r[1:] for r in c.execute('select frame,jpeg_sha256,bytes,first_path from native')}
    for frame,(sha,size,first) in native.items():
        if native_hashes.get(f'{ep}/{first}')!=(sha,size):raise ValueError(f'Native JPEG SHA mismatch at source frame {frame}')
    count=0
    for sample,frame,duplicate,rel in c.execute('select sample,source_frame,duplicate,path from samples order by sample'):
        name=f'{ep}/{rel}';target=under(root,name)
        sha,size,first=native[frame]
        if sample!=count or rel!=f'minute-{sample//3600:03d}/F{sample:07d}.jpg' or name not in jpg_names or not target.is_file() or target.stat().st_size!=size:raise ValueError(f'Missing/invalid sample {sample}: {rel}')
        if rel==first:
            if duplicate or native_hashes.get(name)!=(sha,size):raise ValueError(f'Invalid original JPEG at sample {sample}')
        elif not duplicate or link_targets.get(name)!=f'{ep}/{first}':raise ValueError(f'Hardlink maps to wrong source frame at sample {sample}')
        count+=1
    if count!=len(jpg_names) or len(native)!=regular:raise ValueError('Unexpected or missing JPG entries')
    c.close()
    result={'episode':ep,'state':'pass','jpgPaths':count,'sourceFrameIds':regular,'createdHardlinks':links,'copiedFallbacks':copies,'allPathsExist':True,'nativeJpegSha256Verified':True,'elapsedSeconds':time.time()-start}
    report=root/f'{ep}.restore-report.json';report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False),flush=True);return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('archives',nargs='+',type=pathlib.Path);p.add_argument('--destination',required=True,type=pathlib.Path);p.add_argument('--manifest',type=pathlib.Path);p.add_argument('--resume',action='store_true');p.add_argument('--copy',action='store_true',help='Use copies instead of hardlinks (larger disk use)');a=p.parse_args()
    manifest=json.loads(a.manifest.read_text(encoding='utf-8')) if a.manifest else None
    expanded=[]
    for archive in a.archives:
        if archive.is_dir():expanded.extend(sorted(archive.glob('S1E??.tar.gz')))
        else:expanded.append(archive)
    if not expanded:p.error('No episode archives found')
    results=[restore(x,a.destination,manifest,a.resume,a.copy) for x in expanded]
    print(f"PASS: {len(results)} episodes, {sum(x['jpgPaths'] for x in results)} JPG paths, {sum(x['sourceFrameIds'] for x in results)} source frames")
