from pathlib import Path
import json,hashlib,shutil,zipfile,csv,html
BASE=Path(__file__).resolve().parents[2];W=Path(__file__).resolve().parent;ROOT=BASE/'outputs/jjk-edge-v17-v3-dedup';HF=ROOT/'hyperframes'
plan=json.loads((HF/'edit.json').read_text(encoding='utf8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
def write(name,v):(ROOT/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
readme='''# 挚友 · EDGE · 画面去重 V3

本版处理你反馈的“画面复用严重”：从 D 盘咒术回战重新选片，替换21个重复主镜头位，并调整反复出现的前景动作。V1、V2保留。

## 先看成片

- [播放或下载MP4](挚友_EDGE_画面去重V3.mp4)：1920×1080、24fps、1440帧、60秒。
- [V2/V3播放器与替换定位](观看与对照.html)。
- [完整质检记录](质量检查.json)与[源片区间/画面相似筛查](evidence/源片区间与画面相似筛查.json)。

音乐沿用你的`edge.mp3`原曲147–207秒，master与V2字节相同。67个主镜头的切点和长度保持不动；原有大字、翻叶、撕边、电弧、镜片与主要遮挡接镜继续保留。

## 重复怎样改了

|范围|V2|V3|
|---|---|---|
|主镜头位（含一次黑场）|67|67|
|主镜头唯一素材ID（含黑场）|46|67|
|同一素材再次放进主序列的镜头位|21|0|
|前景事件/独立动作组|16次/7组|11次/11组|
|主字效|8组|8组|
|空间布局事件|14|18|

21处主镜头均从原片重新取片，不用改名、镜像或换裁切冒充新镜头。新片仍围绕少年五条与夏油的关系线，主要来自第二季前五集，保留原有情绪与动作段落。

重复的9处前景呈现中，4处换成新选片制作的独立动态前景；4处采用新素材的空间窗口；1处取消旧脸回放，让新主镜头完整显露。轮廓不稳定的试做alpha没有进入最终画面。原有“撕边人物条”“伸掌接镜”“觉醒人物压字”等主要动态遮挡继续保留。人工alpha仍有细发丝近似和原画裁切限制。

同期的前景与背景配合、翻叶分片、裂口扩成全屏，是同一转场的合成关系，保留同步源帧；它们与隔几秒把同一动作重新放一遍不同。少量眼线、镜片的风格呼应也未宣称彻底消失。

## 改了哪些位置

详见[21处替换清单](evidence/主镜头替换清单.json)与三页[实际成片对照01](evidence/21处替换实际成片对照-01.jpg)、[02](evidence/21处替换实际成片对照-02.jpg)、[03](evidence/21处替换实际成片对照-03.jpg)。每条记录都有旧素材、新集数、源时间码和成片帧位置。

机器检查包括每镜15%/50%/85%的三帧pHash筛查和主镜头源时间区间交叠检查。它们帮助定位疑似重复，不能证明所有相似构图、动画内部循环或观众的重复感都被自动识别。最终成片另有[全片32帧总览](evidence/全片32帧总览.jpg)；完整1440帧以192×108缩略解码检查，未逐张全分辨率人工验收，也未进行实际听觉试听。

## 可编辑工程

- `hyperframes/edit.json`：镜头、布局、前景、大字和音乐时间表。
- `hyperframes/composition.py`：由JSON生成HTML，保留V2的主要技法代码。
- `hyperframes/render.py`：实际HyperFrames CLI分20段渲染，合并MP4及OCC效果插片。
- `openchatcut/`：独立V3工程，原生67镜及20段HF效果序列；复杂alpha、撕边、大字回HyperFrames修改。
- `HyperFrames可编辑工程.zip`：随包短素材、音乐、透明前景、代码与说明，不含整集动画。

OpenChatCut工程通过官方CLI建档，工程包使用该应用的官方导入/导出实现核验。实际结果读`openchatcut/工程包最终回读.json`；没有把文件存在写成已经界面逐帧播放或试听通过。

## 本机再生成与再渲染

在本工作区根目录的PowerShell执行：

```powershell
$jjkPy = 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$jjkNode = 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
$jjkProject = 'outputs/jjk-edge-v17-v3-dedup/hyperframes'
& $jjkPy -X utf8 "$jjkProject/composition.py"
& $jjkNode "$jjkProject/hf.mjs" lint .
& $jjkPy -X utf8 "$jjkProject/render.py" --work work/jjk-edge-v17-v3-dedup/render
```

修改源JSON后需要重新渲染受影响段；`--encode-only`只编码已有主帧，不会更新过期画面。更换电脑时适配HF、Chrome、FFmpeg和Python路径。HF固定沿用0.8.216，本次没有升级工具链。

`制作过程/`保留本机搜索、素材准备、去重计划、alpha试做与核验脚本；它们部分依赖本工作区目录，先阅读路径再运行。`hyperframes/`生成与渲染入口以自身目录定位，可随工程携带。
'''
(ROOT/'README.md').write_text(readme,encoding='utf8')
(HF/'README.md').write_text('''# 画面去重 V3 · HyperFrames

请先读[主说明](../README.md)。本次从V2复制工程后独立修改；源镜头重新选择，音乐master与67个切点不变。

改`edit.json`后运行`composition.py`，再执行`render.py --work 你自己的缓存目录`。所有复杂字效、动态alpha、撕边和空间布局保留独立源码。不要只携带HTML，旁边的assets与Python文件也必须保留。

空间窗口是实拍/动画素材的实时框选，不标为动态抠像。透明人物来自实际源RGB与人工轮廓/LK/GrabCut，发丝与裁切边存在近似，未用生成模型补全人体。声音仍为edge147–207秒；本版未重新试听。
''',encoding='utf8')
changes=json.loads((ROOT/'evidence/主镜头替换清单.json').read_text(encoding='utf8'))
buttons=''.join(f'<button onclick="seek({s["startFrame"]/24})">{s["startFrame"]/24:.2f}秒 · {s["shot"]}</button>' for s in changes)
doc='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>挚友 EDGE · 画面去重 V3</title><style>body{margin:0;background:#0b1020;color:#eef2ff;font:16px/1.6 system-ui;padding:24px;max-width:1500px;margin:auto}h1{font-size:28px}.players{display:grid;grid-template-columns:1fr 1fr;gap:16px}video{width:100%;background:#000}button,a{color:#bde6ff}button{background:#172442;border:1px solid #355078;border-radius:6px;padding:8px;margin:4px;cursor:pointer}a{font-weight:600}@media(max-width:800px){.players{grid-template-columns:1fr}}</style><h1>挚友 · EDGE · 画面去重 V3</h1><p>替换21个重复主镜头位，音乐与67镜切点沿用V2。优先看右侧V3，左侧保留旧版对照。</p><div class="players"><div>旧版 V2<video id="old" controls muted preload="metadata" src="../jjk-edge-v17-v2/挚友_EDGE_精修V2.mp4"></video></div><div>画面去重 V3<video id="fresh" controls preload="metadata" src="挚友_EDGE_画面去重V3.mp4"></video></div></div><p><button onclick="syncPlay()">同位置播放</button><button onclick="old.pause();fresh.pause()">暂停</button><button onclick="seek(Math.max(0,fresh.currentTime-1/24))">上一帧</button><button onclick="seek(Math.min(59.999,fresh.currentTime+1/24))">下一帧</button></p><p>点击以下时间定位21处主镜头替换：</p>'''+buttons+'''<p><a href="挚友_EDGE_画面去重V3.mp4">打开MP4</a> · <a href="README.md">中文说明</a> · <a href="evidence/全片32帧总览.jpg">全片总览</a></p><script>const old=document.getElementById('old'),fresh=document.getElementById('fresh');function seek(t){old.pause();fresh.pause();old.currentTime=t;fresh.currentTime=t}function syncPlay(){old.currentTime=fresh.currentTime;old.play();fresh.play()}</script></html>'''
(ROOT/'观看与对照.html').write_text(doc,encoding='utf8')
proc=ROOT/'制作过程';proc.mkdir(exist_ok=True)
for p in W.glob('*.py'):shutil.copy2(p,proc/p.name)
write('制作约定.json',{'revision':'V3-dedup','baseline':'V2','durationSeconds':60,'fps':24,'frames':1440,'music':'edge.mp3','sourceMusicSeconds':[147,207],'audioMasterUnchanged':True,'v1V2Preserved':True,'primaryChange':'21处主镜头重复替换与前景动作去重','newReferenceDraw':False})
usedAlpha={x['alpha'] for x in plan['foregrounds']};usedShots={Path(a['asset']).name for a in plan['assets']};skip={'.hyperframes','.thumbnails','.source-backups','__pycache__','node_modules','.git'}
files=[]
for p in HF.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(HF)
 if any(s in skip for s in rel.parts):continue
 if rel.parts[:2]==('assets','alpha') and rel.parts[2] not in usedAlpha:continue
 if rel.parts[:2]==('assets','shots') and p.name not in usedShots:continue
 files.append((p,'hyperframes/'+rel.as_posix()))
for name in ['制作约定.json','质量检查.json','成片验证.json']:files.append((ROOT/name,name))
for name in ['V2重复使用基线.json','V3去重统计.json','主镜头替换清单.json','源片区间与画面相似筛查.json','全片32帧总览.jpg']:
 files.append((ROOT/'evidence'/name,'evidence/'+name))
for id in usedAlpha:
 for p in (ROOT/'evidence/alpha').glob(id+'*'):files.append((p,'evidence/alpha/'+p.name))
archive=ROOT/'HyperFrames可编辑工程.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=2) as z:
 z.writestr('README.md','# 挚友 EDGE · 画面去重V3 · HyperFrames工程包\n\n本包是可编辑工程，成片MP4与OpenChatCut工程包在交付目录另行提供。\n\n沿用edge147–207秒，60秒、24fps、1440帧。修改hyperframes/edit.json后运行composition.py与render.py。先读hyperframes/README.md。\n\n只携带本项目引用的短素材、音乐、透明人物、字体、代码和核验记录；不含整集动画及渲染缓存。被淘汰的试做alpha没有收入本包。\n')
 for p,name in files:z.write(p,name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
write('HyperFrames工程包核验.json',{'file':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),'entries':len(files)+1,'zipCrc':'passed','rejectedAlphaExcluded':True})
deliver=[ROOT/'挚友_EDGE_画面去重V3.mp4',archive,ROOT/'README.md',ROOT/'观看与对照.html',*list((ROOT/'openchatcut').glob('*.ccproj'))]
write('交付清单.json',{'revision':'V3-dedup','files':[{'file':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in deliver]})
print('PACKAGED',len(files),archive.stat().st_size)
