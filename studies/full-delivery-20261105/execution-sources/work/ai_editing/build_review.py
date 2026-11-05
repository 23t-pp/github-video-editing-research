import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))

dates = {r['repo']: r for r in read('core-code-dates.json')}
records = []

def add(repo, category, template, beat, dependencies, windows, limits, recommendation, audience, output, evidence):
    folder = repo.replace('/', '--')
    meta, commit = read(folder + '/metadata.json'), read(folder + '/commit.json')
    sha = commit['sha']
    ev = []
    for claim, path, line, detail in evidence:
        local = ROOT / folder / 'source' / path
        assert local.exists() and local.stat().st_size, str(local)
        assert line <= len(local.read_text(encoding='utf-8').splitlines()), (path, line)
        ev.append(dict(claim=claim, path=path, url=f'https://github.com/{repo}/blob/{sha}/{path}#L{line}', detail=detail))
    records.append(dict(repo=repo, url=meta['html_url'], category=category, is_template=template, beat_capability=beat,
        license=meta.get('license', {}).get('spdx_id'), stars=meta['stargazers_count'], pushed_at=meta['pushed_at'], sha=sha,
        sampled_core_commit=dates[repo], evidence=ev, dependencies=dependencies, windows=windows,
        limitations=limits, recommendation=recommendation, audience=audience, output=output))

add('0xsline/OpenChatCut', '可编辑AI时间线 + 用户素材 + 音乐卡点', True,
    '源码有两条真实音频分析路径：无模型 spectral-flux→自相关BPM→相位网格，及 Beat This ONNX beat/downbeat 推理；music_edit_plan→sync_cuts_to_music 将计划落为时间线 split。并非仅加BGM。',
    'Node.js 24.x、React/TypeScript/Electron、Remotion、FFmpeg、ONNX Runtime；AI对话依选用API/已有代理订阅，本地分析模型需下载。Beat This模型文件约83MB是下载大小，不是显存要求；未找到适合一概而论的最低显存。',
    '有win32-x64桌面打包脚本与Windows专用CI路径；节奏worker可选DirectML/CUDA并CPU回退。Windows运行未实测，源码安装较重。',
    ['AGPL-3.0仓库；package.json写AGPL-3.0-or-later。依赖Remotion及模型权重各有独立授权，未完成它们的授权审查。', '传统detect_beats支路的downbeat为4/4启发式，变速/自由节奏/非4拍歌曲不能保证准确。', '发现卡点切分执行路径，不代表系统会自动挑出好镜头；镜头排序、语义匹配、节奏质量仍需小样验证。', '模板工具复用整个ProjectDoc/MG与风格，未证实所有内置模板都提供傻瓜式可换素材槽位。'],
    '本组最值得优先做20秒小样的整合候选；同时要卡点、AI参与、保留可改工程时优先。',
    '愿意配置模型/API、希望AI剪辑后仍能手工调整的人；开发者二次封装。',
    '可编辑ProjectDoc、多轨时间线、MP4、FCPXML；另有剪映草稿导出CLI路径，依赖capcut-cli。',
    [('真实传统节拍分析', 'src/audio/beats.ts', 61, 'onsetEnvelope、estimateTempo、fitBeatGrid、pickDownbeats、analyzeAssetBeats。'),
     ('神经节拍模型推理与CPU回退', 'desktop/native-rhythm-worker.ts', 148, 'onnxruntime session.run({spect})读取beat/downbeat；provider失败回退cpu。'),
     ('卡点计划真实写入时间线', 'src/agent/tools/music-intelligence-tools.ts', 182, 'buildMusicSplitActions生成split action，syncCuts调用ctx.commands.batch。'),
     ('模板可保存/应用完整工程', 'src/agent/tools/template-tools.ts', 288, 'manage_template支持get/list_assets/apply/copy_assets/save，apply走applyDoc。'),
     ('存在可编辑参数的MG模板', 'assets/templates/openchatcut-templates.json', 2, 'JSON包含props及内嵌code，实例Bar Chart读取title/label/val/color等props。'),
     ('工程导出', 'src/export/fcpxml.ts', 1, '源文件实现FCPXML导出；并非只能输出成片MP4。'),
     ('模型固定revision和文件校验', 'shared/vector-inference-contract.ts', 25, 'RHYTHM_INFERENCE_CONTRACT固定musetric/beat-this-onnx版本、采样率及sha256。'),
     ('Windows支持与Node要求', 'package.json', 14, 'Node>=24<25；desktop:dist:win脚本调用win32-x64准备及electron-builder。')])

