# NIGHT RELAY / 夜行接力：60秒原创配乐

双分轨与总声的重建方法、OCC音量设置和最终测量见[FINAL-MIX.md](FINAL-MIX.md)；本页记录原创配乐本身，`score.wav`与用于成片的`score-mix.wav`用途不同。

成品为 [`../hyperframes/assets/audio/score.wav`](../hyperframes/assets/audio/score.wav)：48kHz、立体声、24-bit PCM，**2,880,000个采样帧，正好60.000秒**。128 BPM，4/4拍，32小节。每拍0.46875秒 / 22,500个采样帧，每小节1.875秒；没有用拉伸音频凑时长。

本次从数学振荡器、噪声和包络创作音色与音符，没有下载商业歌曲，没有引用影片原配乐、音频采样或现成旋律。它是独立配乐，尚未与影片引擎、对白和环境声混音。

## 先试听，再做听感决定

- [街头段试听：7.5–22.5秒](preview-street.wav)
- [高速段试听：30–52.5秒](preview-main.wav)
- [完整60秒WAV](../hyperframes/assets/audio/score.wav)

**已经实际合成、导出并执行文件及信号检查；制作代理没有实际监听音频，不能把本次检查称为听感验收。** 人工试听时要确认合成器是否刺耳、低频是否浑浊、主riff能否留下记忆点、主段是否足够有推进感。最后仍需结合源引擎/对白验收，不能仅凭波形和响度判定“高燃”。

## 编曲与画面接口

主riff用D小调的 `D–A–C–D / F–E–D–C–A`轮廓，按D、降B、F、A和声根音变奏。A和弦回转用升C形成属和弦张力；街头与高速段复用同一两小节主题，最强段加入少量高八度回应。音色包含失谐谐波合成器、短FM敲击、中心低音、立体声铺底、合成kick/snare/clap/hi-hat/tom和噪声上升音。噪声、鼓与旋律的随机细节使用固定种子，脚本可复现。

|时间|小节|编曲动作|实测该段RMS dBFS|
|---|---|---|---:|
|0–7.5|1–4|暗色铺底、主题片段、低音逐步进入，鼓保持稀疏|−27.13|
|7.5–22.5|5–12|完整主题与切分贝斯、鼓组、侧边短音；两小节/四小节乐句过门|−16.30|
|22.5–30|13–16|半拍感、减法；约26.25–28.125秒抽空，最后一小节鼓滚与上升音|−25.54|
|30–45|17–24|完整高速主题、中心低音与强鼓回归|−16.01|
|45–52.5|25–28|更密帽镲、高八度回应、过门；减少部分琶音，给引擎瞬态留位置|−15.19|
|52.5–58.125|29–31|减法尾声，鼓和低音退出，产生减速感；BPM保持128|−25.81|
|58.125–60|32|短有力低音/五度终止音与尾响，最后半秒淡到精确零点|−20.66|

最强段RMS比前一主段高约0.82dB，同时提高鼓触发密度；这只是客观编排/信号证据，不替代听感判断。贝斯与合成器在kick后约140ms内回避，合成器中心声部约650–2300Hz略削，低频保持居中。立体声宽度主要来自失谐铺底、侧边敲击与交叉延迟；没有把全频谱铺满来替代引擎声。

## 哪些时间可以用来剪画面

[`beat-markers.json`](beat-markers.json)与[CSV](beat-markers.csv)给出128个**作曲时钟拍位**、段落边界和938个音色触发事件。它们来自本曲的程序编排，不是假装从混合音轨“检测成功”的固定网格。静音/抽空处的网格仍存在，但并非每拍都有声响；连续快切应优先选实际kick/snare/riff事件。

[`validation.json`](validation.json)另记录399个谱通量起音候选、104个kick的鼓分轨实测波形峰。起音分析使用1024样本STFT、240样本hop（5ms）；时间为分析窗中心，存在约10ms窗定位误差，不等于声波起始样本。鼓峰是每次编排kick后45ms内的最大采样能量，可能受同刻镲片影响，不能把它单独当作节拍检测。

例如编排kick为7.500秒，鼓分轨峰实测7.500979秒；1.875秒kick的峰为1.876562秒。画面卡点应依实际需要落在编排触发点或峰前后，而不是再根据“音量最大”重新推一套BPM。60秒是结束边界，不是第129个发声拍。

## 混音源文件与复跑

- `compose_score.py`：全部音符、音色、编排、分轨和MIDI生成源码，可编辑根音、主题、鼓型、力度、滤波及延迟。
- `night-relay-128.mid`：type-1 MIDI、960 PPQ、128 BPM、5轨；包含958个音符/鼓触发和段落标记。MIDI不携带Python合成音色、噪声特效或母带处理，导入DAW后需自行配音色。
- `note-events.json`：可编辑音符与鼓事件明细。
- `stems/drums.wav`、`bass.wav`、`synths.wav`、`atmosphere.wav`：48kHz立体声PCM16分轨，采用共同增益，合计近似重建`score-premaster.wav`；PCM16量化存在微小差别。它们尚未套最终母带响度处理，不能直接与母带叠加。
- `master_score.mjs`：FFmpeg双遍响度处理、stdout写文件、试听片段导出。
- `validate_score.py`：采样数、有限值、结尾、MIDI结构、分段能量和起音测量。

本轮实际依赖Python 3.12.14、numpy 2.5.4、scipy 1.18.1、soundfile 0.14.0、Node 24.22.1、FFmpeg 9.0.2。以下从工作区根目录运行；可将Python/Node变量改为自己的可写运行时，不要求修改系统设置。FFmpeg不同位置用`FFMPEG_PATH`覆盖。

```powershell
$scorePython = '.\work\reference-library-20261105\audio-env\Scripts\python.exe'
$scoreNode = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
& $scorePython '.\outputs\fast60\music\compose_score.py'
& $scoreNode '.\outputs\fast60\music\master_score.mjs'
& $scorePython '.\outputs\fast60\music\validate_score.py'
```

需要自行准备Python环境时，仅需numpy/scipy/soundfile，不依赖分离模型或云服务。脚本写出位置由脚本自身目录推导，WAV不会覆盖源影片。

## 本轮实际验证结果

最终WAV综合响度 **−16.03 LUFS**、真峰值 **−2.17 dBTP**、LRA **11.10 LU**；母带目标分别为−16、−2.2和9，实测LRA没有精确达到目标，保留了引子/抽空与主段的差异。FFmpeg报告里`input_*`才是待测最终文件的实测值，`output_*`为再套一遍测试滤镜的预测，不能混用。

采样数、48kHz、双声道、24-bit、有限值、无采样削波、最后两通道归零、MIDI结构与128拍终点均通过。SHA256为`2362fd21c7d9ced0b30f8e88fadc9a325a70b6e3ee53ffc2d3768bafe3a3a68d`。母带测量完整记录见[`mastering-report.json`](mastering-report.json)。

后续源声混音建议先把配乐作为独立bus保留，再按发动/换挡/碰撞的实际位置做短时自动化；不要仅把源声直接加到−2.17dBTP的母带上，否则叠加可能过载。人声清晰度、引擎主体感与最终总声真峰值，留给第二步实际混音验收。
