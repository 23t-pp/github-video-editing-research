> 返回[研究首页](../README.md) · 先读[桌面源码第一课](12-openchatcut-first-lesson.md)。这是源码层可行性核查与未执行的接线示例，尚未完成本机集成。

推荐职责：HyperFrames继续承担已有复杂视觉与动效；OpenChatCut增加可编辑时间线、人工精修与自动化入口；FFmpeg处理预处理、转码和帧数核验。首先验证渲染片段与拍点交换，再评估保留更多内部结构。
# OpenChatCut × HyperFrames / FFmpeg 集成接口补核

审查快照：`7fa4b7903e7ebecf832a36249f0c0c755200cc17`。只读代码，没有安装、启动或跑剪辑；桌面源码7个关键接口文件与该快照文本一致。

**可以组合做复杂卡点混剪，但需要一个很薄的文件/时间线适配层；不是现成的HF HTML原生互通。** 最容易落地的是HF渲染复杂镜头与字效、FFmpeg处理媒体、把视频和音轨导入OCC继续排布。若要无界面卡点，可由HF输出拍点，再通过OCC headless markers/split写入。要用OCC自己的音乐分析/切镜计划，当前需要打开编辑器用MCP。

## 接口矩阵

| 接口 | 实际命令/端点 | 输入→输出 | 是否开编辑器 |
|---|---|---|---|
| CLI启动与项目库定位 | npm run occ -- where --json；或构建并链接后的 occ where --json | Node24 + 已安装项目依赖；--data-dir <absolute-path> 可显式指定工程库 → mode/profileId/rootDir/mediaDir/keystorePath/projectStoreIndex | 不需要app/browser/MCP；下载源码包尚无node_modules/cli-dist时不能直接运行 |
| 创建/读取工程与时间线 | occ project new NAME --size 1920x1080 --fps 30 --json；occ project show ID --doc --json；occ timeline items ID --json | 工程id/唯一前缀/唯一名称；画幅/fps → 新工程；ProjectDoc/所有timelines/assets或各clip列表 | 不需要；只读工程可在编辑器打开时执行。写会受工程所有权限制。 |
| 导入HF/FFmpeg渲染结果到媒体池 | occ tools call import_assets --project ID --args '@import.json' --apply --json；import_asset/import_folder同理 | {"paths":["D:/project/output/title.mp4","D:/project/music.mp3"]}；单个为{"path":"绝对路径"} → imported[{id,name,kind,src}], duplicateCount, unsupportedFiles/errors；只入媒体池，未自动排到时间线 | 不需要，offline-path-import已有实际实现；occ media import子命令仍不存在，需走通用tools call。 |
| 导入已有剪辑结构 | occ tools call import_timeline --project ID --args '@timeline-import.json' --apply --json | {"format":"fcpxml"/"edl","content":"完整文档文字","name":"可选","activate":true,"fps":30,"startTimecode":"01:00:00:00"}；fps/startTimecode仅EDL → 新可编辑时间线timelineId/itemCount/trackCount/fps/warnings/skipped | 不需要；Node下FCPXML parser用@xmldom/xmldom回退 |
| 外部拍点写marker/剪镜操作 | occ tools call manage_markers --project ID --args '@markers.json' --apply --json；occ item split CLIP --at 120 --project ID --apply；occ edit --project ID --ops '@ops.json' --apply --json | manage_markers:{action:"create",markers:[{fromFrame:整数,note:"beat",scope:"project",color:"cyan"}]}；split_item:{itemId:"clip-id",atFrame:绝对时间线帧} → 可撤销标记或切分片段；ops可同一离线草稿原子提交 | 不需要；manage_markers/split_item均在headless白名单。外部HF beats计算结果可以通过适配器转帧后写入。 |
| OCC无模型节拍检测 | MCP工具 detect_beats({itemId,markers:"beats"/"downbeats",markerLimit})；或assetId仅分析 | 媒体池音频或时间线BGM片段id → bpm/confidence、源秒beats/downbeats、映射后timelineBeatFrames；可顺带落marker | 需要打开目标编辑器并通过MCP浏览器绑定；detect_beats不在headless白名单，occ tools call会拒绝。 |
| OCC神经音乐分析与切镜计划 | MCP: analyze_music→music_edit_plan→sync_cuts_to_music；照片为music_image_plan→sync_images_to_music | analyze:{itemId/assetId,force?,optional?}；plan:{itemId,timing:"auto/beat/downbeat/section",density:"sparse/medium/dense",fromFrame?,toFrame?,targetItemIds?}；sync再加analysisRef → BPM/meter/tags/sections/有限beat点；cutFrames+analysisRef；一批split并可撤销 | 需要编辑器；这些音乐工具不在headless server-direct白名单。不能因CLI有tools call就宣称所有工具都能无界面运行。 |
| MCP连接与绑定 | Streamable HTTP <实际app origin>/api/external-mcp/mcp；Authorization: Bearer <token> | MCP initialize/list-tools/call-tool；list_projects/create_project/target_project({projectId})；按需ToolSearch或load_skill暴露工具 → MCP session；浏览器绑定或offline绑定；结构化工具结果 | 服务进程必须运行；基础离线draft工具可以不开编辑器。浏览器能力需目标工程已在编辑器连接。offline绑定会话不能原地变浏览器绑定，打开编辑器后应新建MCP会话。 |
| CLI渲染与FFmpeg后续处理 | occ render ID --out D:/project/final.mp4 --codec h264 --resolution 1080p --fps 30 --dry-run --json；移除--dry-run实际渲染 | 保存工程；可选--timeline/--from/--to/--format video/audio；codec h264/vp8/prores/mp3/wav → 本地视频/音频文件；JSON有bytes/codec/frames/duration；dry-run只报plan | 不需要开编辑器/服务器/MCP；内部走server export+Remotion渲染，可能启动渲染浏览器子进程，不等于需要用户打开编辑器。 |
| 工程和NLE导出 | occ project show ID --doc --json（结构快照）；occ export jianying ID --out-dir DIR（剪映草稿）；完整portable工程包和FCPXML走现有UI导出路径 | ProjectDoc+媒体；剪映草稿另需capcut-cli；FCPXML转换支持部分结构 → ProjectDoc JSON；openchatcut-project@2流式工程包（兼容@1）；FCPXML或剪映草稿 | CLI结构读取/剪映导出无需编辑器；本次只证实完整portable包和FCPXML有浏览器/应用导出实现，没有对应occ export fcpxml子命令。 |
| 内部工程HTTP接口（不优先作集成入口） | GET /api/project-store/entry?key=project:ID；POST /api/project-store/project-document/write | 内部ProjectStoreRequest、baseRevision/ownership等协议 → 保存工程快照/变更回应 | 服务必须运行；loopback请求不强制用户可见页面，但写请求要求同origin语义 |
| HyperFrames HTML直接可编辑接入 | 未证实有官方原生HyperFrames HTML/GSAP工程导入器或导出器 | HF HTML/JS/CSS/GSAP composition与OCC ProjectDoc/Remotion MG不是同一格式 → 稳妥可验证路线是HF先渲染视频/音频→导入OCC；OCC只保留该视频片段的裁切、位置、效果等外层编辑 | 取决于所选HF/OCC渲染流程；HTML内文案/层/动画仍应回HF改后重渲染 |

