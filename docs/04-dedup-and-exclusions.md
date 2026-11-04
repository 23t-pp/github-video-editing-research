# 去重、降级与排除记录

返回[研究首页](../README.md)。数字身份去重、来源归并、功能重叠和本机已有能力是不同概念。

## 可复算的身份去重

28条查询取回598条记录，按GitHub数字id合并后为555个仓库，去掉43次重复命中。直接repo探查另增加2个身份，最终保留557个仓库的资料。模板族归并没有随意改变这些身份统计。

运行`scripts/Merge-Candidates.ps1`可离线复算搜索池。

## 来源与模板族判断

| 条目 | 归属/保留对象 | 判断与证据范围 |
|---|---|---|
| scherroman/mugen | scherroman/mugen | 同仓库被扩展query重复召回：AMV generator |
| Vincentwei1021/video-shotcraft | Vincentwei1021/video-shotcraft | 同仓库被扩展query重复召回："beat-synced" |
| Moessif/code-video-showcase | Moessif/code-video-showcase | 同仓库被扩展query重复召回："beat-synced" |
| bestagentkits/motion-video-skill | bestagentkits/motion-video-skill | 同仓库被扩展query重复召回："beat-synced" |
| guigulaoshi/music-video-director-skill | guigulaoshi/music-video-director-skill | 同仓库被扩展query重复召回："beat-synced" |
| AbubakrChan/product-launch-motion | AbubakrChan/product-launch-motion | 同仓库被扩展query重复召回："beat-synced" |
| mfahsold/montage-ai | mfahsold/montage-ai | 同仓库被扩展query重复召回："beat-synced" |
| Merserk/BeatSync-Engine | Merserk/BeatSync-Engine | 同仓库被扩展query重复召回："beat-synced" |
| Meteor8/beats-synced-video-generator | Meteor8/beats-synced-video-generator | 同仓库被扩展query重复召回："beat-synced" |
| iart-ai/kinetic-typography-skills | iart-ai/kinetic-typography-skills | 同仓库被扩展query重复召回："beat-synced" |
| ZiadAbdelkarim/beat-synced-edit | ZiadAbdelkarim/beat-synced-edit | 同仓库被扩展query重复召回："beat-synced" |
| Win-Hao/knowledge-video | Win-Hao/knowledge-video | 同仓库被扩展query重复召回："beat-synced" |
| syklayou-glitch/video-shotcraft | syklayou-glitch/video-shotcraft | 同仓库被扩展query重复召回："beat-synced" |
| qingyunAGI/qingyun-cine-skill | qingyunAGI/qingyun-cine-skill | 同仓库被扩展query重复召回："beat-synced" |
| fltman/aimusicvideo | fltman/aimusicvideo | 同仓库被扩展query重复召回："beat-synced" |
| NSK-394/ai-video-agent | NSK-394/ai-video-agent | 同仓库被扩展query重复召回："beat-synced" |
| remotion-dev/template-audiogram | remotion-dev/remotion/packages/template-audiogram | README Contributing明示这是mirror；不要和monorepo重复计数。 |
| remotion-dev/template-tiktok | remotion-dev/remotion/packages/template-tiktok | 官方template family；本轮取得tree与metadata，family级归并，不能视作独立引擎。 |
| nexu-io/html-video:frame-warm-grain,frame-swiss-grid,frame-kinetic-type,frame-nyt-graph,frame-decision-tree,frame-play-mode,frame-product-promo,frame-vignelli | heygen-com/hyperframes/registry/examples | NOTICE说明direct forks、composition文件未变，仅目录布局变化。 |
| nexu-io/html-video:frame-product-promo-30s | nateherkai/hyperframes-student-kit/video-projects/linear-promo-30s | NOTICE明确保留30秒结构与SFX，替换品牌占位素材。 |
| JohnChow90/video-shotcraft | Vincentwei1021/video-shotcraft | 搜索元数据description写originally by Vincentwei1021；只采纳原作者仓库作为canonical，fork代码未深审。 |
| Vincentwei1021/video-shotcraft | 本机已有本机已安装的 video-shotcraft skill | 会话skill catalog已列同名skill；主代理负责实际内容同源核对，本子报告不声称逐字相同。 |
| lumian2015/opus-5-5-video-templates | 同仓库30个template family | 30种设计可单独选择，但工具数只计1，不膨胀为30独立软件。 |
| SamurAIGPT/AI-Youtube-Shorts-Generator | Anil-matcha/AI-Youtube-Shorts-Generator | gh api旧路径返回canonical full_name与同一repo id=821280833；是旧地址重定向，不计独立项目。 |
| Asad-Ismail/MoneyPrinterTurbo-Extended | harry0703/MoneyPrinterTurbo | 描述明确extended implementation，作为衍生家族记录，不重复计主实现。GitHub metadata fork=false，故不能声称是GitHub fork或逐文件相同；本次未做源码hash同源鉴定。 |
| modelscope/FunClip | modelscope/FunClip | 与其他访谈选段方案功能类似不等于同源；metadata fork=false，保留独立实现。 |
| nateherkai/herk-edit-kit | nateherkai/herk-edit-kit | 本机git HEAD与上游快照10511e5af86fc47756ea89803b397422e2d89284一致，作为已有能力计一次。 |
| dsh-montage 本机三份包 | 本机dsh-montage能力族 | 均标0.4.1但Windows启动适配有差异；仅按用途归类，不宣称文件完全相同。公开上游URL仍未确认。 |

