from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,hashlib,io,sys
from PIL import Image,ImageDraw
BASE=Path(__file__).resolve().parents[2];WORK=Path(__file__).resolve().parent
HF=BASE/'outputs/jjk-edge-v17-v3-dedup/hyperframes';EV=HF.parent/'evidence';FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe'
ROWS=[
('N01',3,740,'五条正面冷静回应'),('N02',1,1040,'双人走廊电话错位'),('N03',4,190,'夏油立于礼堂走廊'),('N04',4,365,'夏油与走廊刀群'),('N05',3,815,'甚尔低身急行'),('N06',4,445,'夏油咒灵球掌心'),('N07',3,875,'苍术式蓝色能量流'),('N08',3,950,'甚尔长刃横扫'),('N09',3,830,'甚尔踏碎瓦檐'),('N10',4,815,'五条血手按地'),('N11',4,880,'甚尔红光挥斩'),('N12',3,860,'五条回身背影'),('N13',4,410,'刀刃与绷带手'),('N14',4,1055,'金色空间飞鸟'),('N15',4,935,'锁链红色冲刺'),('N16',4,1002,'花瓣与觉醒感知'),('N17',2,1248,'空中出腿与追击'),('N18',2,1275,'五条侧移闪避'),('N19',3,900,'广场烟尘掠过'),('N20',4,490,'甚尔立于破碎空间'),('N21',5,865,'五条镜片后的惊愕'),
('N22',3,420,'圆镜与蓝眼另一构图'),('N23',4,980,'额前白发与双眼'),('N24',4,350,'咒灵缠绕的长廊'),('N25',3,800,'甚尔持刃展开双臂'),('N26',4,475,'建筑碎块与冲击'),('N27',1,972,'篮球场双人错身'),('N28',2,425,'双人窗边对话'),('N29',3,430,'海边双人近景'),('N30',2,520,'室内双人肩线'),
('N31',5,265,'雨中夏油近脸'),('N32',1,940,'夏油篮球场凝视'),('N33',4,865,'血色五条安静正脸'),('N34',3,1185,'礼堂夏油闭眼笑'),('N35',1,1220,'夏油接电话侧身'),('N36',5,385,'白衣夏油抱臂'),('N37',5,565,'夏油低头抬眼'),('N38',4,825,'血色五条抬手正面'),('N39',5,1050,'指尖展开手势'),('N40',1,948,'五条侧脸与圆镜'),
]
def task(row):
 id,ep,t,desc=row;src=Path('D:/咒术回战/4K 内嵌简中字幕')/f'{ep:02}.mp4';out=HF/'assets/shots'/f'{id}.mp4'
 if not out.exists():
  vf='scale=1920:1080:flags=lanczos,crop=1920:864:0:48,pad=1920:1080:0:108:black,fps=24,setpts=PTS-STARTPTS,setsar=1'
  cmd=[FF,'-v','error','-threads','1','-filter_threads','1','-ss',str(t-.5),'-i',str(src),'-an','-vf',vf,'-frames:v','84','-c:v','libx264','-threads','2','-preset','fast','-crf','17','-bf','0','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-f','mp4','-movflags','frag_keyframe+empty_moov+default_base_moof','pipe:1']
  with out.open('wb') as f:subprocess.run(cmd,stdout=f,check=True)
 # Contact sheets from newly prepared media, not guessed timestamps.
 vf="select='eq(n,12)+eq(n,24)+eq(n,47)+eq(n,59)',scale=384:216"
 r=subprocess.run([FF,'-v','error','-threads','1','-filter_threads','1','-i',str(out),'-vf',vf,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],capture_output=True,check=True)
 n=len(r.stdout)//(384*216*3);assert n==4,(id,n)
 ims=[Image.frombytes('RGB',(384,216),r.stdout[i*384*216*3:(i+1)*384*216*3]) for i in range(n)]
 return dict(id=id,asset='assets/shots/'+id+'.mp4',frames=84,usableFrames=60,sourcePath=str(src),sourceIn=t,preparedSourceStart=t-.5,sourceFps='24000/1001',description=desc,sha256=hashlib.sha256(out.read_bytes()).hexdigest()),ims
if __name__=='__main__':
 results=[]
 with ThreadPoolExecutor(max_workers=2) as ex:
  for data,ims in ex.map(task,ROWS):results.append((data,ims));print('PREPARED',data['id'],flush=True)
 for page,k in enumerate(range(0,len(results),8),1):
  batch=results[k:k+8];can=Image.new('RGB',(1536,len(batch)*242),(12,14,20));d=ImageDraw.Draw(can)
  for y,(a,ims) in enumerate(batch):
   for x,im in enumerate(ims):can.paste(im,(x*384,y*242))
   d.text((5,y*242+219),f"{a['id']} E{Path(a['sourcePath']).stem} {a['sourceIn']}s / prepared F12 F24 F47 F59",fill='white')
  can.save(EV/f'新素材四帧复查-{page:02}.jpg',quality=92)
 (WORK/'new-assets.json').write_text(json.dumps([a for a,i in results],ensure_ascii=False,indent=2),encoding='utf8')
 print('PREPARE COMPLETE',len(results),flush=True)
