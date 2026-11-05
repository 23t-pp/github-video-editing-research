from pathlib import Path
from PIL import Image
import numpy as np,json,sys
B=Path(__file__).resolve().parents[3];R=B/'outputs/jjk-s1-workflow';sys.path.insert(0,str(B/'work/reference-replay-v07/python-deps'))
import cv2
O=R/'hyperframes/assets/alpha/XCHASE';j=json.loads((R/'evidence/alpha/XCHASE-alpha-report.json').read_text(encoding='utf-8'));records={r['preparedFrame']:r for r in j['records']}
# Anatomical source-E pose: only the arm/torso triangular negative space. Coordinates traced from actual original RGB, never RGB repaint.
poly=np.array([(1200,836),(1190,856),(1179,878),(1166,898),(1157,912),(1152,922),(1175,935),(1189,915),(1211,915),(1217,916),(1225,902),(1238,890),(1250,888),(1268,892),(1280,898),(1294,892),(1311,889),(1326,884)],np.int32)
for f in [11,12,23,24]:
 p=O/f'{f:06}.png';im=np.array(Image.open(p));a=im[:,:,3];area=np.zeros(a.shape,np.uint8);cv2.rectangle(area,(1100,780),(1390,985),255,-1);hole=np.zeros(a.shape,np.uint8);cv2.fillPoly(hole,[poly],255)
 rec=records[f]
 if rec.get('warpAccepted'):
  mat=np.array(rec['matrix']);area=cv2.warpAffine(area,mat,(1920,1080));hole=cv2.warpAffine(hole,mat,(1920,1080))
 a[area>127]=255;a[hole>127]=0;a=cv2.GaussianBlur((a>127).astype(np.uint8)*255,(0,0),.65);a[:60]=0;a[1008:]=0;im[:,:,3]=a;Image.fromarray(im).save(p)
print('4 E-pose inner-arm source contours corrected')
