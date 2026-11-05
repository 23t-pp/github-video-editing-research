const fs = require('fs');
const path = require('path');
const base = process.cwd();
const out = path.join(base, 'outputs', 'github-video-editing-research');
const read = p => JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const generatedFiles=[];
const put = (p,v) => { generatedFiles.push({path:p,content:typeof v==='string'?v:JSON.stringify(v,null,2)+'\n'}); };
const clean = s => s.replace(/C:[\\/]Users[\\/]PC[\\/]\.codex[\\/]skills[\\/]video-shotcraft/gi,'本机已安装的 video-shotcraft skill')
 .replace(/D:[\\/]gpt[\\/][^\s`"<>|)]+/gi,'[本机工作路径已脱敏]')
 .replace(/C:[\\/]Users[\\/]PC[^\s`"<>|)]+/gi,'[本机用户路径已脱敏]')
 .replaceAll('实测beat grid','音轨检测生成的beat map（本次未运行）').replaceAll('按实测beats插值','按音轨检测生成的beats插值（本次未运行）');
const groups = [
 {key:'orchestrator',label:'主流程补漏',log:'searches.json'},
 {key:'beat_montage',label:'音乐卡点',log:'search-log.json',review:'beat-montage'},
 {key:'editable_templates',label:'可换素材模板',log:'searches.json',review:'editable-templates'},
 {key:'ai_editing',label:'AI剪辑',log:'searches.json',review:'ai-editing'}
];
let queries=[], occurrences=[], reviews=[];
for (const g of groups) {
 const folder=path.join(base,'work',g.key);
 const logs=read(path.join(folder,g.log));
 logs.forEach((q,i)=>{
   const filename=q.raw_file.replace(/\\/g,'/').split('/').pop();
   const raw=read(path.join(folder,filename));
   const id=g.key+'-'+String(i+1).padStart(2,'0');
   const dest='evidence/search/raw/'+id+'.json';
   put(dest,raw);
   const entry={id,branch:g.label,query:q.query,count:raw.items.length,total_count:raw.total_count,incomplete_results:raw.incomplete_results,
     retrieved_at:q.retrieved_at||q.timestamp||null,retrieved_date:'2026-11-04',raw_file:dest,per_page:30,page:1};
   queries.push(entry);
   for(const repo of raw.items) occurrences.push({repo,query_id:id});
 });
 if(g.review) {
   let r=JSON.parse(clean(JSON.stringify(read(path.join(folder,'review.json')))));
   r.searches=queries.filter(q=>q.id.startsWith(g.key+'-'));
   r.candidates_file='../catalog.json';
   r.research_branch=g.label;
   if(g.key==='editable_templates') {
     const v=r.shortlisted.find(x=>x.repo==='actionow-ai/vvv');
     v.evidence.push({claim:'补充交叉复核：音频检测生成beat map的脚本',path:'kits/remotion/scripts/analyze-music.mjs',url:`https://github.com/actionow-ai/vvv/blob/${v.sha}/kits/remotion/scripts/analyze-music.mjs`,detail:'静态读取确认FFmpeg解码、谱通量起音、自相关tempo和DP beats；本轮未执行。'});
   }
   put('evidence/reviews/'+g.review+'.json',r);
   let md=clean(fs.readFileSync(path.join(folder,'review.md'),'utf8'));
   md=md.replace(/\]\(search[-_](\d+)\.json\)/g,(_,n)=>`](../evidence/search/raw/${g.key}-${String(Number(n)).padStart(2,'0')}.json)`);
   put('reviews/'+g.review+'.md',`> 返回[研究首页](../README.md) · [全部查询和原始响应](../evidence/search/queries.json) · [结构化审查](../evidence/reviews/${g.review}.json)\n\n`+md);
   reviews.push(r);
 }
}
const rootInfo = (repo)=>read(path.join(base,'work','orchestrator',repo.replace('/','__'),'metadata.json'));
const rootSha = repo=>read(path.join(base,'work','orchestrator',repo.replace('/','__'),'commit.json')).sha;
const makeRoot = (repo,body)=> {
 const m=rootInfo(repo),sha=rootSha(repo);
 return {repo,url:m.html_url,stars:m.stargazers_count,pushed_at:m.pushed_at,sha,archived:m.archived,...body,
   evidence:body.evidence.map(e=>({...e,url:`https://github.com/${repo}/blob/${sha}/${e.path}`}))};
};
const rootReview = {research_branch:'主流程：官方示例与已有能力',reviewed_at:'2026-11-04',method:'GitHub CLI元数据、固定SHA、目录、README、LICENSE、模板源码静态核查；另对本机已有提交做只读比较。',shortlisted:[
 makeRoot('heygen-com/hyperframes',{
   category:'HTML视频引擎与可编辑组件目录',is_template:true,license:'Apache-2.0；依赖及媒体另看各自条款',
   beat_capability:'抽查beat-freeze-cut使用CONFIG.beat1/beat2等显式时间；beat-timeline用interval均匀排标签。两个组件不构成自动音频检测器。',
   dependencies:'Node、Chrome/浏览器渲染与FFmpeg；按项目选择匹配版本。',windows:'README提供Windows桌面入口；本次未新安装或渲染。',
   limitations:['引擎、组件和完整模板不是同一层；不能把catalog条目数当作自动混剪软件数。','本机已有旧版工具依赖，不能为搜新模板而统一覆盖。'],
   recommendation:'沿用已存在的生态，按所需字效/转场挑组件；用于补视觉层。',
   evidence:[{claim:'框架定位与本地渲染',path:'README.md',detail:'描述HTML/CSS/媒体与seekable animation导出视频；catalog为可编辑源码。'},
   {claim:'固定beat时间的冻帧切换组件',path:'docs/catalog/blocks/beat-freeze-cut.mdx',detail:'嵌入实现包含CONFIG、beat1/beat2、GSAP paused timeline；不是音频检测。'},
   {claim:'均匀interval节奏行组件',path:'docs/catalog/components/beat-timeline.mdx',detail:'参数beatCount、interval、labels决定时间标签。'}]
 }),
 makeRoot('heygen-com/hyperframes-launches',{
   category:'官方实际发布片源码与4个可换品牌成品模板',is_template:true,license:'原创代码/配置/文档Apache-2.0；媒体、字体、商标不包含在同一授权内',
   beat_capability:'heygen-apple-motion是预设帧时序与动效，README写模板无音轨；不是自动听歌卡点。',
   dependencies:'所审01-ui-sting用npx hyperframes@0.7.94；素材有Git LFS，部分字体另有许可。',windows:'Node/CLI有跨平台基础，具体样片未在本机运行。',
   limitations:['模板偏产品/UI发布片，改电影混剪需另建镜头结构。','换品牌同时替换相应素材与字体；不是下载即自动适配任意内容。'],
   recommendation:'纯动效模板的可靠学习来源，优先看01-ui-sting与04-generate-reel。',
   evidence:[{claim:'四个独立可换品牌模板',path:'heygen-apple-motion/README.md',detail:'列01-ui-sting、02-bouncy-ui、03-message-sting、04-generate-reel，给出各自规格。'},
   {claim:'可实际编辑的单HTML工程',path:'heygen-apple-motion/01-ui-sting/index.html',detail:'有实际结构与按帧动效，可保留动作替换图文。'},
   {claim:'明确预览、检查、渲染命令和版本',path:'heygen-apple-motion/01-ui-sting/package.json',detail:'dev/check/render脚本均固定hyperframes@0.7.94。'},
   {claim:'代码和媒体授权边界',path:'README.md',detail:'License节将原创源码与媒体/字体/商标区分。'}]
 }),
 makeRoot('nateherkai/herk-edit-kit',{
   category:'本机已有的口播剪辑技能、动效卡与starter',is_template:true,license:'LICENSE主体MIT；AIS品牌素材不包含在复用授权内；API为NOASSERTION',
   beat_capability:'抽查motion-showreel/beatgrid.mjs接受--period或--bpm生成章节切点；此脚本本身不检测音频，其余分析功能不在本次源码深审范围。',
   dependencies:'Node>=22；包内HyperFrames0.7.109、GSAP3.14.2；转写等按需依赖。',windows:'本机已有此提交与Windows适配技能；本次未重新渲染。',
   limitations:['406张卡在README中标draft，不能声称全部经过实际渲染质量验证。','品牌示例需换成自己的素材；不同项目的HyperFrames版本要隔离。'],
   recommendation:'已安装且提交相同，优先复用现有starter/style-library；不作为新装工具重复推荐。',
   evidence:[{claim:'starter、draft卡与模板范围',path:'README.md',detail:'15技能、406 draft卡、两套场景模板和无API素材的合成starter。'},
   {claim:'许可不能只读API自动识别值',path:'LICENSE',detail:'MIT主体后有品牌资产排除说明。'},
   {claim:'固定BPM章节规划器',path:'.agents/skills/motion-showreel/scripts/beatgrid.mjs',detail:'从period或60/bpm计算网格，不读取音乐波形。'},
   {claim:'固定版本依赖',path:'package.json',detail:'HyperFrames0.7.109，GSAP3.14.2，Node>=22。'}]
 })
],excluded:[
 {repo:'heygen-com/hyperframes-launch-video',reason:'单个早期官方实例，README称源码/媒体供reference use；不能直接继承框架Apache许可。更优先选许可边界清楚的launches合集。并未证明两仓代码完全重复。',evidence:`https://github.com/heygen-com/hyperframes-launch-video/blob/${rootSha('heygen-com/hyperframes-launch-video')}/README.md`},
 {repo:'zhuyansen/awesome-claude-video-skills',reason:'用作发现索引，非剪辑模板/引擎。其评级没有代替本轮源码审查。'},
 {repo:'JediKnightChan/EternalCrusadeResurrection',reason:'搜索元数据表明是Unreal游戏项目，montage同词异义；未源码深审。'},
 {repo:'xbb1973/USTC-ncov-AutoReport',reason:'搜索元数据表明是健康打卡脚本，“卡点”宽搜噪声；未源码深审。'}
],dedup:[
 {repo:'nateherkai/herk-edit-kit',canonical:'nateherkai/herk-edit-kit',reason:'本机git HEAD与上游快照10511e5af86fc47756ea89803b397422e2d89284一致，作为已有能力计一次。'},
 {repo:'dsh-montage 本机三份包',canonical:'本机dsh-montage能力族',reason:'均标0.4.1但Windows启动适配有差异；仅按用途归类，不宣称文件完全相同。公开上游URL仍未确认。'}
]};
put('evidence/reviews/orchestrator.json',rootReview); reviews.push(rootReview);
const allReviewed=reviews.flatMap(r=>r.shortlisted||[]).map(r=>({...r,evidence_level:'E2 静态源码核查；未运行候选软件'}));
const excluded=reviews.flatMap(r=>(r.excluded||[]).map(x=>({...x,branch:r.research_branch})));
const dedup=reviews.flatMap(r=>(r.dedup||[]).map(x=>({...x,branch:r.research_branch})));
const byId=new Map();
for(const {repo:r,query_id} of occurrences){
 if(!byId.has(r.id)) byId.set(r.id,{id:r.id,repo:r.full_name,url:r.html_url,description:r.description,stars:r.stargazers_count,language:r.language,license_api:r.license?.spdx_id??null,pushed_at:r.pushed_at,archived:r.archived,fork:r.fork,topics:r.topics||[],query_ids:[],origin:'repository_search'});
 byId.get(r.id).query_ids.push(query_id);
}
const searchUnique=byId.size;
const metaPaths=[];
function scan(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,e.name);if(e.isDirectory()){if(!['files','source'].includes(e.name))scan(p);}else if(['meta.json','metadata.json'].includes(e.name))metaPaths.push(p);}}
for(const g of groups) scan(path.join(base,'work',g.key));
const metas=[];
for(const p of metaPaths){try{const m=read(p);if(m.id&&m.full_name){metas.push(m); if(!byId.has(m.id))byId.set(m.id,{id:m.id,repo:m.full_name,url:m.html_url,description:m.description,stars:m.stargazers_count,language:m.language,license_api:m.license?.spdx_id??null,pushed_at:m.pushed_at,archived:m.archived,fork:m.fork,topics:m.topics||[],query_ids:[],origin:'direct_repository_probe'});}}catch{}}
for(const r of byId.values()){
 const rev=allReviewed.find(x=>x.repo.toLowerCase()===r.repo.toLowerCase()); const ex=excluded.find(x=>x.repo.toLowerCase()===r.repo.toLowerCase());
 r.review_status=rev?'重点静态源码审查':ex?'明确排除或降级；见理由':'仅元数据召回；未源码深审';
 if(rev) {r.review_sha=rev.sha;r.category=rev.category;}
 if(ex) r.exclusion_reason=ex.reason;
}
const catalog=[...byId.values()].sort((a,b)=>a.repo.localeCompare(b.repo));
const snapshots=allReviewed.map(r=>{const m=metas.find(m=>m.full_name.toLowerCase()===r.repo.toLowerCase());return{repo:r.repo,id:m?.id??null,sha:r.sha,stars:r.stars,pushed_at:r.pushed_at,archived:m?.archived??false,license_api:m?.license?.spdx_id??null,license_review:r.license,evidence_level:r.evidence_level};});
const stats={research_date:'2026-11-04',timezone:'Asia/Shanghai',query_count:queries.length,retrieved_search_records:occurrences.length,unique_search_repositories:searchUnique,duplicate_search_occurrences:occurrences.length-searchUnique,direct_probe_additional_repositories:byId.size-searchUnique,catalog_repositories:catalog.length,focused_source_review_repositories:allReviewed.length,unique_excluded_or_downgraded: new Set(excluded.map(x=>x.repo.toLowerCase())).size,source_evidence_links:allReviewed.reduce((n,r)=>n+r.evidence.length,0),candidate_software_runtime_tests:0};
put('evidence/search/queries.json',queries); put('evidence/catalog.json',catalog); put('evidence/reviewed-projects.json',allReviewed);put('evidence/repository-snapshots.json',snapshots);put('evidence/exclusions.json',excluded);put('evidence/dedup-decisions.json',dedup);put('evidence/statistics.json',stats);
const escape = v=>String(v??'').replaceAll('|','\\|').replace(/\r?\n/g,' ');
let matrix='# 全部重点项目：按实际能力看，不按星数排名\n\n返回[研究首页](../README.md)。本表中的能力来自固定提交的静态源码/文档；没有安装或渲染这些候选软件。星数与push日期为本次快照，日期以ISO为准。详证在后面的分支报告与JSON中。\n\n';
matrix+='| 项目 | 定位 | 模板？ | 许可核查 | 星数 | 最近push（UTC） |\n|---|---|---|---|---:|---|\n';
for(const r of allReviewed) matrix+=`| [${r.repo}](${r.url}) | ${escape(r.category)} | ${r.is_template?'含模板/配置入口':'主要是工具/流程'} | ${escape(r.license)} | ${r.stars} | ${r.pushed_at.slice(0,10)} |\n`;
matrix+='\n## 逐项适用性与证据\n\n';
for(const r of allReviewed){ matrix+=`### ${r.repo}\n\n${r.recommendation}\n\n- 固定版本：\`${r.sha}\`。\n- 节拍能力：${escape(r.beat_capability)}\n- 依赖：${escape(Array.isArray(r.dependencies)?r.dependencies.join('；'):r.dependencies)}\n- Windows：${escape(r.windows)}\n- 限制：${escape(Array.isArray(r.limitations)?r.limitations.join('；'):r.limitations)}\n\n`;
 for(const e of r.evidence) matrix+=`- [${escape(e.claim||e.path||'源码证据')}](${e.url})：${escape(e.detail||'见固定提交文件。')}\n`;
 matrix+='\n'; }