## 排除、降级或暂不推荐

有的条目只读过搜索元数据；有的读过源码后发现限制。以下理由明确写出证据深度，不能据此给项目做全面质量判决。

| 项目 | 处理理由 |
|---|---|
| [Meteor8/beats-synced-video-generator](https://github.com/Meteor8/beats-synced-video-generator) | 2021年旧demo、无LICENSE；beat1.py确有librosa真实检测，但vid.py硬编码./beats/a1.csv、./video/1.mp4、./music/a.mp3，随机抽20–480秒源片且节拍截到0.1秒。可学最小原理，不适合当可换素材模板或现代工具。 [证据](https://github.com/Meteor8/beats-synced-video-generator/blob/436e2e27987240da57fbf5d947146cf6d3e13592/vid.py) |
| [Tanishk-11/BeatSync](https://github.com/Tanishk-11/BeatSync) | 描述为视频测心率健康应用，beat同词不同义，非音乐剪辑。 |
| [ialakey/music-video-generator](https://github.com/ialakey/music-video-generator) | 描述为单图+慢放混响+频谱可视化；未作源码审查，不列入真实切镜工具推荐。 |
| [riskcapital/ghost-arcade](https://github.com/riskcapital/ghost-arcade) | VJ/投影映射与live可视化，不是本组需要的素材切镜模板。 |
| [for-he-s-loved/awesome-beat-sync-video-editors](https://github.com/for-he-s-loved/awesome-beat-sync-video-editors) | 资源目录，非可运行剪辑器；可做补充索引但不能作为已审实现。 |
| [remotion-dev/template-audiogram](https://github.com/remotion-dev/template-audiogram) | 是真模板但偏播客字幕+音频波形，不是纯素材混剪；README明示mirror，应归并remotion-dev/remotion/packages/template-audiogram，许可要求公司license条件不能写MIT。 |
| [remotion-dev/template-helloworld](https://github.com/remotion-dev/template-helloworld) | React logo/文字入门模板；不具现成混剪素材结构，不作为成品混剪模板推荐。 |
| [remotion-dev/template-tiktok](https://github.com/remotion-dev/template-tiktok) | 真字幕视频模板但目标是转写/加字幕，非纯音乐蒙太奇；与Remotion monorepo同family。 |
| [2boysfromtown/hyperframes-motion](https://github.com/2boysfromtown/hyperframes-motion) | 确有4个1080×1920 GSAP HTML模板，MIT，非引擎；但README仅建议任意录屏/HTML转视频方法，仓库无export/render命令，无音轨卡点；降为手动动效素材备选，不列首选。 |
| [halicotampa-crypto/motion-pack](https://github.com/halicotampa-crypto/motion-pack) | 大型动效/skills混合pack，tree含student-kit及其HyperFrames skills拷贝；与本机已有技能/模板族重复风险高，本轮未逐个复核100+条，不把数量当独立成片模板数。 |
| [nateherkai/herk-edit-kit](https://github.com/nateherkai/herk-edit-kit) | 含完整工作流/样式库而非仅模板；主代理负责与本机edit-video/short-form-edit等同源核查，避免重复引入。 |
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | 基础引擎不作为模板本体计数；其registry/examples可在主代理官方模板审查中计入具体模板。 |
| [heygen-com/hyperframes-vercel-template](https://github.com/heygen-com/hyperframes-vercel-template) | 渲染服务/部署脚手架，不能以名字template当作已设计完成的视频成品模板。 |
| [renezander030/capcut-cli](https://github.com/renezander030/capcut-cli) | 草稿编辑CLI，不是现成成品模板；可作为cookbook外部依赖类工具另评估。 |
| [duoec/duo-video](https://github.com/duoec/duo-video) | Java剪映草稿SDK，不是成品混剪模板。 |
| [SoKeiKei/CapKit-download](https://github.com/SoKeiKei/CapKit-download) | 模板管理器/下载仓库，不等于可直接审查的开源模板。 |
| [VadooAI/ClipAnything](https://github.com/VadooAI/ClipAnything) | 种子仓库API请求返回Not Found；8条搜索中的ClipAnything专搜只召回提及它的榜单/其他项目，未核实官方可复用源码。不能把商业产品宣传页当开源实现。 |
| [gitroomhq/postiz-app](https://github.com/gitroomhq/postiz-app) | 高星但主要是社交媒体排期发布，非本次用户素材剪辑引擎。 |
| [QwenAudio/CosyVoice](https://github.com/QwenAudio/CosyVoice) | 语音生成模型；可作配音组件，不是现成用户素材剪辑方案。 |
| [MeiGen-AI/InfiniteTalk](https://github.com/MeiGen-AI/InfiniteTalk) | 语音驱动视频生成，目标是生成画面；非已有素材剪辑引擎。 |
| [yihui-dev/awesome-opus5-5-videos](https://github.com/yihui-dev/awesome-opus5-5-videos) | 视频展示与提示词收集；不能替代实际可复用剪辑实现。 |
| [21cncstudio/project_aura](https://github.com/21cncstudio/project_aura) | 空气质量ESP32项目，关键词噪声。 |
| [Anil-matcha/ai-clipping-comfyui](https://github.com/Anil-matcha/ai-clipping-comfyui) | 搜索description明确server-side经muapi.ai；可做服务节点封装候选，不作为完全本地开放高光引擎重复推荐。本次未深审其源码。 |
| [heygen-com/hyperframes-launch-video](https://github.com/heygen-com/hyperframes-launch-video) | 单个早期官方实例，README称源码/媒体供reference use；不能直接继承框架Apache许可。更优先选许可边界清楚的launches合集。并未证明两仓代码完全重复。 [证据](https://github.com/heygen-com/hyperframes-launch-video/blob/930f89186b8e155d632d9afe49054c02d4d7d85a/README.md) |
| [zhuyansen/awesome-claude-video-skills](https://github.com/zhuyansen/awesome-claude-video-skills) | 用作发现索引，非剪辑模板/引擎。其评级没有代替本轮源码审查。 |
| [JediKnightChan/EternalCrusadeResurrection](https://github.com/JediKnightChan/EternalCrusadeResurrection) | 搜索元数据表明是Unreal游戏项目，montage同词异义；未源码深审。 |
| [xbb1973/USTC-ncov-AutoReport](https://github.com/xbb1973/USTC-ncov-AutoReport) | 搜索元数据表明是健康打卡脚本，“卡点”宽搜噪声；未源码深审。 |

## 未逐个审查的项目

其他候选保留为“仅元数据召回”，没有编造逐项淘汰理由，也没有把555个搜索命中说成555个已测试项目。
