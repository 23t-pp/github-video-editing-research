# HyperFrames：完整效果可编辑工程

源文件：`edit.json`保存镜头、源入点、效果事件和图层绑定；`composition.py`把它生成`index.html`；`layoutfx.py/typefx.py/screenfx.py`分别负责布局、字形和档案屏；`assets/`含prepared视频、透明PNG、字体、GSAP及master音轨。

## 打开预览

解压ZIP后，用PowerShell进入此目录，再运行：

```powershell
$s1Node = 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
& $s1Node ./hf.mjs lint --json
& $s1Node ./hf.mjs preview --port 5352
```

浏览器按控制台地址打开HyperFrames Studio。`hf.mjs`调用本机已安装的CLI 0.8.216，并传入已存在的Chrome/FFmpeg路径；不会自行升级或重装软件。换电脑需安装对应依赖，并用`HYPERFRAMES_CLI`指定新的CLI文件。

## 修改后生成

```powershell
$s1Py = 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $s1Py -X utf8 ./composition.py
& $s1Node ./hf.mjs lint --json
```

先备份，再改JSON。0基成片帧号，区间[start,end)；1秒=24帧。`assetStartFrame`是prepared片的本地帧，不是全季JPG编号。修改英文词形后，曲面SVG还需相应字形路径，不能只改某个隐藏文字。

实际精确成片用`render.py`的72帧分段方案：源视频先解成同号PNG，alpha逐帧对应，HF CLI实际捕获，再验证全部20段依赖并编码。完整命令和实际执行者在各轮`execution.json`与实作笔记。它不是单纯把浏览器实时播放录屏。

`render.py`可按顺序捕获全部20段；工作区runner只是并行调度入口。ZIP保留创作资源和源码，原工作区保留逐段渲染proof/cache用于复验。普通Studio预览不需要解压全季JPG库，也不需要电影原片；重新选择全季其他素材则需要D盘原视频。

如果你在解压副本里改了效果，下面命令会生成第5轮完整视频，输出到副本旁的`loops/loop-05/`，保留本次最终文件：

```powershell
& $s1Py -X utf8 ./render.py --loop 5 --plan ./edit.json --work ../修改版渲染缓存
```

这会实际解码源PNG、调用HF截图再编码，耗时明显高于网页预览。参数`--work`只指定缓存目录，不改变D盘原片。视频源都已随包包含；想换包内没有的新镜头时，才回原片补取。

## 修改入口

|对象|字段/文件|
|---|---|
|镜头顺序与构图|edit.json shots：startFrame/frames/assetStartFrame/reframe|
|三联、眼缝、裂边、七叶、记忆窗|edit.json layouts + layoutfx.py|
|青掌与跑动前景|edit.json foregrounds + assets/alpha；不得打乱同号源钟|
|曲面/厚度字|edit.json typeEvents + typefx.py + barlow-glyphs.json|
|档案屏|archiveScreen + screenfx.py|
|音乐|assets/audio/master.wav；保持2,880,000采样即可继续60秒|

Studio里可播放/定位；本工程复杂效果为代码驱动，完整编辑入口是这些参数和源码，并非每个SVG路径都能用鼠标直接拖改。OCC的HF序列则是已合成插片，这些细层需回此工程。

当前版本：`L3-D-craft-revision`。实际验收见项目根目录各轮review与最终验收；本README不会替代画面审核。
