from scout import *
import numpy as np,hashlib
src=Path(json.loads((ROOT/'outputs/reference-library-20261105/local-media-paths.json').read_text(encoding='utf-8'))['V17'])
out=ROOT/'outputs/jjk-edge-v17/evidence/V17-关键技法';out.mkdir(parents=True,exist_ok=True)
fs=[150,154,160,452,453,454,455,456,520,521,522]
sel='+'.join(f'eq(n,{f})' for f in fs)
r=subprocess.run([FF,'-v','error','-threads','1','-filter_threads','1','-i',str(src),'-vf',f"select='{sel}'",'-fps_mode','passthrough','-frames:v',str(len(fs)),'-threads','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],capture_output=True);r.check_returncode()
a=np.frombuffer(r.stdout,np.uint8).reshape(len(fs),1080,1920,3)
for f,arr in zip(fs,a):Image.fromarray(arr).save(out/f'V17-F{f:03}-{f/30:.6f}s.jpg',quality=96)
(out/'关键帧索引.json').write_text(json.dumps({'source':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'nativeFps':'30/1','frameIndexing':'0-based native decoded frame n; no ss, no fps filter, no interpolation','selected':[{'technique':'撕边竖人像','frame':154,'seconds':154/30,'file':'V17-F154-5.133333s.jpg'},{'technique':'手已盖旧双笑脸未全幅','frame':454,'seconds':454/30,'file':'V17-F454-15.133333s.jpg'},{'technique':'双半脸','frame':522,'seconds':522/30,'file':'V17-F522-17.400000s.jpg'}]},ensure_ascii=False,indent=2),encoding='utf-8')
print(str(out),probe(src)['format'].get('start_time'),flush=True)