## 逐项证据、认证与限制

### CLI启动与项目库定位

直接本地文件访问，无MCP bearer；必须与目标app使用同一profile/data-dir。dev checkout默认隔离，不能凭默认命令假定看到同一工程。

- [package.json:10](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/package.json#L10)：bin指向cli-dist/occ.mjs；scripts.occ=tsx cli/main.ts
- [cli/profile.ts:11](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/profile.ts#L11)：--data-dir设置OPENCHATCUT_DATA_DIR，且先于动态载入runtime profile
- [cli/main.ts:1](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/main.ts#L1)：明确无app/browser/MCP运行CLI

### 创建/读取工程与时间线

同一profile；显式--project或工程参数，避免默认最近工程。project show --doc不是带媒体的完整portable工程包。

- [cli/commands/project.ts:31](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/commands/project.ts#L31)：list/show/new；show可输出doc
- [cli/store.ts:1](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/store.ts#L1)：读同一project store，读无需离线写session
- [cli/commands/timeline.ts:17](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/commands/timeline.ts#L17)：show/items输出可读结构

### 导入HF/FFmpeg渲染结果到媒体池

headless本地导入读取AGENT_IMPORT_ROOTS：有值则限制realpath范围；空值的本地核心默认允许。浏览器HTTP导入分支必须显式allowlist。离线草稿写入要求工程不被已开编辑器占用。

- [server/external-agent/offline-path-import.ts:1](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/server/external-agent/offline-path-import.ts#L1)：offline MCP/CLI复用server/local-path-import核心
- [src/agent/external-tool-policy.ts:86](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/external-tool-policy.ts#L86)：import_asset/assets/folder为server-direct白名单
- [src/agent/tools/agent-path-import-tools.ts:39](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/agent-path-import-tools.ts#L39)：输入schema与返回imported资产
- [server/local-path-import.ts:75](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/server/local-path-import.ts#L75)：绝对路径、realpath及allowlist判断
- [cli/commands/media.ts:35](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/commands/media.ts#L35)：media其他子命令报不可用；不能照过时注释否定通用headless导入

### 导入已有剪辑结构

先导入其引用素材到媒体池。素材缺失/歧义会原子失败。工程所有权及--apply规则相同。

- [src/agent/tools/schemas/timeline-import-tools.ts:3](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/schemas/timeline-import-tools.ts#L3)：FCPXML1.x/CMX3600 EDL、素材匹配与跳过限制
- [src/agent/tools/timeline-import-tools.ts:21](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/timeline-import-tools.ts#L21)：浏览器DOMParser与Node xmldom分支
- [src/agent/external-tool-policy.ts:68](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/external-tool-policy.ts#L68)：import_timeline headless白名单

### 外部拍点写marker/剪镜操作

CLI写操作无--apply时丢弃草稿；有--apply使用approvalMode:auto的离线session、revision检查与版本快照。编辑器占用时不可并发离线写。

- [src/agent/tools/schemas/markers-tools.ts:5](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/schemas/markers-tools.ts#L5)：批量markers输入schema
- [src/agent/tools/schemas/core-tools.ts:90](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/schemas/core-tools.ts#L90)：split_item使用绝对atFrame
- [src/agent/external-tool-policy.ts:50](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/external-tool-policy.ts#L50)：split_item/manage_markers白名单
- [cli/commands/edit.ts:1](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/commands/edit.ts#L1)：--ops支持@file，一个草稿多个调用
- [cli/session.ts:1](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/session.ts#L1)：草稿原子提交、revision与ownership

### OCC无模型节拍检测

MCP bearer与正确project绑定；该支路无需下载beat模型，但浏览器需解码音频。

- [src/agent/tools/schemas/beat-tools.ts:5](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/schemas/beat-tools.ts#L5)：工具输入输出及帧映射公式
- [src/audio/beats.ts:1](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/audio/beats.ts#L1)：spectral flux→autocorrelation→相位网格→4/4启发式
- [cli/tool-catalog.ts:40](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/tool-catalog.ts#L40)：非headless工具拒绝并提示MCP+编辑器

### OCC神经音乐分析与切镜计划

需安装Beat This+CLAP本地模型包；analyze_music本身不下载。sync只用已有缓存，analysisRef防过期。

- [src/agent/tools/schemas/music-intelligence-tools.ts:104](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/schemas/music-intelligence-tools.ts#L104)：analyze需已安装模型，不下载；其余tool参数
- [src/agent/tools/music-intelligence-tools.ts:182](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/music-intelligence-tools.ts#L182)：按cutFrames生成split动作并batch
- [src/agent/external-tool-policy.ts:34](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/external-tool-policy.ts#L34)：server-direct名单不包含音乐分析/计划/同步工具

### MCP连接与绑定

token来自app设置/连接配置；OPENCHATCUT_MCP_TOKEN可覆盖。持久token在~/.openchatcut/mcp-token或dev profile子目录；不要提交到调研仓库。默认示例端口5199，不保证桌面实际端口。

- [server/plugins/external-agent.ts:139](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/server/plugins/external-agent.ts#L139)：实际MCP挂载路径与token门
- [server/editor-auth.ts:35](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/server/editor-auth.ts#L35)：token选择与Bearer验证
- [server/mcp-token.ts:25](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/server/mcp-token.ts#L25)：token home锚点与profile隔离
- [server/external-agent/mcp-binding.ts:109](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/server/external-agent/mcp-binding.ts#L109)：offline与browser绑定互斥
- [server/external-agent/mcp.ts:177](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/server/external-agent/mcp.ts#L177)：ToolSearch/load_skill按需暴露工具

### CLI渲染与FFmpeg后续处理

同profile媒体库；依赖须已安装，FFmpeg/Remotion渲染环境须可用。HF和OCC各自渲染输出文件可交给FFmpeg拼接/混音/转码；这不是自动语义互通。

- [cli/commands/render.ts:1](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/commands/render.ts#L1)：无HTTP/browser dialog/export queue，同export plan和renderTimeline
- [cli/commands/render.ts:102](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/commands/render.ts#L102)：dry-run计划
- [cli/commands/render.ts:125](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/commands/render.ts#L125)：渲染partial再rename，并输出完成信息

### 工程和NLE导出

不要把裸ProjectDoc当已打包所有素材。FCPXML导入会跳过title/generator/captions/effects/transitions等；MG在FCPXML导出可渲染为视频引用，不能保证跨NLE保留内部编辑性。

- [cli/commands/export.ts:23](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/commands/export.ts#L23)：唯一CLI target为jianying
- [src/persist/projectTransfer.ts:38](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/persist/projectTransfer.ts#L38)：@1/@2完整工程包格式及媒体
- [src/export/artifactExportOperations.ts:121](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/export/artifactExportOperations.ts#L121)：MG渲染后写XML路径
- [src/agent/tools/schemas/timeline-import-tools.ts:6](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/schemas/timeline-import-tools.ts#L6)：导入的跳过与近似说明

### 内部工程HTTP接口（不优先作集成入口）

与MCP auth不同：loopback socket+Host、Sec-Fetch-Site为same-origin或none；写还要Origin匹配Host；无MCP bearer握手。工程写有authoritative ownership，禁止直接PUT project key。建议用CLI/MCP，不绕内部所有权。

- [server/plugins/project-store-plugin.ts:83](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/server/plugins/project-store-plugin.ts#L83)：HTTP挂载路径
- [server/project-store-http-auth.ts:1](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/server/project-store-http-auth.ts#L1)：本机信任与Origin策略
- [server/project-store-http-routes.ts:223](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/server/project-store-http-routes.ts#L223)：直接project key PUT禁止，专用write入口

### HyperFrames HTML直接可编辑接入

Clip kind包括motion-graphic/video/audio/image等，但没有hyperframes/html clip种类。即便有code字段也不能推导任意HF HTML可原样运行；需自写适配器/移植为OCC支持的MG代码，未实现。

- [src/editor/clipTypes.ts:142](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/editor/clipTypes.ts#L142)：TimelineItem kind与MG code、媒体src字段
- [src/agent/tools/agent-path-import-tools.ts:53](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/agent-path-import-tools.ts#L53)：import_asset期望media file
- [src/persist/projectTransfer.ts:38](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/persist/projectTransfer.ts#L38)：原生工程包为OCC专用格式

## HF beats → OCC 的具体schema与命令

以下是**未执行的接线示例**。前提是OCC依赖已装；用户桌面源码目前还没有node_modules/cli-dist。示例工程id、clip id、路径必须换成实际值。源码模式在仓库根目录用`npm run occ -- ...`；下面简写`occ`表示已构建/链接的CLI，不能假定现在PATH已有它。

```powershell
# 先对齐数据目录；不要修改全局配置
occ where --data-dir D:/video-work/occ-library --json
occ project new "HF卡点练习" --size 1920x1080 --fps 30 --data-dir D:/video-work/occ-library --json
occ tools call import_assets --project PROJECT_ID --data-dir D:/video-work/occ-library --args '@import.json' --apply --json
occ timeline items PROJECT_ID --data-dir D:/video-work/occ-library --json
```

`import.json`：

```json
{"paths":["D:/video-work/hf-render/shot-01.mp4","D:/video-work/music.mp3"]}
```

导入只得到asset id，不自动加镜头到轨道。已有素材编排可先转FCPXML/EDL，再通过`import_timeline`保留剪辑区间。HF HTML本身不是上述交换格式；有自己的镜头表时，应由适配器生成EDL/FCPXML或OCC允许的编辑ops。

`markers.json`：假设外部拍点在1秒、2秒，工程30fps且BGM从0开始/未变速，对应30帧、60帧。

```json
{"action":"create","markers":[{"fromFrame":30,"durationFrames":0,"note":"HF beat 1","scope":"project","color":"cyan"},{"fromFrame":60,"durationFrames":0,"note":"HF beat 2","scope":"project","color":"cyan"}]}
```

```powershell
occ tools call manage_markers --project PROJECT_ID --data-dir D:/video-work/occ-library --args '@markers.json' --apply --json
# 先对一个已存在视频clip做一个切点；at是绝对时间线frame
occ item split CLIP_ID --at 60 --project PROJECT_ID --data-dir D:/video-work/occ-library --apply --json
# 多个已核对操作放一份ops.json，同一草稿原子提交
occ edit --project PROJECT_ID --data-dir D:/video-work/occ-library --ops '@ops.json' --apply --json
# 不加--apply会丢弃草稿，便于先看结果。import仍可能复制媒体文件到库，不保证零磁盘副作用。
```

`ops.json`中一条marker+一条split的形状：

```json
[{"tool":"manage_markers","args":{"action":"create","fromFrame":60,"note":"drop","color":"purple"}},{"tool":"split_item","args":{"itemId":"CLIP_ID","atFrame":60}}]
```

时间转换：`timelineFrame = startFrame + round((beatSeconds * fps - srcInFrame) / playbackRate)`适用于简单恒速映射；剪入点、音乐offset、起始frame、变速要一起计算。去掉clip范围外的点并按frame去重。批量切分需要维护每次split后的clip id/区间，不能把所有拍点对同一个旧id升序切完。

保存工程后可无界面渲染：

```powershell
occ render PROJECT_ID --data-dir D:/video-work/occ-library --out D:/video-work/final.mp4 --codec h264 --resolution 1080p --fps 30 --dry-run --json
# 看清plan后，去掉--dry-run才是实际渲染。
```

## 先学这8个入口

1. [cli/main.ts](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/main.ts#L1)：先看有哪些CLI命令，确认不依赖打开界面；package.json的occ脚本是源码入口。
2. [cli/profile.ts](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/profile.ts#L11)：理解工程库在哪，--data-dir为什么要在载入store前生效。
3. [src/agent/external-tool-policy.ts](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/external-tool-policy.ts#L34)：最关键：server-direct白名单解释哪些可以无界面、哪些必须编辑器。
4. [src/agent/tools/agent-path-import-tools.ts](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/agent-path-import-tools.ts#L15)：学import_asset/assets/folder参数以及导入媒体池后的返回asset id。
5. [src/agent/tools/schemas/markers-tools.ts](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/schemas/markers-tools.ts#L5)：HF beats转帧后，从批量markers开始接线，容易检查。
6. [src/agent/tools/schemas/core-tools.ts](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/schemas/core-tools.ts#L90)：看split_item、move_item、set_item_timing，理解OCC剪点按整数frame。
7. [src/agent/tools/schemas/music-intelligence-tools.ts](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/schemas/music-intelligence-tools.ts#L104)：理解analyze→plan→sync与analysisRef，避免把BGM当卡点。
8. [cli/commands/render.ts](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/commands/render.ts#L46)：最后看保存工程如何无界面变成MP4；先dry-run看plan。

## 两条能力边界

**导入HF渲染视频**之后，在OCC仍能改片段位置、裁切、速度、滤镜和外层编排；视频里已经烘焙的HF文字、DOM图层、GSAP动画继续回HF源工程改后重渲染。未证实OCC直接原生支持HF HTML工程。OCC的motion-graphic/code字段属于它自己的MG/Remotion机制，不等于任意HTML工程能原样可编辑导入。

**卡点切分不等于完成复杂混剪。** OCC的sync工具切已经存在的镜头；人物动作入点、镜头语义、密度起伏、变速曲线、转场、音效和叙事还要在适配器/agent/人工编辑里设计。用户现有HF项目可以继续负责这些复杂视觉，OCC作为可视化外层剪辑工作台。

桌面源码只读比对记录：[脱敏比对JSON](../evidence/openchatcut-desktop-comparison.json)。未安装，未运行，未修改桌面代码。
