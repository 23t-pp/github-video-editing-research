from pathlib import Path
import subprocess,json,hashlib
ROOT=Path(__file__).resolve().parents[2];HF=ROOT/'outputs/reference-replay-next/hyperframes'
source=HF/'assets/shots/P15.mp4';target=HF/'assets/shots/P15-clean-pedal.mp4'
ff='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
cmd=[ff,'-v','error','-threads','2','-filter_threads','1','-i',str(source),'-an','-vf','trim=start_frame=10:end_frame=18,setpts=PTS-STARTPTS,tpad=start_mode=clone:start_duration=0.48:stop_mode=clone:stop_duration=0.52','-frames:v','33','-c:v','libx264','-threads','2','-preset','fast','-crf','17','-bf','0','-g','25','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-f','mp4','-fd','1','fd:']
with target.open('wb') as out:subprocess.run(cmd,stdout=out,check=True)
report={'asset':target.name,'source':source.name,'usedOldAssetFrames':[10,11,12,13,14,15,16,17,17],'usedNewAssetFrames':list(range(12,21)),'note':'Eight clean pedal frames plus one repeated last frame. Repeated handles have no extra motion or trim range. No subtitles, exterior shot, or interpolated pixels.','command':cmd,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
(HF/'assets/shots/pedal-cleanup.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
plan=json.loads((HF/'edit.json').read_text(encoding='utf-8'))
for a in plan['assets']:
    if a['id']=='P15':a.update(asset='assets/shots/P15-clean-pedal.mp4',sourceIn=1710.005,retime='8 source frames → 9 timeline frames; last frame held once; handles are repeated')
for s in plan['shots']:
    if s['assetId']=='P15':s.update(asset='assets/shots/P15-clean-pedal.mp4',sourceIn=1710.005)
    if s['assetId']=='P16':s.update(assetStartFrame=6,sourceIn=2249.54)
(HF/'edit.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print('P15 clean replacement, P16 F6..29. 750-frame placements unchanged.')