add('modelscope/FunClip', '真实用户素材的语音/字幕驱动剪辑；可选LLM高光', False,
    '所审查核心剪辑按转录文本/说话人/时间戳截取与拼接；未见用BPM或音乐拍点决定切点的实现。requirements里有librosa不等于已经卡点。',
    'Python、PyTorch/torchaudio、FunASR/Paraformer及可选声纹模型、Gradio、MoviePy1.0.3、FFmpeg。手选转录文本可全本地且无需LLM API；AI选段可用LLM API，可选TwelveLabs会上传本地视频。显存视模型，无统一最低值。',
    '安装文档有PowerShell独立venv方案；文档明确Windows硬件/驱动组合需另验。基础CPU路径可用但未实测性能。',
    ['最适合有可识别语音的访谈/课程/口播；纯画面情绪混剪不是默认强项。', '默认AI依据转录文本；TwelveLabs是另选的实际视频理解路径，不能把默认路径一概称视觉理解。', 'Fun-ASR-Nano/MOSS等模型的时间戳精度与支持剪辑形式有差异；精细任意文字剪辑应按文档选Paraformer。', '源码MIT不自动覆盖下载模型权重或素材的授权。'],
    '中文访谈/课程/口播选段优先；先本地转录+手选验证，再加LLM选段。',
    '中文创作者、需要按说话人或字幕文字剪自己的长视频的人。',
    'MP4/WAV、完整与剪辑后SRT、识别状态；未在本次路径发现可给主流NLE继续编辑的标准时间线导出。',
    [('实际截取用户源视频', 'funclip/videoclipper.py', 280, 'video_clip按dest_text/说话人或timestamp_list求区间，video.subclip后concatenate_videoclips并write_videofile。'),
     ('可选视觉理解需远端服务', 'funclip/llm/twelvelabs_api.py', 77, '_resolve_video_context将本地文件client.assets.create上传；call_twelvelabs_pegasus分析视频并转换时间戳。'),
     ('本地模型选择', 'funclip/model_selection.py', 1, '模型选择与FunASR适配路径；不同模型时间戳能力需要按文档区分。'),
     ('Windows安装边界', 'docs/installation.md', 27, '给出.venv/Scripts/python.exe方案，同时说明--help/pip check不能证明识别和导出工作流。'),
     ('依赖确认', 'requirements.txt', 1, 'FunASR、torch、torchaudio、Gradio及moviepy==1.0.3。')])

add('WyattBlue/auto-editor', '真实用户素材的规则自动粗剪/静音删除；非LLM语义选段', False,
    '响度阈值不等于音乐拍点。默认audio方法按每时间片最响采样幅度判活跃；无语义高光判定。',
    '当前核心为Nim及FFmpeg库；官方跨平台二进制。默认规则剪辑无模型、无API、无显存门槛；转写功能是另行可选能力。CLI当前不再通过pip发布。',
    '官方文档推荐Windows exe，源码构建走WSL交叉编译。适合Windows先用exe跑静音粗剪；本次未下载/执行二进制。',
    ['口误、重复句、观点是否精彩不能靠音量自动判断。', '背景音乐连续响亮时可能保留整段，不能当通用AI高光或音乐卡点器。', '仓库Unlicense；release捆绑二进制依赖可能用其他开源许可证；线上应用/独有资产另有专有授权。'],
    '作为口播/课程粗剪第一步推荐，之后再用语义工具或人工精剪。',
    '不想申请API、不想配置GPU、主要要去静音且保留后期工程的人。',
    '成片、clip sequence、JSON时间线及Premiere/Resolve/Final Cut/Shotcut/Kdenlive等导出；源码另含OTIO exporter。',
    [('默认规则的确是音量阈值', 'src/editmethods.nim', 34, 'audio按最响采样/最大采样值判断；motion是灰度帧差；subtitle/word是匹配。'),
     ('真实音频处理实现', 'src/analyze/audio.nim', 1, 'FFmpeg解码、重采样、分块及峰值分析，非远端模型。'),
     ('JSON时间线保留素材与区间', 'src/exports/json.nim', 11, '序列化每track中clip的src/start/dur/offset/stream/effects。'),
     ('NLE工程导出实现', 'src/exports/fcp7.nim', 1, 'Final Cut 7 XML类导出代码，可供后续编辑器工作流。'),
     ('Windows与pip现状', 'docs/src/installing.md', 6, '官方binary；Notice for Pip Users明确CLI不再发布pip；Windows源码构建列WSL。')])

