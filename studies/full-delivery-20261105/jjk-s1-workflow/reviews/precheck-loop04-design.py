from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
R=Path(__file__).resolve().parents[1];L=R/'loops/loop-04'
sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
s=json.loads((L/'revision-spec.json').read_text(encoding='utf-8-sig'));m=json.loads((R/'data/tail-action-candidates.json').read_text(encoding='utf-8-sig'));p=json.loads((R/'loops/loop-03/plan.json').read_text(encoding='utf-8-sig'))
assert s['inputVideoSha256']==sha('loops/loop-03/loop-03-high-quality.mp4')
assert s['tailMaterialSha256']==sha('data/tail-action-candidates.json')
byid={x['candidateId']:x for x in m['items']};rows=[]
for a in s['tailActions']:
    b=byid[a['candidateId']];pts=b['sourcePtsSeconds'];over=[]
    for q in p['shots']:
        if q.get('sourceId')==a['sourceId'] and max(q['sourceInSeconds'],a['sourceCoreSeconds'][0])<min(q['sourceOutSeconds'],a['sourceCoreSeconds'][1]):over.append(q['id'])
    assert len(pts)==a['nativeFrames'] and all(x<y for x,y in zip(pts,pts[1:]));assert not over
    assert a['sourceId']==b['sourceId'] and a['sourcePath']==b['sourcePath'] and a['sourceCoreSeconds']==b['coreSourceSeconds']
    rows.append({'candidateId':a['candidateId'],'output':[a['outputStartFrame'],a['outputStartFrame']+a['outputFrames']],'nativeFrames':len(pts),'expectedDuplicateSamplesIfEvenNearestIncludesEnds':a['outputFrames']-len(pts),'sourceOverlapWithL3':over,'sourceIdentityAndPtsPass':True})
assert rows[0]['output']==[1290,1312] and rows[1]['output']==[1312,1336] and rows[2]['output']==[1336,1360]
files=['docs/L4精修设计.md','loops/loop-04/revision-spec.json','loops/loop-03/review.json','loops/loop-03/plan.json','data/tail-action-candidates.json','evidence/tail-action-preflight/TAIL-ACT-01-all-native.jpg','evidence/tail-action-preflight/TAIL-ACT-02-all-native.jpg','evidence/tail-action-preflight/TAIL-ACT-03-all-native.jpg','loops/loop-04/reviewer-evidence/C091-subtitle-source-check.png']
r={'reviewer':'/root/s1_design_auditor','reviewedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),'status':'pass','approvalScope':'original_full_resolution_core_decode_and_prepared_validation_only','wholeFilmPass':False,'finalApproval':False,'boundArtifacts':{f:sha(f) for f in files},'independentlyObserved':['65原生帧三组全联系表：真实拳臂换位/旋转能量/水浪扩张，核心内未观察到原切。','另由审核员从原E24以-ss665.62独立解码1张1920原图，实际看到字幕约y955–1015；该截图用于字幕风险定位，不作为正式取片PTS证据。','L3原尺寸823/828稳定相位实际已观察，缩短眼事件设计有证据支持；R4新位移与完整14f仍需实际捕获。'],'structureChecks':rows,'designJudgement':{'eye':'[816,830)真实稳定相位、返回基础12f→奔跑获准小样；完整可见823–829至少7f，暗瞳差≤20且不露空才闭项。','Chinese':'x430/y820方向可执行，至少6连续帧全词可读且和掌/袖留距；不由坐标预签。','tail':'8f眼起势+22f近战+24f旋转能量+24f水浪，局部动作→环境释放→XCHASE前景的递进有真实素材支持，允许高分取片。仍需切口视觉焦点/色彩/动作方向实际审。','eventNormalization':'允许规范最终actualBinding/range/asset/technique，保留L2/L3历史原字节。'},'captureGate':{'authorizedNow':False,'reason':'C091高分原图字幕上沿约955，默认crop保留0..959仍含字顶；应按真实上沿进一步裁去字幕或重构图，prepared全帧图谱经独立复核后再放行捕获。','requiredEvidence':['T062/T091/T007正式1920回源资产、每输出帧到真实PTS映射、duplicates显式标记','T091原生全部23帧及prepared全部24帧下沿检查，确定最终crop/scale参数和损失','新正式计划连续1440、源身份/检索窗/资产映射及主线重叠0错误','三个新片首尾与相邻输出切口的首轮检查']},'notes':['samplePolicy端点式采样输出70帧/65源native，预期5次复用；这些不是新增动作。原动画自身保持还应与采样重复分开。','文档0.873/0.95/0.93为核心窗口/输出时长近似，正式prepared报告以真实PTS映射和端点跨度为准，不宣称精确恒速。','此为R4范围预检，不是R4成片艺术pass，不替代新独立review。']}
r['revision']='R4-PRECHECK-2-crop944-explicit'
r['captureGate']['reason']='已认可T091原图crop[0,0,1920,944]+上下pad68的结构方案，避开已观察955字上沿并保留中央旋涡；须全23原生/24输出帧实查字幕、主体损失和PTS映射后，再独立放行捕获。单张不能证明全段。'
r['history']='初签绑定SHA已与crop944版相同（作者更新和签署调用交错），但初签仍引用默认960风险文字。本修订澄清当前944方案；初签及其实际绑定文件字节保存在design-precheck-initial-inputs，不虚构旧版签名。'
for q in sorted((L/'design-precheck-initial-inputs').glob('*')):
    if q.is_file():r['boundArtifacts'][q.relative_to(R).as_posix()]=sha(q.relative_to(R))
(L/'design-precheck.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(L/'design-precheck.md').write_text('''# R4设计预检：允许高分取片，捕获前再查字幕

审核员实际看过三组65原生帧，动作与PTS连续、源身份和原R3主线无重叠；眼缝14帧稳定相位、中文移空区、尾部8+22+24+24帧递进结构获准做正式prepared。输出仍连续60秒。

此处的pass只批准**回原视频高分解码与prepared验证**，不批准成片，也暂不批准最终捕获。审核员另解码原E24高分图发现字幕约y955–1015，默认保留0..959会含字顶。须进一步裁去或重构图，提交全23原生/24输出帧下沿与具体参数，独立复核后放行捕获；同时记录主体损失。

眼缝、中文和尾部衔接最终均看实际输出；不能用参数和四轮次数预签通过。完整绑定和确定性结构核对见design-precheck.json。
''',encoding='utf-8')
print('R4 design pass scoped original decode/prepared; crop944 explicit; capture pending subtitle/full mapping pilot review')
