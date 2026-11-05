# V07 转场迁移：本机可用能力（2026-11-05）

本次新片按库内 V07 BGM 的实际长度制作，参考视频为25fps、751原生帧、30.04秒；不沿用固定60秒。此文件审查工具与具体可行路线，没有创建OCC工程、修改旧fast60、下载分割模型或修改全局环境。

## 可立即使用的工具

| 工具 | 实测状态 | 用途与边界 |
|---|---|---|
| `C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe` | 9.0.2，实际合成图 `geq` 和 `maskedmerge` 冒烟运行 exit0 | 已有 `alphamerge/alphaextract/geq/gblur/dilation/erosion/maskedmerge/maskfun/perspective/zoompan/displace/remap/minterpolate/vidstabdetect/vidstabtransform/chromakey/colorkey`。可做帧准确解码、亮区蒙版、几何窗、alpha合成。 |
| `C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` | 3.12.14；NumPy2.3.5、Pillow13.0.0可实际导入 | 适合多边形栅格、轮廓关键帧插值、羽化、证据联图。默认 PATH 的 `python.exe` 是 WindowsApps入口，不作可靠运行器。 |
| 本任务 `work/reference-replay-v07/python-deps` | 主流程刚隔离安装 `opencv-python-headless 5.0.0.93`；子代理实际导入得到 `cv2 5.0.0` | `calcOpticalFlowPyrLK`、`calcOpticalFlowFarneback`、`grabCut`、`estimateAffinePartial2D` 均真实存在。此前两个Python环境均没有cv2，现已补齐。无需大模型。 |
| `work/reference-library-20261105/audio-env/Scripts/python.exe` | 3.12.14；find_spec检出Torch、Torchvision、SciPy、ORT、NumPy、Pillow、PyYAML | Torch/Torchvision导入先于ORT没有报错，但组合导入在ORT处因DLL缺失失败，故不能把“包存在”写成所有推理后端可运行。已有 `models/UVR_MDXNET_KARA_2.onnx` 是音源分离模型，不是视频分割模型。 |
| `C:/Users/PC/Apps/hyperframes/node_modules/hyperframes/bin/hyperframes.mjs` | 现有HF0.8.216；既有工程已有精确裁切/clip-path/GSAP制作经验 | 可以按帧驱动SVG/Canvas多点遮罩和圆形门户；HTML中能编辑，但烘成MP4再进OCC后内部遮罩不可直接改。 |
| OpenChatCut本机源码/服务 | 已验证独立视频轨、文字、裁切、变换关键帧、音量、官方完整媒体工程包 | 普通关键帧支持x/y/scale/rotation/opacity等；不能据此假称存在任意逐帧贝塞尔轮廓编辑。复杂轮廓应作为短alpha层，底层镜头仍独立可剪。 |

OpenCV隔离导入，不用修改全局PATH或原venv：

```powershell
$py = 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -c "import sys;sys.path.insert(0,r'D:/gpt/2026-11-04/ps-c-windows-system32-winget-install-2/work/reference-replay-v07/python-deps');import cv2;print(cv2.__version__)"
```

## 自动抠像缓存结论

HF源码 `dist/chunk-QETCWXRM.js` 的默认模型明确为 **`u2net_human_seg`**，缓存路径为：

`C:/Users/PC/.cache/hyperframes/background-removal/models/u2net_human_seg.onnx`

该文件实测不存在。HF安装根不能resolve `onnxruntime-node`；OCC安装根可以resolve，但不等于HF已自动接通它。Python audio-env 的ORT实际import又遇DLL错误。未执行remove-background，以免其隐式安装optional依赖或下载权重。这个模型还是人像分割，不能承诺车轮/汽车精细分离。SAM2、rembg、MediaPipe、Ultralytics在已查的两套Python环境均未发现。

**本轮选用OpenCV短窗口手工轮廓/GrabCut辅助，而不是等待或下载大模型。** GrabCut是前景/背景颜色分布划分，没有“识别手”的语义；必须限制在手工轮廓附近，并逐帧看运动模糊和指缝。

## V07实际关键画面及迁移路线

本次实际查看了V07 overview、两张旧高密图，以及原生帧图 `native-003.jpg`（F120–179）与 `native-012.jpg`（F660–719）。旧高密图是10fps近似采样，精确帧定位以25fps原生图为准。没有谎称人工逐张看完751帧。