add('FujiwaraChoki/supoclip', '长视频AI转短片/字幕/人脸重构图；带内置编辑器', True,
    '所审查选段基于时间戳转录和LLM评分，字幕时间同步不是音乐卡点；未见音乐beat决定切点的证据。',
    'Docker Compose、Python/FastAPI/worker、前端、FFmpeg、数据库等整套服务；默认AssemblyAI+LLM API，但源码有TRANSCRIPTION_PROVIDER=whisper及Ollama支路，可把核心识别和LLM本地化。本地模型与显存依所选Whisper/LLM，未给统一最低值。',
    'Windows优先Docker Desktop/WSL2。editor_document.py顶层import fcntl，表明Windows原生Python直接运行该编辑器路径有兼容障碍。',
    ['AGPL-3.0；适合接受该开源许可的部署/二开，不能把它当MIT模板。', '全套自部署栈比小CLI重，先确认是否需要账户/任务队列/编辑器。', 'virality评分为模型意见，不是传播效果保证。', '字幕模板主要控制字幕视觉风格，不等于万能可替换素材广告模板。'],
    '需要网页上传→自动挑段→竖屏字幕→手工微调的一体流程时推荐；Windows应走容器。',
    '经常将播客、课程、访谈变成多个竖屏短片的团队；能维护Docker服务的人。',
    '竖屏MP4、编辑器的版本化非破坏性clip草稿/确定性渲染指令；未发现本次路径有标准NLE时间线导出。',
    [('LLM真实选择转录区间', 'backend/src/ai.py', 282, 'system prompt要求精确提取和排名已有转录span，模型支持Ollama及多个云提供商。'),
     ('可选本地转写不是README空口宣称', 'backend/src/media/transcription.py', 177, '_whisper.load_model、word_timestamps=True；get_transcript按provider分派whisper/AssemblyAI/YouTube字幕。'),
     ('默认与可选配置入口', 'backend/src/config.py', 25, 'TRANSCRIPTION_PROVIDER默认assemblyai；WHISPER_MODEL和OLLAMA_BASE_URL等可配。'),
     ('真实草稿与Windows障碍', 'backend/src/editor_document.py', 1, '版本化非破坏性草稿、segments/word/style/framing模型；文件顶层import fcntl。'),
     ('字幕模板入口', 'backend/src/caption_templates.py', 1, '字幕模板定义可作为可复用样式层，需与镜头内容模板区分。')])

