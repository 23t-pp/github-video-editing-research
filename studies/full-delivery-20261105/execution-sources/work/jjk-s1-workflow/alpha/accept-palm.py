from pathlib import Path
import json
R=Path(__file__).resolve().parents[3]/'outputs/jjk-s1-workflow';EV=R/'evidence/alpha';p=EV/'XPALM-alpha-report.json';j=json.loads(p.read_text(encoding='utf-8'))
j.update(visuallyReviewed=True,reviewer='/root/s1_source_curator',reviewScope='最终26帧全部棋盘/红底联系表查看；全分辨率红底F2/F27及源F2/F27复查，不冒称26帧全分辨率逐张人工检查',method='1920 prepared-source manual contour;17x17 narrow-support GrabCut;0.65px feather; largest connected hand/forearm; RGB untouched',revision='R2_full_resolution_contour_fixed',remainingDifferences='手姿多数hold；删除大面积原青焰，仅留人物及窄青/黑墨边。个别指缘/袖缘仍有3–12px原深蓝墨影/光污染与手绘近似，右腕和袖底受原画幅裁切。',pipelineOrder=['prepare-palm.py','build-palm.py','verify-palm.py','actual checker/red view','accept-palm.py'],initialFailure='R1低清轮廓误裁弯指顶部；全分辨率审核拒绝后按1920原片重画并重分割，示例XPALM-r1-rejected-foldfinger.png',finalAcceptanceScope='素材可供L2合成；最终构图边缘和过渡由独立成片审核agent验收')
p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
(EV/'XPALM-使用说明.md').write_text('''# 第一季青掌XPALM

正式prepared素材：`hyperframes/assets/shots/XPALM.mp4`，31帧/24fps；RGBA：`hyperframes/assets/alpha/XPALM/000002.png`至`000027.png`，F2–27共26帧。编号与prepared视频同号，不从0重排。全局事件offset2即可顺序引用26帧。

源仅第一季E05，seek554.6秒，首个实际解码源PTS554.6374167秒。几何crop1920:960:0:0后padTop60；源底120行丢弃，无缩放/AI重绘。

26张RGBA逐张RGB核对同号prepared解码完全相等，y0–59/y1020–1079 alpha全0；全31帧差异与3个源锚点未见原切。手姿主要动画hold，源青焰有变化，不宣称大幅动态手势。大青焰不进mask，边缘仍有局部深蓝影/青光污染与手绘近似。

已看全部26帧棋盘/红底联系表，并复查F2/F27全分辨率；R1弯指误裁已发现返修，R2弯指完整。右侧袖/腕到画幅外；不要将直切端缩到空白中心，应出画或压在字板/画框下。素材交付不等于L2最终合成通过，需独立审核agent继续验收。
''',encoding='utf-8')
print('XPALM R2 material ready for L2')
