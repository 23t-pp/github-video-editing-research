# V05 六格卡片小样：本机 HyperFrames 运行时核查

核查对象：`C:/Users/PC/Apps/hyperframes/node_modules/hyperframes` **0.8.216**。初步核查执行 `init/lint/check/render --help`、读取已安装源码、检查工具文件存在；随后按主流程新增授权执行了0.1秒FFmpeg写入/管道探针（见文末）。**没有初始化、安装、HyperFrames渲染、启动浏览器或修改环境/全局配置**。下面的制作命令是主流程下一步使用的建议，并非已经跑通的记录。

## 先用这个结论

- 由已验证可写的 Codex Node 直接运行已安装 CLI，避免 `npx` 选到别的 Node 或触发下载。
- 本机 CLI 的 `render` 主动偏好 managed Chrome；未设置浏览器路径时，**即使系统装着 Chrome，也可能先下载 managed Chrome**。明确用子进程环境 `HYPERFRAMES_BROWSER_PATH` 指向现有 Chrome，才能确定避开这条下载路径。
- 六个 `video` 可以同源、同 `data-start/data-media-start/data-duration`，但必须有**唯一 id、不同轨道**。引擎按源路径/trim/长度/fps/格式去重抽帧，之后按每个 id 和全局时刻注入图片；这支持导出时同步，不依赖六个浏览器播放器自行跟时钟。
- `clip-path` 属于引擎复制的媒体视觉属性；更简单稳妥的是 **普通、非 timed 的 wrapper + `overflow:hidden`**。每格 video 保持固定源尺寸，在 wrapper 上做卡片位移/旋转/缩放。
- FFmpeg 的“streaming”是**截图输入通过 stdin 喂给 FFmpeg**，最终 MP4 仍由 FFmpeg 写磁盘。它**不是**将最终 MP4 输出给 Node 的 stdout 管道。`--output -` 在此 CLI 中会 `resolve('-')` 成磁盘文件，不能拿它绕过写入限制。
- Windows 非 debug workDir 默认在 `os.tmpdir()/hf-render-*`；抽帧 cache 另有官方 `--frames-cache-dir`。换 output 路径不会自动把所有临时文件一并搬过去。

## 工具与选择顺序

已确认文件存在：

```text
Node   C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe
CLI    C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/bin/hyperframes.mjs
Chrome C:/Program Files/Google/Chrome/Application/chrome.exe
FFmpeg C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe
Probe  C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe
GSAP   C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/dist/vendor/npm/gsap@3.15.0/dist/gsap.min.js
```

FFmpeg / ffprobe：环境变量 `HYPERFRAMES_FFMPEG_PATH` / `HYPERFRAMES_FFPROBE_PATH` 优先；否则 Windows 扫 cwd 与 PATH，优先 `.exe`；再查工程 `.hyperframes/bin/<binary>.exe` 与已安装 installer 包。render preflight 找到后还会把解析路径传给引擎。它不是 Remotion bundled FFmpeg。

浏览器：`HYPERFRAMES_BROWSER_PATH` 优先，其次 `PRODUCER_HEADLESS_SHELL_PATH`；本版本的 `browserPathFromEnv()` **没有 `CHROME_PATH`**。render 调 `ensureBrowser({preferManagedChrome:true})`，随后由设置 worker/引擎继承路径。直接启动现成系统 Chrome 会走 screenshot 路线；无需为了这个小样追求 beginFrame / Dev Chrome。

Node 子任务：设置 worker 用 `process.execPath` 启动，因此从上面的 Codex Node 启动 CLI 可以传递给这些 worker；但外部 FFmpeg 和 Chrome 仍是各自进程，Node 能写文件不等于它们也能写同一目录。

源码证据（以下行号来自已安装 0.8.216，仅供本轮定位）：

| 文件（相对 CLI 的 dist/） | 位置与结论 |
|---|---|
| `chunk-VAS6HQX3.js` | 13：FFmpeg env 名；83：工程 `.hyperframes/bin`；131–155：系统/项目/installer 查找；160：env 优先 |
| `chunk-WE42NVH7.js` | 77：两个 browser env 的顺序 |
| `chunk-QRIC4WOO.js` | 491–524：preferManagedChrome 路线；显式 env 在最前返回 |
| `render-AQH2VMHO.js` | 532–536：output 解析；861–881：ensureBrowser；1992–1995：预检工具路径传递 |
| `chunk-X6JUUQCM.js` | `runRenderSetupWorker` 调 `process.execPath` |

