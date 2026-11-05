$ErrorActionPreference='Stop'
$base=Join-Path (Get-Location) 'work\editable_templates'
function Evidence($repo,$claim,$path,$pattern,$detail){
 $folder=Join-Path $base ($repo -replace '/','__')
 $sha=(Get-Content -LiteralPath (Join-Path $folder 'commit.json') -Raw|ConvertFrom-Json).sha
 $file=Join-Path $folder ('files\'+$path)
 $match=Select-String -LiteralPath $file -Pattern $pattern|Select-Object -First 1
 $line=if($match){$match.LineNumber}else{1}
 @{claim=$claim;path=$path;url="https://github.com/$repo/blob/$sha/$path#L$line";detail=$detail}
}
function Item($repo,$category,$beat,$license,$dependencies,$windows,$limitations,$recommendation,$evidence){
 $folder=Join-Path $base ($repo -replace '/','__')
 $m=Get-Content -LiteralPath (Join-Path $folder 'meta.json') -Raw|ConvertFrom-Json
 $sha=(Get-Content -LiteralPath (Join-Path $folder 'commit.json') -Raw|ConvertFrom-Json).sha
 @{repo=$repo;url=$m.html_url;category=$category;is_template=$true;beat_capability=$beat;license=$license;stars=$m.stargazers_count;pushed_at=$m.pushed_at;sha=$sha;evidence=@($evidence);dependencies=$dependencies;windows=$windows;limitations=$limitations;recommendation=$recommendation;validation='仅静态审查：已取得README、固定commit的文件树和所列源文件；未安装依赖、未启动项目、未渲染视频。'}
}
$items=@()
$r='actionow-ai/vvv'
$items+=Item $r '完整婚礼/相册成品模板库；有卡点模板' '源码证实：Starter读取音乐beats.json；每镜4拍，开场/结尾各8拍；无map时96BPM回退。music add/beats分析与music fit流程见文档；算法效果未实测。' 'MIT（代码/模板/部分演示媒体）；README另声明仅学习研究；Remotion运行时采用其独立许可，音乐与字体另看MEDIA_LICENSE。' @('Python 3.9+','Node.js；README当前写26','npm','Remotion','FFmpeg/Chrome','可选Pillow/OpenCV等') 'README仅称macOS ARM64用Claude Code/Codex完整验证；其他平台测试少；Windows未验证。' @('早期0.2版本','婚礼叙事专用；通用混剪需改场景','音乐需授权；Mixkit配乐不随模板独立再分发','使用Codex仅安装skill还不够，需clone kit并设置VVV_KIT','照片顺序/人脸裁切/文字需人工检查') '照片卡点首选实物候选：从starter小模板入门，再看album/editorial；首次只运行doctor和样片。' @(
 (Evidence $r '代码证实：照片slot、每镜拍数与回退BPM' 'kits/remotion/src/templates/starter/index.tsx' 'const BEATS_PER_SHOT' 'gallery接受6–24张；BEATS_PER_SHOT=4，FALLBACK_BPM=96。'),
 (Evidence $r '代码证实：读取实测beat grid，不是仅固定BPM' 'kits/remotion/src/core/beat-clock.ts' 'export function beatClock' '按实测beats插值；少于8拍或缺map时回退；loadBeatGrid从public读取相邻beats.json并扣除trim。'),
 (Evidence $r 'README说明：换素材入口' 'kits/remotion/src/templates/starter/README.md' 'inputs.json' 'inputs.json.props控制couple、photos、copy、music、format/fps。'),
 (Evidence $r 'README说明：初始化、样片、导出、检查命令' 'skills/vvv/references/projects.md' 'python3 scripts/vvv.py doctor' 'init --template starter --photos ... --output ...；validate/sample/render/check；需先npm ci和music。'),
 (Evidence $r 'README说明：平台与用途限制' 'README.md' 'macOS ARM64' '作者只宣称macOS ARM64完整验证；另声明仅学习与研究。'),
 (Evidence $r '媒体许可范围' 'MEDIA_LICENSE.md' 'Preview soundtracks' '照片画面与预览音轨授权不同，不能将Mixkit音频单独分发。')
)
$r='lumian2015/opus-5-5-video-templates'
$items+=Item $r '30个完整HyperFrames HTML动效/广告成品模板' '固定剪点/GSAP镜头编排；所审25号模板SH数组是预设时间段，无音频beat detector。换音乐后须重调剪点。' '模板/脚本MIT；字体OFL；GSAP标准许可；HyperFrames Apache-2.0独立依赖。' @('Node.js22+','FFmpeg','Chrome','npx hyperframes@0.8.96','bundled GSAP/字体') 'Node mjs脚本使用跨平台path/fs，具备Windows迁移基础；README示例使用Bash环境变量，需改PowerShell；未实测。' @('30个模板属同一模板family，不计30个独立工具','多数是品牌动效而非长素材混剪','图片/镜头参数需保持构图关系','固定0.8.96版本，升级兼容性未知','复刻参考片结构，README列出了灵感来源；不代表原作授权') '纯动效换品牌首选：变量工具比手改整页可靠；六图25号UGC模板适合验证素材替换。' @(
 (Evidence $r 'README说明：复制、替换、抽帧与渲染全流程' 'README.md' 'node \$S/scripts/new-video' 'new-video复制模板；vars列出/写入变量；snapshot检查；render输出MP4；未实际运行。'),
 (Evidence $r '代码证实：JSON变量写回HTML默认值' 'scripts/vars.mjs' 'const match = html.match' '解析data-composition-variables；拒绝未知key并校验颜色；写回index.html。'),
 (Evidence $r '代码证实：25号十秒竖版时间线与照片镜头参数' 'templates/25-ugc-product-reel/index.html' 'const SH' 'root=1080×1920、data-duration=10；SH为镜头start/end/scale/焦点/rotation。'),
 (Evidence $r '模板元数据：素材清单、变量和渲染命令' 'templates/25-ugc-product-reel/template.json' '"images"' '六图路径hero/box/wand/swatch/lips/cafe；captions和grain变量；render命令在文件末尾。'),
 (Evidence $r 'README说明：许可分别列出' 'README.md' 'Credits and licenses' 'MIT模板不覆盖第三方GSAP/字体许可。')
)
$r='codeverbojan/remotion-cinematic'
$items+=Item $r '完整Remotion产品演示片模板（5个示例场景）' '音乐床/SFX cue与ducking；按帧设置场景、鼠标和镜头；未发现所审代码提供音频beat自动剪点。' '仓库MIT；Remotion依赖独立许可，不能用MIT概括整个运行时。' @('Node/npm','Remotion4.0.451','React19','TypeScript5.9','Zod4','Chromium') 'npm命令与TS代码具跨平台基础；未看到Windows验证承诺，未实测。' @('产品UI演示专用，不是任意素材混剪','README截图入口存在但public/screenshots仅占位说明；演示主要为生成UI','首次需理解Studio props/场景结构','Figma/Claude截图导入是可选网络能力，需token/API key') '产品发布片首选：先跑自带5场demo，再换品牌、UI和SFX；有Studio编辑面板，适合愿意学少量React的人。' @(
 (Evidence $r '代码证实：预览与渲染命令' 'package.json' '"build"' 'studio=npx remotion studio src/index.ts；build=render CinematicDemo。'),
 (Evidence $r '代码证实：默认品牌、场景与音乐配置' 'src/defaultProps.ts' 'brand:' '完整defaultProps，场景启用/时长/入出场和音乐fade参数。'),
 (Evidence $r '代码证实：输入schema' 'src/schema.ts' 'brand: BrandSchema' 'Zod schema定义品牌、场景、窗口、鼠标、音乐等可调输入。'),
 (Evidence $r 'README说明：换素材与五示例场景' 'README.md' '5 example scenes' 'chaos desktop/product reveal/feature showcase/headline/end card；public放截图与音乐/SFX。')
)
$r='feliperun/slideshow'
$items+=Item $r '成品相册/照片视频混排生成器（配置驱动模板化）' '源码证实有本地音轨分析：FFmpeg转单声道PCM，能量onset、自相关搜索78–175 BPM、估phase后生成beatFrames；并非语义选镜。' 'MIT仓库；Remotion运行时独立许可。' @('Node22+','pnpm11+','FFmpeg/FFprobe','Remotion','Sharp','Chromium') 'README称Windows在原生Sharp/Remotion依赖可用时应能工作；不在CI，仅支持macOS/Linux优先。' @('3星小项目；成熟度未运行验证','节奏估计是全局恒定网格；变速/复杂音乐可能不准','4秒以下音频不分析，异常吞掉返回undefined','输出是配置生成的相册风格，不是CapCut原生时间线') '批量照片+视频+音乐首选备选：比复杂Agent模板更可审计，配置与manifest分离；Windows先测合成demo。' @(
 (Evidence $r 'README说明：配置、预览、导出及Windows状态' 'README.md' 'Windows should work' 'pnpm validate/analyze/editor/preview/render；Windows未入CI。'),
 (Evidence $r '代码证实：素材与输出配置' 'project.example.json' 'photosDirectory' '本地media目录、music文件、时长、画幅、seed及output.file。'),
 (Evidence $r '代码证实：检测而非营销标签' 'src/analysis/analyze-audio.ts' 'export const detectBeatGridFromPcm' '滑窗能量onset、自相关tempo/phase；返回bpm、confidence、beatFrames。'),
 (Evidence $r 'README说明：有合成demo可自检' 'README.md' 'Try the synthetic demo' 'demo:generate生成占位照片与合成音轨，不必上传私有素材。')
)
$r='shotstack/shotstack-templates'
$items+=Item $r '222个官方云端JSON模板；视频/图片/音频混合' '固定timeline start/length与transition；示例模板没有自动音乐节拍检测；不是222个都为混剪视频。' 'PolyForm Shield1.0.0（源码可见、noncompete限制）；GitHub API NOASSERTION。' @('Node18+','csv-parse','Shotstack API key','网络可访问的素材URL','云渲染服务') 'render.mjs为跨平台Node；README的环境变量赋值是POSIX写法，PowerShell需用$env:SHOTSTACK_API_KEY；未实测。' @('非宽松开源；禁止提供竞品','生产云服务收费，沙箱水印','素材需要URL，隐私素材须考虑上传','脚本逐行CSV提交并轮询，失败只打印状态','222包含静图/音频模板，不等于222混剪模板') '想最快把JSON和素材URL换成广告成片，可选官方现成模板；不适合要求纯本地/宽松授权的人。' @(
 (Evidence $r 'README说明：222类模板和测试条件' 'README.md' '222 ready-to-render' 'template.json+merge字段README；生产key或stage水印测试；附在线预览。'),
 (Evidence $r '代码证实：CSV合并变量与调用渲染API' 'render.mjs' 'merge: fields.map' '每行按find的小写字段取CSV覆盖值；POST /edit/v1/render并轮询打印URL。'),
 (Evidence $r '代码证实：真实素材与时间线占位字段' 'templates/adventure-travel-tour-sale-promo-v2/template.json' '"timeline"' '实际有timeline/tracks/clips、src占位符与merge默认值。'),
 (Evidence $r '许可原文：noncompete' 'LICENSE' '## Noncompete' 'PolyForm Shield：任何用途除提供与许可方软件/产品竞争的产品；不是MIT。')
)
$r='xuliang2024/cutcli-cookbook'
$items+=Item $r '剪映/CapCut草稿配方+可替换JSON时间线' '固定微秒start/end与动画、转场；所审product-promo例没有音频beat分析，不应称自动卡点。' 'Cookbook MIT；仓库自己的开源边界文件明确称核心cutcli/jy_cli闭源私有；核心授权/下载/服务条款需另审。' @('外部闭源cutcli','Bash','jq','剪映/CapCut用于继续编辑/导出','远程演示素材URL') '本仓库run.sh需要Bash+jq；Windows用Git Bash/WSL或把命令改写PowerShell，草稿导入/导出兼容性未测试。' @('只有cookbook开源，核心CLI闭源','run.sh生成draft ID，不执行MP4渲染导出；README另列cloud render为外部服务能力','README产品片分镜描述和images.json部分时段并不完全相同，应以数据为准','演示素材为远程URL，可能失效','依赖外部平台草稿兼容性') '明确需要剪映可编辑草稿时再选；新手先看02相册，再10产品片；导出步骤必须在剪映核实。' @(
 (Evidence $r '代码证实：完整30秒草稿命令' 'examples/10-product-promo-30s/run.sh' 'DRAFT_ID=' '创建1080×1920 draft；images/captions/audios add；结尾只draft info。'),
 (Evidence $r '代码证实：素材URL、微秒时间与动画可替换' 'examples/10-product-promo-30s/data/images.json' 'imageUrl' 'imageUrl/start/end/inAnimation/transition；末镜24–30秒。'),
 (Evidence $r '仓库说明：核心闭源，cookbook公开' '.cursor/rules/open-source-boundary.mdc' '\| `jy_cli`' '边界文件表格明确jy_cli闭源私有；案例只调用公开CLI，不直接访问核心源码。')
)
$r='nexu-io/html-video'
$items+=Item $r '部分完整HTML模板+静态风格底稿+Agent Studio' 'frame-product-promo-30s有8场固定时间线；未证实自动听歌卡点。可选AI soundtrack是生成/混音，不等于节拍剪辑。' '根Apache-2.0；部分模板源自HyperFrames Apache-2.0或student-kit MIT，按NOTICE保留来源。' @('Node20+','pnpm9+','Playwright Chromium','FFmpeg','可选coding-agent/Anthropic/MiniMax key') 'Node/Playwright具Windows基础；未取得Windows验证证据，未实测。' @('README称21个均animated，但抽查light-leak-cinema只有静态CSS页面，无动画时间线/输入绑定','21模板中至少8个直接fork官方HyperFrames，1个来自student-kit，需去重','render adapter其实是Playwright实时recordVideo+FFmpeg，注释称不依赖HyperFrames运行时','README称Remotion adapter未完成，tree已有adapter目录，不能据文件存在认定可用','Agent修改模板与一键参数替换不是同一成熟度') '作为中文Studio/Agent整合层备选；只推荐具体审过的30秒产品片结构；不把全部21个当直接换值的完整成品模板。' @(
 (Evidence $r '代码证实：30秒产品片真实分场' 'templates/frame-product-promo-30s/index.html' 'data-duration="30"' '8个data-composition-src，按0/4/8/10/14.8/19.5/22/25秒编排。'),
 (Evidence $r '来源证实：模板级重复' 'templates/NOTICE.md' 'direct forks' '8个官方registry直接fork；product-promo-30s来自hyperframes-student-kit。'),
 (Evidence $r '静态反证：漏光模板并非README宣称的全动画' 'templates/frame-light-leak-cinema/source/index.html' '<style>' '完整文件仅静态HTML/CSS；无keyframes、animation或运动script；Tailwind/Google Fonts远程加载。'),
 (Evidence $r '代码证实：渲染适配器实际实现' 'packages/adapter-hyperframes/src/render.ts' 'Upstream Hyperframes was never required' 'Playwright recordVideo录制WebM后FFmpeg转MP4；不是调用HyperFrames CLI。'),
 (Evidence $r 'README说明：安装/启动' 'README.md' 'pnpm -r build' 'pnpm install; pnpm -r build; node packages/cli/dist/bin.js studio；未运行。')
)
$r='Vincentwei1021/video-shotcraft'
$items+=Item $r '完整Remotion产品片模板+镜头卡/Agent工作流（本机已有同名skill）' '现成Ink Press时间线与BGM/SFX；卡点需要镜头/音效对齐，未在本轮证明自动音轨beat检测。' 'Apache-2.0仓库；Remotion、音乐/SFX等各有独立许可/attribution。' @('Node/npm','Remotion4.0.484','React19','TypeScript6','页面截图工具','可选FFmpeg') 'README剪映安装模块标注Mac实测/Windows未验证；核心Remotion模板未在本轮Windows实测。' @('用户本机已有video-shotcraft skill，不建议再重复安装','主旨是产品发布片不是纯音乐素材混剪','截图需换成用户自己的产品；历史音频需按ATTRIBUTION','镜头卡数量不等于独立全片模板数量') '作为已有能力的优先起点：确认本地版本，直接复用Ink Press完整模板，比引进同源fork更省事。' @(
 (Evidence $r '代码证实：完整成片渲染命令' 'template/package.json' '"render"' 'render=remotion render src/index.ts AiflPromo out/promo.mp4；dev与still也齐备。'),
 (Evidence $r '代码证实：完整composition注册' 'template/src/Root.tsx' 'defaultProps' 'AiflPromo、theme=ink-press、1920×1080、30fps、全片AIFL_TOTAL。'),
 (Evidence $r 'README说明：模板素材/平台限制' 'README_CN.md' 'Windows 未验证' 'template/完整成片模板；jianying-export/Mac实测Windows未验证；演示截图须替换。')
)
$excluded=@(
 @{repo='remotion-dev/template-audiogram';reason='是真模板但偏播客字幕+音频波形，不是纯素材混剪；README明示mirror，应归并remotion-dev/remotion/packages/template-audiogram，许可要求公司license条件不能写MIT。'},
 @{repo='remotion-dev/template-helloworld';reason='React logo/文字入门模板；不具现成混剪素材结构，不作为成品混剪模板推荐。'},
 @{repo='remotion-dev/template-tiktok';reason='真字幕视频模板但目标是转写/加字幕，非纯音乐蒙太奇；与Remotion monorepo同family。'},
 @{repo='2boysfromtown/hyperframes-motion';reason='确有4个1080×1920 GSAP HTML模板，MIT，非引擎；但README仅建议任意录屏/HTML转视频方法，仓库无export/render命令，无音轨卡点；降为手动动效素材备选，不列首选。'},
 @{repo='halicotampa-crypto/motion-pack';reason='大型动效/skills混合pack，tree含student-kit及其HyperFrames skills拷贝；与本机已有技能/模板族重复风险高，本轮未逐个复核100+条，不把数量当独立成片模板数。'},
 @{repo='nateherkai/herk-edit-kit';reason='含完整工作流/样式库而非仅模板；主代理负责与本机edit-video/short-form-edit等同源核查，避免重复引入。'},
 @{repo='heygen-com/hyperframes';reason='基础引擎不作为模板本体计数；其registry/examples可在主代理官方模板审查中计入具体模板。'},
 @{repo='heygen-com/hyperframes-vercel-template';reason='渲染服务/部署脚手架，不能以名字template当作已设计完成的视频成品模板。'},
 @{repo='renezander030/capcut-cli';reason='草稿编辑CLI，不是现成成品模板；可作为cookbook外部依赖类工具另评估。'},
 @{repo='duoec/duo-video';reason='Java剪映草稿SDK，不是成品混剪模板。'},
 @{repo='SoKeiKei/CapKit-download';reason='模板管理器/下载仓库，不等于可直接审查的开源模板。'}
)
$dedup=@(
 @{repo='remotion-dev/template-audiogram';canonical='remotion-dev/remotion/packages/template-audiogram';reason='README Contributing明示这是mirror；不要和monorepo重复计数。'},
 @{repo='remotion-dev/template-tiktok';canonical='remotion-dev/remotion/packages/template-tiktok';reason='官方template family；本轮取得tree与metadata，family级归并，不能视作独立引擎。'},
 @{repo='nexu-io/html-video:frame-warm-grain,frame-swiss-grid,frame-kinetic-type,frame-nyt-graph,frame-decision-tree,frame-play-mode,frame-product-promo,frame-vignelli';canonical='heygen-com/hyperframes/registry/examples';reason='NOTICE说明direct forks、composition文件未变，仅目录布局变化。'},
 @{repo='nexu-io/html-video:frame-product-promo-30s';canonical='nateherkai/hyperframes-student-kit/video-projects/linear-promo-30s';reason='NOTICE明确保留30秒结构与SFX，替换品牌占位素材。'},
 @{repo='JohnChow90/video-shotcraft';canonical='Vincentwei1021/video-shotcraft';reason='搜索元数据description写originally by Vincentwei1021；只采纳原作者仓库作为canonical，fork代码未深审。'},
 @{repo='Vincentwei1021/video-shotcraft';canonical='本机已有C:/Users/PC/.codex/skills/video-shotcraft';reason='会话skill catalog已列同名skill；主代理负责实际内容同源核对，本子报告不声称逐字相同。'},
 @{repo='lumian2015/opus-5-5-video-templates';canonical='同仓库30个template family';reason='30种设计可单独选择，但工具数只计1，不膨胀为30独立软件。'}
)
$searches=Get-Content -LiteralPath (Join-Path $base 'searches.json') -Raw|ConvertFrom-Json
$candidates=Get-Content -LiteralPath (Join-Path $base 'candidates.json') -Raw|ConvertFrom-Json
$seeds=@(Get-ChildItem -LiteralPath $base -Directory|ForEach-Object { $f=Join-Path $_.FullName 'meta.json';if(Test-Path -LiteralPath $f){Get-Content -LiteralPath $f -Raw|ConvertFrom-Json}})
$seeds|ConvertTo-Json -Depth 100|Set-Content -LiteralPath (Join-Path $base 'seeds.json') -Encoding utf8
$review=@{scope='可换素材复用的纯剪辑/动效/卡点模板；静态审查；查询日期2026-11-04';searches=@($searches);raw_unique_candidate_count=@($candidates).Count;seed_count=@($seeds).Count;shortlisted=$items;excluded=$excluded;dedup=$dedup}
$review|ConvertTo-Json -Depth 100|Set-Content -LiteralPath (Join-Path $base 'review.json') -Encoding utf8
$md=@()
$md+='# 可换素材视频模板审查（中文；仅静态审查）'
$md+=''
$md+='优先顺序：照片/婚礼卡点看 actionow-ai/vvv；品牌动效换字换色看 Opus 30模板；产品UI发布片看 remotion-cinematic；照片视频混排看 feliperun/slideshow。需要剪映草稿才看 cutcli-cookbook；接受云端渲染和受限许可再看 Shotstack。本机已有 video-shotcraft，先复用已有能力。'
$md+=''
$md+='本报告未安装或执行任何陌生项目，未声称渲染成功。README功能声明与源码存在证据分开记录。Stars只作当前元数据，不作为淘汰小项目的条件。所有证据链接固定到实际查询到的commit。'
$md+=''
$md+='## 搜索覆盖与原始返回'
$md+=''
$md+="首轮8条GitHub CLI repository search，共$(@($candidates).Count)个去重原始候选（每query最多返回30条，不代表全GitHub全部结果）。额外按品牌seed拉取$(@($seeds).Count)个仓库元数据与tree；原始池candidates.json、seeds.json保留供主流程合并去重。"
$md+=''
$md+='|query|返回条数|API total_count|原始文件|'
$md+='|---|---:|---:|---|'
foreach($s in $searches){$md+="|$($s.query)|$($s.count)|$($s.total_count)|$(Split-Path -Leaf $s.raw_file)|"}
$md+=''
$md+='## 总览'
$md+=''
$md+='|仓库|stars|实际模板定位|节拍能力|Windows|'
$md+='|---|---:|---|---|---|'
foreach($i in $items){$md+="|[$($i.repo)]($($i.url))|$($i.stars)|$($i.category)|$($i.beat_capability)|$($i.windows)|"}
foreach($i in $items){
 $md+='';$md+="## $($i.repo)";$md+=''
 $md+="**判断：** $($i.recommendation)";$md+=''
 $md+="许可：$($i.license)  最近push：$($i.pushed_at)；固定SHA：$($i.sha)。";$md+=''
 $md+="依赖/上手：$($i.dependencies -join '、')。$($i.windows)";$md+=''
 $md+="卡点：$($i.beat_capability)";$md+=''
 $md+="限制：$($i.limitations -join '；')。";$md+=''
 foreach($e in $i.evidence){$md+="- [$($e.claim)]($($e.url))：$($e.detail)"}
}
$md+='';$md+='## 未进首选与淘汰证据';$md+=''
foreach($x in $excluded){$md+="- **$($x.repo)**：$($x.reason)"}
$md+='';$md+='## 去重规则';$md+=''
foreach($x in $dedup){$md+="- $($x.repo) → $($x.canonical)：$($x.reason)"}
$md+='';$md+='## 本轮真实执行的CLI流程（新手可复查）';$md+=''
$md+='以下命令只读取GitHub公开内容。PowerShell中的`&`表示运行带空格路径的程序；不需要把尖括号占位符原样输入。已登录gh账号由主代理提供，本子任务没有更改登录或全局配置。'
$md+=''
$md+='```powershell'
$md+='$gh = ''C:\Program Files\GitHub CLI\gh.exe'''
$md+='& $gh api --method GET search/repositories -f ''q=remotion template video'' -f per_page=30'
$md+='& $gh api repos/actionow-ai/vvv'
$md+='& $gh api repos/actionow-ai/vvv/commits/main'
$md+='& $gh api ''repos/actionow-ai/vvv/git/trees/df9bb12f3d5f7add20959860de18e18c2a5c56f5?recursive=1'''
$md+='& $gh api ''repos/actionow-ai/vvv/contents/kits/remotion/src/templates/starter/index.tsx?ref=df9bb12f3d5f7add20959860de18e18c2a5c56f5'' -H ''Accept: application/vnd.github.raw+json'''
$md+='```'
$md+=''
$md+='输出怎么读：search的total_count是服务器估计命中总量，items是本页候选；repo的stargazers_count/pushed_at/default_branch/license只是元数据；commits拿到sha后，tree用recursive=1列全部路径；contents指定ref=sha读取固定版本源码。API的NOASSERTION/空license不代表可随意商用，必须读LICENSE原文。本轮正是读原文才发现Shotstack为PolyForm Shield。'
$md+=''
$md+='执行记录：首个scratch search.py尝试通过python命令启动时退出1且无输出，因此未产生搜索结果；随后8条查询全部由PowerShell直接gh api完成，searches.json与search_01–08.json可核对。actionow-ai/vvv根目录package.json请求404，因为实际Node工程在kits/remotion；已继续读取真实kits/remotion/package.json，不能将404当项目损坏。'
$md+=''
$md+='复现所有查询时可读取searches.json内query逐条调用同一gh命令。每条最多30项，不使用sort=stars，不用最低星数过滤；搜索总组共享配额，遇403先读rate-limit响应再等待，勿立即循环。其余仓库元数据/tree/contents读取不占repository search的同一小配额。'
$md+=''
$md+='## 从模板到成片的复用步骤（文档提取，未执行）';$md+=''
$md+='1. 选择具体模板风格，先保留默认素材跑官方样例；看清项目输出是MP4、HTML还是剪映draft ID。'
$md+='2. 只改模板开放的props/config/variables或素材路径，先不改时间线算法。替换素材需保持尺寸、裁切和文案容量。'
$md+='3. 如需听歌卡点，优先VVV/Slideshow这种代码中真实读取/生成beat grid的项目；固定start/end模板换歌后需重新调点。'
$md+='4. 小尺寸/短片段预览，检查开头、中间、结尾、文字溢出、人脸和音乐节拍，再全片渲染。'
$md+='5. 源码许可、依赖许可、示例素材许可分别核对。代码MIT不能自动覆盖Remotion、GSAP、字体或音乐。'
$md+=''
$md+='本轮没有提供可照抄的全自动安装脚本，因为没有在本机验证这些项目；具体命令证据都指向固定版本的package.json/README，应先运行项目doctor或样例。'
$md|Set-Content -LiteralPath (Join-Path $base 'review.md') -Encoding utf8
Write-Output "Wrote review.json + review.md; candidates=$(@($candidates).Count), shortlist=$($items.Count), seeds=$($seeds.Count)"
