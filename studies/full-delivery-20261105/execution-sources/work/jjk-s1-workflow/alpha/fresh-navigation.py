from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3]/'outputs/jjk-s1-workflow';W=R/'evidence/source-overviews/fresh-candidates';W.mkdir(parents=True,exist_ok=True)
C=json.loads((R/'data/shot-candidates.json').read_text(encoding='utf-8'))['items'];by={x['id']:x for x in C};plan=json.loads((R/'data/edit-plan.json').read_text(encoding='utf-8'));used={x.get('candidateId') for x in plan['shots']}
ids=[28,35,36,41,45,76,78,80,81,88,89];items=[];font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
for page in range(2):
    subset=ids[page*6:(page+1)*6];sheet=Image.new('RGB',(1920,len(subset)*175+40),'#111620');d=ImageDraw.Draw(sheet);d.text((10,4),'第一季新增候选｜60Hz JPG库8时位导航（非插值）',font=font,fill='#72c7ed')
    for row,n in enumerate(subset):
        id=f'S1C{n:03}';c=by[id];t=c['anchorSeconds'];times=[t-.6+i*(1.2/7) for i in range(8)];y=40+row*175;d.text((8,y),f'{id} E{c["episode"]:02} {t}s · {"/".join(c["characters"])} · {c["visibleActionOrPose"]}',font=small,fill='white');samples=[]
        for k,target in enumerate(times):
            f=round(target*60);p=R/'素材集_60Hz_JPG'/c['sourceId']/f'minute-{f//3600:03}'/f'F{f:07}.jpg';assert p.exists(),p
            im=Image.open(p).convert('RGB').resize((240,135));sheet.paste(im,(k*240,y+27));d.text((k*240+5,y+153),f'{f/60:.3f}s',font=small,fill='white');samples.append({'grid60Frame':f,'targetSeconds':f/60,'jpg':p.relative_to(R).as_posix()})
        items.append({'candidateId':id,'sourceId':c['sourceId'],'sourcePath':c['sourcePath'],'characters':c['characters'],'anchorSeconds':t,'initialWindowSeconds':[t-.6,t+.6],'previouslyUsedInFrozenBMain':id in used,'evidence':f'evidence/source-overviews/fresh-candidates/fresh-{page+1:02}.jpg','row':row,'gridSamples':samples,'humanReviewed':False,'observedMovement':'pending view','coreSourceSeconds':None})
    sheet.save(W/f'fresh-{page+1:02}.jpg',quality=94)
(R/'data/fresh-shot-candidates.json').write_text(json.dumps({'scope':'root批准L2素材扩展；由已完成60Hz JPG库取8时位图，不改冻结source-inventory/原候选索引','count':len(items),'items':items},ensure_ascii=False,indent=2),encoding='utf-8');print(len(items),'fresh candidates navigation')
