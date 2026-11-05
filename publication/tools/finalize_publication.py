from pathlib import Path
import json,hashlib,shutil,zipfile,zlib
R=Path.cwd().resolve();S=R/'work/publish-all-20261105/projects';A=S/'assets';M=S/'manifests';D=S/'docs';T=S/'text-staging'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assets=json.loads((S/'assets-manifest.json').read_text(encoding='utf-8'));mirror=json.loads((M/'text-mirror-manifest.json').read_text(encoding='utf-8'))
(D/'发布过程说明.md').write_text('''# 发布过程与最终判据

本批工作只在 `work/publish-all-20261105/projects` 创建归档、工具和新文档，未改冻结 outputs；`outputs/github-video-editing-research` 由主任务单独维护。

最终核验重新读取范围内全部 5,579 个 outputs 原文件，与 complete 包、supplement 包和独立 HF/OCC 资产的逐文件 bytes/SHA256 对照，缺失 0、摘要差异 0、相互冲突清单 0。全部 archive entries 都在写包时读取源摘要，并在封口后真实解压流读取核 bytes/SHA256/CRC32。

初始 staging 曾发生 S1 测试fixture的同名HF ZIP匹配过宽。问题在 S1 ready 标记前发现，已只拆出项目根级正式HF 172,690,102字节，fixture原字节留在完整包。最终S1资产/还原映射以正式清单为准，初轮packaging.log保留为执行诊断，不能据其早期临时记录判断最终发布资产。

初始按key/profile/token名称规则误排非秘密文件。经内容实检及独立审核，169个唯一文件（原236排除条目含重复）全部补入 `publication-supplement.zip`，保持原路径；exclusions对应标记已改为supplemented。已有verified资产不重建，恢复工具自动合并补包。

OpenChatCut app源目录的.git为无提交初始化，故版本来源如实记作upstream_HEAD:null，不把本机工作树伪称为任一上游提交。以当前ZIP摘要、2,805源文件的逐条摘要固定快照；保留上游LICENSE。局部调研快照另有commit.json的固定SHA、来源URL及已下载的全部LICENSE/NOTICE。

恢复工具已对真实S1完整包、正式HF/OCC及137个S1补包文件执行2356文件实测恢复和逐源SHA复核，二次运行2356文件均同SHA跳过；并测试越界路径拒绝、ZIP符号链接拒绝、缺独立资产预检和不同内容不覆盖。测试暴露的Windows长路径限制已通过扩展路径处理修正。恢复测试工作区不是发布材料。

JPG实物另由专职归档任务交付，本批不以工程归档完成代替JPG全集发布完成。`text-staging`仅是可浏览源码镜像，统一放在 `studies/full-delivery-20261105`，原有studies不会被覆盖。原媒体版权与上游软件许可继续按各项目及其来源约定。
''',encoding='utf-8')
# Final scripts, instructions, and compact verification reports for Git browsing.
files=[S/n for n in ('restore_projects.py','test_restore_projects.py','package_projects.py','finalize_s1.py','finalize_execution.py','package_app.py','package_supplement.py','signal_ready.py','outputs-coverage-verification.json','restore-tests.json','exclusions.json','inventory.json')]+list(D.glob('*'))
for p in files:
 if not p.is_file():continue
 dest=T/'studies/full-delivery-20261105/release-guides'/p.relative_to(S);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);h=sha(p);assert sha(dest)==h
 mirror.append({'path':dest.relative_to(T).as_posix(),'source':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':h})
dump(M/'text-mirror-manifest.json',mirror)
summary={'status':'PASS','scope':'22个实物资产（不计本说明工具/文本指南/最终证据ZIP），JPG由独立任务交付','material_assets':len(assets),'material_asset_bytes':sum(a['bytes'] for a in assets),'outputs_sources_verified':5579,'outputs_sources_missing':0,'outputs_sources_sha_mismatch':0,'text_mirror_files':len(mirror),'text_mirror_bytes':sum(e['bytes'] for e in mirror),'all_assets_below_2GiB':all(a['bytes']<2**31 for a in assets),'source_outputs_modified':False,'restore_actual_s1_files':2356,'restore_same_sha_rerun':2356,'restore_tests':'PASS','supplemented_nonsecret_unique_files':169,'validation':'原源逐文件bytes/SHA256，归档entry解压SHA256/bytes/CRC32，独立ZIP原副本SHA及内部CRC，镜像源副本SHA；另有独立审计'}
dump(S/'validation-summary.json',summary)
# Loose assets let a beginner run restore without unpacking another archive first.
for p,name in [(S/'restore_projects.py','restore_projects.py'),(D/'download-and-restore.zh-CN.md','download-and-restore.zh-CN.md')]:
 out=A/name;shutil.copyfile(p,out);assert sha(p)==sha(out)
 assets.append({'asset':name,'source':p.relative_to(R).as_posix(),'bytes':out.stat().st_size,'sha256':sha(out),'validation':'PASS: 源与发布副本bytes/SHA256一致'})
dump(S/'assets-manifest.json',assets);dump(D/'published-assets-before-tools.json',assets)
# Freeze metadata inputs before zipping; the live asset manifest will gain this ZIP afterward.
items=[(p,p.relative_to(S).as_posix()) for p in files if p.is_file()]
items.extend((p,p.relative_to(S).as_posix()) for p in M.glob('*.json'))
items.extend((S/n,n) for n in ('validation-summary.json','packaging.log','finalize-s1.log','finalize-execution.log','package-app.log','package-supplement.log','restore-tests.log'))
items.append((D/'published-assets-before-tools.json','assets-manifest.json'))
# De-duplicate archive names, never overwrite a previous verified asset.
unique={arc:p for p,arc in items};name='project-release-tools-and-manifests.zip';out=A/name;records=[]
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
 for arc,p in unique.items():
  h=hashlib.sha256();crc=0;n=0
  with p.open('rb') as src,z.open(arc,'w',force_zip64=True) as dst:
   while b:=src.read(4*1024*1024):dst.write(b);h.update(b);crc=zlib.crc32(b,crc);n+=len(b)
  records.append({'path':arc,'source':p.relative_to(R).as_posix(),'bytes':n,'sha256':h.hexdigest(),'crc32':f'{crc&0xffffffff:08x}'})
with zipfile.ZipFile(out) as z:
 for e in records:
  h=hashlib.sha256();crc=0;n=0
  with z.open(e['path']) as f:
   while b:=f.read(4*1024*1024):h.update(b);crc=zlib.crc32(b,crc);n+=len(b)
  assert (n,h.hexdigest(),f'{crc&0xffffffff:08x}')==(e['bytes'],e['sha256'],e['crc32'])
  assert z.getinfo(e['path']).CRC==crc&0xffffffff
asset={'asset':name,'source_file_count':len(records),'bytes':out.stat().st_size,'sha256':sha(out),'validation':'PASS: 每entry bytes/SHA256/CRC32 与封存元数据源逐字节核验','entries_manifest':'manifests/'+name+'.json'}
dump(M/(name+'.json'),{'asset':asset,'files':records});assets.append(asset);dump(S/'assets-manifest.json',assets)
for a in assets:
 dest=S/'ready'/(a['asset']+'.json')
 if dest.exists():continue
 v={'state':'verified','path':str(A/a['asset']),'name':a['asset'],'bytes':a['bytes'],'sha256':a['sha256'],'release':'projects'};tmp=dest.with_suffix('.tmp');dump(tmp,v);tmp.replace(dest)
dump(S/'final-delivery-summary.json',{'state':'COMPLETE','assets':len(assets),'bytes':sum(a['bytes'] for a in assets),'ready_markers':len(list((S/'ready').glob('*.json'))),'text_mirror_files':len(mirror),'text_mirror_bytes':sum(e['bytes'] for e in mirror),'namespace':'studies/full-delivery-20261105','outputs_source_coverage':'5579/5579 bytes/SHA PASS','restore_smoke':'2356 files PASS + rerun same2356','metadata_asset':asset})
print(json.dumps(json.loads((S/'final-delivery-summary.json').read_text()),ensure_ascii=False,indent=2))
