from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
R=Path(__file__).resolve().parents[1];L=R/'loops/loop-01';sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
P=json.loads((L/'plan.json').read_text(encoding='utf-8'));E=json.loads((L/'execution.json').read_text(encoding='utf-8'));M=json.loads((L/'root-machine-check-focus-v2.json').read_text(encoding='utf-8'))
assert sha(E['video'])==E['sha256']==M['sha256']=='d069face423c0822e52debf68377081b4eaf6052cef677472cf977960d0c075f'
assert M['machineState']=='pass' and M['fullDecodedFrames']==1440 and M['decodedAudioSampleFrames']==2880000
assert P['shots'][0]['startFrame']==0 and all(a['startFrame']+a['frames']==b['startFrame'] for a,b in zip(P['shots'],P['shots'][1:]))
initial=json.loads((L/'review-initial.json').read_text(encoding='utf-8'))
findings=initial['findings']
for f in findings:
    if f['id']=='L1-FOCUS-01':f.update(status='resolved_for_loop1',resolution='实际新片前45帧解码并查看15个时位、含F12/13和30/31两侧；掌心宏观特写落点明显接近，源图覆盖画布，无侧面空边。人物脸/指端裁切是已明示取舍，非恢复细节；人工粗标约1070,800不当作亚像素测量。',recheckEvidence=['evidence/palm-focus-AB.jpg','data/palm-focus-proposal.json','reviews/L1-focus-v2-实际前45帧抽查.jpg'])
report={'reviewer':'/root/s1_design_auditor','loop':1,'status':'pass','reviewedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),'artifactRole':'naked_rough_focus_revision_v2','boundArtifacts':{p:sha(p) for p in ['loops/loop-01/plan.json',E['video'],'loops/loop-01/execution.json','loops/loop-01/revision-diff.json','data/retrieved-assets.json','loops/loop-01/root-machine-check-focus-v2.json','evidence/palm-focus-AB.jpg','data/palm-focus-proposal.json','reviews/L1-focus-v2-实际前45帧抽查.jpg']},
'initialReviewRetained':'loops/loop-01/review-initial.json','initialVideoRetained':'loops/loop-01/loop-01-rough.mp4','initialVideoSha256':'d58dccaa12a7caf90e06fa486c25506f936d48eba34d5bcdae151ce467f903f2',
'observedScope':{'wholeRough':'沿用初稿已看58镜首中尾10页，复核新片前45帧解码中的15张运动时位及两切口AB；不是实时逐帧观看全片','geometry':'前三组为宏观手势特写，源图覆盖画布。第三镜底缘仍有残字/黑边差异，L2统一安全matte；没有把该局部小残留写成最终合格','numeric':'root新片1440帧完整缩略解码/60秒/音频2880000采样与零偏移对照通过；本审核校验视频与实际plan等指纹，未重复伪称独立听觉验收','auditoryListeningPerformed':False,'fullResolutionAllFramesIndividuallyViewed':False},
'technicalChecks':M,'findings':findings,
'additionalFindings':[{'id':'L1-TITLE-05','severity':'P2_now_P1_if_obstructs_final_focus','status':'carry_to_loop2','issue':'前三手掌已放大，开场大字不能再次盖住下半掌心焦点。','requiredAction':'L2将片名字放上方/缩短出现/作为掌后层，实际帧证明掌心和字均可辨。'},
{'id':'L1-DEDUP-06','severity':'P2','status':'carry_to_loop2','issue':'主线57镜48unique，9处重叠窗口复用；部分可回钩，但需避免无变化重复。','requiredAction':'L2取经源证据预检的新动作替换大部分重复，保留1–2处有意呼应并标理由；保留旧新candidate/source/frames及受影响事件diff。'}],
'allowedNextActions':['prepare_and_render_loop2_real_complex_low_resolution_composition','retrieve_and_preflight_replacement_S1_actions_for_logged_duplicate_reduction','apply_logged_safe_matte_and_title_hierarchy_fixes'],'advanceToLoop2':True,
'conclusion':'L1裸切原型复核通过，开掌焦点P1已由真实新视频关闭。只允许推进L2制作与独立审核；字幕、复杂alpha/纸边/布局/同源handoff及最终流畅仍未通过。'}
(L/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(L/'review-focus-v2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(L/'review.md').write_text('''# L1焦点修订版复核：通过原型，推进L2

实际新视频指纹`d069face…`，旧版`d58dccaa…`和初审保留。独立解码新片前45帧，查看15个运动时位及两切口AB；宏观掌心落点已经接近，源图填满横向画布，未见侧面露空。前三镜有脸/指端裁切且第三镜2.4倍放大，属于明示特写取舍，不是无损复刻。人工掌心坐标是构图参考，不是亚像素检测。

开掌焦点P1关闭，允许进入L2真实复杂合成与低清全片审核。第三镜底缘残字/黑边及其他多镜字幕残尖仍须在L2统一安全matte；片名不能盖掉已对齐的掌心。重复镜头应从57镜48unique/9重叠减少，保留少量有意回钩。

新片全1440帧缩略解码、60秒、音频采样与对齐报告通过，已核对实际plan与视频hash。本轮只验裸切原型；alpha、能量纸边、眼缝、七叶handoff、艺术字与最终画面密度还没有通过。没有实际听觉试听或逐张全分辨率人工审完1440帧。
''',encoding='utf-8')
print('LOOP1 focus-v2 PASS; advanceToLoop2=true')
