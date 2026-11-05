# 下载与还原（零基础 Windows）

发布仓库：[23t-pp/github-video-editing-research](https://github.com/23t-pp/github-video-editing-research)。成片和工程在 `editing-projects-2026-11-05`；完整 JPG 素材库在 `jjk-s1-jpg-60hz-2026-11-05`。Git 源码目录只保留小文本，体积大的实物均在 Releases。

## 先准备

安装 [Python](https://www.python.org/downloads/windows/)（3.11 或更新）和 [GitHub CLI](https://cli.github.com/)。在 PowerShell 执行 `python --version`、`gh --version` 检查。若 GitHub 提示登录，执行 `gh auth login` 按网页指引完成。以下路径可以换成自己的空目录，建议路径短一些，例如 D:\video-work。

## 完整下载工程、四轮视频与全部证据

在 PowerShell 逐段复制运行：

```powershell
New-Item -ItemType Directory -Force -Path "D:\video-downloads" | Out-Null
gh release download editing-projects-2026-11-05 --repo 23t-pp/github-video-editing-research --dir "D:\video-downloads"
python -X utf8 "D:\video-downloads\restore_projects.py" --downloads "D:\video-downloads" --workspace "D:\video-work" --with-sources
```

还原脚本会安全合并全部 `*-complete.zip`，自动处理 `publication-supplement.zip`，按嵌入清单把独立 HF/OCC 文件放回原路径并核 SHA256。`--with-sources` 同时还原 `work/...` 自写执行代码和 `dependencies/OpenChatCut-main/...` app 源码。遇到缺档、错误 SHA、越界路径或已有不同内容会明确报错；已有同 SHA 文件跳过，不递归删除。脚本只用 Python 标准库，并支持 Windows 长路径。

## 只下载第一季 V20 一分钟工程

若只要 S1，可用这个较小的下载集合；同目录必须有补包，因为它包含非秘密素材指纹和执行证据：

```powershell
New-Item -ItemType Directory -Force -Path "D:\s1-downloads" | Out-Null
gh release download editing-projects-2026-11-05 --repo 23t-pp/github-video-editing-research --dir "D:\s1-downloads" --pattern "jjk-s1-workflow-complete.zip" --pattern "jjk-s1-hyperframes-editable.zip" --pattern "jjk-s1-openchatcut.ccproj" --pattern "publication-supplement.zip" --pattern "restore_projects.py"
python -X utf8 "D:\s1-downloads\restore_projects.py" --downloads "D:\s1-downloads" --workspace "D:\video-work" --project jjk-s1-workflow
```

正式片在 `D:\video-work\outputs\jjk-s1-workflow\咒力接力_一分钟.mp4`。原生工程在同项目的 `openchatcut` 目录；HF 原始编辑 ZIP 也会放回项目根。四轮视频和逐轮证据保留在 `loops`、`evidence`、`reviews`、`workflow` 等目录。它与 EDGE V1/V2/V3 是独立任务。

## 下载和还原全季 JPG

JPG 库很大，可按实际需要下载；工程恢复和看成片不要求先下载它。

```powershell
New-Item -ItemType Directory -Force -Path "D:\jpg-downloads" | Out-Null
gh release download jjk-s1-jpg-60hz-2026-11-05 --repo 23t-pp/github-video-editing-research --dir "D:\jpg-downloads"
python -X utf8 "D:\jpg-downloads\restore_jpg.py" "D:\jpg-downloads" --destination "D:\video-work\outputs\jjk-s1-workflow\素材集_60Hz_JPG" --manifest "D:\jpg-downloads\jpg-manifest.json"
```

该 release 包含 `S1E01.tar.gz` 至 `S1E24.tar.gz`、逐档清单、校验文件和中文指南。档内直接是 `S1E01/minute-000/F0000000.jpg` 等路径，因此目标必须指定到上面的 `素材集_60Hz_JPG`，无需额外套一层目录。

恢复脚本先核每档字节数/SHA，再核 native JPG 和 SQLite 映射及全部样本路径。中断后在原命令末尾加 `--resume`；不能创建硬链接时会复制，也可以加 `--copy` 强制复制。全季 2,061,018 路径由 823,577 原生 JPG 和 1,237,441 重复样本硬链接组成，属于 60Hz 取样，非插帧。复制模式会占更多磁盘。

## 编辑与复现

打开各项目原有中文 README/学习页了解 OCC 与 HF 各自可修改的效果。S1 封存代码继续以 `outputs/jjk-s1-workflow/hyperframes` 为准，`work/.../hf-studio-r4` 是练习副本。

OpenChatCut app 源码快照版本为 0.2.17，保留 AGPL-3.0-or-later LICENSE 和 package-lock；Node 要求 `>=24 <25`。按 `dependencies/OpenChatCut-main/README_ZH.md` 安装依赖，并运行上游资源同步脚本。HyperFrames、FFmpeg、Python 依赖按原项目说明准备，本发布不带安装体或模型权重。自写 OCC 客户端保留了原制作机器的软件路径/UUID证据，复现时应改成自己的安装位置；不含真实账户 token、.env 或浏览器 profile 目录。

`publication-supplement.zip` 补回 169 个先前按名称误排的非秘密文件：64 位 `.key` 是素材缓存指纹，人物 profile 是侧脸证据，OCC profile 日志记录路径和 UUID，token/profile 命名的模块是源码。它们已逐字节核验并经过独立内容审查。

下载后可对照发布清单核对资产 SHA256；`project-release-tools-and-manifests.zip` 保留全部逐源文件清单、恢复实测、打包源码、排除范围与中文发布说明。
