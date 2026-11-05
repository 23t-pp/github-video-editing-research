$ErrorActionPreference='Stop'
$gh='C:\Program Files\GitHub CLI\gh.exe'
$plan=[ordered]@{
 '0xsline/OpenChatCut'=@('src/audio/beats.ts','src/audio/intelligence/musicAnalysis.ts','src/agent/tools/music-intelligence-tools.ts','src/agent/tools/template-tools.ts','src/export/fcpxml.ts','shared/vector-inference-contract.ts')
 'Anil-matcha/AI-Youtube-Shorts-Generator'=@('shorts_generator/local/downloader.py','main.py')
 'harry0703/MoneyPrinterTurbo'=@('app/services/twelvelabs.py')
}
foreach($repo in $plan.Keys){
 $dir=Join-Path $PSScriptRoot ($repo -replace '/','--')
 $sha=(Get-Content (Join-Path $dir 'commit.json') -Raw|ConvertFrom-Json).sha
 $tree=(Get-Content (Join-Path $dir 'tree.json') -Raw|ConvertFrom-Json).tree
 foreach($path in $plan[$repo]){
  if($path -notin $tree.path){Write-Output "ABSENT $repo $path";continue}
  $obj=(& $gh api "repos/$repo/contents/${path}?ref=$sha" |ConvertFrom-Json)
  $target=Join-Path $dir ('source/'+$path)
  New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($target)) -Force|Out-Null
  [IO.File]::WriteAllText($target,[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($obj.content)),[Text.UTF8Encoding]::new($false))
  Write-Output "EXTRA $repo $path"
 }
}
$repo='0xsline/OpenChatCut'
$obj=(& $gh api "repos/$repo/git/blobs/63320846061599b77562a72e090c5980077e8fe4" |ConvertFrom-Json)
[IO.File]::WriteAllText((Join-Path $PSScriptRoot '0xsline--OpenChatCut/source/assets/templates/openchatcut-templates.json'),[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($obj.content)),[Text.UTF8Encoding]::new($false))
$core=[ordered]@{
 'modelscope/FunClip'='funclip/videoclipper.py';'WyattBlue/auto-editor'='src/editmethods.nim';'FujiwaraChoki/supoclip'='backend/src/ai.py';'Anil-matcha/AI-Youtube-Shorts-Generator'='shorts_generator/pipeline.py';'harry0703/MoneyPrinterTurbo'='app/services/video.py';'0xsline/OpenChatCut'='src/agent/tools/music-intelligence-tools.ts';'RayVentura/ShortGPT'='shortGPT/engine/content_short_engine.py';'poseljacob/agentic-video-editor'='src/tools/analyze.py'
}
$dates=@()
foreach($repo in $core.Keys){
 $raw=& $gh api --method GET "repos/$repo/commits" -f "path=$($core[$repo])" -f 'per_page=1'
 $dir=Join-Path $PSScriptRoot ($repo -replace '/','--')
 [IO.File]::WriteAllText((Join-Path $dir 'core-commits.json'),($raw -join "`n"),[Text.UTF8Encoding]::new($false))
 $c=@($raw|ConvertFrom-Json)[0]
 $dates+=[pscustomobject]@{repo=$repo;path=$core[$repo];sha=$c.sha;date=$c.commit.committer.date;message=$c.commit.message}
}
$dates|ConvertTo-Json -Depth 8|Set-Content (Join-Path $PSScriptRoot 'core-code-dates.json') -Encoding UTF8
$dates|Format-Table -Wrap
