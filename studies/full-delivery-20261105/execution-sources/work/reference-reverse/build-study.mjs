import fs from 'node:fs';
import path from 'node:path';
const W=import.meta.dirname, O=path.resolve(W,'../../outputs/reference-editing-study');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,v)};
const json=(p,v)=>write(p,JSON.stringify(v,null,2)+'\n');
const copy=(a,b)=>{fs.mkdirSync(path.dirname(b),{recursive:true});fs.copyFileSync(a,b)};
const manifest=read(path.join(W,'manifest.local.json'));
for(const v of manifest){
 const dir=path.join(W,'visuals',v.id);
 for(const f of fs.readdirSync(dir))if(/\.(jpg|json)$/.test(f))copy(path.join(dir,f),path.join(O,'evidence',v.id,f));
 for(const folder of ['details','anime'])for(const f of fs.readdirSync(path.join(W,folder)))if(f.startsWith(v.id)&&/\.jpg(\.json)?$/.test(f))copy(path.join(W,folder,f),path.join(O,'evidence',v.id,f));
 copy(path.join(W,'audio',v.id+'.json'),path.join(O,'data/audio',v.id+'.json'));
 copy(path.join(W,v.id+'-probe.json'),path.join(O,'data/probe',v.id+'.json'));
}
json(path.join(O,'local-config.json'),{media:Object.fromEntries(manifest.map(v=>[v.id,v.path]))});
json(path.join(O,'data/manifest.json'),manifest.map(({path:_,...v})=>v));
copy(path.join(W,'audio/index.json'),path.join(O,'data/audio-index.json'));
copy(path.join(W,'capabilities.json'),path.join(O,'data/capabilities.json'));
copy(path.join(W,'anime-review.json'),path.join(O,'data/anime-review-original.json'));
copy(path.join(W,'long-montage-review.json'),path.join(O,'data/long-review-original.json'));
const s=(start,end,label,observed,recipe,evidence,confidence='高：可见结构；中：等效实现，尚未试制')=>({start,end,label,observed,recipe,confidence,evidence});
const pic=(id,file)=>`evidence/${id}/${file}.jpg`;
const sheet=(id,n=1)=>pic(id,`timeline-${String(n).padStart(2,'0')}`);
const reviews=[
{id:'V01',title:'蜘蛛侠版本 · 人物拼贴与圆形穿越',difficulty:'4/5',starter:'先练20.8–21.2秒单次圆形展开；不先做整片抠像。',summary:'照片墙、人物前景、轮廓闪白与圆形窗口构成统一风格。最容易拆成可换素材组件的是圆形揭示；完整复现的成本在人物动态边缘。',segments:[
s(0,6.7,'人物在前，照片墙在后','三位演员依次成为中央前景，旁边照片卡片独立移动；底部有人名牌与小字。画面具有不同运动层。','先准备人物alpha片段、3–6张照片和姓名。HyperFrames里分为背景、照片卡、前景人物、文字四层；卡片轻微错时移动，人物保持阅读中心。抠像方法无法从成片判定。',[sheet('V01')]),
s(6.7,11.8,'白色人物剪影与分屏','人物切换时有白色轮廓/剪影；画中画矩形与多人分屏接续，约10.5秒为三位人物分区。','人物alpha复制一层填白，作为短促轮廓桥；下层替换新背景，上层接新人物。白色持续1–2帧是试验起点，不是恢复的原参数。分屏使用独立矩形裁切。',[sheet('V01')]),
s(11.8,20.6,'动作镜头与前景提前出现','面部、飞跃、摆荡镜头串联；有竖向画框和人物提前叠到旧背景上。电影里的蛛丝、机甲、飞行动作不能据此归为剪辑新增。','先按方向和动作相位连接原镜；需要人物提前入场的地方，使用同一B素材的全幅与alpha同步副本。只给连接处做位置/大小微调。',[sheet('V01',2)]),
s(20.6,22.5,'连续圆形揭示','约20.8秒，小圆窗出现在人物胸前，21.1秒左右已转入夕阳镜头；21.5秒新圆窗再次展开。圆边和窗口内不同画面清晰可见。','A在底，B在上；B用圆形mask限制显示，圆心对准胸口，半径由小变大直到覆盖画布。视频内容的缩放与mask半径分开控制。先用6–12帧完成一次展开，时长需用音乐和原片回看调整。',[pic('V01','V01-circle')]),
s(22.5,26.8,'圆窗沿面部继续接力','人物脸附近再次形成下一镜入口，23.667秒附近圆窗可见，24秒左右明显放大；随后回到人物与动作素材。','复用圆形揭示组件，但每镜重选圆心和目标主体位置。窗口铺满之前让B画面主体落到后续全幅相同位置，防止最后一帧跳动。',[pic('V01','V01-face-portal'),sheet('V01',2)]),
s(26.8,32.466667,'署名与蜘蛛侠标题收束','先有蛛网/悬挂背景和文字，之后出现SPIDER-MAN标题，末尾逐渐暗下。','用独立文字层做缩放和透明度；中文说明与主标题分层。字形可找相近替代，不能从压缩成片唯一确认字体、商业模板或插件。',[sheet('V01',3)])]},
{id:'V04',title:'蜘蛛侠循环 · 漫画拼贴与眼罩窗口',difficulty:'4/5',starter:'先练11.7–13秒静态眼形窗口，之后再加漫画贴纸。',summary:'卡通开场、漫画分栏、描边人物、眼罩内换片和回到开场画面。外观统一来自层次和选材，并没有证据能识别原作者的软件或插件。',segments:[
s(0,5.9,'猫和老鼠作为开场钩子','卡通人物互动开场，人物脸部伸缩与动作属于可见动画本身。','直接保留合适的源动画片段；只处理入出点和与后段的节奏关系。不要把原动画的夸张变形误记为剪辑软件新做的效果。',[sheet('V04'),pic('V04','V04-loop-start')]),
s(5.9,9.6,'动作转漫画，分栏与RGB边缘','蜘蛛侠动作片段被放进画中画、倾斜条带和漫画式版面；出现红色弧形文字、近景推拉及彩色错位边缘。','HyperFrames做矩形/斜边裁切、纸张层与标题；主体镜头由OCC选好再放入。RGB错位只做局部短段；漫画纸纹、半调网点属于外观，不代表已识别出某个模板。',[sheet('V04')]),
s(9.6,11.65,'倾斜电影卡片与白边人物','约9.917–10.5秒，斜长视频卡叠在大人物脸前；10.583–10.75秒，小蜘蛛侠带白边向前放大。','卡片使用旋转矩形裁切。人物单独alpha层下方增加白色膨胀轮廓，然后缩放入场；若只有整张视频，先准备人物遮罩，不能对整幅加白边替代。',[pic('V04','V04-cutout')]),
s(11.65,13.15,'眼罩内连续换镜','面罩外侧相对稳定，眼罩形窗口内快速替换多个动作镜头；局部片段出现反相/青色调。','用SVG路径画眼罩边界，把B素材裁进眼形内，上方保留面罩边缘。窗口内每次换片可以硬切，外部脸层不必一起跳。此处适合HyperFrames预合成；OCC仅有圆形/矩形mask不足以原样还原眼形。',[pic('V04','V04-eye-portal')]),
s(13.15,20.7,'漫画牌、反相卡片与动作串联','斜放的小卡、漫画字牌、反相色块和动作片段交替；有明显运动模糊。','将版式限定为眼罩、倾斜卡片、主体描边三类。动作先接顺，再决定是否加短模糊；源片已有模糊时不要机械叠加。',[sheet('V04',2)]),
s(20.7,21.500998,'回到开场构图','末段暗色线条画面叠回猫和老鼠，末帧与开场属于近似构图。已看到视觉回归，未证明首尾像素相同或音频无缝。','选开头动作之前的连续源帧作尾部，去掉重复帧，单独试听尾音接首音。先做画面循环，再检查音频循环；不能因片名写“无缝循环”就判定所有边界完美。',[pic('V04','V04-loop-end'),pic('V04','V04-loop-start')])]},
{id:'V08',title:'能力越大责任越大 · 多版本人物接力',difficulty:'4/5',starter:'先做一个白色剪影换人，再加入照片墙和文字条。',summary:'人物前景与照片墙独立移动，白色剪影遮盖换人，动作桥连接真人与动画。难点在连续人物alpha、边缘处理和视觉中心保持。',segments:[
s(0,7.2,'人物照片墙与白底字幕条','真人及动画人物依次出现在前景，后面有照片、点状轨道和卡片；中文黑字置于白条上，条与文字逐步展开。','HyperFrames做照片墙、轨道线、人物和字幕四层；字幕按短句显示，白条宽度随字数增长。字的出现时间要与实际对白/声音人工核对，本次未听辨台词。',[sheet('V08')]),
s(7.2,8.65,'白剪影先到，人物随后换入','7.25秒附近白色轮廓出现在旧镜，随后新人物显现；矩形背景、斜边背景依次更换。多次新人物先于全幅背景出现。','A底图→白色alpha闪现→B人物alpha→B完整底图。人物alpha与B底图必须引用同一源时刻；不然手脚边缘会双影。透明人物素材需先准备。',[pic('V08','V08-silhouette')]),
s(8.65,14.8,'插卡、脸部接续与字幕','照片卡与新人物短暂叠放，之后进入面部、机甲等全幅镜头；白底字幕条仍参与画面。','以眼睛/头部位置作构图锚点，用少量裁切统一脸的大小。电影机甲本身是源画面视觉内容，不能归成一个可下载的剪辑滤镜。',[sheet('V08')]),
s(14.8,19.0,'真人、蜘蛛宇宙与旧动画互接','不同绘画风格的蜘蛛侠片段按姿势、射蛛丝动作和身体方向接续。','把每条素材的起手、发射、摆荡顶点标出来，再选择方向一致的切口。变速是否为作者新增无法唯一恢复；先按源素材恒速连接。',[sheet('V08',2)]),
s(19.0,30.8,'动作链延续，节奏起伏','真人、CG、2D动作交替，飞跃、受击、摆荡构成视觉接力；并非每段都使用同一种过渡。','OCC负责分割、裁切、音轨和基础变换；只把需要人物边缘或特殊窗口的短段送到HyperFrames合成。源CG保留，避免把所有复杂镜头都变成从零制作任务。',[sheet('V08',2),sheet('V08',3)]),
s(30.8,32.733333,'标题尾卡','黑底风格文字与蜘蛛侠标题在尾部收束，顶部有光感，最后变暗。','标题层、光晕层与黑底分开；用透明度和轻微缩放完成。署名换自己的，准确字体/模板未确认。',[sheet('V08',3)])]},
{id:'V09',title:'Flow赛车 · 高反差与发光空间段',difficulty:'5/5',starter:'先练0.5–4秒的高反差短切；发光空间段先寻找源素材。',summary:'高反差黑白、细小装饰数字、负片/分屏与汽车快切混合。4.5–6秒发光空间的来源不明，这是原样复刻最大的未知项。',segments:[
s(0,1.5,'赛车切黑白人物','赛车掠过起点后进入高反差黑白人物；画面上叠有细小数字、虚线/轨道等图形。','先做裁切与高反差映射，再叠极细图形和小字。小数字是装饰/信息层，并不是整条片以大字卡点为主。',[sheet('V09')]),
s(1.5,3.5,'短镜、分区与负片','街头、人物、雕塑等短段交替，出现竖向分区、像素/网点感、局部反相和推拉模糊。','使用少量不同材质的镜头制造反差；同镜复制成两区，只给其中一区反相。用固定版式变化保持风格，不靠随机叠所有效果。',[sheet('V09')]),
s(3.5,4.5,'轮廓与打击动作','黑白动作轮廓明显，局部亮边和快速尺度变化强化冲击。','先选动作命中帧，再决定阈值/反差、轮廓和短推拉幅度。若源画面自带拖影，额外模糊应少量。',[sheet('V09'),pic('V09','V09-light-travel')]),
s(4.5,6.25,'发光轨道/空间穿梭','亮线组成的空间随视角旋转，亮白物体/车状形体前进，透视结构明显；并非一张平面卡片的简单淡入。','先确认这一段是否已存在于原素材。如果有，复用后做调色与模糊；如果没有，需要专门3D/程序化场景或替代素材。仅凭成片无法证明是某个现成插件，当前不能承诺靠OCC基础转场同等重建。',[pic('V09','V09-light-travel')],'高：可见空间运动；低：制作来源与精确复现成本'),
s(6.25,8.9,'车轮、车尾、漂移与落日停留','近景汽车细节与高反差画面快速切换，最后漂移/落日镜头停留相对较久。','细节短镜后留一个较长全景释放节奏；按运动方向接轮胎/车尾，比整段统一快切更有层次。',[sheet('V09')]),
s(8.9,10.733333,'黑底小字结束','画面转为黑底，细小署名/字样收尾。','用自己的小字署名和短淡出。此片音频太短且HF未输出稳定节拍，学习时按实际起音事件逐个核对，不硬套110 BPM网格。',[sheet('V09')])]},
{id:'V10',title:'BMW M4 · 三分屏与车标轮毂穿越',difficulty:'4/5',starter:'先练12.8秒后的普通细节切镜，再做一个圆形门户。',summary:'三分屏、蓝白轮廓、BMW圆形车标和轮毂构成连续视觉入口。简化圆形版约3/5；原样保留轮辐遮挡、透视和轮廓为4/5。',segments:[
s(0,6.4,'三层横向分屏与车身亮边','上下是车轮/排气/尾灯细节，中间为整车；车身轮廓有蓝白亮边，几块画面分别变化。','用三个裁切容器放独立视频；中间车身描边需要轮廓mask/路径，发光用复制轮廓加模糊实现。整车画面较稳定时手工描线可做原型，但不能把滤镜发光误当作自动理解车边。',[sheet('V10')]),
s(6.4,8.9,'车尾缩入BMW车标，再穿出前灯','6.875–7.625秒，车尾画面缩入BMW圆形标志的特写；外侧露出标志周围的金属灰结构。8.25秒附近下一车头画面又在标志圆内出现并放大。此处按可见圆形标志标注，不对部件位置作额外判断。','先准备车尾A、车标特写B、车头C三镜。A圆形mask随缩放落到B车标；B车标位置用跟踪/手工关键帧对齐。再把C裁进同一圆窗并放大。实际车标带透视，简化圆形版可先做，精确版需要椭圆/路径和透视调整。',[pic('V10','V10-round-portal')]),
s(8.9,10.8,'下一镜藏在轮毂里面','车轮近景中逐渐出现下一车头画面，早期轮辐仍在前景；之后车头画面占满屏幕。','底层轮胎/旧镜，中层下一车头视频限在轮孔内，顶层保留轮辐alpha。三个层的缩放中心一致，窗口铺满后接完整车头。只有一个圆形裁切会丢掉轮辐遮挡关系。',[pic('V10','V10-wheel-portal')]),
s(10.8,12.8,'车头、侧向残影和车灯','车头镜头之后出现两侧重复影像的短暂效果，再进入车灯近景。','复制主体镜头向两侧错位，快速降低透明度作为短残影；主体仍居中。把效果限制在连接处，避免整段影响车身细节。',[sheet('V10')]),
s(12.8,17.5,'细节镜头接节奏','方向盘、车头斜侧、车尾、排气、内饰、座椅等镜头接续；主要是短切和轻微运动，没有每个切口都做门户。','适合第一项练习：选6–8个车细节镜头，先按动作/构图排，再对照实际起音调切口。80/160 BPM为较稳候选，但不要自动把全部镜头长度锁成0.75秒。',[sheet('V10',2)]),
s(17.5,18.069002,'车灯收尾','最后停在车灯近景并结束。','保留最后一个清楚的造型点，让音乐收束；不要为了“每拍有变化”再加多余镜头。',[sheet('V10',2)])]}
];
const anime=read(path.join(W,'anime-review.json'));
const labels={V02:['漫画板式开场','回到动作场景','人物压在大字前','同一漫画板换色换人','红黑段与攻击反应链','人物特写向中心聚拢','结束动作与署名'],V03:['圆形能量缩入巨眼','新前景先入，背景后换','环形与手势匹配','跨2D/3D的手指遮挡','细线、手势与衣袖接力','袖口提前盖住棋盘','稳定尾镜与淡暗'],V05:['标题与故障开场','六格卡片依次拼出','中心拼图小窗','动作、分屏和插卡','三色漫画三联','描边人物与眼部插窗','CRT电视关机'],V07:['手势与中心强光接力','持剑手臂先进入旧镜','金色手与浅色手接力','瞳孔、手掌和亮区匹配','会转动的前臂遮挡','武器、圆盘与巨眼接续','双指内窗与最后手势']};
const extras={V02:{title:'咒术回战 · 漫画排字与人物抠像',difficulty:'4/5',starter:'先做静态漫画底板和大字，再加一段人物alpha。'},V03:{title:'国漫新春 · 巨眼与袖口遮挡',difficulty:'5/5',starter:'先练15.4–17.9秒袖口前景接力中的单个过渡。'},V05:{title:'反击 · 六格拼图、三联画与CRT',difficulty:'4/5',starter:'先练1.7–2.3秒六格卡片；不需要先抠完整人物。'},V07:{title:'国漫手势 · 动态前景与指缝门户',difficulty:'5/5',starter:'先做静态三角窗口；会动的指缝和手部alpha放在最后学。'}};
function normEvidence(raw,id){const p=raw.split('@')[0];return `evidence/${id}/${path.posix.basename(p)}`}
for(const v of anime.videos)reviews.push({...extras[v.id],id:v.id,summary:v.summary,text_analysis:v.text,segments:v.segments.map((x,i)=>({...s(...x.range,labels[v.id][i],`${x.observed}\n可确认：${x.confirmed}\n来源边界：${x.source_animation_boundary||'缺少源素材，无法唯一归因。'}`,`${x.hypothesis}\n${x.recipe.map((r,j)=>`${j+1}. ${r}`).join('\n')}`,x.evidence.map(p=>normEvidence(p,v.id)),x.confidence),proposed_parameters:true}))});
const l=read(path.join(W,'long-montage-review.json'));
const longSegments=l.segments.map(x=>s(x.start,x.end,x.title,`${x.observation}\n限制：${x.uncertainty}`,x.edit,[pic('V06',x.sheet.replace('.jpg',''))],'高：段落结构；细部见重点原帧证据'));
for(const d of l.dense_examples)longSegments.push(s(...d.range,'重点复盘：'+d.title,`${d.observed.join('\n')}\n判断：${d.inference}\n未知：${d.unknown.join('；')}`,d.reproduce,d.artifacts.map(f=>pic('V06',f.replace('.jpg',''))),'高：相邻原帧；参数为待试制起点'));
longSegments.sort((a,b)=>a.start-b.start);
reviews.push({id:'V06',title:'130秒动作混剪 · 跨片运动匹配',difficulty:'5/5',starter:'只先做81.75秒旋转枪那一个硬切，约2–3/5。',summary:l.main_finding+'全片5/5主要因为素材检索、长段编排和多种连接方式；单个动作匹配可以先练。',segments:longSegments});
const gapsFile=path.join(W,'anime-gaps.json');
if(fs.existsSync(gapsFile))for(const g of read(gapsFile)){const v=reviews.find(x=>x.id===g.id);if(v)v.segments.push({...g,recipe:Array.isArray(g.recipe)?g.recipe.map((x,i)=>`${i+1}. ${x}`).join('\n'):g.recipe,metadata_evidence:g.evidence.filter(p=>!p.split('@')[0].endsWith('.jpg')),evidence:g.evidence.filter(p=>p.split('@')[0].endsWith('.jpg')).map(p=>normEvidence(p,g.id))})}
reviews.sort((a,b)=>a.id.localeCompare(b.id));
for(const v of reviews)v.segments.sort((a,b)=>a.start-b.start);
json(path.join(O,'data/reviews.json'),reviews);
const audio=read(path.join(W,'audio/index.json'));
const cutExamples=[{id:'V06',t:81.75,event:'CG旋转枪→真人室内',frame:1962},{id:'V06',t:93.5,event:'真人胸部命中跨片',frame:2244},{id:'V06',t:94+2/24,event:'真人→CG胸腹命中',frame:2258}].map(c=>{
 const a=read(path.join(W,'audio',c.id+'.json'));
 const near=(list)=>list.reduce((best,t)=>Math.abs(t-c.t)<Math.abs(best-c.t)?t:best,Infinity);
 const onset=near(a.onset_events.map(e=>e.t)),beat=near(a.hyperframes.beats.times);
 return {...c,frame_numbering:'zero-based',nearest_onset:onset,cut_minus_onset_ms:Math.round((c.t-onset)*1000),nearest_inferred_beat:beat,cut_minus_beat_ms:Math.round((c.t-beat)*1000),caution:'最近不等于因果；起音包含对白/音效，网格可能在无声区继续，不代表听觉确认。'};
});
json(path.join(O,'data/selected-cut-audio.json'),cutExamples);
const csvCell=x=>'"'+String(x??'').replaceAll('"','""')+'"';
const rows=[['视频ID','短标题','开始秒','结束秒','学习章节','可见事实','复刻方案_未验证','信度','证据路径']];
for(const v of reviews)for(const x of v.segments)rows.push([v.id,v.title,x.start,x.end,x.label,x.observed,x.recipe,x.confidence,x.evidence.join(' | ')]);
write(path.join(O,'镜头与效果事件清单.csv'),'\uFEFF'+rows.map(r=>r.map(csvCell).join(',')).join('\r\n'));
let details='# 10条参考片逐段拆解\n\n本表是学习章节与效果事件，不是原作者工程的全部剪辑点。时间为参考片播放时间；粗采样片段用于定位，原帧证据用于确认少数边界。所有复刻方法和数值都是等效方案，尚未实际复刻渲染。\n\n';
for(const v of reviews){const a=audio.find(x=>x.id===v.id);details+=`## ${v.id} ${v.title}\n\n完整复现难度：**${v.difficulty}**。${v.summary}\n\n先学：${v.starter}\n\n音频：${a.notes.reason}\n\n${a.notes.study}\n\n`;
 for(const x of v.segments)details+=`### ${x.start.toFixed(3)}–${x.end.toFixed(3)}秒 · ${x.label}\n\n**画面证据**：${x.observed}\n\n**等效复刻方法**：\n\n${x.recipe}\n\n**信度**：${x.confidence}\n\n${x.evidence.map(p=>`[查看 ${path.basename(p)}](${p})`).join(' · ')}\n\n`;
}
write(path.join(O,'逐片拆解.md'),details);
let audioDoc='# 音乐卡点：测量结果与实际用法\n\n本次使用本机HyperFrames 0.8.216音频算法、频谱周期分析与montage能量基线。没有完成听觉确认、歌曲识别、鼓/人声分轨，也不把BPM候选当成原曲官方BPM。原始AAC音轨包含对白、音效和音乐；爆点不一定是鼓点。\n\n';
audioDoc+='|视频|周期候选 BPM|稳定性/限制|起步练习|\n|---|---|---|---|\n'+audio.map(a=>`|${a.id}|${a.bpm_candidates.join(' / ')||'不确定'}|${a.confidence}|${a.notes.study}|`).join('\n');
audioDoc+='\n\n## 四个容易混淆的词\n\n- **起音（onset）**：声音突然出现或频谱变化的时刻。枪声、口音、鼓都可能触发。\n- **节拍（beat）**：算法推断的规律时间网格，安静处也可能继续向前走。\n- **重音/乐句转折**：创作上的重点，不能只用一次响度最大值代替。\n- **切镜/动作峰值**：画面的事件。可以落在拍上、半拍、提前一帧，或刻意留白。\n\n学习页把金色起音与绿色节拍分开画；点击可以跳到视频位置，方便你自己听辨。\n\n## 一条反例：无声处也能有预测的拍\n\nV06的87.401–88.464秒低于−50dBFS阈值，但推断节拍仍包含87.885秒。它说明“有网格线”不代表“这一刻真有鼓声”。87–92秒画面也进入对峙和人物反应，长片需要留白而不是全程等距碎切。−50dBFS是测量阈值，不是绝对无声判定。\n\n## 三处原帧切点与声音候选的距离\n\n下列切点已用24fps相邻原帧确认。差值=切点−候选时间，负数表示画面先到。只用来示范核对方法，不用于宣称作者每刀精准卡拍。\n\n|切点秒|画面|最近起音秒|相差毫秒|最近预测拍秒|相差毫秒|\n|---|---|---|---|---|---|\n';
audioDoc+=cutExamples.map(c=>`|${c.t.toFixed(3)}|${c.event}|${c.nearest_onset.toFixed(3)}|${c.cut_minus_onset_ms}|${c.nearest_inferred_beat.toFixed(3)}|${c.cut_minus_beat_ms}|`).join('\n');
audioDoc+='\n\n## 逐片说明\n\n'+audio.map(a=>`### ${a.id}\n\n${a.notes.reason}\n\n${a.notes.structure}\n\n练习：${a.notes.study}\n\n[原始测量JSON](data/audio/${a.id}.json)\n`).join('\n');
audioDoc+='\n## 实际卡点步骤\n\n1. 先听一小段，明确要跟鼓、歌词、音效还是动作。\n2. 在起音候选里挑真正有用的重音，删除误报。\n3. 把动作“接触/命中”放在重点声音附近，镜头开头可以提前。\n4. 根据素材原帧率按±1–3帧微调，回到正常速度检验。\n5. 再做半拍碎切、停顿和高潮，不把算法网格全用掉。\n\n30fps一帧约33.3ms；25fps一帧40ms；24fps一帧约41.7ms。JSON里更多小数来自计算，并不代表人耳或成片拥有毫秒级精确度。\n';
write(path.join(O,'音乐卡点说明.md'),audioDoc);
let evidence='# 证据与执行记录\n\n## 范围\n\n10个本地MP4，总时长'+manifest.reduce((n,v)=>n+v.duration,0).toFixed(3)+'秒。原片保持原位，以SHA-256标识版本。没有上传视频、制作全片复刻或恢复作者工程。\n\n';
evidence+='|ID|秒|尺寸|帧率|SHA-256|\n|---|---|---|---|---|\n'+manifest.map(v=>`|${v.id}|${v.duration}|${v.width}×${v.height}|${v.fps}|\`${v.sha256}\`|`).join('\n');
evidence+='\n\n## 每步实际做了什么\n\n1. 读取REA与montage等适配技能；REA本地CLI版本6.8.0，做了help/doctor与能力检查。没有可用的REA视频反编译路径，doctor也未证明全部运行时引擎可用。\n2. 用ffprobe读取编码、尺寸、帧率、时长；用文件哈希固定输入。见data/manifest.json和data/probe。\n3. 全部视频抽24格总览；短片按0.5秒采样，V06按1秒采样形成联系表。全片联系表由主流程或相应审查分支实际查看。\n4. 对眼罩、手指、袖口、车标、轮毂和动作连接处提取密帧。根流程的details组保留源PTS；anime组为重采样近似时间，V06 frame-*为24fps原帧证据。\n5. FFmpeg scene阈值0.10只产生变化候选；缩放、白闪和运动也会触发，未把候选数当切镜数。\n6. 每条音轨解码为22050Hz单声道PCM；实际调用HF 0.8.216本地signal库，比较频谱周期与montage能量基线。未做听觉确认。\n7. 审查OCC本机源码与HyperFrames本机CLI/实现，分别记录实际功能、限制和未测试链路。\n8. 汇总中文分段、复刻配方、困难排序和本机交互查看器。网页只提供分析与播放，不把推测写成已经做好的特效。\n\n## 协作记录\n\n主流程为GPT-6 Astra；既有GPT-6.1 Sol high三个分支分别审查动画4条、V06与工具能力、音频与学习页。所有分支产物都有本地记录。多分支意见最后按画面/源码证据合并，不以模型投票代替证据。\n\n## 时间与证据边界\n\n- 联系表最后空格是排版补齐，不代表原片突然黑屏。\n- 0.5秒采样会漏掉数帧闪光；因此关键判断要看密帧或播放原片。\n- 视觉来源未知时，使用“源画面内效果候选”，不默认是作者后来添加。\n- 参数、mask路径、字体、速度曲线与原始关键帧数量都不能从最终MP4唯一反解。\n- 此处的普通shell、FFmpeg和HF输出按真实来源命名，不冒充REA MCP Evidence ID。\n\n## 复现脚本\n\n[scripts/source](scripts/source/)保存本次分析脚本快照。路径与HF打包chunk名称对应这台电脑当时版本；升级软件后必须重新检查，不承诺跨版本内部接口稳定。\n\n';
write(path.join(O,'证据与执行记录.md'),evidence);
const snapshot=['analyze-visuals.mjs','extract-details.mjs','v06-dense.mjs','v06-frame.mjs','build-capabilities.cjs'];
for(const f of snapshot)copy(path.join(W,f),path.join(O,'scripts/source',f));
for(const f of ['analyze-audio.mjs','summarize-audio.mjs'])copy(path.join(W,'audio',f),path.join(O,'scripts/source/audio',f));
copy(path.join(W,'anime/extract-window.ps1'),path.join(O,'scripts/source/anime/extract-window.ps1'));
copy(path.join(W,'capabilities.md'),path.join(O,'工具能力核查.md'));
json(path.join(O,'data/study-counts.json'),{videos:reviews.length,segments:reviews.reduce((n,v)=>n+v.segments.length,0),evidence_images:manifest.reduce((n,v)=>n+fs.readdirSync(path.join(O,'evidence',v.id)).filter(f=>/\.jpg$/.test(f)).length,0),source_duration_sec:manifest.reduce((n,v)=>n+v.duration,0),generated_at:new Date().toISOString()});
console.log(JSON.stringify(read(path.join(O,'data/study-counts.json'))));
