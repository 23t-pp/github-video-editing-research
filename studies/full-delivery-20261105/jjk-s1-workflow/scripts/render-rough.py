from pathlib import Path
import subprocess,json,hashlib,datetime
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent.parent;H=R/'hyperframes';L=R/'loops/loop-01';L.mkdir(parents=True,exist_ok=True)
P=json.loads((H/'edit.json').read_text(encoding='utf-8'));F='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';FP='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'
revision=P.get('revision','initial');out=L/('loop-01-rough-focus-v2.mp4' if revision=='L1-FOCUS-v2' else 'loop-01-rough.mp4');log=L/('encode-'+revision+'.log');W,HGT=960,540
cmd=[F,'-v','error','-threads','1','-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24','-video_size',f'{W}x{HGT}','-framerate','24','-i','pipe:0','-i',str(R/'music/master.wav'),'-map','0:v:0','-map','1:a:0','-frames:v','1440','-t','60','-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p','-c:v','libx264','-threads','1','-preset','fast','-crf','19','-bf','0','-c:a','aac','-b:a','256k','-ar','48000','-f','mp4','-fd','1','fd:']
pages=[];changes=[];font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
with out.open('wb') as movie,log.open('wb') as err:
    enc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=movie,stderr=err)
    try:
        for i,s in enumerate(P['shots']):
            path=H/s['asset'];n=s['frames']
            reframe=s.get('reframe',{});k=reframe.get('scale',1);sw=round(1920*k/2)*2;sh=round(1080*k/2)*2;cx=(sw-1920)/2-reframe.get('x',0);cy=(sh-1080)/2-reframe.get('y',0)
            spatial=f'scale={sw}:{sh},crop=1920:1080:{cx}:{cy},' if k!=1 else ''
            command=[F,'-v','error','-threads','1','-filter_threads','1','-i',str(path),'-an','-vf',f'trim=start_frame=12:end_frame={12+n},{spatial}scale={W}:{HGT}:in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24','-fps_mode','passthrough','-frames:v',str(n),'-f','rawvideo','pipe:1']
            raw=subprocess.run(command,capture_output=True,check=True).stdout;arr=np.frombuffer(raw,dtype=np.uint8).reshape(-1,HGT,W,3);assert len(arr)==n
            enc.stdin.write(raw)
            if i%6==0:
                page=Image.new('RGB',(1440,6*310),'#080b13');draw=ImageDraw.Draw(page);pages.append(page)
            row=i%6;y=row*310;draw.text((8,y+2),f'{s["id"]} {s.get("candidateId","BLACK")} F{s["startFrame"]}–{s["startFrame"]+n} · rate {s.get("playbackRate",1):.3f}',font=font,fill='#72c7ed')
            for col,k in enumerate([0,n//2,n-1]):page.paste(Image.fromarray(arr[k]).resize((480,270)),(col*480,y+34))
            diff=np.abs(arr[1:,::6,::6].astype(float)-arr[:-1,::6,::6].astype(float)).mean((1,2,3))
            changes.append({'shot':s['id'],'peaks':[{'preparedFrame':12+int(k)+1,'outputFrame':s['startFrame']+int(k)+1,'meanAbsoluteDiff':float(diff[k])} for k in np.where(diff>35)[0]],'status':'machine_candidates_not_certified_cuts'})
            if i%8==0:print('ROUGH',i+1,'/',len(P['shots']),flush=True)
        enc.stdin.close();assert enc.wait()==0
    except BaseException:
        enc.kill();raise
EV=R/('evidence/retrieved-shot-contacts-focus-v2' if revision=='L1-FOCUS-v2' else 'evidence/retrieved-shot-contacts');EV.mkdir(exist_ok=True)
for i,page in enumerate(pages):page.save(EV/f'retrieval-{i+1:02}.jpg',quality=91)
(R/'data/retrieved-cut-candidates.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
info=json.loads(subprocess.run([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(out)],capture_output=True,check=True).stdout);v=next(s for s in info['streams'] if s['codec_type']=='video');assert int(v['nb_read_frames'])==1440 and v['avg_frame_rate']=='24/1'
execution={'executor':'/root/s1_design_spec','loop':1,'video':'loops/loop-01/loop-01-rough.mp4','sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'renderMethod':'original S1 prepared source frames -> actual FFmpeg raw RGB encode; naked cut with deliberate black only, complex effects deferred to L2','timelineClips':58,'sourceVideoClips':57,'proceduralBlackClips':1,'fps':24,'frames':1440,'seconds':60,'size':[W,HGT],'audioMaster':'music/master.wav','actualAuditoryListening':False,'actualRenderedEffects':['native cut/timing/rate','intentional 8-frame black'],'notYetExecuted':['screen frame','alpha','paper energy','slit','leaves','art typography'],'contacts':'evidence/retrieved-shot-contacts','cutCandidateReport':'data/retrieved-cut-candidates.json','approvedDesignPreserved':'data/edit-plan.json','inputExecutionPlan':'loops/loop-01/plan.json','ffprobe':info}
(L/'hyperframes-edit.json').write_text(json.dumps(P,ensure_ascii=False,indent=2),encoding='utf-8')
execution['video']=out.relative_to(R).as_posix();execution['contacts']=EV.relative_to(R).as_posix();execution['revision']=revision
(L/'plan.json').write_text(json.dumps(P,ensure_ascii=False,indent=2),encoding='utf-8')
(L/'execution.json').write_text(json.dumps(execution,ensure_ascii=False,indent=2),encoding='utf-8')
print('VERIFIED L1',execution['sha256'],flush=True)
