# 20条参考音轨与本地音乐候选库

> **先分清使用方式：独立学习库ZIP解压后，按库根README启动学习页即可阅读、查看证据和听已生成的40条音轨，无须重新分离。完整音频重跑则需要原始20条视频、下述目录结构以及本地分析模块、Python依赖和模型；下载ZIP后的一条启动命令不会完成这些依赖安装。**

统一播放器索引：`data/audio/music-index.json`。每条用V01–V20关联原片，包含 `mix_path` 与 `no_vocals_candidate_path`；`library-summary.json`记录实际完成数量。两类音频的用途不同：

- `audio/mixed/`：从原视频直接提取的混合音轨，保留原有音乐、对白、人声和音效的组合。20条源均为AAC，使用stream copy，未再次编码；AAC编码内容哈希逐条核验与源一致。
- `audio/music-candidates/`：通过真实本地模型生成的 **Instrumental音乐主体候选**，再编码AAC 192kbps。没有实际听辨确认，可能残留人声、对白、和声或SFX，也可能损伤音乐。`no_vocals_candidate_path`是文件角色名称，不是“绝无人声”的质量保证。

有独立证据的曲名才入库。V24 结合片中配乐标注、发行目录和试听波形确认了《trainers》。音乐分离在本机完成。素材适用标签来自周期、时长和能量起伏，用于辅助剪辑。 [V24 声音证据](../../evidence/V24/verified/音频与卡点复核.md)

本轮已完成20条混合轨和20条分离候选，共40个M4A。逐文件SHA256、字节数与FFmpeg完整解码检查全部通过，见 `validation.json`；分离推理累计772.729秒，CPU两线程。原AAC编码内容20/20与源一致；六种精确哈希口径均未发现重复组，这不证明配乐曲目不同。混合轨4,783,210字节，候选15,442,656字节。听感、人声/SFX残留程度和音乐权利归属不在本次自动验证范围内。

## 实际采用的工具与来源

