from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,subprocess,io,sys,collections
BASE=Path(__file__).resolve().parents[2];ROOT=BASE/'outputs/jjk-edge-v17-v3-dedup';HF=ROOT/'hyperframes';W=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'work/reference-replay-v07/python-deps'))
import numpy as np
from PIL import Image,ImageDraw,ImageFont
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';FP='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'
MOV=ROOT/'挚友_EDGE_画面去重V3.mp4';OLD=BASE/'outputs/jjk-edge-v17-v2/挚友_EDGE_精修V2.mp4'
def run(a):return subprocess.run(a,capture_output=True,check=True)
def pcm(p):return np.frombuffer(run([FF,'-v','error','-threads','1','-i',str(p),'-vn','-ac','2','-ar','48000','-f','f32le','pipe:1']).stdout,dtype='<f4').reshape(-1,2)
def frames():return np.frombuffer(run([FF,'-v','error','-threads','1','-filter_threads','1','-i',str(MOV),'-an','-vf','scale=192:108','-pix_fmt','rgb24','-f','rawvideo','pipe:1']).stdout,dtype=np.uint8).reshape(-1,108,192,3)
with ThreadPoolExecutor(max_workers=2) as ex:
 ar=ex.submit(pcm,MOV);fr=ex.submit(frames);audio=ar.result();images=fr.result()
master=pcm(HF/'assets/audio/master.wav');assert len(audio)==len(master)==2880000
assert len(images)==1440;corr=float(np.corrcoef(audio.reshape(-1),master.reshape(-1))[0,1]);assert corr>.995
plan=json.loads((HF/'edit.json').read_text(encoding='utf8'))
audit=json.loads((ROOT/'evidence/源片区间与画面相似筛查.json').read_text(encoding='utf8'))
assert audit['editManifestSha256']==hashlib.sha256((HF/'edit.json').read_bytes()).hexdigest()
assert not audit['nativeSourceIntervalOverlaps']
assert len(plan['shots'])==67 and len({s['assetId'] for s in plan['shots']})==67
assert all(a['startFrame']+a['frames']==b['startFrame'] for a,b in zip(plan['shots'],plan['shots'][1:]))
assert plan['shots'][-1]['startFrame']+plan['shots'][-1]['frames']==1440
dark=np.where(images[:,11:98].mean((1,2,3))<10)[0].tolist();unexpected=[f for f in dark if not(384<=f<433 or f>=1416)];assert not unexpected,unexpected
guard=json.loads((ROOT/'evidence/V1-V2保留指纹.json').read_text(encoding='utf8'))
for rel,digest in guard.items():assert hashlib.sha256((BASE/rel).read_bytes()).hexdigest()==digest,rel+' changed'
info=json.loads(run([FP,'-v','error','-show_streams','-show_format','-of','json',str(MOV)]).stdout)
report={'file':MOV.name,'sha256':hashlib.sha256(MOV.read_bytes()).hexdigest(),'bytes':MOV.stat().st_size,'framesDecoded':len(images),'durationSeconds':float(info['format']['duration']),'fps':24,'size':[1920,1080],'nativeShots':67,'uniqueNativeAssetIds':67,'sourceIntervalOverlaps':[],'foregroundEvents':len(plan['foregrounds']),'uniqueForegroundGroups':len({e['alpha'] for e in plan['foregrounds']}),'layouts':len(plan['layouts']),'textEvents':len(plan['typeEvents']),'masterSampleFrames':len(master),'aacDecodedSampleFrames':len(audio),'audioCorrelationAtZeroOffset':corr,'audioMasterMatchesV2':hashlib.sha256((HF/'assets/audio/master.wav').read_bytes()).digest()==hashlib.sha256((OLD.parent/'hyperframes/assets/audio/master.wav').read_bytes()).digest(),'musicSourceSeconds':[147,207],'unexpectedNearBlackFrames':unexpected,'v1V2Guard':'passed','auditoryListeningPerformed':False,'scope':'完整1440帧192x108缩略解码；全音轨数值对齐；新旧源区间和三帧相似度筛查。不是全分辨率逐帧或实际听觉验收。'}
(ROOT/'质量检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
def picture(p,f,w=480,h=270):
 blob=run([FF,'-v','error','-threads','1','-filter_threads','1','-ss',str(f/24),'-i',str(p),'-frames:v','1','-vf',f'scale={w}:{h}','-f','image2pipe','pipe:1']).stdout
 return Image.open(io.BytesIO(blob)).convert('RGB')
# Every replacement gets an actual output screenshot, not just a plan check.
changes=json.loads((ROOT/'evidence/主镜头替换清单.json').read_text(encoding='utf8'))
for pg,k in enumerate(range(0,len(changes),7),1):
 batch=changes[k:k+7];can=Image.new('RGB',(960,len(batch)*306),'#080b13');d=ImageDraw.Draw(can)
 for i,s in enumerate(batch):
  f=s['startFrame']+max(1,s['frames']//2);y=i*306
  can.paste(picture(OLD,f),(0,y+30));can.paste(picture(MOV,f),(480,y+30));d.text((8,y+4),f"{s['shot']}  {f/24:.3f}秒  V2 → V3  {s['after']['assetId']}",font=font,fill='white')
 can.save(ROOT/'evidence'/f'21处替换实际成片对照-{pg:02}.jpg',quality=93)
# Even full-film overview; all 60 seconds are covered.
can=Image.new('RGB',(1280,8*204),'#080b13');d=ImageDraw.Draw(can)
for i,f in enumerate(np.linspace(6,1430,32).astype(int)):
 x=(i%4)*320;y=(i//4)*204;can.paste(picture(MOV,int(f),320,180),(x,y));d.text((x+5,y+181),f'F{f} / {f/24:.3f}s',font=font,fill='white')
can.save(ROOT/'evidence/全片32帧总览.jpg',quality=92)
picture(MOV,690,1280,720).save(ROOT/'封面.jpg',quality=93)
print(json.dumps(report,ensure_ascii=False))
