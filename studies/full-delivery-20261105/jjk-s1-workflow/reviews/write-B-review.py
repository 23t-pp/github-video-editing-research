from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
R=Path(__file__).resolve().parents[1]
P=json.loads((R/'data/edit-plan.json').read_text(encoding='utf-8'))
assert P['fps']==24 and P['durationFrames']==1440 and len(P['shots'])==58
shots=P['shots'];assert shots[0]['startFrame']==0
assert all(a['startFrame']+a['frames']==b['startFrame'] for a,b in zip(shots,shots[1:]))
assert shots[-1]['startFrame']+shots[-1]['frames']==1440
videos=[s for s in shots if s['kind']=='video']
assert all(s['sourceId'].startswith('S1E') and '1080P 内嵌简中字幕' in s['sourcePath'] and Path(s['sourcePath']).is_file() for s in videos)
assert all(abs((s['sourceOutSeconds']-s['sourceInSeconds'])/(s['frames']/24)-s['playbackRate'])<1e-5 for s in videos)
assert hashlib.sha256((R/P['audio']['master']).read_bytes()).hexdigest()==P['audio']['masterSha256']
sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
slow=[{'shot':s['id'],'candidate':s['candidateId'],'outputSeconds':s['frames']/24,'sourceSeconds':s['sourceOutSeconds']-s['sourceInSeconds'],'rate':s['playbackRate']} for s in videos if s['playbackRate']<.5]
report={
'schemaVersion':1,'reviewer':'/root/s1_design_auditor','reviewedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
'status':'pass','decision':'pass','phase':'B_design_for_retrieval_and_loop1_prototype','versionReviewed':'EDIT-B0.1',
'boundArtifacts':{p:sha(p) for p in ['docs/剪辑设计.md','data/edit-plan.json','data/source-inventory.json','data/run-config.json','music/music-report.json','music/master.wav','data/随机参考抽选.json']},
'allowedActions':['retrieve_58_planned_shots_from_frozen_S1_sources','decode_and_validate_exact_source_cuts','prepare_real_C020_dynamic_palm_alpha','render_loop01_60s_naked_cut_prototype'],
'nextGate':'LOOP_1 independent review required before freezing advanced composition; every later loop requires new rendered artifact and independent review. No final film or alpha accepted by this design pass.',
'machineChecks':{'shotCount':58,'eventCount':14,'timelineContinuous':True,'frames':1440,'seconds':60,'fps':24,'allVideoPathsInFrozenS1Directory':True,'plannedRateDurationEquationsMatch':True,'musicShaMatches':True},
'visualReviewScope':{'reviewerViewed':['motion-01.jpg','motion-02.jpg','motion-03.jpg','motion-04.jpg','motion-05.jpg','motion-06.jpg','motion-07.jpg','motion-08.jpg'],'scope':'58组每组4时位稀疏预检图；不是完整动态或原生逐帧边界验收','observations':['C003/C020/C033确有掌部焦点，可探索开掌形状接力；需要重构图/尺度实测。','C020画面中青掌与暗背景分离较清楚，可做真实序列alpha；帧内青光属于源VFX。','C014红眼与C082蓝眼有可见近景，眼线角度/比例不相同，必须手工对位后看输出。','C052可见青色手部/源能量，适合同源翻叶；是否有前后余量必须实际取镜后验。','多镜本为对话或短动作，必须在实际粗剪检验节奏，不能用高图层数替代动作连贯。']},
'findings':[
 {'id':'B-SLOW-01','severity':'P1_if_retained_unexplained_in_final','status':'must_review_in_loop1','shots':slow,'issue':'低于0.5倍的短源镜拉到约1秒，有6–12个真实运动帧/秒的停顿风险；这不是60Hz拆解带来的流畅提升。','requiredAction':'L1实际查看这些镜；优先扩大经验证的同一原镜区间或缩短输出，确有意图的峰值停顿须写明freeze/graphic motion，不能暗示光流补帧或原生高帧率。'},
 {'id':'B-HANDOFF-02','severity':'P1_execution_gate','status':'must_resolve_before_loop2_acceptance','issue':'F1048–1074翻叶末端接S045的源入点尚未有精确源帧/速率映射。','requiredAction':'从C052同一源时钟取足前余量，末帧→下一基础帧连续，锁定衔接几何并输出±2帧联系表。'},
 {'id':'B-SOURCE-03','severity':'P1_execution_gate','status':'must_resolve_before_rough_acceptance','issue':'58镜源范围只是保守预检窗口；C033等接近源切镜，短样中已能看到4时位存在不同原镜。','requiredAction':'正式取回后逐帧确认所选区间没有意外隐切；所有更改写diff，不静默用第二季或循环帧填充。'},
 {'id':'B-ALPHA-04','severity':'P1_execution_gate','status':'must_resolve_before_loop2_acceptance','issue':'C020 alpha尚未存在，动态领先与能量裂口仍是计划。','requiredAction':'至少26个有效动态帧同号RGB；棋盘格/红底/实际背景检查青光溢出与袖口裁切；不能把移动静态PNG叫动态抠像。'},
 {'id':'B-FOCUS-05','severity':'P2','status':'review_in_loop1_and_loop2','issue':'0–2秒标题可能盖住开掌匹配，F1126–1178大字与合掌接力同区间。','requiredAction':'先保留裸切AB证据；主字放在主体焦点后方或避开手部，原尺寸确认关键词与手势均可读。'},
 {'id':'B-EDIT-06','severity':'P2','status':'accepted_design_choice','issue':'原素材没有适合的实体手机追踪；原创档案屏是结构改编，非原参考道具跟踪复刻。','requiredAction':'继续标注原创屏框；退出用有证据的直接全屏切，不伪称屏幕门户。'},
 {'id':'B-AUDIO-07','severity':'unverified','status':'not_aurally_accepted','issue':'V20库候选复用与1.347125s交叉只做数值设计，分离残留和乐句听感未试听。','requiredAction':'数值时长/波形/起音候选可验；最终保留auditoryListeningPerformed=false，不给听感通过结论。'}
],
'loopPlan':'L1完整裸切→L2真实复杂合成低清→L3高质量及修订→L4按具体发现真实修改终片；此为分阶段设计，4次视频和审核不是4次写日志。',
'notClaimed':['final_aesthetic_pass','all_selected_spans_native_cut_checked','alpha_quality_pass','audio_audition','full_dataset_complete']
}
(R/'reviews/剪辑设计审核.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(R/'reviews/剪辑设计审核.md').write_text('''# 剪辑设计B独立审核

审核版本EDIT-B0.1，审核者`/root/s1_design_auditor`。**pass，仅放行58镜回源、精确切边验证、C020真实动态青掌alpha准备及L1一分钟裸切小样。** 本签署不代表alpha或最终审美通过。

已独立看完motion-01至08全部58组×4时位预检图，机器核对58镜连续1440帧、24fps/60秒、第一季源路径、时长/倍率公式和音乐SHA一致。档案屏是原创改编，有明确诚实边界；同源翻叶与动态领先的设计可以执行，但精确源钟、alpha和动作锚点需在实际视频证明。

最需要L1处理的是低倍率慢放：S019、S034、S038、S040、S046的源片不足一秒，被拉至约一秒，S038更低至约0.255倍。不能因60Hz JPG有重复样本就说动作更流畅。优先回源扩大同一镜的真实动作区间或缩短输出；有意峰值停顿需明确标记并查看效果。

L1还应检查隐切与手势焦点；L2必须检查C020逐帧alpha、袖口截断、两眼对位、青光纸边及翻叶handoff。片名/大字不能盖住要学习的开掌与合掌动作。每项整改按findingId写旧新值、理由与重渲范围。

音乐仅数值确认，尚无听觉审美通过。四轮应为真实的粗剪、复杂合成、高清修订、最终整改；每轮独立审核后再前进。完整绑定SHA、待执行门和观察范围见JSON。
''',encoding='utf-8')
print(json.dumps({'status':'pass','scope':report['phase'],'slowShots':[s['shot'] for s in slow]},ensure_ascii=False))
