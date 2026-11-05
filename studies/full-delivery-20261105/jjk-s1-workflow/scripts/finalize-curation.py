from pathlib import Path
import json,csv
R=Path(__file__).resolve().parents[1];D=R/'data'
f=D/'shot-candidates.json';j=json.loads(f.read_text(encoding='utf-8'));by={x['id']:x for x in j['items']}
by['S1C003']['visibleActionOrPose']='张掌靠近镜头'
by['S1C016']['visibleActionOrPose']='白蛇与鵺雷光展翼'
by['S1C038']['characters']=['三轮'];by['S1C038']['visibleActionOrPose']='三轮腾空跨步（动态预检纠正静帧初判真希）'
notes={
3:([0,.65],'张掌向镜头展开/画面右侧能量增亮','末段切到能量球，取掌段'),4:([0,.7],'横臂基本稳定，手部向侧面微动','末段原切到咒灵全身'),5:([0,1.3],'头部向上/口部动作','无明显切镜（4点抽检）'),8:([0,1.3],'近乎静止站姿','适合抠像/构图，非高速动作'),9:([0,1.3],'双肘向外/轻微抬头','轮廓清楚'),10:([0,1.3],'两人横向近身交击','动作复杂，逐源帧定相位'),11:([0,1.3],'脸部抬起/画幅趋正','适合表情接镜'),12:([0,1.3],'伏黑右拳前伸，主体朝屏幕左侧','近乎动画hold，需相位检查'),13:([.4,1.3],'伏黑朝右上侧翻/宿傩手臂伸直','开头是另一景别，跳过'),14:([0,1.3],'红眼微动/脸基本稳定','适合眼形匹配'),16:([0,1.3],'白蛇抬首/鸟翼上升再下落','人物标签仅式神；非单独鵺全景'),17:([0,.5],'伏黑向镜头低头前冲','后段切远景，保留近景段'),19:([0,.7],'宿傩肩臂基本稳定','末段原切到飞鸟'),20:([0,1.3],'手指向画面左侧张开','持续青光，适合手势接镜'),21:([0,1.3],'手部沿右侧上移/伏黑脸逐渐露出','强光边难抠，窗口更可靠'),22:([0,.7],'伏黑眼部基本稳定','末段原切到宿傩眼部'),24:([0,1.3],'双掌向左右外展后回落','适合开合动作'),26:([0,1.3],'双手合在下巴前/基本静止','适合手形接镜'),27:([0,1.3],'双指转为单指/镜头略推近','动作完整，适合手势匹配'),29:([.4,1.3],'五条微侧脸/眼罩轮廓稳定','前0.4秒含远景切换，跳过'),30:([.35,.65],'指尖向右射光束','后切漏瑚远景；短局部高能峰值'),31:([0,1.3],'从抬头回到正面','较静，适合版式窗口'),32:([0,1.3],'手指额侧/嘴部小动作','较静，适合标签排版'),33:([0,.5],'手掌面向镜头张开','后原切到漏瑚，不能全1.5s使用'),34:([0,1.3],'长杆斜向上转起','同镜连续旋杆'),37:([0,1.0],'长杆由左上扫至右下前景','运动遮挡强，不宜整人alpha'),38:([0,1.0],'三轮身体由左向右跃起/腿靠近镜头','已纠正人物；后景真希不可混淆'),39:([0,.7],'真希从前景刀后侧视','后段切新角度'),42:([0,.7],'真希双杆由头顶下落分开','后段原切三轮脸'),46:([0,1.3],'钉崎微笑/轻微抬眼','表情稳定，适合透明半身'),48:([.4,1.3],'钉崎锤臂由右向左挥出','前段手部特写原切到背面'),49:([0,1.3],'钉崎正面口部动作','脸部稳定'),50:([0,1.3],'红黑爆发向四周扩散/虎杖拳向花御','源片自带黑闪，不能称新增CG'),51:([0,1.3],'虎杖脸保持/气泡向上','适合冷暖回忆窗口'),52:([0,.7],'蓝光手部张合','末段切虎杖中景'),53:([0,.5],'虎杖双拳在胸前保持','后切脸部近景'),56:([0,1.3],'虎杖空中旋身/脚从侧面收回','动作位移大，抠像难度高'),57:([.35,.65],'虎杖回身看后方','原切密集，仅短核心候选'),58:([.4,1.3],'虎杖与东堂朝画面右侧奔跑','最前段花御画面为原切'),61:([0,.5],'前景脚掌朝镜头/鞋底扩大','后原切对手，适合遮挡匹配'),63:([0,.7],'虎杖拳从胸前向上抬起','后原切双人中景'),64:([0,1.3],'东堂双手准备合掌/微下蹲','动作基本稳定'),65:([0,1.3],'五条双手合在胸前/侧脸稳定','天空背景，抠像首选'),67:([0,1.3],'合掌逐渐转为双手交扣','明确手势变化'),71:([0,1.3],'手指展开到胸前合手','黑白空间，适合原生术式高潮'),72:([0,1.3],'蓝色球体水平变形/五条结印','源自带VFX'),73:([0,1.0],'虎杖拳抬到额头前再降低','最后可能切背部角度'),75:([0,1.3],'五条抬眼/手指向镜头张开','末部手掌可作遮挡入场'),79:([0,1.3],'伏黑身体由下向上跃起/转身','深色洞窟，应保留明亮边缘'),82:([0,1.3],'眼睛画幅逐渐拉远到双眼','适合眼部形状连续变换'),84:([.8,1.3],'钉崎手臂前伸/钉子靠近镜头','前段手部特写与后面大构图有原切'),85:([.4,1.3],'钉崎手指弯曲/青光钉子转入手腕','开头蓝光局部切到双手'),86:([0,1.3],'钉崎抬手和头部倾斜','脸与手臂同画面稳定'),87:([.4,1.3],'钉崎手臂由右上朝前下挥出','开头为另一远景，跳过'),92:([0,1.3],'钉崎竖指后屈指向前','适合五条指势匹配'),93:([0,.5],'红黑能量从钉崎周围向外扩散','后切脸部，不用于无切长镜'),94:([0,1.3],'钉崎侧脸微笑/嘴部动作','稳态表情段'),97:([0,1.3],'虎杖朝镜头奔跑/左右臂交替','相位可配真希前冲')}
idx=json.loads((D/'motion-preflight-index.json').read_text(encoding='utf-8'));out=[]
for item in idx['items']:
    n=int(item['candidateId'][3:]);win,move,note=notes[n];c=by[item['candidateId']];item.update(humanReviewed=True,reviewLevel='每段4个时间点+实际短片存在性；未做全分辨率每源帧人工检验',observedMovement=move,observedLimit=note,recommendedCoreSearchSeconds=[round(item['sourceStartSeconds']+win[0],3),round(item['sourceStartSeconds']+win[1],3)],sourceCutExactBoundaryVerified=False)
    c.update(motionDirection=move,motionVerified='four_point_temporal_preflight',motionEvidence=item['contactSheet'],recommendedCoreSearchSeconds=item['recommendedCoreSearchSeconds'],motionCaveat=note)
    out.append({**c,'reviewMovie':item['reviewMovie'],'reviewContactSheet':item['contactSheet'],'reviewRow':item['row']})
