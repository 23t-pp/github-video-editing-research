from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];L=R/'loops/loop-03';O=L/'reviewer-evidence'
sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
anchors=[(823,(640,525),(1280,520)),(828,(650,530),(1280,510)),(830,(650,530),(1280,460)),(839,(655,535),(1300,305))]
im=Image.new('RGB',(1920,1128),'#090f19');d=ImageDraw.Draw(im)
for j,(f,red,blue) in enumerate(anchors):
    a=Image.open(L/f'evidence/F{f:04}.png').convert('RGB');a.thumbnail((960,540));x=j%2*960;y=j//2*564;im.paste(a,(x,y))
    for pt,c in [(red,'#ff6c62'),(blue,'#65c8ff')]:
        cx=x+pt[0]/2;cy=y+pt[1]/2;d.line((x,cy,x+960,cy),fill=c,width=2);d.ellipse((cx-6,cy-6,cx+6,cy+6),outline=c,width=2)
    d.text((x+10,y+543),f'F{f} manual dark pupil y: red~{red[1]}, blue~{blue[1]}, delta~{abs(red[1]-blue[1])}px',fill='white')
im.save(O/'eye-axis-manual-anchors.jpg',quality=95)
(O/'eye-axis-manual-anchors.json').write_text(json.dumps({'reviewer':'/root/s1_design_auditor','method':'人工从实际原尺寸PNG估读暗瞳几何中心，约±10–15px；不把HSV下弧或高光质心当瞳孔中心，也非全帧自动跟踪。','anchors':[{'frame':f,'redPupilApprox':r,'blueDarkPupilApprox':b,'deltaYApprox':abs(r[1]-b[1]),'inputSha256':sha(f'loops/loop-03/evidence/F{f:04}.png')} for f,r,b in anchors]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
bound=['loops/loop-03/loop-03-high-quality.mp4','loops/loop-03/plan.json','loops/loop-03/execution.json','loops/loop-03/render-completion.json','loops/loop-03/frozen.json','loops/loop-03/capture-evidence.json','loops/loop-03/event-version-status.json','loops/loop-03/revision-diff.json','loops/loop-03/reused-payload-validation.json','loops/loop-03/root-machine-check.json','data/metadata-consistency-L3.json','loops/loop-02/review.json']
bound += [f'loops/loop-03/evidence/{x}.jpg' for x in ['paired-eyes','strike-type','palm-energy-paper','same-source-leaves','limitless-type']]
bound += [f'loops/loop-03/evidence/F{x:04}.png' for x,_,_ in anchors]
bound += [x.relative_to(R).as_posix() for x in sorted(O.glob('*')) if x.is_file()]
ref=['../reference-library-20261105/evidence/V20/'+x for x in ['overview.jpg','native-013.jpg','native-014.jpg','native-015.jpg']]
bound +=ref
closed=[
 {'id':'L2-TEAR-02','state':'closed_for_L3_observed_event','evidence':'loops/loop-03/evidence/palm-energy-paper.jpg','why':'全事件竖条由真实侧脸填充，眼鼻可见；前景青掌与竖条分离，原上半空黑块已去除，边缘发光仍在。'},
 {'id':'L2-LEAF-03','state':'closed_for_L3_observed_event','evidence':'loops/loop-03/evidence/same-source-leaves.jpg','why':'全事件1062–1074可见1071–1073全部归位、正常明度，1074续同源；不再发生后叶未归位的几何跳变。'},
 {'id':'L2-TYPE-04','state':'English_requirement_closed_new_Chinese_finding_open','evidence':'loops/loop-03/evidence/strike-type.jpg','why':'STRIKE整个主词约613–637连续完整可读，英文≥6帧要求已满足；中文另列新缺陷，不倒改原验收。'},
 {'id':'L2-META-05','state':'closed_for_actual_L3_plan','evidence':'loops/loop-03/reviewer-evidence/actual-film-check.json','why':'审核员独立重查正式plan57镜sourceId/episode/inventory.localPath/检索窗包容正式源区间/证据存在性，错误0；仍不把路径存在当语义全证实。'},
 {'id':'L2-STATE-07','state':'closed_for_L3_version_snapshot','evidence':'loops/loop-03/event-version-status.json','why':'14稳定事件+新增XCHASE共15项逐版本实际binding、区间、rendered_pending_review及新片SHA已存；不使用data可变latest替代冻结证据。'},
 {'id':'L2-GESTURE-08','state':'closed_for_L3_observed_event','evidence':'loops/loop-03/evidence/limitless-type.jpg','why':'全52帧文字移至右上，合掌动作位置连续无遮挡，中文与英文成组。'}]
find=[
 {'id':'L2-EYE-01','severity':'P1','status':'still_open_after_real_L3_revision','range':[816,842],'issue':'F823暗蓝瞳约y520/红525；828约510/530；830约460/530；839约305/535，后半眼焦点偏移约230px。初始调位有效，源眼部向上运动令后半失配，HSV蓝环质心目标不能代表整段对位。','requiredAction':'按实际每帧暗瞳/虹膜几何锚点跟踪y补偿，或重选保持相位的真实源窗。不能恒加65；需全26帧眼线、眼白尺度、不露空验证。','evidence':'loops/loop-03/reviewer-evidence/eye-axis-manual-anchors.jpg'},
 {'id':'L3-CN-TYPE-09','severity':'P1','status':'new_visible_regression','range':[612,638],'issue':'英文STRIKE已修，但底中文被下移青掌遮住，主体段只剩碎笔画，直到约634–637才逐渐显出。可见残笔比干净没有副标更像错误。','requiredAction':'把中文移至不和掌/袖重叠的左下空区或重新布局，至少连续6帧完整可读；可设计省略副标，但必须同步工程说明，不能留碎笔。','evidence':'loops/loop-03/evidence/strike-type.jpg'},
 {'id':'L3-PACING-10','severity':'P1_creative_goal','status':'new_whole_film_finding','range':[1282,1360],'issue':'记忆窗后约53.4–56.7秒连续紫眼保持→侧脸→蓝眼，3.25秒凝视近景链缺少动作释放，尾部能量弱。与V20尾段实际射网、跃起、回身再尾卡的运动接力差距明确，不能用新增事件数量抵消。','requiredAction':'R4给出尾部动作接力或短促眼神→动作释放的具体取片方案，保持60秒/当前BGM；用真实角色动作、方向及相位承接，先预检源切口与焦点再渲。保留必要呼吸，不要求所有低运动镜都变快。','evidence':['loops/loop-03/reviewer-evidence/actual-film-02.jpg','loops/loop-03/reviewer-evidence/low-motion-candidates-first-mid-last.jpg','../reference-library-20261105/evidence/V20/native-013.jpg','../reference-library-20261105/evidence/V20/native-014.jpg','../reference-library-20261105/evidence/V20/native-015.jpg']},
 {'id':'L3-EVENTS-11','severity':'P2','status':'final_normalization_pending','issue':'旧events作为历史意图已通过独立版本状态图消歧；最终交付工程应进一步规范为实际稳定ID/binding/range，防止学习者直接读取旧561–612或1048–1074而误解。','requiredAction':'L4最终元数据规范，保留L2/L3冻结历史，执行render payload变化另核查。'}]
r={'reviewer':'/root/s1_design_auditor','reviewedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),'loop':3,'status':'revise','advanceToLoop4ForRemediation':True,'finalApproval':False,'wholeFilmPass':False,'boundArtifacts':{p:sha(p) for p in bound},'actualArtifact':{'file':'loops/loop-03/loop-03-high-quality.mp4','sha256':sha(bound[0]),'width':1920,'height':1080,'fps':24,'frames':1440,'seconds':60},'technicalDecision':'pass','artDecision':'revise','observedScope':{'actualVideo':'审核员独立全1440帧解码到320×180做帧差/逐镜候选；实际看60张整秒图及12个低运动候选的首中尾36图。','manualMasterEvidence':'实际看5组全事件联系表，双眼823/828/830/839原尺寸图；以同SHA视频和冻结captured evidence锚定。','reference':'本轮实际复看V20overview与native13–15尾段180帧联系表；加上此前native1、7观察。不宣称通看全920帧。','motionMetricLimits':'阈值MAD<0.5只定位保持候选；例如S032实际有动作末段、档案屏有意停顿，不按该指标自动判失败。','audio':'根报告2,880,000采样/零偏移相关0.99914，未实际听音。','fullResolutionLimit':'不是全1440张原尺寸人工边缘验收。'},'closedOrNarrowed':closed,'findings':find,'referenceAssessment':{'works':['开掌接力焦点比初稿更集中；档案屏内换→直接全幅保留V20结构。','真实源前景、人物裂条、七叶同源交接和文字空间关系已有实物，强于纯硬切初版。'],'remainingGap':'不是100%复刻V20动作相位与尾部运动接力，也未证明达到全部20参考同等优秀水准；本轮仍需尾部设计整改。','notAProxy':'事件数、效果覆盖秒数、源库大小均不能替代动作/焦点/节奏质量。'},'allowedNext':['准备并独立审R4具体整改spec','按真实暗瞳轨迹或新相位修眼位，改中文副标','尾段真实源取片/动作接力预检后执行','补最终events规范，并制作第四个真实不同1080成片和新独立审核'],'mustNotDo':['把本轮revise伪写pass凑4轮','复用旧片审核签名给L4','只加通用闪白/缩放代替实际角色动作'],'deliveryGateRemaining':['L4及必要后续实际成片P1清零','OCC/HF工程实开/媒体链接/可重渲染验收','最终音乐跨接听感尚无实际试听证据，应如实说明或补试听']}
(L/'review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md='''# L3独立审核：实际有改善，继续修订

本次审核绑定实际1920×1080、24fps、1440帧、60秒视频，SHA `'''+r['actualArtifact']['sha256']+'''`。技术通过，艺术结论为 **revise**，允许R4整改，未批准最终交付。

本轮真正闭合了裂条黑空、七叶末端归位、英文STRIKE可读、换源元数据、事件版本状态以及LIMITLESS遮合掌问题。它们均以新实际像素或正式计划核对，不用设计参数代替实物。

## R4必须修的3项

1. 双眼的后半段仍失配。原尺寸F823/F828/F830/F839估读暗蓝瞳y约520/510/460/305，红瞳约525–535。初始对位有改善，但后段差到约230像素。须跟随实际瞳位或换源相位；恒加65会把初段改坏。
2. STRIKE英文完整了，但中文被青掌盖成碎笔。副标移到真实空区或明确省略，不能保留残字。
3. 53.4–56.7秒尾段为紫眼保持→侧脸→蓝眼，连续3.25秒近景凝视，动作能量没有释放。我实际复看V20尾段逐帧图，参考此处仍有射网、跃起、回身动作。因此要设计真实动作接力或短促眼神→动作释放，不能仅修文字/眼位就宣布达到优秀参考水平。

旧events历史意图通过版本状态图已消歧；最终工程仍需规范实际ID/binding/range，保留历史文件。

审核员独立解码实际整片1440张320×180缩略图；人工看60张整秒图、12个候选各首中尾36图、5组全事件联系表和4张眼部原尺寸。帧差阈值只用于定位，不能把所有保持帧都判错；档案屏与预备停顿有叙事用途。未实际听音，也未对全1440张原尺寸逐张人工检查。

完整证据SHA、闭项与待修项见 `review.json`。第四轮仍需真实新视频与独立审核；若P1仍未清零，就继续返修，不能因轮数够而放宽。
'''
(L/'review.md').write_text(md,encoding='utf-8')
print('L3 review written: revise; 3 P1; R4 actual remediation allowed; '+str(len(bound))+' bound artifacts')
