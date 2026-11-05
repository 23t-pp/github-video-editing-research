from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
report={
 'schemaVersion':1,'reviewer':'/root/s1_design_auditor','independentFromAuthorAndExecutor':True,
 'reviewedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
 'status':'pass','decision':'pass','phase':'A_material_preparation_design_only',
 'specVersion':'SPEC-0.2',
 'boundArtifacts':{p:sha(p) for p in ['docs/设计规格.md','data/acceptance-criteria.json','data/run-config.json','data/source-inventory.json','data/frame-pilot.json','data/随机参考抽选.json','scripts/extract-library.py']},
 'allowedActions':['materialize_pilot_episode_S1E01','machine_and_independent_review_of_pilot_episode','continue_source_semantic_curation','prepare_edit_design_B'],
 'notYetApproved':['bulk_remaining_23_episodes_before_pilot_review','formal_edit_design_B','final_film','full_dataset_completion'],
 'conclusion':'素材准备设计A通过，先执行S1E01一集；独立核对该集物理JPG/PTS/重复/数量及空间后再放行其余23集。设计B与终片未通过，不得将本pass作为所有阶段批准。',
 'findings':[
  {'id':'D-A01','severity':'P1','status':'resolved','issue':'同源拼图独立时钟的表述会破坏同源接镜','resolution':'SPEC-0.2 T03改为独立窗口与共用源时钟。'},
  {'id':'D-A02','severity':'P1','status':'resolved','issue':'完成缓存曾只看state，源或配置变化/丢图仍会假跳过','resolution':'提取器现在绑定config SHA和完整源SHA，回读SQLite数量/连续范围、磁盘JPG数量和每分钟首中尾解码。'},
  {'id':'D-A03','severity':'P1','status':'resolved','issue':'packet数不证明真实帧PTS；浮点尾界不满足确定性','resolution':'同次FFmpeg showinfo的真实n/整数PTS与输出JPEG配对；duration_ts×time_base用Fraction，采样比较使用整数式。'},
  {'id':'D-A04','severity':'P2','status':'accepted_with_followup','issue':'当前pilot只有E01十秒，未测P95','resolution':'不把均值说成上界；可用443GiB对逻辑均值估计约60.2GiB有余量，运行80GiB硬门。首集实测后重新估算其余23集规模。'},
  {'id':'D-A05','severity':'P1','status':'must_verify_before_dataset_acceptance','issue':'提取器分钟首中尾解码是抽检，不能证明所有唯一JPEG或所有硬链接完好','resolution':'root明确补最终独立QA：唯一JPEG逐张load+SHA、全部sample路径/文件ID/源映射校验；raw complete不能写最终corrupt0。'},
  {'id':'D-A06','severity':'P2','status':'must_verify_at_pilot_review','issue':'SQLite目前部分字段由join可推导，JSONL导出与显式storageMode/hardlinkTarget尚需检验','resolution':'试集核对原生PTS、sample n/60、duplicate指向与硬链接fileID；最终提供可读导出入口。'}
 ],
 'sourceEvidenceScope':{'machine':'读取24集ffprobe清单；全部24000/1001；02/05重复副本SHA一致；未另做全季解码。','human':'实际查看E01/E24总览共16张稀疏图，符合第一季起止内容；没有为其余每个动作背书。','paths':['reviews/素材身份抽查.md','evidence/source-overviews/S1E01-overview.jpg','evidence/source-overviews/S1E24-overview.jpg']},
 'determinism':{'sampleGrid':'n/60，归零于第一解码PTS；取不晚于sample的最近原帧；无AI/光流插值','storage':'每sample可打开的JPEG路径，重复以NTFS硬链接共享字节；硬链接失败复制受80GiB门监控；统计逻辑与物理占用','integrityLevels':'raw extraction、full structural/hash verification、sample decode、all unique JPEG decode分开报告'},
 'loopDesignAccepted':{'minimumLoops':4,'realArtifactsAndIndependentReviewsRequired':True,'failuresReturnToCurrentLoop':True,'continueIfUnresolvedP0P1':True,'emptyReportsDoNotCount':True},
 'remainingGates':['S1E01试集独立验收后才能扩全季','剪辑设计B需冻结具体EDL/技法事件/源证据/音乐处理并独立审核','四轮真实产物与审核、全素材集完整验收、工程重开与最终成片艺术验收仍未完成']
}
(R/'reviews/设计审核.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
text='''# 设计审核：阶段A通过，先执行一集

审核者：`/root/s1_design_auditor`，与设计作者、执行作者不同。审核对象为SPEC-0.2、验收标准、run-config与实际提取器；各文件SHA绑定在同名JSON。

**结论：pass，仅限素材准备设计A。先提取S1E01，再由独立审核者核对试集后放行剩余23集。** 正式剪辑设计B、全季素材集完成和最终成片均未通过。

已关闭的三个关键问题：同源窗口共享源时钟；缓存恢复核对源/配置/索引/文件；showinfo真实解码PTS配JPEG，并使用有理数/整数采样边界。设计已将60Hz重复样本与真实23.976fps动作区分，标记unknown语义，四轮都有实产物、独立审核和返修闭环。

试样仅10秒，平均31,361字节，尚无P95。当前约443GiB可用对均值估算有足够余量，但此为容量试跑放行，不是全季大小保证；保持80GiB运行门，试集后更新估计。

目前提取器的分钟首/中/尾JPG解码只是抽检。raw complete表示提取流程结束，不能据此声称所有JPG坏图0。整季素材集验收前，还需唯一JPEG全解码与SHA、每个sample路径与文件ID/映射核对、JSONL导出入口。缺这些证据时只标中间态。

源身份独立观察仅覆盖E01/E24总览16张稀疏图；24集流信息、重复副本SHA由执行清单读回。第一季全片逐帧语义未人工审完，标签需继续带证据及置信度。详见[素材身份抽查](素材身份抽查.md)。

阶段B需再签具体音乐处理、镜头单和技法映射；最终要审核四轮实产物、全季JPG完整性、MP4与OCC/HF真实工程重开。达到四轮本身不构成通过。
'''
(R/'reviews/设计审核.md').write_text(text,encoding='utf-8')
print(json.dumps({'status':report['status'],'phase':report['phase'],'allowedActions':report['allowedActions']},ensure_ascii=False))
