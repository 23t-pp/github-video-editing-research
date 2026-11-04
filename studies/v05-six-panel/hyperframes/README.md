# HyperFrames 六格卡片工程

此目录可以单独复制。两段素材、一次混音与离线GSAP已包含，不需要整部电影。

先修改 `sample-config.json` 中的 `gridScale`（卡片组大小）或 `order`（出场顺序）；固定规格是1920×1080、24fps、3列2行。随后使用本机可用Node运行 `build.mjs`，再运行 `hf.mjs check .` 和 `hf.mjs preview . --background`。

本机快速使用：

```powershell
$nodeExe='C:\Users\PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
& $nodeExe .\build.mjs
& $nodeExe .\hf.mjs preview . --background --no-open --no-proxy --port 5210
```

打开浏览器 `http://127.0.0.1:5210/#project/hyperframes`。`Open-Preview.ps1` 包装了上述预览动作。

完整重渲染使用 `Render-Sample.ps1`；它实际调用官方HyperFrames输出PNG序列，再用 `encode.mjs` 合成MP4。这个适配是为了处理本机FFmpeg直接写文件失败的问题。渲染图像和动画仍由HyperFrames完成。

压缩包不包含可以重新生成的图片缓存和渲染PNG；首次build会从附带的短片生成。中间帧保留在本工程 `work/`，成片输出到本工程的上一级文件夹。

`build.mjs` 会重写 `index.html`。如果在Studio或HTML中手工修改了动画，请先备份；参数生成流程不会自动合并手动编辑。当前源码中的工具路径适配这台Windows电脑，换电脑要修改Node、HyperFrames、Chrome、FFmpeg路径。

完整中文教程在交付目录 `README_中文学习指南.md`，包含素材时间码、关键帧解释、OpenChatCut教学方法和验证证据。
