"""Render the actual HyperFrames composition in bounded 72-frame chunks."""
from pathlib import Path
import argparse,json,subprocess,os,sys,shutil,struct,hashlib
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from composition import build,load_edit,save_editable
FF=os.environ.get('FFMPEG_PATH','C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe')
FP=os.environ.get('FFPROBE_PATH','C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe')
NODE=os.environ.get('JJK_NODE','C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
CLI=os.environ.get('HYPERFRAMES_CLI','C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/bin/hyperframes.mjs')
ENV={**os.environ,'HYPERFRAMES_BROWSER_PATH':os.environ.get('HYPERFRAMES_BROWSER_PATH','C:/Program Files/Google/Chrome/Application/chrome.exe'),'HYPERFRAMES_FFMPEG_PATH':FF,'HYPERFRAMES_FFPROBE_PATH':FP}
VOPTS=['-c:v','libx264','-threads','3','-preset','fast','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-bf','0']
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
        assert blob[pos:pos+8]==b'\x89PNG\r\n\x1a\n',(asset['id'],n,'missing source frame')
        end=pos+8
        while end<len(blob):
            size=struct.unpack_from('>I',blob,end)[0];kind=blob[end+4:end+8];end+=size+12
            if kind==b'IEND':break
        if n in indices:(folder/f'{asset["id"]}-{n:04}.png').write_bytes(blob[pos:end])
        pos=end
    assert pos==len(blob)
def encode(frames,start,count,output,fps,audio=None):
    cmd=[FF,'-v','error','-threads','2','-filter_threads','1','-framerate',str(fps),'-start_number',str(start),'-i',str(frames/'frame_%06d.png')]
    if audio:cmd+=['-i',str(audio),'-map','0:v:0','-map','1:a:0']
    cmd+=['-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p','-frames:v',str(count),*VOPTS]
    if audio:cmd+=['-c:a','aac','-b:a','256k','-ar','48000','-t',str(count/fps)]
    else:cmd+=['-an']
    cmd+=['-f','mp4']
    if not audio:cmd+=['-movflags','frag_keyframe+empty_moov+default_base_moof']
    cmd+=['-fd','1','fd:']
    with output.open('wb') as f:subprocess.run(cmd,stdout=f,check=True)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--work',type=Path,default=ROOT/'.render-cache');parser.add_argument('--chunks',type=int,nargs='+');parser.add_argument('--force',action='store_true');parser.add_argument('--encode-only',action='store_true');args=parser.parse_args()
    plan=load_edit();fps=plan['fps'];duration=plan['durationFrames'];assets={a['id']:a for a in plan['assets']};work=args.work.resolve();work.mkdir(parents=True,exist_ok=True)
    result=work/'master-frames';result.mkdir(exist_ok=True);fx=ROOT.parent/'occ-effects';fx.mkdir(exist_ok=True)
    if not args.encode_only:
        for chunk,first in enumerate(range(0,duration,72)):
            if args.chunks is not None and chunk not in args.chunks:continue
            last=min(duration,first+72);html,needed,copies=build(plan,first,last,True)
            deps=[ROOT/'composition.py',ROOT/'typefx.py',ROOT/'barlow-glyphs.json',ROOT/'layoutfx.py',ROOT/'assets/gsap.min.js',*[ROOT/assets[a]['asset'] for a in sorted({a for a,n in needed})],*[ROOT/p for p in sorted(copies)],*sorted((ROOT/'assets/fonts').glob('*'))]
            digest=hashlib.sha256(html.encode())
            for path in deps:digest.update(hashlib.sha256(path.read_bytes()).digest())
            key=digest.hexdigest();folder=work/f'chunk-{chunk:02}';folder.mkdir(exist_ok=True);cache=folder/'cache-key.txt';movie=fx/f'HF-{first:04}-{last:04}.mp4'
            if not args.force and cache.exists() and cache.read_text()==key and movie.exists() and all((result/f'frame_{f+1:06}.png').exists() for f in range(first,last)):
                print(f'CACHED [{first},{last})',flush=True);continue
            run=1
            while (folder/f'pass-{run}').exists():run+=1
            project=folder/f'pass-{run}';framefolder=project/'assets/frames';framefolder.mkdir(parents=True)
            (project/'index.html').write_text(html,encoding='utf-8')
            for name in ['hyperframes.json','DESIGN.md','assets/gsap.min.js',*copies,*[p.relative_to(ROOT).as_posix() for p in (ROOT/'assets/fonts').glob('*')]]:
                dest=project/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dest)
            for id in sorted({a for a,n in needed}):extract(assets[id],{n for a,n in needed if a==id},framefolder)
            out=folder/f'png-{run}';log=folder/f'hyperframes-{run}.log'
            command=[NODE,CLI,'render',str(project),'--fps',str(fps),'--format','png-sequence','--workers','1','--low-memory-mode','--sdr','--experimental-fast-capture=false','--no-best-effort','--frames-cache-dir','off','--output',str(out)]
            print(f'RENDER [{first},{last}) source={len(needed)} alpha={len(copies)}',flush=True)
            with log.open('wb') as f:p=subprocess.run(command,env=ENV,stdout=f,stderr=subprocess.STDOUT)
            if p.returncode:raise RuntimeError(log.read_text(encoding='utf-8',errors='replace')[-3500:])
            names=sorted(out.glob('frame_*.png'));assert len(names)==last-first,(chunk,len(names))
            for i,path in enumerate(names):shutil.copy2(path,result/f'frame_{first+i+1:06}.png')
            encode(result,first+1,last-first,movie,fps);cache.write_text(key)
            print(f'DONE [{first},{last})',flush=True)
        save_editable(build(plan)[0])
    if args.chunks is None:
        assert all((result/f'frame_{f+1:06}.png').exists() for f in range(duration))
        final=ROOT.parent/'挚友_EDGE_精修V2.mp4';encode(result,1,duration,final,fps,ROOT/plan['audio']['master'])
        info=json.loads(capture([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(final)]));video=next(s for s in info['streams'] if s['codec_type']=='video')
        assert int(video['nb_read_frames'])==duration and video['avg_frame_rate']==f'{fps}/1'
        (ROOT.parent/'成片验证.json').write_text(json.dumps({'sha256':hashlib.sha256(final.read_bytes()).hexdigest(),'frames':duration,'fps':fps,'durationSeconds':duration/fps,'ffprobe':info},ensure_ascii=False,indent=2),encoding='utf-8')
        print('VERIFIED',final,flush=True)
if __name__=='__main__':main()
