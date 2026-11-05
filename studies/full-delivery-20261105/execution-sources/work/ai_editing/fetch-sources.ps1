$ErrorActionPreference = 'Stop'
$gh = 'C:\Program Files\GitHub CLI\gh.exe'
$plan = [ordered]@{
 'modelscope/FunClip' = @('funclip/videoclipper.py','funclip/llm/openai_api.py','funclip/llm/twelvelabs_api.py','funclip/model_selection.py','requirements.txt','docs/installation.md','LICENSE')
 'WyattBlue/auto-editor' = @('src/analyze/audio.nim','src/editmethods.nim','src/exports/fcp7.nim','src/exports/json.nim','src/exports/otio.nim','docs/src/installing.md','ae.nimble','LICENSE')
 'FujiwaraChoki/supoclip' = @('backend/src/ai.py','backend/src/media/transcription.py','backend/src/config.py','backend/src/editor_document.py','backend/src/media/timeline.py','backend/src/caption_templates.py','backend/pyproject.toml','docs/configuration.md','LICENSE')
 'Anil-matcha/AI-Youtube-Shorts-Generator' = @('shorts_generator/pipeline.py','shorts_generator/highlights.py','shorts_generator/local/llm.py','shorts_generator/local/clipper.py','shorts_generator/local/transcriber.py','shorts_generator/config.py','requirements-local.txt','LICENSE')
 'harry0703/MoneyPrinterTurbo' = @('app/services/task.py','app/services/video.py','app/services/video_project.py','app/services/bgm.py','app/models/schema.py','requirements.txt','LICENSE')
 '0xsline/OpenChatCut' = @('desktop/native-rhythm-worker.ts','desktop/native-rhythm-service.ts','src/agent/tools/beat-tools.ts','src/agent/tools/schemas/beat-tools.ts','assets/templates/openchatcut-templates.json','src/agent/skills/beat-sync-montage/SKILL.md','cli/commands/export.ts','package.json','LICENSE')
 'RayVentura/ShortGPT' = @('shortGPT/engine/content_short_engine.py','shortGPT/engine/content_video_engine.py','shortGPT/editing_framework/editing_engine.py','shortGPT/editing_framework/editing_steps/background_music.json','shortGPT/editing_framework/editing_steps/add_background_video.json','requirements.txt','LICENSE')
 'poseljacob/agentic-video-editor' = @('src/tools/analyze.py','src/tools/edit.py','src/tools/render.py','src/models/schemas.py','src/pipeline/preprocess.py','src/agents/director.py','styles/dtc-testimonial.yaml','pyproject.toml','LICENSE')
}
$manifest = @()
foreach ($repo in $plan.Keys) {
 $dir = Join-Path $PSScriptRoot ($repo -replace '/','--')
 $sha = (Get-Content -LiteralPath (Join-Path $dir 'commit.json') -Raw | ConvertFrom-Json).sha
 foreach ($path in $plan[$repo]) {
   $raw = & $gh api "repos/$repo/contents/${path}?ref=$sha" 2>$null
   if ($LASTEXITCODE -ne 0) { Write-Output "FAILED $repo $path"; continue }
   $obj = $raw | ConvertFrom-Json
   $target = Join-Path $dir ('source/' + $path)
   New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($target)) -Force | Out-Null
   [IO.File]::WriteAllText($target,[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($obj.content)),[Text.UTF8Encoding]::new($false))
   $manifest += [pscustomobject]@{repo=$repo;sha=$sha;path=$path;url="https://github.com/$repo/blob/$sha/$path";local=$target}
 }
 Write-Output "FETCHED $repo $($plan[$repo].Count) planned files"
}
$manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'source-manifest.json') -Encoding UTF8
