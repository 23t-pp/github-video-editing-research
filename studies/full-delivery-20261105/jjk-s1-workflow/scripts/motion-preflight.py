from pathlib import Path
import subprocess,json,io
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];D=R/'evidence/source-overviews/motion-preflight';D.mkdir(parents=True,exist_ok=True)
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
c=json.loads((R/'data/shot-candidates.json').read_text(encoding='utf-8'))['items'];lookup={(x['episode'],x['anchorSeconds']):x for x in c}
keys=[(4,1030),(4,1050),(4,1065),(5,325),(5,335),(5,340),(5,345),(5,350),(5,365),(5,370),(5,390),(5,405),(5,435),(5,555),(5,590),(5,595),(5,610),(5,630),(7,245),(7,270),(7,280),(7,320),(7,330),(7,340),(17,115),(17,130),(17,135),(17,140),(17,205),(17,440),(17,495),(17,505),(19,880),(19,890),(19,915),(19,920),(20,205),(20,210),(20,220),(20,270),(20,300),(20,315),(20,1100),(20,1125),(20,1175),(20,1180),(20,1195),(20,1210),(23,260),(23,295),(24,400),(24,405),(24,410),(24,415),(24,690),(24,695),(24,705),(24,765)]
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16);records=[]
for batch in range((len(keys)+7)//8):
    canvas=Image.new('RGB',(1280,8*218+40),'#10131a');draw=ImageDraw.Draw(canvas);draw.text((10,4),f'候选运动预检{batch+1}｜每行同一1.5s区间，显示0/0.4/0.8/1.2s',font=font,fill='#72c7ed')
    for row,key in enumerate(keys[batch*8:(batch+1)*8]):
        item=lookup[key];folder=D/item['id'];folder.mkdir(exist_ok=True);start=item['anchorSeconds']-.4;movie=folder/'review.mp4'
        if not movie.exists():
            cmd=[FF,'-v','error','-threads','1','-ss',str(start),'-i',item['sourcePath'],'-t','1.5','-an','-vf','scale=640:360','-c:v','libx264','-threads','1','-preset','ultrafast','-crf','20','-pix_fmt','yuv420p','-movflags','frag_keyframe+empty_moov+default_base_moof','-f','mp4','pipe:1'];movie.write_bytes(subprocess.run(cmd,capture_output=True,check=True).stdout)
        y=40+row*218;draw.text((8,y),f'{item["id"]} E{item["episode"]:02} {start:.1f}s | {"/".join(item["characters"])} · {item["visibleActionOrPose"]}',font=small,fill='white')
        for k,t in enumerate([0,.4,.8,1.2]):
            path=folder/f'frame{k}.jpg'
            if not path.exists():path.write_bytes(subprocess.run([FF,'-v','error','-threads','1','-ss',str(t),'-i',str(movie),'-an','-frames:v','1','-q:v','3','-f','image2pipe','pipe:1'],capture_output=True,check=True).stdout)
            im=Image.open(path).convert('RGB').resize((320,180));canvas.paste(im,(k*320,y+25))
        records.append({'candidateId':item['id'],'episode':item['episode'],'sourceStartSeconds':start,'durationSeconds':1.5,'reviewMovie':movie.relative_to(R).as_posix(),'contactSheet':f'evidence/source-overviews/motion-preflight/motion-{batch+1:02}.jpg','row':row,'humanReviewed':False})
    canvas.save(D/f'motion-{batch+1:02}.jpg',quality=92);print('BATCH',batch+1,flush=True)
(R/'data/motion-preflight-index.json').write_text(json.dumps({'scope':'58个候选短片与每段4帧运动预检图；不是最终剪辑素材','items':records},ensure_ascii=False,indent=2),encoding='utf-8')
