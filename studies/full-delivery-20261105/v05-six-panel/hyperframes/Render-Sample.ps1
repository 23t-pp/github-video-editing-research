param([string]$FramesDirectory)
$ErrorActionPreference='Stop'
$nodeExe='C:\Users\PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
if(-not (Test-Path -LiteralPath $nodeExe)){throw '请把脚本中的 nodeExe 改为你电脑上可用的 Node.js 路径。'}
if(-not $FramesDirectory){$FramesDirectory=Join-Path $PSScriptRoot ('work\render-'+[guid]::NewGuid().ToString('N'))}
$FramesDirectory=[IO.Path]::GetFullPath($FramesDirectory)
function Invoke-SampleNode([string[]]$Arguments){
 & $nodeExe @Arguments
 if($LASTEXITCODE -ne 0){throw "命令失败，退出码 $LASTEXITCODE；请查看上面的错误。"}
}
Push-Location $PSScriptRoot
try {
 Write-Host '1/4 根据参数生成视频工程、兼容渲染副本和混音'
 Invoke-SampleNode -Arguments @('build.mjs')
 Write-Host '2/4 检查工程能否在浏览器里正常运行'
 Invoke-SampleNode -Arguments @('hf.mjs','check','.','--at','0,1.5,1.875,2.1,4.3','--timeout','45s')
 Invoke-SampleNode -Arguments @('hf.mjs','check','.render-source','--at','0,1.5,1.875,2.1,4.3','--timeout','45s')
 Write-Host '3/4 使用真正的 HyperFrames 引擎渲染 PNG 帧'
 Invoke-SampleNode -Arguments @('hf.mjs','render','.render-source','--fps','24','--format','png-sequence','--workers','1','--low-memory-mode','--sdr','--experimental-fast-capture=false','--no-best-effort','--output',$FramesDirectory)
 Write-Host '4/4 把画面与声音编码为 MP4，并检查帧数'
 Invoke-SampleNode -Arguments @('encode.mjs',$FramesDirectory,(Join-Path $PSScriptRoot '..\V05六格卡片_成片.mp4'))
 Write-Host ('完成；PNG 中间帧保留在：'+$FramesDirectory)
} finally {Pop-Location}
