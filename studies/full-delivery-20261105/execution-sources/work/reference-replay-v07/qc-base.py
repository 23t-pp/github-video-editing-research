from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work/reference-replay-v07/python-deps'))
import cv2,numpy as np
HF=ROOT/'outputs/reference-replay-next/hyperframes';plan=json.loads((HF/'edit.json').read_text(encoding='utf-8'))
assets=[a for a in plan['assets'] if a['id'].startswith('P')]
out=ROOT/'work/reference-replay-v07/qc';out.mkdir(exist_ok=True)
pages=[];rows=[]
for a in assets:
    cap=cv2.VideoCapture(str(HF/a['asset']));cells=[]
    for n in [12,12+a['frames']//2,11+a['frames']]:
        cap.set(cv2.CAP_PROP_POS_FRAMES,n);ok,im=cap.read();assert ok,(a['id'],n)
        im=cv2.resize(im,(480,270));cv2.putText(im,f'{a["id"]}  F{n}',(10,25),cv2.FONT_HERSHEY_SIMPLEX,.7,(40,255,255),1,cv2.LINE_AA);cells.append(im)
    cap.release();rows.append(np.concatenate(cells,axis=1))
    if len(rows)==7:
        pages.append(rows);rows=[]
if rows:pages.append(rows)
for i,rows in enumerate(pages):
    ok,b=cv2.imencode('.jpg',np.concatenate(rows,axis=0),[cv2.IMWRITE_JPEG_QUALITY,90]);assert ok;(out/f'base-{i+1:02}.jpg').write_bytes(b)
print(len(pages),'base contact sheets')
