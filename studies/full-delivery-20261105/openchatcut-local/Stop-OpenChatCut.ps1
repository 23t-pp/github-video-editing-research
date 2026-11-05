param([string]$ProjectRoot = (Join-Path ([Environment]::GetFolderPath('Desktop')) 'OpenChatCut-main'))
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$listener = Get-NetTCPConnection -LocalPort 5199 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $listener) { Write-Host '5199 端口上没有运行中的 OpenChatCut。'; return }
$owner = Get-CimInstance Win32_Process -Filter ('ProcessId=' + $listener.OwningProcess)
if ($owner.CommandLine -notmatch [regex]::Escape($ProjectRoot) -or $owner.CommandLine -notmatch 'vite[\\/]bin[\\/]vite\.js') {
    throw '端口所属程序与这个 OpenChatCut 项目不匹配；没有停止任何程序。'
}
Stop-Process -Id $listener.OwningProcess -ErrorAction Stop
Write-Host 'OpenChatCut 已停止，工程数据已保留。'
