from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3]/'outputs/jjk-s1-workflow';E=R/'evidence/source-overviews/fresh-candidates';by={x['id']:x for x in json.loads((R/'data/shot-candidates.json').read_text(encoding='utf-8'))['items']};used={x.get('candidateId') for x in json.loads((R/'data/edit-plan.json').read_text(encoding='utf-8'))['shots']}
spec=[(18,429.5,430.7),(35,118.55,119.65),(41,179.4,180.6),(47,444.5,445.7),(54,924.5,925.7),(66,1109.4,1110.6),(69,1159.4,1160.6),(76,1214.25,1215.45),(80,265.15,266.35),(81,289.4,290.6),(85,405.0,406.2),(88,449.4,450.6)];font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16);items=[]
for page in range(2):
    subset=spec[page*6:(page+1)*6];sheet=Image.new('RGB',(1920,len(subset)*175+40),'#111620');d=ImageDraw.Draw(sheet);d.text((10,4),'L2新增未用候选｜各核心窗8时位（60Hz源帧采样，非插值）',font=font,fill='#72c7ed')
    for row,(n,start,end) in enumerate(subset):
        id=f'S1C{n:03}';c=by[id];assert id not in used,id;y=40+row*175;d.text((8,y),f'{id} E{c["episode"]:02} {start:.3f}–{end:.3f}s · {c["visibleActionOrPose"]}',font=small,fill='white');samples=[]
        for k in range(8):
            f=round((start+(end-start)*k/7)*60);p=R/'素材集_60Hz_JPG'/c['sourceId']/f'minute-{f//3600:03}'/f'F{f:07}.jpg';assert p.exists();im=Image.open(p).convert('RGB').resize((240,135));sheet.paste(im,(k*240,y+27));d.text((k*240+5,y+153),f'{f/60:.3f}s',font=small,fill='white');samples.append({'grid60Frame':f,'targetSeconds':f/60,'jpg':p.relative_to(R).as_posix()})
        items.append({'candidateId':id,'sourceId':c['sourceId'],'sourcePath':c['sourcePath'],'characters':c['characters'],'anchorSeconds':c['anchorSeconds'],'coreSourceSeconds':[start,end],'previouslyUsedInFrozenBMain':False,'evidence':f'evidence/source-overviews/fresh-candidates/fresh-core-{page+1:02}.jpg','row':row,'gridSamples':samples,'humanReviewed':False,'observedMovement':'pending final view','nativeExactCutVerification':'requires per-source-frame confirmation by execution agent'})
    sheet.save(E/f'fresh-core-{page+1:02}.jpg',quality=94)
(R/'data/fresh-shot-candidates.json').write_text(json.dumps({'version':'FRESH-L2-0.2','scope':'12个B主线未用候选，60Hz JPG库核心窗8点预检；不改冻结索引','count':len(items),'items':items},ensure_ascii=False,indent=2),encoding='utf-8');print('12 core windows for final view')
