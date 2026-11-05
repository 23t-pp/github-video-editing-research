# V11–V15视觉审查方法（影像就绪前的准备）

范围：只审V11–V15画面，不写音频结论、不改GitHub、不改既有编辑工程。标题只用于索引，不作为效果证据。

1. 从manifest取得文件身份、长度、尺寸与源帧率；从frame-analysis取得检测方法与候选时间，检测器只辅助定位。
2. 实际查看overview与全部timeline分页，记录画面、字幕、构图、接镜方向和章节。每段覆盖连续范围，明确章节边界与逐帧切点不是同一概念。
3. 按用户更正，对短转场查看原生帧率atlas，每页60个原帧，不强制60Hz、不复制、不插值。VFR以每帧原始PTS为时间依据；必要时请求/制作小窗口原生帧接触表，不把一页60帧误写成源视频60fps。
4. 同时区分观察、实现建议、未知归属：人物动作和原片CG不能自动归为混剪新增；不认定AI抠像或特定AE插件。
5. 以手法→素材条件组织：同方向/同相位动作、相似圆形/线条、光照/色域、可分离前景、稳定镜头、足够边缘信息。写明缺原片/alpha/跟踪的具体位置。
6. 每片给最适合新手的一个小样；不从未运行的建议推导“可直接自动高质量”。原生OCC用于帧级切镜/基础变换，HF/GSAP用于文字和显式图层动画；复杂动态mask和光流仍要另作预处理验证。

输出兼容旧reviews.json：id/title/difficulty/starter/summary/segments；segments保留start/end/label/observed/recipe/confidence/evidence。补充techniques、suitable_materials、implementation、unknowns、sampling与actual_viewed_evidence。证据路径相对于outputs/reference-library-20261105，报告不携带原视频或密钥。

难度：1=基本切镜/单文字；2=明确参数的几何/简单关键帧；3=多层/动作筛选/手动校准；4=动态遮挡/复杂合成与大量素材检索；5=原片级CG/精细抠像/不可唯一恢复。难度与视觉华丽程度不是同一指标。

交付前核对：5条齐全，时间段从0覆盖到manifest终点；所有evidence实际存在且已看；区分整段章节和经密帧核实的边界；每条都有字幕/构图/转场/动作匹配说明、素材条件、能力与未知项。绝不宣称看完每一帧或实际试听。
