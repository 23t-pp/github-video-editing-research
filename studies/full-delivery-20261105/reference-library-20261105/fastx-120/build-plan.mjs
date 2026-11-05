import fs from 'node:fs';
import path from 'node:path';

const base=path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/,'$1'));
const scout=JSON.parse(fs.readFileSync(path.join(base,'evidence/scout-index.json'),'utf8').replace(/^\uFEFF/,''));
const music=JSON.parse(fs.readFileSync(path.join(base,'music-design.json'),'utf8').replace(/^\uFEFF/,''));
const sourceId='FASTX10';
const sourceFilename='11 速度与激情10（2023）4K.mp4';
const bpm=128,spb=60/bpm,fps=24;
const tc=t=>{const ms=Math.round(t*1000),h=Math.floor(ms/3600000),m=Math.floor(ms/60000)%60,s=Math.floor(ms/1000)%60;return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}.${String(ms%1000).padStart(3,'0')}`;};
const ftc=f=>`${String(Math.floor(f/86400)).padStart(2,'0')}:${String(Math.floor(f/1440)%60).padStart(2,'0')}:${String(Math.floor(f/24)%60).padStart(2,'0')}:${String(f%24).padStart(2,'0')}`;
const content={
 1650:['窗边人物','人物近景，男子在窗边向外看；没有动作长度证据','人物/关系','窗框竖线、视线'],
 1710:['踏板与脚','脚和打孔金属踏板近景；是否踩下/释放要回看','驾驶细节','脚/踏板接触点'],
 1770:['手持监看屏','双手握持屏幕设备，屏上有多路街景；已有中英硬字幕','情报/装置','矩形屏幕、双手'],
 1830:['驾驶座人物','女性在驾驶座握方向盘看向旁侧，旁边另有人','驾驶反应','眼线、方向盘'],
 1890:['刮擦火星','道路旁硬质物体近景伴随火星；物体身份、运动方向与接触前后待复查','危险细节','亮火星/道路边缘'],
 1950:['换挡手部','手握挡杆，邻近中控；换挡阶段与连续性待复查','驾驶细节','手、挡杆轴线'],
 2010:['骑行人物侧脸','戴墨镜长发男子侧面，背景有横向模糊；具体动作与屏幕移动待复查','对手/动作','侧脸、水平主线'],
 2070:['车辆斜近景','车辆引擎盖/开放座舱斜角近景，上方可见人手与橙黄区域','车辆细节','车身斜线/开口'],
 2130:['仪表盘','仪表表盘近景，前景有遮挡；指针运动待复查','驾驶细节','圆形表盘/指针'],
 2190:['车厢反应','公交式车厢内多人失衡/扶座的瞬间，方向与前因待复查','危险反应','座椅/黄色竖杆'],
 2250:['街口双车','街口两车斜向构图，建筑与路面可读；行驶方向、转弯相位待复查','地理/追逐','车头朝向/道路'],
 2310:['摩托低角度','摩托车与骑行者下半身近景，背景是矮墙和天空','车辆动作','车轮/车身斜线'],
 3630:['夜间对手面部','紫衣男子面向前方，后方有围观人群；已有中英硬字幕','人物/威胁','面部居中/夜色'],
 3690:['夜间双人对位','前景光头后脑与紫衣男子面对面；已有中英硬字幕','人物关系','正反打眼线'],
 3750:['枪旁对峙','紫衣人物旁有一把横向手枪，后方有人群；没有开枪动作证据','人物/威胁','横向枪线/反应'],
 3810:['两车内人物对位','相邻车窗中两位男子对位，前景人物较虚；已有中英硬字幕','人物关系','窗框/眼线'],
 3870:['夜间车灯起势','数车前脸和车灯，人群及近处人物腿部；是否起跑待复查','建立/车辆','平行车灯/正面'],
 3930:['方向盘红色控件','方向盘附近红色圆形控件与前景手；是否按下待复查','驾驶细节','红圆/手指'],
 6960:['高速路车队','两辆并排SUV与后方车辆正面构图；前后车距/追逐关系待复查','地理/威胁','并行车头/道路'],
 7000:['驾驶者强反应','光头驾驶者握方向盘张口的近景；台词与动作时长未听辨','人物反应','眼睛/方向盘'],
 7040:['并行直升机','低空直升机侧面及另一架在后，门内有人可见','威胁/空间','机身横向/旋翼'],
 7080:['直升机与缆线','两架直升机、向下连接的缆线及近处车顶；载具动态待复查','危险/空间','V形缆线/上下关系'],
 7120:['另一驾驶者','长发男子在车内握方向盘，背景有车；已有中英硬字幕','对手/驾驶','双手/正面脸'],
 7160:['车内保护人物','成人俯身护住孩子的车内近景，背景暖橙色','情绪/行动理由','弯曲护抱轮廓'],
 7200:['跑道远景','空旷长直跑道和远处载具/物体，山脉在后；具体动作和结果未知','地理/释放','消失点/大留白'],
 7240:['弯道大货车','大货车在弯道路段，护栏和山体清晰','威胁/车辆','弯道/车头'],
 7280:['驾驶者专注面部','光头男子车内近景，视线向侧前方；已有短硬字幕','人物/决心','眼线/脸部'],
 7320:['烟柱与肩侧器材','男子站在岩壁附近，肩侧有大型武器/器材，旁有烟柱；是否刚发射未知','危险/反应','竖人物/烟柱'],
 7360:['室内对手近景','白衣长发男子在室内设备旁侧看','人物/情绪','眼线/冷色设备'],
 7400:['对讲机与对手','长发男子持对讲机在岩石环境中，已有中英硬字幕','悬念/威胁','手持物/面部']
};
const candidates=scout.map(x=>({id:`SRC${x.t}`,center_seconds:x.t,center_timecode:tc(x.t),evidence:`evidence/${x.file}`,label:content[x.t][0],observed_single_frame:content[x.t][1],category:content[x.t][2],visual_anchor:content[x.t][3],
 verification:'仅人工看过中心单帧；连续动作、源入出点、可用时长、方向、音轨均未验证',source_in:null,source_out:null,
 review_window:{start_seconds:x.t-4,end_seconds:x.t+4,purpose:'建议首次回看的邻域，不是已确认可用片段；越过邻镜时必须缩短'}}));
const byTime=new Map(candidates.map(x=>[x.center_seconds,x]));
const sections=[
 {id:'A',name:'冷开：危险先到',start:0,end:7.5,beats:16,pattern:[2,2,4,8],intent:'未来危险碎片先抓住视线，再落到人物/车辆建立。不是按电影时间顺序重述。'},
 {id:'B',name:'人物与威胁建立',start:7.5,end:22.5,beats:32,pattern:[8,4,4,8,4,4],intent:'主角、对手、两人对位、装置/控件；建立谁在应对谁。'},
 {id:'C',name:'第一轮街道追逐',start:22.5,end:52.5,beats:64,pattern:[...Array(14).fill(4),8],intent:'控制细节→街道地理→对手/驾驶者→危险反应，最后一镜拉长。'},
 {id:'D',name:'呼吸与行动理由',start:52.5,end:67.5,beats:32,pattern:[8,8,8,8],intent:'用保护人物与面部停留给后续高速段一个理由，不加花式转场。'},
 {id:'E',name:'高速主高潮',start:67.5,end:112.5,beats:96,pattern:[...Array(8).fill(4),...Array(16).fill(1),...Array(8).fill(2),...Array(8).fill(4)],intent:'空间升级15秒→细节密集7.5秒→反应加速7.5秒→恢复可读的大动作15秒。'},
 {id:'F',name:'最后回应与悬念',start:112.5,end:120,beats:16,pattern:[2,2,4,8],intent:'短冲击→主角反应→对手悬念→自己的标题，不虚构追逐胜负。'}
];
// 每条仅分配候选中心与意图，不在这里生成未经核验的源入出点。
const spec={
 A:[
 [7000,'先给驾驶者强反应','脸/方向盘近景；入点找动作前半拍，不从最高峰截起','硬切','一次短促原片反应/车厢声，待听辨'],
 [1890,'亮火星切入危险','只取刮擦接触的一次短峰值，不能称已确认撞车','亮点硬切','一次刮擦声，不能重复叠在每帧'],
 [7080,'威胁有空间关系','两架直升机和缆线宽景，保留上下结构','硬切','旋翼/风声层，待找可用声'],
 [3870,'回到准备：车灯与人群','较长车前建立镜，允许读清车辆方位；本镜是否起跑须复查','直接切换段落','音乐导轨进入建立段，低车怠速']
 ],
 B:[
 [7280,'主角专注','人物近景停留，视线指向后续对位；不剪成随机吼叫','硬切/极短叠化待实看','可留一个确认过的短字/呼吸，未选台词'],
 [3630,'对手被识别','夜间对手正脸，控制为一个清楚表情','对位硬切','原片环境低留，台词须完整语义'],
 [3750,'危险具体化','枪旁对峙只当威胁形象，不伪造枪击或命中','眼线硬切','不在无开枪证据时添加枪响'],
 [3810,'两人关系','两车窗内人物对位；保留眼线与前后层次','硬切','可提取一条完整对话短句，须试听核对'],
 [1770,'装置/情报插入','矩形监看屏，读一个清楚画面即可；不虚构屏幕任务信息','矩形形状接镜，可选一次卡片','只给一个轻设备提示，不覆盖硬字幕'],
 [3930,'准备动作落点','红圆控件与手；确认是否按下后选动作相位','圆形/手势匹配','确认真实动作后用点击/机械声']
 ],
 C:[
 [1710,'脚部准备','脚接近/压踏板的一个完整相位；当前只有中心帧','动作硬切','短踏板/机械声'],
 [1950,'手部决定','换挡一个动作，不从同段反复倒放','动作硬切','一次换挡声'],
 [2250,'街道地理','两车与街口宽景，先确认屏幕运动方向','宽景硬切','道路/轮胎底声'],
 [1830,'驾驶者回应','方向盘与人物视线；对齐上一镜运动方向','反应硬切','车内声保留少量'],
 [2010,'对手动作线','侧脸/骑行者一镜，方向必须回看确认','同向硬切','风声短起'],
 [2310,'摩托细节兑现','车轮/车身低角度；接同一方向，不镜像商标/人物','细节硬切','轮胎/引擎声'],
 [2070,'靠近车身','斜角车辆细节带动尺度变化，不随意旋转全画面','动作相位硬切','引擎声短抬'],
 [2130,'仪表紧张','圆表盘作为视觉锚点，指针是否跳动待回看','形状匹配，可选一次短圆窗','机械/引擎声；不造虚假速度读数'],
 [1890,'火星第一次主冲击','找与冷开不同的非重叠时段；不足时取消再演同一碰撞','动作硬切，源光已足就不闪白','一次刮擦峰值，音乐短让位'],
 [2190,'危险反应被看见','车厢反应镜，必须确认与前镜方向/动作可读；不伪称原剧情因果','反应硬切','原片车厢撞动/惊呼须试听'],
 [2250,'回宽景重建方向','选不同连续瞬间或更宽构图，不重复完全相同动作','重新建立宽景','道路底声衔接'],
 [1830,'驾驶者第二次判断','换另一动作瞬间或短反应，不能简单复制已用片段','眼线硬切','少量呼吸/车内声'],
 [2010,'对手逼近的印象','只有找到不同可用动作才再用；本候选不证明逼近速度','动作硬切','风声/引擎片段'],
 [1890,'冲击后的细节','优先非重叠的接触后瞬间；没有则宽景跨拍保持','细节硬切或保持上一镜','让冲击声尾自然衰减'],
 [2250,'拉长一镜释放','尝试连续街道宽景；必须找到至少本槽时长加余量的同镜','长镜停留','音乐层次略减，保留道路感']
 ],
 D:[
 [7160,'观众看见要保护的人','较长车内保护画面，完整读出护抱姿态；不加大字遮脸','直接硬切/轻叠化待复核','音乐降层，原声呼吸/衣料可短留'],
 [1650,'人有停顿','窗边人物视线镜；仅作情绪联想，不宣称与前镜同一现场','视线硬切','低环境，不硬凑台词'],
 [7280,'主角重新判断','找未用的专注表情；缓慢源镜优先，不强加数字推镜','硬切','对白如要留须完整语义并duck音乐'],
 [7360,'对手冷静对照','室内对手近景作为情绪反差；不是已证明此人正在监视前段','对照硬切','低环境；导轨准备进入高潮']
 ],
 E:[],
 F:[
 [1890,'最后一次亮点冲击','只能找新的源瞬间或不同细节；不把同次碰撞演三遍','直接硬切','一个短冲击，若无新原声则使用已授权独立SFX'],
 [7000,'主角反应收束','找不同反应相位，动作读清再离开','反应硬切','让声尾接到下镜，不再多叠hit'],
 [7400,'悬念留给对手','对讲机近景；如保留对白只用原片确实完整的一句，当前未选','硬切','短完整对白候选，待试听，音乐退后'],
 [7200,'余韵与自己的片名','可用跑道宽景作底后淡黑；没有足够连续素材就直接黑底标题','淡暗到黑底标题','导轨最终小节收束；不硬循环接回开头']
 ]
};
spec.E.push(
 [6960,'高潮先交代车队','宽景读清前后车距和道路；动作关系须复查','宽景硬切','道路/引擎层'],
 [7000,'主角应对','确认后的握方向盘/反应相位','反应硬切','车内短声'],
 [7040,'威胁升到空中','侧面直升机，先让观众辨认','硬切','旋翼声适量'],
 [7120,'对手驾驶','另一车内正面，形成主/对手轮换','对位硬切','引擎不同音色候选'],
 [7080,'空间危险升级','缆线和车顶关系作为主信息，别裁掉连接点','硬切','风/缆线/机声分层'],
 [7240,'增加另一体量威胁','大货车与弯道宽景；不靠单帧编造拦截结果','宽景硬切','低频引擎与轮胎'],
 [7200,'地理与速度尺度','跑道远景释放视觉；不称已逃脱','硬切','环境气流'],
 [3930,'准备进入细节密集段','确认红控件动作，作为一拍段入口','圆形或手势硬切','一次机械触发候选']
);
const flurry=[
 [1710,'脚与踏板接触','与下一槽取同镜不同瞬间/互补裁切，不倒放'],
 [1710,'打孔踏板细节','可让同一源镜连续播放，仅换裁切；若分辨率不足保留原构图'],
 [1950,'握挡杆的手','手部相位与上一脚动作相接只是剪辑设计，源关系待核实'],
 [1950,'挡杆轴线/中控','同镜另一空间细节或连续瞬间，禁止重复同一次换挡'],
 [2130,'仪表圆心','确认仪表读数，不能人为指针乱跳'],
 [2130,'仪表边缘与前景','互补裁切/同镜延续，不再播放相同镜头起点'],
 [3930,'红控件近景','只在源片确有动作时切接触'],
 [3930,'手指与控件关系','与前槽连续的源时间；没有动作就跨两个槽保持'],
 [7000,'驾驶者眼神','可从面部近景取不同瞬间，勿裁切到严重软糊'],
 [7000,'方向盘手部','同镜下方细节，眼线与手的来源/时间需一致'],
 [7040,'直升机机身/旋翼区','源尺寸允许才裁；不从静帧假造旋翼加速'],
 [7040,'门内/侧窗人物','同镜互补细节，不能把同一次晃动循环'],
 [7080,'缆线连接关系','保持线条与车顶可读，不裁成无意义天空'],
 [7080,'车辆/线条下端','同镜时间连续或不同未用瞬间，回看确认真实位置'],
 [1890,'火星亮区','一拍短峰值；优先用尚未使用的源瞬间'],
 [1890,'刮擦边缘/道路','若源素材不足，连续保持并用构图变化，不重播整次冲击']
];
for(const [t,label,note] of flurry)spec.E.push([t,label,note,'一拍细节硬切/连续裁切','大多数不加独立hit；只给整个16拍组保留少数重点']);
spec.E.push(
 [7000,'主角反应回中景','从细节回到可识别面部，不再裁眼睛','反应硬切','还给观众真实车内声'],
 [7120,'对手反应','另一未用表情/转向瞬间','对位硬切','引擎/短呼吸'],
 [7160,'保护人物再提醒一次','不同源瞬间；若不能找到，保持上一主角镜跨拍','情绪硬切','音乐短让位，勿插虚构尖叫'],
 [6960,'回到车队位置','宽镜确认危险仍在，车距变化需实看','宽景硬切','道路底层'],
 [7040,'空中威胁还在','选择未用相位，不复制整段旋翼动作','硬切','旋翼声不过量'],
 [7080,'缆线/车顶再次成为问题','不同连续瞬间，保持上下关系','动作硬切','张力音效仅作设计'],
 [7240,'弯道车辆接近','确认车头运动方向后接入；不得用镜像强改身份','动作硬切','车辆体量音色'],
 [7200,'短宽景重建空间','留一个消失点，下一段回较长动作','硬切','环境声过桥'],
 [7280,'决定被读清','较长专注面部，预留下一动作入点','硬切','短呼吸/完整短字如有'],
 [1950,'控制动作兑现','找新的换挡/控制动作完整相位','动作硬切','一次机械声'],
 [1710,'脚的动作回应','与手动作相位衔接；并非已证实来自同一实际操作','动作硬切','低踏板声'],
 [7240,'长一点的大车辆动作','完整车头/弯道信息，别把大动作切断','硬切','引擎持续'],
 [6960,'车队大画面','未用连续范围或更宽构图','宽景硬切','道路持续'],
 [7080,'高潮主空间画面','缆线/车辆一并保留，不能只剩直升机','硬切','风/旋翼与音乐错开峰值'],
 [7320,'新的危险形象','人、肩侧器材、烟柱；先查实际动作，不凭静帧添加发射/命中','硬切','没有发射证据不加导弹发射声'],
 [7000,'高潮反应落点','同角色未用反应；让动作/眼神结束再进入尾段','反应硬切','保留一次主峰，随后释放']
);

const shots=[];let beat=0,frame=0;
for(const section of sections){
 const list=spec[section.id];
 if(list.length!==section.pattern.length)throw new Error(`${section.id} slots ${list.length} != ${section.pattern.length}`);
 section.first_slot=shots.length+1;
 section.beat_start=beat;
 for(let i=0;i<list.length;i++){
  const [t,role,detail,transition,sound]=list[i],len=section.pattern[i],c=byTime.get(t);
  if(!c)throw new Error(`missing center ${t}`);
  const startIdeal=beat*spb,endIdeal=(beat+len)*spb,startFrame=Math.round(startIdeal*fps),endFrame=Math.round(endIdeal*fps);
  if(startFrame!==frame)throw new Error('timeline gap');
  const quick=section.id==='E'&&i>=8&&i<24;
  shots.push({id:`S${String(shots.length+1).padStart(2,'0')}`,section:section.id,section_name:section.name,
   beat_start_zero_based:beat,beat_end_exclusive:beat+len,beat_length:len,
   start_frame:startFrame,end_frame_exclusive:endFrame,duration_frames:endFrame-startFrame,
   timeline_start_timecode:ftc(startFrame),timeline_end_timecode_exclusive:ftc(endFrame),
   start_seconds:startFrame/fps,end_seconds:endFrame/fps,duration_seconds:(endFrame-startFrame)/fps,
   ideal_start_seconds:startIdeal,ideal_end_seconds:endIdeal,
   start_quantization_error_ms:+((startFrame/fps-startIdeal)*1000).toFixed(6),end_quantization_error_ms:+((endFrame/fps-endIdeal)*1000).toFixed(6),
   candidate_id:c.id,sourceId,sourceFilename,source_center_seconds:t,source_center_timecode:c.center_timecode,
   source_evidence:c.evidence,source_observed:c.observed_single_frame,
   source_in_seconds:null,source_out_seconds:null,source_in_frame:null,source_out_frame:null,
   suggested_review_window:c.review_window,source_trim_status:'需复查起止/源动作/可用时长；未锁定片段',
   intended_role:role,edit_intent:detail,transition_plan:transition,
   motion_direction:'待动态复查；单帧不证明运动方向。先按车头/手势/视线选择同向入出点，反向时加宽景重建。',
   detail_flurry:quick,reuse_policy:quick?'优先同一原镜连续时间的不同细节/互补裁切；不同槽不重播同一完整动作':'重复候选必须复查并取未用非重叠范围；或改变构图但源时间连续，不能无脑循环',
   source_speed:1,speed_status:'默认原时间；未设计/未验证曲线变速，不为凑槽强拉速度',
   sound_plan:sound,sound_status:'设计建议，尚未听辨选定原片声段',
   text_plan:section.id==='F'&&i===3?'自己的短片名/署名；可黑底实现':'默认不加中央大字；原片已有硬字幕需在最终取景时检查',
   fallback_if_unusable:'改选相近职责的候选或补找同场源镜；可让前一镜连续跨过本槽节拍标记，不能以静帧/重复动作假装新镜头',
   checks:['连续源镜足够长且含首尾余量','人物/车辆方向和动作相位已看动态','与相邻镜不存在同段动作重复','HDR转SDR样片检查通过','硬字幕/视线/车轮等重要区域未被遮挡']
  });
  beat+=len;frame=endFrame;
 }
 section.last_slot=shots.length;section.beat_end_exclusive=beat;section.start_frame=Math.round(section.start*fps);section.end_frame_exclusive=Math.round(section.end*fps);
}
if(shots.length!==73||beat!==256||frame!==2880)throw new Error(`bad totals ${shots.length}/${beat}/${frame}`);
if(music.bpm!==128||music.beats!==256||music.durationSeconds!==120)throw new Error('music design mismatch');

const plan={
 schema:'fastx-120/edit-plan-v1',title:'速度与选择｜两分钟高燃混剪方案',status:'可编辑剪辑计划；73个镜头槽；不是已剪好视频，也不是OCC原生工程',
 scope:'只人工查看候选中心帧、读取节奏设计与源流元数据；未提取/试听所有源段，未渲染完整电影。',
 narrative:'危险预告→人物和对手→街道追逐→保护人物的理由→高速空间升级→对手悬念收束。属于主题式重组，不宣称保持电影完整时序/单场景因果，也不凭跑道单帧声称已逃脱或获胜。',
 source:{sourceId,sourceFilename,width:3840,height:1600,frame_rate:'24000/1001',fps:24000/1001,pixel_format:'yuv420p10le',color_primaries:'bt2020',color_transfer:'smpte2084',color_matrix:'bt2020nc',metadata_verification:'只读ffprobe实际返回；源入出点另待动态复核'},
 delivery:{duration_seconds:120,fps:24,total_frames:2880,width:1920,height:1080,active_picture:{width:1920,height:800,pad_top:140,pad_bottom:140},color:'SDR Rec.709',pixel_format:'yuv420p',audio_sample_rate:48000,
  frame_policy:'24fps制作序列；镜头切口按累计拍点取最近整数帧。保持23.976源真实时间时由编辑器正常帧采样，不做光流；若另选逐源帧解释为24fps，会0.1%提速，必须同步处理声音并重算入出点。分析证据仍保留源原生帧。'},
 rhythm:{bpm,designed:true,time_signature:'4/4',beats:256,bars:64,seconds_per_beat:spb,guide:'128BPM_120秒_原创节奏导轨.m4a',midi:'128BPM_120秒_可编辑节奏.mid',markers:'beat-markers.csv',guide_status:'原创节奏/结构导轨，不是最终配器混音歌曲',quantization:'Math.round(累计拍×60/128×24)；不逐镜四舍五入后累加',max_cut_rounding_error_ms:Math.max(...shots.flatMap(x=>[Math.abs(x.start_quantization_error_ms),Math.abs(x.end_quantization_error_ms)]))},
 sections,candidates,shots,
 color_workflow:{verified_input:'BT.2020/PQ HDR 10bit，不可只改标签假装SDR',steps:['先检查HDR原片在正确HDR监看/播放器中的亮度与肤色','在浮点/足够精度链中把PQ线性化，做tone mapping，再转换Rec.709','按实际高光和肤色调曝光/高光滚降，保留火星/车灯层次，不把高光全夹成白','先做日景、夜景、强光各2–3秒样片，统一肤色与黑位，再批量做选定短段代理','保留3840×1600比例，缩1920×800后上下各140黑边；不把2.4:1拉伸到16:9','输出标记Rec.709/有限范围，检查没有重复tone map、灰黑、过饱和红与色带'],
  ffmpeg_filter_starting_point:"zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=2,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,scale=1920:800:flags=lanczos,pad=1920:1080:0:140:black",
  filter_status:'本机ffmpeg帮助已核实zscale/tonemap和hable/desat；本滤镜链是起始方案，尚未对电影短段实际渲染或视觉验收；npl/峰值与曝光应按素材和监看校准'},
 audio_plan:{status:'设计层；等待实际选段试听，不假装已有干净对白/独立音效stems',tracks:[{track:'A1',role:'128BPM原创导轨/将来完整配乐',rule:'完整120秒结构，按六段能量分层；当前导轨可用于选镜，不当作最终已混音歌曲'},{track:'A2',role:'原片对白/呼吸/车内原声',rule:'少量完整语义短句，字幕核对；对白出现时音乐局部降约6–10dB可作试验，具体听辨调整'},{track:'A3',role:'车辆/刮擦/旋翼/换挡',rule:'源片常混有配乐；没有干净声段时使用已授权独立SFX，不能宣称EQ或取中置声道就能完美去音乐'},{track:'A4',role:'少量设计冲击/上升与环境',rule:'只服务段落/主落点；16个一拍槽不各叠一次hit，不把没有发射动作的器材静帧配成导弹发射'}],
  dialogue_review:['先核对实际台词、开始/结束呼吸与语义，不按图片硬字幕拼接虚假对白','若源是多声道，先确认布局再试中置候选；中置也可能含配乐，非干净对白保证','轻降噪/EQ/包络只能改善可懂度，不能无损分离重叠音乐','对白与车辆动作声做短J/L-cut可连续，但不能制造未发生的开枪/命中'],
  mix_trial_targets:{integrated_lufs:'-14至-16（本方案试听起点，最终按平台/内容调整）',true_peak_dbtp:'不高于-1',master_status:'未混音/未测量'},
  short_reference_loop_reason:'不能把约10秒参考片段机械循环12次当完整两分钟配乐：乐句、和声/人声、段落落点与尾声不完整，重复动机会失去推进；若按128BPM算10秒只有21又1/3拍，也不是完整4/4乐句的整数循环。即使参考实际BPM不同，也需独立分析并取完整乐句。交叉淡化只能藏接缝，不能补出真正的建立/呼吸/高潮/收尾。'},
 learned_methods:{apply:[{references:['V20动作硬切','R05动作相位匹配'],use:'控制手/脚、方向盘与车辆动作先直接硬切；匹配方向/大小/动作相位'},{references:['V18人物章节'],use:'用角色建立、威胁、反应和行动结果分组，避免全程随机车镜头'},{references:['V16/V17记忆窗'],use:'人物关系段最多一处矩形回忆窗；不用每个转弯都插卡'},{references:['V19同心形状连接'],use:'红控件/仪表/轮毂可试1–2次圆形匹配，普通叠化能成立就不做复杂门户'}],
  avoid:[{method:'整片逐帧人物抠像/手指门户',why:'现有候选不提供动态alpha；精修成本高，也会分散驾驶动作信息'},{method:'每刀RGB故障/白闪/甩镜',why:'源镜已有高速、火星、摄影运动；叠满会让路线和车距不可读'},{method:'参考小窗默认参数直接套73镜头',why:'背景、主体与方向不同；模板不是自动识别动作/空间的系统'},{method:'大量光流慢放或轮毂光流',why:'快旋转、烟雾、遮挡容易变形；默认原速，必要变速单独做短样片'},{method:'同段10秒音乐或同次碰撞硬循环',why:'破坏段落推进和动作因果，不能用数量填充时长'}]},
 subtitle_policy:'当前候选显示原片有烘焙中英字幕，不能承诺可直接关掉；优先另找无字幕版本/源镜无字时段。若只能用当前源，不用大面积上下裁切毁掉2.4:1构图，不假装AI修复已完成；需要清理时逐镜评估。',
 operational_order:['按候选中心±4秒先看动态，登记真实镜头起止，不把该窗口当可用范围','每镜足够长再分配sourceIn/sourceOut与首尾余量，重复候选检查非重叠/连续源时间','先做A/B连接与C一组8–12秒小样，验证方向、HDR→SDR、字幕、音效','确定120秒节奏后补剩余镜头；一拍槽素材不足可让一镜跨节拍标记，不硬凑73次画面变化','准备必要mask/标题，再导入OCC或HF工程；plan.json不是OCC原生工程','选定短段代理或外部合成后才渲染最终120秒，不处理整部电影'],
 validation:{planned_slots:shots.length,total_beats:beat,total_frames:frame,total_seconds:frame/fps,continuous:true,all_source_trims_verified:false,all_evidence_files_exist:candidates.every(c=>fs.existsSync(path.join(base,c.evidence))),rendered:false,full_movie_processed:false}
};
fs.writeFileSync(path.join(base,'plan.json'),JSON.stringify(plan,null,2),'utf8');
const cols=['id','section','section_name','beat_start_zero_based','beat_length','start_frame','end_frame_exclusive','duration_frames','timeline_start_timecode','timeline_end_timecode_exclusive','ideal_start_seconds','ideal_end_seconds','start_seconds','end_seconds','sourceId','sourceFilename','candidate_id','source_center_timecode','source_center_seconds','source_in_seconds','source_out_seconds','source_evidence','intended_role','edit_intent','transition_plan','detail_flurry','reuse_policy','sound_plan','source_trim_status'];
const esc=v=>`"${String(v??'').replaceAll('"','""')}"`;
fs.writeFileSync(path.join(base,'shot-plan.csv'),'\uFEFF'+[cols.join(','),...shots.map(s=>cols.map(k=>esc(s[k])).join(','))].join('\r\n'),'utf8');
let md='# 速度与选择｜两分钟高燃剪辑方案\n\n';
md+='这是能编辑的**73个镜头槽计划**，还没有剪成视频。已实际查看30张候选中心单帧和总览；只读ffprobe确认源片规格，没有回看所有候选的完整动作，也没有锁定源入出点。JSON的source_in/source_out全部为空；表中电影时码是候选中心，**不是可直接导出的入点**。\n\n';
md+='先抓危险，再让观众认人；第一轮街道追逐后留15秒给人物，再把高速公路/直升机的体量推上去。最后用反应与对讲机留下悬念。它是主题式高燃重组，不是原电影单场追逐复述；跑道、武器和刮擦单帧不能证明逃脱、发射或胜负。\n\n';
md+='文件：[plan.json](plan.json)保存可改参数与素材目录；[shot-plan.csv](shot-plan.csv)可用Excel改镜头；[节奏设计](music-design.json)、[拍点表](beat-markers.csv)、[可编辑MIDI](128BPM_120秒_可编辑节奏.mid)、[原创节奏导轨](128BPM_120秒_原创节奏导轨.m4a)。修改CSV不会自动写回JSON；批量重建时应同步修改build-plan.mjs中的spec再运行，避免两份计划不一致。\n\n';
md+='## 在自己的电脑连接源片\n\n公开计划仅记录`sourceId: FASTX10`与文件名`11 速度与激情10（2023）4K.mp4`，不含本机盘符。使用前，在剪辑器中把FASTX10重新链接到自己有权使用的实际媒体文件；如果写自动化导入器，另外建立仅在本地保存的素材映射，例如`{"FASTX10":"填写你电脑上的实际媒体路径"}`，不要提交这份私人路径配置。源路径不是plan.json的一部分，源入出点也仍需复查后填写。\n\n';
md+='## 交付与节奏\n\n';
md+='- 交付：24fps，120秒，2880帧；1920×1080，活动画面1920×800，上下各140像素黑边，保留原片2.4:1。\n- 源片：3840×1600、24000/1001≈23.976fps、10bit BT.2020/PQ HDR；这些是本机ffprobe实际返回。\n- 节奏：128BPM，4/4，64小节、256拍。现有MIDI/音轨是原创节奏导轨，尚不是完整配器/混音的最终歌曲。\n- 切点：从累计拍数换算24fps，再取最近整数帧；一拍约11或12帧、两拍约22或23帧、四拍45帧、八拍90帧。不要逐镜时长先四舍五入再累加。最大拍点量化误差约20.833毫秒，所有章节边界恰为整数帧。\n- 源23.976与交付24并非完全相同：默认保持源真实时间，常规帧采样而非光流；若选择逐源帧解释为24，会提速0.1%，声音也要同步、入出点要重算。原生分析证据不做改帧率。\n\n';
md+='|段落|时间线|拍数|槽数|目的|\n|---|---|---:|---:|---|\n';
for(const s of sections)md+=`|${s.id} ${s.name}|${s.start}–${s.end}s|${s.beats}|${s.last_slot-s.first_slot+1}|${s.intent}|\n`;
md+='\n主高潮不是45秒一路越切越短：67.5–82.5秒先读清车队/直升机，82.5–90秒才做16拍细节密集，90–97.5秒回人物反应与短宽景，97.5–112.5秒恢复1.875秒动作槽，让关键大动作能看完。\n\n';
md+='## 30个单帧候选：什么已看见、什么没证明\n\n';
md+='![候选总览](evidence/速激素材候选总览.jpg)\n\n';
md+='下表中心时码只定位已看见的图片。首次建议查看中心前后各4秒，再收缩到真实同镜；±4秒不是已确认可用长度。运动方向、对白、动作起止、是否另有硬切都需动态回看。\n\n';
md+='|候选|原片中心时码|单帧可见|图片证据|\n|---|---|---|---|\n';
for(const c of candidates)md+=`|${c.id} ${c.label}|${c.center_timecode}|${c.observed_single_frame}|[中心帧](${c.evidence})|\n`;
md+='\n## 73槽镜头表\n\n';
md+='时间线时码格式为HH:MM:SS:FF、24fps；结束时码不含该帧。拍号为0基，拍数是长度。**每行都待复查源入出点**，不会拿中心帧前后想象一段“肯定可用”的动作。\n\n';
for(const sec of sections){
 md+=`### ${sec.id} · ${sec.name}（${sec.start}–${sec.end}秒）\n\n|槽|时间线入–出|拍数|候选中心 / 证据|剪辑职责与动作|\n|---|---|---:|---|---|\n`;
 for(const s of shots.filter(s=>s.section===sec.id))md+=`|${s.id}|${s.timeline_start_timecode}–${s.timeline_end_timecode_exclusive}|${s.beat_length}|[${s.source_center_timecode}](${s.source_evidence})|${s.intended_role}：${s.edit_intent}|\n`;
 md+='\n';
}
md+='## 一拍槽与重复候选怎么处理\n\n';
md+='S38–S53是16个一拍槽（82.5–90秒）。优先把同一原镜的脚/踏板、手/挡杆、仪表/边缘、控件/手指、脸/方向盘、机身/门内、缆线/车顶、亮火星/刮擦边缘分成互补细节：源时间继续向前，不能每槽从同一动作起点重放。4K源可供适度裁切，但若细节软糊或构图不成立，保持原景别；不能凭中心单帧保证眼部特写有足够分辨率。\n\n';
md+='重复候选只是“再去这个中心附近查找”，不是批准重播同次换挡/同次碰撞。若找不到不同动作或同镜连续范围，换同职责源镜；也可让一镜跨过几个节拍槽，只用标记保留节奏结构。73个槽不强迫73次实际换画面，更不能用静帧横移凑成动态。\n\n';
md+='## 学到的手法如何用\n\n';
for(const x of plan.learned_methods.apply)md+=`- ${x.references.join(' / ')}：${x.use}。\n`;
md+='\n不宜直接套用：\n\n';
for(const x of plan.learned_methods.avoid)md+=`- **${x.method}**：${x.why}。\n`;
md+='\n最多保留一套短标题、一处矩形/圆形桥和自己的尾卡。先把车的方向、车距、人物判断剪清楚，再加图层。OCC负责主时间线和基础变换；HF/GSAP只做必要的短合成。复杂alpha、跟踪、曲线变速不是已具备的自动服务。\n\n';
md+='## HDR转SDR与画幅\n\n';
md+=plan.color_workflow.steps.map((x,i)=>`${i+1}. ${x}。`).join('\n\n')+'\n\n';
md+='可试的FFmpeg滤镜起点（仅滤镜文本，不是本轮已渲染的结果）：\n\n```text\n'+plan.color_workflow.ffmpeg_filter_starting_point+'\n```\n\n';
md+=plan.color_workflow.filter_status+'。只给最终选定的短段做代理或转换，不转整部电影。\n\n';
md+='## 对白、车辆音效与配乐\n\n';
md+='本方案不假装已选好台词或拥有干净stems。建议四轨：\n\n';
for(const t of plan.audio_plan.tracks)md+=`- **${t.track} ${t.role}**：${t.rule}。\n`;
md+='\n'+plan.audio_plan.dialogue_review.map((x,i)=>`${i+1}. ${x}。`).join('\n\n')+'\n\n';
md+='冷开只保留少数真实冲击；52.5–67.5秒减鼓/低频层让人物有呼吸；高潮细节段不每拍叠hit；末段给完整短句/尾音留下空间。试混目标可从-14至-16LUFS-I、True Peak不高于-1dBTP起步，之后按平台和内容调整。这是计划目标，尚未混音测量。\n\n';
md+='**为什么不把10秒参考曲硬循环两分钟：** '+plan.audio_plan.short_reference_loop_reason+'\n\n';
md+='## 原片硬字幕与源段复查\n\n'+plan.subtitle_policy+'\n\n';
md+='每个槽锁定前填写：真实源入点/出点、动作方向、接触/反应相位、同镜可用长度、余量、是否已用过、硬字幕、原片声段。需要的源长度要覆盖时间线槽长；变速或转场时另算，不把建议回看窗口整段直接导出。\n\n';
md+='建议按JSON的operational_order执行：\n\n'+plan.operational_order.map((x,i)=>`${i+1}. ${x}。`).join('\n\n')+'\n\n';
md+='## 自检结果\n\n';
md+=`- 73个槽；256拍；24fps下2880帧；精确120秒。\n- 六段帧边界：0/180/540/1260/1620/2700/2880；镜头槽连续、无重叠/空洞。\n- ${candidates.length}张候选证据引用全部存在；中心单帧已看，源入/出点仍全部null。\n- 音乐设计与128BPM/256拍/120秒一致；没有把10秒参考音频当成两分钟完整歌曲。\n- 本轮未提取整部电影、未渲染最终视频、未试听锁定对白、未改OpenChatCut或GitHub。\n`;
md+='\n重新生成后运行`node validate-plan.mjs`，可复查[MIDI与时间线验证记录](validation.json)。本轮实际解析到MIDI为480PPQ、每四分音符468750微秒（128BPM）、4/4、122880ticks=256拍，文件终点精确120秒；最后note-off约119.892578秒。六段MIDI时间边界与计划逐一相等。已有AAC容器约120.021333秒是编码padding，不能据此把120秒时间线改长。\n';
fs.writeFileSync(path.join(base,'README_两分钟高燃剪辑方案.md'),md,'utf8');
console.log(JSON.stringify(plan.validation));