add('Anil-matcha/AI-Youtube-Shorts-Generator', '真实长视频AI高光+竖屏裁切；API/半本地双模式', False,
    '高光按转录文本及LLM评分；人脸跟踪裁切不是卡点，未见BPM/beat切点实现。',
    '默认MuAPI远端下载/Whisper/LLM/裁切，按服务调用成本计。--mode local使用faster-whisper、FFmpeg、OpenCV、yt-dlp，但LLM仍必须OpenAI或Gemini API。CPU int8或CUDA float16；本地base等模型可选，无统一最低显存。',
    '标准Python本地路径，_resolve_local_path支持直接Windows文件路径；需FFmpeg在PATH和相应Python wheels。未实测中文路径/音画同步/人脸追踪质量。',
    ['README使用free不表示零运行费；默认MuAPI，以及local分支LLM均可能计费。', 'local名称不表示完全离线；代码call_local_llm只分派OpenAI/Gemini。', '本次local clipper只见截取+人脸裁切+音轨合并，未见把缓存SRT烧录为成片字幕的步骤。', '无语音片段时pipeline直接抛错，不适合无台词情绪片作为默认路径。'],
    '想看清短小Python管线、接受LLM API并自行扩展字幕/剪辑逻辑的开发者可选；零基础一体使用优先FunClip/SupoClip。',
    '要把本地访谈转成若干竖屏高光、需要JSON供后续自动化的Python开发者。',
    'MP4或远端URL、候选分数/理由/起止时间与transcript JSON；local转录缓存SRT；不是NLE时间线。',
    [('两模式真实管线与无语音限制', 'shorts_generator/pipeline.py', 16, '_run_local先转写→get_highlights→crop_highlights_local，结果包含transcript/highlights/shorts；空segments报错。'),
     ('local仍调用远端LLM', 'shorts_generator/local/llm.py', 12, 'OpenAI(api_key) chat.completions或Google genai.Client；仅openai/gemini。'),
     ('本地人脸裁切', 'shorts_generator/local/clipper.py', 41, 'Haar最大人脸+平滑裁切，输出静音视频后用FFmpeg合并音轨，未见字幕烧录。'),
     ('本地CPU/CUDA切换', 'shorts_generator/local/transcriber.py', 120, 'WhisperModel，cuda float16、cpu int8，并写SRT缓存。'),
     ('本地文件输入入口', 'shorts_generator/local/downloader.py', 62, 'Path存在则直接用本地文件，跳过YouTube下载。')])

add('poseljacob/agentic-video-editor', '真实多素材目录→AI广告组装；视频理解+EditPlan', True,
    'YAML中的pacing、music mood和广告结构是LLM指令；add_music只混音，本次未见BPM/节拍检测或按拍点生成剪辑的实现。',
    'Python>=3.11、Google ADK/genai API、PySceneDetect/OpenCV、faster-whisper、FFmpeg/MoviePy。Gemini视频理解会上传或内联用户视频；默认preprocess用Whisper CPU int8，无本地GPU硬要求，但远端推理可能计费。',
    'README有Windows venv激活说明；FFmpeg/Python依赖需安装。源码可落地倾向较好，未做Windows实跑。',
    ['v0.1.0，源码历史与产品成熟度有限；README明确CLI为主，Studio网页UI仍WIP。', '预处理默认description为空；真正视觉判断由Director调analyze_footage工具执行，不能把预处理本身称完整视觉理解。', 'YAML风格是给LLM的结构化指导，不是确定性像素级成片模板，镜头选择/时长执行需验证。', '本地search_moments只是token重叠排序，不是向量检索模型。'],
    'AI看自己的多段产品素材并按广告brief组装的研究/二开候选；模板入口清楚，但成熟度低于可直接交付承诺。',
    '愿意用Gemini API、想研究镜头索引→导演选镜头→审片反馈循环的开发者。',
    'footage_index.json、EditPlan（shot_id/trim/order/text_overlay/music）、迭代MP4与review分数；未发现标准NLE交换格式导出。',
    [('实际视频理解输入', 'src/tools/analyze.py', 267, 'analyze_footage调用client.files.upload或Part.from_bytes，并generate_content([video_part,prompt])；不是仅文字脚本。'),
     ('真实用户文件夹预处理', 'src/pipeline/preprocess.py', 190, '递归视频、ContentDetector切镜头、Whisper词级时间戳、写FootageIndex；后段WhisperModel(cpu,int8)。'),
     ('明确可复用剪辑计划', 'src/models/schemas.py', 50, 'EditPlanEntry有shot_id/start_trim/end_trim/position/text_overlay/transition；EditPlan另有music_path。'),
     ('结构模板可改入口', 'styles/dtc-testimonial.yaml', 1, '30秒hook/problem/solution/social_proof/CTA结构和duration、text_overlay、music、pacing。'),
     ('音乐只混音证据', 'src/tools/edit.py', 373, 'add_music用volume与amix=duration=first；没有音乐节拍检测。')])

