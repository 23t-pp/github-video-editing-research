$jjkBase = 'D:/gpt/2026-11-04/ps-c-windows-system32-winget-install-2/outputs/jjk-edge-v17-v2'
$jjkNode = 'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
if (-not (Get-NetTCPConnection -State Listen -LocalPort 5241 -ErrorAction SilentlyContinue)) {
    Start-Process -FilePath $jjkNode -ArgumentList @('player-server.mjs') -WorkingDirectory $jjkBase -WindowStyle Hidden -RedirectStandardOutput "$jjkBase/evidence/player-server.log" -RedirectStandardError "$jjkBase/evidence/player-server-error.log"
}
if (-not (Get-NetTCPConnection -State Listen -LocalPort 5240 -ErrorAction SilentlyContinue)) {
    Start-Process -FilePath $jjkNode -ArgumentList @('hf.mjs','preview','.','--port','5240','--no-open') -WorkingDirectory "$jjkBase/hyperframes" -WindowStyle Hidden -RedirectStandardOutput "$jjkBase/evidence/hyperframes-preview.log" -RedirectStandardError "$jjkBase/evidence/hyperframes-preview-error.log"
}
Get-NetTCPConnection -State Listen -LocalPort 5240,5241 -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,OwningProcess
