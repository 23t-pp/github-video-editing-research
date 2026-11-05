"""Generate beginner-facing guides from actual artifacts; never invent a passed review."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]

def read(path, default=None):
    p = ROOT / path
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default

loops = []
for p in sorted((ROOT / 'loops').glob('loop-*/execution.json')):
    e = json.loads(p.read_text(encoding='utf-8'))
    r = read(p.parent.relative_to(ROOT) / 'review.json', {})
    loops.append((e, r))
last = loops[-1] if loops else ({}, {})
approved = last[1].get('status') == 'pass' and last[0].get('loop', 0) >= 4
state = '末轮画面审核通过；交付文件与最终验收证据见下方' if approved else '制作中；未获得最终交付批准'
library = read('data/library-verification.json', {})
plan = read('hyperframes/edit.json', {})
movie = ROOT / '咒力接力_一分钟.mp4'
occ = read('openchatcut/工程包最终回读.json', {})
occ_name = occ.get('packageFilename', '')
occ_link = f'[OpenChatCut可编辑工程](<openchatcut/{occ_name}>)' if occ_name else 'OpenChatCut工程：等待最终媒体锁定与真实导入验收。'
sample_count = library.get('samples', 2061018)
video_count = sum(s.get('kind') != 'black' for s in plan.get('shots', []))

text = f'''# 咒力接力 · 第一季一分钟混剪与素材学习库

**当前状态：{state}。** 本目录属于第一季新片，与此前EDGE第二季V1/V2/V3分开保存。

这次交付的目标是：先把24集素材变成可查询的JPG库，再让设计、取片、执行和独立审核代理合作制作一分钟混剪。主参考只随机抽了一次，结果为V20；另外19条提供技法选择，不等于把20部的全部效果塞进一分钟，也不声称100%还原原作者工程。

## 先从哪里看

1. [一分钟成片](咒力接力_一分钟.mp4)：1920×1080、24fps、1440帧、60秒。
2. [学习入口](学习入口.html)：看不同制作轮次、按集数和秒数找JPG、查有证据的人物/动作候选。需要先启动下面的本地服务。
3. {occ_link}
4. [HyperFrames完整可编辑工程ZIP](HyperFrames可编辑工程.zip)：复杂字、抠像、裂边和空间布局在这里修改。
5. [中文操作与学习](docs/操作与学习.md)、[本片技法与参考逐项对照](docs/最终剪辑技法对照.md)、[技法适配与难易排行](docs/技法选用与难易排行.md)、[四轮改进对照](docs/四轮改进对照.md)。

## 不懂命令行也可以跟着做

打开PowerShell，把下面三行一次粘贴进去。前两行给长路径取名字，第三行启动本地只读学习服务。

```powershell
$s1Root = '{ROOT.as_posix()}'
$s1Py = 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $s1Py -X utf8 "$s1Root/scripts/serve-learning.py"
```

浏览器打开 <http://127.0.0.1:5351>。服务只读本工程，素材查询不依赖云端。PowerShell窗口保持打开；按Ctrl+C停止。如果5351已被这次服务占用，直接打开网页，不需要重复启动。

例子：选第24集、输入765秒，再点下一帧。采样每次前进1/60秒；有时图像不变，因为它仍指向同一原片帧。下方显示真实源PTS、原生帧号和重复标记。

视频上方选择轮次；视频下方可输入成片秒数、定位、前/后一成片帧。成片一步是1/24秒，与下面JPG的一步1/60秒分开显示。播放器刷新进度不会反复重载正在看的版本。

```powershell
& $s1Py -X utf8 "$s1Root/scripts/library-query.py" --episode 24 --time 765
& $s1Py -X utf8 "$s1Root/scripts/workflow.py" next
```

第一条返回这张JPG的位置与源时钟；第二条读取真实计划、执行和审核文件，显示下一步该交给哪个角色。它不会用一个脚本假装执行了多个代理。

## 素材库到底包含什么

- 24集第一季原视频，只读使用；02(1)/05(1)与正本逐字节相同，只索引一次。
- {sample_count:,}个60Hz JPG路径，映射823,577个原生帧ID；重复路径1,237,441个。原片为24000/1001fps，未插帧。
- JPG为640×360、JPEG q6，适合看图和检索。成片回1920×1080原视频取素材，没有用缩略图放大充当原画质。
- 共享源帧JPEG数据15,532,337,138字节；所有路径的逻辑JPG大小38,869,820,409字节。此数未包含SQLite/JSONL/NTFS元数据，不当作精确整目录磁盘占用。
- 每集都有真实PTS索引、逐行采样映射、SHA和完整性报告。所有原生JPEG完整解码与SHA通过，每个别名路径/文件ID/采样时钟均检查；独审另核24份报告并实际抽查。
- 97个静帧锚点有人工观察记录，另有58组四点短序列、12个新增窗口共331原生帧预检，以及第四轮3个尾动作窗口65原生帧。各范围有交集，不把它们相加冒称不重复覆盖总数。未看过的全季其余画面保持语义未知，不能把全部JPG生成称作全部剧情已理解。
- `material-catalog.json`将旧静帧与精确窗口证据分列。调度优先用窗口内人物/动作；C007/C091窗口中看不清人物，保留unknown，即使旧锚点曾推断了姓名也不沿用。

NTFS硬链接让多个名字共享同一份JPG。若要涂改一张，先复制为独立文件；不要直接覆盖硬链接。跨盘复制通常展开为独立副本，会多占空间。详细说明在[素材库README](素材集_60Hz_JPG/README.md)。

## 一分钟怎样设计

整体结构是伸掌/武器/腾空接力→档案屏群像→武器与手势→黑闪与冲锋→五条术式→动作回钩。当前主线含{video_count}段原视频镜头，另有明确黑场。多数源片裁去底部120行后上下各补60行；T091字幕较高，单独保留944行、上下各补68行，丢失下136行及能量外圈底部，中央旋涡保留。裁切实际丢失原图内容，不能说成恢复或无损去字幕。

实际制作的图层包括：持续存在的档案监视器、动态三联与记忆小窗、真实源RGB的26帧青掌和26帧跑动人物alpha、青紫电弧/纤维撕边、同源七叶展开、曲面厚字及前后景遮挡。动画本来就有的黑闪/术式/能量属于原片内容，不冒称新生成的3D或粒子。

完整效果与源时钟请看[HyperFrames实作笔记](docs/HyperFrames技法实作笔记.md)。是否达到预期以末轮独立审核为准，不能只用“用了多少特效”代替质量。

## 音乐为什么这样选

使用曲库V20对应的music-candidate，没有换用EDGE。这条候选实解码30.6735625秒；本次明确一分钟，所以同乐段复用两次，以1.347125秒等功率重叠接成60秒。输出48kHz双声道、2,880,000采样；片长与帧网格量化差为0。

10ms频谱起音检测为镜头切口提供候选，再量化到24fps；起音不等于强拍。音频逐样本时长、零时偏相关性与断尾数据有机器报告；制作中未实际听觉试听，不把去人声候选说成无残留纯音乐，也不声称已试听乐句接缝。

## 两种工程怎样改

|想修改的内容|打开哪里|保留的编辑能力|
|---|---|---|
|镜头顺序、源入点、基础构图、音轨|OCC的原生教学序列|独立视频clip与基础transform，复杂HF字效仅用教学小字说明|
|直接看完整效果，再裁整段|OCC的HF效果序列|20段各72帧的完整合成插片，加独立master；段内字/alpha已合成|
|人物边缘、字的曲面/厚度、电弧、七叶、窗布局|HyperFrames源码|edit.json、各Python模块、SVG字形、RGBA和源视频均保留|

两边没有自动双向同步。改HF后需重新渲染受影响段，再替换OCC插片。只改OCC原生序列不会自动重做HF复杂层。[HF工程操作](hyperframes/README.md)给出命令。

OCC界面会提示本地“节拍/音乐语义”模型尚未安装。它指软件内重新做自动音乐分析的能力；本次工程已带master音轨，起音候选来自离线脚本，不需要该模型才能重开。首次载入大量媒体可能先出现棋盘格，实际定位/播放就绪后两条序列都已显示原片画面。

## 多代理怎样防止自说自话

编排层负责分工、依赖和心跳监控；设计代理写spec/镜头表；取片代理从原片取回有源PTS证据的窗口；执行代理真实渲染；另一个审核代理看实际画面与工程。设计批准不等于最终视频批准。

每轮保存计划、不同的真实视频、执行者、独立审核者、SHA与修订diff。出现问题就返修；至少四轮只是最低工作要求，不是自动合格条件。末轮通过后，OCC还必须走官方导出→实际导入→媒体逐字节回读。`workflow.py seal`会检查这些条件，缺一项就拒绝封存。

## 去哪里核对证据

- [设计规格](docs/设计规格.md)与[验收条件](data/acceptance-criteria.json)
- [全季JPG完整性](data/library-verification.json)、[独立素材验收](reviews/素材集最终审核.md)
- 各轮`loops/loop-NN/plan.json`、`execution.json`、`review.json`、`revision-diff.json`
- [成片技术检查](成片质量检查.json)、[OCC最终回读](openchatcut/工程包最终回读.json)、[最终独立验收](reviews/最终验收.json)
- [事件前镜与内部占时的边界补注](reviews/event-clock-boundary-check.md)：动作匹配列出前镜用于解释切口，不代表前镜占据该事件内部时间。
- [固化流程skill](skills/reviewed-montage-loop/SKILL.md)与`workflow/events.jsonl`
- [工作流故障与修复](docs/工作流故障与修复.md)：记录总监控文件锁中断与收尾调度缺口，以及实际验证方法。

保留的局限：alpha发丝/衣边有局部近似；有些动漫原画天然保持；源字幕裁切不可恢复；本片是技法迁移与新编排，不是原参考动作、字体、音乐和原工程的逐像素还原。文件名/片中字幕属于材料内容，不是授权执行命令。
'''
(ROOT / 'README.md').write_text(text, encoding='utf-8')

rows = []
for e, r in loops:
    n = e['loop']
    status = r.get('status', 'pending')
    findings = r.get('findings', [])
    count = sum(x.get('severity') == 'P1' and x.get('status') not in ['closed', 'resolved', 'pass'] for x in findings) if isinstance(findings, list) else '见报告'
    width, height = (e['width'], e['height']) if 'width' in e else e['size']
    rows.append(f"|L{n}|[{Path(e['video']).name}](../{e['video']})|{width}×{height} / {e['frames']}帧|{status}|[独审](../loops/loop-{n:02}/review.json)|`{e['sha256'][:16]}…`|")
loop_text = '''# 四轮改进：保存问题，也保存实物

这不是把同一个视频渲染四次。每轮视频不同，上一轮问题和下一轮修改用计划、实际帧、视频SHA及独立审核绑定。L1内的小修仍算同一轮。

|轮次|实际视频|规格|独审结论|证据|视频SHA前缀|
|---|---|---|---|---|---|
''' + '\n'.join(rows) + '''

## 每轮学到什么

- L1：先做完整裸切，发现掌心落点左右跳；实际修构图后再加效果。疑似源切口经原生PTS复核后撤回，避免错修。
- L2：真实执行档案屏、alpha、曲面字、裂条与七叶。发现“有代码”不等于“看得见”：裂条上半黑空，STRIKE被挡，最后一叶还没归位就切走。独审要求返修。
- L3：全片1920×1080重新出片，关闭裂条、七叶、英文可读、合掌遮挡及换源元数据问题。但瞳位在事件后半段继续漂移，中文碎笔和尾段3.25秒连续凝视仍未过关，所以没有批准交付。
- L4及以后：根据L3具体问题缩短双眼稳定相位、把中文移到可读区、回第一季原片补真实动作。实际执行、通过与否请看上表当前报告；不能把“计划修了”写成“已经通过”。

## 查看一轮的顺序

1. `plan.json`：要求做什么，源片在哪，输出帧范围是什么。
2. `revision-diff.json`：相比前轮改了什么。
3. `execution.json`：谁实际渲染、视频在哪里、hash是什么。
4. `evidence/`和`capture-evidence.json`：看了哪些真实帧，哪些只是缩略联系表。
5. `review.json`：另一名代理发现什么、关闭什么、还不能宣称什么。

完整解码1440帧并不表示人工逐张查看1440张原尺寸图。每轮分别记录机器范围、人工联系表/原尺寸范围和试听范围，保留这几种证据的区别。
'''
(ROOT / 'docs/四轮改进对照.md').write_text(loop_text, encoding='utf-8')

tech = json.loads((ROOT.parent / 'reference-library-20261105/catalog/techniques.json').read_text(encoding='utf-8'))
rank = '''# 技法适配与当前难易排行

1最容易，5最难。这是当前本机把技法做成可控结果的难度，不是作品价值。完整掌握动作与遮挡需要素材证据，不能由安装一个工具替代。

## 本片最值得先学的次序

|学习次序|做什么|适合怎样的素材|本次经验|
|---|---|---|---|
|1|裸切、停顿与小字落定|有起手/命中/后摇的完整短动作|先接掌心、武器、眼神，不用闪白隐藏跳焦|
|2|动作/形状对齐|方向近似、主角尺度可匹配|源片内移镜也会改变焦点；只设事件首帧锚点不够|
|3|动态分屏、屏内换片|能装进窄窗的眼、脸、武器|条内要真有内容，不能只有发光空框|
|4|漫画字牌与前后遮挡|字幕空区明确、人物移动边界可知|字形厚度与细节再多，也要有连续完整阅读窗口|
|5|同源七叶交接|前段效果和后段全幅能取同一源片|最后一叶须先归平，下一帧源时钟接上|
|6|动态人物alpha与裂边|背景可分离、轮廓不被源画面切断|腰线要接出画边；逐帧RGB/alpha对应，发丝仍需人工修|
|7|精确运动匹配、跟踪/复杂3D|足够覆盖的动作、深度和遮挡素材|原片自带术式不等于我们新做了3D模拟|

## 20条参考提供的18类方法

下表沿用原学习库的证据分类。参考ID是观察来源，不代表本片每类都实际执行了；具体执行以最终edit.json和独审为准。

|难度|ID与手法|适配素材|为什么难/容易|参考|
|---|---|---|---|---|
'''
for t in sorted(tech['techniques'], key=lambda t: (t['difficulty'], t['id'])):
    materials = '；'.join(t.get('suitable_materials', [])[:2])
    refs = '、'.join(dict.fromkeys(x['reference_id'] for x in t.get('references', [])))
    rank += f"|{t['difficulty']}/5|{t['id']} {t['name_zh']}|{materials}|{t.get('reason','见原学习库配方')}|{refs}|\n"
rank += '''

T16的5/5指从成片重建原CG、摄影机与粒子系统。本次使用已有红钉/冲击浪镜头属于选片与普通合成，操作难度约2/5；不能把借用原动画VFX当作已经掌握5/5的CG重建。

## 调度素材时怎样判断

- 同动作转场：先看真实运动方向、动作相位、主体位置/大小和切口两侧，不按“都是拳头”就自动匹配。
- 画中画：先确认小窗中仍能识别主角/道具，再决定窗比例；多窗同时抢主体时应减少。
- 真实抠像：先检查原片有没有切掉手、腰和发梢；缺掉的部分不能靠alpha恢复。源帧、RGB和蒙版必须同号。
- 字效：先给词语留可读区域，再做厚度、曲面、透视、电弧；重叠出碎笔就需要改布局。
- 卡点：频谱起音只提供候选，画面还要对动作峰值。没有实际听觉试听的部分要明确保留未验证状态。

未实现的技法继续保持“等效建议/需要预处理”，不把观察到别人的效果写成自己的已验收能力。此学习库存储规则和证据，没有训练模型权重。
'''
(ROOT / 'docs/技法选用与难易排行.md').write_text(rank, encoding='utf-8')

hf_text = f'''# HyperFrames：完整效果可编辑工程

源文件：`edit.json`保存镜头、源入点、效果事件和图层绑定；`composition.py`把它生成`index.html`；`layoutfx.py/typefx.py/screenfx.py`分别负责布局、字形和档案屏；`assets/`含prepared视频、透明PNG、字体、GSAP及master音轨。

## 打开预览

解压ZIP后，用PowerShell进入此目录，再运行：

```powershell
$s1Node = 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
& $s1Node ./hf.mjs lint --json
& $s1Node ./hf.mjs preview --port 5352
```

浏览器按控制台地址打开HyperFrames Studio。`hf.mjs`调用本机已安装的CLI 0.8.216，并传入已存在的Chrome/FFmpeg路径；不会自行升级或重装软件。换电脑需安装对应依赖，并用`HYPERFRAMES_CLI`指定新的CLI文件。

## 修改后生成

```powershell
$s1Py = 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $s1Py -X utf8 ./composition.py
& $s1Node ./hf.mjs lint --json
```

先备份，再改JSON。0基成片帧号，区间[start,end)；1秒=24帧。`assetStartFrame`是prepared片的本地帧，不是全季JPG编号。修改英文词形后，曲面SVG还需相应字形路径，不能只改某个隐藏文字。

实际精确成片用`render.py`的72帧分段方案：源视频先解成同号PNG，alpha逐帧对应，HF CLI实际捕获，再验证全部20段依赖并编码。完整命令和实际执行者在各轮`execution.json`与实作笔记。它不是单纯把浏览器实时播放录屏。

`render.py`可按顺序捕获全部20段；工作区runner只是并行调度入口。ZIP保留创作资源和源码，原工作区保留逐段渲染proof/cache用于复验。普通Studio预览不需要解压全季JPG库，也不需要电影原片；重新选择全季其他素材则需要D盘原视频。

本次实际静态检查为0错误、9警告：同源多窗实例、逐帧alpha密集轨、复杂SVG层级和重叠图层较多。正式渲染使用分段HTML控制负载；这些警告没有被隐藏，也不建议直接一次捕获60秒全片HTML。Studio实测可选字效容器，但曲面字`editText=false`，完整改字仍回源码/字形路径。

Studio打开文件时会自动加入`data-hf-id`定位属性，Windows换行也可能从LF变为CRLF，因而文件SHA会变化。独立检查只去掉定位属性并规范换行后，要求与冻结计划生成的HTML完全相同；CSS、GSAP、媒体和布局不允许混入变化。本次ZIP与封存index使用精确UTF-8/LF原始生成字节，Studio注释版及等价报告另保存在证据目录。本机示范预览使用独立工作副本`work/jjk-s1-workflow/hf-studio-r4`，保护封存文件。你以后运行`composition.py`会备份Studio版本再生成HTML，D盘原视频不会被删除。

如果你在解压副本里改了效果，下面命令会生成第5轮完整视频，输出到副本旁的`loops/loop-05/`，保留本次最终文件：

```powershell
& $s1Py -X utf8 ./render.py --loop 5 --plan ./edit.json --work ../修改版渲染缓存
```

这会实际解码源PNG、调用HF截图再编码，耗时明显高于网页预览。参数`--work`只指定缓存目录，不改变D盘原片。视频源都已随包包含；想换包内没有的新镜头时，才回原片补取。

## 修改入口

|对象|字段/文件|
|---|---|
|镜头顺序与构图|edit.json shots：startFrame/frames/assetStartFrame/reframe|
|三联、眼缝、裂边、七叶、记忆窗|edit.json layouts + layoutfx.py|
|青掌与跑动前景|edit.json foregrounds + assets/alpha；不得打乱同号源钟|
|曲面/厚度字|edit.json typeEvents + typefx.py + barlow-glyphs.json|
|档案屏|archiveScreen + screenfx.py|
|音乐|assets/audio/master.wav；保持2,880,000采样即可继续60秒|

Studio里可播放/定位；本工程复杂效果为代码驱动，完整编辑入口是这些参数和源码，并非每个SVG路径都能用鼠标直接拖改。OCC的HF序列则是已合成插片，这些细层需回此工程。

当前版本：`{plan.get('version','unknown')}`。实际验收见项目根目录各轮review与最终验收；本README不会替代画面审核。
'''
(ROOT / 'hyperframes/README.md').write_text(hf_text, encoding='utf-8')
print(json.dumps({'state': state, 'loopCount': len(loops), 'docs': 5}, ensure_ascii=False))
