$ErrorActionPreference='Stop'
$nodeExe='C:\Users\PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
& $nodeExe (Join-Path $PSScriptRoot 'hf.mjs') preview . --background --no-open --no-proxy --port 5210
if($LASTEXITCODE -ne 0){throw '预览启动失败；请查看错误。'}
Start-Process 'http://127.0.0.1:5210/#project/hyperframes'
