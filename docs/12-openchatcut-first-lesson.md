# 第一课：看懂桌面上的OpenChatCut源码

先认识你已经下载的东西。确认目录名是`OpenChatCut-main`，包版本为0.2.17。它是编辑器程序的源码；`src`存放其中的界面和剪辑逻辑。以后在编辑器里创建的“某条视频工程”，会保存素材引用、时间线和剪辑参数，是另一种数据。

本次只读检查发现还没有`node_modules`和`cli-dist`，因此源码尚未安装依赖和构建CLI。没有`.git`，符合下载源码压缩包的结构；这不影响学习源码。本机Node v24.22.2符合项目声明的`>=24 <25`，FFmpeg也已存在。

主流程还用`git hash-object`比较了5个本机文件与本轮审查的上游目录树：package.json、音频节拍、音乐剪辑工具、时间线导入工具、CLI工程命令均匹配。仅证明这5个文件相同，未声称整个目录没有任何变化。

## 文件夹地图

| 位置 | 白话含义 | 什么时候才需要读 |
|---|---|---|
| `README_ZH.md` | 中文使用说明 | 第一个读 |
| `package.json` | 依赖清单和启动命令目录 | 要启动软件、看Node版本时 |
| `src/components/` | 你在屏幕上看到的按钮、面板等 | 修改界面时 |
| `src/editor/` | 时间线及剪辑状态的核心 | 理解素材片段怎么排列、分割和撤销时 |
| `src/audio/` | 音频、拍点与音乐信息 | 学卡点时 |
| `src/agent/tools/` | AI可以调用的剪辑操作 | 让助手代你修改工程时 |
| `src/media/` | 素材导入、管理与搜索 | 找素材、替换素材时 |
| `src/export/` | 导出工程和成片的相关逻辑 | 做交接或查导出问题时 |
| `server/` | 本机服务、存储和外部接口 | 连接MCP、CLI、模型服务时 |
| `cli/` | `occ`命令行入口 | 批量处理工程时 |
| `desktop/` | 桌面壳与本机能力 | 打包Windows应用或使用原生能力时 |
| `remotion/` | OpenChatCut自己的渲染实现 | 深入理解它怎样导出画面时 |
| `assets/`、`public/` | 软件自带资源 | 查模板、字体、图标等资源时 |

不用一次读懂全部文件。第一阶段只沿一条操作链找入口。

## 一次音乐卡点操作经过哪里

```mermaid
flowchart LR
  A[导入本地视频与音乐] --> B[分析音乐的拍点]
  B --> C[决定哪些拍点要换镜头]
  C --> D[把秒转换成时间线帧号]
  D --> E[生成split等剪辑操作]
  E --> F[预览并人工调整]
  F --> G[导出成片或工程]
```

“知道音乐哪里有拍点”与“决定哪里应该换镜头”是两个步骤。强拍可以用来切镜，也可以只触发推近、字幕或音效。每一拍都切镜不一定好看。

## 先看这5个文件

| 文件 | 找什么 | 你要学会的问题 |
|---|---|---|
| [src/audio/beats.ts](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/audio/beats.ts) | analyzeAssetBeats等入口 | 拍点来自音乐分析还是人为常数？ |
| [src/agent/tools/music-intelligence-tools.ts](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/music-intelligence-tools.ts) | buildMusicSplitActions、syncCuts | 分析结果怎样变成真的剪辑操作？ |
| [src/agent/tools/timeline-import-tools.ts](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/agent/tools/timeline-import-tools.ts) | import_timeline、fps与warning | 导入别的时间线时，帧率转换会发生什么？ |
| [cli/commands/project.ts](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/cli/commands/project.ts) | list、show、new | 一条命令如何读取或创建工程？ |
| [src/export/fcpxml.ts](https://github.com/0xsline/OpenChatCut/blob/7fa4b7903e7ebecf832a36249f0c0c755200cc17/src/export/fcpxml.ts) | 时间线与素材如何写进输出 | 什么能继续编辑，什么需要预渲染？ |

第一遍只找函数名、输入和输出，不必理解每一行TypeScript语法。

## 一个能直接看懂的代码细节

`buildMusicSplitActions`会筛掉片段之外的切点，跳过锁定轨道，再把切点按从后到前的顺序排列，最后生成`split`操作。

假设一个镜头要在第5秒和第10秒各切一次。先切第10秒，原来的前段仍包含第5秒，下一刀容易落到同一个片段上。这说明剪辑操作不仅需要一组时间，还需要正确的执行顺序和对象标识。

另一个基础计算是：30fps的视频，第2秒对应约第60帧。不同工具交换时间线时，必须说明时间单位和帧率。不能把“60”交给另一工具，却不说明它代表秒、帧还是毫秒。

## 现在能做的只读练习

在PowerShell中运行下面的命令。`$projectRoot`改为你自己的源码目录；它们只读信息，不启动编辑器。

```powershell
$projectRoot = Join-Path ([Environment]::GetFolderPath('Desktop')) 'OpenChatCut-main'
Set-Location -LiteralPath $projectRoot
node --version
$pkg = Get-Content -LiteralPath .\package.json -Raw | ConvertFrom-Json
$pkg.version
$pkg.engines
Get-ChildItem -LiteralPath .\src -Directory | Select-Object Name
```

读懂输出即可完成第一课：确认版本、运行环境，以及各功能目录。

## 启动是下一步独立检查

源码启动需要安装依赖，然后运行项目提供的启动脚本。当前核查尚未执行`npm install`、`npm run dev`，也没有建立MCP连接或验证成片。

学习顺序建议：启动一个独立测试环境 → 用少量自有素材完成普通剪辑 → 读工程和时间线 → 验证HF拍点到OCC的连接 → 再加入复杂字效、遮罩和变速。每一步都应能说明“输入是什么、修改了哪里、输出怎样检查”。

具体两条集成路线及限制见[OpenChatCut与本机工具集成](11-openchatcut-integration.md)。
