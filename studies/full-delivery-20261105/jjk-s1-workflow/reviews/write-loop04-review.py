from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
R=Path(__file__).resolve().parents[1];L=R/'loops/loop-04';sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest();planSha=sha('loops/loop-04/plan.json');frozen=json.loads((L/'frozen.json').read_text(encoding='utf-8'))
proofs=[]
for c in range(20):
    rel=f'loops/loop-04/render-proofs/chunk-{c:02}.json';p=json.loads((R/rel).read_text(encoding='utf-8'));assert p.get('currentValidationPlanSha256',p['planSha256'])==planSha and len(p['outputFrameSha256'])==72 and p['inputSpec']['htmlSha256']==frozen['chunkHtmlSha256'][str(c)]
    if c not in [8,11,17,18]:assert p['reuseHistory'][-1]['actualPixelInputsByteEqual'] and p['reuseHistory'][-1]['allSourcePngReDecodedAndShaMatched']>0
    proofs.append(rel)
for frame in [624,823,829]:
    pr=json.loads((L/f'render-proofs/chunk-{frame//72:02}.json').read_text(encoding='utf-8'));assert sha(f'loops/loop-04/evidence/F{frame:04}.png')==pr['outputFrameSha256'][f'frame_{frame+1:06}.png']
chain=[]
for i in range(1,4):
    j=json.loads((R/f'loops/loop-{i:02}/review.json').read_text(encoding='utf-8'));assert j['reviewer']=='/root/s1_design_auditor'
    for path,h in j['boundArtifacts'].items():assert sha(path)==h,(i,path)
    chain.append({'loop':i,'reviewStatusAtThatTime':j['status'],'reviewSha256':sha(f'loops/loop-{i:02}/review.json')})
videos=['loops/loop-01/loop-01-rough-focus-v2.mp4','loops/loop-02/loop-02-composite-preview.mp4','loops/loop-03/loop-03-high-quality.mp4','loops/loop-04/loop-04-final.mp4'];assert len(set(sha(x) for x in videos))==4
closed=[
 {'id':'L2-EYE-01','status':'closed_in_actual_R4','evidence':'loops/loop-04/reviewer-evidence/actual-eyes-815-843.jpg','result':'实际816–829眼缝使用真实稳定相位；完整可见823–829的7帧近同轴，末829原尺寸暗瞳差约10px。830回基础微笑、842接前冲，无后半上漂。原生红小瞳/蓝大虹膜差异保留，不把虹膜大小强扭相同。'},
 {'id':'L3-CN-TYPE-09','status':'closed_in_actual_R4','evidence':'loops/loop-04/reviewer-evidence/actual-strike-611-638.jpg','result':'中文移左下黄色留白，实际613–637均可完整读，超过6连续帧；624原尺寸清晰，与手/袖有间距，英文仍完整。'},
 {'id':'L3-PACING-10','status':'closed_in_actual_R4','evidence':['loops/loop-04/reviewer-evidence/actual-tail-01.jpg','loops/loop-04/reviewer-evidence/actual-tail-02.jpg','loops/loop-04/reviewer-evidence/actual-tail-03.jpg'],'result':'原3.25秒凝视链改8帧起势眼→22帧近身换拳/扭肩→24帧真实旋转能量→24帧环境冲击浪，随后前景奔跑；实际1280–1362共83时位看完，中心聚合→扩张释放成立。不是用虚拟缩放代替身体动作。'},
 {'id':'L3-EVENTS-11','status':'closed_with_frozen_index_and_boundary_clarification','evidence':'reviews/event-clock-boundary-check.json','result':'16实际事件ID/binding/range已规范；4个出镜context明确不计内部占时。S048实际1152–1178在clap事件内，S046才是前镜context。不改冻结计划。'}]
