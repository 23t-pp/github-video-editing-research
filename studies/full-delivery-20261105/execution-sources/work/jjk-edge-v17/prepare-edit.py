from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,shutil,hashlib,csv
ROOT=Path(__file__).resolve().parents[2]/'outputs/jjk-edge-v17';HF=ROOT/'hyperframes';W=Path(__file__).resolve().parent
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';FP='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'
scout=json.loads((W/'scout-source.json').read_text(encoding='utf-8'));C={s['id']:s for s in scout['shots']}
audio=json.loads((HF/'audio-report/selected-audio.json').read_text(encoding='utf-8'))
desired=[(0,'C38'),(2,'C20'),(3.25,'C03'),(4,'C12'),(5,'C13'),(5.8,'C05'),(7,'C02'),(7.8,'C16'),(9,'C17'),(9.83,'C18'),(11,'C54'),(12.17,'C23'),(13.17,'C24'),(13.96,'C25'),(14.79,'C14'),(16,'BLACK'),(17.708333,'C22'),(18.791667,'C21'),(20,'C32'),(21,'C33'),(21.5,'C36'),(22,'C37'),(22.791667,'C29'),(23.583333,'C30'),(24,'C31'),(24.833333,'C06'),(25.625,'C35'),(26.25,'C45'),(27,'C46'),(27.875,'X-awaken'),(29.875,'C39'),(30.5,'C43'),(31,'C40'),(32,'C09'),(32.625,'X-palm'),(33.75,'C55'),(35,'C28'),(36,'C29'),(37.25,'C30'),(37.75,'C35'),(38.375,'C36'),(39,'C39'),(39.625,'C43'),(40.25,'C33'),(41,'C32'),(41.75,'C37'),(42.375,'C49'),(43.25,'C48'),(44,'C47'),(45,'C50'),(45.75,'C51'),(46.75,'C52'),(47.5,'C53'),(48,'C42'),(49,'C46'),(49.5,'C45'),(50,'C51'),(50.75,'C52'),(51.5,'C40'),(52,'C09'),(52.5,'C55'),(53.25,'C49'),(54,'C48'),(54.75,'C46'),(55.5,'C23'),(56.5,'C07'),(58,'C01'),(60,None)]
fps=24;bound=[round(t*fps) for t,_ in desired]
locked={0,16*24,round(17.708333*24),round(27.875*24),round(29.875*24),round(32.625*24),round(33.75*24),round(55.5*24),1440}
# Snap only where the real onset is very close and the next source window remains safe.
onsets=sorted({e['frame24'] for e in audio['onsets'] if e['strength']>.075})
for i in range(1,len(bound)-1):
    if bound[i] in locked:continue
    near=min(onsets,key=lambda f:abs(f-bound[i]))
    if abs(near-bound[i])<=1 and bound[i-1]+4<near<bound[i+1]-4:bound[i]=near
for i,(t,id) in enumerate(desired[:-1]):
    cap=48 if id=='BLACK' else 48 if id=='X-awaken' else 27 if id=='X-palm' else int(C[id]['usableDuration']*fps+.001)
    if bound[i+1]-bound[i]>cap:bound[i+1]=bound[i]+cap
