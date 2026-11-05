from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1];L=R/'loops/loop-04';I=L/'prepared-review-inputs'
sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
for rel in ['data/retrieved-assets-loop4.json','data/tail-prepared-check.json']:
    dst=I/Path(rel).name
    if not dst.exists():shutil.copyfile(R/rel,dst)
files=['loops/loop-04/design-precheck.json','loops/loop-04/revision-spec.json','loops/loop-04/reviewer-evidence/prepared-independent-check.json','loops/loop-04/reviewer-evidence/T091-highres-native-bottom23.jpg']+[p.relative_to(R).as_posix() for p in sorted(I.iterdir()) if p.is_file()]
for aid in ['T062','T091','T007']:
    files += [f'hyperframes/assets/shots/{aid}.mp4',f'evidence/tail-retrieval/{aid}-all-prepared.jpg',f'evidence/tail-retrieval/{aid}-all-bottom-strips.jpg']
r={'reviewer':'/root/s1_design_auditor','reviewedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),'status':'pass','reviewLevel':'R4_prepared_material_gate_only','captureAuthorized':True,'wholeFilmPass':False,'finalApproval':False,'boundArtifacts':{p:sha(p) for p in files},'observedScope':['实际看T062全22/T091全24/T007全24编码prepared联系表，共70帧，真实拳臂/旋转/水浪运动保留。','实际看三组全部70帧下沿条；另看由正式高分原生PNG生成的T091全23帧原字幕区条，字幕存在于原片且在prepared已去净，中央旋涡保留。','审核员独立解码三个MP4全部70张1920×1080RGB，与其明确选中的原生PNG crop/pad比对，maxMAD为1.601/1.176/1.436；不是照抄作者检查。','独立核查65原生PNG SHA、真实整数PTS×timebase、70逐输出nearest-index选样和重复3+1+1标记；顺序正确。'],'subtitleDecision':{'T091':'crop0..943+pad68避开原字幕，实际24下沿无白字残尖；去原下136行外圈/下部粒子，中心能量仍可辨。','T062_T007':'crop0..959+pad60，全部编码下沿未见字幕残留。','lossDisclosureRequired':True},'allowedActions':['冻结按已审revision-spec及70-frame manifest构建的正式R4 plan','执行眼14f/中文新位/尾3动作的真实变化段capture，未变段严格payload校验后复用','编码完整1920×1080/24/1440帧新成片并提交独立review'],'stillPending':['正式R4连续1440帧/所有新资产offset/事件ID映射规范检查','816–843和612–638完整实际事件，以及1280–1362切口/焦点/色彩/动作节奏审','R4完整成片新SHA、technical checks、最终可编辑工程验收'],'limits':['材料门pass不等于中文/双眼/新尾部合成已经通过。','手工审图为全帧联系表与字幕区域条，不是逐张原尺寸全画面人工扫查；但全70原尺寸RGB顺序与cropped源比对已机器完成。']}
(L/'prepared-review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(L/'prepared-review.md').write_text('''# R4正式素材门：通过，允许实际捕获

审核员实际看完三组70帧prepared与全部下沿条、T091正式高分原生23帧字幕区条；T091 crop944后的24输出帧无可见白字残尖，中央能量保留。其下136原图行外圈损失须在学习说明披露。

另独立解码全部70张1920RGB逐张比对选中原PNG crop/pad，最大MAD分别1.601、1.176、1.436，符合有损编码误差。65原生文件SHA、整数PTS×timebase、70输出采样顺序及3+1+1重复标记均核查正确。

允许冻结正式R4计划、捕获真实变化段并编码整片；未变段按payload严格校验复用。这个pass仅为素材门，中文、双眼和新尾部实际合成仍须独立新片审核，未批准最终交付。
''',encoding='utf-8')
print('R4 prepared gate PASS; captureAuthorized=true; '+str(len(files))+' artifacts bound')
