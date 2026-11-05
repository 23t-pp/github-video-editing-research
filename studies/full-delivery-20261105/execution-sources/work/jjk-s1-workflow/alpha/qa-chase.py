from pathlib import Path
import subprocess,json,hashlib,numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3]/'outputs/jjk-s1-workflow';E=R/'evidence/alpha';O=R/'hyperframes/assets/alpha/XCHASE';F='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
raw=subprocess.run([F,'-v','error','-threads','1','-i',str(R/'hyperframes/assets/shots/XCHASE.mp4'),'-an','-vf','scale=in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24','-f','rawvideo','pipe:1'],capture_output=True,check=True).stdout;rgb=np.frombuffer(raw,np.uint8).reshape(-1,1080,1920,3);yy,xx=np.indices((1080,1920));red=np.full((1080,1920,3),(190,38,38),np.uint8);checker=np.repeat(np.where(((xx//32+yy//32)%2)[...,None],155,80),3,axis=2).astype(np.uint8);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19);cells={'red':[],'checker':[]};checks=[]
for f in range(2,28):
    p=O/f'{f:06}.png';im=np.array(Image.open(p));assert np.array_equal(im[:,:,:3],rgb[f]);assert not im[:60,:,3].any() and not im[1008:,:,3].any();a=im[:,:,3:]/255
    for kind,bg in [('red',red),('checker',checker)]:
        comp=Image.fromarray((rgb[f]*a+bg*(1-a)).astype(np.uint8))
        if f in [2,4,6,7,8,10,12,22,23,27]:comp.save(E/f'XCHASE-{kind}-F{f:02}.png')
        small=comp.resize((480,270));d=ImageDraw.Draw(small);d.text((7,5),f'XCHASE F{f:02} R3.2',font=font,fill='yellow');cells[kind].append(small)
    checks.append({'preparedFrame':f,'sameDecodedRgb':True,'bandsAndSubtitleBottomAlphaZero':True,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for kind,images in cells.items():
    for page,start in enumerate(range(0,len(images),16)):
        selected=images[start:start+16];sheet=Image.new('RGB',(1920,270*((len(selected)+3)//4)),'black')
        for k,img in enumerate(selected):sheet.paste(img,((k%4)*480,(k//4)*270))
        sheet.save(E/f'XCHASE-{kind}-{page+1:02}.jpg',quality=94)
j=json.loads((E/'XCHASE-alpha-report.json').read_text(encoding='utf-8'));j.update(finalPerFrameChecks=checks,revision='R3.2_canonical_final_source_grey_pavement_removed',finalCanonicalEvidence='XCHASE-red/checker-01/02.jpg and XCHASE-red-F02/04/06/07/08/10/12/22/23/27.png',limitations='手绘发尖/暗蓝衣缘有局部1–8px近似；D姿态左后手原生出左画边，腰/前拳底部原生裁切，alpha明确截到y1008避原字幕；应贴底或由版式压住截断。',pipelineOrder=['prepare-chase.py','build-chase.py','refine-chase.py --all','clean-chase-head.py','qa-chase.py','actual view','final acceptance note'])
(E/'XCHASE-alpha-report.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8');print('26 final RGB equality and alpha band checks passed; fresh canonical views')