add('harry0703/MoneyPrinterTurbo', '文案/主题驱动的素材合成；支持本地素材与生成素材', True,
    '所审查主渲染路径按max_clip_duration固定分段、随机/顺序挑素材以铺满配音；BGM是混音，未见BPM/beat决定切点。不能称已验证音乐卡点。',
    'Python>=3.11、Streamlit/FastAPI、MoviePy2、FFmpeg、字幕/语音及多种可选云提供商。可配置本地LLM或提供现成文案/音频；Pexels/Pixabay/生成素材/TTS等依所选服务需key/可能付费。默认并不要求本地视频生成GPU；本地Whisper按模型耗内存。',
    'README有Windows发布/批处理，近期核心修复直接针对Windows控制台FFmpeg；video_project锁实现对nt用msvcrt分支。仍未执行验证。',
    ['支持上传本地素材≠理解素材内容、自动找动作高潮；已审主路径没有此类自动语义选镜头证据。', '可选TwelveLabs实现是搜索词语义重排及成片/素材描述QA，不能混同用户原片高光定位。', '新增video_project本地revision manifest可改场景/素材/渲染设置，但不是通用NLE多轨编辑器。', '仓库MIT；库存素材、声音、音乐及云模型输出依各来源条款，不能随源码许可推导全部可商用。'],
    '做主题解说/科普/营销批量合成值得选；用户核心若是音乐情绪混剪或自动挑自己素材高光，优先其他项目。',
    '有主题文案、愿意用配音和库存/本地素材批量出解说短视频的人。',
    'MP4、SRT、任务产物；可选本地video_project保存project.json/spec.json/revisions及可重渲染设置，未在该路径见标准NLE时间线导出。',
    [('主题生成流程而非默认素材理解', 'app/services/task.py', 1727, '先generate_script，非local才generate_terms，然后generate_audio并准备素材/合成。'),
     ('真实本地素材入口', 'app/services/task.py', 738, 'video_source==local时preprocess_materials，clip_duration取配置；证明能用本地素材但不自动证明理解素材。'),
     ('固定时长分段', 'app/services/video.py', 983, 'combine_videos取max_clip_duration；1057起按source_clip_duration切段，231起random模式shuffle优先独立素材。'),
     ('新增本地可重渲染工程', 'app/services/video_project.py', 292, 'create_revision接收prepared local media的scenes manifest，写project.json和revision spec；不调AI选镜头。'),
     ('TwelveLabs实际用途', 'app/services/twelvelabs.py', 1, '模块明示Marengo重排搜索词、Pegasus描述/QA公开URL视频；可选且无key时no-op。')])

add('RayVentura/ShortGPT', '文案/配音+背景库存素材自动合成框架', True,
    'content_short_engine选随机背景片段覆盖配音，background_music步骤循环+normalize+调音量；未见音乐拍点分析。',
    'Python、Gradio、MoviePy2.1.2、torch/whisper-timestamped、OpenAI、可选ElevenLabs/EdgeTTS/Pexels/Bing素材。非零运行费保证；本地转写有CPU/GPU资源需求，未给统一最低显存。',
    'README建议Colab或Docker；Windows更适合Docker/WSL，未实测。依赖与文档年代较旧，适合研究框架而非新手首装。',
    ['最新仓库push为2025-02-10，抽查核心文件提交2025-01-13；相对当前日期明显停缓。', 'ContentTranslationEngine可翻译自己的视频，但不是高光提取/音乐情绪混剪。', 'Editing JSON是内部schema，不应宣传为已兼容Premiere/Resolve等标准时间线。'],
    '保留作AI剪辑DSL/参数模板的学习对照；当前落地优先级低于更活跃方案。',
    '研究LLM剪辑指令和素材合成框架的开发者。',
    'MP4、文字metadata、内部Editing JSON schema/TinyDB状态；未发现标准NLE导出。',
    [('主流程是生成文案再合成', 'shortGPT/engine/content_short_engine.py', 36, 'stepDict: generateScript→voice→captions→image搜索→background→render。'),
     ('随机背景片段不是语义高光', 'shortGPT/engine/content_short_engine.py', 109, '_prepareBackgroundAssets按配音时长调用extract_random_clip_from_video。'),
     ('JSON步骤的模板参数入口', 'shortGPT/editing_framework/editing_engine.py', 48, 'addEditingStep读editing_steps JSON并注入参数；dumpEditingSchema可取内部schema。'),
     ('背景音乐只有循环/归一化/音量', 'shortGPT/editing_framework/editing_steps/background_music.json', 1, 'loop_background_music、normalize_audio、volume_percentage三个action；没有拍点输入。'),
     ('依赖年代和重度', 'requirements.txt', 1, 'torch、torchaudio、whisper-timestamped、openai==1.37.0、moviepy==2.1.2等。')])

