"""Independent streaming tar audit against sealed source SQLite. No source writes."""
import argparse,hashlib,json,os,tarfile,time,shutil,random
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).parent
def hashfile(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def safe(name):
 p=PurePosixPath(name)
 return bool(name) and not p.is_absolute() and '..' not in p.parts and '\\' not in name and ':' not in name
def audit(archive,ep,extract_full=False):
 import sqlite3
 started=time.time();src=ROOT/'outputs/jjk-s1-workflow/素材集_60Hz_JPG'/ep
 c=sqlite3.connect(f'file:{src.as_posix()}/index.sqlite?mode=ro&immutable=1',uri=True)
 samples={p:(f,d) for _,f,d,p in c.execute('select sample,source_frame,duplicate,path from samples')}
 native={f:(sha,b,p) for f,sha,b,p in c.execute('select frame,jpeg_sha256,bytes,first_path from native')};c.close()
 seen={}; seen_all=set();errors=[];regular=hardlinks=jpgs=byte_count=0;sample_data={};first,last=next(iter(samples)),next(reversed(samples))
 wanted={first,last};rng=random.Random(ep)
 wanted.update(rng.sample(list(samples),10));wanted_frames={samples[x][0] for x in wanted};frame_data={}
 restore=OUT/'extracted'/ep
 if extract_full:restore.mkdir(parents=True,exist_ok=True)
 with tarfile.open(archive,'r|gz') as tf:
  for t in tf:
   name=t.name
   if not safe(name):errors.append('unsafe entry '+name);continue
   if name in seen_all:errors.append('duplicate tar entry '+name)
   seen_all.add(name)
   if t.issym() or t.isdev() or t.isfifo():errors.append('unexpected special entry '+name);continue
   parts=PurePosixPath(name).parts
   # Accept source root with or without project prefix; episode must be an exact component.
   if ep not in parts:
    if name.lower().endswith('.jpg'):errors.append('jpg outside episode '+name)
    if t.isfile():
     f=tf.extractfile(t)
     while f.read(1048576):pass
    continue
   sub='/'.join(parts[parts.index(ep)+1:])
   if not sub.lower().endswith('.jpg'):
    if t.isfile():
     f=tf.extractfile(t)
     while f.read(1048576):pass
    continue
   jpgs+=1
   if sub not in samples:errors.append('unexpected JPG '+name);continue
   frame,duplicate=samples[sub];sha,size,first_path=native[frame]
   dest=restore/sub
   if extract_full:dest.parent.mkdir(parents=True,exist_ok=True)
   if t.isfile():
    regular+=1;h=hashlib.sha256();data=[];f=tf.extractfile(t)
    out=dest.open('wb') if extract_full else None
    while True:
     b=f.read(1048576)
     if not b:break
     h.update(b);byte_count+=len(b)
     if frame in wanted_frames:data.append(b)
     if out:out.write(b)
    if out:out.close()
    actual=h.hexdigest()
    if t.size!=size or actual!=sha:errors.append('regular SHA/size mismatch '+name)
    seen[name]=(frame,actual,size)
    if data:frame_data[frame]=b''.join(data)
    if sub in wanted:sample_data[sub]=frame_data[frame]
   elif t.islnk():
    hardlinks+=1
    if not safe(t.linkname) or t.linkname not in seen:errors.append('unsafe/missing/forward hardlink '+name+' -> '+t.linkname);continue
    target=seen[t.linkname]
    if target!=(frame,sha,size):errors.append('hardlink source/SHA mismatch '+name)
    seen[name]=target
    if extract_full:
     tp=PurePosixPath(t.linkname).parts;target_dest=restore/Path(*tp[tp.index(ep)+1:]);os.link(target_dest,dest)
    if sub in wanted:
     sample_data[sub]=frame_data[frame]
   else:errors.append('unsupported JPG entry '+name)
 missing=set(samples)-{'/'.join(PurePosixPath(n).parts[PurePosixPath(n).parts.index(ep)+1:]) for n in seen if ep in PurePosixPath(n).parts}
 if regular!=len(native):errors.append('regular native count mismatch')
 if hardlinks!=len(samples)-len(native):errors.append('hardlink duplicate count mismatch')
 if missing:errors.append('missing JPG count '+str(len(missing)))
 # Decode reproducible random material and verify independently restored aliases/copies.
 from PIL import Image
 import io
 decoded=[]
 for sub,data in sample_data.items():
  im=Image.open(io.BytesIO(data));im.load()
  if im.size!=(640,360) or im.format!='JPEG':errors.append('decode mismatch '+sub)
  decoded.append(sub)
 extraction_count=None;hardlink_test=None
 if extract_full:
  extraction_count=sum(len(fs) for _,_,fs in os.walk(restore))
  if extraction_count!=len(samples):errors.append('extracted count mismatch')
  alias=next(p for p,(fr,dup) in samples.items() if dup)
  primary=native[samples[alias][0]][2]
  ap,pp=restore/alias,restore/primary
  copied=OUT/'copy-fallback'/ep/'copy.jpg';copied.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ap,copied)
  hardlink_test={'alias':alias,'primary':primary,'sameFile':os.path.samefile(ap,pp),'copiedHashMatches':hashfile(copied)==native[samples[alias][0]][0],'copyIsIndependent':not os.path.samefile(ap,copied)}
  if not all(hardlink_test[x] for x in ['sameFile','copiedHashMatches','copyIsIndependent']):errors.append('hardlink/copy restore test failed')
 result={'archive':str(Path(archive).resolve()),'episode':ep,'archiveBytes':Path(archive).stat().st_size,'archiveSha256':hashfile(Path(archive)),'expectedJpg':len(samples),'expectedNative':len(native),'tarEntries':len(seen_all),'jpgEntries':jpgs,'regularJpg':regular,'hardlinkJpg':hardlinks,'regularBytesRead':byte_count,'missingJpg':len(missing),'decodedSamples':decoded,'actualExtractionJpgCount':extraction_count,'hardlinkCopyRestoreTest':hardlink_test,'errors':errors,'pass':not errors and jpgs==len(samples),'elapsedSeconds':time.time()-started}
 (OUT/(ep+'-archive-audit.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({k:result[k] for k in ['episode','jpgEntries','regularJpg','hardlinkJpg','pass','elapsedSeconds']},ensure_ascii=False),flush=True)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('archive');p.add_argument('episode');p.add_argument('--extract-full',action='store_true');a=p.parse_args();audit(a.archive,a.episode,a.extract_full)
