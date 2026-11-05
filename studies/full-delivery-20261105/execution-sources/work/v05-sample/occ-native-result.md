# OCC原生六格已写入并读回

新项目UUID：`0fd76ceb-875e-4507-be68-f296dd3dacfd`。

项目名：`V05六格卡片学习小样-2026-11-04T15-00-57-302Z`。

原生时间线ID：`tl_44436b4d-d623-4d92-9856-55be7bb7f7c7`，名为“01 OCC原生六格教学 · 24fps”。库根为已确认的`4bcb4e74-803a-4abe-8dbc-a4d40dea37c3`隔离profile；未使用旧Desktop/OpenChatCut-data库。

官方CLI实际执行成功：创建新项目 → 导入A/B两段短片 → 命名时间线 → 新建六个视频轨 → 增加8个video clip → 批量裁切与关键帧 → 读回验证。所有11条CLI调用退出0、stderr为空；工具回执均applied=true，无result.error。每步命令argv、stdout JSON、stderr均在本目录编号文件；脚本为`occ-native.mjs`，再次执行会因state已存在而拒绝重复创建。

读回断言已通过：1920×1080、24fps、终点108帧（4.5秒）；底轨A全局0–48源0，六份B全局30–48源0，末段B全局48–108源18；七个video轨、8个clip；六格crop为同一完整B画面的3×2区域，scale=.72、x=0；顺序0,3,1,4,2,5，入场局部0,2,4,6,8,10帧，opacity两帧到1，y上下分别−0.8/+0.8画布百分比、3帧easeOut到0；所有视频volume=0，末段B淡出6帧。独立HTTP读回同一新UUID，found=true、1 timeline、8 items、2 assets、全部静音。

原生Doc及带项目元数据的读取快照保存在`outputs/v05-six-panel/openchatcut/`；精确断言明细为`occ-native-verification.json`，项目状态为`occ-native-state.json`。这些是官方应用已保存的可编辑多轨数据，不是烘焙MP4伪装的工程。

后续音轨阶段已完成：master-audio.wav已导入资产池并放入原生时间线独立音轨，全局0–108帧、源0、volume=1；8个video clip仍全部静音，最终为9个item、8条轨、3个资产。7次新增CLI调用均退出0，写操作applied=true；官方CLI与HTTP完整Doc深比较一致。音轨资产ID为`2e9fd18f-ec48-4d84-990f-2e6a56e88406`，轨ID为`track_e88fc9ea-3b6a-4629-ab3c-97f0bbdd6cec`，clip为`item_8a18bfa3-6341-47b4-876e-95f1aa60652e`。更新后的Doc与快照已覆盖保存到outputs；审计在audio-*文件与occ-audio-verification.json。

按主流程要求没有打开该工程UI，**尚未做视觉播放/渲染验证**。HF最终MP4尚未导入；第二条HF整合时间线、portable .ccproj、实际导入副本验证留待媒体齐备后完成。当前Doc快照不是带媒体的portable工程包。