| 参考证据 | 可确认的机制 | 迁移到汽车素材的具体做法 |
|---|---|---|
| F154约6.16秒新手臂已覆盖旧蓝剑；F164–166约6.56–6.64秒底图换成新场景 | **来镜真实前景先入，遮挡最大时换底**。不是只给A/B加闪白。 | 选择拨挡/按氮气按钮/握方向盘的B镜。A在底；B的真实手/前臂短alpha提前约8–12帧入；手覆盖切口最大时切到B全镜。alpha与B全镜必须同一源帧时钟，不能“隐藏时已走了几帧”。先做最清楚的一处，确认后扩两处。 |
| 约9.5–11秒金手、浅色手接力；16–17秒手腕旋转跨背景（既有逐段报告） | 动态形变轮廓，含指缝、真实转腕 | 首选6–20帧短窗口，每2–4帧手工多点轮廓，必要时每帧修正。LK只辅助估计短程局部运动，不能在遮挡后强行续追。轮廓和运动模糊来自真实B，不生成新手。 |
| 约12–14秒眼睛/瞳孔中心与强光；26秒前后圆形纹样 | 圆心、尺度、亮度作形状桥；是否作者加电光未知 | 以轮毂/车灯/仪表圆面替代眼睛/圆盘。先匹配圆心与相对直径，再短尺度拉远到车身；圆形/椭圆遮罩可用Pillow/OpenCV直接生成。椭圆窗只是门户，不宣称切出了整台车。 |
| F667约26.68秒指缝可见下一人物，F675约27.00秒变全幅 | **小窗内先出现B，窗扩大，同时A外侧手指仍挡在前面** | 用方向盘内孔、车窗、轮毂孔作真实边界；A完整片为底，B缩放/位置匹配后用动态多边形窗露出，A的前景边框/手alpha置顶。窗铺满才切B全幅。须让B画面在门户内与全幅切换时人物/车不跳位。 |
| 约5.12秒蓝色剑光斜线；强光过门 | 明亮线条遮住连接，光束本体可能来自源动画 | 用车灯扫光、反光车身边缘、氮气火焰或隧道亮带；阈值亮度必须再乘手工ROI，防止天空和皮肤全被选中。只把切口附近的亮带扩张/羽化，不能靠全屏白闪代替前景关系。 |

## 传统跟踪可用，但需要的质检

当前隔离OpenCV已使 **Pyramidal LK + 前后向一致性检查 + RANSAC仿射** 成为可运行路线。先在手工前景内部取特征点，估计相邻帧局部变换传播轮廓；每个手工关键帧重新锚定，跨镜头、快速失焦、出画、指尖形变时停止自动传播。没有足够内点或前后误差过大就回退到手工插值/逐帧轮廓。

Farneback可生成稠密流用于短程mask传播，但光流在手指之间、反光轮胎、运动模糊和遮挡新露区域会失真。它既不识别主体，也不保证指尖边缘。OpenCV现有headless主包不应假设带contrib的CSRT/KCF；本轮无需这些tracker。

FFmpeg `minterpolate` 是运动估计插帧滤镜，**不是**输出可编辑多边形或点轨迹的跟踪器；本片保持25fps，不将插帧当跟踪。`vidstab`主要稳定全局相机，不等同手部区域跟踪。

## 只烘焙必要部分，OCC保留哪些层

1. **V1**：A/B各原始短镜头，独立素材、入点和剪点；正常镜头不烘成一整条。
2. **V2**：门户内B画面。简单缩放/位移尽量保留OCC关键帧；复杂动态窗可短窗口预合成，需保留外部JSON轮廓与源片ID。
3. **V3**：来自真实B的手/车身/轮廓短alpha，必要时烘为PNG序列或VP9-alpha WebM；这层仍可在OCC单独移位/替换。普通MP4没有alpha，不能假称透明。
4. **V4**：少量光束/边缘遮盖；能几何生成就留源参数。复杂光束与背景作用确实不可拆时，只烘8–20帧过门并保留旁边原片，不把全片烘焙。
5. 音乐沿V07库内BGM长度；不要为了硬凑60秒循环。原片声音与BGM分轨。

alpha交付优先 **全分辨率RGBA PNG序列 + 每帧源帧索引/PTS JSON + 黑白alpha/灰底合成证据**。OCC一般不能直接把PNG序列当一条时间线视频；后续应编码透明WebM或官方可用透明MOV代理后再导入，必须实际检查alpha解码，保留PNG作为无损源。

## 已有技能/模板的真实边界

- montage：本地入口 `C:/Users/PC/.codex/skills/montage/scripts/montage.mjs`。离线组件 `registry/components/chromatic-aberration-wipe` 是通用滑动/RGB分离，不是V07的真实手部遮挡；`colorama-wipe` 实际为文字擦出，也不能冒充汽车转场抠像。
- HF/GSAP：可手写SVG/Canvas mask和确定性时间线；跟踪数据仍需OpenCV/人工输入。优先用最少可编辑参数，不套无关字幕模板。
- REA：技能自己明确面向软件工件。这里仅采用“观察/假设/未知”证据边界，未对MP4运行REA反编译，也不把普通FFmpeg输出叫REA证据。

原始工具探测在 `tool-probe.json`、`ffmpeg-filters.txt`；该JSON记录的是OpenCV隔离安装之前的第一轮，安装后的cv2导入结果见本报告及后续alpha工具运行记录。
