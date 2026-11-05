$ErrorActionPreference='Stop'
$base=Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$r=Get-Content -LiteralPath (Join-Path $base 'anime-review.json') -Raw|ConvertFrom-Json
$md=[Collections.Generic.List[string]]::new()
function Add([string]$t=''){ $md.Add($t) }
Add '# 四条动画混剪：证据拆解与等效复现配方'
Add
Add 'V02/V05偏漫画拼贴与版式：大字、人物分离、卡片、三联、分屏。V03/V07偏前景接力：下一镜的手、袖口或武器先进入旧镜，遮挡后换底图。能复用的是这些结构；任意换两段素材并套统一转场，通常接不起来。'
Add
Add '|参考ID|时长 / 帧率|重点|难度|'
Add '|---|---|---|---|'
foreach($v in $r.videos){Add "|$($v.id)|$($v.duration)s / $($v.fps)fps|$($v.summary)|$($v.difficulty)|"}
Add
Add '## 看了哪些证据、哪些没有证明'
Add
Add $r.method.viewed
Add
Add $r.method.timing_precision
Add
Add $r.method.audio_boundary
Add
Add $r.method.attribution_boundary
Add
Add '本轮只使用REA的证据边界方法、shot-sequencing的动作衔接方法与montage的镜头/字/冲击层拆分。MP4不是软件包，没有对视频执行软件反编译。没有从文件名推断某个转场、软件或模板。'
Add
Add '以下“配方”是能做出相近视觉的实现方案，包含建议参数起点；不是恢复出的作者工程。所有时间均从源视频开头计，约数。'
foreach($v in $r.videos){
 Add;Add "## $($v.id)";Add
 Add $v.summary;Add
 Add "文字/字幕：$($v.text)";Add
 Add "源SHA-256：$($v.sha256)";Add
 Add "全片证据：[24格总览](visuals/$($v.id)/overview.jpg)、[0.5秒时间线第一页](visuals/$($v.id)/timeline-01.jpg)、[第二页](visuals/$($v.id)/timeline-02.jpg)。";Add
 foreach($s in $v.segments){
  Add "### 约$($s.range[0])–$($s.range[1])秒";Add
  Add "**可见事实：** $($s.observed)";Add
  Add "**能确认：** $($s.confirmed)";Add
  Add "**复现推测：** $($s.hypothesis)";Add
  Add "**与源动画区分：** $($s.source_animation_boundary)";Add
  Add '操作顺序：';Add
  $n=1;foreach($step in $s.recipe){Add "$n. $step";$n++};Add
  $links=@($s.evidence|ForEach-Object{$parts=$_ -split '@',2;$label=if($parts.Length -gt 1){$parts[1]+'秒'}else{$parts[0]};"[$label]($($parts[0]))"})
  Add "证据：$($links -join '；')。把握度：$($s.confidence)。";Add
 }
}
Add '## 四张最有代表性的密帧'
Add
Add 'V02：前景动作与背景排字独立；观察3.6–5.5秒，人物持续运动，大字依次替换和重复。'
Add
Add '![V02文字与人物分层](anime/V02-type-cutout-3.200.jpg)'
Add
Add 'V03：16.5–16.8秒袖口先出现在棋盘上，16.9秒后才换成蓝树林底图。'
Add
Add '![V03袖口先入再换底图](anime/V03-sleeve-wipe-15.400.jpg)'
Add
Add 'V05：1.8–2.2秒六格窗口逐步拼成下一镜，底下还保留上一镜伸掌。'
Add
Add '![V05六格卡片](anime/V05-panel-grid-1.500.jpg)'
Add
Add 'V07：26.7秒下一人物先出现在双指的三角区域内，26.9秒放大，27秒全幅替换。'
Add
Add '![V07双指门户](anime/V07-pink-portal-25.700.jpg)'
Add
Add '## 统一分层配方'
Add
Add '从底向上可采用以下轨道；具体效果会调整文字和局部窗口的前后顺序。'
Add
foreach($x in $r.shared_recipe.layer_order_bottom_to_top){Add "- $x"};Add
Add '最需要记录的参数：';Add
foreach($x in $r.shared_recipe.core_parameters){Add "- $x"};Add
Add '## 工具如何分工'
Add
Add '|工具|适合承担|还缺什么|'
Add '|---|---|---|'
foreach($x in $r.shared_recipe.implementation_options){Add "|$($x.tool)|$($x.fit)|$($x.gap)|"}
Add
Add $r.shared_recipe.template_reuse_boundary
Add
Add '建议练习顺序：';Add
$n=1;foreach($x in $r.shared_recipe.training_order){Add "$n. $x";$n++};Add
Add '## 跨片关系与避免误判'
Add
foreach($x in $r.cross_video_notes){Add "- $x"};Add
Add '画面中复杂的电光、火焰、粒子、三维手势、袖料、面部表演和摄影运动，通常应先从源动画镜头取得。缺少原片对照时，保留“原生/后加未知”，不要把所有能量效果都写成后期滤镜清单。'
Add
Add '## 本地复现证据采样'
Add
Add '原视频不变。运行脚本只读manifest所指的该视频，把本任务密帧写到anime子目录。';Add
Add '```powershell'
Add $r.reproducibility.example
Add '```'
Add
Add $r.reproducibility.technical_note
Add
Add $r.reproducibility.privacy
Add
Add 'JSON版本见[anime-review.json](anime-review.json)，包含28个时间段、分层顺序、工具边界和每段证据引用。密帧脚本见[extract-window.ps1](anime/extract-window.ps1)，每图旁同名JSON记录采样参数。'
$md|Set-Content -LiteralPath (Join-Path $base 'anime-review.md') -Encoding utf8
Write-Output "Wrote $base\anime-review.md"
