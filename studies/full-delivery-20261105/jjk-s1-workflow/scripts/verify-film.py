from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,subprocess,json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1];FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';FP='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'
p=argparse.ArgumentParser();p.add_argument('--movie',type=Path,required=True);p.add_argument('--report',type=Path,required=True);args=p.parse_args();movie=args.movie.resolve();report=args.report.resolve();report.parent.mkdir(exist_ok=True,parents=True)
def run(c):return subprocess.run(c,capture_output=True,check=True)
def audio(file):return np.frombuffer(run([FF,'-v','error','-threads','1','-i',str(file),'-vn','-ac','2','-ar','48000','-f','f32le','pipe:1']).stdout,dtype='<f4').reshape(-1,2)
def video():return np.frombuffer(run([FF,'-v','error','-threads','1','-i',str(movie),'-an','-vf','scale=192:108','-pix_fmt','rgb24','-f','rawvideo','pipe:1']).stdout,dtype=np.uint8).reshape(-1,108,192,3)
with ThreadPoolExecutor(max_workers=3) as ex:
    fs=[ex.submit(audio,movie),ex.submit(audio,ROOT/'music/master.wav'),ex.submit(video)];a,b,frames=[f.result() for f in fs]
info=json.loads(run([FP,'-v','error','-show_streams','-show_format','-of','json',str(movie)]).stdout);vs=next(s for s in info['streams'] if s['codec_type']=='video')
assert len(frames)==1440 and vs['avg_frame_rate']=='24/1';assert abs(float(info['format']['duration'])-60)<.001
assert len(a)==len(b)==2880000;corr=float(np.corrcoef(a.reshape(-1),b.reshape(-1))[0,1]);assert corr>.995
dark=np.where(frames[:,6:102].mean((1,2,3))<3)[0].tolist();unexpected=[i for i in dark if not (168<=i<176 or i>=1416)]
loud=run([FF,'-hide_banner','-threads','1','-i',str(movie),'-af','ebur128=peak=true','-f','null','-']).stderr.decode(errors='replace');report.with_suffix('.loudness.log').write_text(loud,encoding='utf-8')
r={'file':str(movie.relative_to(ROOT)),'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'bytes':movie.stat().st_size,'fullDecodedFrames':len(frames),'fps':24,'durationSeconds':float(info['format']['duration']),'width':vs['width'],'height':vs['height'],'decodedAudioSampleFrames':len(a),'masterSampleFrames':len(b),'sameTimeCorrelation':corr,'nearBlackFrames':dark,'unexpectedNearBlackCandidates':unexpected,'nearBlackDefinition':'192x108缩略完整解码，active y6:102 RGB mean<3；候选需结合实际图查看','auditoryListeningPerformed':False,'machineState':'pass' if not unexpected else 'needs_visual_review_of_dark_candidates','scope':'完整缩略解码与采样数、零偏移声音对照；不是全1440张全分辨率逐张人工审美验收'}
report.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(r,ensure_ascii=False))
