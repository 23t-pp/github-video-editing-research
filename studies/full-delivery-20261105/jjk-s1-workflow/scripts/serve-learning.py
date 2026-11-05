from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs,unquote
import json,sqlite3,mimetypes,re,time
ROOT=Path(__file__).resolve().parents[1]
def monitor_health(heartbeat,sealed,now=None):
    age=max(0,(time.time() if now is None else now)-heartbeat)
    return {'monitorAgeSeconds':age,'monitorStale':age>180 and not sealed,'monitorSealed':sealed}
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        req=urlparse(self.path);q=parse_qs(req.query)
        try:
            if req.path=='/api/status':
                r=json.loads((ROOT/'workflow/monitor.json').read_text(encoding='utf-8'));p=ROOT/'data/library-verification.json';r['verification']=json.loads(p.read_text(encoding='utf-8')) if p.exists() else {};r['filmReady']=(ROOT/'咒力接力_一分钟.mp4').is_file() and (ROOT/'咒力接力_一分钟.mp4').stat().st_size>10000
                r.update(monitor_health(r.get('heartbeatUnix',0),(ROOT/'workflow/delivered.json').exists()))
                if r['monitorStale']:r.setdefault('alerts',[]).append({'type':'orchestrator_monitor_stale','ageSeconds':round(r['monitorAgeSeconds']),'meaning':'这是上次状态，编排监控超过180秒未更新'})
                r['loopArtifacts']=[]
                for p in sorted((ROOT/'loops').glob('loop-*/execution.json')):
                    try:
                        e=json.loads(p.read_text(encoding='utf-8'));movie=ROOT/e['video'];rp=p.parent/'review.json';review=json.loads(rp.read_text(encoding='utf-8')) if rp.exists() else {}
                        if movie.is_file() and movie.stat().st_size>10000:r['loopArtifacts'].append({'loop':e['loop'],'video':e['video'],'sha256':e['sha256'],'review':review.get('status','pending_review')})
                    except (ValueError,KeyError,OSError):continue
                return self.json(r)
            if req.path=='/api/tags':
                file=ROOT/'data/material-catalog.json'
                if not file.exists():file=ROOT/'data/shot-candidates.json'
                r=json.loads(file.read_text(encoding='utf-8'));search=q.get('q',[''])[0];return self.json([x for x in r['items'] if search in json.dumps([x['characters'],x['visibleActionOrPose'],x['suggestedTechniques'],x.get('motionDirection',''),x.get('alphaMotionEvidence',{}),x.get('tailActionEvidence',{})],ensure_ascii=False)])
            if req.path=='/api/frame':
                episode=int(q.get('episode',['1'])[0]);seconds=float(q.get('time',['0'])[0]);assert 1<=episode<=24 and seconds>=0
                folder=ROOT/'素材集_60Hz_JPG'/f'S1E{episode:02}';db=sqlite3.connect(folder/'index.sqlite');n=round(seconds*60);row=db.execute('SELECT s.sample,s.source_frame,s.duplicate,s.path,n.pts_seconds,n.pts,n.first_path FROM samples s JOIN native n ON s.source_frame=n.frame WHERE s.sample=?',(n,)).fetchone();db.close()
                if not row:return self.json({'error':'该采样尚未生成或超出单集范围'},404)
                sample,f,dup,path,pts,ip,first=row;return self.json({'sample':sample,'sampleSeconds':sample/60,'nativeFrame':f,'duplicate':bool(dup),'sourcePtsSeconds':pts,'sourcePtsInteger':ip,'jpg':'/素材集_60Hz_JPG/'+folder.name+'/'+path,'firstAlias':first,'semantic':'只有已人工看过的候选窗口有语义标签，其余保持未知'})
            path=(ROOT/('学习入口.html' if req.path=='/' else unquote(req.path).lstrip('/'))).resolve();path.relative_to(ROOT.resolve())
            if not path.is_file():return self.json({'error':'文件尚未准备好'},404)
            size=path.stat().st_size;start=0;end=size-1;status=200
            if 'Range' in self.headers:
                m=re.fullmatch(r'bytes=(\d+)-(\d*)',self.headers['Range']);assert m;start=int(m[1]);end=min(size-1,int(m[2])) if m[2] else size-1;status=206
                if start>=size or end<start:return self.json({'error':'invalid range'},416)
            self.send_response(status);self.send_header('Content-Type',mimetypes.guess_type(path)[0] or 'application/octet-stream');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
            if status==206:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
            self.end_headers()
            with path.open('rb') as f:
                f.seek(start);left=end-start+1
                while left:
                    data=f.read(min(left,1024*1024))
                    if not data:break
                    self.wfile.write(data);left-=len(data)
        except (BrokenPipeError,ConnectionResetError):pass
        except Exception as e:self.json({'error':str(e)},400)
    def json(self,x,status=200):
        data=json.dumps(x,ensure_ascii=False).encode('utf-8');self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def log_message(self,*a):pass
print('学习入口 http://127.0.0.1:5351',flush=True);ThreadingHTTPServer(('127.0.0.1',5351),H).serve_forever()
