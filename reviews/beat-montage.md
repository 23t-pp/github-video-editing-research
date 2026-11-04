> 返回[研究首页](../README.md) · [全部查询和原始响应](../evidence/search/queries.json) · [结构化审查](../evidence/reviews/beat-montage.json)

# 音乐卡点、情绪混剪与可换素材模板：源码审查

审查时间：2026-11-04T12:11:12.969Z。这是静态源码审查；没有安装、启动、渲染、跑测试或观看样片。因此“有实现”只证明代码存在，不证明画面质量与本机运行效果。所有源码链接固定到commit，星数和推送时间是检索快照。

优先顺序：想要情绪影视混剪和可换素材视觉模板，先看 **easyedit**；想理解并改造最小卡点流水线，先看 **beat-synced-edit**；要Windows图形界面AMV工具，再评估 **BeatSync-Engine**。**montage-ai是非商业许可**。

| 仓库 | 星数 | 最近推送 | 许可 | 真正能复用什么 |
|---|---:|---|---|---|
| [blixvip/easyedit](https://github.com/blixvip/easyedit) | 167 | 2026-10-31 | MIT | 情绪影视混剪 / 可换素材视觉模板 |
| [ZiadAbdelkarim/beat-synced-edit](https://github.com/ZiadAbdelkarim/beat-synced-edit) | 13 | 2026-08-08 | MIT | 卡点剪辑流水线 / JSON白闪模板 |
| [Merserk/BeatSync-Engine](https://github.com/Merserk/BeatSync-Engine) | 75 | 2026-07-06 | AGPL-3.0 | Windows自动AMV/GMV卡点编辑器 |
| [guigulaoshi/music-video-director-skill](https://github.com/guigulaoshi/music-video-director-skill) | 67 | 2026-09-25 | MIT | 歌词意象/情绪弧线的agent剪辑流程 |
| [zhangzhanglaila/ai-montage-agent](https://github.com/zhangzhanglaila/ai-montage-agent) | 39 | 2026-10-22 | MIT | 中文模块化混剪/AI素材筛选流水线 |
| [scherroman/mugen](https://github.com/scherroman/mugen) | 246 | 2023-10-04 | MIT | 经典随机AMV节拍拼接库 |
| [mfahsold/montage-ai](https://github.com/mfahsold/montage-ai) | 63 | 2026-03-09 | PolyForm Noncommercial License 1.0.0 | 完整本地混剪系统 / 非商业源代码 |

## 三种“卡点”要分开理解

真实beat/onset检测会读取歌曲波形后得到一组时刻；规则BPM网格只根据tempo和phase等距铺拍；配置模板则直接消费作者写好的时长。它们都能做有节奏的视频，但不能互相冒充。频谱可视化只让画面随声音动，不自动证明有源素材切镜。

## blixvip/easyedit

本组最贴近情绪混剪和可换素材模板：先研究template/film.js，再用本地素材验证整条流程。

- 固定版本：`b0462b776b5ccd1a2225f35e09ffab2396448a0e`
- 节拍能力：真音频分析：numpy谱通量、自相关估计70–180 BPM、动态规划beat tracker；按实际beat时间取短长镜头，慢歌会插入半拍。
- 依赖：Python 3.10+、Node 22+、FFmpeg；numpy、OpenCV、faster-whisper、yt-dlp；HyperFrames 0.8.40；可选Claude/Codex CLI。
- Windows：README提供easyedit-web.cmd，仓库含Windows启动器。CPU路径和NVIDIA加速均有文档；本次未运行。

- **谱通量+DP跟踪真实beat**：[easyedit/beats.py](https://github.com/blixvip/easyedit/blob/b0462b776b5ccd1a2225f35e09ffab2396448a0e/easyedit/beats.py)。onset_envelope→tempo→track；find_drop结合前后响度与beat strength。
- **切镜实际消耗beat数组**：[easyedit/assemble.py](https://github.com/blixvip/easyedit/blob/b0462b776b5ccd1a2225f35e09ffab2396448a0e/easyedit/assemble.py)。montage_slots使用beats[drop:]，PATTERN=[2,2,1,3,...]确定每个镜头跨几拍；不是仅按常数BPM切。
- **可复用视觉层**：[template/film.js](https://github.com/blixvip/easyedit/blob/b0462b776b5ccd1a2225f35e09ffab2396448a0e/template/film.js)。beatPulse读取E.beats；镜头含push-in/whip/flash，Canvas含逐词字幕和按帧种子的grain。
- **可替换本地素材**：[README.md](https://github.com/blixvip/easyedit/blob/b0462b776b5ccd1a2225f35e09ffab2396448a0e/README.md)。--speech / --montage / --music支持file、URL、search query；可修改curate.json和render/edit.js。

不能据此证明或必须注意：

- 专门做speech→music montage→hero的固定叙事结构，不是任意多轨编辑器。
- 本地素材可替换，但默认会下载YouTube素材；素材许可需自行确认。
- 节拍范围70–180 BPM与短长PATTERN是实现约束；不是经过实测的万能节拍/情绪识别。
- README展示性能和样片，本次只静态审查，未验证渲染结果。

## ZiadAbdelkarim/beat-synced-edit

最适合拆成可维护的小型pipeline；拿beat_map/plan_edit/render_edit做原型，flash_montage单独当换图换视频的确定性模板。

- 固定版本：`48c09c92ee69c2d89b7e44b146bbd7b9c26fff08`
- 节拍能力：主流水线真librosa beat_track→能量/scene标签→beat对齐EDL。独立flash_montage.py不检测节拍，只按seq.json时长拼接。
- 依赖：Python 3.10+、FFmpeg on PATH、librosa、PySceneDetect、OpenCV、NumPy、SciPy。CLI不用AI；skill由Claude编排。
- Windows：通用Python/subprocess+FFmpeg路径；README主要用python3/brew示例，未见Windows专用验证。

- **真实节拍检测**：[beat_map.py](https://github.com/ZiadAbdelkarim/beat-synced-edit/blob/48c09c92ee69c2d89b7e44b146bbd7b9c26fff08/beat_map.py)。analyze_audio调用librosa.beat.beat_track，输出beat_times、RMS、峰谷和top segments。
- **可控beat剪辑计划**：[plan_edit.py](https://github.com/ZiadAbdelkarim/beat-synced-edit/blob/48c09c92ee69c2d89b7e44b146bbd7b9c26fff08/plan_edit.py)。beats_relative用于timeline_start；--beat-stride稀疏切点，--lead/--pin手动指定素材。
- **白闪实际由配置决定**：[flash_montage.py](https://github.com/ZiadAbdelkarim/beat-synced-edit/blob/48c09c92ee69c2d89b7e44b146bbd7b9c26fff08/flash_montage.py)。读取seq[items]；每个dur作为输入时长；xfade offset=acc-flash，总长=sum(dur)-(N-1)*flash。没有调用beat_map。
- **真实FFmpeg组装**：[render_edit.py](https://github.com/ZiadAbdelkarim/beat-synced-edit/blob/48c09c92ee69c2d89b7e44b146bbd7b9c26fff08/render_edit.py)。extract_clip按源入出点编码，concat demuxer拼接，再混入音频；不会自动修复EDL时间空隙。

不能据此证明或必须注意：

- 白闪模板没有beatmap输入，items[].dur与flash overlap决定切点；需要人工/agent预先计算时间。
- 主EDL对齐不等于最终成片已验证：plan_edit可能按源片长度缩短镜头；render_edit连续concat而不使用timeline_start补空隙，短镜头是否造成后续偏拍需要实际样例检查。
- 示例MP4存在，但本次未播放或渲染；视觉质量/Windows兼容性未实测。

## Merserk/BeatSync-Engine

若优先Windows自动生成AMV/GMV，可列试用第一梯队；若要抽代码商用，先审AGPL与依赖。

- 固定版本：`06679c1f28c6d0b56c901495e52497cccebc744a`
- 节拍能力：真librosa onset strength+beat_track，失败可退onset_detect；后续音乐分段、能量切点选择、视觉片段规划，渲染按绝对帧量化。
- 依赖：便携Python 3.13、FFmpeg/ffprobe、Gradio、librosa 0.11、NumPy、OpenCV、cupy-cuda13x[ctk]；可选llama.cpp Vulkan+Qwen3-VL GGUF。
- Windows：明确Windows目标且有install.bat/run.bat/install.ps1，贴合本机。安装器下载模型/CUDA相关依赖，最后执行CuPy GPU自检；不能凭CPU编码选项断言无GPU安装零障碍。

- **真实节拍检测与fallback**：[src/auto_mode/stage1_audio.py](https://github.com/Merserk/BeatSync-Engine/blob/06679c1f28c6d0b56c901495e52497cccebc744a/src/auto_mode/stage1_audio.py)。计算onset_env，beat_track(start_bpm=120只是起始先验)，失败退onset_detect，并用frames_to_time取得时刻。
- **帧锁切点与片段规划**：[src/video_processor.py](https://github.com/Merserk/BeatSync-Engine/blob/06679c1f28c6d0b56c901495e52497cccebc744a/src/video_processor.py)。build_frame_aligned_cut_timeline量化beat_times到输出帧；create_music_video调用build_planned_clip_sequence，失败才随机采样。
- **按音乐特征选择源片段**：[src/auto_mode/stage6_av_planner.py](https://github.com/Merserk/BeatSync-Engine/blob/06679c1f28c6d0b56c901495e52497cccebc744a/src/auto_mode/stage6_av_planner.py)。每个slot采样能量、impact、rhythm、novelty等特征，形成target并materialize源片段。
- **Windows安装依赖成本**：[scripts/install.ps1](https://github.com/Merserk/BeatSync-Engine/blob/06679c1f28c6d0b56c901495e52497cccebc744a/scripts/install.ps1)。下载便携Python、FFmpeg、llama.cpp、Qwen GGUF；pip装CuPy并在收尾执行cupy.arange和sum GPU检查。

不能据此证明或必须注意：

- AGPL-3.0，复制/修改/分发须先核对许可条款，不能当MIT素材包。
- README提供CPU H.264输出，但安装脚本仍安装CuPy并执行GPU运算自检，CPU-only整条链路未证实。
- Qwen模型、CUDA runtime、Vulkan与NVENC会增加环境成本；本次未安装、启动或渲染。
- 这是完整编辑应用，不是一个仅替换素材即可套出的固定成片工程。

## guigulaoshi/music-video-director-skill

更适合作为“如何带agent做音乐MV”的流程参考，不是现成套版；可复用EDL格式、音频分析和渲染器。

- 固定版本：`66de7f0dcc8d714c4f6cd9988a4d214387caee36`
- 节拍能力：madmom可选，fallback为librosa HPSS节拍检测再退plain librosa；downbeat简化为每4拍，歌词转写有实现。创意匹配由agent产生EDL。
- 依赖：FFmpeg、Python、librosa、openai-whisper/stable-ts、scenedetect、ffmpeg-python、yt-dlp；可选madmom；外部能读图/执行shell的agent。
- Windows：README列Windows winget FFmpeg入口，Python CLI跨平台；madmom编译与Whisper依赖较重，未运行Windows测试。

- **检测有真实三级实现**：[mvd/audio.py](https://github.com/guigulaoshi/music-video-director-skill/blob/66de7f0dcc8d714c4f6cd9988a4d214387caee36/mvd/audio.py)。_detect_beats依次尝试madmom、HPSS+librosa、plain librosa；downbeat_times=beat_times[::4]。
- **渲染器真实实现**：[mvd/renderer.py](https://github.com/guigulaoshi/music-video-director-skill/blob/66de7f0dcc8d714c4f6cd9988a4d214387caee36/mvd/renderer.py)。读取EDL cuts/audio_file，为每个cut抽取编码、concat、混音。
- **创意分工边界明确**：[README.md](https://github.com/guigulaoshi/music-video-director-skill/blob/66de7f0dcc8d714c4f6cd9988a4d214387caee36/README.md)。Division of labor明确Python CLI做技术工作，AI agent做scene description/edit planning/editorial judgment；CLI无AI API调用。

不能据此证明或必须注意：

- 没有自动语义剪辑模型内置在CLI：镜头描述、歌词意象匹配、情绪弧线由外部agent判断。
- 每四拍标downbeat是假定4/4，不是音乐学上已检测小节强拍。
- renderer消费cuts并FFmpeg拼接，不能单靠说明保证agent生成EDL合理。

## zhangzhanglaila/ai-montage-agent

中文二次开发可研究；需把mock/fallback变成显式质量警报并补真实素材端到端验证，再用于批量成片。

- 固定版本：`0a010202e2ede7c9b2e20e06d10520942e84a44c`
- 节拍能力：librosa真beat/onset/RMS；sync优先用实际beats[end_idx]-beat_time。没检测到beat则120 BPM均匀网格；缺librosa则模拟20拍/10秒。
- 依赖：Python、FFmpeg、librosa、PySceneDetect、OpenCV、PyTorch/torchvision、transformers、open-clip、FastAPI、Playwright；可选Whisper/madmom/Redis。
- Windows：Python/FFmpeg理论可移植；依赖较重。README与代码应按Windows路径/字体/编码实测，目前未安装执行。

- **节拍检测及模拟边界**：[packages/montage/beat.py](https://github.com/zhangzhanglaila/ai-montage-agent/blob/0a010202e2ede7c9b2e20e06d10520942e84a44c/packages/montage/beat.py)。analyze使用librosa.beat_track和RMS；空检测np.arange(0,duration,0.5)，ImportError调用_mock_analysis固定10秒/120 BPM。
- **切镜优先真实边界**：[packages/montage/sync.py](https://github.com/zhangzhanglaila/ai-montage-agent/blob/0a010202e2ede7c9b2e20e06d10520942e84a44c/packages/montage/sync.py)。sync按beats[end_idx].time-beat_time得duration，按可用画面和速度范围约束；短xfade最大0.08秒。
- **可复用风格预设**：[packages/video_enhancement/src/styles/mtv.json](https://github.com/zhangzhanglaila/ai-montage-agent/blob/0a010202e2ede7c9b2e20e06d10520942e84a44c/packages/video_enhancement/src/styles/mtv.json)。JSON含very_fast、hard_cuts、vibrant、energy_mapping；是参数预设，不是完整成片模板。
- **流水线与交付格式**：[packages/montage/pipeline.py](https://github.com/zhangzhanglaila/ai-montage-agent/blob/0a010202e2ede7c9b2e20e06d10520942e84a44c/packages/montage/pipeline.py)。存在镜头去重、BGM清理、音视频组装流程；目录另含timeline_export/otio_exporter.py。

不能据此证明或必须注意：

- ImportError直接返回_mock_analysis的20个模拟beat，运行成功也不代表真实卡点。
- 未检出beat时生成120 BPM网格，应显式区分fallback输出。
- 模板JSON是风格参数（节奏、转场、颜色）而非带素材占位符的完整可视项目。
- 多模块广泛存在不代表每项端到端稳定；本次只审核心beat/sync/pipeline与export。

## scherroman/mugen

保留作算法和API设计参考；新项目优先现代小pipeline，避免先移植整个旧依赖栈。

- 固定版本：`d85c082a0ec0b68e458d7060d19d9b84893aa2ea`
- 节拍能力：真librosa beat_track/onset检测；按events.segment_durations从源素材抽取片段，支持events-speed/offset和按段分组。
- 依赖：conda Python3.9、FFmpeg、libsndfile、Tesseract；锁MoviePy1.0.3/librosa0.8.1/NumPy1.22.2/Pillow9.3.0等旧依赖。
- Windows：README声明支持Linux/macOS/Windows，用Miniconda安装；旧版本依赖不宜直接放入现有Python环境。

- **真实beat/onset事件API**：[mugen/audio/Audio.py](https://github.com/scherroman/mugen/blob/d85c082a0ec0b68e458d7060d19d9b84893aa2ea/mugen/audio/Audio.py)。_beats调用librosa.beat.beat_track(units=time)；_onsets尝试onset_detect；包装成EventList。
- **事件转真实源片段**：[mugen/video/MusicVideoGenerator.py](https://github.com/scherroman/mugen/blob/d85c082a0ec0b68e458d7060d19d9b84893aa2ea/mugen/video/MusicVideoGenerator.py)。generate_from_events取events.segment_durations；SourceSampler.sample_with_filters选片段，再组MusicVideo。
- **旧栈与Alpha状态**：[setup.py](https://github.com/scherroman/mugen/blob/d85c082a0ec0b68e458d7060d19d9b84893aa2ea/setup.py)。Development Status::3-Alpha；MoviePy1.0.3/librosa0.8.1/numpy1.22.2均明确锁定。

不能据此证明或必须注意：

- 最近推送2023-10-04，维护显著放缓；setup标Alpha。
- 核心是随机素材采样与过滤，没有歌词语义匹配/现代AI素材生成。
- onset调用路径为librosa.beat.onset.onset_detect，是否兼容其锁定依赖需运行检查，不能凭静态读取视为已测试。
- 许可宽松与测试目录存在不等于现代Windows/最新Python可直接使用。

## mfahsold/montage-ai

只作非商业学习/设计比较；商业项目优先MIT候选。

- 固定版本：`2e9dc03bfd0c320cf30f2762791bcccfd1d12b06`
- 节拍能力：可选madmom RNN真beat/downbeat；默认FFmpeg分析用峰值推tempo/phase，再生成规则beat网格；峰不足则响度启发式规则网格。不可统称每拍都真实检测。
- 依赖：Python、FFmpeg、MoviePy2.2、OpenCV、scenedetect、Flask、Redis/RQ、Kubernetes客户端、OpenTimelineIO；madmom/VLM/GPU为可选。
- Windows：主文档以Docker/Linux shell/容器部署为主；Windows可能经Docker Desktop/WSL接入，原生Windows未验证，系统规模和依赖重。

- **许可证实际限制**：[LICENSE](https://github.com/mfahsold/montage-ai/blob/2e9dc03bfd0c320cf30f2762791bcccfd1d12b06/LICENSE)。标题PolyForm Noncommercial License 1.0.0，Noncommercial Use Only；不能把API NOASSERTION当无约束。
- **真beat与规则fallback区别**：[src/montage_ai/audio_analysis.py](https://github.com/mfahsold/montage-ai/blob/2e9dc03bfd0c320cf30f2762791bcccfd1d12b06/src/montage_ai/audio_analysis.py)。get_beat_times优先cloud/madmom；_ffmpeg_estimate_tempo挑tempo/phase后np.arange，峰不足按响度heuristic生成网格。
- **风格配置可复用思路**：[src/montage_ai/styles/mtv.json](https://github.com/mfahsold/montage-ai/blob/2e9dc03bfd0c320cf30f2762791bcccfd1d12b06/src/montage_ai/styles/mtv.json)。mtv preset有快速节奏、hard_cuts、vibrant、sync_to_beats参数。
- **依赖默认值**：[requirements.txt](https://github.com/mfahsold/montage-ai/blob/2e9dc03bfd0c320cf30f2762791bcccfd1d12b06/requirements.txt)。注明audio_analysis FFmpeg-first、librosa/numba omitted，madmom仅optional。

不能据此证明或必须注意：

- 实际LICENSE为PolyForm Noncommercial，GitHub API只有NOASSERTION；不适合未经授权抽取商业流水线。
- 默认requirements特意省略librosa/numba，madmom也可选；默认fallback是估计tempo后规则grid，不能当madmom质量宣传。
- 风格JSON可读，但完整系统复杂、目录和部署文档多；本次未执行测试或部署。

## 搜索与排除记录

本组遵守共享repo search额度，仅做8条扩展query，per_page=30，不设最小星数、不按星数排除小项目。读取指定仓库metadata/tree/raw不占repo search额度。中文“卡点”产生大量银行卡/打卡等词切分噪声；英文短语更准确。一次只保留GitHub相关性返回第一页，故不是穷举。

| Query | 请求UTC时间 | 返回数 | 总命中 | 原始JSON |
|---|---|---:|---:|---|
| "beat sync" video | 2026-11-04T12:05:38.5331662Z | 30 | 269 | search-1.json |
| "music video generator" | 2026-11-04T12:05:40.7032941Z | 30 | 181 | search-2.json |
| "beat detection" montage | 2026-11-04T12:05:43.1991843Z | 0 | 0 | search-3.json |
| AMV generator | 2026-11-04T12:05:44.2278023Z | 15 | 15 | search-4.json |
| 卡点 | 2026-11-04T12:05:46.0569531Z | 30 | 2087 | search-5.json |
| 混剪 | 2026-11-04T12:05:48.0864689Z | 30 | 292 | search-6.json |
| "lyric video" generator | 2026-11-04T12:05:50.0358409Z | 30 | 92 | search-7.json |
| "beat-synced" | 2026-11-04T12:05:52.5278129Z | 30 | 508 | search-8.json |

合并后179个唯一候选，原始metadata在candidates.json；重复召回记录在review.json的dedup。补充指定seed：blixvip/easyedit由主流程发现后直接读取，不消耗本组额外search query。

- **Meteor8/beats-synced-video-generator**：2021年旧demo、无LICENSE；beat1.py确有librosa真实检测，但vid.py硬编码./beats/a1.csv、./video/1.mp4、./music/a.mp3，随机抽20–480秒源片且节拍截到0.1秒。可学最小原理，不适合当可换素材模板或现代工具。 [固定源码](https://github.com/Meteor8/beats-synced-video-generator/blob/436e2e27987240da57fbf5d947146cf6d3e13592/vid.py)
- **Tanishk-11/BeatSync**：描述为视频测心率健康应用，beat同词不同义，非音乐剪辑。
- **ialakey/music-video-generator**：描述为单图+慢放混响+频谱可视化；未作源码审查，不列入真实切镜工具推荐。
- **riskcapital/ghost-arcade**：VJ/投影映射与live可视化，不是本组需要的素材切镜模板。
- **for-he-s-loved/awesome-beat-sync-video-editors**：资源目录，非可运行剪辑器；可做补充索引但不能作为已审实现。

## 实际执行过的命令和输出含义

以下命令使用GitHub CLI绝对路径；没有执行仓库中的程序。所有metadata.json、commit.json、tree.json和source/文件均来自CLI API。Python检查失败（系统只有WindowsApps别名），后续使用PowerShell和本机Node整理报告；没有为审查安装Python。Node直接写文件曾返回EPERM，改为Node生成JSON到标准输出，PowerShell负责保存。

```powershell
$gh = "C:\Program Files\GitHub CLI\gh.exe"
$query = '"beat sync" video'
& $gh api --method GET search/repositories -f "q=$query" -f "per_page=30"
# 对另7条query同样执行；search-log.json记录UTC时间、total_count、返回数和文件名。

$repo = "blixvip/easyedit"
& $gh api "repos/$repo"
# metadata：星数、许可证API判定、默认分支、pushed_at。
& $gh api "repos/$repo/commits/main"
# 实际执行时main由metadata.default_branch动态取得；commit.json中的sha是固定引用。
$sha = "b0462b776b5ccd1a2225f35e09ffab2396448a0e"
& $gh api "repos/$repo/git/trees/$($sha)?recursive=1"
# tree列出文件路径，先确认不是只有README的宣传仓库。
& $gh api "repos/$repo/contents/easyedit/beats.py?ref=$sha" -H "Accept: application/vnd.github.raw+json"
# raw文件可静态确认真实算法；ref固定后不受默认分支后续更新影响。
rg -n "beat|onset|tempo|np.arange|mock|PATTERN" work/beat_montage/*/source
# 检索命中只负责定位；报告依据上下文阅读后的函数行为。
powershell -File work/beat_montage/build-review.ps1
# 本地作者脚本：合并原始搜索metadata，并生成review.json/review.md，不运行仓库代码。
```

若复现下载，可逐项使用review.json的repo/sha/evidence.path构造相同API请求。GitHub搜索会随时间变化，因此精确复核请先读留存的search-*.json，而不要期待今天重搜结果顺序完全相同。

## 学习路径

1. beat-synced-edit：从beat_map的时间数组，到plan_edit的JSON EDL，再到render_edit的FFmpeg串联，理解素材如何真正切到音乐上。
2. easyedit：学习语音段进入drop、镜头短长pattern、局部镜头策展，以及视觉层读取统一时间轴的做法。
3. music-video-director-skill：学习歌词、情绪弧线和镜头语法如何变成可审阅EDL；外部agent的判断仍需人审。
4. BeatSync-Engine / ai-montage-agent：再研究能量分区、素材可用长度、速度约束、帧量化和转场重叠补偿。
