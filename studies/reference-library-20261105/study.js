const $=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const study=await fetch('data/study.json').then(r=>r.json());
let music=await fetch('data/audio/music-index.json').then(r=>r.ok?r.json():[]).catch(()=>[]);if(!Array.isArray(music))music=music.items??music.tracks??[];
let available=null;try{available=(await fetch('/health').then(r=>r.json())).availableIds;}catch{}
const s=study.summary;$('stats').innerHTML=[[s.videos,'条参考视频'],[s.nativeFrames.toLocaleString(),'张原生帧'],[s.atlasPages,'页连续帧图谱'],[s.learningChapters,'个学习分段']].map(([n,t])=>`<div class="stat"><strong>${n}</strong><span>${t}</span></div>`).join('');
let current,pts=[],page=0,samplePage=-1,selectedTab='review',revision=0;
function list(){const q=$('search').value.toLowerCase();$('list').innerHTML=study.items.filter(x=>JSON.stringify([x.id,x.name,x.review.title,x.review.summary,x.review.techniques]).toLowerCase().includes(q)).map(x=>`<button class="ref ${current?.id===x.id?'selected':''}" data-id="${x.id}"><small>${x.id} · ${x.fpsValue} fps · ${x.duration.toFixed(2)}s · ${esc(x.review.difficulty)}</small><strong>${esc(x.review.title)}</strong></button>`).join('');$('list').querySelectorAll('button').forEach(b=>b.onclick=()=>select(b.dataset.id));}
function seek(t){$('video').currentTime=t;document.querySelector('[data-tab="review"]').click();}
function showPage(n){page=Math.min(Math.max(n,0),current.frameAnalysis.pages.length-1);const p=current.frameAnalysis.pages[page],url=`evidence/${current.id}/${p.file}`;$('page').value=page;$('atlas').src=url;$('atlas-open').href=url;$('atlas-link').href=url;$('page-info').textContent=`F${p.firstFrame}–F${p.lastFrame} · ${p.start.toFixed(6)}–${p.end.toFixed(6)} 秒 · 本页 ${p.count} 张原帧 · 源 ${current.fpsValue}fps`;$('frame').value=p.firstFrame;frameLabel();}
function frameLabel(){const n=Math.min(Math.max(Number($('frame').value)||0,0),current.frameAnalysis.nativeFrameCount-1);$('frame').value=n;$('frame-pts').textContent=pts[n]?`F${n} · PTS ${pts[n].pts.toFixed(6)}s`:'';return n;}
function loadFrame(){const n=frameLabel(),saved=current.frameAnalysis.nativeJpgDirectory;$('full-frame').src=saved?`${saved}/F${String(n).padStart(4,'0')}.jpg`:`/frame/${current.id}/${n}.jpg`;$('full-frame').alt=`${current.id} F${n} 原尺寸JPEG证据帧`}
function switchTab(name){
 selectedTab=name;
 for(const tab of document.querySelectorAll('[data-tab]')){
  const active=tab.dataset.tab===name;
  tab.classList.toggle('active',active);
  tab.setAttribute('aria-selected',active);
 }
 for(const panel of document.querySelectorAll('.panel'))panel.hidden=panel.id!==name;
}
function showSample(n){
 const sampling=current.sampling60Hz;
 n=Math.min(Math.max(Math.trunc(n)||0,0),sampling.sampleCount-1);
 const nextPage=sampling.pages.findIndex(p=>n>=p.firstFrame&&n<=p.lastFrame);
 if(nextPage!==samplePage){
  samplePage=nextPage;
  const p=sampling.pages[samplePage],url=`evidence/${current.id}/${p.file}`;
  $('sample-page').value=samplePage;
  $('sample-atlas').src=url;
  $('sample-atlas-open').href=url;
  $('sample-atlas-link').href=url;
  $('sample-page-info').textContent=`S${p.firstFrame}–S${p.lastFrame} · ${p.start.toFixed(6)}–${p.end.toFixed(6)} 秒 · 本页 ${p.count} 个样本`;
  $('prev-sample-page').disabled=samplePage===0;
  $('next-sample-page').disabled=samplePage===sampling.pages.length-1;
 }
 const sampleId=`S${String(n).padStart(7,'0')}`;
 const nativeFrame=Math.floor(n*current.fpsValue/sampling.sampleRate);
 const repeated=n>nativeFrame*sampling.sampleRate/current.fpsValue;
 const sourceTime=pts[nativeFrame]?.pts;
 $('sample').value=n;
 $('sample-image').href=`${sampling.sampleDirectory}/${sampleId}.jpg`;
 $('prev-sample').disabled=n===0;
 $('next-sample').disabled=n===sampling.sampleCount-1;
 $('sample-info').textContent=`${sampleId} · 采样时间 ${(n/sampling.sampleRate).toFixed(6)}s → 原帧 F${nativeFrame}${sourceTime===undefined?'':` · 源 PTS ${sourceTime.toFixed(6)}s`} · ${repeated?'沿用上一样本的原帧':'此原帧的首个样本'}`;
 return nativeFrame;
}
function showSamplePage(index){
 const p=current.sampling60Hz.pages[index];
 if(p)showSample(p.firstFrame);
}
function samplePanel(x){
 const sampling=x.sampling60Hz;
 document.querySelector('[data-tab="samples"]').hidden=!sampling;
 if(!sampling){
  if(selectedTab==='samples')switchTab('frames');
  return;
 }
 $('sample-coverage').textContent=`按 ${sampling.sampleRate}Hz 时间网格覆盖 ${sampling.sampleCount} 个采样位置。源视频为 ${x.fpsValue}fps，共 ${x.frameAnalysis.nativeFrameCount} 张原帧。每张原帧用于两个相邻样本，未做插帧。图谱中的 N 是原帧序号，= 标记沿用上一样本的原帧。`;
 $('sample-csv').href=sampling.mappingCsv;
 $('sample-page').innerHTML=sampling.pages.map((p,i)=>`<option value="${i}">${i+1} / ${sampling.pages.length}</option>`).join('');
 $('sample').max=sampling.sampleCount-1;
 samplePage=-1;
 showSamplePage(0);
}
function audioSource(id,link,p){const a=$(id),l=$(link);a.pause();if(p){a.src=p;l.href=p;l.hidden=false;a.hidden=false;}else{a.removeAttribute('src');a.load();a.hidden=true;l.hidden=true;}}
function musicPanel(x){const m=music.find(m=>m.id===x.id),mix=m?.mix_path??`audio/mixed/${x.id}__mixed.m4a`,candidate=m?.no_vocals_candidate_path??m?.music_candidate_path;
 audioSource('mix','mix-link',mix);audioSource('instrumental','instrumental-link',candidate);$('candidate-state').textContent=candidate?'已生成。未经人工听辨验收；残留对白、音效和伪影需自行试听。':'候选文件尚未生成，或当前下载包未包含音频。';
 const a=x.audio,n=a.rms.length,points=a.rms.map((r,i)=>`${i/Math.max(1,n-1)*1000},${145-Math.max(0,Math.min(1,(r.dbFS+60)/60))*130}`).join(' ');$('wave').innerHTML=`<polyline points="0,150 ${points} 1000,150" fill="#b9ee9230" stroke="#b9ee92" stroke-width="1.5"/>`;
 $('tempo').textContent=`模型速度候选 ${a.tempoCandidate??'未知'} BPM · 拍点置信度 ${a.beatConfidence??'未知'}。半速/倍速、变速与对白干扰均可能存在，不代表已锁定音乐BPM。`;
 const events=x.sync.humanVisualEvents.length?x.sync.humanVisualEvents:x.sync.machineCandidates;
 $('sync').innerHTML=`<p class="small">${x.sync.humanVisualEvents.length?'下列视觉事件经过人工图谱查看。':'本片表中为机器变化候选，也可能是闪光或大幅运动。'}与最近声音起音的距离只用于定位复听，正值表示视觉晚于起音。</p><table><thead><tr><th>帧 / 时间</th><th>视觉事件</th><th>最近起音差</th><th>模型拍点差</th></tr></thead><tbody>${events.slice(0,18).map(e=>`<tr><td>F${e.frame}<br>${e.time.toFixed(3)}s</td><td>${esc(e.claim??e.kind)}</td><td>${e.onsetDeltaMs??'—'}ms</td><td>${e.beatDeltaMs??'—'}ms</td></tr>`).join('')}</tbody></table>`;$('audio-data').href=`data/audio/${x.id}.json`;
}
async function select(id){const rev=++revision;current=study.items.find(x=>x.id===id)??study.items[0];const x=current,r=x.review;history.replaceState(null,'',`#${x.id}`);list();$('video').pause();$('id').textContent=x.id;$('title').textContent=r.title;$('format').textContent=`${x.width}×${x.height} · ${x.fpsValue}fps · ${x.frameAnalysis.nativeFrameCount}帧 · ${x.duration.toFixed(3)}s`;$('summary').textContent=r.summary;
 $('correction').hidden=!r.native_review;if(r.native_review)$('correction').textContent='本轮原帧复核：'+r.native_review.verifiedFinding;
 $('starter').textContent='建议第一步：'+r.starter;$('video').src=`/media/${x.id}`;$('video-state').textContent=available?.includes(x.id)?'已连接本地原视频。学习段是章节，不一定只含一个切镜。':'原视频未连接；图谱和报告仍可阅读。请启动本地服务并配置 local-media-paths.json。';
 $('segments').innerHTML=r.segments.map((e,i)=>`<section class="segment"><h3><span class="time" data-seek="${e.start}">${e.start.toFixed(3)}–${e.end.toFixed(3)}s</span>${esc(e.label)}</h3><p><b>看到什么：</b>${esc(e.observed)}</p><p class="recipe"><b>怎样练习：</b>${esc(e.recipe)}</p><p class="confidence">${esc(e.confidence)}</p><div class="evidence-links">${(e.evidence??[]).map(p=>`<a href="${esc(p)}" target="_blank">${esc(p.split('/').at(-1))} ↗</a>`).join('')}</div></section>`).join('');$('segments').querySelectorAll('[data-seek]').forEach(b=>b.onclick=()=>seek(Number(b.dataset.seek)));
 $('coverage').textContent=`机器解码/指标/图谱均覆盖 ${x.frameAnalysis.nativeFrameCount} 张原帧。`+(r.human_viewed?.scope_note??`本轮人工查看 ${x.humanAtlasPagesViewed}/${x.frameAnalysis.pages.length} 页原生帧缩略图，另查看全片总览和逐秒图谱；未宣称人工逐张精读全分辨率画面。`);
 $('page').innerHTML=x.frameAnalysis.pages.map((p,i)=>`<option value="${i}">${i+1} / ${x.frameAnalysis.pages.length}</option>`).join('');$('frame').max=x.frameAnalysis.nativeFrameCount-1;$('full-frame').removeAttribute('src');$('full-frame').alt='尚未读取当前视频的原尺寸帧';pts=[];showPage(0);samplePanel(x);musicPanel(x);
 const p=await fetch(`data/frame-analysis/${x.id}-pts.json`).then(r=>r.json());if(rev===revision){pts=p;frameLabel();if(x.sampling60Hz)showSample(Number($('sample').value));}
}
$('search').oninput=list;document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>switchTab(b.dataset.tab));
$('page').onchange=()=>showPage(Number($('page').value));$('prev-page').onclick=()=>showPage(page-1);$('next-page').onclick=()=>showPage(page+1);$('frame').onchange=frameLabel;$('load-frame').onclick=loadFrame;
$('prev-frame').onclick=()=>{$('frame').value=Number($('frame').value)-1;loadFrame()};$('next-frame').onclick=()=>{$('frame').value=Number($('frame').value)+1;loadFrame()};
$('sample-page').onchange=()=>showSamplePage(Number($('sample-page').value));
$('prev-sample-page').onclick=()=>showSamplePage(samplePage-1);
$('next-sample-page').onclick=()=>showSamplePage(samplePage+1);
$('sample').onchange=()=>showSample(Number($('sample').value));
$('prev-sample').onclick=()=>showSample(Number($('sample').value)-1);
$('next-sample').onclick=()=>showSample(Number($('sample').value)+1);
$('open-sample-source').onclick=()=>{
 const nativeFrame=showSample(Number($('sample').value));
 showPage(current.frameAnalysis.pages.findIndex(p=>nativeFrame>=p.firstFrame&&nativeFrame<=p.lastFrame));
 $('frame').value=nativeFrame;
 switchTab('frames');
 $('full-frame').closest('details').open=true;
 loadFrame();
 $('frame').focus();
};
$('wave').onclick=e=>{const r=$('wave').getBoundingClientRect();$('mix').currentTime=Math.max(0,Math.min(1,(e.clientX-r.left)/r.width))*current.duration};
for(const id of ['mix','instrumental','video'])$(id).onplay=()=>{for(const other of ['mix','instrumental','video'])if(other!==id)$(other).pause()};
$('full-frame').onerror=()=>{$('full-frame').alt='原帧读取失败。请检查本地原视频和FFmpeg配置；可先查看上方图谱。'};
await select(location.hash.slice(1)||'V05');
