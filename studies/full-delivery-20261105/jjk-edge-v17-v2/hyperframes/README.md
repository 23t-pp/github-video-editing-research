# 《挚友 · EDGE》精修V2 · HyperFrames工程

本工程1920×1080、24fps、1440帧、60秒，音乐保持edge原曲147–207秒。最新方向是效果与流畅度优先，允许超出V17/V02，增加动态抠像、排版、连续曲面字、细撕边、电弧和纤维。参考结构与原创延伸写在`edit.json`的`layouts[].origin`，没有把所有新增技法声称来自参考。

先读上一级[学习总结与命令](../学习总结与命令.md)，其中有适用素材、难度顺序、alpha限制、全部20段渲染表和声明覆盖解释。最终影片名`挚友_EDGE_精修V2.mp4`；最终UI、工程包和QA结果由主入口及单独核验记录说明。

## 本机打开

PowerShell：

```powershell
$jjkProject = 'D:/gpt/2026-11-04/ps-c-windows-system32-winget-install-2/outputs/jjk-edge-v17-v2/hyperframes'
$jjkCache = 'D:/gpt/2026-11-04/ps-c-windows-system32-winget-install-2/work/jjk-edge-v17-v2/render'
$jjkPy = 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$jjkNode = 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
& $jjkPy -X utf8 "$jjkProject/composition.py"
& $jjkNode "$jjkProject/hf.mjs" lint .
& $jjkNode "$jjkProject/hf.mjs" preview . --port 5240 --no-open
```

打开[Studio 5240](http://127.0.0.1:5240)，服务已运行时直接访问。最终成片播放器使用[5241](http://127.0.0.1:5241)，由主README提供入口与启动说明。`hf.mjs`将子进程工作目录设为本工程，并使用本机安装的HyperFrames、Chrome与FFmpeg；换电脑需适配其路径或环境变量。

## 修改入口

|文件或目录|作用|
|---|---|
|`edit.json`|67镜、16个前景事件、14个布局、8次字效、音轨与闪光；帧号全局24fps、结束不包含|
|`composition.py`|素材时钟、图层顺序、前景残影、镜片与基础合成；生成`index.html`|
|`layoutfx.py`|景深窗、三连胶片、七叶、扩窗、双眼竖缝、细撕边及电弧/纤维|
|`typefx.py`与`barlow-glyphs.json`|窄高SVG字、9层挤出、高光、双排、连续柱面/圆环；两文件必须同目录|
|`assets/alpha/`|7组逐帧真实前景；文件号是prepared素材fileF，不从0重新编号|
|`assets/shots/`|prepared短片段及前后余量，OCC原生镜头引用这些素材|
|`assets/audio/master.wav`|固定60秒master，最终编码接入，短HF插片无声|
|`motion/lens-keyframes.json`|对应原镜片的人工圆心和半径，不是任意镜片自动跟踪器|
|`render.py`|20个72帧chunk、PNG抓取、缓存、HF插片与总片编码|

改JSON/Python后运行`composition.py`。Studio手改的旧HTML会在下次生成时备份到`.source-backups/*.html.bak`，不会自动合并回JSON；长期修改请写回源码。

## 文字、撕边和alpha的边界

大字事件为F15–48 THE STRONGEST、F120–156双人姓名、F432–456 BEYOND、F669–717 THE STRONGEST/AWAKEN、**F840–864 NO LIMIT**、F966–996 GETO SUGURU、F1098–1134 PURPLE、F1200–1224 EDGE。前景通常z60，大字z45，布局z10–35。

`slam/twin`保留SVG text，`cylinder/ribbon/orbit`将原Barlow glyph轮廓逐点映射为连续SVG path，没有用一整块rotationY冒充弯曲。主字应改`edit.json.text`再生成；直接改defs里的隐藏文字不会重建路径。曲面模式支持已采样的大写英文、数字和常见标点，小中文用`subtitle`。Studio可能只将整组识别为group而非可直接打字的文字框，应使用JSON或子SVG源码入口。`font_size/width`分别控制字高/字宽，`x/y/scale_x/scale_y`控制构图，`pulse=False`关闭有限回弹，新增中文先查字体子集覆盖。

撕边的素材遮罩、纸纤维和能量路径共享同一不规则边界；`edgeFx`实际生成紫青光、白核心、移动电弧和纤维粒子，由CLI渲染。F451–480的`energy-paper`、F864–888的`blue-tear`分别示范细人物条和扩幅接镜。先改几何与展开时间，再调`edgeFx.strength/particles/arcSpeed`。原片本来的术式和破玻璃不是本工程新增CG。

新增alpha范围：Y-hurt `[12,60)`、Y-geto `[12,48)`、Y-blue `[12,23)`但优选`[12,20)`、Y-getopalm `[38,51)`、Y-stand `[12,36)`，另保留X-awaken/X-palm。详见上级`evidence/alpha/动态抠像可用帧范围.json`。prepared有效画面为y108–971；冠顶/下颌、制服底沿、手腕/指尖都有原生截断，alpha不能恢复。Y-stand是红夕阳夏油，原人物高约390px；Y-getopalm前30帧无手，不应把offset改12；Y-blue末段与白发接触仍有同色残留。用排版接住截断，不把不完整身体移到空白中心。

## 再渲染与局部更新

```powershell
& $jjkPy -X utf8 "$jjkProject/render.py" --work $jjkCache
```

全片20段，每段72帧/3秒，chunk编号0–19，完整表见上级学习文档。chunk11为F792–864，chunk12为F864–936，chunk15为F1080–1152。真实CLI输出PNG，预览视频与离线源帧共用几何；跨段从全局elapsed恢复，素材时钟不从头重播。

只改NO LIMIT及其后的蓝色撕边，可在已有完整缓存时：

```powershell
& $jjkPy -X utf8 "$jjkProject/render.py" --work $jjkCache --chunks 11 12
& $jjkPy -X utf8 "$jjkProject/render.py" --work $jjkCache --encode-only
```

`--encode-only`要求同一缓存已有1440张主帧，不会替你重渲过期帧；第一次执行完整命令。跨多个chunk的改变要重渲所有受影响段；`--force`强制忽略缓存。主帧`frame_000001.png`对应全局F0。

输出为上一级`挚友_EDGE_精修V2.mp4`、上一级`occ-effects/HF-0000-0072.mp4`至`HF-1368-1440.mp4`，及缓存的`master-frames`与日志。脚本用二进制管道保存FFmpeg输出，不要改用PowerShell文本重定向。

普通修改/导出只用Python标准库、Node、现有HyperFrames、FFmpeg和Chrome。重新抠像另需OpenCV/NumPy，重新采样字体另需fontTools；完成的alpha和glyph字库已在工程内。

## 与OCC交换及证据范围

OCC原生序列提供67个独立镜头、8个小中文标签和音乐轨；复杂字形、alpha、纸边、空间动画保留在本工程。OCC的20段HF序列是完整合成插片，内部图层不能在那里拆开；修改本工程后重渲并替换。两边不会自动同步，原生镜头改变需同步到`edit.json`。

`evidence/附加层覆盖计划.json`记录布局16.041667秒、前景20.75秒、大字10.625秒，合并34.5秒/57.5%，仅是**声明覆盖**，不是实际可见或质量通过结论。7组alpha复用成16次前景，不等于16种原动作。

master为48kHz、2,880,000个采样帧/60秒；147–207秒与1440/24的帧边界量化差0。选段和切点依据能量/起音测量，没有实际听觉试听。文字独立短样和alpha局部证据在上级evidence中，不能代替最终整片UI、OCC导出或声画QA；最终检查范围请读主交付记录。
