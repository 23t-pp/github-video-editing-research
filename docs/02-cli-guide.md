# 零基础看懂这次 GitHub CLI 调研

这里解释命令的目的、输入、输出和检查方法。代码块可以复制到 PowerShell；不要把屏幕上的 `PS C:\...>` 一起复制。

本次真的执行了 GitHub 登录检查、搜索、读取仓库资料和源码、保存证据、建立调研仓库。没有安装或运行候选剪辑软件，没有测试它们能否在你的电脑上导出成片。下文用于以后操作的示例会明确标注。

## 1. Git、GitHub、gh 分别是什么

| 名词 | 可以怎样理解 | 常见命令 |
|---|---|---|
| GitHub | 存放项目的网站 | 浏览器打开仓库链接 |
| Git | 管理本地文件版本、与远端同步的工具 | `git status`、`git commit` |
| GitHub CLI / gh | 用命令操作 GitHub 网站的工具 | `gh search repos`、`gh api` |
| 仓库 / repository | 一个带版本记录的项目文件夹 | `作者名/仓库名` |
| README | 仓库首页的说明书 | 通常是 `README.md` |
| commit / SHA | 某次保存的版本编号 | 一串 40 位十六进制字符 |
| API | 网站提供给程序的数据入口 | `gh api repos/作者/仓库` |
| JSON | 带字段名的结构化文本 | `{"name":"demo","stars":10}` |

安装 GitHub CLI 后，命令名是 `gh`。`github` 不是这款工具的命令。

## 2. 检查工具和登录

```powershell
git --version
gh --version
gh auth status
gh api user --jq .login
```

读法：前两行应显示版本；第三行检查是否登录；最后一行只输出当前账号名。不要把登录 token 复制到公开仓库。

本次使用的 GitHub CLI 为 `2.103.3`。桌面应用进程的 PATH 没有立即包含新安装的 gh，因此实际调用用了完整路径：

```powershell
& 'C:\Program Files\GitHub CLI\gh.exe' --version
```

开头的 `&` 是 PowerShell 的调用运算符：让一个带空格的程序路径作为命令执行。如果你新打开的终端已经能识别 `gh`，直接使用短命令即可。两种写法调用的是同一个程序。

## 3. 搜索仓库：先宽搜，再核实

较容易上手的写法：

```powershell
gh search repos 'beat sync video' --limit 30
```

本次为了保留完整原始数据，实际采用 API 形式：

```powershell
gh api --method GET search/repositories -f 'q="beat-synced"' -f per_page=30
```

逐项解释：

| 片段 | 含义 |
|---|---|
| `gh api` | 通过已经登录的 gh 调 GitHub API |
| `--method GET` | 只读取数据。这里显式写出，避免带 `-f` 后变成 POST |
| `search/repositories` | 搜索仓库这个接口 |
| `-f 'q=...'` | q 是搜索词；单引号保护里面的空格与双引号 |
| `-f per_page=30` | 本次每条查询最多取一页、30 条结果 |

响应中的 `total_count` 是服务端报告的匹配总量；`items.Count` 才是这次真正拿回的数量。它们不一样，不能把几千条 total_count 写成“已逐个审查几千个项目”。还要保留 `incomplete_results`，因为搜索索引可能返回不完整结果。

这次使用了中英关键词扩展，例如“卡点”扩展为 `beat sync`、`beat-synced`、`AMV generator`，而不是假设 GitHub 本身提供向量语义搜索。完整查询在 [queries.json](../evidence/search/queries.json)。

## 4. 把搜索结果存成文件

```powershell
New-Item -ItemType Directory -Path .\work -Force | Out-Null
$raw = gh api --method GET search/repositories -f 'q="beat-synced"' -f per_page=30
if ($LASTEXITCODE -ne 0) { throw 'GitHub 搜索失败，请先检查报错' }
$raw | Set-Content -LiteralPath .\work\beat-search.json -Encoding utf8
$data = $raw | ConvertFrom-Json
$data.items | Select-Object full_name,stargazers_count,description
```

`$raw` 是一个变量，用来暂存响应；`|` 把左边的输出交给右边；`ConvertFrom-Json` 把 JSON 文本变成 PowerShell 能读字段的对象；`Select-Object` 只显示你关心的列。`$LASTEXITCODE` 检查外部程序是否成功，0 通常表示成功。

如果一个命令报错，不要继续把错误页面当成搜索结果。先读错误，再决定如何处理。

## 5. 看仓库元数据

```powershell
gh api repos/ZiadAbdelkarim/beat-synced-edit --jq '{name:.full_name,stars:.stargazers_count,pushed:.pushed_at,archived:.archived,fork:.fork,license:.license.spdx_id}'
```

这些字段只适合初筛：

- `stargazers_count`：关注度，不能证明剪辑质量。
- `pushed_at`：仓库最近推送时间，不能证明所有功能最近都维护过。
- `archived`：是否归档。
- `fork`：GitHub 记录的分叉关系，不一定能识别手工复制的镜像。
- `license.spdx_id`：GitHub 自动识别的许可。`NOASSERTION` 表示没有给出标准识别结论，必须继续读 LICENSE；它不等于“没有许可证”。

