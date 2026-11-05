# 弯心 / APEX：双分轨与最终总声

三条文件均为60秒、48kHz、立体声、PCM24，精确2,880,000个采样帧。

- `hyperframes/assets/audio/score-mix.wav`：已自动化和统一增益后的原创配乐。
- `hyperframes/assets/audio/source-mix.wav`：按锁定镜头表铺设的30条原混音cue，含引擎、动作等声音，也可能保留影片原配乐、对白。
- `hyperframes/assets/audio/master.wav`：上述两条的精确求和。

**OpenChatCut中两条分轨各设音量1，才能重建master；不要再叠加master或原始score.wav，不要同时打开原视频音轨。** 如只需成品总声，单独使用master即可。

## 本轮实际测量

总声综合响度 **-16.50 LUFS**，真峰值 **-2.04 dBTP**，LRA **11.10 LU**。三条均经过FFmpeg完整解码，文件采样数/采样率/通道数检查通过。

PCM24整数域逐采样验证：`score-mix + source-mix - master`最大绝对误差 **0 LSB**，非零差异样本 **0**。总声仅使用两轨共同的线性增益，未在master上另加无法回分到两轨的非线性处理。

|文件|综合响度 LUFS|真峰值 dBTP|LRA LU|
|---|---:|---:|---:|
|score-mix.wav|-16.70|-2.71|11.00|
|source-mix.wav|-28.48|-11.69|18.60|
|master.wav|-16.50|-2.04|11.10|

## 剪辑与包络

按`shots[].startFrame`精确定位，每个24fps画面帧对应2000个音频采样；每条cue从自身第0个采样开始，截取`frames × 2000`个采样，不再重复加sourceIn。sourceIn仅记录源片取样证据。

S04采用片11、原片入点3930.613333秒，锁定sourceGain=0.22。输入edit.json SHA256：`4e03aea0fbe5c86631265c55147594f8b06b4e88eecb26a6208efd49d5af473b`；全部cue的SHA256、放置位置和包络参数在`mix-automation.json`。

原声先做95Hz高通与10kHz低通，弱化原混音中无关低频/高频；通用淡入6ms、淡出最长65ms，短动作镜头3ms/最长28ms，S42采用250ms/380ms。它们用于抑制剪接爆音，不改变画面对齐。

sourceGain严格采用镜头表作为基准；只有过强cue额外向下约束，让其持续RMS不超过同期配乐参考RMS的45%。安静cue不会被自动拉响，避免一并抬高影片原BGM。轻微能量跟随包络在0.88–1范围，音乐仅作最多0.65dB的浅让位。滤波、包络和RMS约束都不是人声/配乐分离，不能保证原声完全没有电影音乐。

最后两轨共同增益-0.540dB，目标−16.5 LUFS，并以−1.6dBTP限制共同增益上界。此方法保留情绪段落的动态，最终值以实测为准。分轨量化后用整数相加生成master，确保重新叠加时没有一轨被重复母带处理。

## 重建命令

使用已有numpy/scipy/soundfile的Python和FFmpeg，从工作区根运行：

```powershell
$mixPython = '.\work\reference-library-20261105\audio-env\Scripts\python.exe'
& $mixPython '.\outputs\fast60\music\build_final_mix.py'
```

FFmpeg不在默认工具目录时，先设置`FFMPEG_PATH`。若没有上例venv，可另建隔离Python环境，并安装本目录`requirements-score.txt`的三个依赖，再用该Python运行同一脚本；无需分离模型。脚本读取当前edit.json、score.wav和cue文件，输出两分轨、总声、报告和自动化参数；修改cue后必须重跑，旧报告的SHA不能代表新cue。执行末尾会核对edit.json及所有cue未在混音期间被修改。`mix-envelopes.npz`保留逐采样音乐让位曲线，主编辑参数在Python源码与mix-automation.json中。

## 验收范围

**制作代理没有实际监听。** 本轮完成的是信号/文件验收，未宣称听过引擎、擦撞或直升机声音；这些分类来自镜头表。人工仍需试听原配乐残留、源声是否刺耳、音乐是否被遮蔽、画面声响是否主观同步，以及耳机/小扬声器的低频表现。响度、峰值与精确求和通过，不能替代这些听感判断。
