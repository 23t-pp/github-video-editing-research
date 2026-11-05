"""Prepare editable shot handles and source-sound cues. Run from any directory."""
import argparse
import json
import os
import subprocess
import wave
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

PROJECT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--plan', type=Path, default=PROJECT/'edit.json')
parser.add_argument('--sources', type=Path, required=True)
parser.add_argument('--jobs', type=int, default=2)
parser.add_argument('--only', nargs='+', help='Only replace the named shot assets, e.g. S04')
args = parser.parse_args()
plan = json.loads(args.plan.read_text(encoding='utf-8-sig'))
fps = plan['fps']
files = {p.name[:2]:p for p in args.sources.iterdir() if p.suffix.lower() in {'.mp4','.mkv','.mov'}}
ffmpeg = os.environ.get('FFMPEG_PATH','C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe')
ffprobe = os.environ.get('FFPROBE_PATH','C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe')

def run(command):
    p = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode: raise RuntimeError(p.stderr.decode(errors='replace')[-3000:])
    return p.stdout

def prepare(take):
    src = files[take['film']]
    count = take['frames'] + take['assetStartFrame'] + take['tailFrames']
    start = take['sourceIn'] - take['assetStartFrame']/fps
    out = PROJECT/take['asset']
    out.parent.mkdir(parents=True, exist_ok=True)
    streams=json.loads(run([ffprobe,'-v','error','-show_streams','-of','json',str(src)]))['streams']
    video=next(s for s in streams if s['codec_type']=='video')
    aud=next(s for s in streams if s['codec_type']=='audio')
    timing=f'fps={fps},setpts=PTS-STARTPTS'
    if video.get('color_transfer')=='smpte2084':
        color='zscale=w=1920:h=-2:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p'
    else:
        color='scale=1920:-2:flags=lanczos:out_range=tv,format=yuv420p'
    vf=','.join([timing,color,'crop=1920:800','pad=1920:1080:0:140:black','setsar=1'])
    common=[ffmpeg,'-v','error','-nostdin','-threads','2','-filter_threads','1']
    # MP4s are silent so the single source-sound track cannot play twice.
    encoded=run(common+['-ss',f'{start:.6f}','-i',str(src),'-map','0:v:0','-an','-vf',vf,'-frames:v',str(count),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','17','-g','24','-bf','0','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','frag_keyframe+delay_moov+default_base_moof','-f','mp4','pipe:1'])
    out.write_bytes(encoded)
    stats=json.loads(run([ffprobe,'-v','error','-select_streams','v:0','-count_packets','-show_entries','stream=nb_read_packets,start_time,width,height','-of','json',str(out)]))['streams'][0]
    if int(stats['nb_read_packets'])!=count or abs(float(stats['start_time']))>0.00001:raise ValueError((take['id'],count,stats))
    if take.get('cue'):
        # Front left/right and surround effects carry less centre-channel dialogue.
        af=[]
        if aud.get('channels')==6:
            left,right=('SL','SR') if 'side' in aud.get('channel_layout','') else ('BL','BR')
            af.append(f'pan=stereo|c0=0.72*FL+0.22*{left}+0.06*LFE|c1=0.72*FR+0.22*{right}+0.06*LFE')
        af.extend(['aresample=48000','asetpts=PTS-STARTPTS'])
        size=take['frames']*(48000//fps)*4
        raw=run(common+['-ss',f"{take['sourceIn']:.6f}",'-i',str(src),'-map','0:a:0','-vn','-t',f"{take['frames']/fps:.9f}",'-af',','.join(af),'-ar','48000','-ac','2','-c:a','pcm_s16le','-f','s16le','pipe:1'])
        if len(raw)<size-4*96: raise ValueError(f"{take['id']} source audio unexpectedly short")
        cue=PROJECT/take['cue'];cue.parent.mkdir(parents=True,exist_ok=True)
        with wave.open(str(cue),'wb') as w:
            w.setparams((2,2,48000,0,'NONE','not compressed'));w.writeframes((raw+bytes(max(0,size-len(raw))))[:size])
    print(f"{take['id']}: {count} frames prepared from {take['film']} at {take['sourceIn']:.3f}s",flush=True)

takes = [take for take in plan['assets'] if not args.only or take['id'] in args.only]
if args.only and len(takes) != len(set(args.only)):
    parser.error('Unknown shot ID in --only')
with ThreadPoolExecutor(max_workers=max(1,min(3,args.jobs))) as pool:
    list(pool.map(prepare,takes))
