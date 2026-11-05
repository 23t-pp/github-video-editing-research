from pathlib import Path
from datetime import datetime,timezone,timedelta
from urllib.parse import unquote
import json,zipfile,hashlib,re
ROOT=Path(__file__).resolve().parents[2]/'outputs/jjk-edge-v17';HF=ROOT/'hyperframes'
STAMP=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while chunk:=f.read(1024*1024):h.update(chunk)
    return h.hexdigest()
def write(name,data):(ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write('UI验收.json',{
 'recordedAt':STAMP,'browser':'本机实际界面检查，使用CUA操作；见evidence/ui截图',
 'moviePlayer':{'url':'http://127.0.0.1:5231','observedPlaybackTimeSeconds':50.189745,'durationSeconds':60,'readyState':4,'error':None,'muted':False,'frameStep':'定位32.25秒后点击下一帧，显示32.292秒、F775，步进为1/24秒','referenceReadyStates':{'V17':4,'V02':4},'proof':'evidence/ui/观看与学习播放器.png'},
 'openchatcut':{'importedProjectId':'dc02577e-2c3e-435f-9515-51411e73ced4','importedProjectUrl':'http://127.0.0.1:5199/#/editor/dc02577e-2c3e-435f-9515-51411e73ced4','officialMediaRestored':68,'missingMedia':0,'hfSequencePlayback':'已点击播放，观察42秒和49.91秒画面；随后暂停。','nativeSequence':'已打开67镜序列，实际显示首镜受伤五条，67段缩略图与独立master可见。','editableProperties':'已打开C05.mp4片段属性，源区间12–41帧及滑移控件可见；未修改参数。','fps':24,'durationFrames':1440,'proof':['evidence/ui/OpenChatCut重开工程.png','evidence/ui/OpenChatCut原生67镜.png','evidence/ui/OpenChatCut片段属性.png']},
 'hyperframes':{'url':'http://127.0.0.1:5230','previewTimeSeconds':28.8,'observed':'动态五条位于紫色最强/觉醒字前；实际选中V02 Awake Line0，右侧可见最强内容输入、JJK Heavy、280px、900字重及48个Motion效果。','proof':'evidence/ui/HyperFrames可编辑文字.png','lint':{'errors':0,'warnings':8},'runtimeValidate':'通过；无控制台错误，抽检3个文字元素通过其对比度检查'},
 'auditoryListeningPerformed':False,'parameterOrDragMutationTestPerformed':False,
 'scope':'实际播放、定位、选择、属性与工程重开；不把界面播放等同听觉试听，也不声称在UI中拖动/修改过片段。'
})
quality=json.loads((ROOT/'质量检查.json').read_text(encoding='utf-8'))
quality['audioLoudness']={'integratedLUFS':-11.4,'LRA_LU':4.3,'truePeakDbFS':-2.1,'evidence':'evidence/声音响度实测.log'}
quality['hyperframesLint']={'errors':0,'warnings':8,'evidence':'evidence/HyperFrames-lint.log'}
quality['hyperframesRuntimeValidate']={'exitCode':0,'consoleErrors':0,'contrastElementsPassed':3,'evidence':'evidence/HyperFrames-runtime-validate.log'}
quality['animationMapHelper']={'status':'unavailable','reason':'技能附加脚本需要独立@hyperframes/producer包，本机安装的CLI未提供该导入；不计为通过。'}
write('质量检查.json',quality)
scope=json.loads((ROOT/'evidence/片源选择与时间表.json').read_text(encoding='utf-8'))
plan=json.loads((HF/'edit.json').read_text(encoding='utf-8'));scope['shotTimeline']=plan['shots'];scope['finalNotes']='已按最终S05、S58与复用源入点修正；此处使用最终edit.json快照。';write('evidence/片源选择与时间表.json',scope)

intro='''# 《挚友 · EDGE》HyperFrames可编辑工程

这是用户指定edge.mp3与《咒术回战》素材的一分钟混剪，V17为主参考、V02为文字副参考。24fps、1440帧、1920×1080。

1. 先读[学习总结与命令](学习总结与命令.md)。
2. 按[HyperFrames工程说明](hyperframes/README.md)启动预览。
3. 看[六组参考对照](evidence/六组参考对照.jpg)，再从edit.json修改一个参数练习。

包内包含短片段、60秒音乐、真实逐帧alpha、字体子集、镜片人工锚点、HTML/GSAP、Python生成器与渲染器。普通预览和再渲染可直接使用这些资产；本机工具路径与换电脑的调整方法见工程说明。

最终MP4与OpenChatCut .ccproj在外部交付目录单独提供。本包含HyperFrames工程、教程、证据与质量报告，不含整集动画、渲染缓存或旧HTML备份。部分教程讲解本工作区的首次提取命令，普通编辑无需重新提取整片。

字效、前景与纸边属于本次新增合成；源动画的术式、玻璃与光束属于原片。人物角度、纸边细节、鞋尖裁切和镜片折射仍存在差异，具体检查范围见质量检查及学习总结。
'''
skip={'.hyperframes','.thumbnails','.waveform-cache','.render-cache','__pycache__','.source-backups','node_modules','.git'}
files=[]
for folder in ['hyperframes','evidence']:
    for p in sorted((ROOT/folder).rglob('*')):
        rel=p.relative_to(ROOT)
        if p.is_file() and not any(s in skip for s in rel.parts) and p.suffix not in ('.pyc',):files.append((p,rel.as_posix()))
for name in ['学习总结与命令.md','制作约定.json','成片验证.json','质量检查.json','UI验收.json']:
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
    assert 'hyperframes/index.html' in names and 'hyperframes/assets/audio/master.wav' in names
    assert not any(n.endswith('.html.bak') for n in names)
write('HyperFrames工程包核验.json',{'recordedAt':STAMP,'file':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),'entries':len(names),'zipCrcCheck':'passed','excluded':sorted(skip)})
occ=next((ROOT/'openchatcut').glob('*.ccproj'))
write('交付清单.json',{'recordedAt':STAMP,'primaryReference':'V17','secondaryReference':'V02文字','musicSource':'用户edge.mp3，147–207秒','durationSeconds':60,'frames':1440,'fps':24,'files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [ROOT/'挚友_EDGE_一分钟.mp4',occ,archive,ROOT/'README.md',ROOT/'学习总结与命令.md',ROOT/'观看与学习.html']]})
missing=[]
for doc in [ROOT/'README.md',HF/'README.md']:
    for link in re.findall(r'\]\(([^)]+)\)',doc.read_text(encoding='utf-8')):
        if not link.startswith(('http:','https:','#')) and not (doc.parent/unquote(link.split('#')[0])).exists():missing.append((doc.name,link))
assert not missing,missing
print(json.dumps({'zipBytes':archive.stat().st_size,'entries':len(names),'crc':'passed','links':'passed','occBytes':occ.stat().st_size},ensure_ascii=False))
