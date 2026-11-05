param([ValidateSet('validate','native','hf','export','import','finalize')][string]$Phase='validate',[switch]$ReviseNative)
$ErrorActionPreference='Stop'
$occNode='C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
$occRepo='C:/Users/PC/Desktop/OpenChatCut-main'
switch($Phase){
 'validate' { & $occNode (Join-Path $PSScriptRoot 'manifest.mjs') --validate --hf }
 'native' { if($ReviseNative){ & $occNode (Join-Path $PSScriptRoot 'build.mjs') --revise-native }else{ & $occNode (Join-Path $PSScriptRoot 'build.mjs') } }
 'hf' { if($ReviseNative){ & $occNode (Join-Path $PSScriptRoot 'build.mjs') --hf --revise-native }else{ & $occNode (Join-Path $PSScriptRoot 'build.mjs') --hf } }
 'export' { & $occNode (Join-Path $occRepo 'node_modules/tsx/dist/cli.mjs') (Join-Path $PSScriptRoot 'export.mjs') }
 'import' { & $occNode (Join-Path $occRepo 'node_modules/tsx/dist/cli.mjs') (Join-Path $PSScriptRoot 'import-package.mjs') }
 'finalize' { & $occNode (Join-Path $PSScriptRoot 'finalize.mjs') }
}
if($LASTEXITCODE -ne 0){throw "OpenChatCut phase $Phase failed ($LASTEXITCODE)"}