put('docs/03-reviewed-catalog.md',matrix);
let cand='# 所有召回候选：不是推荐榜\n\n返回[研究首页](../README.md)。555个搜索唯一仓库与直接探查补充项都保留在这里。只有标为“重点静态源码审查”的项目有深入结论；其余不应视为已验证。完整字段与命中查询在[catalog.json](../evidence/catalog.json)。\n\n| 仓库 | 状态 | 召回方式 |\n|---|---|---|\n';
for(const r of catalog) cand+=`| [${r.repo}](${r.url}) | ${escape(r.review_status)} | ${r.query_ids.length? r.query_ids.join('、'):'指定仓库补漏'} |\n`;
put('docs/08-all-candidates.md',cand);
let dd='# 去重、降级与排除记录\n\n返回[研究首页](../README.md)。数字身份去重、来源归并、功能重叠和本机已有能力是不同概念。\n\n';
dd+=`## 可复算的身份去重\n\n${stats.query_count}条查询取回${stats.retrieved_search_records}条记录，按GitHub数字id合并后为${stats.unique_search_repositories}个仓库，去掉${stats.duplicate_search_occurrences}次重复命中。直接repo探查另增加${stats.direct_probe_additional_repositories}个身份，最终保留${stats.catalog_repositories}个仓库的资料。模板族归并没有随意改变这些身份统计。\n\n运行\`scripts/Merge-Candidates.ps1\`可离线复算搜索池。\n\n## 来源与模板族判断\n\n| 条目 | 归属/保留对象 | 判断与证据范围 |\n|---|---|---|\n`;
for(const x of dedup) dd+=`| ${escape(x.repo)} | ${escape(x.canonical)} | ${escape(x.reason)} |\n`;
dd+='\n## 排除、降级或暂不推荐\n\n有的条目只读过搜索元数据；有的读过源码后发现限制。以下理由明确写出证据深度，不能据此给项目做全面质量判决。\n\n| 项目 | 处理理由 |\n|---|---|\n';
for(const x of excluded) dd+=`| ${x.repo.includes('/')?`[${x.repo}](https://github.com/${x.repo})`:escape(x.repo)} | ${escape(x.reason)}${x.evidence?` [证据](${x.evidence})`:''} |\n`;
dd+='\n## 未逐个审查的项目\n\n其他候选保留为“仅元数据召回”，没有编造逐项淘汰理由，也没有把555个搜索命中说成555个已测试项目。\n';
put('docs/04-dedup-and-exclusions.md',dd);
let searches='# 搜索执行清单\n\n这是实际28条查询及其返回快照。每条只取一页30条；total_count是服务端匹配量，不是本次读取量。没有记录精确时刻的分支保留为当日，不补造时间。\n\n| ID | 查询 | 本页 | total_count | incomplete | 原始响应 |\n|---|---|---:|---:|---|---|\n';
for(const q of queries) searches+=`| ${q.id} | \`${escape(q.query)}\` | ${q.count} | ${q.total_count} | ${q.incomplete_results} | [JSON](../${q.raw_file}) |\n`;
put('docs/09-query-log.md',searches);
let ops=[];
for(const g of groups){let p=path.join(base,'work',g.key,'operations.json');if(fs.existsSync(p)){const v=read(p);ops.push({branch:g.label,operations:JSON.parse(clean(JSON.stringify(v)))});}}
if(ops.length) put('evidence/supplementary-cli-operations.json',ops);
process.stdout.write(JSON.stringify({stats,files:generatedFiles}));
