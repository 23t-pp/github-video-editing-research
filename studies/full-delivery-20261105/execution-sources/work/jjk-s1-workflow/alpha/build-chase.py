from pathlib import Path
import sys,subprocess,json,hashlib
BASE=Path(__file__).resolve().parents[3];R=BASE/'outputs/jjk-s1-workflow';E=R/'evidence/alpha';O=R/'hyperframes/assets/alpha/XCHASE';O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(BASE/'work/reference-replay-v07/python-deps'))
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
cv2.setNumThreads(1)
FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';MOV=R/'hyperframes/assets/shots/XCHASE.mp4'
raw=subprocess.run([FF,'-v','error','-threads','1','-i',str(MOV),'-an','-vf','scale=in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24','-f','rawvideo','pipe:1'],capture_output=True,check=True).stdout;rgb=np.frombuffer(raw,dtype=np.uint8).reshape(-1,1080,1920,3);bgr=rgb[:,:,:,::-1].copy()
# Visible anatomical outlines at five real stride poses, authored against actual prepared frames.
# Coordinates are prepared640x360 scaled3 (pad already included).
P={
'A':[(86,339),(85,314),(93,287),(104,264),(119,234),(132,216),(137,200),(150,184),(165,173),(180,160),(194,149),(210,139),(216,133),(213,127),(207,122),(218,117),(210,114),(228,107),(220,99),(237,98),(228,89),(246,89),(235,79),(252,86),(257,78),(253,68),(265,80),(270,72),(274,64),(275,50),(283,69),(292,58),(300,42),(296,70),(310,59),(323,51),(317,66),(332,59),(344,56),(333,70),(350,68),(362,67),(347,81),(364,80),(373,79),(361,91),(377,93),(366,100),(382,99),(373,111),(370,116),(384,121),(405,132),(420,141),(435,155),(445,170),(456,183),(468,198),(480,212),(491,226),(500,239),(496,253),(503,263),(510,280),(515,288),(520,300),(521,312),(518,323),(512,329),(503,332),(492,329),(483,329),(478,323),(476,313),(471,307),(471,299),(475,294),(470,286),(456,286),(450,279),(446,271),(442,261),(437,254),(431,246),(427,240),(420,245),(415,260),(408,276),(402,291),(397,310),(389,325),(384,339),(198,339),(194,320),(190,303),(184,285),(178,278),(169,285),(161,295),(157,309),(154,326),(153,339)],
'B':[(212,339),(191,333),(175,324),(164,317),(151,315),(140,315),(125,317),(108,319),(93,320),(85,314),(76,300),(65,285),(51,281),(43,272),(42,264),(48,253),(60,241),(72,228),(85,218),(97,211),(108,203),(112,184),(123,180),(137,178),(142,164),(150,149),(165,137),(179,127),(183,109),(189,95),(201,83),(215,72),(229,61),(244,49),(260,38),(275,28),(285,23),(300,23),(315,28),(330,37),(342,47),(354,57),(365,65),(368,73),(392,67),(407,66),(420,66),(431,62),(444,62),(456,55),(470,54),(483,53),(495,47),(503,40),(512,42),(520,56),(529,66),(540,68),(542,79),(538,91),(538,101),(544,106),(551,112),(555,119),(555,127),(550,132),(547,139),(542,142),(536,140),(534,136),(530,136),(526,130),(524,119),(520,110),(508,111),(500,106),(495,97),(483,95),(470,95),(460,93),(447,94),(436,99),(427,108),(419,122),(411,139),(404,156),(400,174),(396,191),(393,209),(387,225),(384,238),(386,250),(384,265),(387,277),(382,290),(388,300),(400,308),(405,315),(404,329),(403,339)],
'C':[(49,339),(60,315),(70,296),(84,279),(99,263),(107,245),(117,230),(124,211),(130,193),(142,175),(158,159),(176,143),(187,139),(185,126),(187,110),(198,99),(201,88),(217,74),(233,62),(248,50),(264,42),(279,39),(294,40),(310,45),(325,54),(338,66),(351,80),(362,91),(382,72),(399,65),(410,66),(420,73),(433,74),(448,77),(461,75),(475,78),(484,80),(489,90),(494,101),(495,113),(502,119),(510,128),(516,139),(521,149),(521,159),(526,165),(533,175),(537,187),(537,199),(533,210),(527,218),(520,220),(516,216),(511,216),(507,210),(498,208),(493,198),(490,185),(487,178),(479,179),(471,176),(460,171),(451,160),(442,156),(429,149),(422,158),(415,173),(408,192),(401,212),(395,232),(390,247),(385,265),(385,281),(378,293),(384,306),(384,319),(384,339)],
'D':[(158,339),(162,319),(161,304),(164,285),(164,267),(158,249),(151,231),(143,210),(135,189),(128,170),(121,151),(114,132),(104,118),(90,111),(79,111),(69,113),(60,109),(49,109),(38,111),(28,109),(17,113),(8,119),(0,130),(0,93),(3,91),(3,83),(0,79),(0,64),(10,62),(15,60),(26,60),(37,54),(49,44),(60,39),(66,36),(75,38),(84,42),(96,47),(109,49),(121,47),(133,48),(144,52),(156,58),(168,55),(179,59),(193,62),(207,59),(222,47),(236,37),(250,31),(265,29),(280,30),(295,35),(310,41),(326,49),(341,61),(353,77),(362,95),(367,117),(369,132),(381,146),(392,158),(403,170),(411,182),(416,190),(427,197),(440,210),(449,219),(462,230),(473,246),(485,263),(495,284),(507,302),(512,319),(515,331),(509,337),(498,339),(478,339),(458,339),(442,339),(430,339),(419,333),(407,327),(396,322),(385,318),(378,309),(375,301),(367,306),(360,310),(356,321),(358,339)],
'E':[(172,339),(171,324),(175,306),(177,289),(174,275),(169,259),(165,243),(161,228),(156,216),(149,208),(140,206),(133,205),(125,207),(119,218),(114,231),(110,247),(102,265),(91,267),(81,266),(74,266),(70,276),(68,290),(62,306),(55,310),(48,313),(41,311),(35,309),(29,305),(24,303),(23,295),(25,287),(24,280),(26,273),(33,266),(40,257),(45,249),(47,238),(50,231),(50,225),(48,221),(56,210),(63,202),(70,189),(75,177),(81,168),(90,157),(92,149),(101,145),(109,145),(116,140),(123,137),(128,132),(135,129),(147,129),(158,125),(171,119),(185,116),(191,100),(194,87),(204,76),(214,62),(226,50),(241,42),(257,35),(275,30),(293,30),(310,35),(327,44),(344,59),(358,76),(368,94),(375,115),(380,133),(384,149),(391,152),(403,163),(418,176),(429,188),(439,194),(449,207),(462,222),(472,235),(482,249),(492,263),(503,279),(514,296),(524,313),(533,330),(536,339)]}
P['D']=P['D'][:P['D'].index((411,182))]+[(408,178),(420,183),(437,195),(450,207),(464,218),(477,233),(490,246),(503,260),(516,274),(528,287),(539,290),(541,297),(539,302),(530,307),(513,311),(493,316),(470,320),(446,322),(430,323),(418,320),(413,315),(408,311),(398,310),(386,312),(373,315),(367,318),(363,321),(367,326),(369,336),(358,339)]
ANCHOR={'A':2,'B':4,'C':6,'D':10,'E':12};PHASE={0:'E',1:'A',2:'A',3:'B',4:'B',5:'C',6:'C',7:'A',8:'A',9:'D',10:'D',11:'E'}
base={};gray=[cv2.cvtColor(x,cv2.COLOR_BGR2GRAY) for x in bgr]
for name,points in P.items():
    m=np.zeros((1080,1920),np.uint8);cv2.fillPoly(m,[np.array(points,np.int32)*3],255);base[name]=m
