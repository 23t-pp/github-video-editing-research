# V05六格小样：OpenChatCut集成路径核查

最可靠路径是官方CLI创建**全新项目**，导入主流程提供的短片与HF成片，再用 `edit_track` / `edit_item` 建原生多轨时间线。交付同时保留两种编辑层次：HF成片整合时间线负责展示真实HF→OCC流程；OCC原生六格教学时间线负责逐格裁切、时序、位置和透明度编辑。HF HTML本身不能自动变成OCC原生图层。

当前仅只读核查，**没有创建项目、导入媒体或改服务/全局配置**。待主流程给出最终媒体路径、fps、时序后执行。没有读取 `.env.local/settings.env` 内容或认证密钥。

## 1. 当前服务与旧测试目录的关系

实际检查结果（本次会话）：

- `127.0.0.1:5199` LISTEN，PID **29360**；HTTP首页200，HTML671字节。这只证明服务响应，不能单独证明编辑器能渲染或CLI指向同库。
- Vite进程命令为本机可写Node运行 `node_modules/vite/bin/vite.js --config config/vite.config.ts --host 127.0.0.1`。
- 只读 `.git/openchatcut-dev-profile.json` 得到 `profileId=4bcb4e74-803a-4abe-8dbc-a4d40dea37c3`、repoRoot为桌面OpenChatCut-main。
- 正确库根：`C:/Users/PC/.openchatcut/dev-profiles/4bcb4e74-803a-4abe-8dbc-a4d40dea37c3`。设置**CLI子进程专用** `OPENCHATCUT_DEV_PROFILE_ID` 并显式 `--data-dir` 后，`occ where`报告 isolated-dev、正确media/uploads及该目录settings.env路径。没有打开settings.env。
- CLI project list读到3个有效项目；HTTP `GET /api/project-store/entry?key=projects`同样3个，**完整ID集合相等**。没有输出用户项目名称或内容。
- `C:/Users/PC/Desktop/OpenChatCut-data`为另一套旧测试库：CLI读到2个项目，ID集合与5199不等。此前将它认作同库的推断已被追加检查证伪；没有向该库写入。

源码依据：[scripts/dev-profile.mjs:11](C:/Users/PC/Desktop/OpenChatCut-main/scripts/dev-profile.mjs:11)定义元数据文件；[server/runtime-profile.ts:129](C:/Users/PC/Desktop/OpenChatCut-main/server/runtime-profile.ts:129)优先结合profile ID与DATA_DIR定位库；[cli/profile.ts:17](C:/Users/PC/Desktop/OpenChatCut-main/cli/profile.ts:17)在加载store前应用data-dir。不要只设置DATA_DIR而省略profile ID：这样CLI可能显示default，keystore路径落到源码目录 `.env.local`，与服务profile不一致。

`where.projectStoreIndex`仍显示兼容目录的projects.json路径，但实际库目录有SQLite、WAL、SHM与迁移receipt。[server/plugins/project-store.ts:25](C:/Users/PC/Desktop/OpenChatCut-main/server/plugins/project-store.ts:25)已导入SQLite实现，getStoredEntry第182行读SQLite。**不应手写JSON索引或复制正在使用的SQLite单文件**；用官方写入路径和portable工程包。

## 2. 官方入口与操作次序

源码包v0.2.17已装依赖，使用已验证的可写Node和本地tsx，不需要npm全局链接或MCP token：

```powershell
Set-Location 'C:/Users/PC/Desktop/OpenChatCut-main'
$env:OPENCHATCUT_DEV_PROFILE_ID='4bcb4e74-803a-4abe-8dbc-a4d40dea37c3'
$node='C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
$tsx='node_modules/tsx/dist/cli.mjs'
$dataDir='C:/Users/PC/.openchatcut/dev-profiles/4bcb4e74-803a-4abe-8dbc-a4d40dea37c3'
& $node $tsx cli/main.ts where --data-dir $dataDir --json
```

