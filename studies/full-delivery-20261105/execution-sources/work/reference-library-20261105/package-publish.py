from pathlib import Path
import shutil, zipfile, hashlib, json, re

workspace=Path.cwd()
outputs=workspace/'outputs'
library=outputs/'reference-library-20261105'
sample=outputs/'v05-six-panel'
repo=outputs/'github-video-editing-research'
release=outputs/'reference-library-release-20261105'
release.mkdir(exist_ok=True)
tag='reference-library-2026-11-05'
release_url=f'https://github.com/23t-pp/github-video-editing-research/releases/tag/{tag}'
download=f'https://github.com/23t-pp/github-video-editing-research/releases/download/{tag}/v05-six-panel.zip'

def allowed(p):
    return p.name not in {'local-media-paths.json','manifest.local.json'} and not p.name.startswith('.env') and not any(x in {'__pycache__','node_modules','.git'} for x in p.parts) and p.suffix not in {'.pyc','.log'}
library_files=[p for p in library.rglob('*') if p.is_file() and allowed(p.relative_to(library))]
with zipfile.ZipFile(release/'reference-library-20261105.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in library_files:z.write(p,'reference-library-20261105/'+p.relative_to(library).as_posix())

# The existing HyperFrames archive is the tested portable project: do not include generated frame caches.
sample_entries={}
for p in sample.iterdir():
    if p.is_file() and p.suffix in {'.md','.html','.mp4','.zip','.json'}:sample_entries[p.relative_to(sample).as_posix()]=p.read_bytes()
for d in ['openchatcut','evidence']:
    for p in (sample/d).rglob('*'):
        if p.is_file() and allowed(p.relative_to(sample)):sample_entries[p.relative_to(sample).as_posix()]=p.read_bytes()
with zipfile.ZipFile(sample/'HyperFrames可编辑工程.zip') as z:
    for n in z.namelist():
        if n.endswith('/'):continue
        # Existing archive paths start directly at the project root.
        parts=Path(n).parts
        if '..' in parts or Path(n).is_absolute():raise RuntimeError('Unexpected archive path')
        sample_entries[n if n.startswith('hyperframes/') else 'hyperframes/'+n]=z.read(n)
with zipfile.ZipFile(release/'v05-six-panel.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name,data in sample_entries.items():z.writestr('v05-six-panel/'+name,data)

study_dest=repo/'studies/reference-library-20261105'
for p in library_files:
    if p.suffix.lower() in {'.m4a','.wav','.mp3','.mp4','.zip'}:continue
    target=study_dest/p.relative_to(library);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
sample_dest=repo/'studies/v05-six-panel'
for name,data in sample_entries.items():
    if Path(name).suffix.lower() in {'.m4a','.wav','.mp3','.mp4','.zip','.ccproj'}:continue
    target=sample_dest/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)

# In GitHub source browsing, media links should lead to the complete tested download package.
readme=sample_dest/'README_中文学习指南.md'
text=readme.read_text(encoding='utf-8')
text=re.sub(r'\]\(([^)]+\.(?:mp4|zip|ccproj))\)',lambda m:']('+download+')',text,flags=re.I)
text=text.replace('## 先看什么，打开什么','## 先看什么，打开什么\n\n本页媒体链接下载完整 `v05-six-panel.zip`，解压后按表内文件名打开。工程源码与证据留在Git仓库；可播放媒体和内嵌素材工程位于Release附件。')
readme.write_text(text,encoding='utf-8')

root_readme=repo/'README.md'
old=root_readme.read_text(encoding='utf-8')
if old.startswith('# 混剪拆解、音乐库与可编辑工程：中文学习仓库'):
    old=old[old.index('# AI剪辑、卡点混剪与可复用模板：中文调研与学习手册'):]
old=old.replace('AI剪辑、导出及HyperFrames联动尚未实测。','后续已完成V05六格的HyperFrames真实渲染、OpenChatCut分层工程及官方工程包导入；其他AI剪辑能力仍按各专题的验证范围理解。')
head='''# 混剪拆解、音乐库与可编辑工程：中文学习仓库

**2026年11月5日更新：你提供的20条参考短片，已经按原生帧率拆解并整理为学习库。** 共17,290张原帧、299页图谱、205个学习段、18类技法；20条原始音轨与20条音乐主体候选已实际生成。低于60fps的片源没有补帧。

## 如果你没有基础，先打开这三个入口

1. **[中文学习总入口](studies/reference-library-20261105/README.md)**：怎样看画面证据、音乐卡点、转场/抠像/字效，以及本地学习页如何启动。
2. **[下载工程、音乐和完整学习包](RELEASE_URL)**：`reference-library-20261105.zip`是本轮完整学习库；`v05-six-panel.zip`包含可播放小样、慢放、HyperFrames工程与OpenChatCut可导入工程。解压后按中文README操作。
3. **[技法分类与难度排行](studies/reference-library-20261105/catalog/技法分类与难度排行.md)**：每种手法适合什么素材、需要哪些资源、目前是否实际做过。

| 你关心的内容 | 结果与入口 |
|---|---|
| 新旧20条逐片拆解 | [V01–V10](studies/reference-library-20261105/reviews/V01-V10.md) · [V11–V15](studies/reference-library-20261105/reviews/V11-V15.md) · [V16–V20](studies/reference-library-20261105/reviews/V16-V20.md) |
| 音乐单独提取和去重 | [音乐索引](studies/reference-library-20261105/data/audio/music-index.json) · [处理说明](studies/reference-library-20261105/data/audio/processing-notes.md) |
| 速度与激情10两分钟高燃怎么剪 | [73槽镜头方案、源片证据与128BPM节奏设计](studies/reference-library-20261105/fastx-120/README_两分钟高燃剪辑方案.md) |
| 已经真正做出来的例子 | [V05六格中文教程](studies/v05-six-panel/README_中文学习指南.md)，4.5秒、108帧、24fps；真实HF渲染与OCC可编辑导入 |
| 命令行每一步做什么 | [命令、异常处理与复查记录](studies/reference-library-20261105/docs/命令行与复查记录.md) |
| 后续继续提供参考 | [可复用skill](studies/reference-library-20261105/skills/reference-editing-replay/SKILL.md) |

**结果边界也写清楚：** 全部原帧有机器解码与图谱，人工看过全片总览/逐秒图谱和111页原生帧缩略图；没有声称人工全分辨率精读17,290帧。音乐主体候选可能残留对白/音效，未冒充原版纯伴奏或已识别曲名。FastX两分钟是可编辑计划和原创节奏导轨，目前成片实测范围是V05小样，其他参考的配方不等于已全部复刻。仅凭成片不能保证100%恢复作者工程。

[交付验证记录](studies/reference-library-20261105/data/delivery-validation.json)含原帧连续性、证据路径、40音频检查、MIDI、脚本及学习页验证。完整原视频、整部电影、个人路径配置、模型权重和缓存没有放入公开下载包；第三方媒体权利见[媒体说明](studies/reference-library-20261105/MEDIA_NOTICE.md)。

---

## 之前的GitHub软件研究仍保留

'''.replace('RELEASE_URL',release_url)
# Run once on the clean prior README.
root_readme.write_text(head+old,encoding='utf-8')

checks=[]
for name in ['reference-library-20261105.zip','v05-six-panel.zip']:
    p=release/name
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        assert not any(Path(n).name in {'local-media-paths.json','manifest.local.json'} or '.env' in Path(n).parts for n in z.namelist())
        if name.startswith('reference-library-'):
            assert len([n for n in z.namelist() if '/audio/' in n and n.endswith('.m4a')])==40
            assert len([n for n in z.namelist() if '/native-' in n and n.endswith('.jpg')])==299
        else:
            assert any(n.endswith('.ccproj') for n in z.namelist())
            assert 'v05-six-panel/hyperframes/index.html' in z.namelist()
        checks.append({'file':name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'entries':len(z.namelist()),'zip_integrity':True})
(release/'package-manifest.json').write_text(json.dumps({'packages':checks,'private_path_configs_excluded':True,'model_weights_excluded':True},ensure_ascii=False,indent=2),encoding='utf-8')
(repo/'studies/reference-library-20261105/data/package-manifest.json').write_text((release/'package-manifest.json').read_text(encoding='utf-8'),encoding='utf-8')
notes='''本轮按用户要求，将新旧20条混剪参考按原生帧率拆解并发布中文学习资料。

- 17,290张原帧、299页图谱、205个学习段、18类技法；低帧率素材未补成60fps。
- 20条原始AAC混音与20条本地模型分离的音乐主体候选；40文件完整解码、SHA/大小检查通过。未经人耳验收，不保证去净对白/音效，也未确认曲名。
- FastX：73槽、256拍、120秒计划，真实源片候选图、可编辑JSON/CSV/MIDI和原创128BPM节奏导轨；这不是已渲染的两分钟成片。
- V05：4.5秒真实成片、18秒慢放、HyperFrames源码与资源、OpenChatCut可导入工程，保留此前实际验证证据。

下载 `reference-library-20261105.zip` 后先读README；下载 `v05-six-panel.zip` 后读README_中文学习指南.md。两个包均保留中文文件名。

所有原帧有机器数据；人工审看的111页图谱范围逐片记录，不声称全分辨率人工看完17,290帧。除了V05结构短样，其余为研究与等效配方，不保证100%还原原作者工程。

原视频、整部电影、私有路径配置、模型权重没有分发。第三方影像、音乐仍属各自权利人；公开下载不是额外的商业素材许可。源码与报告在同tag提交中，附件SHA256见package-manifest.json。
'''
(release/'release-notes.md').write_text(notes,encoding='utf-8')
print(json.dumps(checks,ensure_ascii=False))
