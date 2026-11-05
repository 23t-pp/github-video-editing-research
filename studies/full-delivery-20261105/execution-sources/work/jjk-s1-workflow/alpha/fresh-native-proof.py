from pathlib import Path
import subprocess,json,re,hashlib,numpy as np
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parents[3];R=B/'outputs/jjk-s1-workflow';E=R/'evidence/source-overviews/fresh-candidates/native';E.mkdir(exist_ok=True);ff='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15);rows=[]
for it in json.loads((R/'data/fresh-shot-candidates.json').read_text(encoding='utf-8'))['items']:
 cid=it['candidateId'];a,b=it['coreSourceSeconds'];cmd=[ff,'-v','info','-threads','1','-ss',str(a),'-i',it['sourcePath'],'-t',str(b-a),'-an','-vf','scale=320:180,showinfo','-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','pipe:1'];p=subprocess.run(cmd,capture_output=True,check=True);raw=p.stdout;frames=np.frombuffer(raw,np.uint8).reshape(-1,180,320,3);pts=[a+float(x) for x in re.findall(r' n:\s*\d+ pts:\s*[-\d]+ pts_time:([-\d.]+)',p.stderr.decode('utf-8',errors='replace'))]
 # PTS label is derived from actual showinfo output; no invented interpolated samples.
 s=Image.new('RGB',(1920,((len(frames)+5)//6)*200),'#111')
 for f,arr in enumerate(frames):
  x=f%6*320;y=f//6*200;s.paste(Image.fromarray(arr),(x,y));ImageDraw.Draw(s).text((x+4,y+181),f'{cid} f{f} '+(f'{pts[f]:.5f}s' if f<len(pts) else 'PTS unavailable'),font=font,fill='white')
 sp=E/f'{cid}-native-all.jpg';s.save(sp,quality=95)
 mov=E/f'{cid}-navigation-only.mp4';out=subprocess.run([ff,'-v','error','-threads','1','-f','rawvideo','-pix_fmt','rgb24','-s','320x180','-r','24000/1001','-i','pipe:0','-an','-c:v','libx264','-threads','1','-crf','24','-pix_fmt','yuv420p','-bf','0','-movflags','frag_keyframe+empty_moov+default_base_moof','-f','mp4','pipe:1'],input=raw,capture_output=True,check=True).stdout;mov.write_bytes(out)
 rows.append({'candidateId':cid,'requestedCoreSeconds':[a,b],'decodedNativeFrames':len(frames),'sourcePtsSeconds':pts[:len(frames)],'sheet':sp.relative_to(R).as_posix(),'navigationClip':mov.relative_to(R).as_posix(),'clipSha256':hashlib.sha256(out).hexdigest(),'humanViewedAllFrames':False,'cutStatus':'pending visual review','warning':'320x180 original-frame navigation evidence only; final high resolution must return original source'})
 print(cid,len(frames),len(pts),flush=True)
(R/'data/fresh-native-verification.json').write_text(json.dumps({'version':'FRESH-NATIVE-0.1','status':'await actual sheet inspection','items':rows},ensure_ascii=False,indent=2),encoding='utf-8')
