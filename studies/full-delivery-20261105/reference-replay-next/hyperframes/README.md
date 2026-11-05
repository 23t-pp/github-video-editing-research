# HyperFrames可编辑工程

本目录包含源视频、音乐、真实动态alpha、侧窗跟踪点、动画生成代码和渲染脚本。

先读上一级的 `学习总结与命令.md`。本工程长30秒、25fps、750帧，1920×1080。

```powershell
python -X utf8 .\composition.py
node .\hf.mjs preview . --port 5215 --no-open
```

浏览器访问 `http://127.0.0.1:5215`。如果命令路径未加入PATH，使用上一级学习总结给出的本机Python/Node完整路径。

常用修改入口：

- `edit.json` → `shots`：镜头位置与使用的素材范围。
- `edit.json` → `effects`：动态前景进入位置、旋转、尺度、出现与换底时间。
- `assets/alpha/`：逐帧RGBA图像、人工控制点及证据图。
- `motion/window-keyframes.json`：侧窗四角人工锚点。
- `composition.py`：新增或修改动画逻辑；生成的 `index.html` 可在Studio里选中图层查看。

修改 `edit.json` 后运行 `composition.py` 更新页面。若Studio直接修改过HTML，再生成时会保存 `.source-backups/index-studio-<指纹>.html.bak`，避免覆盖后找不回。备份不用 `.html` 作为最终扩展名，防止Studio把它识别成第二个作品。

重新渲染：

```powershell
python -X utf8 .\tools\render.py --work .\.render-cache
```

需要本机已有的FFmpeg、HyperFrames CLI和Chrome。当前工具路径集中在 `hf.mjs`、`tools/render.py`；换电脑时按实际安装位置修改。成片会写到上一级 `越界_V07复刻.mp4`，对应OpenChatCut插片写入上一级 `occ-effects`。

重做动态抠像或车窗跟踪额外需要OpenCV和NumPy；普通预览/再渲染使用已保存的PNG与矩阵，不需要重新安装分割模型。此工作区的OpenCV安装在 `work/reference-replay-v07/python-deps`。若复制工程到别处，要先调整工具里的依赖搜索路径。

`prepare-base.py`是本次初始截取脚本，不是当前最终选镜的自动重建器。正式片段已经包含在 `assets/shots`。三处最终QC修正的记录为该目录内的 `base-qc-repairs.json`、`pedal-cleanup.json`、`P17-replacement.json`；重截整部电影前应按这些最终记录更新参数。

源影片自带爆炸、飞车、绳索和物理运动。本次新增的是前景分离、层间接力、透视窗口、图像拼接和组合动画；这里没有可独立编辑的电影原CG工程。
