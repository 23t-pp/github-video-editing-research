from scout import *
base=Path('D:/咒术回战/4K 内嵌简中字幕')
jobs=[(1,954,2),(1,962,2),(2,328,2),(2,391,2),(2,509,2),(2,1169,2),(2,1220,2),(2,1259,2),(2,1287,2),(4,989,2)]
for k,(ep,t,d) in enumerate(jobs):
 print(sheet(base/f'{ep:02}.mp4',[t+x*.25 for x in range(9)],f'first{k+1:02}-e{ep:02}-{t}'),flush=True)
