from pathlib import Path
import sys,json
sys.path.insert(0,'work/jjk-edge-v17-v2/dynalpha');from build import *
entries=[]
for id,shot,first,last,method in [('Y-geto','C03',12,48,'3个人工可见轮廓锚点、受限LK、5px窄带GrabCut'),('Y-hurt','C20',12,60,'3个人工139点侧发轮廓锚点、受限LK、5px窄带GrabCut'),('Y-blue','C29',12,23,'12/18/20/22人工74点手轮廓锚点、受限LK、6px窄带GrabCut，受限亮肤色分离、孔洞填充；保留大于3000像素明亮指体连通块'),('Y-getopalm','C32',38,51,'38/43/50人工近手轮廓限制区、源肤色分离、3px闭运算及封闭线孔填充、保留手主体最大连通块'),('Y-stand','C21',12,36,'12/23/35人工全身轮廓锚点、受限LK、3px窄带GrabCut')]:
 frames=load(shot);rgbok=True;barsok=True;counts=[]
 for f in range(first,last):
  rgba=cv2.imread(str(OUT/id/f'{f:06}.png'),cv2.IMREAD_UNCHANGED);assert rgba is not None
  rgbok &= np.array_equal(rgba[:,:,:3],frames[f]);barsok &= (int(rgba[:108,:,3].max())==0 and int(rgba[972:,:,3].max())==0);counts.append(int((rgba[:,:,3]>127).sum()))
 assert rgbok and barsok
 p=EV/f'{id}-report.json';rep=json.loads(p.read_text(encoding='utf8'));rep['method']=method;rep['verifiedOnDisk']={'RGB逐帧与prepared同号源完全一致':bool(rgbok),'上下黑边alpha全零':bool(barsok),'nonemptyFrames':len(counts),'minOpaquePixels':min(counts),'maxOpaquePixels':max(counts)};rep['visualQA']='全部输出帧的棋盘格及红底联系图已查看；Y-stand另按人物放大查看24帧。不是100%发丝级分离。';p.write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf8')
 entries.append(dict(id=id,sourcePreparedShot=f'assets/shots/{shot}.mp4',alphaDirectory=f'assets/alpha/{id}',firstFileFrame=first,lastFileFrameExclusive=last,frameCount=last-first,fps=24,durationSeconds=(last-first)/24,filenamePattern='%06d.png',filenameIndex='与prepared素材fileF同号，不从0起；未输出范围外占位帧',method=method,verifiedExactRGB=bool(rgbok),verifiedBlackBarsTransparent=bool(barsok),report=f'evidence/alpha/{id}-report.json',limitations=rep['limitation']))
manifest=dict(format='v2-dynamic-alpha-real-source-v1',width=1920,height=1080,fps=24,rgb='解码prepared MP4的同号帧，PNG无损保存，不重绘、不生成RGB',alpha='8-bit straight alpha',entries=entries,totalPNG=sum(x['frameCount'] for x in entries),visualQANote='见各组checker/red-allframes，站姿另见zoom-checker/zoom-red。C29后段急退/失焦已缩短，C32无手开头未生成手。')
(EV/'动态抠像可用帧范围.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'count':manifest['totalPNG'],'groups':len(entries),'allExactRGB':True,'barsZero':True},ensure_ascii=False))
