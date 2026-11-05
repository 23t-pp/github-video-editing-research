from scout import *
base=Path('D:/咒术回战/4K 内嵌简中字幕')
info=[]
for i in range(1,6):
 p=base/f'{i:02}.mp4';pr=probe(p);v=next(s for s in pr['streams'] if s['codec_type']=='video');dur=float(pr['format']['duration'])
 print(i,dur,flush=True);info.append({'id':f's2e{i:02}','path':str(p),'duration':dur,'video':v})
 print(sheet(p,list(range(30,1381,60)),f's2e{i:02}-coarse'),flush=True)
(OUT/'s2-probes.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
