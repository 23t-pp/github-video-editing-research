# 挚友 · EDGE · 画面去重 V3

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
