# 本地模板与 Skill 适配核查

优先复用的是卡片的错时入场、文字的短 RGB 抖动、几何窗口和转场的时序机制。参考片里的动态人物边缘、指缝、轮辐遮挡，需要另外准备遮罩；这 8 项里没有自动恢复这些边缘的模板。

本次逐项读取了本机 `registry-item.json`、核心 HTML，以及存在的 README；只读审查，未安装、运行、渲染或修改技能/应用。以下是**等效实现的适配建议，不是查明了参考片作者使用的原模板**。参考时间沿用[逐片拆解](逐片拆解.md)。本地源码路径可点击，行号为本次文件中的一基行号。

“能直接改”指保留组件机制、修改文字/样式/时序后可进入小样制作，不表示已经渲染通过；“需改结构”指必须改媒体输入、分层或动画机制；“不适合”指不能拿它充当该局部的主要实现。

| 本地项 | 判定 | 对应参考片的局部 | 主要差距 |
|---|---|---|---|
| grid-card-assemble | **需改结构** | V05 1.7–2.3秒六格拼图、2.9–3.5秒中心拼图；V01/V08照片墙 | 默认是图标文字能力卡，不是同一视频切成六块 |
| split-tilt-cards | **能直接改：双卡原型；精确复刻需改结构** | V04 9.6–11.65秒倾斜电影卡片；V01开场照片卡 | 原机制仅两张对称卡、固定Y轴倾角；参考有不同卡数、平面斜转和人物前景 |
| rgb-glitch-text | **能直接改：标题文字局部** | V05 0–1.5秒标题故障；V04 5.9–9.6秒中新增的小字故障 | 只偏移文字副本，不处理整段视频的RGB边缘 |
| caption-glitch-rgb | **需改结构：精确版式** | V05 14.3–15.3秒中央字条的短故障；V08 0–7.2秒对白条仅能借用时间数据组织 | 默认是底部逐词英文字幕+扫描线，不是中央条牌或黑字白条 |
| outline-draw | **不适合：人物/车身描边** | V01 6.7–11.8秒白剪影、V02 5.6–7秒红轮廓、V10 0–6.4秒车身亮边 | 实际是圆角矩形边框绘制，没有人物/车边识别 |
| grid-pixelate-wipe | **能直接改：纯色方格过门；不适合直接当视频拼图** | 可做V05六格段前后的自选过门；V09 1.5–3.5秒像素感仅属外观近似 | 方格填纯色，不是视频像素化采样，也不是六路素材拼接 |
| vfx-portal | **需大改结构：圆窗；不适合自动手指抠像** | V01 20.6–26.8秒圆形揭示的机制参考；V10 6.4–10.8秒只能借圆形部分 | 实际是网页面板的WebGL圆孔穿越；没有手/指缝/车标/轮辐跟踪 |
| chromatic-radial-split | **需大改结构：视频输入** | V04 5.9–9.6秒局部RGB边缘、V05开场的短色散；不是V06动作接镜的必需品 | 自带演示板和静态纹理捕获，不能只换视频路径就当通用视频转场 |

## 1. grid-card-assemble：可借错时与网格，不会自动切好六格视频

[元数据](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/grid-card-assemble/registry-item.json:6)声明能力卡网格/列表，并提供 `items`、`columns`、`cues` 等变量。[核心HTML第267行](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/grid-card-assemble/grid-card-assemble.html:267)确实检查 `data-slot="items"` 的现有子节点：已有节点就直接动画，不再自动生成图标文字卡。第316行起计算列数；第402行起解析每卡相对入场秒数；第415行起做透明度与短距离向上滑动。最终卡片保持静止，不是飞散、旋转碎片。[README](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/grid-card-assemble/README.md:32)也说明需要在组件模板内部写自定义卡内容。

适配 V05 时可保留网格和 `cues`，将内容改成两行三列的裁切窗口，去掉卡面、图标、文字、圆角和间隙。**六格要共享同一B镜头、同一播放时间，但每格显示不同空间区域**；六格各自 `object-fit:cover` 播完整画面，会得到六份重复人物，不是完整画面拼图。V05约0.6秒的组合很短，默认每卡0.65秒的落位也要重写，不能只填一个更短总时长就认为节奏一致。照片墙则需每卡独立照片与不同角度，不应保留产品功能卡外观。

## 2. split-tilt-cards：已有媒体槽，但只有两张比较卡