|组件|本轮版本 / 用途|
|---|---|
|Node|Codex bundled Node 24.22.1，负责本地FFmpeg stdout Buffer写入|
|FFmpeg / ffprobe|9.0.2，解复用、解码、响度测量、候选AAC编码、文件验证|
|HyperFrames|0.8.216 local signal provider：频带谱通量、自相关和DP节拍候选、音色结构候选|
|montage|0.4.1的log-RMS正差作为基线交叉比较|
|Python|隔离venv，3.12.14；没有改全局Python|
|audio-separator|0.48.0，MIT代码，[官方项目](https://github.com/nomadkaraoke/python-audio-separator)|
|ONNX Runtime / PyTorch|1.31.1 / 2.15.0+cpu；实际使用CPUExecutionProvider，2线程、单任务、模型常驻|
|模型|UVR_MDXNET_KARA_2.onnx，52,786,726字节，[UVR模型发布源](https://github.com/TRvlvr/model_repo/releases/tag/all_public_uvr_models)|

模型参数由 [UVR application_data](https://github.com/TRvlvr/application_data) 的MDX参数表按末尾10,240,000字节MD5匹配；本轮匹配值为 `1d64a6d2c30f709b8c9b4ce1366d96ee`。工具代码MIT与模型权重不是同一授权对象；模型repo本轮未找到可识别LICENSE，**不随本研究包分发权重**。模型来源、SHA256、版本及实际执行统计另记在 `provenance.json`。

## 怎样复跑

**独立ZIP可放在任意目录学习；以下完整重跑命令要求先还原工作区布局。** 将解压后的学习库放到 `outputs/reference-library-20261105/`，再创建同级工作区下的 `work/reference-library-20261105/`。不要把 `work` 建在学习库根里面。最小目录如下，`工作区/`可以是你选择的任意父目录：

```text
工作区/
├─ outputs/
│  └─ reference-library-20261105/    ← 解压后的学习库根，有index.html
│     ├─ scripts/prepare-manifest.mjs
│     ├─ scripts/audio/
│     ├─ local-media-paths.json      ← 自己填写V01–V20原片路径
│     └─ manifest.local.json        ← prepare-manifest生成
└─ work/
   └─ reference-library-20261105/
      └─ manifest.local.json        ← 从学习库根复制，音频脚本读取此处
```

在“工作区”目录打开PowerShell，先把 `local-media-paths.example.json` 复制为库根的 `local-media-paths.json`，填写自己的20条原视频路径。原视频不在ZIP内；相对原片路径按这个配置文件所在目录解析。然后生成清单并复制到音频脚本约定的位置：

```powershell
$audioNode = 'node' # 若有写入限制，改成已验证可写的Node完整路径
$libraryRoot = (Resolve-Path '.\outputs\reference-library-20261105').Path
$audioWork = '.\work\reference-library-20261105'
# 如ffprobe不在默认位置，先将下一行改为自己的路径。
$env:FFPROBE_PATH = 'C:\你的工具目录\ffprobe.exe'
& $audioNode "$libraryRoot\scripts\prepare-manifest.mjs" "$libraryRoot\local-media-paths.json"
if ($LASTEXITCODE -ne 0) { throw '清单生成失败，请先检查原片和ffprobe路径。' }
New-Item -ItemType Directory -Force -Path $audioWork | Out-Null
Copy-Item -LiteralPath "$libraryRoot\manifest.local.json" -Destination "$audioWork\manifest.local.json" -Force
```

**分析依赖必须对应本轮版本：** `HYPERFRAMES_INSTALL`指向HyperFrames **0.8.216包根**，其中必须实际存在 `dist/chunk-NOH32H42.js`；任意新版HyperFrames不保证兼容。montage必须有 **0.4.1** 本地模块，脚本当前读取用户目录下 `.codex/skills/montage/assets/dsh-montage/lib/analyze.js`。这些模块不包含在独立ZIP中；`Setup-Audio.ps1`只准备分离所需的隔离Python依赖和模型，不安装HyperFrames、montage、Node或FFmpeg。

先在本工作区的 `work/reference-library-20261105/manifest.local.json` 提供20个本地原片路径。该私有manifest和临时日志不属于公开报告；公开JSON只保留ID、文件名和相对输出路径。

以下命令从包含 `outputs/` 与 `work/` 的工作区根目录运行。它们依赖本机已有HyperFrames 0.8.216和montage 0.4.1分析模块；仅安装普通Node并不足以复跑分析。`HYPERFRAMES_INSTALL`可指向已有HyperFrames包目录，FFmpeg路径可用 `FFMPEG_PATH` / `FFPROBE_PATH`覆盖；这些环境变量只由进程读取，不会写入公开JSON。不同HyperFrames版本的内部chunk文件名可能变化，本轮固定为 `dist/chunk-NOH32H42.js`，来源版本必须对应。

```powershell
$audioNode = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
$audioScripts = '.\outputs\reference-library-20261105\scripts\audio'

# 先提取原始混合轨、测响度，再重算音频起音和节奏候选。
& $audioNode "$audioScripts/extract-mixed.mjs"
& $audioNode "$audioScripts/analyze-library.mjs"
& $audioNode "$audioScripts/hash-integrity.mjs"

# 只有要重新分离时才需要安装这个work内venv和下载单个模型。
& "$audioScripts/Setup-Audio.ps1"
& $audioNode "$audioScripts/prepare-separation-inputs.mjs"
$separatorPython = '.\work\reference-library-20261105\audio-env\Scripts\python.exe'
& $separatorPython "$audioScripts/separate-local.py"

# 根据已成功完成的逐条checkpoint生成可播放候选、统一索引及去重。
& $audioNode "$audioScripts/finalize-library.mjs"
& $audioNode "$audioScripts/validate-library.mjs"
```

`validate-library.mjs`输出 `passed=true` 和 `files_checked=40` 才表示本轮成品检查完整通过。`write-provenance.mjs`用于记录本轮安装与探针证据，需保留已完成的8秒探针记录和模型参数缓存；它不是正常重跑成品所必需的步骤。

`separate-local.py`每完成一条就缓存WAV与checkpoint，重新启动时跳过已完成条目。分离输出峰值阈值0.95、不开静音放大，MDX overlap 0.25、batch1、segment256；没有额外宣称去掉全部音效。首次8秒V01探针实际生成Vocals和Instrumental两条WAV，用时约18.98秒，之后才开始全量处理。

本机AMD显卡未用于CUDA。ONNX初次导入缺MSVC运行库，处理脚本仅对当前Python进程使用 `os.add_dll_directory` 加载Codex现有运行库；没有系统安装或安全设置修改。依赖缺失的audioread补装在venv中，`pip check`通过。完整锁定版本在 `scripts/audio/requirements-lock.txt`。

## 为什么使用stdout而不是直接让FFmpeg写文件

本机FFmpeg进程直接写工作区曾报Permission denied，而Codex Node可以写。所有新音频通过FFmpeg stdout返回二进制，由Node保存。M4A使用fragmented MP4容器，不把CLI进度文本当媒体。

原AAC有decoder preroll：直接empty_moov会丢失跳过信息；本轮改用delay_moov保留负PTS/skip信息。原混合轨容器时长可能包含preroll，索引同时区分容器时长和实际解码时长。边界padding仍可能令解码PCM末尾与原片有毫秒级差别，AAC包内容保持一致并已核验。

长分离候选在初次AAC封装后检测到解码错误，因此改用 `default_base_moof` 与1秒fragment，并重新编码/完整解码验证；只把验证通过的候选纳入最终索引。分离主体先落WAV；公开库为M4A，192kbps用于控制再编码影响，不代表恢复原片已损失的信息。

## 节拍与去重的证据边界

- RMS/dBFS、LUFS描述电平或响度，不等同音乐节拍。谱起音也可能是对白辅音、碰撞、whoosh或引擎声。
- HF beat是周期模型推断；未通过门槛时保持空数组。V07/V09/V16/V17/V19即不能拿固定网格填成“检测成功”。V05/V12/V15等保留多算法冲突。
- 索引BPM只列候选，存在半倍/倍速、切分节奏和变速歧义。没有试听，不用分离后的电平变化冒充“人声去除率”。
- `dedup.json`分别比较成品文件SHA256、AAC ADTS编码内容SHA256、原生采样率/通道数的float32 PCM SHA256。只有完全相等才是相应口径的重复；没有使用声纹相似判定同曲。
- 即便20条混合轨没有精确重复，也不能推出20首不同BGM：对白、音效、增益、裁切和编码都会改变哈希。
- 混合轨stream copy保留原编码采样率；分析使用22.05kHz单声道副本，模型分离使用44.1kHz立体声副本，模型候选为44.1kHz。视频按原生帧率拆解。BPM不是FPS；音频分析的10ms hop不代表把视频补成60fps。

建议先用混合轨研究原片的声音落点，再试听音乐主体候选决定能否重新配画面。起音与BPM数据可以帮助下标记；素材顺序、音效、段落张力和最后的听感仍需单独判断。
