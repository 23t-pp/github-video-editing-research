from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
R=Path(__file__).resolve().parents[1];L=R/'loops/loop-01'
P=json.loads((L/'plan.json').read_text(encoding='utf-8'));E=json.loads((L/'execution.json').read_text(encoding='utf-8'));M=json.loads((L/'root-machine-check.json').read_text(encoding='utf-8'));A=json.loads((R/'data/retrieved-assets.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
assert sha(E['video'])==E['sha256']==M['sha256']
assert all(sha(a['file'])==a['sha256'] for a in A['assets'])
assert len(P['shots'])==58 and all(a['startFrame']+a['frames']==b['startFrame'] for a,b in zip(P['shots'],P['shots'][1:]))
report={'reviewer':'/root/s1_design_auditor','loop':1,'status':'revise','reviewedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),'artifactRole':'initial_naked_rough','boundArtifacts':{p:sha(p) for p in ['loops/loop-01/plan.json','loops/loop-01/loop-01-rough.mp4','loops/loop-01/execution.json','loops/loop-01/revision-diff.json','data/retrieved-assets.json','loops/loop-01/root-machine-check.json']},
'observedScope':{'contactSheets':'实际查看retrieval-01至10，覆盖58镜首中尾；另看S046全部26正式帧及原生PTS窗、S019/S038/S046慢窗；原尺寸抽查和后续AB仍有范围限制','sourceGlitch':'独立读取S1E07库F0014743/F0014745/F0014748，前两图已有横错行，后一图恢复；不能由此唯一判定原作者VFX或源编码加工','machine':'独立核对全部取回资产SHA、58镜连续；读取root完整1440帧缩略解码与音频样本/对齐报告，不把该报告当审美通过','notPerformed':['actual auditory listening','all 1440 frames full-resolution manual review','complex effects acceptance']},
'technicalChecks':{'allRetrievedAssetHashesMatch':True,'shots':58,'sourceVideoClips':57,'frames':1440,'fps':24,'seconds':60,'audioSampleFrames':2880000,'zeroOffsetAudioCorrelation':M['sameTimeCorrelation'],'intentionalBlackFrames':[168,176],'blackReview':'首中尾图显示8帧设计黑停顿；root mean<3阈值不把#080b13算纯黑，因此不能拿nearBlack0说没有设计黑场'},
'findings':[
 {'id':'L1-FOCUS-01','severity':'P1','status':'open','frames':[12,13,30,31],'issue':'开掌接力的手掌焦点右侧→中部→左下，观看落点明显跳；目前只证明同为手掌，尚未证明焦点连续。','evidence':['evidence/retrieved-shot-contacts/retrieval-01.jpg'],'requiredAction':'保留原版，制作裸切对齐版本：在安全构图内调整源片位置/尺度或动作相位，使同一掌心锚点接近并量测误差；检查完整手势不被裁掉、无空边。单独看AB后更新L1视频/plan/diff/执行hash，再复核。不能用大字/闪光遮掉问题。'},
 {'id':'L1-MATTE-02','severity':'P2_for_rough_P1_if_final','status':'carry_to_loop2','issue':'很多镜头底边留有内嵌字幕的白色残尖，黑边与有效画面交界不干净。','evidence':['evidence/retrieved-shot-contacts/retrieval-01.jpg','evidence/retrieved-shot-contacts/retrieval-04.jpg','evidence/retrieved-shot-contacts/retrieval-07.jpg'],'requiredAction':'L2采用经原尺寸核对的安全matte/裁切，边界统一；检查掌、武器与下巴的损失，不声称恢复被裁掉内容。'},
 {'id':'L1-SOURCE-03','severity':'P2','status':'source_origin_confirmed_choice_pending','shot':'S022','issue':'S022末端可见横错行；同一源PTS的全季JPG也存在，非本轮编码新引入。仅末一帧切走可能显突兀。','evidence':['evidence/retrieved-shot-contacts/retrieval-04.jpg','素材集_60Hz_JPG/S1E07/minute-004/F0014743.jpg','素材集_60Hz_JPG/S1E07/minute-004/F0014745.jpg','素材集_60Hz_JPG/S1E07/minute-004/F0014748.jpg'],'requiredAction':'记录来源，选择移开此源时位或保留有意完整短过门；无证据不称其为新增故障特效或必然坏帧。'},
 {'id':'L1-S046-CHECK','severity':'none','status':'closed_false_alarm','issue':'审核者最初从预检小图误读切口约919.74，怀疑S046跨原切。','resolution':'独立查看formal12–37共26帧均为中景；真实原生PTS中cut在920.127542，当前所用区间结束前，撤销跨切判断，不要求无谓重渲。','evidence':['evidence/S046-prepared-all.jpg','evidence/S046-original-all.jpg','evidence/S046-cut-verification.json']},
 {'id':'B-SLOW-01','severity':'none','status':'resolved_for_prototype','resolution':'五个低于0.5倍率已由真实扩大源区间修至1/1/.7/.8/1；联系表显示真实动作与短暂姿态变化，不再以原极低倍率拉长。高能程度仍要在最终完整合成审核。'},
 {'id':'L1-REPEAT-04','severity':'P2','status':'review_in_loop3','issue':'S005/S026、S007/S037、S008/S054、S014/S049等复用相同动作窗口。可作为接力回钩，但终片需避免机械重复。','requiredAction':'L3从完整片检查复用是否有结构作用，必要时换同一源附近不同相位或换已审镜头，不仅增加滤镜。'}],
'allowedNextActions':['revise_loop1_palm_focus_and_render_new_version','prepare_independent_alpha_assets_without_claiming_loop2_pass'],'advanceToLoop2':False,'conclusion':'L1技术可用且素材季数范围成立；开掌焦点P1需要实际裸切修订后复核，当前不放行冻结L2整片合成。'}
for name in ['review-initial.json','review.json']:(L/name).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(L/'review-initial.md').write_text('''# L1初稿独立审核：需修订

审核对象为d58dccaa开头指纹的L1裸切片，实际查看58镜首中尾10页，以及慢窗/源PTS疑点证据。机器完整解码和音频数值通过不等同视觉通过。

阻断项L1-FOCUS-01：开掌接力的掌心落点右→中→左下，需调整安全构图或择相位，并给裸切AB。请保留当前初稿，新文件名与新hash复核后再冻结L2。复杂效果仍未执行，不以尚未有字效/alpha来判粗剪失败。

字幕残尖明确存在，列为L2必修；S022末端横错行已确认源中存在，应作有说明的取舍。S046曾被审核者从小图误判跨切，完整formal26帧和原生PTS证据排除了该问题，撤销该项，不要求无谓改源。五个极慢镜的修订已在粗剪阶段成立。

没有实际听觉试听，也未逐张人工全分辨率查看1440帧。详细发现、证据、输入hash和后续允许范围见JSON。
''',encoding='utf-8')
print('L1 initial review: revise, focus P1 open; S046 false alarm closed')