files=videos+['loops/loop-04/plan.json','loops/loop-04/frozen.json','loops/loop-04/execution.json','loops/loop-04/render-completion.json','loops/loop-04/root-machine-check.json','loops/loop-04/capture-evidence.json','loops/loop-04/event-version-status.json','loops/loop-04/plan-precheck.json','loops/loop-04/prepared-review.json','loops/loop-04/reviewer-evidence/actual-film-check.json','loops/loop-04/evidence/F0624.png','loops/loop-04/evidence/F0823.png','loops/loop-04/evidence/F0829.png','loops/loop-01/review.json','loops/loop-02/review.json','loops/loop-03/review.json','reviews/素材集最终审核.json','reviews/event-clock-boundary-check.json','reviews/event-clock-boundary-check.md','reviews/studio-annotation-equivalence.json','evidence/ui/studio-annotation-drift/check.json','evidence/ui/studio-annotation-drift/expected-frozen-build.html','evidence/ui/studio-annotation-drift/studio-open-normalized.html','reviews/审核方法与学习笔记.md','music/music-report.json','music/master.wav','data/final-event-index.json','data/material-catalog.json','reviews/catalog-query665.5.json']+proofs
files += [f'loops/loop-04/reviewer-evidence/{s}.jpg' for s in ['actual-film-01','actual-film-02','actual-eyes-815-843','actual-strike-611-638','actual-tail-01','actual-tail-02','actual-tail-03']]
r={'reviewer':'/root/s1_design_auditor','reviewedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),'loop':4,'status':'pass','wholeFilmPass':True,'filmApproved':True,'finalApproval':False,'projectDeliveryApproved':False,'approvalScope':'actual_R4_video_visual_craft_and_machine_technical_checks; editable_project_delivery_gate_still_separate','boundArtifacts':{p:sha(p) for p in files},'actualArtifact':{'file':'loops/loop-04/loop-04-final.mp4','sha256':sha(videos[-1]),'width':1920,'height':1080,'fps':24,'frames':1440,'seconds':60,'bytes':(R/videos[-1]).stat().st_size},'technicalDecision':'pass','artDecision':'pass_for_documented_reference_adaptation_and_closed_P1s','blockingP1Count':0,'observedScope':{'actualMP4':'审核员独立全1440帧解码320×180；人工看完整60张整秒图、眼815–843的29图、STRIKE611–638的28图、尾1280–1362的83图。','fullsize':'实际看624中文、829双眼原尺寸，且核624/823/829保存PNG与对应新chunk proof中的真实捕获SHA一致；823由整事件图及proof核对，并不虚称逐像素人工测量。','priorEvidence':'新尾70个1920prepared逐帧RGB源序比对、65源PNG SHA/PTS/选样/5重复已独立材料门通过；其余16段按当前执行proof严格复用。','proofs':'独立读取20个归档proof，均plan51f4028…、各72输出hash条目；执行者另作完整key/payload/segment验。','reviewChain':'前三轮主review全部boundArtifacts再次逐SHA核对无漂移；四个不同实际视频SHA存在。','technicalAudio':'root全片解码1440、音频2,880,000采样、零偏相关0.9991414078、无异常近黑；音频只技术检查，未实际听音。','limitation':'全1440张原尺寸人工边缘扫描未执行；人工以完整片时序抽图+风险事件全帧+原尺寸关键图为范围。'},'closedInThisLoop':closed,'priorClosedFindingsRetained':['L1掌心焦点','L2裂边空黑','L2七叶未归位/暗叶','L2英文STRIKE遮词','L2换源episode/window错误','L2逐版本事件状态','L2 LIMITLESS遮合掌'],'remainingNonBlockingLimits':['V20为结构与技法的原创改编，原创档案屏不是动画实体手机跟踪；不宣称100%复刻或达到20参考全部镜头的原作者水准。','XPALM/XCHASE是实际源RGB+手工近似alpha，少量发梢/衣缘仍约1–8px近似；缺失腰袖通过出画处理，未补造肢体。','源底部裁切损失已披露，T091去下136行外圈保留中心，其他片安全带亦有损失。','BGM确来自V20音乐库候选，时长/采样/偏移已验证；分离残留、跨接乐句与听感未经实际试听，不把数值检查写成听感通过。','全季JPG/技术色彩标签完整不等于全季逐帧人物语义理解，未知身份和窗口证据边界继续保留。'],'referenceAssessment':{'retained':['手势焦点接力','短黑后稳定外框内换→直接全幅','动作与能量对比、尾部再次释放'],'authoredAdditions':['真实动态青掌/奔跑前景','漫画连续字形与九层厚度','带纤维/电弧渲染的人物裂条','同源七叶归位交接','独立胶片/记忆卡排版'],'motionAssessment':'尾部实际身体换位及能量/环境扩张使节奏有释放；保留档案屏、反应镜和短眼起势的呼吸，没有把所有保持帧当错误。'},'loopEvidence':{'priorReviews':chain,'fourDistinctVideos':[{ 'path':v,'sha256':sha(v)} for v in videos],'L4FreshChunks':[8,11,17,18],'L4ReusedChunks':16,'statusHistory':['L1 rough-focus-v2 pass for rough scope','L2 revise','L3 revise','L4 video pass']},'allowedNext':['promote_this_exact_video_as_canonical_deliverable','export_OpenChatCut_editable_projects_and_HyperFrames_release_bundle','run_final_editable_project_media_and_ui_verification','seal_project_only_after_separate_delivery_gate_pass'],'projectDeliveryGateStillRequired':['OpenChatCut实开并核查native/HF效果序列可播放与素材链接','HyperFrames规范无注释raw index封存、必要资产及可重渲参数齐；Studio注释差异依独立等价报告说明','中文学习入口/README/参考差异/最终结果与工程封存脚本实际通过']}
(L/'review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md='''# R4实际成片审核：视频通过，交付工程另验

审核员 `/root/s1_design_auditor`。实际文件：`loop-04-final.mp4`；SHA `'''+r['actualArtifact']['sha256']+'''`；1920×1080、24fps、1440帧、60秒。

**本轮视频视觉及技术验收通过，阻断P1为0。允许把这支确切视频作为canonical，并继续导出/验收可编辑工程。不是整个项目已经封存完成。**

## 三处实际整改

- 双眼只用816–829真实稳定相位；完整可见823–829有7帧近同轴。830回微笑、842接前冲，不再显示后半大幅上漂。原红小瞳与蓝虹膜的形态差异保留。
- STRIKE中文移到左下留白，613–637连续完整可读，和手掌/袖口分开；英文可读性保留。
- 尾部原凝视近景链改成短促眼神→近身换拳/扭肩→旋转能量→水浪扩张→前景奔跑。实际83个时位看完，局部动作到环境释放成立。原生CG明确记为原动画，而非本轮新建特效。

事件索引已规范，并以独立边界补注说明4个前镜context不算事件内部占时；未修改冻结渲染输入。

## 实际审阅范围

审核员另从实际MP4解码全1440张320×180图；人工看60张整秒图、29张眼缝及返回动作图、28张文字图、83张新尾部图。624文字与829双眼看原尺寸；对应保存PNG还与当前proof SHA核对。前轮审核绑定再次逐SHA全检，四轮均有不同真实视频。

根代理的整片技术报告通过：2,880,000音频采样、零偏相关约0.99914、无异常近黑。音乐来源为V20曲库候选，但**未实际听音**；不声称已确认分离无残留或循环乐句听感自然。

这是一支按V20结构/焦点/层级改编并加入真实alpha、漫画字、人物裂条与七叶交接的一分钟作品。它不是100%复刻，手工alpha和原片裁切仍有公开限制；全季技术标签也不等于全季语义逐帧理解。

## 下一道门

OpenChatCut工程实开、native/HF效果序列播放、素材链接、HyperFrames封存raw HTML/资产以及中文学习包仍需实际验收。Studio自动data-hf-id仅为编辑器选层元数据，已有等价证明；封存使用规范raw HTML最清楚，不因此重渲。
'''
(L/'review.md').write_text(md,encoding='utf-8');print(json.dumps({'status':'pass','filmApproved':True,'projectDeliveryApproved':False,'P1':0,'videoSha256':r['actualArtifact']['sha256'],'boundArtifacts':len(files)},ensure_ascii=False))
