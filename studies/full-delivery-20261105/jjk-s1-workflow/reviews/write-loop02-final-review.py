from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
R=Path(__file__).resolve().parents[1];L=R/'loops/loop-02'
sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
contacts=['opening-slam','strike-type','limitless-type','weapon-triptych','paired-eyes','palm-energy-paper','memory-windows','yuji-runs-ahead','archive-screen','same-source-handoff-1060-1076','native-cut-adjacency']
files=['loops/loop-02/loop-02-composite-preview.mp4','loops/loop-02/plan-final.json','loops/loop-02/execution.json','loops/loop-02/frozen-final.json','loops/loop-02/revision-diff.json','loops/loop-02/render-completion.json','loops/loop-02/capture-evidence.json','loops/loop-02/root-machine-check.json','loops/loop-02/review-pilot.json','loops/loop-02/review-alpha-machine.json','loops/loop-02/review-pilot-inputs/metadata-precheck.json','loops/loop-02/reviewer-evidence/actual-video-01.jpg','loops/loop-02/reviewer-evidence/actual-video-02.jpg','loops/loop-02/reviewer-evidence/actual-video-and-proposal-check.json']+[f'loops/loop-02/evidence/{p}.jpg' for p in contacts]
findings=[
 {'id':'L2-EYE-01','severity':'P1','status':'open_confirmed_in_complete_L2','frames':[823,830,839,841],'issue':'左右双眼实际联系表仍显示红瞳约y435、蓝瞳约y555，约120px眼轴差；右眼开口也明显较大。主题相同但视觉焦点未匹配。','acceptance':'L3实际823/830/839及切口逐帧复核：眼轴差≤20px、眼白开口高度比约1–1.3；不能只凭变换参数闭项。','evidence':'loops/loop-02/evidence/paired-eyes.jpg'},
 {'id':'L2-TEAR-02','severity':'P1','status':'open_confirmed_in_complete_L2','frames':[970,980,995],'issue':'竖裂条上半持续大块空黑，横向青掌与竖向人物条没有内容关系；实际边缘发光存在，但空条像占位素材。','acceptance':'改用真实人物侧脸填竖条并使眼鼻可读，青掌独立前景且右袖出画；不得靠透明度掩饰空内容。提供全26帧及原尺寸关键帧。','evidence':'loops/loop-02/evidence/palm-energy-paper.jpg'},
 {'id':'L2-LEAF-03','severity':'P1','status':'open_upgraded_after_full_event_review','frames':list(range(1060,1077)),'issue':'前段面部受深阴影压暗；1073仍有后叶透出/倾角，1074才突然全幅，几何和亮度handoff未完成。','acceptance':'缩短展开/错开且降低遮罩；1071–1073全部归位、无阴影、全不透明，1073源F11→1074源F12，逐帧接触表验收。','evidence':'loops/loop-02/evidence/same-source-handoff-1060-1076.jpg'},
 {'id':'L2-TYPE-04','severity':'P1','status':'open_upgraded_after_full_event_review','frames':list(range(611,639)),'issue':'STRIKE大部时间被青掌盖住，约634–637掌淡出后才完整，清晰窗口约1–4帧，未满足连续6帧可读。','acceptance':'字上手下分区、保持动态前后顺序；完整STRIKE连续至少6帧清楚可读；全事件逐帧取证。','evidence':'loops/loop-02/evidence/strike-type.jpg'},
 {'id':'L2-META-05','severity':'P1','status':'open_in_frozen_L2_proposed_fix_machine_checked_only','shots':['S026','S037','S052','S053','S054','S056','S057','S058'],'issue':'8个换源镜继承旧searchWindow；S037/S052/S053/S056还继承错误episode。真实像素回源路径正确，但这些标记会误导下一次素材调度，必须与工程同步。','acceptance':'L3重建candidateId/sourceId/episode/inventory path/in-out/searchWindow/evidence并输出一致性0错误；保留L2错误证据。proposal57镜结构检查现为0错误，还需绑定正式L3计划。','evidence':'loops/loop-02/review-pilot-inputs/metadata-precheck.json'},
 {'id':'L2-ALPHA-06','severity':'P2_material_limit','status':'actual_XCHASE_placement_locally_passes_manual_edge_limit_remains','frames':list(range(1360,1386)),'issue':'全26帧实际合成中XCHASE腰线贴画底、左后手源裁切未在画中浮空，未见旧灰三角。1382–1385渐隐后切橙眼，是跨场景前景，不是同源handoff。','acceptance':'L3保留该摆位或修改后复核原尺寸；手工轮廓约1–8px近似不宣称完美。XPALM袖口仍应在右画外。','evidence':'loops/loop-02/evidence/yuji-runs-ahead.jpg'},
 {'id':'L2-STATE-07','severity':'P2','status':'open','issue':'冻结计划的14事件仍planned_not_rendered，execution证明全片确已渲染，但未提供逐事件实际版本状态图。','acceptance':'新增独立事件执行状态表（已渲染/待审/局部通过/待返修），绑定该版本捕获；保留冻结计划不回改历史。'},
 {'id':'L2-GESTURE-08','severity':'P2','status':'open_confirmed_full_event','frames':[1126,1151,1152,1177],'issue':'LIMITLESS文字可读，但52帧都占用合掌位置，动作匹配主角被字挡住。','acceptance':'文字让到右上天空等空区，中文与英文成组；提供全事件手掌连续无遮挡证据。','evidence':'loops/loop-02/evidence/limitless-type.jpg'}]
