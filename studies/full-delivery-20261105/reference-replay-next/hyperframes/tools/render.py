"""Run the real HyperFrames CLI in bounded chunks, then encode its frames with the library BGM."""
from pathlib import Path
import argparse,json,subprocess,os,sys,shutil,struct,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from composition import build,load_edit,save_editable
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';FP='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'
NODE='C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
CLI='C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/bin/hyperframes.mjs'
ENV={**os.environ,'HYPERFRAMES_BROWSER_PATH':'C:/Program Files/Google/Chrome/Application/chrome.exe','HYPERFRAMES_FFMPEG_PATH':FF,'HYPERFRAMES_FFPROBE_PATH':FP}
RGB='scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p'
VOPTS=['-c:v','libx264','-threads','3','-preset','fast','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv']
def capture(cmd):
    p=subprocess.run(cmd,capture_output=True)
    if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-3000:])
    return p.stdout
def extract(asset,indices,folder):
    first,last=min(indices),max(indices)+1
    vf=f'trim=start_frame={first}:end_frame={last},scale=in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24'
    blob=capture([FF,'-v','error','-threads','2','-filter_threads','1','-i',str(ROOT/asset['asset']),'-an','-vf',vf,'-fps_mode','passthrough','-c:v','png','-threads','1','-compression_level','1','-f','image2pipe','pipe:1'])
    pos=0
    for n in range(first,last):
        assert blob[pos:pos+8]==b'\x89PNG\r\n\x1a\n',(asset['id'],n,'missing image')
        end=pos+8
        while end<len(blob):
            size=struct.unpack_from('>I',blob,end)[0];kind=blob[end+4:end+8];end+=size+12
            if kind==b'IEND':break
        if n in indices:(folder/f'{asset["id"]}-{n:03}.png').write_bytes(blob[pos:end])
        pos=end
    assert pos==len(blob)
def probe(p):return json.loads(capture([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))
def encode(frames,start,count,output,audio=None):
    args=[FF,'-v','error','-threads','2','-filter_threads','1','-framerate','25','-start_number',str(start),'-i',str(frames/'frame_%06d.png')]
    if audio:args+=['-i',str(audio),'-map','0:v:0','-map','1:a:0']
    args+=['-vf',RGB,'-frames:v',str(count),*VOPTS]
    if audio:args+=['-c:a','aac','-b:a','256k','-ar','48000','-t','30']
    else:args+=['-an']
    args+=['-f','mp4','-fd','1','fd:']
    with output.open('wb') as f:subprocess.run(args,stdout=f,check=True)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,default=ROOT/'.render-cache');ap.add_argument('--chunks',type=int,nargs='+');ap.add_argument('--force',action='store_true');ap.add_argument('--encode-only',action='store_true');args=ap.parse_args()
    plan=load_edit();A={a['id']:a for a in plan['assets']};work=args.work.resolve();work.mkdir(parents=True,exist_ok=True)
    result=work/'master-frames';result.mkdir(exist_ok=True);fx=ROOT.parent/'occ-effects';fx.mkdir(exist_ok=True)
    if not args.encode_only:
        for chunk,first in enumerate(range(0,750,50)):
            if args.chunks is not None and chunk not in args.chunks:continue
            last=min(750,first+50);html,needed,copies=build(plan,first,last,True)
            assets=sorted({a for a,n in needed});deps=[ROOT/'composition.py',ROOT/'assets/gsap.min.js',*[ROOT/A[a]['asset'] for a in assets],*[ROOT/p for p in sorted(copies)]]
            if (ROOT/'motion/portal-matrices.json').exists():deps.append(ROOT/'motion/portal-matrices.json')
            digest=hashlib.sha256(html.encode())
            for d in deps:digest.update(hashlib.sha256(d.read_bytes()).digest())
            key=digest.hexdigest();folder=work/f'chunk-{chunk:02}';folder.mkdir(exist_ok=True);cache=folder/'cache-key.txt'
            movie=fx/f'HF-{first:03}-{last:03}.mp4'
            if not args.force and cache.exists() and cache.read_text()==key and movie.exists() and all((result/f'frame_{f+1:06}.png').exists() for f in range(first,last)):
                print(f'CACHED HyperFrames [{first},{last})',flush=True);continue
            run=1
            while (folder/f'pass-{run}').exists():run+=1
            project=folder/f'pass-{run}';framefolder=project/'assets/frames';framefolder.mkdir(parents=True)
            (project/'index.html').write_text(html,encoding='utf-8')
            for p in ['hyperframes.json','DESIGN.md','assets/gsap.min.js',*copies]:
                dest=project/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p,dest)
            for id in assets:extract(A[id],{n for a,n in needed if a==id},framefolder)
            out=folder/f'png-{run}';log=folder/f'hyperframes-{run}.log'
            command=[NODE,CLI,'render',str(project),'--fps','25','--format','png-sequence','--workers','1','--low-memory-mode','--sdr','--experimental-fast-capture=false','--no-best-effort','--output',str(out)]
            print(f'RENDER HyperFrames [{first},{last}) / {len(needed)} source frames / {len(copies)} alpha frames',flush=True)
            with log.open('wb') as f:p=subprocess.run(command,env=ENV,stdout=f,stderr=subprocess.STDOUT)
            if p.returncode:raise RuntimeError(log.read_text(encoding='utf-8',errors='replace')[-3500:])
            names=sorted(out.glob('frame_*.png'));assert len(names)==last-first,(chunk,len(names))
            for i,p in enumerate(names):shutil.copy2(p,result/f'frame_{first+i+1:06}.png')
            encode(result,first+1,last-first,movie);cache.write_text(key)
            print(f'DONE HyperFrames [{first},{last})',flush=True)
        save_editable(build(plan)[0])
    if args.chunks is None:
        assert all((result/f'frame_{f+1:06}.png').exists() for f in range(750))
        master=ROOT.parent/'越界_V07复刻.mp4';encode(result,1,750,master,ROOT/plan['audio']['master'])
        info=probe(master);v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
        assert int(v['nb_read_frames'])==750 and v['avg_frame_rate']=='25/1'
        assert int(a['sample_rate'])==48000 and a['channels']==2
        assert all(abs(float(x['duration'])-30)<.00001 for x in [v,a,info['format']])
        report={'sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'frames':750,'duration':30,'hyperframesChunks':15,'ffprobe':info}
        (ROOT.parent/'成片验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print('VERIFIED',master,flush=True)
if __name__=='__main__':main()
