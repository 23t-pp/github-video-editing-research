from pathlib import Path
import numpy as np,json,hashlib,sys
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3]/'outputs/jjk-s1-workflow';sys.path.insert(0,str(R.parents[1]/'work/reference-replay-v07/python-deps'))
import cv2
cv2.setNumThreads(1)
E=R/'evidence/alpha';O=R/'hyperframes/assets/alpha/XCHASE';yy,xx=np.indices((1080,1920));red=np.full((1080,1920,3),(190,38,38),np.uint8);checker=np.repeat(np.where(((xx//32+yy//32)%2)[...,None],155,80),3,axis=2).astype(np.uint8);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19);cells={'red':[],'checker':[]};checks=[]
for f in range(2,28):
    p=O/f'{f:06}.png';im=np.array(Image.open(p));r,g,b=[im[:,:,k].astype(np.int16) for k in range(3)];a=im[:,:,3]
    # Source pavement behind right head is neutral magenta-grey; pink hair/red hood are red-dominant.
    neutral=(r>18)&(r<220)&(r>b*.85)&(r<b*1.35)&(g>r*.50)&(np.abs(r-b)<55)&(np.abs(r-g)<55)
    head=(xx>1010)&(xx<1300)&(yy>65)&(yy<520)
    edge=cv2.distanceTransform((a>127).astype(np.uint8),cv2.DIST_L2,3)<65
    notches=(((xx>1080)&(yy>680))|((xx<650)&(yy>600)))&edge
    darkhead=(r>1)&(r<220)&(r>b*.60)&(r<b*1.35)&(g>r*.30)&(np.abs(r-b)<55)&(np.abs(r-g)<55)
    bad=(head&darkhead)|(notches&neutral)
    removed=int(((a>0)&bad).sum());a[bad]=0
    count,labels,stats,_=cv2.connectedComponentsWithStats((a>127).astype(np.uint8));keep=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);remaining=(labels==keep).astype(np.uint8)*255;a=cv2.GaussianBlur(remaining,(0,0),.65);a[:60]=0;a[1008:]=0
    im[:,:,3]=a;Image.fromarray(im).save(p);alpha=a[:,:,None]/255
    for kind,bg in [('red',red),('checker',checker)]:
        comp=Image.fromarray((im[:,:,:3]*alpha+bg*(1-alpha)).astype(np.uint8))
        if f in [2,4,6,10,12,27]:comp.save(E/f'XCHASE-{kind}-F{f:02}.png')
        sm=comp.resize((480,270));d=ImageDraw.Draw(sm);d.text((8,5),f'XCHASE F{f:02} final',font=font,fill='yellow');cells[kind].append(sm)
    checks.append({'frame':f,'headPavementPixelsRemoved':removed,'pngSha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for kind,images in cells.items():
    for page,start in enumerate(range(0,len(images),16)):
        sel=images[start:start+16];sheet=Image.new('RGB',(1920,270*((len(sel)+3)//4)),'black')
        for k,img in enumerate(sel):sheet.paste(img,((k%4)*480,(k//4)*270))
        sheet.save(E/f'XCHASE-{kind}-{page+1:02}.jpg',quality=94)
j=json.loads((E/'XCHASE-alpha-report.json').read_text(encoding='utf-8'));j.update(headCleanupChecks=checks,revision='R3.1_remove_neutral_pavement_behind_head',finalCanonicalEvidence='XCHASE-red/checker-01/02.jpg and XCHASE-red-F02/04/06/10/12/27.png; r1/r3-test images are diagnostic only')
(E/'XCHASE-alpha-report.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8');print('head pavement removed, canonical evidence refreshed')
