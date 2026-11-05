# 三处真实手部短alpha

三套均为1920×1080 RGBA PNG、25fps，从 `000000.png` 开始。`alpha-manifest.json` 给出本地帧与B视频asset帧的对应；`validation.json` 已逐帧确认RGB与实际B视频解码结果完全相同，黑边alpha为零。没有生成手、补出不存在的手或光流插帧。

| 目录 | 源asset帧（含首尾） | 使用说明 |
|---|---|---|
| B04-gear-hand | 12–24，13帧 | 首两帧透明；源F12无手，F13严重模糊，F14起干净前景。手握的少量黑色档把顶端随手保留。 |
| B03-switch-hand | 12–26，15帧 | 手/拇指为主，避免把大块驾驶室当作前景。末两帧手退场且严重模糊，alpha为空，应用同源完整B承接。 |
| B01-steering-hand | 12–20，9帧 | 蓝光下的真实手/前臂与少量握持轮缘；强运动模糊保留。不得冻结第8帧填更长窗口。 |

`alpha-evidence.png` 每行三列依次为源画面、棋盘合成、灰度alpha。三套全帧联图均已实际查看。夜景模糊边缘属于本地手工轮廓/GrabCut近似，不宣称逐毛发或透明运动模糊的完美分离。

`roto-keyframes.json` 可逐帧改轮廓。工具位于项目 `tools/dynamic-alpha.py` 与 `dynamic-alpha.mjs`：手工关键帧优先，短程LK和RANSAC只填间隔，GrabCut只在轮廓附近细化；可设 `emptyFrames` 明确禁止凭空造前景。

重跑：在本工作区使用可写Node执行 `node tools/dynamic-alpha.mjs <roto-keyframes.json>`。Python从本任务隔离的 `work/reference-replay-v07/python-deps` 加载OpenCV，不修改全局环境。工具只读真实B视频，并将PNG编码字节交给Node落盘。

PNG是无损源，不应直接假设OCC能把PNG序列导成一条视频；若要导入OCC，应另编码并实际验证VP9-alpha WebM或可用的透明MOV代理。普通MP4不携带透明度。
