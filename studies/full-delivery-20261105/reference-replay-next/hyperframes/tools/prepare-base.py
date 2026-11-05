"""Prepare small editable source clips; Python owns output handles on Windows."""
from pathlib import Path
import json, subprocess, hashlib, sys
ROOT=Path(__file__).resolve().parents[1]
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
FP='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'
plan=json.loads((ROOT/'edit.json').read_text(encoding='utf-8'))
files={p.name[:2]:p for p in Path('D:/速度与激情').iterdir() if p.name[:2].isdigit()}
report=[]
for a in plan['assets']:
    if not (a['id'].startswith('P') or a['id']=='BLACK'):continue
    target=ROOT/a['asset']
    if target.exists():
        print('EXISTS',a['id'],flush=True);continue
    if a['film']:
        src=files[a['film']]
        v=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_streams','-of','json',str(src)]))['streams'][0]
        color='zscale=w=1920:h=-2:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p' if v.get('color_transfer')=='smpte2084' else 'scale=1920:-2:flags=lanczos:out_range=tv,format=yuv420p'
        inp=['-ss',str(a['sourceIn']-12/25),'-i',str(src)]
        vf=f'fps=25,setpts=PTS-STARTPTS,{color},crop=1920:800,pad=1920:1080:0:140:black,setsar=1'
    else:
        inp=['-f','lavfi','-i','color=black:s=1920x1080:r=25'];vf='format=yuv420p'
    args=[FF,'-v','error','-threads','2','-filter_threads','1',*inp,'-map','0:v:0','-an','-vf',vf,'-frames:v',str(a['frames']+24),'-c:v','libx264','-threads','2','-preset','fast','-crf','17','-bf','0','-g','25','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-f','mp4','-fd','1','fd:']
    with target.open('wb') as out:subprocess.run(args,stdout=out,check=True)
    info=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=nb_read_frames,avg_frame_rate,width,height','-of','json',str(target)]))['streams'][0]
    assert int(info['nb_read_frames'])==a['frames']+24
    report.append(dict(id=a['id'],command=args,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),probe=info))
    print('PREPARED',a['id'],a['frames'],flush=True)
(ROOT/'assets/shots/base-source-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
