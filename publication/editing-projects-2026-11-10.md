# 11/06–11/10 剪辑成果（每个系列的最新版）

[本批 Release](https://github.com/23t-pp/github-video-editing-research/releases/tag/editing-projects-2026-11-10) · [下载中枢](README.md) · [仓库首页](../README.md)

这一批收录 11 月 6 日到 10 日完成的 **12 个项目，每个系列只收最新版**。共 **13 个附件、11,829,647,149 字节**。每个完整包里是该项目在工作区的原目录，包括成片 MP4、OpenChatCut 工程（.ccproj）、HyperFrames 工程、剪映工程（有的话）、中文说明和制作证据。

> **版权提醒**：除《银蓝穿越》和 BMW 素材是 AI 生成图外，其余项目使用了电影/动画原片画面和音乐，仅供剪辑学习研究。

## 每个项目下载哪些

|完成日期|项目|主参考|完整包（字节）|还要下载的独立附件|说明|
|---|---|---|---|---|---|
|11/06|最后一线 · 超凡蜘蛛侠 V4（V21）|V21|[tasm-v21-hold-on-v4-complete.zip](https://github.com/23t-pp/github-video-editing-research/releases/download/editing-projects-2026-11-10/tasm-v21-hold-on-v4-complete.zip)<br>1,034,532,991|无|60 秒，V1–V3 未收录|
|11/08|让名字回响 V3 · 寻梦环游记|—|[coco-mrbro-v3-complete.zip](https://github.com/23t-pp/github-video-editing-research/releases/download/editing-projects-2026-11-10/coco-mrbro-v3-complete.zip)<br>1,862,059,343|无|60 秒，V1–V2 未收录|
|11/08|记得我 · V22 复练|V22|[coco-v22-replay-complete.zip](https://github.com/23t-pp/github-video-editing-research/releases/download/editing-projects-2026-11-10/coco-v22-replay-complete.zip)<br>562,124,025|无|19 秒|
|11/09|一路回家 · 绿皮书 V23|V23|[greenbook-v23-replay-complete.zip](https://github.com/23t-pp/github-video-editing-research/releases/download/editing-projects-2026-11-10/greenbook-v23-replay-complete.zip)<br>565,638,315|无|25 秒|
|11/09|进入绿洲 · 头号玩家 V24|V24|[readyplayer-v24-replay-complete.zip](https://github.com/23t-pp/github-video-editing-research/releases/download/editing-projects-2026-11-10/readyplayer-v24-replay-complete.zip)<br>1,315,582,542|无|15 秒|
|11/09|赴约 · 斗破苍穹 20 秒|—|[doupo-zhujue-20s-complete.zip](https://github.com/23t-pp/github-video-editing-research/releases/download/editing-projects-2026-11-10/doupo-zhujue-20s-complete.zip)<br>519,635,999|无|20 秒|
|11/09|破界 V2 · 环太平洋 60 秒|V15、V24|[pacific-rim-60s-v2-complete.zip](https://github.com/23t-pp/github-video-editing-research/releases/download/editing-projects-2026-11-10/pacific-rim-60s-v2-complete.zip)<br>1,328,715,750|[pacific-rim-60s-v2-hyperframes-editable.zip](https://github.com/23t-pp/github-video-editing-research/releases/download/editing-projects-2026-11-10/pacific-rim-60s-v2-hyperframes-editable.zip)<br>847,311,125|60 秒，V1 未收录；HF 工程为独立附件|
|11/09|破界 · 环太平洋 30 秒紧凑版|V15、V24|[pacific-rim-30s-complete.zip](https://github.com/23t-pp/github-video-editing-research/releases/download/editing-projects-2026-11-10/pacific-rim-30s-complete.zip)<br>1,777,808,550|无|30 秒，由 V2 缩编|
|11/10|归地 · 灵笼第二季 11月10日原声版（V25）|V25|[linglong-v25-35-bgm2-complete.zip](https://github.com/23t-pp/github-video-editing-research/releases/download/editing-projects-2026-11-10/linglong-v25-35-bgm2-complete.zip)<br>1,109,912,216|无|35 秒原声版，首版未收录|
|11/10|银蓝穿越 V4 · 丝滑横屏（V10）|V10|[v10-silverblue-replay-v4-flow-complete.zip](https://github.com/23t-pp/github-video-editing-research/releases/download/editing-projects-2026-11-10/v10-silverblue-replay-v4-flow-complete.zip)<br>133,725,141|无|18.1 秒横屏，V1–V3 未收录|
|11/10|告白 · 回声档案 V26 横屏强化版|V26|[confession-v26-replay-v2-complete.zip](https://github.com/23t-pp/github-video-editing-research/releases/download/editing-projects-2026-11-10/confession-v26-replay-v2-complete.zip)<br>748,562,070|无|30 秒横屏，首版未收录|
|11/10|BMW M4 GT3 横屏生图素材|—|[bmw-m4-gt3-angle-assets-complete.zip](https://github.com/23t-pp/github-video-editing-research/releases/download/editing-projects-2026-11-10/bmw-m4-gt3-angle-assets-complete.zip)<br>24,039,082|无|5 张生图素材，尚未成片|

精确 SHA-256 和包内逐文件清单见 [manifests/projects-20261110/](manifests/projects-20261110/)。

## Windows 下载和恢复

完整包里的路径都以 `outputs/<项目名>/` 开头，解压到同一个工作区目录即可还原。下面示例恢复到 `D:/video-backup/workspace`。

```powershell
New-Item -ItemType Directory -Force -Path D:/video-backup/packages-20261110 | Out-Null
gh release download editing-projects-2026-11-10 --repo 23t-pp/github-video-editing-research --dir D:/video-backup/packages-20261110
Set-Location D:/video-backup/packages-20261110
Get-ChildItem *-complete.zip | ForEach-Object { Expand-Archive $_.FullName -DestinationPath D:/video-backup/workspace -Force }
Copy-Item ./pacific-rim-60s-v2-hyperframes-editable.zip "D:/video-backup/workspace/outputs/pacific-rim-60s-v2/破界_V2_HyperFrames可编辑工程.zip"
```

- 第 1 行：建下载目录。
- 第 2 行：用 GitHub CLI 下载本批全部附件。只要其中一个项目，可加 `--pattern 项目名-complete.zip`。
- 第 4 行：把每个完整包解压到工作区，得到 `outputs/<项目名>/`。
- 最后一行：把独立附件放回原位置（环太平洋 V2 整个目录约 2.07 GB，超过单个附件 2 GiB 的上限，所以把其中 808 MB 的 HyperFrames 工程单独上传）。

核对下载是否完整：`Get-FileHash 文件名 -Algorithm SHA256`，结果应与清单里的 `sha256` 一致。

## 打包时排除的内容

只排除了剪映自动生成的 `.tmp` 临时文件和 Python 的 `.pyc` 缓存，共 21 个，逐个列在 [package-report.json](manifests/projects-20261110/package-report.json)。

## 引用了未收录旧版本的地方

这些引用只出现在制作证据或说明链接里，不影响成片播放和工程打开：

- **coco-mrbro-v3**：制作证据里的对照指标和节拍说明引用了 V1/V2 目录（`coco-mrbro`、`coco-mrbro-v2`）的文件。
- **coco-v22-replay**：`hyperframes/plates.json` 记录的取帧索引来自 `coco-mrbro/逐帧拆解/全片逐帧索引.csv`。
- **pacific-rim-60s-v2**：README 里“原版逐帧拆解”链接指向 V1 目录 `pacific-rim-60s`。