上面where与project list已实际执行。下列为**待媒体/时序明确后执行的建议命令**：

```powershell
& $node $tsx cli/main.ts project new 'V05六格学习小样-唯一时间戳' --size 1920x1080 --fps 30 --data-dir $dataDir --json
# 解析返回的新UUID；之后每条命令都显式 --project $newId，禁止用“最近项目”默认值。
& $node $tsx cli/main.ts tools call import_assets --project $newId --args '@D:/.../import.json' --apply --data-dir $dataDir --json
& $node $tsx cli/main.ts tools call edit_track --project $newId --args '@D:/.../tracks.json' --apply --data-dir $dataDir --json
& $node $tsx cli/main.ts edit --project $newId --ops '@D:/.../add-ops.json' --apply --data-dir $dataDir --json
& $node $tsx cli/main.ts project show $newId --doc --data-dir $dataDir --json
```

`project new`本身立即创建，不需要也不支持用 `--apply` 批准创建；说明文字中的“Only tools call --apply writes”不能据此否定project new行为。[cli/commands/project.ts:100](C:/Users/PC/Desktop/OpenChatCut-main/cli/commands/project.ts:100)解析尺寸/fps后调用创建；[server/external-agent/projects.ts:32](C:/Users/PC/Desktop/OpenChatCut-main/server/external-agent/projects.ts:32)构造默认 `track_v1`、空timeline与UUID，最后写入新project键和项目列表。

导入用 `tools call import_assets`，不是不存在的 `occ media import`。`import.json={"paths":["绝对路径的背景短片.mp4","绝对路径的拼图源短片.mp4","绝对路径的HF成片.mp4"]}`。[server/external-agent/offline-path-import.ts:1](C:/Users/PC/Desktop/OpenChatCut-main/server/external-agent/offline-path-import.ts:1)复用官方本地导入核心；[src/agent/tools/agent-path-import-tools.ts:175](C:/Users/PC/Desktop/OpenChatCut-main/src/agent/tools/agent-path-import-tools.ts:175)导入后按工程fps转换媒体池资产，返回 `imported:[{id,name,kind,src}]`，并单独报告errors、unsupportedFiles、duplicateCount。必须断言errors为空、导入资产数符合预期，不能只看CLI exit0。

导入会把媒体复制到库media/uploads，并保留内容身份；[server/local-path-import.ts:75](C:/Users/PC/Desktop/OpenChatCut-main/server/local-path-import.ts:75)验证绝对路径/realpath与可选allowlist。不要导入整部4K电影；主流程先截出短片。已有 `AGENT_IMPORT_ROOTS` 限制导致拒绝时停下来报告，不改配置绕过。本步骤不需要读取/打印该键。

## 3. 原生六格的具体数据schema

ProjectDoc当前公开版本为**3**（[shared/project-version.ts:2](C:/Users/PC/Desktop/OpenChatCut-main/shared/project-version.ts:2)）；根结构为 `{version,assets,mediaFolders,timelines,activeTimelineId}`，见[src/editor/projectTypes.ts:8](C:/Users/PC/Desktop/OpenChatCut-main/src/editor/projectTypes.ts:8)。Timeline含id/name/order/fps/width/height/items/trackOrder/tracks/selectedId等，见[src/editor/timelineTypes.ts:25](C:/Users/PC/Desktop/OpenChatCut-main/src/editor/timelineTypes.ts:25)。以官方创建结果作底，不凭空省字段拼“看起来像”工程。

先新增6个video轨，默认底轨放A背景；主流程若另有声音再加audio轨。`edit_track`输入里的 `json` 是**JSON字符串**：

```json
{"action":"create","json":"{\"trackType\":\"video\",\"count\":6,\"name\":\"六格\"}"}
```

