from pathlib import Path
import subprocess,time,json,math
ROOT=Path(__file__).resolve().parents[1];FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
src='D:/咒术回战/1080P 内嵌简中字幕/01.mp4';dest=ROOT/'evidence/frame-pilot';dest.mkdir(exist_ok=True)
t=time.monotonic();p=subprocess.run([FF,'-v','error','-threads','2','-ss','300','-i',src,'-t','10','-an','-vf','scale=640:360','-fps_mode','passthrough','-c:v','mjpeg','-q:v','6','-threads','2','-f','image2pipe','pipe:1'],capture_output=True,check=True)
frames=[b'\xff\xd8'+v for v in p.stdout.split(b'\xff\xd8')[1:]]
assert all(v.endswith(b'\xff\xd9') for v in frames)
for n in [0,len(frames)//2,len(frames)-1]:(dest/f'sample-{n:04}.jpg').write_bytes(frames[n])
r={'pilotSeconds':10,'nativeFrames':len(frames),'elapsedSeconds':time.monotonic()-t,'jpegResolution':[640,360],'jpegQualityFFmpeg':6,'meanJpegBytes':sum(map(len,frames))/len(frames),'allSeason60HzEntriesEstimate':2061018,'allSeasonNativeJpegEstimate':823577,'estimatedBytesIndependent60HzJpg':math.ceil(sum(map(len,frames))/len(frames)*2061018),'estimatedBytesHardlinkedDuplicates':math.ceil(sum(map(len,frames))/len(frames)*823577),'samplingPolicy':'60Hz取不晚于采样时刻的最近真实源PTS；重复帧为相同JPEG硬链接，非插值；逐样本映射记录。','note':'这是十秒试样估算，不能证明全季大小、季数或语义；保留80GiB空闲阈值。'}
(ROOT/'data/frame-pilot.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(r,ensure_ascii=False))
