const fs = require('node:fs');
const path = require('node:path');
const root = __dirname;
const read = p => JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const draft = fs.readFileSync(path.join(root,'build_review.py'),'utf8');
// Read this report's own literal data; no downloaded source is executed.
let pos=0, source='';
function skip(){while(/\s/.test(source[pos]||'') && pos<source.length)pos++;}
function expect(c){skip();if(source[pos]!==c)throw Error(`Expected ${c} at ${pos}: ${source.slice(pos,pos+50)}`);pos++;}
function value(){
 skip();const c=source[pos];
 if(c==='\''||c==='"'){pos++;let out='';while(pos<source.length){let ch=source[pos++];if(ch===c)return out;if(ch==='\\'){const next=source[pos++];out+=({n:'\n',r:'\r',t:'\t'})[next]??next;}else out+=ch;}throw Error('string');}
 if(c==='['||c==='('){pos++;const end=c==='['?']':')';const out=[];skip();while(source[pos]!==end){out.push(value());skip();if(source[pos]===','){pos++;skip();}else if(source[pos]!==end)throw Error(`separator at ${pos}`);}pos++;return out;}
 if(source.startsWith('True',pos)){pos+=4;return true;}
 if(source.startsWith('False',pos)){pos+=5;return false;}
 if(source.startsWith('dict(',pos)){pos+=5;const out={};skip();while(source[pos]!==')'){const m=source.slice(pos).match(/^\w+/);if(!m)throw Error('dict key');pos+=m[0].length;expect('=');out[m[0]]=value();skip();if(source[pos]===','){pos++;skip();}}pos++;return out;}
 const number=source.slice(pos).match(/^\d+/);if(number){pos+=number[0].length;return Number(number[0]);}throw Error(`unknown at ${pos}: ${source.slice(pos,pos+50)}`);
}
const dates=Object.fromEntries(read('core-code-dates.json').map(d=>[d.repo,d]));
const records=[];
function add(repo,category,is_template,beat_capability,dependencies,windows,limitations,recommendation,audience,output, evidence){
 const dir=repo.replace('/','--'),meta=read(dir+'/metadata.json'),commit=read(dir+'/commit.json');
 const sha=commit.sha;
 const ev=evidence.map(([claim,p,line,detail])=>{
  const file=path.join(root,dir,'source',p);if(!fs.existsSync(file)||fs.statSync(file).size===0)throw Error('Missing '+file);
  if(line>fs.readFileSync(file,'utf8').split('\n').length)throw Error('Bad line '+p);
  return {claim,path:p,url:`https://github.com/${repo}/blob/${sha}/${p}#L${line}`,detail};
 });
 records.push({repo,url:meta.html_url,category,is_template,beat_capability,license:meta.license?.spdx_id,stars:meta.stargazers_count,pushed_at:meta.pushed_at,sha,sampled_core_commit:dates[repo],evidence:ev,dependencies,windows,limitations,recommendation,audience,output});
}
source=draft.slice(draft.indexOf("add('0xsline/OpenChatCut'"),draft.indexOf('\nexcluded ='));
while(pos<source.length){skip();if(pos===source.length)break;if(!source.startsWith('add(',pos))throw Error('add literal expected');pos+=3;add(...value());}
source=draft.slice(draft.indexOf('excluded =')+10,draft.indexOf('\ndedup ='));pos=0;const excluded=value();
source=draft.slice(draft.indexOf('dedup =')+7,draft.indexOf('\nsearches=read'));pos=0;const dedup=value();
const searches=read('searches.json'),candidates=read('candidates.json');
const summary={date:'2026-11-04',scope:'AI editing静态源码审查；8项目深审，未安装/启动仓库、未生成视频、未做效果测试',commands:['search.ps1','inspect.ps1','fetch-sources.ps1','fetch-extra.ps1'],search_calls:searches.length,returned_rows:searches.reduce((a,s)=>a+s.count,0),unique_search_candidates:candidates.length,seed_repositories:9,inspected_code_repositories:records.length};
const report={summary,searches,shortlisted:records,excluded,dedup};
const lines=['# AI自动剪辑与真实素材处理：静态源码核验','','**结论：** 同时想要AI参与、可继续改工程和音乐卡点，优先小样验证 OpenChatCut；中文长口播选段选 FunClip；快速去静音选 auto-editor；播客竖屏高光工作流看 SupoClip。MoneyPrinterTurbo与ShortGPT主要是文案/配音驱动素材合成，不能因为星多就当音乐混剪或自动挑原片高光。','','> 审查日期2026-11-04。此报告只读GitHub元数据、README、目录树与固定提交源码；没有安装、执行仓库代码或验证成片效果。“有实现”表示源码路径存在，不表示运行成功或剪辑质量过关。','','## 一屏对比','','| 项目 | 实际定位 | 音乐卡点证据 | 模板/可改工程 | 许可 | 当次星数 |','|---|---|---|---|---|---|'];
const shortBeat={'0xsline/OpenChatCut':'有真实拍点分析→时间线切分','modelscope/FunClip':'未发现','WyattBlue/auto-editor':'按响度阈值，非拍点','FujiwaraChoki/supoclip':'转录高光，未发现拍点','Anil-matcha/AI-Youtube-Shorts-Generator':'转录高光，未发现拍点','poseljacob/agentic-video-editor':'风格/混音，未发现拍点','harry0703/MoneyPrinterTurbo':'固定时长分段铺配音','RayVentura/ShortGPT':'随机背景+音乐循环'};
for(const r of records)lines.push(`| [${r.repo}](${r.url}) | ${r.category} | ${shortBeat[r.repo]} | ${r.is_template?'有复用入口，详见下文':'以剪辑参数/区间为主'} | ${r.license} | ${r.stars.toLocaleString('en-US')} |`);
lines.push('','读表：给片子加BGM、字幕跟随语音、让LLM写“有节奏”不满足真实音乐卡点证据标准。“模板”要区分确定性素材槽位、可编辑工程和给LLM看的风格提示；三者的可控程度不同。','','## 已执行的命令行处理流程','','通过已登录GitHub CLI访问公开API，没有安装第三方代码。实际入口：`search.ps1`、`inspect.ps1`、`fetch-sources.ps1`、`fetch-extra.ps1`。下面是执行过的命令模式；SHA占位表示应填入commit API返回值，实际脚本使用40位SHA。','','```powershell',"$gh = 'C:\\Program Files\\GitHub CLI\\gh.exe'",'& $gh api rate_limit --jq .resources.search',"& $gh api --method GET search/repositories -f 'q=\"automatic video editing\" in:name,description,readme stars:>20' -f per_page=30 -f sort=stars",'& $gh api repos/modelscope/FunClip','& $gh api repos/modelscope/FunClip/commits/main','& $gh api "repos/modelscope/FunClip/git/trees/<sha>?recursive=1"','& $gh api "repos/modelscope/FunClip/contents/funclip/videoclipper.py?ref=<sha>"','# contents响应是base64；用Convert.FromBase64String还原为文本，只读、不导入运行','& $gh api --method GET repos/modelscope/FunClip/commits -f path=funclip/videoclipper.py -f per_page=1','rg -n "subclip|concatenate|write_videofile|AutoModel" <本地审查源文件>','```','',`本分支8条repo search返回${summary.returned_rows}行，按full_name去重后${summary.unique_search_candidates}个候选；另探测9个种子路径，其中ClipAnything路径未找到，8个项目读取了实现代码。每条最多30项，非全GitHub穷尽；count是实际取回行数，total_count是GitHub报告的总匹配数。`,'','| 实际query | 取回/总匹配 | 原始文件 |','|---|---:|---|');
for(const s of searches)lines.push(`| \`${s.query}\` | ${s.count}/${s.total_count} | [${s.raw_file}](${s.raw_file}) |`);
lines.push('','实现核验顺序：搜仓库→去重与种子补漏→读README→看目录树找核心入口→固定SHA读取源码→检索真实解码/区间/节拍/渲染调用→核对依赖与Windows分支→记录限制。README只宣称但没有调用证据的能力，不标为已核实。','', '`pushed_at`只是仓库最后push，不保证是核心代码更新；下方还给一条抽查核心文件的最近提交。这个抽样日期不是整个仓库最后代码更新的全量证明。','','## 逐项源码证据与适用人群','');
for(const r of records){const d=r.sampled_core_commit;
 lines.push(`### ${r.repo}`,'',`**定位：** ${r.category}。**推荐判断：** ${r.recommendation}`,'',`**适合谁：** ${r.audience}`,'',`**卡点核验：** ${r.beat_capability}`,'',`**产物与复用入口：** ${r.output}`,'',`**依赖/费用/模型：** ${r.dependencies}`,'',`**Windows：** ${r.windows}`,'',`**维护记录：** 仓库push \`${r.pushed_at}\`；抽查 \`${d.path}\` 最近提交 \`${d.date}\`。审查快照 \`${r.sha}\`。`,'','**固定提交源码证据：**','');
 for(const e of r.evidence)lines.push(`- [${e.claim}](${e.url})：${e.detail}`);
 lines.push('','**限制：**','',...r.limitations.map(s=>'- '+s),'');
}
lines.push('## 淘汰与去重记录','',...excluded.map(r=>`- **${r.repo}**：${r.reason}`),'','下列是重定向/衍生家族处理，不把功能类似直接认定同源：','',...dedup.map(r=>`- **${r.repo} → ${r.canonical}**：${r.reason}`),'','## 零基础下一步：最小验证怎么做','','以下是选型后的**建议操作，未在本轮执行**。先用20至60秒的小素材，不以静态核验替代实际试剪。','','1. 去静音：从auto-editor官方Releases取Windows exe，先看`--help`，再试`auto-editor.exe input.mp4 --export resolve`，检查间隙是否伤到尾音。当前不要照旧教程用pip装CLI。','2. 中文口播：FunClip独立Python环境→转录→复制文字剪一段→对照原片检查字幕与切点→再加LLM高光。手选转录路径无需LLM账单。','3. 音乐混剪+可改工程：OpenChatCut导入少量素材与音乐，`analyze_music`看拍点，再`music_edit_plan`审计划，最后`sync_cuts_to_music`切分。这些是app/agent工具名，不能直接当PowerShell命令。听节奏并检查动作衔接，再换音乐复验。','4. 批量竖屏：SupoClip先Docker跑一条任务，确认用AssemblyAI还是`TRANSCRIPTION_PROVIDER=whisper`，以及云LLM还是Ollama，核对实际API调用和字幕成片。','5. 多段产品素材做广告：agentic-video-editor以`ave edit --footage-dir ./footage --brief brief.json`为入口；先读footage_index和EditPlan，再看MP4。YAML风格只是模型指导，需要看它是否真正执行。','','验收同时看：选段是否正确、剪点是否切断台词/动作、音乐切点是否命中、竖屏是否裁掉主体、字幕是否对时、修改素材能否重渲染。没有运行验收，只能称静态候选。','','学习顺序：auto-editor规则区间/工程导出→FunClip转录时间戳→agentic-video-editor镜头索引/EditPlan→OpenChatCut音乐分析、时间线、模板、agent工具整合。','');
process.stdout.write(JSON.stringify({report,markdown:lines.join('\n')}));
