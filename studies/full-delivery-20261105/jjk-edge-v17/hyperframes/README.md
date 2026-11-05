# HyperFrames可编辑工程

本项目为《挚友 · EDGE》一分钟混剪，24fps、1440帧、1920×1080。用户指定V17主参考、V02字效和edge.mp3音乐。

先读上一级 [学习总结与命令](../学习总结与命令.md)，再修改工程。已经准备好用于预览与再渲染的短片段、60秒master、逐帧透明前景、字体、镜片坐标和动画代码。

## 本机启动

在本目录打开PowerShell：

```powershell
$jjkPy = 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$jjkNode = 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
& $jjkPy -X utf8 .\composition.py
& $jjkNode .\hf.mjs preview . --port 5230 --no-open
```

浏览器访问 `http://127.0.0.1:5230`。服务已经运行时直接访问，避免重复启动。`hf.mjs`使用本机已安装的HyperFrames 0.8.216、Chrome和FFmpeg；换电脑时可通过环境变量或修改包装器路径适配。

## 修改入口

- `edit.json`：67镜的时间、素材入点、5组大字、前景、窗口、闪光和音乐位置。
- `composition.py`：窗口位置、纸边轮廓、半脸对位、镜片遮罩与整体合成算法。
- `typefx.py`：slam、twin、ribbon、orbit四种字效运动。
- `assets/alpha/X-awaken`、`X-palm`：逐帧RGBA；PNG编号沿准备素材文件帧号，正式区间从000012开始。
- `motion/lens-keyframes.json`：真实C07镜片的人工圆心、半径与源动画跳变。
- `assets/fonts/heavy.ttf`：按现用文字生成的粗中文字体子集。增加新汉字需重做字体子集或换为覆盖这些字的本地字体，并更新`@font-face`。

修改JSON后运行`composition.py`生成`index.html`。Studio直接改HTML时，再次生成会将旧HTML保存在`.source-backups/*.html.bak`；生成器不会把Studio改动自动合并回JSON。

## 再渲染

```powershell
& $jjkPy -X utf8 .\render.py --work .\.render-cache
```

按72帧一段调用真实HyperFrames CLI，保存PNG后用FFmpeg合成成片和20段OCC插片。完整成片写到上一级`挚友_EDGE_一分钟.mp4`，插片写到上一级`occ-effects`。

只改了32秒附近的大掌时，可以单独渲染第10段（0基，720–792帧），再重编码总片：

```powershell
& $jjkPy -X utf8 .\render.py --work .\.render-cache --chunks 10
& $jjkPy -X utf8 .\render.py --work .\.render-cache --encode-only
```

`--encode-only`要求同一缓存目录已经具有完整1440帧。第一次重新渲染请执行完整命令。预览使用视频，离线导出用对应的真实源帧PNG，二者共用图层与动画规则。

普通预览和导出使用Python标准库、Node、已安装的HyperFrames、FFmpeg与Chrome。重新抠像另需OpenCV与NumPy；当前已保留完成的透明序列，普通修改无需再跑分割。

当前CLI lint实测0错误、8警告，提示复用媒体、密集alpha帧与字块建议拆分子合成；runtime validate已通过，未发现控制台错误，抽检3个文字元素通过其对比度检查。完整检查范围见上级质量记录。
