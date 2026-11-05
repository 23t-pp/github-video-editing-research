# 当前本机可复现能力与REA边界

结论：OCC适合可编辑多轨、帧级切镜、基础特效、几何mask和恒速；HF/GSAP/montage适合精确字效与图层合成。人物精细抠像、曲线变速、复杂跟踪通常要预处理/人工校准；现有REA没有已核实的MP4自动反求剪辑工程入口。

本报告只读本地源码、技能和命令帮助，未分析10条视频本身，未停止OCC服务、未上传视频、未调用云AI或安装引擎。OCC固定参考SHA：`7fa4b7903e7ebecf832a36249f0c0c755200cc17`；本地HF0.8.216，REA CLI6.8.0。

## REA到底能做什么

活动会话没有REA MCP工具。已运行doctor --client codex --json，exit=1、healthy=false；Codex注册与技能报告config_drift，原生分析引擎缺少。没有修复配置或安装任何引擎。

REA技能适用于软件工件、二进制、JS/Electron和运行行为等逆向问题；已安装CLI命令清单未发现视频拍点、字幕/字效/转场检测、MP4转原工程入口。可以采用“证据→假设→小样→验证→标未知”的逆向方法，但这与实际调用REA不是一回事。

本报告代码审查/CLI帮助/doctor是本地工具能力观察；视频接触表、音频onset、FFmpeg切点统计若由其他工具生成，应以原工具名归档，不得包装成REA Evidence。REA doctor不是视频分析Evidence。

## 当前效果难度排序（不替代逐视频评级）

| 排序 | 效果类别 | 难度 | 原因 |
|---|---|---|---|
| 1 | 硬切卡点、简单文字入场、缩放与闪白 | 低，1–2/5 | 可直接用frames、GSAP、既有模板/转场复现；主要成本在选点与视觉校准。 |
| 2 | 多层冲击字幕、glitch/甩镜组合、几何mask、恒速快慢切换 | 中，2–3/5 | 组件原生可用，需处理层级、声音同步、遮罩边界和参数。 |
| 3 | 人物遮字、干净绿幕、简单运动跟踪、局部稳定 | 中高，3–4/5 | 已有处理路线，但必须检查alpha边缘、时间同步和跟踪漂移。 |
| 4 | 连续速度曲线、复杂光流、遮挡中贴字、头发/透明物精细抠像 | 高，4–5/5 | 当前组件不足以承诺一键高质量，通常需要外部预渲染与人工修整。 |
| 5 | 原剪辑软件/插件/层次与历史工程的唯一恢复 | 不可保证 | 成片信息不可逆且多解；只能做有证据的近似重建。 |

## 原生、预渲染与不可承诺项

### 卡点硬切/重拍锚点 — 1–2/5

**支持方式：** OCC原生；HF/montage可编程；外部拍点适配可无界面。

**复现路线：** 先找音乐重拍、动作入点与句尾，再把切点量化为整数frame；少量强锚点优于每拍都切。

**边界：** 拍点检测不等于正确挑镜头/动作高潮，也不保证自由节奏/变速曲正确。OCC音乐分析/plan/sync在当前headless白名单之外，需编辑器+MCP；HF算点后可经manage_markers/split_item写入。

证据：

