from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parents[2];HF=ROOT/'outputs/reference-replay-next/hyperframes'
plan=json.loads((HF/'edit.json').read_text(encoding='utf-8'))
replacement=json.loads((ROOT/'work/reference-replay-v07/P17-replacement.json').read_text(encoding='utf-8'))
for a in plan['assets']:
    if a['id']=='P17':a.update(asset='assets/shots/P17-replacement.mp4',film='02',sourceIn=replacement['sourceIn'],label='黄色与紫色跑车并行疾驰')
for s in plan['shots']:
    if s['assetId']=='P17':s.update(asset='assets/shots/P17-replacement.mp4',film='02',sourceIn=replacement['sourceIn'],label='黄色与紫色跑车并行疾驰')
assert sum(s['frames'] for s in plan['shots'])==750
for i,s in enumerate(plan['shots']):assert s['startFrame']==sum(p['frames'] for p in plan['shots'][:i])
(HF/'edit.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(ROOT/'work/reference-replay-v07/P17-replacement.json',HF/'assets/shots/P17-replacement.json')
shutil.copy2(ROOT/'work/reference-replay-v07/base-qc-repairs.json',HF/'assets/shots/base-qc-repairs.json')
print('Final 32 cuts locked, P15 clean + P16 early offset + P17 clear lateral cars.')