本次 `herk-edit-kit` 就是一个实例：API 返回 `NOASSERTION`，实际 LICENSE 主体为 MIT，并额外说明品牌素材不在复用授权内。

## 6. 先锁定版本，再看文件树

下面是可复现的检查示例：

```powershell
$repo = 'ZiadAbdelkarim/beat-synced-edit'
$meta = gh api "repos/$repo" | ConvertFrom-Json
$branch = $meta.default_branch
$commit = gh api "repos/$repo/commits/$branch" | ConvertFrom-Json
$sha = $commit.sha
$tree = gh api "repos/$repo/git/trees/${sha}?recursive=1" | ConvertFrom-Json
$tree.tree | Select-Object path,type,size
```

先拿 SHA，是为了让 README、文件树和源码都对应同一版。以后 main 分支变了，本仓库里的固定提交链接仍然能解释当时的判断。`recursive=1` 请求子目录；如果 `truncated` 为 true，还要继续读取子树，不能声称已经检查了全部目录。

不要凭文件名猜路径。本次官方 launch 模板的一次读取返回 404；查看树后确认 `heygen-apple-motion` 下还有 `01-ui-sting` 等子项目，路径修正后继续审查。404 是路径或权限线索，不是项目不存在的充分证据。

## 7. 读 README、许可证和真正的实现

```powershell
gh api -H 'Accept: application/vnd.github.raw+json' "repos/$repo/readme?ref=$sha"
gh api -H 'Accept: application/vnd.github.raw+json' "repos/$repo/contents/beat_map.py?ref=$sha"
```

第二条路径要先从文件树确认。这里举的 `beat_map.py` 是实际审查过的文件。`Accept` 告诉接口返回文件文本，方便阅读和保存。

审查顺序是：README 了解作者声称的功能 → LICENSE 看复用条件 → 依赖文件看安装门槛 → 入口代码看输入输出 → 关键函数看功能是否实现。

例如：README 写“跟随音乐”，源码却只写 `60 / bpm`，只能证明使用给定 BPM 计算网格；找到 `librosa.beat.beat_track`，还需继续看返回时间是否被剪辑规划和渲染器使用。每一层都要连接起来。

## 8. 去重：为什么不用项目名称直接判断

第一层按 GitHub 数字 `id` 合并：同一仓库被多个关键词找到，只保留一份身份记录，同时保留所有命中查询。

第二层检查 fork、重命名、官方 mirror、README 的来源说明和模板归属。

第三层检查模板级重复：两个仓库可能不是 fork，但其中几套模板来自相同上游。只合并那部分模板来源，不把整个项目粗暴当作同一项目。

最后检查已有环境：本次本机的 `herk-edit-kit` 提交恰好与查到的上游一致，因此“下载更多同一套技能”没有新增价值。

## 9. 自己复跑本次搜索

以下是以后可执行的命令，不是本次已渲染视频的证明：

```powershell
# 在本调研仓库根目录、PowerShell 7 终端运行
$run = & .\scripts\Search-GitHub.ps1 -MaxQueries 1
& .\scripts\Merge-Candidates.ps1 -RawDirectory $run.raw_directory -OutputFile (Join-Path $run.run_directory 'merged.json')
```

第一条先只跑一个查询，结果写进被 Git 忽略的 `replay/时间戳/raw/`，同时返回本次目录；第二条明确合并刚产生的结果。熟悉后可去掉 `-MaxQueries 1` 重跑全部。脚本会控制查询间隔，遇到 API 错误会停止，不会悄悄把失败当成空结果。

若只想离线复算本报告的历史555个仓库，不访问网络，单独运行：

```powershell
pwsh -NoProfile -File .\scripts\Merge-Candidates.ps1
```

实时结果可能与 2026-11-04 的快照不同，因为仓库、星数和搜索排序会变。复现的是方法；本次证据快照保留在 `evidence/`。

## 10. 看懂创建公开仓库的流程

本次发布采用下面这组命令的结构，发布结果另外记录在执行日志中：

```powershell
git init -b main
git add .
git commit -m 'docs: add Chinese video editing research and evidence'
gh repo create github-video-editing-research --public --source . --remote origin --push
gh repo view --json nameWithOwner,url,visibility,defaultBranchRef
git status --short
```

`git add` 把选定文件放入本次提交；`commit` 在本地保存一版；`gh repo create --public` 建公开远端；`--push` 上传本地提交；最后两条检查可见性与本地状态。它们的目的不同，不要把“本地 commit 成功”当作“GitHub 已经收到文件”。

完整命令含义可查：[gh api 官方手册](https://cli.github.com/manual/gh_api)、[gh search repos](https://cli.github.com/manual/gh_search_repos)、[gh repo create](https://cli.github.com/manual/gh_repo_create)。
