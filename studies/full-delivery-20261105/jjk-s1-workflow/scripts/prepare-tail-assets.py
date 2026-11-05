"""Original high-resolution native core → explicit source-PTS sample map → R4 clips.

No old media is overwritten. This script must be run after independent R4
design precheck; --retrieve is an explicit execution switch.
"""
from pathlib import Path
from fractions import Fraction
import argparse,subprocess,json,re,hashlib,math,os,shutil,struct
A=argparse.ArgumentParser();A.add_argument('--retrieve',action='store_true');a=A.parse_args()
R=Path(__file__).resolve().parent.parent;H=R/'hyperframes';W=R.parents[1]/'work/jjk-s1-workflow/tail-native-final';E=R/'evidence/tail-retrieval';E.mkdir(exist_ok=True)
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';FP='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=json.loads((R/'loops/loop-04/revision-spec.json').read_text(encoding='utf-8'));manifest=R/'data/tail-action-candidates.json';assert sha(manifest)==spec['tailMaterialSha256']
cores={s['candidateId']:s for s in json.loads(manifest.read_text(encoding='utf-8'))['items']};inventory={s['id']:s for s in json.loads((R/'data/source-inventory.json').read_text(encoding='utf-8'))['items']}
if not a.retrieve:raise SystemExit('Prepared code only. Use --retrieve after independent design precheck.')
results=[]
for s in spec['tailActions']:
 core=cores[s['candidateId']];asset=s['assetId'];N=s['outputFrames'];folder=W/asset;native=folder/'native';selected=folder/'selected';native.mkdir(parents=True,exist_ok=True);selected.mkdir(exist_ok=True)
 expected=core['sourcePtsSeconds'];tb=Fraction(inventory[s['sourceId']]['timeBase']);first,last=expected[0],expected[-1];seek=max(0,first-.3)
 # trim end is exclusive and rescaled to source TB; a quarter native frame
 # margin includes the rounded last curated PTS without admitting the next.
 margin=float(1/Fraction(core['sourceNativeFps']))*.25
 decode=[FF,'-v','info','-threads','1','-filter_threads','1','-copyts','-ss',f'{seek:.9f}','-t',f'{last-first+.7:.9f}','-i',s['sourcePath'],'-an','-vf',f'trim=start={first-margin:.9f}:end={last+margin:.9f},showinfo,scale=in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24','-fps_mode','passthrough','-c:v','png','-threads','1','-compression_level','1','-f','image2pipe','pipe:1']
 cache=folder/'native-proof.json'
 if cache.exists():
  cp=json.loads(cache.read_text(encoding='utf-8'));assert cp['command']==decode
  for f in cp['files']:assert sha(folder/f['path'])==f['sha256']
  pts=cp['sourcePtsSeconds']
 else:
  assert not list(native.glob('native_*.png')),'incomplete native cache requires explicit inspection, no silent replacement'
  run=subprocess.run(decode,capture_output=True);log=run.stderr.decode(errors='replace');(E/f'{asset}-native-final.log').write_text(log,encoding='utf-8');assert run.returncode==0,log[-2000:]
  blob=run.stdout;pos=0;image_count=0
  while pos<len(blob):
   assert blob[pos:pos+8]==b'\x89PNG\r\n\x1a\n';end=pos+8
   while end<len(blob):
    length=struct.unpack_from('>I',blob,end)[0];kind=blob[end+4:end+8];end+=length+12
    if kind==b'IEND':break
   (native/f'native_{image_count:06}.png').write_bytes(blob[pos:end]);pos=end;image_count+=1
  assert pos==len(blob) and image_count==len(expected),(asset,image_count,len(expected))
  values=[(int(m.group(1)),int(m.group(2))) for m in re.finditer(r'\bn:\s*(\d+).*?\bpts:\s*(-?\d+)',log)]
  assert [n for n,_ in values]==list(range(len(expected))),(asset,len(values),len(expected))
  pts=[float(p*tb) for _,p in values];assert all(abs(x-y)<.000002 for x,y in zip(pts,expected)),(asset,pts,expected)
  files=sorted(native.glob('native_*.png'));assert len(files)==len(pts)
  cp={'command':decode,'timeBase':str(tb),'sourcePtsSeconds':pts,'sourcePtsIntegers':[p for _,p in values],'files':[{'path':f.relative_to(folder).as_posix(),'sha256':sha(f)} for f in files]};cache.write_text(json.dumps(cp,indent=2),encoding='utf-8')
 files=sorted(native.glob('native_*.png'));mapping=[]
 for f in range(N):
  j=math.floor(f*(len(files)-1)/(N-1)+.5);dest=selected/f'{f:06}.png'
  if not dest.exists():
   try:os.link(files[j],dest)
   except OSError:shutil.copyfile(files[j],dest)
  assert sha(dest)==sha(files[j]);mapping.append({'preparedFrame':f,'nativeCoreIndex':j,'sourcePtsSeconds':pts[j],'duplicateOfPrevious':bool(mapping and mapping[-1]['nativeCoreIndex']==j)})
 is_red=s['candidateId']=='S1C091';height,top=(944,68) if is_red else (960,60)
 target=H/f'assets/shots/{asset}.mp4';assert not target.exists(),'R4 prepared media already exists; preserve and inspect instead of overwriting'
 encode=[FF,'-v','error','-threads','1','-filter_threads','1','-framerate','24','-start_number','0','-i',str(selected/'%06d.png'),'-an','-vf',f'crop=1920:{height}:0:0,pad=1920:1080:0:{top}:black,scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p','-frames:v',str(N),'-c:v','libx264','-threads','1','-preset','fast','-crf','17','-bf','0','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','frag_keyframe+empty_moov+default_base_moof','-f','mp4','pipe:1']
 r=subprocess.run(encode,capture_output=True);assert r.returncode==0,r.stderr.decode(errors='replace');target.write_bytes(r.stdout)
 probe=json.loads(subprocess.run([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(target)],capture_output=True,check=True).stdout);v=next(v for v in probe['streams'] if v['codec_type']=='video');assert int(v['nb_read_frames'])==N and v['width']==1920 and v['height']==1080
 nominal=(s['sourceCoreSeconds'][1]-s['sourceCoreSeconds'][0])/(N/24)
 result={'candidateId':s['candidateId'],'sourceId':s['sourceId'],'episode':inventory[s['sourceId']]['episodeNumber'],'sourcePath':s['sourcePath'],'sourceCoreSeconds':s['sourceCoreSeconds'],'actualSourcePtsSeconds':pts,'outputStartFrame':s['outputStartFrame'],'outputFrames':N,'asset':{'id':asset,'asset':f'assets/shots/{asset}.mp4','frames':N,'usableFrames':N,'sha256':sha(target),'sourceId':s['sourceId'],'sourcePath':s['sourcePath'],'sourceIn':s['sourceCoreSeconds'][0],'sourceFps':core['sourceNativeFps'],'description':core['observedMovement']},'assetStartFrame':0,'nominalCoreWindowRate':nominal,'effectiveFirstLastPtsRate':(pts[-1]-pts[0])/((N-1)/24),'sourceSampleMapping':mapping,'cropOriginal':[0,0,1920,height],'padTop':top,'characters':s['characters'],'characterConfidence':s['characterConfidence'],'observedMovement':s['observedMovement'],'evidence':s['evidence'],'nativeProof':cache.as_posix(),'decodeCommand':decode,'encodeCommand':encode,'ffprobe':probe,'status':'actual original prepared created; all-frame subtitle/geometry review pending'}
 (E/f'{asset}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');results.append(result)
 print(f'PREPARED {asset} {len(pts)}native→{N}output; duplicates={sum(m["duplicateOfPrevious"] for m in mapping)}; crop{height}/pad{top}',flush=True)
(R/'data/retrieved-assets-loop4.json').write_text(json.dumps({'items':results,'scope':'R4 new3 original cores; explicit native sourcePTS selection; old loop media untouched','nativeCount':sum(len(v['actualSourcePtsSeconds']) for v in results),'outputCount':sum(v['outputFrames'] for v in results)},ensure_ascii=False,indent=2),encoding='utf-8')
