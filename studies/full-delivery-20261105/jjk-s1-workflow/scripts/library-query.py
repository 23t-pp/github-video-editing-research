from pathlib import Path
import argparse,sqlite3,json
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description='按集数和秒数查60Hz JPG及真实源PTS，不用肉眼翻两百万文件');p.add_argument('--episode',type=int,required=True);p.add_argument('--time',type=float,required=True);a=p.parse_args()
folder=ROOT/'素材集_60Hz_JPG'/f'S1E{a.episode:02}';db=sqlite3.connect(folder/'index.sqlite');n=max(0,round(a.time*60));row=db.execute('SELECT s.sample,s.time_seconds,s.source_frame,s.duplicate,s.path,n.pts,n.pts_seconds,n.first_path FROM samples s JOIN native n ON s.source_frame=n.frame WHERE s.sample=?',(n,)).fetchone();assert row,'requested sample not materialized'
keys=['sample','sampleSeconds','nativeFrame','repeated','jpg','sourcePtsInteger','sourcePtsSeconds','firstAliasPath'];r=dict(zip(keys,row));r['absoluteJpg']=str(folder/r['jpg']);r['sourceVideo']=f'D:/咒术回战/1080P 内嵌简中字幕/{a.episode:02}.mp4'
catalog=ROOT/'data/material-catalog.json'
tags=json.loads((catalog if catalog.exists() else ROOT/'data/shot-candidates.json').read_text(encoding='utf-8'));near=[x for x in tags['items'] if x['episode']==a.episode and abs(x['anchorSeconds']-a.time)<=1]
r['humanCandidateLabelsNearOneSecond']=[{k:x.get(k) for k in ['id','characters','visibleActionOrPose','motionVerified','semanticConfidence','anchorJpg']} for x in near]
r['nativeVerifiedWindowsAtRequestedTime']=[x['tailActionEvidence'] for x in tags['items'] if x['episode']==a.episode and 'tailActionEvidence' in x and x['tailActionEvidence']['coreSourceSeconds'][0]<=a.time<x['tailActionEvidence']['coreSourceSeconds'][1]]
r['note']='附近静帧标签与窗口内证据分列；调度窗口优先用nativeVerifiedWindowsAtRequestedTime中的人物/动作，不继承旧静帧推断。没有证据时语义未知。高分取片回原视频。'
print(json.dumps(r,ensure_ascii=False,indent=2))