excluded = [
    dict(repo='VadooAI/ClipAnything', reason='种子仓库API请求返回Not Found；8条搜索中的ClipAnything专搜只召回提及它的榜单/其他项目，未核实官方可复用源码。不能把商业产品宣传页当开源实现。'),
    dict(repo='gitroomhq/postiz-app', reason='高星但主要是社交媒体排期发布，非本次用户素材剪辑引擎。'),
    dict(repo='QwenAudio/CosyVoice', reason='语音生成模型；可作配音组件，不是现成用户素材剪辑方案。'),
    dict(repo='MeiGen-AI/InfiniteTalk', reason='语音驱动视频生成，目标是生成画面；非已有素材剪辑引擎。'),
    dict(repo='yihui-dev/awesome-opus5-5-videos', reason='视频展示与提示词收集；不能替代实际可复用剪辑实现。'),
    dict(repo='21cncstudio/project_aura', reason='空气质量ESP32项目，关键词噪声。'),
    dict(repo='Anil-matcha/ai-clipping-comfyui', reason='搜索description明确server-side经muapi.ai；可做服务节点封装候选，不作为完全本地开放高光引擎重复推荐。本次未深审其源码。'),
]
dedup = [
    dict(repo='SamurAIGPT/AI-Youtube-Shorts-Generator', canonical='Anil-matcha/AI-Youtube-Shorts-Generator', reason='gh api旧路径返回canonical full_name与同一repo id=821280833；是旧地址重定向，不计独立项目。'),
    dict(repo='Asad-Ismail/MoneyPrinterTurbo-Extended', canonical='harry0703/MoneyPrinterTurbo', reason='描述明确extended implementation，作为衍生家族记录，不重复计主实现。GitHub metadata fork=false，故不能声称是GitHub fork或逐文件相同；本次未做源码hash同源鉴定。'),
    dict(repo='modelscope/FunClip', canonical='modelscope/FunClip', reason='与其他访谈选段方案功能类似不等于同源；metadata fork=false，保留独立实现。'),
]

searches=read('searches.json')
candidates=read('candidates.json')
summary=dict(date='2026-11-04', scope='AI editing静态源码审查；8项目深审，未安装/启动仓库、未生成视频、未做效果测试',
    commands=['search.ps1','inspect.ps1','fetch-sources.ps1','fetch-extra.ps1'],
    search_calls=len(searches), returned_rows=sum(s['count'] for s in searches),
    unique_search_candidates=len(candidates), seed_repositories=9, inspected_code_repositories=len(records))