idx['humanReviewedAllContactSheets']=True;idx['note']='推荐核心是4点图估计的保守搜索区间，非最终精确切边；执行前应在源native PTS帧上确认原切、运动相位及可用余量。'
(D/'motion-preflight-index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2),encoding='utf-8')
j['corrections']=['S1C003由挥拳改为张掌，源短序列可见','S1C016显示白蛇与鵺，不是单独鵺','S1C038跃起者为三轮，纠正静帧初判真希'];j['motionPreflightCount']=len(out)
f.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
with (D/'shot-candidates.csv').open('w',encoding='utf-8-sig',newline='') as csvfile:
    columns=['id','episode','anchorSeconds','characters','visibleActionOrPose','shotSize','dominantPalette','cutoutFeasibility','motionDirection','semanticConfidence','anchorJpg'];writer=csv.DictWriter(csvfile,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows([{**v,'characters':'/'.join(v['characters'])} for v in j['items']])
nav=json.loads((D/'action-navigation-index.json').read_text(encoding='utf-8'))
for x in nav['items']:x['viewed']=True
nav['humanViewScope']='13张联系表共312个5秒间隔静帧全部查看；不是其间连续帧验收'
(D/'action-navigation-index.json').write_text(json.dumps(nav,ensure_ascii=False,indent=2),encoding='utf-8')
(D/'retrieval-candidates.json').write_text(json.dumps({'scope':'58个已查看4时间点的1.5秒预检短片和核心搜索区间，供执行agent回源取材；非最终镜头审批','count':len(out),'sampleImagesPerClip':4,'nativePtsExactCutAuditRequired':True,'items':out},ensure_ascii=False,indent=2),encoding='utf-8')
oi=json.loads((D/'source-overview-index.json').read_text(encoding='utf-8'))
actors=[['虎杖','伏黑'],['虎杖','伏黑','五条'],['虎杖','伏黑','钉崎'],['虎杖','伏黑','宿傩'],['宿傩','伏黑','五条'],['虎杖','宿傩','五条'],['五条','漏瑚','虎杖'],['钉崎','真依','伏黑','东堂'],['虎杖','七海','顺平','真人'],['顺平','真人','七海'],['真人','顺平','七海'],['虎杖','顺平','真人'],['真人','七海','虎杖','五条'],['虎杖','伏黑','钉崎','真希'],['虎杖','东堂'],['东堂','机械丸','熊猫','三轮'],['真希','三轮','钉崎','真依'],['加茂','伏黑','花御'],['伏黑','虎杖','东堂','花御'],['虎杖','东堂','五条'],['伏黑','东堂','真希'],['虎杖','伏黑','钉崎'],['伏黑','钉崎'],['虎杖','钉崎','坏相','血涂']]
for i,x in enumerate(oi['items']):x.update(humanViewed=True,semanticLabels=[{'field':'visibleCharactersAcrossSamples','values':actors[i],'confidence':'qualitative human attribution from shown sparse overview','scope':'只代表8张抽样里出现的角色，不代表整集所有角色'}])
(D/'source-overview-index.json').write_text(json.dumps(oi,ensure_ascii=False,indent=2),encoding='utf-8')
inv=json.loads((D/'source-inventory.json').read_text(encoding='utf-8'))
inv['seasonIdentity']={'observed':'S1 E01–24内容线索：虎杖入学、五条眼罩对漏瑚、交流会花御、八十八桥钉崎/虎杖战；与4K目录此前S2怀玉/玉折素材不同','evidence':['evidence/source-overviews/S1E01-overview.jpg','evidence/source-overviews/S1E07-overview.jpg','evidence/source-overviews/S1E19-overview.jpg','evidence/source-overviews/S1E24-overview.jpg'],'humanReviewed':'24张联系表共192张稀疏帧全部看过；非全季逐帧人工理解'}
(D/'source-inventory.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'evidence/source-overviews/素材理解与取回说明.md').write_text('''# 第一季素材理解与取回说明

本次素材为1080P目录01–24，视频累计34350.02404秒、24000/1001fps。02(1)/05(1)与正本完整SHA相同，不重复索引，未删除任何原片。

已实际生成并查看24集各8张稀疏总览、13组各24张五秒动作导航。形成97个静帧候选，再对其中58条取回1.5秒低分辨率审片短片，逐条查看0/0.4/0.8/1.2秒四帧图。JPG总览和这些审片短片不是60fps全季素材集，后者由独立流水线负责。

`data/retrieval-candidates.json`为执行入口，`recommendedCoreSearchSeconds`给保守核心搜索区间，`sourcePath`仍指向第一季原片。执行须回源读PTS、精确选帧；审片MP4仅640×360，不应拿它作为最终1920成片素材。

发现的静帧误判已明确纠正：S1C003实际张掌而非挥拳，S1C016同画面有白蛇与鵺，S1C038跃起人物是三轮而非真希。多段原片自带切镜，已经在预检注释标出，不能直接把1.5秒区间整体做成一个动态透明层。

可优先设计三组形状链：S1C003宿傩掌→S1C033五条掌；S1C026伏黑手→S1C067五条合掌→S1C085钉崎手；S1C014宿傩红眼→S1C082伏黑双眼→S1C075五条蓝眼。动作链可尝试S1C037真希挥杆→S1C048钉崎挥锤；需再次按屏幕方向、接触点和动作相位对齐，不是仅凭同名手法拼接。

源动画自带黑闪、赫、苍、紫、血线等VFX不算本次新制作；新增效果应分别记录。抠像可行性是构图预判，high也不代表已有可用alpha。
''',encoding='utf-8')
print('annotated',len(out),'motion-preflight candidates; 97 static anchors; 24 sparse overviews')