## 六格媒体与同步的最小 contract

下面是**技术结构示意**，不是最终美术稿或已验证小样。`assets/shot.mp4` 需由主流程选定，示意 trim=2 秒、片长=4 秒，源文件须至少有相应长度。GSAP 从本机现有 vendor 文件复制进工程 `assets/gsap.min.js` 即可，无需 CDN 或 npm install。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=1920, height=1080">
  <script src="assets/gsap.min.js"></script>
  <style>
    * { box-sizing: border-box; }
    html,body { margin:0; width:1920px; height:1080px; overflow:hidden; background:#000; }
    #root { position:relative; width:1920px; height:1080px; overflow:hidden; }
    /* 3列 × 2行：六个裁剪窗组合为同一帧，非六份全画面缩略图。 */
    .tile { position:absolute; width:640px; height:540px; overflow:hidden;
      left:calc(var(--col) * 640px); top:calc(var(--row) * 540px); }
    .source { position:absolute; width:1920px; height:1080px; max-width:none;
      left:calc(var(--col) * -640px); top:calc(var(--row) * -540px);
      object-fit:cover; }
  </style>
</head>
<body>
<div id="root" data-composition-id="six-cards" data-start="0"
  data-duration="4" data-width="1920" data-height="1080" data-fps="30">
  <div class="tile" id="card-0" style="--col:0;--row:0"><video class="source" id="video-0" src="assets/shot.mp4" data-start="0" data-duration="4" data-media-start="2" data-track-index="0" data-volume="0" muted playsinline></video></div>
  <div class="tile" id="card-1" style="--col:1;--row:0"><video class="source" id="video-1" src="assets/shot.mp4" data-start="0" data-duration="4" data-media-start="2" data-track-index="1" data-volume="0" muted playsinline></video></div>
  <div class="tile" id="card-2" style="--col:2;--row:0"><video class="source" id="video-2" src="assets/shot.mp4" data-start="0" data-duration="4" data-media-start="2" data-track-index="2" data-volume="0" muted playsinline></video></div>
  <div class="tile" id="card-3" style="--col:0;--row:1"><video class="source" id="video-3" src="assets/shot.mp4" data-start="0" data-duration="4" data-media-start="2" data-track-index="3" data-volume="0" muted playsinline></video></div>
  <div class="tile" id="card-4" style="--col:1;--row:1"><video class="source" id="video-4" src="assets/shot.mp4" data-start="0" data-duration="4" data-media-start="2" data-track-index="4" data-volume="0" muted playsinline></video></div>
  <div class="tile" id="card-5" style="--col:2;--row:1"><video class="source" id="video-5" src="assets/shot.mp4" data-start="0" data-duration="4" data-media-start="2" data-track-index="5" data-volume="0" muted playsinline></video></div>
  <!-- 如需保留原音，只加一份独立audio，勿让六个video重复混音。 -->
  <audio id="source-audio" src="assets/shot.mp4" data-start="0" data-duration="4"
    data-media-start="2" data-track-index="6" data-volume="1"></audio>
</div>
<script>
  window.__timelines = window.__timelines || {};
  const tl = gsap.timeline({paused:true});
  tl.fromTo('.tile', {scale:0.92}, {scale:1,duration:0.25,stagger:0.025,ease:'power2.out'}, 0);
  window.__timelines['six-cards'] = tl;
</script>
</body>
</html>
```

需要“六个独立卡片里各显示完整画面”时，把 `.source` 改为各格 640×540，`left:0;top:0;object-fit:cover`。这是**不同视觉结构**，不要与上面把一帧切成六块的结构混淆。做斜切/不规则卡片可在 wrapper 上设 `clip-path:polygon(...)`；先用普通 overflow 六格确认同步，再加复杂裁剪。

必须保留的约束：

- root 是真实 DOM 元素，不要把主画面放 `<template>` 中；root 的 data-duration 决定总长。
- 六个 media id 不可重复；视频叠加需要不同 `data-track-index`，视觉前后层级仍由 CSS z-index 决定。
- 六格 wrapper **不加** data-start / data-duration。不要把 timed video 套入另一个 timed clip，避免重复时序控制。
- GSAP timeline paused、同步构造并注册；不要自己调用 video.play/pause/currentTime，也不要用 RAF / `setTimeout` 驱动剪辑。
- wrapper 动画统一改变几何布局；源 video 维持固定尺寸。不要依赖 JS 只更新 video 的视觉样式而漏掉引擎注入的替身图片。
- 离线导出与预览不是同一可靠性：预览可能仍受 HTMLMediaElement 解码/seek 影响；需用导出关键帧验证六格是否真同步。

实现证据：`chunk-VZENYSX7.js:14270` 附近 dedupeKey 包含物理源路径、extractionMediaStart、videoDuration、fps、格式/色彩等；`uniqueWorks` 去重后，结果重新关联每个 videoId。`FrameLookupTable`（约14440行）按 `(id,globalTime,start,mediaStart,rate)` 决定帧；`createVideoFrameInjector`（14636起）逐 id 注入。相同源/trim但时长或速率不同不应假设一定共享同一抽帧窗口。

`injectResolvedVideoFramesBatch`（约3940行）在 video **同一个父节点**中插入 `<img class="__render_frame__">`，复制 object-fit、object-position、transform 等 computed style；父节点 overflow/clip-path 因而可以同时裁切原 video 与替身图片。`chunk-DYHAZFK3.js:1696` 的 `MEDIA_VISUAL_STYLE_PROPERTIES` 明确含 `clip-path`、`mask`、`overflow`、transform。`clip-path` 又会被标记为某些快速捕获优化的风险属性（`chunk-VZENYSX7.js:7584`），所以本小样优先 screenshot 路线。

## 下一步可用的 CLI 命令（本轮未执行）

下面从当前 workspace 根目录执行。`init` 只能指向不存在或空目录；不要对已有 `work/v05-sample` 根目录执行 init，因为本文件已经在里面。

```powershell
$hfNode = 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
$hfCli = 'C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/bin/hyperframes.mjs'
$hfProject = Join-Path (Get-Location) 'work/v05-sample/composition'

# blank模板随包存在；不传--video，不触发转码；不转写、不装skills。
& $hfNode $hfCli init $hfProject --example blank --non-interactive --skip-transcribe --skip-skills

# 主流程放置选定素材、离线GSAP，并按最终构图替换index.html之后：
& $hfNode $hfCli lint $hfProject --json
& $hfNode $hfCli check $hfProject --json --at 0,0.2,0.5,2,3.9 --timeout 45s

# 初次先1个worker、SDR、截图路线，拒绝缺失素材，写显式输出位置。
$hfOutput = Join-Path (Get-Location) 'outputs/v05-six-cards-sample.mp4'
& $hfNode $hfCli render $hfProject --fps 30 --quality draft --format mp4 `
  --workers 1 --low-memory-mode --sdr --experimental-fast-capture=false `
  --no-best-effort --strict --output $hfOutput
```

**先给 check/render 所在子进程传入下列 env。** 本轮没有设置；建议主流程通过 Node `spawn(...,{env:{...process.env,...overrides}})` 限定到该子进程，避免改用户会话/全局设置。

```js
const overrides = {
  HYPERFRAMES_BROWSER_PATH: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  HYPERFRAMES_FFMPEG_PATH: 'C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe',
  HYPERFRAMES_FFPROBE_PATH: 'C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe',
};
// spawn(CODEX_NODE, [HF_CLI, 'render', project, ...flags],
//       {cwd:project,env:{...process.env,...overrides},stdio:'inherit',windowsHide:true});
```

相对 output 是按**启动CLI的 cwd**解析，默认 `renders/` 也是 cwd 下；传 project 参数不会自动把进程 cwd 变成 project。显式绝对 output 最容易核查。

本机版本与旧 skill 示例的差异：默认 quality 是 **looks（CRF16）**，还支持 draft/delivery，standard/high 是兼容名称；fps 可用25和有理数，非仅24/30/60；`--video-frame-format png` 是**源视频抽帧格式**，不是将最终成片导出为 PNG；最终序列要用 `--format png-sequence`。`check` 有浏览器运行时检查，不能以 `lint` 成功替代实际 check/导出验收。

## 写入限制：哪些官方选项确实能做什么

1. **先区分 Node 写失败还是 FFmpeg 写失败。** 顶层用 Codex Node 已知可写，但FFmpeg仍是 Apps/ffmpeg 的单独EXE。不能把“切换Node”说成FFmpeg Permission denied的必然解法。新增探针已确认FFmpeg直接写工作目录仍失败，详见文末。
2. **官方可定位的目录：** `--output <absolute-path>` 控制最终文件；`--frames-cache-dir <directory>` 控制源帧cache；`--frames-cache-dir off` 禁cache，把源抽帧落render workDir并结束清理；Windows非debug workDir取 `os.tmpdir()`。只对子进程设置 `TMP/TEMP` 可以改变Node选择的tmpdir，但必须先验证该目录确实可被Node/Chrome/FFmpeg写入，不能凭Node写成功推断全部可写。
3. **先不加 --debug。** debugDir 默认以安装的producer根目录为锚点，可能落Apps工具包内；非debug Windows workDir在系统temp更合理。需要debug时可仅对子进程设 `PRODUCER_RENDERS_DIR=<自己工程内/renders>`，使 `.debug` 锚到该目录的父目录。这不替代显式 `--output`，也不搬所有OS temp。
4. **1 worker 更利于查错。** 默认auto会启动多个Chrome并可能走校准。`--workers 1 --low-memory-mode`固定小规模截图路径，通常允许streaming encode，但仍有落盘抽帧/音频中间文件。它解决并发/内存压力，不解决EXE写权限。
5. **CLI没有本轮可确认的“最终MP4 stdout”选项。** `buildStreamingArgs`（`chunk-VZENYSX7.js:10837`）使用 `-f image2pipe -i -`，最后仍 `-y outputPath`；`spawnStreamingEncoder`（11018起）启动FFmpeg把截图写进stdin。更后面的音频mix/mux也需要文件。不要用PowerShell `>` 把CLI stdout当MP4，那里面是进度/诊断文本。
6. **可用官方PNG序列作为中间交付，但要理解限制。** `--format png-sequence --output <frames-directory>`由引擎保存RGBA帧，源码还支持audio sidecar；这能避开最终MP4编码器的磁盘输出，却**不能自动避开源视频抽帧与音频FFmpeg的写盘**。若预处理已将源素材转换成图片序列，可能更适合这条路径。
7. **已知成功的外层补救不是HF官方CLI能力：** 本机先前FFmpeg输出 `-f wav pipe:1` / `-f image2pipe pipe:1`，由Codex Node接Buffer再写盘，确实工作过。新增0.1秒探针已验证fragmented MP4输出stdout再由Node保存成功，但这是外层FFmpeg封装，不是`hyperframes render --output -`。若要把HF所有抽帧/编码写盘都这样替换，需要另写适配层；本轮没有改源码，也没有验证该完整方案。

源码定位：`chunk-CX4TSC7T.js:11595`给Windows/macOS选system temp；12302创建workDir；`chunk-VZENYSX7.js:10837–11040`为streaming参数与spawn；`chunk-CX4TSC7T.js:11839`为streaming gate（单worker可用、配置/format等仍可关闭）；11133附近为PNG序列交付；`render-AQH2VMHO.js:536`为CLI output resolve。若主流程仍报Permission denied，先保留实际失败的**二进制路径+命令+输出/临时目录**，才能决定是改官方目录选项还是采用自写管道封装。

## 本轮已执行清单

- Codex Node + 本机 CLI：`render --help`、`init --help`、`lint --help`、`check --help`，均exit 0。
- `Get-Content` / `rg` 静态审查上述安装包脚本、blank模板与vendor资源。
- 检查Chrome、FFmpeg、ffprobe文件存在。
- 没有执行doctor（可能有下载/探测）、browser ensure、init实际建工程、check浏览器会话、render或任何全局修改。

这份记录证明“本机实现具备这些接口与同步路径”，并不证明六格卡片已渲染成功。制作完成仍需至少查看首帧、六格同时出现的中帧、收尾帧，以及用同一源中的运动边缘跨格检查时间一致性。

## 追加授权后的实测：FFmpeg写盘仍失败，stdout MP4成功

实际运行 `runtime-probe/probe.mjs`，以同一个 good Node spawn 同一个 Apps/ffmpeg：

|探针|实际结果|
|---|---|
|lavfi black 64×64、30fps、0.1秒 → `direct-file.mp4`|FFmpeg exit `4294967283`；`Permission denied`；没有输出文件|
|同样输入/编码，加 `-movflags frag_keyframe+empty_moov -f mp4 pipe:1` → Node Buffer写文件|FFmpeg exit0、stderr空；写出1622字节MP4|
|ffprobe读取Node保存的MP4|exit0；H.264，64×64，duration=0.100000s|

探针记录：`work/v05-sample/runtime-probe/probe-result.json`。这只验证小型外层编码管道；没有运行HF真实渲染，不能把探针MP4当样片。

### 当前最小可控的制作路线

1. **原素材先转图片序列，FFmpeg只写stdout。** 主流程已具备image2pipe解析/Node保存能力；按选定source start、duration、fps抽出 `source/frame_000001.jpg` 等。这里仍使用视频内容，避免将实际动图变成静态拼图。
2. **HF HTML只引用本地图片，不放 `<video>` / `<audio>`。** 每张源帧是持续 `1/fps` 的timed `<img>`；六个非timed裁剪wrapper共享同序号源图片。GSAP负责六格卡片的运动、揭示、缩放和组合。这一步的最终合成和动画由真正HyperFrames/Chrome完成。
3. **官方CLI输出PNG序列。** 使用 `render project --format png-sequence --fps 30 --workers 1 --low-memory-mode --sdr --experimental-fast-capture=false --no-best-effort --output <hf-frames-directory>`。先做1–2帧/极短sample验证Chrome启动和Node帧写出，再扩到4秒。不要附带audio，以免触发HF音频mix写盘。
4. **外层FFmpeg读取HF真实PNG序列编码。** HF最终导出序列从 **`frame_000001.png`** 开始（`formatExportFrameName(index)`使用index+1），不是capture工作目录的零起序号。用 `-framerate 30 -start_number 1 -i <hf-frames>/frame_%06d.png ... -movflags frag_keyframe+empty_moov -f mp4 pipe:1`；Node保存Buffer或stream。需要原音时在这一步另加音频输入、trim与map，不要回头把音轨加入HF工程。

源码实证：`chunk-VZENYSX7.js:7992` 捕获截图Buffer由Node `writeFileSync`保存；`chunk-CX4TSC7T.js:11127–11146`的PNG序列分支用Node `copyFileSync`复制捕获PNG到导出目录并返回，跳过最终FFmpeg编码；14050行的最终assemble也对PNG序列跳过。不要依赖保留临时frames：它们可能按成功路径清理，官方`--format png-sequence`才是清晰可交付的出口。

图片版六格的静态HTML可由自己的小脚本生成，保持与上文相同的`.tile`和`.source`几何规则：

```js
// 示意：生成到每个非timed .tile中；不在浏览器异步创建这些clips。
// 六格的cellTrack分别0–5；同一格内图片不重叠，不用data-media-start。
const clips = Array.from({length:frameCount}, (_,i) => {
  const n=String(i+1).padStart(6,'0');
  return `<img id="tile-${cellTrack}-frame-${i}" class="source"
    src="source/frame_${n}.jpg" data-start="${i/fps}"
    data-duration="${1/fps}" data-track-index="${cellTrack}" alt="">`;
}).join('');
```

短样片几十/百余帧×六格会增加DOM量，但比修改HF内部FFmpeg执行逻辑可控。持续性运动来自源帧替换，卡片空间运动来自HF timeline，不是全程FFmpeg滤镜拼图。使用较短片段先验收，避免一次塞入整段V05的全部帧。

### 为什么不改用所谓公开render API

本机`hyperframes/package.json`确实导出`./api`，但`dist/api.d.ts`与`api.js`只公开 `transcribe` / `removeBackground` 及其类型；**没有公开 render-to-buffer / frame callback**。bundled `chunk-CX4TSC7T.js`内部导出`executeRenderJob`等不等于稳定公开API，而且仍走相同FFmpeg落盘路径。当前不应为了赶小样去patch全局安装或依赖hash文件名的内部API。

额外明确：该路线已验证的是FFmpeg stdout封装与官方PNG序列代码路径；Chrome/HF真渲染仍由主流程下一步执行并验收。本轮没有越权替主流程渲染。

