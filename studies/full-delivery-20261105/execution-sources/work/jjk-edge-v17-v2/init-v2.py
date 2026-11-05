from pathlib import Path
import shutil,json,hashlib
BASE=Path(__file__).resolve().parents[2]
OLD=BASE/'outputs/jjk-edge-v17';NEW=BASE/'outputs/jjk-edge-v17-v2'
NEW.mkdir(parents=True,exist_ok=True)
ignore=shutil.ignore_patterns('.hyperframes','.thumbnails','.waveform-cache','.render-cache','__pycache__','.source-backups')
shutil.copytree(OLD/'hyperframes',NEW/'hyperframes',dirs_exist_ok=True,ignore=ignore)
for name in ['制作约定.json','封面.jpg']:
    shutil.copy2(OLD/name,NEW/name)
(NEW/'evidence').mkdir(exist_ok=True)
plan=json.loads((NEW/'hyperframes/edit.json').read_text(encoding='utf-8'))
plan['title']='挚友 · EDGE · V2 精修';plan['revision']='V2'
(NEW/'hyperframes/edit.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
baseline={'file':'../jjk-edge-v17/挚友_EDGE_一分钟.mp4','sha256':hashlib.sha256((OLD/'挚友_EDGE_一分钟.mp4').read_bytes()).hexdigest(),'durationSeconds':60,'frames':1440,'request':'增加全片动态抠像和排版覆盖，V17主技法更高复刻，V02文字更精细；沿用既有BGM选段和一分钟。','audioSha256':hashlib.sha256((NEW/'hyperframes/assets/audio/master.wav').read_bytes()).hexdigest()}
(NEW/'evidence/V1基线与精修目标.json').write_text(json.dumps(baseline,ensure_ascii=False,indent=2),encoding='utf-8')
design=NEW/'hyperframes/DESIGN.md'
design.write_text(design.read_text(encoding='utf-8')+'\n\n## V2精修\n\n新增冷脸动态前景跨暖景、参考尺度的细撕条、矩形窗扩成全幅、竖缝到双眼；中后段用人物前后景、动作裁片与景深版式延伸。V02主字使用窄高英文字形，中文作辅助语义；曲面切片、挤出和遮挡须实际渲染验收。实际覆盖秒数按有效区间并集统计，不把重复图层数当成技法数量。\n',encoding='utf-8')
print('V2 independent source project copied; V1 retained')
