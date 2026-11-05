"""Restore test: two real source JPEGs, all six sample paths, hardlink and copy modes."""
import hashlib, importlib.util, io, json, os, pathlib, sqlite3, tarfile, time
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('restore_jpg',HERE/'restore_jpg.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source=HERE.parents[2]/'outputs/jjk-s1-workflow/素材集_60Hz_JPG/S1E01'
work=HERE/'restore-smoke'/str(time.time_ns());work.mkdir(parents=True)
c=sqlite3.connect((source/'index.sqlite').as_uri()+'?mode=ro&immutable=1',uri=True)
native=c.execute('select frame,jpeg_sha256,bytes,first_path from native where frame<2 order by frame').fetchall()
samples=c.execute('select sample,source_frame,duplicate,path from samples where sample<6 order by sample').fetchall();c.close()
db=work/'index.sqlite';c=sqlite3.connect(db)
c.execute('create table native(frame integer primary key,jpeg_sha256 text,bytes integer,first_path text)')
c.execute('create table samples(sample integer primary key,source_frame integer,duplicate integer,path text)')
c.executemany('insert into native values (?,?,?,?)',native);c.executemany('insert into samples values (?,?,?,?)',samples);c.commit();c.close()
archive=work/'S1E99.tar.gz'
with tarfile.open(archive,'w:gz') as tf:
    tf.add(db,arcname='S1E99/index.sqlite')
    for sample,frame,duplicate,rel in samples:
        if duplicate:
            ti=tarfile.TarInfo('S1E99/'+rel);ti.type=tarfile.LNKTYPE;ti.linkname='S1E99/'+native[frame][3];tf.addfile(ti)
        else:tf.add(source/rel,arcname='S1E99/'+rel)
results=[]
for mode in ('hardlinks','copies'):
    result=m.restore(archive,work/mode,None,force_copy=mode=='copies')
    for sample,frame,duplicate,rel in samples:
        p=work/mode/'S1E99'/rel
        assert m.digest(p)==native[frame][1]
    p0=work/mode/'S1E99'/samples[0][3];p1=work/mode/'S1E99'/samples[1][3]
    assert os.path.samefile(p0,p1)==(mode=='hardlinks')
    assert result['jpgPaths']==6 and result['sourceFrameIds']==2
    results.append({'mode':mode,**result})
report={'state':'pass','source':'first six actual S1E01 samples; two original JPEG bytes','verifiedHardlinkIdentity':True,'verifiedForcedCopyFallback':True,'results':results,'testDirectory':str(work)}
(HERE/'restore-smoke-test.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
