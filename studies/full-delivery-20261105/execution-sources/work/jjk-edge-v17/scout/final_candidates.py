from scout import *
import numpy as np
base=Path('D:/咒术回战/4K 内嵌简中字幕')
# Explicit short windows; all source clocks are seconds from each file start.
rows=[
(1,954,2,'五条镜片正脸','静→轻低头','蓝眼与圆镜片'),(1,962.25,1,'双人伸展','两侧展开','双人肩线'),(2,328,2,'夏油笑脸','微抬头','夏油眼线'),(2,391,2,'俯拍室内双人','五条向左展臂','夏油前景五条后景'),(2,509,1.75,'搭肩双人','五条向右低头','两人面部'),(2,1169.75,1.25,'五条举臂敌人出拳','左向右拳','五条脸与右上举臂'),(2,1220,2,'五条举圆镜片','镜片左上→中央','镜片与蓝眼'),(2,1259,1.5,'伸掌破窗起手','掌朝镜头','前景掌心'),(2,1287,2,'红色术式球','上右→下中','红球与五条'),(4,989,2,'五条金色悬空','仰躺/双臂展开','中央全身'),
(1,895,1.5,'篮球双人擦肩','左向右','前后双人'),(1,920,1.5,'五条篮球场笑脸','略向右','圆镜片笑脸'),(1,935,1.5,'夏油篮球场皱眉','正面','夏油面部'),(1,1290,1.5,'五条无下限刀片','静/刀片悬空','五条蓝眼'),(2,495,1.5,'夏油闭眼笑','静','耳钉与笑脸'),(3,444,1.5,'海边双人','五条抬臂','两人肩线'),(3,454,1.5,'海边夏油微笑','微低头','夏油脸'),(3,1170,1.5,'树荫双人交谈','五条握拳','两人眼线'),(3,1175,1.5,'树荫夏油微笑','面向左','夏油脸'),(4,1340,1.5,'受伤五条冷色正脸','静','蓝眼伤痕'),(4,1280,1.5,'红色夕阳五条独行','左→右下','长影与人物'),(4,1300,1.5,'红色室内夏油','向前/背身','夏油背影'),(5,978,1.5,'人群中夏油正脸','向前','夏油脸'),(5,1030,1.5,'人群中夏油反问','静/微抬头','夏油孤立正脸'),(5,1080,1.5,'台阶五条镜片脸','向上看','眼睛镜片'),
(3,689,1.5,'五条前伸掌','向镜头','掌心与笑脸'),(3,820,.8,'苍碎墙蓝色宽景','前向后','蓝光与双人'),(3,879,1.3,'苍球反手凝聚','右上→左下','球体与手'),(3,889,1.5,'苍前伸掌','向镜头','前景手掌'),(3,920,1.5,'五条被虫群包围','左转身','五条白发'),(3,930,1.5,'五条平掌停顿','向镜头','掌心'),(4,209,1.5,'夏油前伸掌','向镜头','手与脸'),(4,329,1.5,'夏油浮空黑球','上向下','三球与人物'),(4,359,1.5,'伏黑甚尔横斩','右→左','手臂刀刃'),(4,420,1.5,'蓝色骨手术式','环绕','蓝手与亮刀'),(4,429,1.5,'夏油横向伸臂','右→左','长袖与脸'),(4,449,1.5,'夏油持咒灵起手','向上','前景手'),(4,787,2,'受伤五条抬脸','由下向上','伤痕蓝眼'),(4,810,1.5,'五条近身袭击','右→左','五条与对手'),(4,820,1.5,'红色掌上咒力','指尖向下','红光与手'),(4,839,1,'六眼极近','瞳孔放大','蓝色眼瞳'),(4,859,1.5,'五条仰头大笑','向上展开','脸和双臂'),(4,870,1,'对手被击飞','左→右','横向飞行身体'),(4,879,1.2,'红色反击对手','上左→下右','红刃与面部'),(4,975,1.5,'刀刃映六眼','纵向刀与静眼','蓝眼与刀刃'),(4,994,1.5,'五条蓝眼极近','静/推近','蓝瞳'),(4,1014,1.5,'觉醒五条抬臂','右上划弧','脸与抬手'),(4,1029,1.5,'五条破墙漂移','左→右','白发与碎块'),(4,1049,1.5,'碎块中五条伸臂','右→左展臂','背身与手'),(4,1059,1.2,'红蓝咒力融合','环绕收聚','能量球'),(4,1064,1.5,'虚式茈起手','掌朝镜头','手与紫光'),(4,1070,1.5,'紫光击出','向纵深','紫束'),(4,1074,1,'对手紫光照脸','正面冲击','眼睛'),(4,1330,1.5,'礼堂冷色距离','深度推进','五条与夏油远近')]
def clip(job):
 k,row=job;ep,t,d,action,direction,focus=row;p=base/f'{ep:02}.mp4'
 cmd=[FF,'-v','error','-ss',str(t),'-i',str(p),'-t',str(d),'-vf','fps=8,scale=384:216','-f','rawvideo','-pix_fmt','rgb24','pipe:1']
 r=subprocess.run(cmd,capture_output=True);r.check_returncode();n=len(r.stdout)//(384*216*3);a=np.frombuffer(r.stdout,dtype=np.uint8)[:n*384*216*3].reshape(n,216,384,3)
 if n<2:raise RuntimeError(str(row))
 inds=sorted(set([0,n//3,n*2//3,n-1]));ims=[Image.fromarray(a[x]) for x in inds]
 target=OUT/f'C{k:02}-e{ep:02}-{t:.3f}.jpg';ims[len(ims)//2].save(target,quality=90)
 diffs=np.abs(a[1:].astype(float)-a[:-1].astype(float)).mean((1,2,3)).tolist()
 return {'id':f'C{k:02}','path':str(p),'episode':ep,'sourceIn':t,'usableDuration':d,'action':action,'direction':direction,'focus':focus,'evidenceFrame':str(target),'sampleCount':n,'sampleFps':8,'diffMax':max(diffs)},ims
if __name__=='__main__':
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for k,(data,ims) in enumerate(pool.map(clip,enumerate(rows,1))):
   results.append((data,ims));print(data['id'],data['diffMax'],flush=True)
 for pg in range((len(results)+7)//8):
  chunk=results[pg*8:(pg+1)*8];canvas=Image.new('RGB',(1536,len(chunk)*242),(15,15,15));dr=ImageDraw.Draw(canvas)
  for row,(data,ims) in enumerate(chunk):
   for col,im in enumerate(ims):canvas.paste(im,(col*384,row*242))
   dr.text((5,row*242+217),f"{data['id']} e{data['episode']:02} {data['sourceIn']}s  duration={data['usableDuration']}s   8fps",font=font,fill='white')
  canvas.save(OUT/f'candidates-{pg+1:02}.jpg',quality=88)
 obj={'scope':'8fps decode of selected short windows; 4 representative frames per row; candidate visual QA pending','sources':json.loads((OUT/'s2-probes.json').read_text(encoding='utf-8')),'recommendedCrop':{'sourceResolution':[3840,2160],'crop':[3840,1600,0,280],'equivalent1920':[1920,800,0,140],'note':'中心宽银幕裁切去除底部烧录字幕；个别上举手/全身需另外平移与缩小，以最终画面验收'},'shots':[x[0] for x in results]}
 (ROOT/'work/jjk-edge-v17/scout-source.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
