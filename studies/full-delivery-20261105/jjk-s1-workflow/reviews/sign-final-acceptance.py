from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
R=Path(__file__).resolve().parents[1]
def sha(p):
    with (R/p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
check=json.loads((R/'reviews/final-preparation/all-ready-independent-check.json').read_text(encoding='utf-8'));assert check['frozenFilmReviewBindingsAllPass'] and check['OCCIndependentPackageRead']['mediaStreamsIndependentlyBase64DecodedShaCompared']==85
assert sha('README.md')==check['finalReadmeSha256']=='b44917f8d7a5e4504f02cf5639c5b6d1916ea2c5b793a84058a8c1c5aaf20e8d'
files=['咒力接力_一分钟.mp4','hyperframes/edit.json','openchatcut/工程包最终回读.json','data/hyperframes-package-verification.json','evidence/ui/最终交付界面验收.json','HyperFrames可编辑工程.zip','openchatcut/咒力接力 · CURSED FLOW.ccproj','loops/loop-04/review.json','README.md','学习入口.html','成片质量检查.json','hyperframes/index.html','hyperframes/README.md','openchatcut/README_工程说明.md','openchatcut/官方工程包验证.json','openchatcut/官方工程包导入回验.json','openchatcut/最终既有工程与写目标审计.json','reviews/final-preparation/preparation.json','reviews/final-preparation/all-ready-independent-check.json','reviews/final-preparation/learning-api-final-snapshot.json','reviews/final-preparation/next-before-final-sign.json','reviews/素材集最终审核.json','data/library-verification.json','data/library-summary.json','data/material-catalog.json','data/随机参考抽选.json','music/music-report.json','docs/操作与学习.md','docs/最终剪辑技法对照.md','docs/HyperFrames技法实作笔记.md','docs/技法选用与难易排行.md','docs/四轮改进对照.md','skills/reviewed-montage-loop/SKILL.md','scripts/workflow.py','scripts/monitor.py','scripts/serve-learning.py','workflow/final-dispatch-repair/verification.json','workflow/final-dispatch-repair/workflow.diff','workflow/monitor-repair/validation.json','workflow/monitor-repair/monitor.diff','reviews/event-clock-boundary-check.json','reviews/event-clock-boundary-check.md','reviews/studio-annotation-equivalence.json','reviews/审核方法与学习笔记.md']
ui=json.loads((R/'evidence/ui/最终交付界面验收.json').read_text(encoding='utf-8'))
files=list(dict.fromkeys(files+list(ui['boundArtifacts'])))
for p,h in ui['boundArtifacts'].items():assert sha(p)==h,p
r={'reviewer':'/root/s1_design_auditor','status':'pass','finalApproval':True,'projectDeliveryApproved':True,'reviewedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),'independence':'审核员未执行本片设计、正式取片、渲染或OCC导入；设计/执行/OCC/UI分别出证据，本审核员独立核文件、像素和交付包，不替作者自签。','scope':'第一季V20任务的本地素材库、60秒成片、双可编辑工程、中文学习文档及可恢复审核工作流；EDGE V3另属历史任务。','boundArtifacts':{p:sha(p) for p in files},'blockingFindings':[],'checks':{'dataset':'24集pass；2,061,018样本路径/823,577原生JPEG/1,237,441重复。全唯一JPEG解码与所有alias/PTS由verifier完成；独审核24报告/SQLite/JSONL及72实际图像样本，最终复核已签绑定，未重复全季解码。','fourLoops':'四支不同真实视频，L1粗剪范围pass、L2 revise、L3 revise、L4电影pass；旧签全部绑定无漂移。','film':'exact90d75e55…新片1920×1080/24/1440/60秒；全帧技术解码、2,880,000音频采样、零偏相关0.99914；眼位/中文/尾动作P1清零。','OCC':'独立流式读取205,861,867字节官方ccproj并解码85嵌入媒体，逐SHA与官方导出/实际导入报告一致；59原生镜源钟/构图/1x检查通过，20HF插片逐SHA对应R4渲染段；118项双份reframe及导入master288万采样一致。15既有工程保持未改。','HyperFrames':'独立读取ZIP216成员并验CRC/SHA；64视频/52alpha/音乐/字体/源码齐；最终包f849b667…未变、当前成员文件仍相同；index规范LF无data-hf-id，精确SHA6820afa3…。','UI':'编排层实际播放/定位与选层；审核员实际查看5张当前截图并核13绑定。成片54秒、HF26.083秒、OCC完整效果与原生两序列均显示真实媒体；未把截图当作审核员亲自执行过UI。','catalogAndLearning':'中文README已指向实际ccproj，技法/难易/四轮/操作说明齐；候选静帧与精确窗口分列，C007/C091 unknown约束正确，不把全季技术标签称作全剧情理解。','workflow':'已读next收尾链修复、核17隔离调度用例与seal AST未变；真实next为final_acceptance_pending，不提前complete。监控有限6次重试、终止失败保留旧state，API独立stale判断；最终活心跳约1.77秒、24集/4轮、alerts为空。'},'detailedEvidence':'reviews/final-preparation/all-ready-independent-check.json及各已签轮次review；此处引用现有范围，不复制或扩大它。','limitations':['未实际听觉试听；声音只验来源、时长、采样与时间对齐，分离残留及乐句听感未确认。','不是100%复刻；原创档案屏不冒称实体手机跟踪，原动画能量不冒称新建CG。','手工alpha局部边缘近似、底部字幕裁切有原内容损失，均已披露。','OCC的20HF段是合成插片；复杂字/alpha/裂条回HF源码编辑，两边无自动双向同步。曲面SVG不保证鼠标直接改字。','OCC可选本地节拍/音乐语义模型未安装；既有时间线、master与本次成片不依赖它。','机器完整解码不等于人工逐张看完所有原尺寸图；实际人工时序/关键帧范围见各轮报告。'],'allowedNextAction':'编排层现在运行workflow.py next，预期seal_pending，再实际运行workflow.py seal并核delivered及监控正常退出。','sealAlreadyExecutedByReviewer':False}
(R/'reviews/最终验收.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(R/'reviews/最终验收.md').write_text('''# 最终独立验收：通过，允许封存

审核员：`/root/s1_design_auditor`。本次第一季V20任务的本地交付已齐，阻断项为0。允许编排层运行`workflow.py seal`；本审核脚本没有代写delivered标记。

|交付|实际验收|
|---|---|
|素材库|24集；2,061,018条60Hz路径对应823,577原生JPEG，重复显式记录；不把技术标签称为全季语义理解|
|成片|1920×1080、24fps、1440帧、60秒；SHA `90d75e55…af682d`；L4三项P1均已实际闭合|
|四轮|四支不同视频与独立审核、修订及SHA证据完整，前两次合成未通过的记录保留|
|OpenChatCut|官方导出后实际导入；独立解码85包内媒体核SHA；59原生镜与20HF插片、源钟/构图/1x/master通过；15旧工程未改|
|HyperFrames|ZIP 216成员逐CRC/SHA、64视频、52alpha与音乐/字体/源码齐；规范LF原始HTML封存，Studio用独立工作副本|
|界面及学习|成片、HF、OCC两序列实际显示/播放；审核员看5截图并核13当前绑定；中文操作、技法适配、难易和四轮总结齐|
|工作流|next收尾链不再提前返回空动作；17测试与真实待总审状态已核。监控锁失败有限重试、stale独立判断及最新活心跳通过|

实际检查范围与49项左右的精确文件SHA绑定见[最终验收JSON](最终验收.json)，详细独立复核见[all-ready检查](final-preparation/all-ready-independent-check.json)。没有重复解码整季来凑检查数量。

保留的局限：未实际听音；不是100%复刻；alpha边缘和字幕裁切有公开取舍；复杂字/抠像回HF源码修改，OCC插片不能反拆成细层；可选本地音乐模型未安装，既有master和时间线可用。全帧机器解码也不等于全帧原尺寸人工审美检查。

可继续学习：[审核方法与学习笔记](审核方法与学习笔记.md)、[事件前镜上下文补注](event-clock-boundary-check.md)。这些说明把真实执行、检查范围和剩余差异分开，未将设计承诺写成实物完成。
''',encoding='utf-8')
print(json.dumps({'status':'pass','reviewer':r['reviewer'],'boundArtifacts':len(files),'README':r['boundArtifacts']['README.md'],'next':'seal_pending_then_actual_seal'},ensure_ascii=False))
