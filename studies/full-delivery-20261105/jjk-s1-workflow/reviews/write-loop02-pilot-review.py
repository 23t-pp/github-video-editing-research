from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
R=Path(__file__).resolve().parents[1];L=R/'loops/loop-02';sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
pics=['evidence/L2-early-capture/frame_000025-title-fixed.png','evidence/L2-early-capture/frame_000241.png','evidence/L2-middle-capture/frame_000627-initial.png','evidence/L2-middle-capture/frame_000831-initial.png','evidence/L2-middle-capture/frame_000981-initial.png','evidence/L2-middle-capture/frame_001065-initial.png']
inputs=[p.relative_to(R).as_posix() for p in sorted((L/'review-pilot-inputs').rglob('*')) if p.is_file()]
r={'reviewer':'/root/s1_design_auditor','status':'revise','reviewLevel':'partial_pilot_only_not_whole_film','reviewedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),'frameIndexing':'PNG suffix is1-based; frame_000831 is globalF830','boundArtifacts':{p:sha(p) for p in pics+inputs+['loops/loop-02/review-alpha-machine.json']},
'observedScope':'独立实际查看6张初期/中期实际渲染不可变快照；XCHASE与XPALM各26帧红/棋盘canonical联系表，以及XCHASE F07/F23原尺寸；这些不是最终完整L2艺术验收。',
'materialChecks':{'groups':['XCHASE','XPALM'],'alphaPngFrames':52,'allRgbIndependentlyComparedWithSamePreparedFrame':True,'allBlackBandAlphaZero':True,'XCHASEFrozenManifestAllFilesShaMatch':True,'evidence':'loops/loop-02/review-alpha-machine.json','scope':'素材完整性通过；轮廓近似与摆位仍须实际合成查看，未批准所有alpha审美。'},
'findings':[
 {'id':'L2-EYE-01','severity':'P1','status':'found_in_initial_copy_final_fix_not_yet_reviewed','frames':[830],'issue':'左红瞳约(665,435)、右蓝瞳约(1370,555)，眼线差约120px、眼白开口高度比例约1:1.6，不符合眼线对位设计。','requiredAction':'先将两个眼中心归同一输出y≈530，差控制在约20px内；统一眼白开口到约1–1.3比例，再调左右焦点。新实际图与邻帧复核，不能只对中线。','evidence':pics[3]},
 {'id':'L2-TEAR-02','severity':'P1','status':'open','frames':[980],'issue':'竖条x1120–1440的上半y100–450大块为空黑，横向手掌并非条内竖向主体。虽然边缘发光已渲染，内容组织失败。','requiredAction':'保留竖条则换有内容的真实脸部片并让青掌越界；或改横向贴合手部的裂口。清除黑空块，保持真实边缘渲染与运动顺序。','evidence':pics[4]},
 {'id':'L2-LEAF-03','severity':'P2_pending_handoff_check','status':'open','frames':[1064],'issue':'已接近展开的七叶及面部仍明显发暗，主体可读性弱。单张不能确定末端handoff是否也跳亮。','requiredAction':'降低shade或只对背面加阴影；给1071–1075邻帧检查末1073回到正常亮度/几何/源F11，1074接F12，连续源时钟不能重播。','evidence':pics[5]},
 {'id':'L2-TYPE-04','severity':'P2_pending_temporal_readability_P1_if_no_readable_window','status':'open','frames':[626],'issue':'STRIKE大部被掌盖，在该帧只ST较完整，仍需整事件证据确定是否存在可读窗口。','requiredAction':'证明至少约6帧主词可读，或将字移到上方独立行/缩掌约0.75；保留文字与手的主次，不用一句“遮挡效果”替代可读性。','evidence':pics[2]},
 {'id':'L2-META-05','severity':'P1','status':'open','issue':'独立读冻结计划：8处替换继承旧检索窗口；其中S037/S052/S053/S056的episode与sourceId不一致，证据指针也需逐项校正。会导致后续取片调度错误。','requiredAction':'L3同步candidateId/sourceId/episode/inventory path/正式入出点/searchWindow/evidence；相同总览页仅在确含新时位时可复用并标时位，不能默认旧证据有效。机器一致性检查应输出0错误。','evidence':'loops/loop-02/review-pilot-inputs/metadata-precheck.json'},
 {'id':'L2-ALPHA-06','severity':'P2_material_limits','status':'must_check_actual_composite','issue':'XCHASE腰线/拳与后手有原生出画裁切；XPALM袖口右端亦到源画边。红底上轮廓可用于合成，但浮在画布中央会暴露平切。','requiredAction':'将裁切压画框底或出画；检查XCHASE末26帧实际摆位、入出场及背景交接，不能补造缺失肢体。头发/衣缘少量手工近似按原尺寸实际背景审。'},
 {'id':'L2-STATE-07','severity':'P2','status':'open_until_execution_map','issue':'冻结设计事件仍全部planned_not_rendered；计划可保留原状态，但需有逐版本执行状态表避免后续调度误读。','requiredAction':'在execution或独立事件状态文件逐项记录实际已渲染/待审/已通过及时间证据，不改过去计划来伪造历史。'}],
'locallyWorks':['上移后的CURSED FLOW在F24整词可见，掌心有独立区域；时序仍待完整事件审。','F240原创档案屏的边框、内部真实人物、顶部双语标签、暗网格背景在单帧结构上成立。','XPALM可见完整弯指，26帧RGB保持源像素；不把原青焰说成新增CG。'],
'allowedActions':['finish_and_freeze_actual_full_loop2_initial_artifact','prepare_loop3_remediation_proposal','render_loop3_remediation_after_frozen_loop2_review'],'wholeFilmPass':False,'finalApproval':False}
(L/'review-pilot.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('L2 pilot review persisted: revise, not whole film pass')
