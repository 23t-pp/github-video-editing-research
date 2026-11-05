import subprocess,json,pathlib,time
p=pathlib.Path('work/editable_templates'); gh=r'C:\Program Files\GitHub CLI\gh.exe'
queries=['remotion template video','remotion slideshow','hyperframes template','ffmpeg beat montage template','shotstack template','剪映 草稿 模板','capcut template json','moviepy video template']
out=[]; candidates={}
for i,q in enumerate(queries):
 r=subprocess.run([gh,'api','--method','GET','search/repositories','-f','q='+q,'-f','per_page=30'],capture_output=True,text=True,encoding='utf-8')
 file=p/f'search_{i+1:02}.json';file.write_text(r.stdout or r.stderr,encoding='utf-8')
 try:
  d=json.loads(r.stdout);items=d.get('items',[])
  out.append(dict(query=q,count=len(items),total_count=d.get('total_count'),raw_file=str(file)))
  for x in items:candidates[x['full_name']]=x
  print(q,d.get('total_count'),[(x['full_name'],x['stargazers_count']) for x in items[:15]])
 except:print(q,r.stderr)
(p/'searches.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(p/'candidates.json').write_text(json.dumps(list(candidates.values()),ensure_ascii=False,indent=2),encoding='utf-8')
