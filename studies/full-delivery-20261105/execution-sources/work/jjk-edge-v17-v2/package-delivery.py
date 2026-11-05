from pathlib import Path
from datetime import datetime,timezone,timedelta
from urllib.parse import unquote
import json,zipfile,hashlib,re
BASE=Path(__file__).resolve().parents[2];ROOT=BASE/'outputs/jjk-edge-v17-v2';HF=ROOT/'hyperframes'
STAMP=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while b:=f.read(1024*1024):h.update(b)
    return h.hexdigest()
def write(name,data):(ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write('UI验收.json',{'recordedAt':STAMP,'method':'实际本机界面操作与截图；播放不等同听觉试听',
'moviePlayer':{'url':'http://127.0.0.1:5241','durationSeconds':60,'observedMainPlaybackTimeSeconds':33.224998,'mainPaused':False,'mainReadyState':4,'mainError':None,'mainMuted':False,'v1TimeSeconds':33.243027,'v1Muted':True,'frameStep':'定位460帧后点击下一帧，显示19.208秒/F461，步进1/24秒','comparisonScreenshot':'evidence/ui/V1-V2播放器.png'},
'hyperframes':{'url':'http://127.0.0.1:5240','durationSeconds':60,'observedPlayhead':28.75,'selectedLayer':'V02v2 Awake','canEditGroupStyles':True,'canMoveGroup':True,'groupDirectTextEditing':False,'observed':'大字、漫画板与独立动态前景可见；复杂文字通过edit.json与生成器修改；不以图层组可选中冒充直接可输入文字。','screenshot':'evidence/ui/HyperFrames精修图层.png'},
'openchatcut':{'url':'http://127.0.0.1:5199/#/editor/9ec9cec9-0a71-43fb-99be-adec9b564c60','importedProjectId':'9ec9cec9-0a71-43fb-99be-adec9b564c60','hfPlaybackObservedSeconds':51.16,'hfLocatedSeconds':28.79,'nativeSequenceOpened':True,'nativeClipInspected':'C05.mp4','observedSourceFrameRange':[12,41],'observedPlaybackRate':1,'nativeSmallLabelFontSize':36,'fps':24,'totalSeconds':60,'screenshots':['evidence/ui/OpenChatCut完整效果.png','evidence/ui/OpenChatCut原生片段属性.png']},
'auditoryListeningPerformed':False,'dragOrParameterMutationTestPerformed':False,'scope':'实际打开、播放、定位、逐帧与属性查看；工程重导入和媒体指纹见OCC回读报告。未在UI执行试拖或修改片段参数。'})
quality=json.loads((ROOT/'质量检查.json').read_text(encoding='utf-8'))
quality.update(audioLoudness={'integratedLUFS':-11.4,'LRA_LU':4.3,'truePeakDbFS':-2.1,'evidence':'evidence/声音响度实测.log'},hyperframesLint={'errors':0,'warnings':33,'evidence':'evidence/HyperFrames-lint.log'},hyperframesRuntimeValidate={'exitCode':0,'consoleErrors':0,'sampledTextElementsPassingAA':1,'evidence':'evidence/HyperFrames-runtime-validate.log','scope':'不是全片无障碍或所有文字可读性验收'},officialOpenChatCutRoundtrip={'restoredMedia':68,'missing':0,'mediaSha256Equal':True,'editStructureEqual':True,'evidence':'openchatcut/工程包最终回读.json'})
write('质量检查.json',quality)
contract=json.loads((ROOT/'制作约定.json').read_text(encoding='utf-8'))
contract.update(title='挚友 · EDGE · 精修V2',revision='V2',artDirection='不局限V17/V02，效果与流畅度优先；增加真实动态抠像与排版；撕边人物条必须渲染边缘效果。',v1Preserved=True,outputMovie='挚友_EDGE_精修V2.mp4',referencePolicy='本次指定任务的精修续作，不重新抽样；参考结构与原创延伸在edit.json标注。')
write('制作约定.json',contract)
(ROOT/'evidence/README.md').write_text('''# 精修V2证据索引

- `V1-V2八组对照.jpg`：最终MP4的同一时刻新旧版。
- `四处衔接逐帧检查.jpg`：最终MP4的四处源时钟与构图衔接。
- `V1-V2首批对照.jpg`：早期诊断图，其中撕边仍是加强前状态；最终效果以八组对照为准。
- `源帧与衔接检查.json`：所有源帧范围、透明文件存在性、准备媒体指纹与四个连续源帧边界。
- `附加层覆盖计划.json`：事件声明区间并集；不等同每帧实际可见或质量验收。
- `alpha`：新增动态抠像范围、透明/红底联系表与源裁切限制。
- `typography`：字体轮廓、短片段真实渲染及跨段一致检查。
- `ui`：真实播放器、HyperFrames图层和OpenChatCut重导入工程界面。
- 静态lint、运行检查、声音响度日志保留原始警告，不将警告隐藏成“全通过”。

整片缩略解码与音频数值检查见上一级`质量检查.json`。无实际听觉试听，也未逐张人工看完1440张全分辨率画面。
''',encoding='utf-8')
# Small reproducibility tools live with the delivered evidence, not render caches.
proc=ROOT/'制作过程';proc.mkdir(exist_ok=True)
for name in ['plan-v2.py','verify-v2.py','check-dependencies.py','validate-hf.py','start-previews.ps1']:
    import shutil
    shutil.copy2(Path(__file__).resolve().parent/name,proc/name)
(proc/'README.md').write_text('''# 本机本轮操作记录

这些脚本记录本工作区的计划、核验和预览操作，部分以本工作区根目录为基准。它们不是跨电脑通用安装器。

真正可随工程移动的生成与渲染入口是`hyperframes/composition.py`和`hyperframes/render.py`；请按HyperFrames说明操作。不要在移动后的目录直接执行本文件夹内的核验脚本。
''',encoding='utf-8')
intro='''# 《挚友 · EDGE · 精修V2》HyperFrames可编辑工程

本轮增加动态抠像、空间布局、连续曲面字与撕边电弧。60秒、24fps、1440帧、1920×1080，沿用用户edge.mp3的147–207秒。

先读[学习总结与命令](学习总结与命令.md)，再按[HyperFrames工程说明](hyperframes/README.md)启动预览。短素材、音乐、RGBA透明序列、字体、字形路径、镜片锚点、JSON、HTML/GSAP与Python脚本均已包含。无需重新读取整集动画。

[八组画面对照](evidence/V1-V2八组对照.jpg)和[逐帧衔接](evidence/四处衔接逐帧检查.jpg)来自最终成片。质量检查保留真实检查范围和剩余差异。

最终MP4与OpenChatCut .ccproj在交付目录单独提供；本包不含整集动画、渲染缓存、旧HTML备份。它也不是单文件HTML，预览依赖整个assets目录。工具路径按当前Windows电脑配置，换电脑需按说明调整。
'''
skip={'.hyperframes','.thumbnails','.waveform-cache','.render-cache','__pycache__','.source-backups','node_modules','.git'}
files=[]
for folder in ['hyperframes','evidence','制作过程']:
    for p in sorted((ROOT/folder).rglob('*')):
        rel=p.relative_to(ROOT)
        if p.is_file() and not any(s in skip for s in rel.parts) and p.suffix!='.pyc' and not p.name.endswith('.html.bak'):files.append((p,rel.as_posix()))
for name in ['学习总结与命令.md','制作约定.json','成片验证.json','质量检查.json','UI验收.json']:
    assert (ROOT/name).is_file(),name
    files.append((ROOT/name,name))
manifest=[{'path':n,'bytes':p.stat().st_size,'sha256':sha(p)} for p,n in files]
archive=ROOT/'HyperFrames可编辑工程.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=4) as z:
    z.writestr('README.md',intro)
    for p,n in files:z.write(p,n)
    z.writestr('文件校验清单.json',json.dumps(manifest,ensure_ascii=False,indent=2))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    names=z.namelist();assert len(names)==len(set(names))
    for n in ['hyperframes/index.html','hyperframes/assets/audio/master.wav','hyperframes/barlow-glyphs.json','hyperframes/layoutfx.py']:assert n in names,n
write('HyperFrames工程包核验.json',{'recordedAt':STAMP,'file':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),'entries':len(names),'zipCrcCheck':'passed','excluded':sorted(skip)})
occ=next((ROOT/'openchatcut').glob('*.ccproj'))
write('交付清单.json',{'recordedAt':STAMP,'revision':'V2','referencePolicy':'沿用指定任务，技法自由扩展','durationSeconds':60,'fps':24,'frames':1440,'files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [ROOT/'挚友_EDGE_精修V2.mp4',occ,archive,ROOT/'README.md',ROOT/'学习总结与命令.md',ROOT/'观看与对照.html']]})
missing=[]
for doc in [ROOT/'README.md',HF/'README.md',ROOT/'学习总结与命令.md']:
    for link in re.findall(r'\]\(([^)]+)\)',doc.read_text(encoding='utf-8')):
        if not link.startswith(('http:','https:','#')) and not (doc.parent/unquote(link.split('#')[0])).exists():missing.append((doc.name,link))
assert not missing,missing
print(json.dumps({'zipBytes':archive.stat().st_size,'entries':len(names),'crc':'passed','links':'passed','occBytes':occ.stat().st_size},ensure_ascii=False))
