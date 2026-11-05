$ErrorActionPreference = 'Stop'
$gh = 'C:\Program Files\GitHub CLI\gh.exe'
$repos = @('modelscope/FunClip','WyattBlue/auto-editor','FujiwaraChoki/supoclip','Anil-matcha/AI-Youtube-Shorts-Generator','harry0703/MoneyPrinterTurbo','0xsline/OpenChatCut','RayVentura/ShortGPT','VadooAI/ClipAnything','poseljacob/agentic-video-editor')
$seeds = @()
foreach ($repo in $repos) {
 $dir = Join-Path $PSScriptRoot ($repo -replace '/','--')
 New-Item -ItemType Directory -Path $dir -Force | Out-Null
 $raw = & $gh api "repos/$repo" 2>$null
 if ($LASTEXITCODE -ne 0) { Write-Output "MISSING $repo"; continue }
 [IO.File]::WriteAllText((Join-Path $dir 'metadata.json'), ($raw -join "`n"), [Text.UTF8Encoding]::new($false))
 $meta = $raw | ConvertFrom-Json
 $seeds += $meta
 $commit = & $gh api "repos/$repo/commits/$($meta.default_branch)"
 [IO.File]::WriteAllText((Join-Path $dir 'commit.json'), ($commit -join "`n"), [Text.UTF8Encoding]::new($false))
 $sha = ($commit | ConvertFrom-Json).sha
 $tree = & $gh api "repos/$repo/git/trees/${sha}?recursive=1"
 [IO.File]::WriteAllText((Join-Path $dir 'tree.json'), ($tree -join "`n"), [Text.UTF8Encoding]::new($false))
 $readme = & $gh api "repos/$repo/readme?ref=$sha"
 if ($LASTEXITCODE -eq 0) { $readObj = $readme | ConvertFrom-Json; [IO.File]::WriteAllText((Join-Path $dir 'README.md'),[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($readObj.content)),[Text.UTF8Encoding]::new($false)) }
 Write-Output "$repo | $($meta.stargazers_count) | $($meta.license.spdx_id) | $($meta.pushed_at) | $sha | fork=$($meta.fork) parent=$($meta.parent.full_name)"
}
$seeds | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'seeds.json') -Encoding UTF8
