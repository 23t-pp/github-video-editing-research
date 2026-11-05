from pathlib import Path
import subprocess,json,numpy as np
R=Path(__file__).resolve().parents[3]/'outputs/jjk-s1-workflow';F='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
raw=subprocess.run([F,'-v','error','-threads','1','-i',str(R/'hyperframes/assets/shots/XCHASE.mp4'),'-an','-vf','scale=160:90','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],capture_output=True,check=True).stdout
imgs=np.frombuffer(raw,np.uint8).reshape(-1,90,160,3).astype(np.int16)
A={'A':2,'B':4,'C':6,'D':10,'E':12};P={0:'E',1:'A',2:'A',3:'B',4:'B',5:'C',6:'C',7:'A',8:'A',9:'D',10:'D',11:'E'};out=[]
for f in range(2,28):
    errors={k:float(np.abs(imgs[f,5:85]-imgs[a,5:85]).mean()) for k,a in A.items()};phase=min(errors,key=errors.get);out.append({'frame':f,'assigned':P[f%12],'nearestActualPose':phase,'same':phase==P[f%12],'distances':errors})
(R/'evidence/alpha/XCHASE-pose-classification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(out,ensure_ascii=False))