[src/agent/tools/track-tools.ts:63](C:/Users/PC/Desktop/OpenChatCut-main/src/agent/tools/track-tools.ts:63)创建并返回created稳定track id和完整tracks；后续用稳定id，不依赖会重排的V1/V2别名。再用 `edit_item.adds` 加六份同一池资产，返回后读回timeline取得clip id，再一批updates补裁切和关键帧。新增片段示例：

```json
{"adds":[{"type":"video","assetId":"导入返回的B资产ID","track":"创建返回的稳定trackID","fromFrame":60,"sourceStartFrame":0,"sourceDurationInFrames":30}]}
```

此处60、30仅schema示例，不是最终小样时序。`sourceStartFrame/sourceDurationInFrames`与 `durationInFrames/srcInFrame`不要混用；schema见[src/agent/tools/schemas/edit-item-tools.ts:16](C:/Users/PC/Desktop/OpenChatCut-main/src/agent/tools/schemas/edit-item-tools.ts:16)。音量在后续updates置0，避免六份B源音叠加。

六格应取**同一完整画面不同空间区域**：1920×1080、3列2行，格(c,r)的crop像素为 `left=c*640,right=(2-c)*640,top=r*540,bottom=(1-r)*540`；六份内容均从相同时间开始。透明度控制显现，y控制短滑动，仍保留一张拼图的全局空间坐标。每格单独cover完整B镜头会得到六份重复画面，不能当整幅拼图。

```json
{"updates":[{"type":"video","itemId":"格子clipID","volume":0,"transform":{"crop":{"left":640,"right":640,"top":0,"bottom":540}},"keyframes":{"opacity":[{"frame":0,"value":0},{"frame":3,"value":0},{"frame":5,"value":1}],"y":[{"frame":3,"value":3,"easing":"easeOut"},{"frame":8,"value":0}]}}]}
```

重要单位：工具输入crop是**工程像素**；内部Doc的crop是0..1比例，[src/agent/tools/edit-item-visual.ts:60](C:/Users/PC/Desktop/OpenChatCut-main/src/agent/tools/edit-item-visual.ts:60)负责换算；[src/editor/clipTypes.ts:91](C:/Users/PC/Desktop/OpenChatCut-main/src/editor/clipTypes.ts:91)说明先在整画布裁切，再变换。x/y及其关键帧单位是**画布百分比**，不是像素；关键帧frame为**clip局部帧**，不是全时间线帧。easing放在**左侧关键帧**控制到下一帧的区间，上例frame3的easeOut控制3→8（数字仍须最终设计），不要放到右端。建议最终生成器加断言。

同一工程另建“HF整合”时间线，将HF渲染MP4放为独立媒体clip，接必要的A/B镜头与声音；保留“原生六格教学”时间线使6格可单独编辑。两种路线各自命名，不能把HF总MP4的外壳裁剪宣称保留了HTML内部图层。时间线创建/激活走headless `manage_timelines`，不直接改库文件。

## 4. 提交、并发与可移植交付

[cli/session.ts:1](C:/Users/PC/Desktop/OpenChatCut-main/cli/session.ts:1)说明offline session有ownership、revision与版本快照；[cli/commands/edit.ts:18](C:/Users/PC/Desktop/OpenChatCut-main/cli/commands/edit.ts:18)支持一个ops列表原子提交。只操作新ID；新工程完成CLI写入前暂不在编辑器打开该ID，避免编辑器占用导致离线写拒绝。现有其他工程和运行服务不受更改。`--apply`省略会丢弃Doc草稿，但本地媒体导入有复制副作用，所以不要对导入做无意义“dry-run”。

CLI `project show --doc --json`输出 `{project,timelines,doc}`，见[cli/commands/project.ts:71](C:/Users/PC/Desktop/OpenChatCut-main/cli/commands/project.ts:71)。它是结构快照，**不是带媒体可移植工程**。`occ export`当前只接受jianying（[cli/commands/export.ts:24](C:/Users/PC/Desktop/OpenChatCut-main/cli/commands/export.ts:24)），不要杜撰 `occ export project`。