[元数据](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/split-tilt-cards/registry-item.json:6)是两张等权卡从左右进入；[核心HTML第16行](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/split-tilt-cards/split-tilt-cards.html:16)列出 `card-a`、`card-b` 两个内容槽，第235行起直接支持 `img/video` 覆盖槽面。[README](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/split-tilt-cards/README.md:50)要求改**组件副本内部槽子节点**，不是把子节点随意放到宿主clip上。

双卡练习可以直接换两张剧照、清空 `label_a/b` 与 `badge_a/b`，修改卡面背景。要贴近V04则还需加入独立人物alpha层、平面 `rotation`、非对称位置与出入场；原模板左右分别固定 `rotateY(18deg/-18deg)`，入场移动的主要是x、scale、opacity（[第473行](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/split-tilt-cards/split-tilt-cards.html:473)），不是每张卡任意翻转。默认入场包络2.15秒，对不到1秒的小卡段须改时序。HTML槽支持video不等于已经验证多视频在HyperFrames中逐帧同步，仍需小样检查。

## 3. rgb-glitch-text：最适合先练的短字效

[元数据](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/rgb-glitch-text/registry-item.json:15)有 `text/intensity/tone`；[核心HTML第34行](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/rgb-glitch-text/rgb-glitch-text.html:34)实际是两个span加一个strong，同一文字三份叠放。第56行起红/青副本左右偏移，第79行把强度映射为0.5/1/2.25，第109行给出 paused GSAP 时间线接法。

V05开头只复刻标题时，可直接换中文、字体、字号、位置及持续时间，再把抖动窗口对齐确认后的起音。示例是8px偏移、0.06秒往复，不是参考片恢复参数。该文件的时间线接法在**注释示例**中，需要接入宿主时间线，复制文件后不会自动卡点。它也不会给人物、背景或整个视频分离RGB通道；要做V04全画面边缘故障，需另写媒体层/着色器。

## 4. caption-glitch-rgb：逐词时间机制可用，默认画面不是中央条牌

[元数据](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/caption-glitch-rgb/registry-item.json:6)写RGB和CRT扫描线，但没有暴露一组文案变量。[核心HTML第116行](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/caption-glitch-rgb/caption-glitch-rgb.html:116)是硬编码 `TRANSCRIPT=[{text,start,end},…]`；第170行按词数/标点/间隔分组，第262行起给文字x与红青text-shadow动画。它不是自动识别语音、自动生成字幕或自动检测拍点。

若做V05中央字条，需把底部120px定位改成脸部附近，添加条牌底板，改字号和分组，并减少/关闭全屏渐暗与扫描线。若做V08黑字白条，RGB阴影未必符合参考，应该保留词时间数据而换掉外观。默认英文长词判断使用 `/[^\w]/`（[第198行](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/caption-glitch-rgb/caption-glitch-rgb.html:198)），中文不能沿用它判断“长词后震”；需要中文分句与自定强调词。

## 5. outline-draw：圆角矩形框，不是人物轮廓

[元数据](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/outline-draw/registry-item.json:6)明确写 rounded outline。核心[第80行](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/outline-draw/outline-draw.html:80)用 `border-radius`、`conic-gradient` 与 padding-box/border-box 的 `mask-composite:exclude` 留出空心矩形中心；[第162行](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/outline-draw/outline-draw.html:162)只动画绘制进度和透明度。公开参数只有进度、粗细、圆角。

它可直接用于**学习讲解时框出画面区域**，或给照片卡加绘制边框；不能拿来做V01/V08人物白剪影、V02人物红描边、V10车身发光。那些局部需要人物alpha/车辆路径：从alpha扩张减原alpha得到边缘，再着色/模糊，或者手工画路径。把圆角调小不会使矩形贴合人体，也不含追踪功能。

## 6. grid-pixelate-wipe：纯色方格遮挡，不是视频马赛克

[元数据](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/grid-pixelate-wipe/registry-item.json:6)描述方格过门。[核心HTML第30行](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/components/grid-pixelate-wipe/grid-pixelate-wipe.html:30)给方格统一黑色，第42行固定16×9，创建的是空div；第58行以后的动画只是注释示例：方格scale覆盖→切A/B可见性→方格缩小揭示。