# Final manual durations were selected inside every source's reviewed safe interval.
assert bound[-1]==1440 and all(a<b for a,b in zip(bound,bound[1:]))
used={id for _,id in desired if id and id in C}|{'C05','C20','C23','C03','C01','C07'}
shotsdir=HF/'assets/shots';shotsdir.mkdir(parents=True,exist_ok=True)
def prepare(id):
    s=C[id];frames=int(s['usableDuration']*fps+.001);out=shotsdir/(id+'.mp4')
    if not out.exists():
        vf='scale=1920:1080:flags=lanczos,crop=1920:864:0:48,pad=1920:1080:0:108:black,fps=24,setpts=PTS-STARTPTS,setsar=1'
        cmd=[FF,'-v','error','-threads','2','-filter_threads','1','-ss',str(s['sourceIn']-.5),'-i',s['path'],'-an','-vf',vf,'-frames:v',str(frames+24),'-c:v','libx264','-threads','2','-preset','fast','-crf','17','-bf','0','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-f','mp4','-movflags','frag_keyframe+empty_moov+default_base_moof','pipe:1']
        with out.open('wb') as f:subprocess.run(cmd,stdout=f,check=True)
        print('PREPARED',id,frames+24,flush=True)
    return {'id':id,'asset':'assets/shots/'+id+'.mp4','frames':frames+24,'usableFrames':frames,'sourcePath':s['path'],'sourceIn':s['sourceIn'],'description':s.get('description',s.get('action')),'sourceFps':'24000/1001','sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
with ThreadPoolExecutor(max_workers=2) as pool:assets=list(pool.map(prepare,sorted(used)))
black=shotsdir/'BLACK.mp4'
if not black.exists():
    with black.open('wb') as f:subprocess.run([FF,'-v','error','-f','lavfi','-i','color=c=0x080b13:s=1920x1080:r=24','-frames:v','72','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','17','-bf','0','-f','mp4','-movflags','frag_keyframe+empty_moov+default_base_moof','pipe:1'],stdout=f,check=True)
assets.append({'id':'BLACK','asset':'assets/shots/BLACK.mp4','frames':72,'usableFrames':48,'description':'制作新增黑场，承接音乐能量低谷'})
for id,n,src in [('X-awaken',48,989),('X-palm',36,1259.5)]:assets.append({'id':id,'asset':f'assets/shots/{id}.mp4','frames':n+24,'usableFrames':n,'sourceIn':src,'description':'真实逐帧前景对应素材，由字效子代理准备'})
seen={};shots=[]
for i,((_,id),start,end) in enumerate(zip(desired[:-1],bound,bound[1:])):
    frames=end-start;offset=12
    if id=='X-palm':offset=21
    elif id in C:
        maximum=int(C[id]['usableDuration']*fps+.001)-frames;offset+=min(maximum,seen.get(id,0)*5);assert maximum>=0,(id,frames,maximum)
    shots.append({'id':f'S{i+1:02}','assetId':id,'asset':f'assets/shots/{id}.mp4','startFrame':start,'frames':frames,'assetStartFrame':offset,'punch':.045 if start<384 or start>1332 else .10 if start<669 else .17,'motion':1 if i%2==0 else -1,'rotation':0 if start<669 else (1.0 if i%3==0 else 0)})
    seen[id]=seen.get(id,0)+1
visuals=[
 {'id':'warm-window','kind':'memory','start':264,'end':292,'clips':[{'assetId':'C05','offset':12}],'z':25},
 {'id':'hurt-portrait','kind':'tear','start':292,'end':316,'clips':[{'assetId':'C20','offset':12}],'rotation':-5,'z':30},
 {'id':'void','kind':'black','start':384,'end':425,'z':35},
 {'id':'pulse','kind':'lightning','start':387,'end':433,'z':36},
 {'id':'geto-tear','kind':'tear','start':451,'end':478,'clips':[{'assetId':'C23','offset':12}],'x':-170,'z':30,'sourceX':-60},
 {'id':'two-faces','kind':'halves','start':624,'end':648,'clips':[{'assetId':'C20','offset':20},{'assetId':'C03','offset':12}],'scale':1.6,'z':28},
 {'id':'lens-finish','kind':'circle','start':1392,'end':1440,'clips':[{'assetId':'C01','offset':12}],'z':30}
]
types=[
 {'id':'bond','mode':'twin','text':['唯一','挚友'],'start':127,'end':160,'font_size':220,'color':'#fffaf0','stroke':'#080b13','depth':'#72c7ed','z':40,'font':'JJK Heavy'},
 {'id':'strongest','mode':'slam','text':'最强','start':432,'end':451,'font_size':355,'color':'#fffaf0','z':40,'font':'JJK Heavy'},
 {'id':'awake','mode':'twin','text':['最强','觉醒'],'start':669,'end':717,'font_size':280,'board':True,'color':'#34135f','stroke':'#f5f3f0','depth':'#b517c6','board_color':'#7bbbd4','edge_color':'#34135f','z':45,'font':'JJK Heavy'},
 {'id':'limitless','mode':'ribbon','text':'无下限','start':1017,'end':1047,'font_size':390,'board':False,'color':'#fffaf0','stroke':'#a42a68','stripe':'#72c7ed','z':40,'font':'JJK Heavy'},
 {'id':'purple','mode':'orbit','text':'茈','start':1098,'end':1116,'font_size':440,'color':'#b517c6','stroke':'#f5f3f0','depth':'#34135f','z':40,'font':'JJK Heavy'}
]
fg=[{'id':'awaken','alpha':'X-awaken','start':669,'end':717,'offset':12,'z':60,'x':-120,'y':140,'enterScale':1.25,'scale':1.0,'glow':3},
    {'id':'palm','alpha':'X-palm','start':774,'end':783,'offset':12,'z':60,'x':-150,'y':160,'enterScale':1.25,'scale':1,'glow':2}]
flashes=[{'frame':f,'width':2,'amount':.28} for f in [432,669,810,864,1056,1116,1200,1260]]
plan={'title':'挚友 · EDGE · V17主参考 / V02字效','width':1920,'height':1080,'fps':24,'durationFrames':1440,'audio':{'master':'assets/audio/master.wav','source':'edge.mp3','sourceStartSeconds':147,'sourceEndSeconds':207},'assets':assets,'shots':shots,'visuals':visuals,'foregrounds':fg,'typeEvents':types,'flashes':flashes,'hfChunks':[{'asset':f'../occ-effects/HF-{f:04}-{f+72:04}.mp4','startFrame':f,'frames':72,'assetStartFrame':0} for f in range(0,1440,72)],'nativeTexts':[{'id':e['id'],'text':' / '.join(e['text']) if isinstance(e['text'],list) else e['text'],'startFrame':e['start'],'frames':e['end']-e['start'],'fontSize':96,'color':'#fffaf0','fontWeight':900,'align':'center'} for e in types]}
(HF/'edit.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'evidence/片源选择与时间表.json').write_text(json.dumps({'scope':scout['scope'],'sourceClips':assets,'shotTimeline':shots},ensure_ascii=False,indent=2),encoding='utf-8')
with (HF/'镜头表.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['镜头ID','素材ID','成片起始帧','成片结束帧不含','成片秒','长度秒','素材入帧','描述'])
    for s in shots:w.writerow([s['id'],s['assetId'],s['startFrame'],s['startFrame']+s['frames'],s['startFrame']/24,s['frames']/24,s['assetStartFrame'],next(a['description'] for a in assets if a['id']==s['assetId'])])
font=HF/'assets/fonts';font.mkdir(parents=True,exist_ok=True)
shutil.copy2('C:/Windows/Fonts/msyhbd.ttc',font/'heavy.ttc')
shutil.copy2('C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/blocks/lower-third-bild/assets/fonts/BarlowCondensed-ExtraBold.woff2',font/'BarlowCondensed-ExtraBold.woff2')
shutil.copy2('C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/blocks/wireframe-portal-title/assets/gsap.min.js',HF/'assets/gsap.min.js') if Path('C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/blocks/wireframe-portal-title/assets/gsap.min.js').exists() else shutil.copy2(ROOT.parent/'reference-replay-next/hyperframes/assets/gsap.min.js',HF/'assets/gsap.min.js')
shutil.copy2(W/'typefx/typefx.py',HF/'typefx.py')
shutil.copy2(ROOT.parent/'reference-replay-next/hyperframes/hf.mjs',HF/'hf.mjs')
shutil.copy2(ROOT.parent/'reference-replay-next/hyperframes/hyperframes.json',HF/'hyperframes.json')
print('EDIT READY',len(shots),'shots',len(assets),'assets',flush=True)
