from pathlib import Path
from fractions import Fraction
from datetime import datetime,timezone
import json,hashlib,subprocess,shutil
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];L=R/'loops/loop-04';O=L/'reviewer-evidence';I=L/'prepared-review-inputs';I.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for aid in ['T062','T091','T007']:
    path=R/f'evidence/tail-retrieval/{aid}.json';m=json.loads(path.read_text(encoding='utf-8'));proofPath=Path(m['nativeProof']);proof=json.loads(proofPath.read_text(encoding='utf-8'))
    for source,target in [(path,I/f'{aid}.json'),(proofPath,I/f'{aid}-native-proof.json')]:
        if not target.exists():shutil.copyfile(source,target)
    native=[]
    for j,f in enumerate(proof['files']):
        fp=proofPath.parent/f['path'];assert sha(fp)==f['sha256'];native.append(fp)
        assert abs(float(Fraction(proof['sourcePtsIntegers'][j])*Fraction(proof['timeBase']))-m['actualSourcePtsSeconds'][j])<1e-9
    asset=R/'hyperframes'/m['asset']['asset'];assert sha(asset)==m['asset']['sha256']
    raw=subprocess.run(['C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe','-v','error','-i',str(asset),'-vf','scale=in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],capture_output=True,check=True).stdout
    frames=np.frombuffer(raw,np.uint8).reshape(-1,1080,1920,3);assert len(frames)==m['outputFrames'];mads=[];last=-1;dups=0
    for j,z in enumerate(m['sourceSampleMapping']):
        n=z['nativeCoreIndex'];assert z['preparedFrame']==j and n==int(np.floor(j*(len(native)-1)/(len(frames)-1)+.5))
        assert z['duplicateOfPrevious']==(n==last);dups+=int(n==last);last=n
        assert abs(z['sourcePtsSeconds']-m['actualSourcePtsSeconds'][n])<1e-9
        src=np.asarray(Image.open(native[n]).convert('RGB'));expected=np.zeros((1080,1920,3),np.uint8);x,y,w,h=m['cropOriginal'];top=m['padTop'];expected[top:top+h]=src[y:y+h,x:x+w]
        mads.append(float(np.abs(frames[j].astype(np.float32)-expected.astype(np.float32)).mean()))
    assert max(mads)<3,(aid,max(mads))
    rows.append({'assetId':aid,'assetSha256':sha(asset),'nativeFramesHashed':len(native),'preparedFramesIndependentlyDecodedCompared':len(frames),'duplicateSamplesVerified':dups,'maxNativeCroppedPixelMAD':max(mads),'mappingIntegerPtsAndNearestIndexPass':True})
    if aid=='T091':
        im=Image.new('RGB',(1920,7*180),'#070d17');d=ImageDraw.Draw(im)
        for j,fp in enumerate(native):
            a=Image.open(fp).convert('RGB').crop((0,900,1920,1080));a.resize((480,150));a=a.resize((480,150));x=j%4*480;y=j//4*180;im.paste(a,(x,y));d.text((x+3,y+153),f'native{j:02} PTS{m["actualSourcePtsSeconds"][j]:.6f} y900..1079',fill='#94d8ec')
        im.save(O/'T091-highres-native-bottom23.jpg',quality=96)
report={'reviewer':'/root/s1_design_auditor','check':'independent70actualpreparedframes_rgb_sourceorder_pts_and_nativeSHA','rows':rows,'totalPreparedFrames':sum(x['preparedFramesIndependentlyDecodedCompared'] for x in rows),'totalNativeFrames':sum(x['nativeFramesHashed'] for x in rows),'machinePass':True,'limitations':'MAD阈值3覆盖H264压缩误差，不等于逐像素无损；全70帧实际解码比对，不替代合成艺术审核。'}
(O/'prepared-independent-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