把COLS/ROWS改成3×2并不会自动得到V05六格视频，只会得到六块纯色。可直接用作自己设计的纯色像素过门，或抽取 stagger 顺序作为V05改造时的参考；若追求V09的素材像素化，需要对视频采样、降分辨率/最近邻放大或着色器量化。也没有证据表明参考片实际使用了该转场。遮屏盖满的时刻要重新计算：示例单格0.6秒加总stagger0.6秒，不能仅凭注释里的3.6秒就认定全屏已盖住。

## 7. vfx-portal：网页明暗面板的圆孔，不是自动rotoscope

[元数据](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/blocks/vfx-portal/registry-item.json:7)标为experimental、1920×1080、10秒。实际HTML大量内容是演示网页light/dark面板；[第487行](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/blocks/vfx-portal/vfx-portal.html:487)通过 `drawElementImage` 把面板捕获到canvas，转换成Three.js纹理。第455行检查 `layoutSubtree/drawElementImage`，不支持就显示错误层，**不是已经证明本机浏览器能运行**。

圆孔确实存在：[第537行](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/blocks/vfx-portal/vfx-portal.html:537)有中心、半径、边宽、发光颜色；[第586行](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/blocks/vfx-portal/vfx-portal.html:586)按到中心的距离制作圆形mask，并加噪声边缘、色散、火花。它可为V01胸口/脸部圆窗提供机制参考，但要替换网页纹理输入、改圆心、去掉不需要的能量环，并缩短10秒叙事。仅复现干净圆窗，用普通圆mask通常比改这个实验演示更直接。

**不能用它宣称已支持V03/V07手指rotoscope。** 指缝随手势变化需要独立动态路径/alpha和前景手层；模板没有手指分割、关键点跟踪或逐帧轮廓接口。V10车标透视和轮辐前后关系也要另加层。元数据虽列 `--bg-color/--portal-color`，当前HTML没有发现读取这两个CSS参数或 `getVariables()` 的实现，而颜色在shader uniforms内设定；因此不承诺改registry参数就能换实际发光色。

## 8. chromatic-radial-split：有真实RGB着色器，但视频输入要重写

[元数据](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/blocks/chromatic-radial-split/registry-item.json:6)声明径向RGB转场；[核心HTML第150行](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/blocks/chromatic-radial-split/chromatic-radial-split.html:150)实际是左侧1200×1080演示区、右侧说明板，并非全屏通用媒体转场。[第213行](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/blocks/chromatic-radial-split/chromatic-radial-split.html:213)的捕获函数只画背景矩形与文字，没有把img/video绘进纹理；第335行只在初始化捕获A/B一次。

[第309行](C:/Users/PC/.codex/skills/montage/assets/dsh-montage/registry/blocks/chromatic-radial-split/chromatic-radial-split.html:309)的fragment shader确实分别取RGB通道、沿径向偏移，再混合A/B。可抽出这段用于V04/V05短色散过门；但要改成全画幅、删除说明板，按时间更新视频纹理并管理两段媒体的seek/播放同步，重设1–3秒的默认转场区间。单改 `SCENE A/B` 为视频标签仍会留下静态捕获问题。V06旋转枪的关键是动作硬切，不必为它强加这种色散。

## Skill如何组合，下一步只做小样

- **montage**：管理镜头表、实际拍点与组件图层；这些模板自身不分析音乐。把确认的音频事件换成组件相对秒数，或自行写GSAP时点，不能把演示默认cascade叫“自动卡点”。
- **hyperframes / gsap**：负责媒体层、mask与paused时间线；修改项目副本，不改技能库原件。参考V06为24fps，模板常带30fps或无帧率；时点要按当前工程帧率重新量化。
- **hyperframes-registry / hyperframes-cli**：实际安装、校验、预览与渲染阶段再使用。这里仅做本地文件核查，没有执行 `add` 或任何安装命令。
- **OpenChatCut**：先选动作段与切镜，HF完成必要的图层合成后作为媒体回填。渲染MP4并不会让HTML内部文字、遮罩、卡片自动变成OCC原生可编辑层。

建议练习顺序：V05短标题RGB字效 → V04双卡原型 → V05六格视频窗口 → V01单个圆窗。人物、手指、轮辐遮挡单独立项；先准备合格alpha，再谈门户效果。源码里多处仍引用CDN上的GSAP/Three.js或Google Fonts（例如portal第7–12行、caption第7–13行）；本次没有联网加载或验证离线依赖，不能将“文件在本机”等同于“开箱即离线可渲染”。
