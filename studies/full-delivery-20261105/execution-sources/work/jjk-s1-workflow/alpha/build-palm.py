from pathlib import Path
import subprocess,sys,json,hashlib
BASE=Path(__file__).resolve().parents[3];R=BASE/'outputs/jjk-s1-workflow';W=Path(__file__).resolve().parent;EV=R/'evidence/alpha';O=R/'hyperframes/assets/alpha/XPALM';O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(BASE/'work/reference-replay-v07/python-deps'))
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
cv2.setNumThreads(1)
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';MOV=R/'hyperframes/assets/shots/XPALM.mp4'
raw=subprocess.run([FF,'-v','error','-threads','1','-i',str(MOV),'-an','-vf','scale=in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24','-f','rawvideo','pipe:1'],capture_output=True,check=True).stdout
frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,1080,1920,3);assert len(frames)==31
if '--inspect' in sys.argv:
    for f in [2,15,27]:Image.fromarray(frames[f]).save(EV/f'XPALM-source-F{f:02}.png')
    print('inspection RGB frames extracted');raise SystemExit
# Manual outer contour from the source review, transformed only by the approved crop/pad geometry.
# Key refinement is applied on actual prepared source frames below; no source RGB replacement.
P=[(640,321),(566,318),(513,313),(500,309),(495,298),(492,273),(489,243),(486,237),(451,237),(423,239),(398,246),(376,258),(355,266),(335,269),(309,276),(284,283),(249,286),(212,287),(181,281),(170,276),(167,266),(174,260),(196,257),(218,251),(242,249),(247,243),(228,230),(205,219),(182,207),(171,194),(160,178),(161,169),(166,162),(175,160),(190,166),(205,177),(213,184),(212,168),(216,153),(221,135),(225,119),(235,114),(243,118),(250,133),(253,151),(261,161),(273,158),(288,146),(295,138),(311,137),(326,139),(334,145),(330,151),(317,155),(306,156),(300,163),(301,173),(330,171),(356,159),(385,148),(416,147),(443,158),(466,163),(493,164),(509,166),(526,157),(640,157)]
# Original 640x360 review pixels -> full1920 original -> prepared (pad top60).
poly=np.array([(1919,1019),(1500,1018),(1470,1013),(1450,1002),(1435,985),(1426,960),(1420,920),(1415,880),(1410,840),(1400,813),(1390,795),(1370,788),(1350,785),(1300,785),(1250,798),(1200,812),(1150,832),(1100,851),(1050,867),(1000,881),(950,890),(900,911),(850,922),(800,924),(750,923),(700,920),(650,916),(600,915),(550,911),(520,900),(505,889),(497,871),(500,853),(510,840),(535,830),(565,825),(595,820),(625,812),(650,805),(675,797),(690,790),(650,780),(610,760),(580,740),(550,720),(530,690),(510,660),(490,630),(475,600),(470,580),(475,562),(485,550),(500,540),(520,538),(545,542),(570,555),(590,575),(610,595),(630,615),(650,632),(675,641),(690,646),(676,610),(670,570),(669,520),(671,470),(675,430),(686,408),(704,407),(726,416),(746,439),(758,468),(768,500),(777,526),(789,548),(802,555),(813,551),(815,536),(807,516),(803,490),(806,467),(818,447),(835,431),(854,419),(880,411),(910,409),(945,410),(974,411),(997,417),(1014,429),(1022,446),(1018,465),(1003,478),(980,484),(953,488),(927,487),(904,482),(886,476),(888,490),(903,507),(920,515),(942,520),(963,526),(983,533),(1000,533),(1015,525),(1040,513),(1070,503),(1110,489),(1150,480),(1190,476),(1230,477),(1270,486),(1310,500),(1350,512),(1390,520),(1440,522),(1475,520),(1500,516),(1540,518),(1580,522),(1640,533),(1700,540),(1760,550),(1820,562),(1880,575),(1919,580)],np.int32)
base=np.zeros((1080,1920),np.uint8);cv2.fillPoly(base,[poly],255)
yy,xx=np.indices((1080,1920));checker=np.repeat(np.where(((xx//32+yy//32)%2)[...,None],155,80),3,axis=2).astype(np.uint8);red=np.full((1080,1920,3),(190,38,38),np.uint8)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
allcount=[];bounds=[];cells={'checker':[],'red':[]};alphas=[]
for f in range(2,28):
    rgb=frames[f];bgr=rgb[:,:,::-1].copy();gray=cv2.cvtColor(bgr,cv2.COLOR_BGR2GRAY)
    # Refine only within a narrow manual support so unrelated background glow is excluded.
    support=cv2.dilate(base,np.ones((17,17),np.uint8));core=cv2.erode(base,np.ones((17,17),np.uint8))
    mask=np.full(base.shape,cv2.GC_BGD,np.uint8);mask[support>0]=cv2.GC_PR_BGD;mask[base>0]=cv2.GC_PR_FGD;mask[core>0]=cv2.GC_FGD
    # Native sleeve stays attached through the right canvas edge; no imaginary arm extension.
    mask[:60]=cv2.GC_BGD;mask[1020:]=cv2.GC_BGD
    cv2.grabCut(bgr,mask,None,np.zeros((1,65),float),np.zeros((1,65),float),2,cv2.GC_INIT_WITH_MASK)
    matte=np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),255,0).astype(np.uint8)
    matte=cv2.GaussianBlur(matte,(0,0),.65);matte[:60]=0;matte[1020:]=0
    rgba=np.dstack((rgb,matte));Image.fromarray(rgba).save(O/f'{f:06}.png');assert np.array_equal(np.array(Image.open(O/f'{f:06}.png'))[:,:,:3],rgb)
    a=matte[:,:,None]/255
    for kind,bg in [('checker',checker),('red',red)]:
        comp=Image.fromarray((rgb*a+bg*(1-a)).astype(np.uint8)).resize((480,270));draw=ImageDraw.Draw(comp);draw.text((7,5),f'XPALM F{f:02}',font=font,fill='yellow');cells[kind].append(comp)
    ys,xs=np.where(matte>127);allcount.append(int(len(xs)));bounds.append([int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]);alphas.append(matte)
for kind,images in cells.items():
    for page,start in enumerate(range(0,len(images),16)):
        selected=images[start:start+16];sheet=Image.new('RGB',(1920,270*((len(selected)+3)//4)),'black')
        for k,im in enumerate(selected):sheet.paste(im,((k%4)*480,(k//4)*270))
        sheet.save(EV/f'XPALM-{kind}-{page+1:02}.jpg',quality=94)
prep=json.loads((EV/'XPALM-prepared-source.json').read_text(encoding='utf-8'))
report={'id':'XPALM','season':1,'candidateId':'S1C020','preparedMovie':MOV.relative_to(R).as_posix(),'preparedSha256':prep['preparedSha256'],'firstPreparedFrame':2,'lastPreparedFrameExclusive':28,'count':26,'fps':24,'clock':'same prepared XPALM file frame number; global event offset2 uses000002.png','allRgbExactlyEqualsPreparedDecodedFrame':True,'rgbDecodeFilter':'scale=in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24','blackBandsAlphaZero':True,'activeRect':[0,60,1920,960],'method':'manual visible source contour support, 35px constrained GrabCut,0.65px feather; no generated/repainted source pixels','alphaPixelCounts':allcount,'bounds':bounds,'manualPolygon':poly.tolist(),'visuallyReviewed':False,'limitations':'Original palm/wrist extends beyond right frame; approved crop removes source bottom120 rows. Original cyan glow and soft spill remain; no reconstruction of offscreen arm. Must inspect red/checker sheet before acceptance.'}
(EV/'XPALM-alpha-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('Built26 RGBA, awaits actual red/checker view')
