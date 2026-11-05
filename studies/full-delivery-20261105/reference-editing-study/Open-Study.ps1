[CmdletBinding()]
param([string]$NodePath,[switch]$NoBrowser)
$ErrorActionPreference='Stop'
$address='http://127.0.0.1:5208'
$serverScript=Join-Path $PSScriptRoot 'scripts/serve-study.mjs'
function Get-StudyHealth {
    try { return Invoke-RestMethod -Uri ($address+'/health') -TimeoutSec 2 } catch { return $null }
}
$health=Get-StudyHealth
if($health -and $health.app -ne 'reference-editing-study') { throw '5208端口已有其他服务，请先关闭它。' }
if(-not $health) {
    if(-not $NodePath) {
        $bundledNode=Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
        if(Test-Path -LiteralPath $bundledNode) { $NodePath=$bundledNode }
        else { $nodeCommand=Get-Command node -ErrorAction SilentlyContinue; if($nodeCommand) {$NodePath=$nodeCommand.Source} }
    }
    if(-not $NodePath -or -not(Test-Path -LiteralPath $NodePath)) { throw '没有找到Node.js。请用 -NodePath 指定已安装的 node.exe。' }
    $quotedScript='"'+$serverScript+'"'
    $studyProcess=Start-Process -FilePath $NodePath -ArgumentList $quotedScript -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru
    for($attempt=0;$attempt -lt 25;$attempt++) {
        Start-Sleep -Milliseconds 200
        $health=Get-StudyHealth
        if($health -and $health.app -eq 'reference-editing-study') { break }
        if($studyProcess.HasExited) { break }
    }
    if(-not $health -or $health.app -ne 'reference-editing-study') { throw '本地服务没有启动。请在终端直接运行 scripts/serve-study.mjs 查看视频白名单或端口错误。' }
    Write-Host ('服务进程：'+$studyProcess.Id+'。需要停止时，在PowerShell运行 Stop-Process -Id '+$studyProcess.Id)
}
Write-Host ('学习页：'+$address+'；可读视频 '+$health.media_count+'/10。视频仅在本机播放。')
if(-not $NoBrowser) { Start-Process $address }
