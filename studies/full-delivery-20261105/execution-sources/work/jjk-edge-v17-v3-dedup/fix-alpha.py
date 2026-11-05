from pathlib import Path
import importlib.util,json,sys
W=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('alpha',W/'alpha.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
cv2,np=a.cv2,a.np
a.S['N34']=[(72,194),(76,185),(116,168),(145,158),(156,148),(158,139),(158,128),(151,111),(152,99),(151,86),(155,76),(158,65),(161,53),(166,42),(170,35),(180,27),(190,31),(201,35),(211,43),(217,53),(225,58),(232,69),(235,81),(237,97),(231,110),(224,125),(216,136),(218,150),(239,162),(265,174),(289,189),(293,194)]
a.S['N35']=[(191,194),(191,165),(195,139),(202,125),(215,124),(219,113),(220,105),(215,102),(211,102),(206,101),(211,96),(211,91),(216,87),(217,82),(211,81),(208,78),(208,72),(214,68),(219,60),(220,51),(222,44),(226,35),(237,29),(247,28),(259,31),(267,32),(273,29),(282,32),(286,42),(282,50),(296,53),(284,60),(291,65),(281,69),(279,82),(271,91),(267,101),(276,113),(276,119),(288,125),(293,144),(293,170),(289,194)]
a.S['N36']=[(70,194),(68,166),(73,145),(80,135),(94,129),(98,122),(96,115),(99,104),(101,92),(106,85),(118,80),(130,82),(136,88),(138,103),(140,116),(141,126),(153,134),(163,144),(168,158),(165,178),(160,194)]
a.S['N37']=[(194,194),(194,172),(198,157),(195,148),(186,143),(179,136),(175,128),(167,124),(165,120),(169,114),(166,111),(155,110),(158,103),(161,96),(158,87),(156,78),(159,66),(164,56),(170,49),(179,44),(194,44),(207,48),(219,55),(228,66),(233,77),(237,84),(239,104),(246,121),(251,132),(228,142),(222,148),(229,162),(234,194)]
# Round the visible crown rather than leave the preliminary angular contour.
q=a.S['N34'];left=q[:11];right=q[22:]
a.S['N34']=left+[(158,65),(160,49),(166,39),(176,31),(190,28),(204,29),(219,36),(229,48),(235,65),(237,81)]+right
old=a.r.refine_grabcut;active={}
def corrected(im,mask,band):
 id=active['asset'];b,g,r=[im[:,:,i].astype(np.int16) for i in range(3)]
 if id=='N39':
  skin=((r>100)&(g>70)&(b>40)&(r-g>12)&(r-g<95)&(g-b>3)&(g-b<50)).astype(np.uint8)*255
  skin=cv2.morphologyEx(skin,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
  cs,_=cv2.findContours(skin,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);out=np.zeros_like(mask)
  if cs:cv2.drawContours(out,[max(cs,key=cv2.contourArea)],-1,255,-1)
  return out
 out=old(im,mask,band)
 if id=='N38':
  goldgreen=(g>b*1.06)&(g>r*.90)
  out[goldgreen]=0
  support=cv2.dilate((mask>127).astype(np.uint8),np.ones((81,81),np.uint8))>0
  skin=(r>100)&(g>70)&(b>45)&(r-g>12)&(r-g<95)&(g-b>3)&(g-b<50)&support
  out[skin]=255
  out=cv2.morphologyEx(out,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
 if id=='N21':
  keep=(r>105)&(g>75)&(b>65)&(r-g<80)&(g-b<55)
  out[~keep]=0
  cs,_=cv2.findContours(out,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
  filled=np.zeros_like(out)
  if cs:cv2.drawContours(filled,[max(cs,key=cv2.contourArea)],-1,255,-1)
  out=filled
 return out
a.r.refine_grabcut=corrected
for j in json.loads((W/'foreground-jobs.json').read_text(encoding='utf8')):
 if len(sys.argv)>1 and j['id'] not in sys.argv[1:]:continue
 (a.EV/f"{j['id']}.json").unlink(missing_ok=True)
 active['asset']=j['assetId'];a.main(j)