- [src/audio/beats.ts:1](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/audio/beats.ts#L1)：spectral flux→自相关BPM→相位grid→4/4重拍启发式
- [src/agent/tools/music-intelligence-tools.ts:182](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/music-intelligence-tools.ts#L182)：cutFrames转换为split actions再batch
- [src/agent/external-tool-policy.ts:50](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/external-tool-policy.ts#L50)：manage_markers/split_item为server-direct白名单；音乐工具不在名单
- C:/Users/PC/.codex/skills/montage/assets/dsh-montage/lib/beat.js:57：按预测点±20%拍长局部对齐onset；beats与细分grid分开
- C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/dist/beats-KSUZ23LE.js:1：本地CLI含beats命令；命令帮助已留存hf-beats-help.txt

### 文字砸入/逐字/描边/弹性/色散重影 — 2–3/5

**支持方式：** HF+GSAP与montage已有可复用实现；OCC有MG/文字/props和关键帧。

**复现路线：** 按字符或词分层，用短时缩放/位移/透明度、错帧和重印层搭出冲击；字体、节奏、声音同时重建。

**边界：** MP4里字已烘焙，不能自动恢复原字体/AE工程/插件参数；OCR/逐帧只能给候选。复杂字形逐笔变形、液体字体需另写SVG/Canvas/Shader或预渲染。

证据：

- C:/Users/PC/.codex/skills/montage/references/workflow.md:97：字块kind: slam/outline/ember/assemble/title等
- C:/Users/PC/.codex/skills/montage/assets/dsh-montage/templates/project/build/gen.mjs:184：slam/outline/ember/assemble真实HTML+GSAP生成代码
- C:/Users/PC/.codex/skills/gsap/SKILL.md:24：ease/stagger与duration、transform aliases
- [src/agent/tools/schemas/core-tools.ts:23](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/schemas/core-tools.ts#L23)：MG模板添加及update_item_props入口

### 缩放冲击/位移/旋转/音量包络 — 1–2/5

**支持方式：** OCC原生关键帧；HF/GSAP原生动画。

**复现路线：** 给item-local frame设置关键帧，先还原主运动路径，再调easing、回弹与hold；音效峰值和视觉落点对齐。

**边界：** OCC通用关键帧不包含playbackRate；不要把变换缓动等同视频时间重映射。HF在其源HTML内可细调，渲染导入OCC后内部动画已烘焙。

证据：

- [src/editor/keyframeRegistry.ts:29](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/editor/keyframeRegistry.ts#L29)：scale/scaleX/scaleY/x/y/rotation/opacity/borderRadius/volume注册
- [src/editor/keyframes.ts:68](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/editor/keyframes.ts#L68)：按左侧关键帧easing采样和边界保持
- C:/Users/PC/.codex/skills/gsap/SKILL.md:40：transform aliases与CSS variables
- C:/Users/PC/.codex/skills/hyperframes/SKILL.md:150：HTML timing attributes与composition模型

### 闪白/甩镜/故障/光学模糊/遮挡式转场 — 2–3/5

**支持方式：** OCC原生GLSL转场；HF CSS/Shader及montage模板。

**复现路线：** 先判定是硬切上叠闪光、真实相机甩动，还是两帧纹理混合，再选转场；只在对应切点重建。

**边界：** “有glitch/whip模板”不能证明与参考同款；曝光/模糊/切点前后素材运动匹配决定效果。参考若明确硬切，应保留其剪辑语法，不机械套通用技能的“每场都转场”约定。

证据：

- [src/gl/transitions.ts:1](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/gl/transitions.ts#L1)：cross-dissolve/flash/whip-pan/radial-blur/glitch等真实shader registry
- C:/Users/PC/.codex/skills/hyperframes/references/transitions.md:91：CSS容器变换与WebGL纹理合成的区别
- C:/Users/PC/.codex/skills/montage/references/workflow.md:119：离线组件/blocks复用入口

### 矩形/圆形柔边遮罩与画幅裁切 — 2–3/5

**支持方式：** OCC原生几何mask；HF CSS clip-path/SVG mask可编程。

**复现路线：** 平面几何揭示可直接用中心/尺寸/羽化/反转；复杂形状遮挡优先HF SVG mask或预渲染alpha。

**边界：** 矩形/圆形mask不是任意路径逐帧rotoscope。尚未核实OCC有通用Bezier遮罩顶点动画/跟踪遮罩精修。

证据：

- [src/gl/fx/shaderEffects.ts:91](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/gl/fx/shaderEffects.ts#L91)：builtin:fx-rect-mask和circle-mask参数中心、尺寸、圆角、羽化、反转
- [src/agent/tools/schemas/edit-item-tools.ts:30](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/schemas/edit-item-tools.ts#L30)：transform.crop/flexCrop裁切像素透明
- C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/svg-mask-reveal/svg-mask-reveal.html:1：已有SVG mask揭示组件，可编辑源实现

### 绿幕/纯色背景抠除 — 2–3/5

**支持方式：** OCC原生chroma-key效果。

**复现路线：** 纯色、干净光照素材用键色/容差/羽化/溢色抑制；把效果作为可调参数保留在OCC。

**边界：** 不是杂乱背景AI抠像；主体服装同色、半透明、毛发与运动模糊可能难处理，需样片检验。

证据：

- [src/gl/fx/shaderEffects.ts:183](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/gl/fx/shaderEffects.ts#L183)：绿幕效果已注册keyColor/similarity/smoothness/spill
- [src/gl/fx/chroma-key.frag:4](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/gl/fx/chroma-key.frag#L4)：YCbCr色距算alpha，并抑制溢色；实际premultiplied-alpha输出

### 人像抠像/人物遮字/前后景分层 — 3–4/5；头发/遮挡/透明物5/5

**支持方式：** HF有本地remove-background预处理；OCC的几何分析分割不是逐帧抠像输出。

**复现路线：** HF生成透明subject.webm或ProRes4444.mov→人物前景/文字/背景三层叠放→逐帧对齐；OCC可以在视频层做外部编排，但本轮没有实测其alpha解码导出，最稳先在HF合成。

**边界：** HF是u2net_human_seg单帧推理，输入320×320，不能承诺复杂毛发/闪烁抑制/运动模糊高质量。quality只控制VP9 CRF；background-output是反alpha挖洞底板，不是AI补出人物后面的完整背景。模型约168MB未缓存，初次运行还可能自动安装sharp/ORT；本轮未运行、未下载。

证据：

- C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/dist/chunk-QETCWXRM.js:104：u2net模型路径、URL与估算内存1500MB（非实测）
- C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/dist/chunk-QETCWXRM.js:155：缺模型时下载约168MB
- C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/dist/chunk-QETCWXRM.js:167：320×320输入，sharp与onnxruntime-node依赖
- C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/dist/chunk-QETCWXRM.js:617：逐RGB帧调用session.process再编码前景/反alpha背景
- C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/dist/chunk-Y65ZU7XY.js:121：缺optional包默认可能调用npm安装
- C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/dist/skills/media-use/audio/references/remove-background.md:18：quality只改编码；分割质量固定
- [src/geometry/mediapipe.ts:198](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/geometry/mediapipe.ts#L198)：OCC把confidence mask降成occ网格并返回face/occ，未导出全分辨率alpha
- [src/geometry/visual-geometry.ts:1](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/geometry/visual-geometry.ts#L1)：几何结果用于safe-zone/构图并缓存

### 贴字跟随/区域运动跟踪/简易稳定 — 3–4/5

**支持方式：** OCC原生浏览器区域模板跟踪；HF可接外部轨迹驱动GSAP。

**复现路线：** 选高纹理、无遮挡的小区域，跟踪后检查漂移；写目标层x/y关键帧，让图形跟随，或反向位移稳定。

**边界：** 360×240灰度、最多150样本，最多2次丢失后停；只证实平移x/y，不是透视平面、3D相机解算、人体关节/自动物体精密跟踪。大旋转、尺度变化、遮挡需人工修。

证据：

- [src/tracking/analyzeMotion.ts:11](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/tracking/analyzeMotion.ts#L11)：分析尺寸与样本上限
- [src/tracking/templateMatch.ts:53](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/tracking/templateMatch.ts#L53)：归一化灰度相关匹配
- [src/tracking/keyframeActions.ts:37](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/tracking/keyframeActions.ts#L37)：follow/stabilize方向；只写x/y关键帧
- [src/agent/tools/schemas/reframe-tools.ts:7](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/schemas/reframe-tools.ts#L7)：自动重构图另是浏览器检测焦点写reframe keyframes

### 恒速/快慢切换/丝滑变速曲线/光流慢放 — 恒速2/5；曲线4/5；复杂光流5/5

**支持方式：** OCC原生恒速0.1–8倍；复杂时间重映射建议外部预渲染。

**复现路线：** 简单快慢切换可以拆片逐段恒速；连续曲线/倒放/补帧需要单独时间映射/FFmpeg滤镜或专用光流工具，经2–3秒样片确认后导入OCC/HF。

**边界：** 未见OCC原生速度关键帧或光流实现。FCPXML speed ramp导入明确近似平均速度；帧率/素材原速未知时，不能从成片唯一恢复原变速曲线。光流尤其怕遮挡、烟雾、水花。

证据：

- [src/editor/rateStretch.ts:7](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/editor/rateStretch.ts#L7)：MIN_RATE=.1 MAX_RATE=8；保持source span按恒速重算duration
- [src/editor/clipTypes.ts:198](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/editor/clipTypes.ts#L198)：playbackRate是scalar
- [src/agent/tools/timeline-import-fcpxml-timing.ts:133](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/timeline-import-fcpxml-timing.ts#L133)：注释与localToParent把非线性ramp近似平均速度
- [src/agent/tools/timeline-import-fcpxml-walk.ts:252](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/timeline-import-fcpxml-walk.ts#L252)：明确warning: speed ramp approximated by its average speed
- [src/editor/keyframeRegistry.ts:29](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/editor/keyframeRegistry.ts#L29)：通用关键帧注册没有speed/rate

### 保留可改工程/无界面批量导出 — 2–3/5

**支持方式：** OCC ProjectDoc/CLI原生；HF HTML原生，但二者无原生HTML互导证据。

**复现路线：** OCC负责媒体编排与外层调整，HF负责复杂字效/图形/合成；交换视频/音频、拍点JSON/镜头表。用CLI --dry-run检查计划再render。

**边界：** HF渲染视频入OCC后只保留外层裁切/位置/效果，内部DOM/文字/GSAP要回HF改。EDL/FCPXML导入会丢title/caption/transition/effect；不能承诺跨工具无损还原。montage baked稳定但镜头已合成，editable模式多镜头较慢。

证据：

- [cli/commands/render.ts:1](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/commands/render.ts#L1)：不需用户打开浏览器，使用server导出和Remotion pipeline
- [cli/commands/tools.ts:1](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/commands/tools.ts#L1)：只允许headless白名单tools
- [src/agent/tools/schemas/timeline-import-tools.ts:11](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/schemas/timeline-import-tools.ts#L11)：明确列出交换导入跳过要素
- [src/export/artifactExportOperations.ts:121](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/export/artifactExportOperations.ts#L121)：导出MG可以渲染成媒体引用
- C:/Users/PC/.codex/skills/montage/references/workflow.md:162：baked和editable模式边界
- C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/dist/skills/media-use/audio/references/remove-background.md:5：透明WebM/MOV用于分层交换

### 从成片反推原工程/原软件/原插件 — 不能承诺；仅候选重建

**支持方式：** 现有工具能重建视觉规律，不能唯一恢复历史制作过程。

**复现路线：** 按时间码记录观察→列可能实现→做最小复现→并排对照→保留未知。剪点/字体/转场/抠像属于多解问题，区分“看见了”与“猜测制作方式”。

**边界：** 同一MP4可由多种软件/模板/插件产生；没有原工程和素材，就不能保证层次、速度曲线、字体/插件版本完全正确。REA也没有宣称本地MP4自动反求剪辑工程。

证据：

- C:/Users/PC/.codex/skills/reverse-engineer-anything/SKILL.md:16：普通完整源码分析用普通工具，REA适用于发布工件/运行证据等问题
- C:/Users/PC/.codex/skills/reverse-engineer-anything/references/connection-and-recovery.md:48：普通shell观察须标为shell；只有真实REA输出才是REA Evidence

## 推荐复现顺序

1. 用FFmpeg/音频onset与人工逐帧定位剪点、冲击点、转场区间，单列“观察事实”和“制作方式猜测”。
2. 在OCC还原最小镜头顺序、画幅与音乐，先检查节奏，不急着堆特效。
3. 将复杂文字/遮罩/图层留在HF源HTML中制作，GSAP用确定性时间线；输出时与OCC统一fps。
4. 绿幕先用OCC原生chroma-key；非绿幕人物遮字可尝试HF本地remove-background预处理，但模型当前未缓存，需另行进行实际推理验收。
5. 曲线变速/复杂跟踪先做2–3秒独立样片，必要时外部工具预渲染，不承诺当前OCC原生无损承接。
6. 检查t-2帧到t+2帧、alpha边缘、字的可读性、动作方向、音乐落点与音画同步，再扩大到全片。

技能不是“已运行效果”的证据。montage的baked模式稳定但镜头烘焙成picture.mp4；editable保留逐镜HTML却可能更慢。HF成片导入OCC之后，只能编辑其外层片段，内部文字/图层要回HF修改后重渲染。

## 可复现的纯本地分析命令（本轮未对素材运行）

```powershell
$node = 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
$hf = 'C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/bin/hyperframes.mjs'
& $node $hf audio "D:/your-video.mp4" --quality fast --only onsets,loudness,silence,envelope --json
# best会上传到HeyGen并可能计费；本任务不要用best。
& $node $hf beats "D:/your-hf-project" --json
& $node $hf check "D:/your-hf-project"
& $node $hf snapshot --help
```

remove-background虽是本地推理，首次会下载模型并可能安装optional dependencies；本轮只读取帮助与代码，没有执行。其--quality只影响编码CRF，不升级抠像模型，也不会把有洞的反alpha底板补成完整背景。

原始帮助留存：rea-help.txt、hf-help.txt、hf-remove-background-help.txt、hf-beats-help.txt、hf-audio-help.txt、hf-render-help.txt。doctor原始输出不建议直接公开；已在JSON中保留不含配置内容的name/ok/classification摘要。