首选官方UI导出：项目卡片“下载工程”调用 `buildProjectExport`，生成 `.ccproj`、格式 `openchatcut-project@2`；同时核查mediaMissing为空。[src/persist/projectTransfer.ts:239](C:/Users/PC/Desktop/OpenChatCut-main/src/persist/projectTransfer.ts:239)汇总Doc及媒体，[src/components/dashboard/DashboardViews.tsx:134](C:/Users/PC/Desktop/OpenChatCut-main/src/components/dashboard/DashboardViews.tsx:134)有该入口。官方导入器接受@2及旧@1；最终还应实际导入一份新副本验证（不覆盖原项目），然后检查时间线和媒体能显示。

若UI导出不便，可**按已存在官方格式**生成包，但必须额外实际导入验证，不能只把手写JSON称为已通过工程。旧@1最小schema见[src/persist/projectTransfer.ts:49](C:/Users/PC/Desktop/OpenChatCut-main/src/persist/projectTransfer.ts:49)：

```json
{"format":"openchatcut-project@1","name":"V05六格小样","exportedAt":"ISO时间","doc":"这里必须是实际ProjectDoc对象","media":[{"src":"/media/uploads/库内文件名.mp4","name":"文件名.mp4","mime":"video/mp4","bytes":12345,"dataBase64":"实际媒体字节base64"}]}
```

@2为逐行JSON：第一行manifest含真实Doc；每媒体依次media-start（src/name/mime/bytes）、media-chunk（data=base64）、media-end（src）。可复用官方输出机制[src/persist/projectTransferStream.ts:108](C:/Users/PC/Desktop/OpenChatCut-main/src/persist/projectTransferStream.ts:108)。媒体单项512MiB上限，行16MiB上限；因此只携短片，不携整部电影。包内去掉originalFilePath（官方[src/persist/portableProject.ts:37](C:/Users/PC/Desktop/OpenChatCut-main/src/persist/portableProject.ts:37)深拷贝清理）；媒体src仍须与Doc一致。

HTTP仅作比对和必要的回退读：本次GET返回found/value，已经使用。写接口有同Origin、Sec-Fetch-Site、revision/ownership合同，见[server/project-store-http-auth.ts:74](C:/Users/PC/Desktop/OpenChatCut-main/server/project-store-http-auth.ts:74)、[server/project-store-http-routes.ts:184](C:/Users/PC/Desktop/OpenChatCut-main/server/project-store-http-routes.ts:184)。既有CLI已覆盖，不需要另造HTTP写库逻辑。

## 5. 最小自动化脚本建议（此阶段不执行写入）

Node使用 `spawnSync(node,[tsx,cliEntry,...args,'--data-dir',correctProfile,'--json'],{cwd:repo,env:{...process.env,OPENCHATCUT_DEV_PROFILE_ID:id},encoding:'utf8',windowsHide:true})`；参数数组传路径，避免shell插值。每步保存命令argv、exit、stdout JSON及stderr到本次work目录；不保存env对象，不读密钥。

生成器应依序：profile与HTTP库集合检查 → 创建唯一新项目并记录UUID → 导入短片检查errors → 建轨记录稳定ID → 加clips并读回ID → 一批crop/时序/关键帧updates → 建HF整合timeline → Doc读回断言 → 打开该项目视觉检查 → 官方portable导出 → 新副本实际导入验证。断言至少覆盖：六个格子的src相同、source窗口相同、crop覆盖完整3×2、音量0、入场时点递增、同一个结束帧；HF整合timeline确有HF成片资产；所有Doc引用媒体均被工程包携带。

目前完成的是路径/接口核查，不是工程创建或测试通过。需要主流程给：A/B短片及HF渲染路径、工程fps/尺寸、六格开始结束帧、每格相对入场帧、滑动/透明度曲线、音频策略与整合时间线顺序。
