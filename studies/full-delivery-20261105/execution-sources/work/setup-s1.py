from pathlib import Path
import json,secrets,datetime
base=Path(__file__).resolve().parents[1];out=base/'outputs/jjk-s1-workflow'
for d in ['data','docs','reviews','scripts','evidence','workflow','hyperframes','openchatcut','renders','music']:(out/d).mkdir(parents=True,exist_ok=True)
p=out/'data/随机参考抽选.json'
if not p.exists():
    p.write_text(json.dumps({'referenceId':f'V{secrets.randbelow(20)+1:02}','method':'Python secrets.randbelow(20)+1；V01–V20等概率；本次新片只抽一次','time':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'status':'selected','techniquePool':'全部20条参考的18类技法，主参考优先，其他按适配组合','durationOverride':'本次用户明确一分钟，优先于整首默认'},ensure_ascii=False,indent=2),encoding='utf-8')
print(p.read_text(encoding='utf-8'))
