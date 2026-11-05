from pathlib import Path
import json,time,shutil,hashlib,datetime,os,sys
ROOT=Path(__file__).resolve().parents[1];W=ROOT/'workflow';W.mkdir(exist_ok=True);last=None
def atomic_state(path,value):
    temp=path.with_name(path.name+f'.{os.getpid()}.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    for attempt in range(6):
        try:
            temp.replace(path)
            return
        except PermissionError:
            if attempt==5:raise
            print(f'MONITOR_ATOMIC_RETRY {attempt+1}/6',file=sys.stderr,flush=True)
            time.sleep(.05*2**attempt)
while True:
    now=time.time();episodes=[];alerts=[]
    for p in sorted((ROOT/'素材集_60Hz_JPG').glob('*/progress.json')):
        try:r=json.loads(p.read_text(encoding='utf-8'))
        except (ValueError,OSError):continue
        episodes.append({k:r.get(k) for k in ['id','state','samplesWritten','expectedSamples','nativeFramesDecoded','heartbeatUnix']})
        if r.get('state')=='running' and now-r.get('heartbeatUnix',now)>180:alerts.append({'type':'stale_heartbeat','episode':r['id']})
        if r.get('state')=='failed':alerts.append({'type':'worker_failure','episode':r['id'],'error':r.get('error')})
    free=shutil.disk_usage(ROOT).free
    if free<80*1024**3:alerts.append({'type':'low_disk','freeBytes':free})
    render=None
    rp=W/'render-heartbeat.json'
    if rp.exists():
        try:render=json.loads(rp.read_text(encoding='utf-8'))
        except (ValueError,OSError):pass
    if render and render.get('state')=='running' and now-render.get('heartbeatUnix',now)>180:alerts.append({'type':'render_stale','loop':render.get('loop'),'chunk':render.get('chunk')})
    if render and render.get('state')=='running':
        workers=render.get('workers',[])
        stalled=[w for w in workers if w.get('state')=='running' and (w.get('stalled') or now-w.get('lastProgressUnix',w.get('heartbeatUnix',now))>180)]
        if render.get('stalled') or stalled:alerts.append({'type':'render_no_frame_progress','loop':render.get('loop'),'workers':stalled})
    if render and render.get('state')=='failed':alerts.append({'type':'render_failed','details':render})
    loops=[]
    for p in sorted((ROOT/'loops').glob('loop-*/review.json')):
        try:r=json.loads(p.read_text(encoding='utf-8'));loops.append({'path':str(p.relative_to(ROOT)), 'status':r.get('status',r.get('decision'))})
        except (ValueError,OSError):pass
    state={'time':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'heartbeatUnix':now,'freeBytes':free,'episodesComplete':sum(x['state']=='complete' for x in episodes),'samplesWritten':sum(x.get('samplesWritten') or 0 for x in episodes),'episodes':episodes,'loops':loops,'alerts':alerts,'owner':'orchestrator /root','monitorPolicy':'5秒刷新，180秒无心跳标红；发现失败由编排层审核后重分派，最多两次，不自动跳过门禁'}
    state['render']=render
    atomic_state(W/'monitor.json',state)
    key=json.dumps([[(x['id'],x['state'],(x.get('samplesWritten') or 0)//3600) for x in episodes],loops,alerts,None if not render else [render.get('state'),render.get('loop'),render.get('chunk'),render.get('framesCaptured')]])
    if key!=last:
        with (W/'events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(state,ensure_ascii=False)+'\n')
        last=key
    if (W/'delivered.json').exists():break
    time.sleep(5)
