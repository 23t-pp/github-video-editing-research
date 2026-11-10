# 全部剪辑工程、成片与2,061,018个JPG采样路径

这份仓库面向没有剪辑和编程基础的学习者。可以先读混剪参考的逐条拆解，也可以下载成片与可编辑工程，按中文说明练习。

## V01–V25 混剪参考学习库

1. [按编号读 25 条拆解](studies/reference-library-20261105/reviews/逐条索引.md)。每条都能直达报告、逐帧表和声音卡点数据。
2. [下载完整学习包](https://github.com/23t-pp/github-video-editing-research/releases/tag/reference-library-v01-v25-2026-11-10)。解压后打开包内的中文 README，按步骤启动学习页。包内有逐帧图谱、单帧证据、25 条原混音和 25 条音乐主体候选。
3. [按技法选练习](studies/reference-library-20261105/catalog/技法分类与难度排行.md)。可以从同动作对位或矩形画窗开始，再练动态抠像和多层接力。

25 条参考共覆盖 **21,198 个原生帧、366 页原生图谱**。V21 额外用 60Hz 网格记录 1,856 个采样位置，对应 928 个原生帧。参考的逐帧数据、原生图谱和单帧 JPG 保存范围见[学习库说明](studies/reference-library-20261105/README.md)。

## 先下载什么

|内容|下载入口|里面有什么|
|---|---|---|
|全部剪辑工程与结果|[工程成果 Release](https://github.com/23t-pp/github-video-editing-research/releases/tag/editing-projects-2026-11-05)|V05、V07、速度与激情、EDGE V1/V2/V3、第一季一分钟混剪、音乐与研究证据、完整OCC/HF工程、自写执行脚本及OCC应用源码快照|
|11/06–11/10 新成果（每个系列最新版）|[11/10 工程 Release](https://github.com/23t-pp/github-video-editing-research/releases/tag/editing-projects-2026-11-10) · [中文下载说明](publication/editing-projects-2026-11-10.md)|蜘蛛侠 V4、寻梦环游记 V3、V22–V25 复刻、斗破苍穹、环太平洋 V2/30 秒、银蓝穿越 V4、告白 V26、BMW 生图素材，共 12 个项目|
|全部JPG素材|[2,061,018路径 Release](https://github.com/23t-pp/github-video-editing-research/releases/tag/jjk-s1-jpg-60hz-2026-11-05)|24个逐集归档，包含全部JPG路径、SQLite索引、逐样本JSONL与校验元数据|
|当前第一季成片|[下载60秒MP4](https://github.com/23t-pp/github-video-editing-research/releases/download/editing-projects-2026-11-05/jjk-s1-final-60s.mp4)|1920×1080、24fps、1440帧|
|直接改第一季完整效果|[HyperFrames工程](https://github.com/23t-pp/github-video-editing-research/releases/download/editing-projects-2026-11-05/jjk-s1-hyperframes-editable.zip)|源视频片段、字体、52张RGBA、字形和创作源码|
|直接在剪辑器打开|[OpenChatCut工程](https://github.com/23t-pp/github-video-editing-research/releases/download/editing-projects-2026-11-05/jjk-s1-openchatcut.ccproj)|59镜原生序列、20段HF效果序列、85媒体无缺失|

**206万个路径实际存放在Release附件中。Git代码浏览页不逐个平铺这206万个文件；下载24档后会恢复全部路径，绝非只有索引。** 同一源帧的重复样本在tar中保存为硬链接条目，恢复时逐个创建；目标盘不支持硬链接则复制字节，路径数仍完整。

源码镜像里的原项目说明保持原字节，其中相对MP4、ZIP、图片链接需要先下载完整包并恢复到本地才能打开。各项目需要的完整包和独立HF/OCC回填附件，见[中文下载中枢](publication/README.md)。

工程Release共27附件（25项工程资产、独立预览MP4、独立审计ZIP），7,048,393,867字节；JPG Release共30附件（24集归档、6份工具与清单），14,602,310,573字节。合计57附件、21,650,704,440字节，均已核对GitHub大小及SHA-256 digest。

JPG为640×360/q6，方便检索。60Hz是采样网格，源片24000/1001fps，823,577个源帧ID映射为2,061,018个JPG路径，其中1,237,441次重复采样。没有插帧或凭空新增动作。正式剪辑回原视频取高分素材。

## 完整下载与还原：按顺序复制命令

先在PowerShell运行`gh --version`和`python --version`检查。需要登录时执行`gh auth login`。当前制作电脑已安装GitHub CLI，也有Codex自带Python；若`python`命令不可用，可用`& 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'`替代下文的`python`，无需重复安装。

```powershell
New-Item -ItemType Directory -Path D:/video-backup/packages -Force
gh release download editing-projects-2026-11-05 --repo 23t-pp/github-video-editing-research --dir D:/video-backup/packages
gh release download jjk-s1-jpg-60hz-2026-11-05 --repo 23t-pp/github-video-editing-research --dir D:/video-backup/packages
```

前一条下载工程与成果，后一条下载24集素材。`git clone`只取源码与文档，不会自动下载Release附件。若下载中断，重跑时可加`--skip-existing`，然后用提供的SHA清单核验；不要把半截文件当完成。

```powershell
Set-Location D:/video-backup/packages
python -X utf8 ./restore_projects.py --downloads . --workspace D:/video-backup/workspace --with-sources
python -X utf8 ./restore_jpg.py . --destination D:/video-backup/workspace/outputs/jjk-s1-workflow/素材集_60Hz_JPG --manifest ./jpg-manifest.json
```

第一条还原全部工程目录，并按内置映射把独立HF/OCC附件回填原路径；第二条恢复全部JPG，使学习服务直接找到素材。两份工具都会核对字节与SHA并拒绝越界路径。工程恢复遇到已有不同内容会报错；JPG恢复中断后加`--resume`重新校验和恢复。完整操作以附件的中文还原说明和`--help`为准。

只学习第一季时，可以先下载`jjk-s1-workflow-complete.zip`、`jjk-s1-hyperframes-editable.zip`、`jjk-s1-openchatcut.ccproj`、`publication-supplement.zip`与还原脚本；JPG也可先下某一集。

```powershell
python -X utf8 ./restore_projects.py --downloads . --workspace D:/video-backup/workspace --project jjk-s1-workflow
```

```powershell
python -X utf8 ./restore_jpg.py ./S1E01.tar.gz --destination D:/video-backup/workspace/outputs/jjk-s1-workflow/素材集_60Hz_JPG --manifest ./jpg-manifest.json
```

NTFS硬链接共享数据；要单独涂改某一张请先复制为独立文件。复制模式会占用更多磁盘。完整数据、索引及工程空间以发布清单的实际大小为准，另预留解压空间。

## 学习顺序

1. 先播放第一季一分钟MP4，再打开[中文项目入口](studies/full-delivery-20261105/jjk-s1-workflow/README.md)。
2. [比较四轮改进](studies/full-delivery-20261105/jjk-s1-workflow/docs/四轮改进对照.md)：L1裸切、L2复杂合成、L3修订、L4真实动作与字效精修；前两次revise保留，不冒充每轮都一次通过。
3. [技法与参考对照](studies/full-delivery-20261105/jjk-s1-workflow/docs/最终剪辑技法对照.md)、[适配素材与难易排行](studies/full-delivery-20261105/jjk-s1-workflow/docs/技法选用与难易排行.md)。
4. [命令与操作](studies/full-delivery-20261105/jjk-s1-workflow/docs/操作与学习.md)、[工作流故障与修复](studies/full-delivery-20261105/jjk-s1-workflow/docs/工作流故障与修复.md)。
5. 修改复杂字、alpha和电弧回HyperFrames；OCC原生序列负责顺序、裁切与音轨。两边没有自动双向同步。

## 如何证明完整

- 发布清单记录每档字节、SHA-256、JPG条目和硬链接数。
- 逐档实际流读全部JPEG并对源索引核SHA，全部采样路径与硬链接目标逐项核验。
- 独立审核实际恢复首集全部路径，核对共享硬链接、复制模式与可复现抽样JPEG解码。
- 上传后读取GitHub服务端`digest`与`size`，逐项匹配本地附件。
- [发布与远端校验清单](publication/README.md)提供准确版本、下载表和验证证据。
- [下载独立审计证据ZIP](https://github.com/23t-pp/github-video-editing-research/releases/download/editing-projects-2026-11-05/publication-audit-evidence.zip)，或在线查看[审计证据](publication/evidence/independent/)和[审计工具源码](publication/tools/independent/)。

第一季原有51项交付验收与四轮视频证据保留。复刻是参考技法迁移，局部发丝/衣边有近似；音乐残留和接缝未做听觉试听。源码、上游许可和自写改动来源分开记录。依赖安装体、模型权重、浏览器/账号profile及可重建渲染缓存不属于成果附件。

## 以前的研究与发布

- [软件选型、GitHub CLI与原学习仓库首页](README-before-full-publication-20261105.md)
- [最初发布的 20 条参考、音乐库与 V05 小样](https://github.com/23t-pp/github-video-editing-research/releases/tag/reference-library-2026-11-05)

第三方媒体权利不因上传自动转移；现有代码与媒体说明、上游许可证继续适用。
