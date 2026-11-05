from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,hashlib,io,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];SOURCE=Path('D:/咒术回战/1080P 内嵌简中字幕')
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';FP='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'
EV=ROOT/'evidence/source-overviews';DATA=ROOT/'data';EV.mkdir(parents=True,exist_ok=True);DATA.mkdir(parents=True,exist_ok=True)
def probe(p):
    j=json.loads(subprocess.run([FP,'-v','error','-show_streams','-show_format','-of','json',str(p)],capture_output=True,check=True).stdout)
    v=next(s for s in j['streams'] if s['codec_type']=='video');a=next((s for s in j['streams'] if s['codec_type']=='audio'),{})
    return {'id':'S1E'+p.stem,'episodeNumber':int(p.stem),'localPath':p.as_posix(),'filename':p.name,'bytes':p.stat().st_size,'width':v['width'],'height':v['height'],'videoCodec':v['codec_name'],'videoDurationSeconds':float(v['duration']),'containerDurationSeconds':float(j['format']['duration']),'avgFrameRate':v['avg_frame_rate'],'rFrameRate':v['r_frame_rate'],'sourceFrames':int(v.get('nb_frames',0)),'timeBase':v['time_base'],'colorPrimaries':v.get('color_primaries'),'colorTransfer':v.get('color_transfer'),'colorSpace':v.get('color_space'),'audioCodec':a.get('codec_name'),'audioSampleRate':a.get('sample_rate'),'audioChannels':a.get('channels'),'identityEvidence':'目录结构待画面核实，非仅靠目录名宣称季数','rawProbe':j}
files=[SOURCE/f'{n:02}.mp4' for n in range(1,25)]
with ThreadPoolExecutor(max_workers=4) as pool:items=list(pool.map(probe,files))
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while b:=f.read(4*1024*1024):h.update(b)
    return h.hexdigest()
dups=[]
for n in [2,5]:
    a=SOURCE/f'{n:02}.mp4';b=SOURCE/f'{n:02}(1).mp4';ha=digest(a);hb=digest(b)
    dups.append({'canonical':a.as_posix(),'duplicate':b.as_posix(),'sha256Canonical':ha,'sha256Duplicate':hb,'byteIdentical':ha==hb,'action':'保留原文件，仅索引正本一次'})
summary={'scope':'24个编号文件，不含重复副本；本清单尚未做整季逐帧解码','episodes':len(items),'totalVideoSeconds':sum(i['videoDurationSeconds'] for i in items),'totalBytes':sum(i['bytes'] for i in items),'sourceFrameRateSet':sorted({i['avgFrameRate'] for i in items}),'totalDeclaredNativeFrames':sum(i['sourceFrames'] for i in items),'requested60fpsGridFramesApprox':sum(math.ceil(i['videoDurationSeconds']*60) for i in items),'duplicateChecks':dups,'items':items}
(DATA/'source-inventory.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:summary[k] for k in ['episodes','totalVideoSeconds','totalBytes','sourceFrameRateSet','totalDeclaredNativeFrames','requested60fpsGridFramesApprox','duplicateChecks']},ensure_ascii=False),flush=True)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15)
TIMES=[120,280,440,600,760,920,1080,1240]
def overview(item):
    p=Path(item['localPath']);folder=EV/item['id'];folder.mkdir(exist_ok=True)
    picks=[];canvas=Image.new('RGB',(1280,490),'#10131a');d=ImageDraw.Draw(canvas)
    d.text((12,5),f'{item["id"]} | 稀疏内容导航（8张；不是60fps拆解）',font=font,fill='#7fd5f0')
    for k,t in enumerate(TIMES):
        dest=folder/f't{t:04}.jpg'
        if not dest.exists():
            r=subprocess.run([FF,'-v','error','-threads','1','-ss',str(t),'-i',str(p),'-frames:v','1','-an','-vf','scale=640:360','-q:v','3','-f','image2pipe','pipe:1'],capture_output=True,check=True);dest.write_bytes(r.stdout)
        im=Image.open(dest).convert('RGB');x=(k%4)*320;y=40+(k//4)*225
        canvas.paste(im.resize((320,180)),(x,y));d.text((x+6,y+184),f'{t//60:02}:{t%60:02} · target {t}s',font=small,fill='white')
        picks.append({'targetSeconds':t,'jpg':dest.relative_to(ROOT).as_posix(),'method':'ffmpeg input seeking single frame; not native PTS index and not exact60fps grid'})
    sheet=EV/f'{item["id"]}-overview.jpg';canvas.save(sheet,quality=91)
    print('OVERVIEW',item['id'],flush=True)
    return {'id':item['id'],'overviewJpg':sheet.relative_to(ROOT).as_posix(),'samples':picks,'semanticLabels':[],'humanViewed':False}
with ThreadPoolExecutor(max_workers=3) as pool:overview_records=list(pool.map(overview,items))
(DATA/'source-overview-index.json').write_text(json.dumps({'scope':'24集各8张稀疏导航；192个单帧JPG与24张联系表','notFullFrameAnalysis':True,'items':overview_records},ensure_ascii=False,indent=2),encoding='utf-8')
print('DONE 24 OVERVIEWS',flush=True)