report=dict(summary=summary, searches=searches, shortlisted=records, excluded=excluded, dedup=dedup)
(ROOT/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')

lines=['# AI自动剪辑与真实素材处理：静态源码核验', '',
 '**结论：** 同时想要AI参与、可继续改工程和音乐卡点，优先小样验证 OpenChatCut；中文长口播选段选 FunClip；快速去静音选 auto-editor；播客竖屏高光工作流看 SupoClip。MoneyPrinterTurbo与ShortGPT是文案/配音驱动素材合成，不能因为星多就当音乐混剪或自动挑原片高光。', '',
 '> 审查日期2026-11-04。此报告只读GitHub元数据、README、目录树与固定提交源码；没有安装、执行仓库代码或验证成片效果。文中的“有实现”表示源代码路径存在，不表示运行成功或剪辑质量过关。', '',
 '## 一屏对比', '',
 '| 项目 | 真实用户素材 | 音乐卡点 | 可改模板/工程 | Windows判断 | 许可 | 星数（当次） |',
 '|---|---|---|---|---|---|---|']
matrix={
'0xsline/OpenChatCut':('是，多轨工程','有音频分析与切分执行','完整工程+MG模板','有win打包；未实跑'),
'modelscope/FunClip':('是，按语音/文本/说话人','未发现','参数+SRT；非NLE','有安装说明；需适配依赖'),
'WyattBlue/auto-editor':('是，阈值粗剪','非拍点','多NLE/JSON导出','官方exe；源码构建WSL'),
'FujiwaraChoki/supoclip':('是，转录高光+人脸裁切','未发现','字幕模板+内置草稿','宜Docker/WSL；fcntl障碍'),
'Anil-matcha/AI-Youtube-Shorts-Generator':('是，本地/YouTube','未发现','候选JSON；非NLE','Python+FFmpeg；未实跑'),
'poseljacob/agentic-video-editor':('是，多素材+视觉理解','未发现','YAML指导+EditPlan','Python+FFmpeg；未实跑'),
'harry0703/MoneyPrinterTurbo':('可用本地素材；未证自动理解','主路径固定分段','任务参数+revision manifest','有Windows支持；未实跑'),
'RayVentura/ShortGPT':('合成/翻译为主','随机背景+循环音乐','内部JSON步骤','更宜Docker/WSL；旧框架')}
for r in records:
    a,b,c,d=matrix[r['repo']]
    lines.append(f"| [{r['repo']}]({r['url']}) | {a} | {b} | {c} | {d} | {r['license']} | {r['stars']:,} |")
lines += ['', '读表方式：**卡点**必须至少分析音乐中的拍点并让剪辑点跟随；给片子加BGM、字幕跟随语音、让LLM写“有节奏”均不满足这个证据标准。**模板**要区分确定性素材槽位、可编辑工程、给LLM看的风格提示；这三者的可控程度不同。', '',
          '## 已执行的命令行审查流程', '',
          '通过已登录GitHub CLI查询公开API。没有调用搜索网页或安装第三方代码。PowerShell脚本保存在本目录，原始search JSON和仓库metadata/tree/commit也保留，便于复查。', '',
          '```powershell', "$gh = 'C:\\Program Files\\GitHub CLI\\gh.exe'", '& $gh api rate_limit --jq .resources.search',
          "& $gh api --method GET search/repositories -f 'q=\"automatic video editing\" in:name,description,readme stars:>20' -f 'per_page=30' -f 'sort=stars'",
          '# 以下每个仓库读取：元数据 -> 当前固定SHA -> 目录树 -> 指定源码文件',
          '& $gh api repos/modelscope/FunClip',
          '& $gh api repos/modelscope/FunClip/commits/main',
          '& $gh api "repos/modelscope/FunClip/git/trees/<sha>?recursive=1"',
          '& $gh api "repos/modelscope/FunClip/contents/funclip/videoclipper.py?ref=<sha>"',
          '# contents响应是base64；用Convert.FromBase64String还原，只读取，不导入运行',
          '& $gh api --method GET repos/modelscope/FunClip/commits -f path=funclip/videoclipper.py -f per_page=1',
          'rg -n "subclip|concatenate|write_videofile|AutoModel" <本地审查源文件>', '```', '',
          '实际批量运行入口：`search.ps1`、`inspect.ps1`、`fetch-sources.ps1`、`fetch-extra.ps1`。上面SHA占位写法是读者复查模板；实际脚本使用commit API返回的40位SHA，未把占位命令当执行结果。', '',
          f"本分支8条repo search返回{summary['returned_rows']}行，按full_name去重后{summary['unique_search_candidates']}个候选；另做9个种子路径探测，其中ClipAnything路径未找到，8个项目读取了实现代码。搜索每条最多30个结果，非全GitHub穷尽；total_count是GitHub报告的匹配数，count是这次实际取回行数。", '',
          '| 实际query | 取回/总匹配 | 原始文件 |', '|---|---:|---|']
for s in searches:
    lines.append(f"| `{s['query']}` | {s['count']}/{s['total_count']} | [{s['raw_file']}]({s['raw_file']}) |")
lines += ['', '元数据解读：`pushed_at`只是仓库最后push，不保证是核心代码更新；下方同时列一条抽查核心文件的最近提交。这个抽样日期也不是整个仓库“最后代码修改”的全量证明。', '',
          '## 逐项实现证据与适用人群', '']
for r in records:
    date=r['sampled_core_commit']
    lines += [f"### {r['repo']}", '', f"**定位：** {r['category']}。**推荐判断：** {r['recommendation']}", '',
              f"**适合谁：** {r['audience']}", '', f"**卡点核验：** {r['beat_capability']}", '',
              f"**产物与复用入口：** {r['output']}", '', f"**依赖/费用/模型：** {r['dependencies']}", '',
              f"**Windows：** {r['windows']}", '',
              f"**维护记录：** 仓库push `{r['pushed_at']}`；抽查 `{date['path']}` 最近提交 `{date['date']}`；审查快照 `{r['sha']}`。", '',
              '**固定提交源码证据：**', '']
    for e in r['evidence']:
        lines.append(f"- [{e['claim']}]({e['url']})：{e['detail']}")
    lines += ['', '**限制：**', ''] + [f'- {x}' for x in r['limitations']] + ['']
lines += ['## 淘汰与去重记录', '']
for r in excluded:
    lines.append(f"- **{r['repo']}**：{r['reason']}")
lines += ['', '下列是同名重定向/衍生家族处理，不把相似功能直接认定同源：', '']
for r in dedup:
    lines.append(f"- **{r['repo']} → {r['canonical']}**：{r['reason']}")
lines += ['', '## 零基础下一步：怎么做最小验证', '',
          '以下是选型后的**建议操作，未在本轮执行**。先用一份20至60秒、有明确授权的小素材；别一次喂整盘素材或直接承诺商用交付。', '',
          '1. 只要去静音：从auto-editor官方Releases取Windows exe，先看`--help`，随后试`auto-editor.exe input.mp4 --export resolve`，检查去掉的间隙是否伤到尾音。当前不要照旧教程`pip install auto-editor`。',
          '2. 中文口播/课程：FunClip独立Python环境→先转录→复制文字剪一段→对照原片检查字幕/切点；再开启LLM高光。手选路径无需LLM账单。',
          '3. 音乐混剪+可改工程：OpenChatCut导入少量自己的素材与音乐，先`analyze_music`检查BPM/拍点，再`music_edit_plan`审计划，最后`sync_cuts_to_music`切分；听节奏、看动作衔接、再换音乐复验。它是工具/agent流程，不能把这些工具名直接当PowerShell可执行命令。',
          '4. 长视频批量竖屏：SupoClip先Docker跑一条任务，确认用云转写还是`TRANSCRIPTION_PROVIDER=whisper`，以及云LLM还是Ollama；核对实际API调用和输出字幕，不以“免费开源”推导零运行成本。',
          '5. 自己多段产品素材做广告：agentic-video-editor以`ave edit --footage-dir ./footage --brief brief.json`为入口；先看footage_index与EditPlan是否真的选到了正确镜头，再看MP4。YAML风格指导可能需要调提示与重试。', '',
          '验收应同时看：源素材选段是否正确、剪点是否切断台词/动作、音乐是否真在切点命中、竖屏是否裁掉主体、字幕是否对时、修改素材能否重渲染。没有做这些运行验收，就只能称“静态候选”。', '',
          '学习顺序可从auto-editor的规则区间/工程导出，进到FunClip的转录时间戳，再看agentic-video-editor的EditPlan和素材索引，最后看OpenChatCut把音乐分析、时间线、模板、agent工具连起来。', '']
(ROOT/'review.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
print('Saved review.json and review.md')