yy,xx=np.indices((1080,1920));checker=np.repeat(np.where(((xx//32+yy//32)%2)[...,None],155,80),3,axis=2).astype(np.uint8);red=np.full((1080,1920,3),(190,38,38),np.uint8);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19);cells={'red':[],'checker':[]};records=[]
for f in range(2,28):
    phase=PHASE[f%12];a=ANCHOR[phase];m=base[phase].copy();flow={'anchor':a,'phase':phase,'warpAccepted':False}
    if f!=a:
        features=cv2.goodFeaturesToTrack(gray[a],120,.02,12,mask=cv2.erode(m,np.ones((31,31),np.uint8)))
        if features is not None:
            q,status,_=cv2.calcOpticalFlowPyrLK(gray[a],gray[f],features,None,winSize=(25,25),maxLevel=3)
            valid=status.ravel()>0
            if valid.sum()>20:
                mat,inliers=cv2.estimateAffinePartial2D(features[valid],q[valid],method=cv2.RANSAC,ransacReprojThreshold=3)
                if mat is not None and .94<np.hypot(mat[0,0],mat[0,1])<1.06 and np.linalg.norm(mat[:,2])<90:
                    m=cv2.warpAffine(m,mat,(1920,1080));flow.update(warpAccepted=True,matrix=mat.tolist(),inliers=int(inliers.sum()))
    support=cv2.dilate(m,np.ones((41,41),np.uint8));core=cv2.erode(m,np.ones((65,65),np.uint8));gc=np.full(m.shape,cv2.GC_BGD,np.uint8);gc[support>127]=cv2.GC_PR_BGD;gc[m>127]=cv2.GC_PR_FGD;gc[core>127]=cv2.GC_FGD
    rr,gg,bb=[rgb[f,:,:,k].astype(np.int16) for k in range(3)]
    # Real pink/red hair and hood sit on a dark background, permitting source-colour detail seeds.
    hair=(xx>520)&(xx<1210)&(yy>65)&(yy<510)&(rr>60)&(rr>gg*1.16)&(rr>bb*1.08)
    gc[hair]=cv2.GC_FGD
    # Neutral grey pavement visible through arm notches is background, not coat fabric.
    grey=(rr>35)&(rr<145)&(np.abs(rr-gg)<17)&(np.abs(gg-bb)<23)
    notches=((xx>1180)&(yy>680))|((xx<650)&(yy>600))
    gc[grey&notches]=cv2.GC_BGD
    gc[:60]=cv2.GC_BGD;gc[1008:]=cv2.GC_BGD
    cv2.grabCut(bgr[f],gc,None,np.zeros((1,65),float),np.zeros((1,65),float),2,cv2.GC_INIT_WITH_MASK)
    mask=((gc==cv2.GC_FGD)|(gc==cv2.GC_PR_FGD)).astype(np.uint8)*255;n,lab,stats,_=cv2.connectedComponentsWithStats(mask);keep=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);mask=(lab==keep).astype(np.uint8)*255;mask=cv2.GaussianBlur(mask,(0,0),.65);mask[:60]=0;mask[1008:]=0
    rgba=np.dstack((rgb[f],mask));p=O/f'{f:06}.png';Image.fromarray(rgba).save(p);assert np.array_equal(np.array(Image.open(p))[:,:,:3],rgb[f]);assert not mask[:60].any() and not mask[1008:].any()
    alpha=mask[:,:,None]/255
    for kind,bg in [('red',red),('checker',checker)]:
        im=Image.fromarray((rgb[f]*alpha+bg*(1-alpha)).astype(np.uint8));
        if f in [2,4,6,10,12,27]:im.save(E/f'XCHASE-{kind}-F{f:02}.png')
        small=im.resize((480,270));draw=ImageDraw.Draw(small);draw.text((8,5),f'XCHASE F{f:02} {phase}',font=font,fill='yellow');cells[kind].append(small)
    ys,xs=np.where(mask>127);records.append({'preparedFrame':f,'sameRgb':True,'alphaBounds':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],'opaqueArea':int(len(xs)),'pngSha256':hashlib.sha256(p.read_bytes()).hexdigest(),**flow});print('XCHASE',f,phase,flush=True)
for kind,images in cells.items():
    for page,start in enumerate(range(0,len(images),16)):
        sel=images[start:start+16];sheet=Image.new('RGB',(1920,270*((len(sel)+3)//4)),'black')
        for k,img in enumerate(sel):sheet.paste(img,((k%4)*480,(k//4)*270))
        sheet.save(E/f'XCHASE-{kind}-{page+1:02}.jpg',quality=94)
prep=json.loads((E/'XCHASE-prepared-source.json').read_text(encoding='utf-8'));j={'id':'XCHASE','sourceSeason':1,'candidateId':'S1C097','preparedMovie':MOV.relative_to(R).as_posix(),'preparedSha256':prep['preparedSha256'],'firstPreparedFrame':2,'lastPreparedFrameExclusive':28,'frames':26,'fps':24,'clock':'same prepared source frame number; offset2 yields000002..000027','all26RgbExact':True,'rgbDecodeFilter':'scale=in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24','blackBandsAlphaZero':True,'manualAnchors':P,'method':'five real stride anatomical contours, source-only sparse LK affine per phase,25x25 narrow-band GrabCut,largest component,0.65px feather','alphaBottomClipY':1008,'bottomClipReason':'remove residual original hard subtitle tops visible in approved crop/pad at y1015; upperbody ends at this explicit crop, no reconstructed waist/legs','records':records,'visuallyReviewed':False,'acceptance':'await red/checker and original-size actual view; material only, L2 composition independently reviewed','limitations':'Hair points/cloth folds approximate; left hand leaves original canvas in D phase; lower torso/forward fist cut by original bottom crop; source RGB untouched.'};(E/'XCHASE-alpha-report.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8');print('DONE XCHASE26',flush=True)
