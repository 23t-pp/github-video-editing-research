from final_candidates import *
changes={8:(1259.5,1.75),9:(1289,1),11:(895.5,1),15:(495,.5),19:(1175,.625),20:(1338,2.25),22:(1300.5,1),24:(1030,1),29:(889.75,1.5),30:(920,1),35:(420.5,1),36:(429.5,1),37:(449.75,1),38:(790,3),41:(839.5,.5)}
excluded={27:'short interval crossed source edit',34:'multiple source angles inside short attack',44:'multiple source angles inside short attack'}
if __name__=='__main__':
 jobs=[]
 for k,row in enumerate(rows,1):
  if k in excluded:continue
  row=list(row)
  if k in changes:row[1],row[2]=changes[k]
  if k==9:row[3]='红色术式球与五条俯拍'
  if k==35:row[3:]=['甚尔打碎蓝色术式空间','向右上跃出','白底人体与碎块']
  if k==38:row[3:]=['受伤五条抬脸','低头→抬眼→微笑','伤痕与蓝眼']
  jobs.append((k,row))
 jobs.append((55,[2,1261.5,1.75,'玻璃破碎中伸掌','掌向镜头','前景掌心与五条脸']))
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for data,ims in pool.map(clip,jobs):
   data['inspection']='8fps short window decoded; representative frames viewed in contact sheets'
   data['crop']='3840:1600:0:280 (center); reframe upward for raised hands/full-body'
   data['priority']='A' if data['id'] in ['C01','C03','C05','C07','C08','C10','C16','C18','C20','C21','C29','C31','C32','C36','C38','C45','C46','C47','C51','C55'] else 'B'
   results.append((data,ims));print(data['id'],flush=True)
 for pg in range((len(results)+7)//8):
  chunk=results[pg*8:(pg+1)*8];canvas=Image.new('RGB',(1536,len(chunk)*242),(15,15,15));dr=ImageDraw.Draw(canvas)
  for row,(data,ims) in enumerate(chunk):
   for col,im in enumerate(ims):canvas.paste(im,(col*384,row*242))
   dr.text((5,row*242+217),f"{data['id']} e{data['episode']:02} {data['sourceIn']}s  duration={data['usableDuration']}s",font=font,fill='white')
  canvas.save(OUT/f'final-{pg+1:02}.jpg',quality=88)
 obj={'scope':'52 short source windows, at 8fps for selected spans only; four representative frames per shot visually reviewed. Not a complete episode or native-frame QA; no audio audition by source scout.','sources':json.loads((OUT/'s2-probes.json').read_text(encoding='utf-8')),'recommendedCrop':{'sourceResolution':[3840,2160],'crop':[3840,1600,0,280],'equivalent1920':[1920,800,0,140],'note':'中心宽银幕裁切去除底部烧录字幕；个别上举手/全身需另外平移与缩小，以最终画面验收'},'excludedOriginalCandidates':excluded,'shots':[x[0] for x in results]}
 (ROOT/'work/jjk-edge-v17/scout-source.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
