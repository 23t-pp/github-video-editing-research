# 弯心 / APEX · HyperFrames 可编辑工程

在这台电脑上双击 **Preview.cmd**，或在 PowerShell 里运行 `.\Preview.cmd`。预览中第28.125秒出现三联驾驶员特写，第30秒切回全屏。双击 **Render.cmd** 可重新生成工程与一分钟成片。

| 想改什么 | 从这里开始 |
|---|---|
| 片名和出现时间 | `edit.json` 的 `effects.title` |
| 字体、大小和颜色 | `style.css` 中的 `.word` 和 `.latin` |
| 三联窗口里的脸偏左或偏右 | `edit.json` 的 `effects.triptych.panels`。例如 `focusX: 0.61` 表示取源画面宽度61%处作为窗口中心 |
| 镜头入点 | 查 `镜头表.csv`，修改 `edit.json` 中同一镜号的 `sourceIn`，按学习手册的命令重新提取镜头和声音 |
| 鼓、贝斯、合成器 | 同级的 `music` 文件夹里有MIDI、四条乐器声部分轨、编曲和混音脚本 |

时间统一用24fps的整数帧。片段的起始帧算在片段内，结束帧属于下一个片段。编排数据在 **edit.json**，画面结构与动效在 **composition.py** 与 **style.css**，生成的 **index.html** 可直接交给 HyperFrames 预览和检查。

**两种编辑方式。** 跟手册改参数后用 **Render.cmd** 导出。若你在 Studio 的画布或代码面板里直接改了 HTML，可用 Studio 自带的 Export 保留这些修改。Render.cmd 会从参数文件生成画面，检测到 Studio 单独改过的 HTML 时会先将它另存成 `index-studio-*.html`。

**从另一台电脑运行。** 需要Python 3.10以上、Node.js 22以上、HyperFrames CLI、FFmpeg及支持 `fd:` 输出的构建、ffprobe和Chromium浏览器。本工程验证于HyperFrames 0.8.216及FFmpeg 9.0.2。可通过 `HYPERFRAMES_CLI`、`NODE_PATH_EXE`、`HYPERFRAMES_BROWSER_PATH`、`FFMPEG_PATH`、`FFPROBE_PATH` 指定本机路径。渲染已交付素材只需Python标准库。重建配乐和混音另需 `music/requirements-score.txt` 列出的库。

详细中文操作和剪点练习见上一级目录的 **剪辑学习手册.md**。打包的42个主镜头和P03补充素材可以直接使用，仅重新选择电影里的另一个时段时才需要原片目录。
