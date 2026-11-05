"""Render HyperFrames effects and conform the editable cut to a 24 fps stereo MP4."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from composition import build, load_edit, save_editable


def executable(variable, examples, fallback=None):
    values = [os.environ.get(variable), *examples]
    if fallback:
        values.append(shutil.which(fallback))
    for value in values:
        if value and Path(value).is_file():
            return str(Path(value).resolve())
    raise SystemExit(f'Set {variable} to the installed executable.')


FF = executable('FFMPEG_PATH', ['C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'], 'ffmpeg')
PROBE = executable('FFPROBE_PATH', ['C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'], 'ffprobe')
NODE = executable('NODE_PATH_EXE', [Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'], 'node')
CLI = executable('HYPERFRAMES_CLI', ['C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/bin/hyperframes.mjs'])
BROWSER = executable('HYPERFRAMES_BROWSER_PATH', ['C:/Program Files/Google/Chrome/Application/chrome.exe'], 'google-chrome')
ENV = {**os.environ, 'HYPERFRAMES_BROWSER_PATH':BROWSER, 'HYPERFRAMES_FFMPEG_PATH':FF, 'HYPERFRAMES_FFPROBE_PATH':PROBE}


def capture(args):
    proc = subprocess.run(args, capture_output=True)
    if proc.returncode:
        raise RuntimeError(proc.stderr.decode(errors='replace')[-3000:])
    return proc.stdout


def probe(path):
    return json.loads(capture([PROBE,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)]))


def extract_images(asset, indices, folder):
    start, end = min(indices), max(indices)+1
    vf = f'trim=start_frame={start}:end_frame={end},scale=in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24'
    data = capture([FF,'-v','error','-threads','2','-filter_threads','1','-i',str(ROOT/asset['asset']),'-an','-vf',vf,'-fps_mode','passthrough','-c:v','png','-threads','1','-compression_level','1','-f','image2pipe','pipe:1'])
    offset = 0
    for frame in range(start,end):
        if data[offset:offset+8] != b'\x89PNG\r\n\x1a\n':
            raise ValueError(f'Missing PNG {asset["id"]} {frame}')
        end_png = offset+8
        while end_png+12 <= len(data):
            size = struct.unpack_from('>I',data,end_png)[0]
            kind = data[end_png+4:end_png+8]
            end_png += size+12
            if kind == b'IEND':
                break
        if end_png > len(data):
            raise ValueError('Incomplete PNG packet')
        if frame in indices:
            (folder/f'{asset["id"]}-{frame:03}.png').write_bytes(data[offset:end_png])
        offset = end_png
    if offset != len(data):
        raise ValueError('Unexpected image packet count')


def effect_render(name, spec, plan, work, effects, force=False):
    first, last = spec['startFrame'], spec['endFrame']
    project = work/name
    project.mkdir(parents=True,exist_ok=True)
    html, needed = build(plan, first, last, frame_mode=True)
    asset_ids = sorted({identity for identity,_ in needed})
    assets = {a['id']:a for a in plan['assets']}
    dependencies = [ROOT/assets[i]['asset'] for i in asset_ids] + [ROOT/'assets/gsap.min.js',Path(__file__),Path(CLI)]
    digest = hashlib.sha256(html.encode())
    for file in dependencies:
        digest.update(hashlib.sha256(file.read_bytes()).digest())
    key = digest.hexdigest()
    frames = project/'rendered'
    cache = project/'cache-key.txt'
    count = last-first
    insert = effects/f'FX-{name}.mp4'
    names = [f'frame_{i+1:06}.png' for i in range(count)]
    if not force and cache.exists() and cache.read_text()==key and insert.is_file() and all((frames/n).is_file() for n in names):
        print(f'HyperFrames {name}: verified cached range [{first},{last})',flush=True)
        return frames
    # A new run directory prevents stale frames from a previously longer effect range.
    render_number = 1
    while (project/f'pass-{render_number}').exists():
        render_number += 1
    isolated = project/f'pass-{render_number}'
    input_folder = isolated/'assets'/'frames'
    input_folder.mkdir(parents=True)
    (isolated/'index.html').write_text(html,encoding='utf-8')
    for config in ['hyperframes.json','DESIGN.md']:
        shutil.copy2(ROOT/config,isolated/config)
    shutil.copy2(ROOT/'assets/gsap.min.js',isolated/'assets/gsap.min.js')
    for identity in asset_ids:
        extract_images(assets[identity],{i for j,i in needed if j==identity},input_folder)
    fresh = project/f'png-{render_number}'
    cmd = [NODE,CLI,'render',str(isolated),'--fps',str(plan['fps']),'--format','png-sequence','--workers','1','--low-memory-mode','--sdr','--experimental-fast-capture=false','--no-best-effort','--output',str(fresh)]
    log = project/f'hyperframes-{render_number}.log'
    print(f'HyperFrames {name}: rendering {count} frames, timeline [{first},{last})',flush=True)
    with log.open('wb') as out:
        result = subprocess.run(cmd,env=ENV,stdout=out,stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(log.read_text(encoding='utf-8',errors='replace')[-3500:])
    if sorted(x.name for x in fresh.glob('frame_*.png')) != names:
        raise ValueError(f'Incorrect HyperFrames PNG sequence in {fresh}')
    frames.mkdir(exist_ok=True)
    for n in names:
        os.replace(fresh/n,frames/n)
    # Produce silent MP4 effect inserts for the matching OpenChatCut timeline.
    encode = [FF,'-v','error','-threads','2','-filter_threads','1','-framerate',str(plan['fps']),'-i',str(frames/'frame_%06d.png'),'-frames:v',str(count),'-vf',RGB_TO_YUV,'-an',*video_options(),'-f','mp4','-fd','1','fd:']
    with insert.open('wb') as out:
        subprocess.run(encode,stdout=out,check=True)
    cache.write_text(key)
    print(f'HyperFrames {name}: {count} PNGs and {insert.name} verified',flush=True)
    return frames


RGB_TO_YUV = 'scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p'


def video_options():
    return ['-c:v','libx264','-threads','4','-preset','fast','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv']


def conform(plan, ranges, renders, output, work):
    # Pass unchanged picture as YUV and composite only frames with a HyperFrames effect.
    split = {0,plan['durationFrames']}
    for shot in plan['shots']:
        split.update([shot['startFrame'],shot['startFrame']+shot['frames']])
    for s in ranges.values():
        split.update([s['startFrame'],s['endFrame']])
    bounds = sorted(split)
    segments = []
    for a,b in zip(bounds,bounds[1:]):
        fx = next((k for k,s in ranges.items() if s['startFrame']<=a<s['endFrame']),None)
        if fx:
            source = str(renders[fx]/'frame_%06d.png')
            offset = a-ranges[fx]['startFrame']
            dec = ['-framerate',str(plan['fps']),'-start_number',str(offset+1),'-i',source,'-vf',RGB_TO_YUV]
            label = f'FX-{fx}'
        else:
            shot = next(s for s in plan['shots'] if s['startFrame']<=a<s['startFrame']+s['frames'])
            offset = shot['assetStartFrame']+a-shot['startFrame']
            source = str(ROOT/shot['asset'])
            dec = ['-i',source,'-vf',f'trim=start_frame={offset}:end_frame={offset+b-a}']
            label = shot['id']
        segments.append((a,b,label,dec))
    fps=plan['fps']
    width,height=plan['width'],plan['height']
    expected_samples=plan['durationFrames']*48000//fps
    audio_stats=probe(ROOT/plan['audio']['master'])['streams'][0]
    if int(audio_stats['duration_ts'])!=expected_samples or int(audio_stats['sample_rate'])!=48000 or audio_stats['channels']!=2:
        raise ValueError('Master audio length or layout differs from the timeline')
    output.parent.mkdir(parents=True,exist_ok=True)
    partial = output.with_name(output.stem+'.in-progress.mp4')
    cmd = [FF,'-v','error','-filter_threads','1','-f','rawvideo','-pixel_format','yuv420p','-video_size',f'{width}x{height}','-framerate',str(fps),'-i','pipe:0','-i',str(ROOT/plan['audio']['master']),'-map','0:v:0','-map','1:a:0',*video_options(),'-c:a','aac','-b:a','256k','-ar','48000','-t',f'{plan["durationFrames"]/fps:.9f}','-metadata','title='+plan['title'],'-f','mp4','-fd','1','fd:']
    with partial.open('wb') as target, (work/'encode.log').open('wb') as log:
        encoder = subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=target,stderr=log)
        try:
            for a,b,label,source in segments:
                args = [FF,'-v','error','-threads','2','-filter_threads','1',*source,'-map','0:v:0','-an','-frames:v',str(b-a),'-c:v','rawvideo','-threads','1','-pix_fmt','yuv420p','-f','rawvideo','pipe:1']
                moved = 0
                with subprocess.Popen(args,stdout=subprocess.PIPE,stderr=log) as decoder:
                    while data := decoder.stdout.read(1024*1024):
                        encoder.stdin.write(data)
                        moved += len(data)
                    if decoder.wait() or moved != (b-a)*width*height*3//2:
                        raise ValueError(f'Incorrect decoded byte count for {label}, frames {a}..{b}')
            encoder.stdin.close()
            if encoder.wait():
                raise RuntimeError(f'Encoder failed, see {work/"encode.log"}')
        finally:
            if encoder.poll() is None:
                encoder.kill()
                encoder.wait()
    info = probe(partial)
    v = next(s for s in info['streams'] if s['codec_type']=='video')
    audio = next(s for s in info['streams'] if s['codec_type']=='audio')
    if (int(v['nb_read_frames']),int(v['width']),int(v['height']),int(audio['sample_rate']),audio['channels']) != (plan['durationFrames'],width,height,48000,2):
        raise ValueError('Final MP4 streams failed validation')
    for stream in [v,audio,info['format']]:
        if abs(float(stream['duration'])-plan['durationFrames']/fps)>.00001:
            raise ValueError(f'Unexpected duration {stream["duration"]}')
    os.replace(partial,output)
    info['format']['filename']=output.name
    report={'file':output.name,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'pictureEditCount':len(plan['shots']),'renderedEffects':{n:[v['startFrame'],v['endFrame']] for n,v in ranges.items()},'frames':int(v['nb_read_frames']),'ffprobe':info}
    (output.parent/'成片验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'OK {output} | {v["nb_read_frames"]} frames | {info["format"]["duration"]} s',flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--work',type=Path,default=ROOT/'.render-cache')
    parser.add_argument('--output',type=Path,default=ROOT.parent/'弯心_APEX_60秒.mp4')
    parser.add_argument('--effects-dir',type=Path,default=ROOT.parent/'occ-effects')
    parser.add_argument('--occ-cut',type=Path,help='Read frame placements from a verified OpenChatCut timeline export.')
    parser.add_argument('--only',choices=['title','triptych','end'],nargs='+',help='Render selected effects without encoding the master.')
    parser.add_argument('--force',action='store_true',help='Re-render even when the exact input cache matches.')
    args=parser.parse_args()
    work=args.work.resolve();work.mkdir(parents=True,exist_ok=True)
    effects=args.effects_dir.resolve();effects.mkdir(parents=True,exist_ok=True)
    plan=load_edit()
    if args.occ_cut:
        recorded=json.loads(args.occ_cut.read_text(encoding='utf-8-sig'))['shots']
        if len(recorded)!=len(plan['shots']):
            raise ValueError('OpenChatCut and HyperFrames shot counts differ')
        for shot,clip in zip(plan['shots'],recorded):
            keys=('id','startFrame','frames','assetStartFrame')
            if any(shot[k]!=clip[k] for k in keys):
                raise ValueError(f'OpenChatCut and HyperFrames disagree on {shot["id"]}')
            shot.update({k:clip[k] for k in keys})
            next(a for a in plan['assets'] if a['id']==shot['id'])['assetStartFrame']=clip['assetStartFrame']
        print(f'Using {len(recorded)} verified OpenChatCut placements',flush=True)
    if sum(s['frames'] for s in plan['shots'])!=plan['durationFrames'] or any(s['startFrame']!=sum(x['frames'] for x in plan['shots'][:i]) for i,s in enumerate(plan['shots'])):
        raise ValueError('Picture timeline contains a gap or overlap')
    html,_=build(plan)
    save_editable(html)
    timelines={'title':plan['effects']['title'],'triptych':plan['effects']['triptych'],'end':plan['effects']['endFade']}
    renders={k:effect_render(k,v,plan,work,effects,args.force) for k,v in timelines.items() if not args.only or k in args.only}
    if not args.only:
        conform(plan,timelines,renders,args.output.resolve(),work)


if __name__=='__main__':
    main()
