"""Independent read-only episode pilot audit; never writes source/library files."""
from pathlib import Path
from fractions import Fraction
from PIL import Image
import argparse,json,sqlite3,hashlib,os,io,time
from datetime import datetime,timezone,timedelta
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('episode',nargs='?',default='S1E01');a=p.parse_args()
E=R/'素材集_60Hz_JPG'/a.episode;S=json.loads((E/'progress.json').read_text(encoding='utf-8'))
assert S['state']=='complete',S['state']
started=time.time();db=sqlite3.connect(f'file:{(E/"index.sqlite").as_posix()}?mode=ro',uri=True)
tb=Fraction(S['sourceTimeBase']);first=S['firstSourcePts'];n=S['expectedSamples'];native=S['nativeFramesDecoded']
assert S['samplesWritten']==n
assert db.execute('SELECT COUNT(*),MIN(sample),MAX(sample) FROM samples').fetchone()==(n,0,n-1)
assert db.execute('SELECT COUNT(*),MIN(frame),MAX(frame) FROM native').fetchone()==(native,0,native-1)
# Each sample belongs to the native display interval [pts_i,pts_i+1).
bad_interval=db.execute('SELECT COUNT(*) FROM samples s JOIN native n ON n.frame=s.source_frame LEFT JOIN native nx ON nx.frame=n.frame+1 WHERE s.sample*? < (n.pts-?)*?*60 OR (nx.frame IS NOT NULL AND s.sample*?>=(nx.pts-?)*?*60)',(tb.denominator,first,tb.numerator,tb.denominator,first,tb.numerator)).fetchone()[0]
assert bad_interval==0,bad_interval
paths=[entry for folder in E.glob('minute-*') for entry in os.scandir(folder) if entry.name.endswith('.jpg')]
assert len(paths)==n,(len(paths),n)
native_info={};bad_sha=[];marker_checked=0
for f,pts,h,size,rel in db.execute('SELECT frame,pts,jpeg_sha256,bytes,first_path FROM native ORDER BY frame'):
    path=E/rel;data=path.read_bytes();actual=hashlib.sha256(data).hexdigest()
    if actual!=h:bad_sha.append(f)
    with Image.open(io.BytesIO(data)) as im:
        assert im.format=='JPEG' and im.size==(640,360);im.verify()
    st=path.stat();native_info[f]=(st.st_ino,st.st_dev,st.st_size,rel);assert st.st_size==size
    marker_checked+=1
assert not bad_sha,bad_sha[:10]
alias_mismatch=[];copy_entries=0;duplicate_flag_mismatch=[];previous_source=None
for sample,source_frame,duplicate,rel in db.execute('SELECT sample,source_frame,duplicate,path FROM samples ORDER BY sample'):
    path=E/rel;st=path.stat();ino,dev,size,primary=native_info[source_frame]
    assert st.st_size==size
    is_primary=(rel==primary)
    if bool(duplicate)==is_primary:duplicate_flag_mismatch.append(sample)
    if (st.st_ino,st.st_dev)!=(ino,dev):
        # A real copy fallback is allowed only when its bytes still match.
        copy_entries+=1
        if hashlib.sha256(path.read_bytes()).hexdigest()!=hashlib.sha256((E/primary).read_bytes()).hexdigest():alias_mismatch.append(sample)
assert not alias_mismatch and not duplicate_flag_mismatch
assert copy_entries==S['hardlinkFallbackCopies'],(copy_entries,S['hardlinkFallbackCopies'])
decode_samples=sorted(set(S['jpgDecodeCheckedSampleIndices']+[0,n-1]))
for sample in decode_samples:
    rel=db.execute('SELECT path FROM samples WHERE sample=?',(sample,)).fetchone()[0]
    with Image.open(E/rel) as im:im.load();assert im.size==(640,360)
inv=json.loads((R/'data/source-inventory.json').read_text(encoding='utf-8'));item=next(x for x in inv['items'] if x['id']==a.episode)
with Path(item['localPath']).open('rb') as file:source_hash=hashlib.file_digest(file,'sha256').hexdigest()
assert source_hash==S['sourceSha256']
cfg_hash=hashlib.sha256((R/'data/run-config.json').read_bytes()).hexdigest();assert cfg_hash==S['configSha256']
out={'reviewer':'/root/s1_design_auditor','episode':a.episode,'reviewedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),'status':'pass','scope':'A试集独立结构/指纹/文件ID全检，JPG像素解码抽检；不是全季完成或全唯一JPG像素解码','sourceSha256':source_hash,'configSha256':cfg_hash,'progressSha256':hashlib.sha256((E/'progress.json').read_bytes()).hexdigest(),'expectedSamples':n,'actualSamplePaths':len(paths),'nativeFrames':native,'allSampleIntervalsChecked':True,'badSampleIntervals':bad_interval,'allNativeJpegShaAndMarkerChecks':marker_checked,'allSampleFileIdOrCopyByteChecks':n,'copyEntries':copy_entries,'fullPixelDecodeCheckedSamples':decode_samples,'allUniqueFullPixelDecodePerformed':False,'elapsedSeconds':time.time()-started,'spaceFreeBytesAfterReview':__import__('shutil').disk_usage(R).free,'remainingBeforeFinalDatasetAcceptance':['full-season physical completion','full unique JPEG pixel decode and final all-sample mapping audit','JSONL export interface','semantic tags have independent viewed evidence']}
(R/f'reviews/{a.episode}-试集审核.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:out[k] for k in ['status','expectedSamples','actualSamplePaths','nativeFrames','badSampleIntervals','copyEntries','elapsedSeconds']},ensure_ascii=False))