r={'reviewer':'/root/s1_design_auditor','status':'revise','advanceToLoop3ForRemediation':True,'wholeFilmPass':False,'finalApproval':False,'reviewedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),'reviewLevel':'complete_L2_artifact_review_with_declared_visual_sampling','boundArtifacts':{p:sha(p) for p in files},'actualArtifact':{'file':'loops/loop-02/loop-02-composite-preview.mp4','sha256':sha(files[0]),'width':960,'height':540,'fps':24,'frames':1440,'seconds':60},'observedScope':{'independentEncodedVideoInspection':'审核员从实际MP4独立解码每秒1帧共60帧并实际查看2页；不是仅看作者截图，也不是全1440帧逐张人工验收。','actualMasterContactsViewed':contacts,'technicalWholeDecode':'另核对root完整1440缩略解码报告及其文件SHA，2,880,000音频采样、同时间相关0.9991414，机器通过不代表美学通过。','priorPilot':'保留pilot6张初中期不可变快照、52张alpha RGB逐像素比对、各26帧红底/棋盘及2张原尺寸关键图结果。','auditoryListeningPerformed':False,'limits':['未进行实际听音，音乐分离残留和跨接听感不能在本轮签通过。','局部全帧联系表与整片每秒抽查仍不能证明所有原尺寸边缘无细小瑕疵；L3高质量片继续查。','可编辑OpenChatCut/HyperFrames完整交付尚待最终工程实开与媒体链接检查。']},'technicalDecision':'pass_for_L2_preview_spec_only','artDecision':'revise','findings':findings,'locallyWorks':['开场字上移后整词及三段手掌焦点基本分离，前作纯裸切已变成实际合成。','原创档案屏176–311内换真实源画面，312直接回全幅，继承V20屏内层级→全幅节奏；不冒称跟踪手机。','胶片三片与双记忆窗实际存在、位置序列可读；它们为补充排版，不把新增效果数量当复刻度评分。','XCHASE真实源RGB动态前景在实际26帧摆位局部成立，腰切线出画，主体边缘无先前灰三角。','主线替换使用真实第一季新源；C078/C088身份保持unknown。'],'L3Activation':{'allowed':True,'scope':['激活基于冻结L2的实际眼位/裂边/七叶/STRIKE/LIMITLESS修订','同步8处换源元数据，并补逐事件实际状态表','渲染1920×1080/24/1440帧完整L3，输出新SHA及真实修订diff','只对逐段HTML和媒体payload完全一致者复用捕获，所有受影响段重捕'],'proposalReview':'docs/L3精修设计.md及loop03 proposal整改方向获准执行，不等于修复通过。独立57镜结构检查为0错误，见actual-video-and-proposal-check.json。','documentationDrift':'第4节STRIKE拟y350/font270/width1380与plan-proposal实际y210/font240/width1400不一致；作者应同步以明确执行版本。','requiresIndependentNewReview':True},'nextGate':'L3实际新视频独立审核，所有P1闭项后仍需L4真实修订和最后工程验收；不得把本轮revise换为pass来满足轮数。'}
(L/'review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md='''# L2完整初版独立审核：需要修订，允许进入L3真实整改

审核员：`/root/s1_design_auditor`。输入为实际60秒、960×540、24fps、1440帧的完整合成初版，SHA `'''+r['actualArtifact']['sha256']+'''`。这是第二轮实际产物，不能作为最终成片通过。

我从编码MP4另行解码每秒1帧、共60帧，实际看完两页；又查看11组作者已冻结的实际捕获联系表，含全STRIKE、双眼、七叶交接、尾部动态前景以及114张切口邻帧。根代理的全1440帧机器解码及音频样本检查通过。以上范围并不等于逐张原尺寸人工审美验收，也没有实际听音。

## 必须修的5项P1

|编号|实际问题|下一轮验收|
|---|---|---|
|EYE-01|左右眼线约差120像素，眼白开口尺度不齐|看新像素，眼轴差≤20像素，开口比约1–1.3|
|TEAR-02|裂边竖条上半持续空黑|真实侧脸填条、眼鼻可见；动态青掌在条外且袖口出画|
|LEAF-03|1073后叶仍未归位、1074跳全幅，前段过暗|1071–1073全部归位、阴影归零，1073源F11→1074源F12|
|TYPE-04|STRIKE直到掌淡出才完整，仅约1–4帧可读|上字下手分区，至少连续6帧完整读词|
|META-05|8处换源旧检索窗，4处episode错误|正式L3计划、源路径、候选、入出点、证据0不一致|

另有P2：LIMITLESS连续遮住合掌主体，需要文字让位；已渲染14事件应单列真实执行/待审/待修状态。手工alpha边缘仍属近似，不宣称完美抠像。

## 已实际成立的局部

开场标题和掌心已分区；原创档案屏的内部换镜→直接全幅层级成立；胶片/记忆排版实际渲染。尾部XCHASE全26帧的腰线贴底、源裁切后手未浮空，未见旧灰三角；1382–1385渐出后切橙眼，这是跨场景前景，不能称为同源无缝交接。

## L3可以执行的范围

允许激活现有整改proposal并渲染1920×1080完整新片，逐项修复以上问题，保留L2及其错误证据。我独立检查proposal的57源镜episode、sourceId、文件、检索窗及证据存在性，结构错误为0；这不代表新像素已通过。STRIKE设计文档参数与proposal有小漂移，须明确以实际执行版为准并同步说明。

L3仍需新的独立审核，L4仍需真实不同的修订视频。音乐听感、原尺寸细边和OpenChatCut/HyperFrames可编辑工程实开验收留在后续门，不能因轮数够而跳过。

完整SHA、证据、8条finding及范围见同目录 `review.json`；审核员从实际MP4生成的两页位于 `reviewer-evidence/actual-video-01.jpg`、`actual-video-02.jpg`。
'''
(L/'review.md').write_text(md,encoding='utf-8')
print('L2 review: revise; advanceToLoop3ForRemediation=true; five P1 open; artifact bindings='+str(len(files)))
