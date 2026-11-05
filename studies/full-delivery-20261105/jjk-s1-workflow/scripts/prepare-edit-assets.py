"""Approved Season 1 retrieval; preserve reviewed plan and write execution snapshot."""
from pathlib import Path
import json,subprocess,hashlib,re,time
R=Path(__file__).resolve().parent.parent;H=R/'hyperframes';W=R/'loops/loop-01';W.mkdir(parents=True,exist_ok=True)
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';FP='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'
plan=json.loads((R/'data/edit-plan.json').read_text(encoding='utf-8'))
review=json.loads((R/'reviews/剪辑设计审核.json').read_text(encoding='utf-8'))
assert review['status']=='pass'
assert hashlib.sha256((R/'data/edit-plan.json').read_bytes()).hexdigest()==review['boundArtifacts']['data/edit-plan.json']
# Same-source extensions verified by full 24fps contact sheets, not invented motion.
extensions={'S019':(403.95,1.0),'S034':(693.95,1.0),'S038':(209.72,.70),'S040':(269.40,.80),'S046':(918.95,1.0)}
diff=[]
for s in plan['shots']:
    if s['id'] in extensions:
        start,rate=extensions[s['id']];old={k:s[k] for k in ['sourceInSeconds','sourceOutSeconds','playbackRate']}
        s.update(sourceInSeconds=start,sourceOutSeconds=start+s['frames']/24*rate,playbackRate=rate)
        diff.append({'findingId':'B-SLOW-01','shot':s['id'],'old':old,'new':{k:s[k] for k in old},'reason':'同一原镜扩大真实已查看动作范围，取消极慢速；保留时间线长度','evidence':f'evidence/slow-window-inspection/{s["id"]}-{s["candidateId"]}.jpg'})
plan['version']='EDIT-B0.1-LOOP1';plan['status']='executing_loop1_approved_retrieval_with_recorded_slow_window_fixes'
(W/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
(W/'revision-diff.json').write_text(json.dumps({'from':'reviewed EDIT-B0.1','to':plan['version'],'changes':diff,'approvedDesignNotOverwritten':True},ensure_ascii=False,indent=2),encoding='utf-8')
out=H/'assets/shots';out.mkdir(parents=True,exist_ok=True);logs=R/'evidence/retrieval-logs';logs.mkdir(exist_ok=True)
assets=[];records=[]
def probe(p):return json.loads(subprocess.run([FP,'-v','error','-count_frames','-show_streams','-of','json',str(p)],capture_output=True,check=True).stdout)['streams'][0]
for i,s in enumerate(plan['shots']):
    target=out/(s['id']+'.mp4');count=s['frames']+24;rate=s.get('playbackRate',1)
    if s['kind']=='black':
        cmd=[FF,'-v','info','-f','lavfi','-i','color=c=0x080b13:s=1920x1080:r=24','-an','-frames:v',str(count)]
        original=None
    else:
        start=max(0,s['sourceInSeconds']-.5*rate);span=count/24*rate+.15
        cmd=[FF,'-v','info','-threads','1','-filter_threads','1','-ss',f'{start:.9f}','-t',f'{span:.9f}','-i',s['sourcePath'],'-an','-vf',f'showinfo,setpts=(PTS-STARTPTS)/{rate:.9f},fps=24,crop=1920:960:0:0,pad=1920:1080:0:60:black','-frames:v',str(count)]
        original={'sourcePath':s['sourcePath'],'sourceId':s['sourceId'],'decodeSeekSeconds':start,'requestedFormalSourceIn':s['sourceInSeconds'],'requestedFormalSourceOut':s['sourceOutSeconds'],'playbackRate':rate,'geometry':'crop source y0..959; pad y60..1019; no stretch'}
    cmd+=['-c:v','libx264','-threads','1','-preset','fast','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-bf','0','-movflags','frag_keyframe+empty_moov+default_base_moof','-f','mp4','pipe:1']
    key=hashlib.sha256(json.dumps(cmd,ensure_ascii=False).encode()).hexdigest();marker=target.with_suffix('.key')
    if not (target.exists() and marker.exists() and marker.read_text()==key):
        start_wall=time.time()
        p=subprocess.run(cmd,capture_output=True)
        (logs/(s['id']+'.log')).write_bytes(p.stderr)
        if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-2000:])
        target.write_bytes(p.stdout);info=probe(target);assert int(info['nb_read_frames'])==count,(s['id'],info)
        marker.write_text(key)
    else:info=probe(target)
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    assets.append({'id':s['id'],'asset':f'assets/shots/{s["id"]}.mp4','frames':count,'usableFrames':s['frames'],'sha256':digest,'sourceFps':'24000/1001','sourcePath':s.get('sourcePath'),'sourceIn':s.get('sourceInSeconds'),'sourceId':s.get('sourceId'),'description':s.get('focus','有意短黑')})
    records.append({'shot':s['id'],'file':str(target.relative_to(R)).replace('\\','/'),'frames':count,'formalPreparedRange':[12,12+s['frames']],'sha256':digest,'source':original,'ffprobe':info,'command':cmd,'exactCutBoundaryHumanStatus':'pending_all_shot_contact_review'})
    s.update(assetId=s['id'],asset=f'assets/shots/{s["id"]}.mp4',assetStartFrame=12,cameraLocked=True,punch=0,rotation=0)
    if i%5==0:print(f'PREPARED {i+1}/{len(plan["shots"])} {s["id"]}',flush=True)
plan['assets']=assets;plan['audio']={'master':'assets/audio/master.wav','source':'V20 library candidate'}
plan['visuals']=[];plan['layouts']=[];plan['foregrounds']=[];plan['typeEvents']=[];plan['flashes']=[]
(H/'assets/audio').mkdir(exist_ok=True)
import shutil
shutil.copy2(R/'music/master.wav',H/'assets/audio/master.wav')
(H/'edit.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'data/retrieved-assets.json').write_text(json.dumps({'version':'LOOP1-retrieval','assets':records,'sourcePolicy':'All picture pixels original S1; procedural black only; S2 code reuse has no picture assets'},ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared',len(assets),'assets; source boundaries still require contact review',flush=True)
