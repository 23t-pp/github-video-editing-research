import fs from 'node:fs';
import path from 'node:path';
const root=import.meta.dirname;
const round=n=>Number(n.toFixed(3));
const notes={
 V01:{bpm:[139.9,69.9],confidence:'较高（周期候选；未听觉确认）',reason:'8秒滑窗大多数落139.7–140.1，12–20秒半速69.9；频谱自相关0.472。montage能量基线92.3不是同一拍速，提示切分/对白影响，不据此推翻频谱140候选。',structure:'约0–25.3秒维持同一主要音色区；25.3秒出现统计音色边界。11.75秒前后响度降低约7.8dB、13.5秒回升约5.1dB；27.25秒再下降约10.8dB。不能把这些直接命名为副歌或drop。',study:'以0.429秒一拍、0.214秒半拍试建标记；先检查8.43/10.57秒附近起音，再决定镜头是否需要每拍切。'},
 V02:{bpm:[128,64],confidence:'中等偏高（后半段更稳）',reason:'HF128和能量基线127.7接近；12–24秒局部谱周期127.1–127.3，早期及4–12秒的51 BPM峰表现为更长节奏型，不应照抄为音乐速度。',structure:'17.24秒统计音色边界与17.25秒响度回升约5.5dB接近；15.25秒先下降约5.4dB，23.5秒明显收尾衰减。',study:'从12–20秒选择4–8小节练习，先按约0.469秒一拍，叠看17.2秒附近声音/画面共同变化。'},
 V03:{bpm:[88.5,177],confidence:'中等（有稳定慢脉冲，细分/音效仍不确定）',reason:'大多数0–28秒滑窗落88.4–89.0；HF0.263低于其high标签阈值0.35。谱峰88.7，能量基线82.2不一致，因此88.5只是可试脉冲。177为倍速细分假设，不是独立识别结果。',structure:'22.315秒统计音色边界；8.75秒、12.25秒响度上升；28.75秒附近大幅衰减约23.8dB。',study:'按0.678秒一拍或0.339秒半拍设置候选标记，先学习动作落点，不将177 BPM当已确认曲速。'},
 V04:{bpm:[123.9,61.9],confidence:'较高（半速/倍速记谱歧义）',reason:'HF123.9；能量基线61.9；谱周期62和124两组峰均强。8–20秒局部124很一致，属于清楚的2:1别名关系。',structure:'6.0秒音色边界；5.5秒前后响度抬升约13.9dB，强谱起音从6.254/6.735秒起清楚出现。10.25和14.0秒附近有响度回落。',study:'从6.25秒后练0.484秒一拍；长镜头也可用0.969秒半速。转场若跨多个画面帧，先把“视觉最强瞬间”而非转场起点对到声音。'},
 V05:{bpm:[140,93.4,56,96.9],confidence:'低（拒绝给唯一BPM）',reason:'算法冲突明显：HF96.9、全局频谱最强56、其次93.4、能量基线139.5。56/93.4/140呈较长节奏型/细分相关，HF96.9又有漂移，不能任挑一个当歌曲真速。',structure:'8.235秒音色边界；1.25秒响度抬升约11.1dB，15.5秒抬升约5.6dB，22.0秒下降约7.2dB。强起音分布密，可能混有打击/对白/剪辑音效。',study:'先使用1.894/4.681/6.495/13.350/18.141/21.679秒等真实谱起音做锚点，人工听拍后再建立全局网格；不建议新手先做全自动对齐。'},
 V06:{bpm:[105.9,53,212],confidence:'中等偏低（长片、多段、节拍网格有明显局部失效风险）',reason:'多数中段滑窗可归到约106、53或212这组倍半速；0–12秒、84–96秒和若干局部窗不稳定。HF0.235，能量基线60.6与主候选不符，不能用一个BPM覆盖130秒。',structure:'统计边界约6.50、51.53、58.33、87.27、92.53、101.57、109.52秒；87.3秒后确有极低电平/静音间隔，91.3秒重新进入高电平，需分段重置。尤其87.401–88.464秒低于−50dBFS，HF却在87.885秒仍插入推断beat，是网格不能冒充真实声响的直接例子。A/B字母只指统计音色相似，不是主歌/副歌。',study:'先抽58–68或104–116秒10秒段练习；约0.566秒脉冲。在87–92秒断开拍点网格，禁止把平滑外推的beats当音乐仍在响。'},
 V07:{bpm:[100.2,50],confidence:'低到中等（局部周期可用；HF拒绝稳定拍点）',reason:'HF confidence0.132低于其0.15门槛，返回no steady beat；但4–28秒滑窗常有100/50候选。可以用100作人工核对的起点，不能把不存在的HF beat数组填成“检测拍点”。',structure:'4.5、10.5秒统计音色分界；10.5、15.5、24.25秒存在响度抬升；28.75秒附近明显收尾衰减。',study:'从10.5秒后试听并手打拍；先用10.163/14.693/19.033/21.629秒强起音作为片段锚点，不宣称整首100 BPM。'},
 V08:{bpm:[140,70],confidence:'较高（本组稳定候选之一）',reason:'全7个8秒滑窗均约139.5–140.2；HF140、能量基线139.5、谱峰139.9互相接近，HF confidence0.504。仍有70半速记谱歧义。',structure:'13.315秒音色边界；13.75秒响度提升约8.2dB；此前2、4、6.75秒也逐步升高。31.5秒附近回落。',study:'以0.429秒一拍、0.214秒半拍练习；对照14.573/16.718/17.149秒密集起音，区分音乐拍和额外音效。'},
 V09:{bpm:[109.3,54.9,218.6],confidence:'低（短片、无通过门槛的稳定拍点）',reason:'HF confidence0.119并返回no steady beat；谱峰约55和109，能量基线95.2不同。218.6仅是109.3倍速假设；10.7秒片段不宜作曲速识别依据。',structure:'HF最短4秒分段未给出内部音色边界，不等于没有变化；4.75和6.5秒有响度上升，9.5秒显著衰减。',study:'按1.273/1.544/2.095/2.365/4.560/7.206秒起音手动比对画面；先复刻少量明确撞点，别追求机器给出全曲BPM。'},
 V10:{bpm:[80.1,160.2,40],confidence:'较高（本组最易建立节拍骨架）',reason:'HF80.1、能量基线80、4秒后滑窗均80；谱峰40、80、160都是同族倍半速。HF confidence0.657为本组最高，仍不代表人工确认100%正确。',structure:'5.755秒音色边界，与5.75秒前后约6.4dB响度抬升一致；4.0秒前后有约4.9dB回落。',study:'以0.749秒一拍，0.375秒半拍建立网格；先练2–4镜头在0.751秒间隔起音上的切换，再添加画面速度/变形。'}
};
function nearest(time,list,key){if(!list.length)return null;let best=list[0];for(const x of list)if(Math.abs((key?x[key]:x)-time)<Math.abs((key?best[key]:best)-time))best=x;const t=key?best[key]:best;return {time:round(t),delta_ms:round((time-t)*1000),...(key?{strength:best.strength}:{})};}
const index=[];
let md='# 10条参考视频：本地音频节奏与强起音分析\n\n本轮实际执行了FFmpeg本地解码、HyperFrames 0.8.216信号分析与montage 0.4.1基线比较。**没有实际监听音轨、没有上传、没有装模型。** 以下BPM、起音、音色分段均为机器测量候选；不冒充曲名识别、听觉确认或成片复刻。\n\n音量大不等于节拍：RMS只描述电平；谱通量检测“频谱突然发生的新变化”，可能是鼓点，也可能是对白辅音、whoosh、碰撞或引擎声；DP跟拍才是对起音序列施加周期模型。三层数据在JSON里分开。\n\n|ID|解码音频时长|BPM候选|本次判断|HF内部confidence|\n|---|---:|---|---|---:|\n';
for(const id of Object.keys(notes)){
 const f=path.join(root,`${id}.json`),r=JSON.parse(fs.readFileSync(f,'utf8')),n=notes[id];
 r.interpretation=n;
 const visualFile=path.join(root,`../visuals/${id}/scene-candidates.json`);
 const visual=JSON.parse(fs.readFileSync(visualFile,'utf8'));
 const kept=[];for(const v of [...visual.candidates].sort((a,b)=>b.score-a.score))if(kept.every(q=>Math.abs(q.time-v.time)>.15)){kept.push(v);if(kept.length>=12)break;}
 const examples=kept.sort((a,b)=>a.time-b.time).map(v=>({visual_candidate_sec:round(v.time),scene_score:round(v.score),nearest_observed_spectral_onset:nearest(v.time,r.onset_events,'t'),nearest_inferred_beat:nearest(v.time,r.hyperframes.beats.times)}));
 r.visual_audio_candidates={method:'按视觉scene score从高到低选最多12个、相互间隔>150ms，然后才计算最近起音/推断beat距离，未按音频对齐好坏筛选。未将这些未清洗候选算命中率。',warning:'这些可包含闪白、形变、动作、镜头内运动；不是人工确认cut。delta_ms=视觉候选时间-音频事件时间，正数表示画面变化稍后。',examples};
 fs.writeFileSync(f,JSON.stringify(r,null,2));
 index.push({id,duration_sec:r.duration_sec,bpm_candidates:n.bpm,confidence:n.confidence,hf_bpm:r.hyperframes.tempo.value,hf_confidence:r.hyperframes.beats.confidence,beat_count:r.hyperframes.beats.times.length,strong_onset_examples:r.strong_onset_examples,structure_candidates:r.structure_candidates.spans,silence:r.silence_below_minus50dbfs_200ms,notes:n,file:`${id}.json`});
 md+=`|${id}|${r.duration_sec.toFixed(3)}s|${n.bpm.join(' / ')}|${n.confidence}|${r.hyperframes.beats.confidence}|\n`;
}
md+='\n“较高”只表示多种周期线索/滑窗相互一致，**不是验证后的音乐真BPM**。HF confidence是源码内部启发式指标，不是概率。V07/V09没有通过HF稳定节拍门槛，因此没有推断beat数组；不拿固定网格冒充检测结果。\n\n## 每条怎么读、怎么练\n\n';
for(const r of index){const n=r.notes;md+=`### ${r.id}\n\n- **候选与信度：** ${n.bpm.join(' / ')} BPM；${n.confidence}。${n.reason}\n- **结构：** ${n.structure}\n- **可观测强起音样本（秒）：** ${r.strong_onset_examples.map(o=>o.t.toFixed(3)).join('、')}。这些是谱变化峰，不是都标为音乐beat。\n- **练习：** ${n.study}\n`;
 if(r.silence.length)md+=`- **低电平区间：** ${r.silence.map(s=>`${s.start.toFixed(3)}–${s.end.toFixed(3)}s`).join('；')}（10ms RMS窗口、低于−50dBFS、至少200ms；不能由此认定素材完全无声）。\n`;
 const detailed=JSON.parse(fs.readFileSync(path.join(root,r.file),'utf8'));
 md+='\n按视觉强度选出的复核点（只用于定位，不算卡点命中率）：\n\n|视觉候选秒|scene score|最近谱起音秒 / 差值|最近推断beat秒 / 差值|\n|---:|---:|---|---|\n';
 for(const v of detailed.visual_audio_candidates.examples.slice(0,6)){const o=v.nearest_observed_spectral_onset,b=v.nearest_inferred_beat;md+=`|${v.visual_candidate_sec}|${v.scene_score}|${o?`${o.time} / ${o.delta_ms}ms`:'无'}|${b?`${b.time} / ${b.delta_ms}ms`:'未通过稳定beat检测'}|\n`;}
 md+='\n';
}
md+='## 方法与实际执行记录\n\n1. 从manifest.local.json按ID读取原MP4；每条带源SHA256。FFmpeg仅解码第一音轨为22050Hz/单声道/16bit PCM，写入本目录VXX.mono.wav，不修改原视频。\n2. 本机FFmpeg直接写工作目录曾返回Permission denied。已改用`-f wav pipe:1`返回二进制，由可写的Codex Node runtime保存Buffer；最终10条均exit 0。此修正不改系统权限。\n3. 直接导入本机HyperFrames 0.8.216的signal provider和频带分析库：谱通量起音、40–240BPM自相关/DP、4秒最短音色结构。直接调用signal provider，未进入可上传的best/API provider。\n4. 自写脚本复用HF频带，去局部均值后列自相关峰；8秒滑窗/4秒步长交叉检查。候选峰包括长节奏型及倍半速，不自动认定全部为曲速。\n5. montage基线使用log-RMS正差，覆盖能量起伏；其结果和谱法不一致时明确保留冲突。\n6. `scene-candidates.json`来自320×180/阈值>0.10的未清洗变化候选。这里只提供按视觉分数独立选出的复核例子，不计算“卡点命中率”，不把闪白/动作误报当cut。\n\n可复跑（以下均使用本机已存在工具，参数说明在脚本中）：\n\n```powershell\n$audioNode = "C:\\Users\\PC\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\bin\\node.exe"\n& $audioNode .\\work\\reference-reverse\\audio\\analyze-audio.mjs\n& $audioNode .\\work\\reference-reverse\\audio\\summarize-audio.mjs\n```\n\n`analyze-audio.mjs`会从原MP4重新生成音频与JSON；`summarize-audio.mjs`增加中文判断和视觉复核点。操作参数、退出码和源路径仅在本地operations.local.json；每条JSON保留工具源文件hash。VXX.json的beats与onsets分开，onsets是检测到的频谱起音候选，beats含周期模型插入/平滑的推断。\n\nAAC解码出的音频长度与容器视频长度可能相差几十毫秒，本轮V01/V02/V05/V08/V09均如此。此处所有时间从解码音频0秒计，原素材未加偏移；用于逐帧复刻时应结合音视频PTS、播放器试听与30/25/24fps帧边界检查，不能把毫秒小数当真实感知精度。\n\n## 学习顺序（仅指音频骨架，不是整条视觉复刻难度）\n\n先V10（80/160稳定、短片）→V04（124/62清晰，练分段起势）→V08/V01（140稳定，开始区分拍与额外音效）→V02/V03（段落与细分歧义）→V07/V09（拒绝强行出beat，练手工锚点）→V05（多算法冲突）→V06（130秒长片、多段与静音重入，必须分段）。完整难度还取决于视觉遮罩、素材动作衔接、速度曲线与关键帧，不能从BPM单独排行。\n';
fs.writeFileSync(path.join(root,'index.json'),JSON.stringify(index,null,2));
fs.writeFileSync(path.join(root,'summary.md'),md);
console.log(JSON.stringify({files:index.length,summary:'summary.md',index:'index.json',silences:index.map(r=>({id:r.id,spans:r.silence}))}));
