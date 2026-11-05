param(
    [string]$ProjectRoot = (Join-Path ([Environment]::GetFolderPath('Desktop')) 'OpenChatCut-main'),
    [switch]$CheckOnly
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
if (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot 'node_modules/vite/bin/vite.js'))) {
    throw '缺少依赖，请先按照教程安装 package-lock.json 中的依赖。'
}

# Prefer the Node 24 runtime whose filesystem access was verified on this PC.
$nodeCandidates = @(
    (Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'),
    (Get-Command node.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1)
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique
$nodeExe = $null
foreach ($candidate in $nodeCandidates) {
    $version = & $candidate --version
    if ($LASTEXITCODE -ne 0 -or $version -notmatch '^v24\.') { continue }
    $probe = Join-Path $ProjectRoot ('.node-write-check-' + [Guid]::NewGuid().ToString('N') + '.tmp')
    & $candidate -e 'const fs=require("node:fs");try{fs.writeFileSync(process.argv[1],"check",{flag:"wx"});fs.unlinkSync(process.argv[1]);}catch(e){console.error(e.code);process.exit(1)}' $probe
    if ($LASTEXITCODE -eq 0) { $nodeExe = $candidate; break }
}
if (-not $nodeExe) { throw '没有找到可以正常写入文件的 Node.js 24 运行环境。' }

Write-Host "Project: $ProjectRoot"
Write-Host "Node:    $nodeExe"
Write-Host 'URL:     http://127.0.0.1:5199/'
if ($CheckOnly) { Write-Host '启动检查通过。本次仅检查，没有启动服务。'; return }

$listener = Get-NetTCPConnection -LocalPort 5199 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($listener) {
    $owner = Get-CimInstance Win32_Process -Filter ('ProcessId=' + $listener.OwningProcess)
    if ($owner.CommandLine -match [regex]::Escape($ProjectRoot) -and $owner.CommandLine -match 'vite[\\/]bin[\\/]vite\.js') {
        Write-Host 'OpenChatCut 已在运行，打开上面的地址即可。'
        return
    }
    throw '5199 端口被其他程序占用；本脚本没有停止任何程序。'
}

$savedEnvironment = @{}
foreach ($name in @('PATH', 'OPENCHATCUT_DATA_DIR', 'BROWSER', 'VITE_CONFIG_NATIVE_IGNORE_WARNING')) {
    $savedEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
}
Push-Location -LiteralPath $ProjectRoot
try {
    $env:PATH = (Split-Path -Parent $nodeExe) + ';' + $env:PATH
    # Use the official isolated profile; its settings loader expects the native data location.
    [Environment]::SetEnvironmentVariable('OPENCHATCUT_DATA_DIR', $null, 'Process')
    $env:BROWSER = 'none'
    # Hide only Vite's advisory about a future config-loader default.
    $env:VITE_CONFIG_NATIVE_IGNORE_WARNING = 'true'

    if (-not (Test-Path -LiteralPath '.git')) {
        & git init
        if ($LASTEXITCODE -ne 0) { throw '本地 Git 目录初始化失败。' }
    }
    if (-not (Test-Path -LiteralPath '.env.local')) {
        Copy-Item -LiteralPath '.env.example' -Destination '.env.local'
    }

    # These are the three preparation steps from package.json's predev command.
    & $nodeExe 'scripts/sync-mediapipe.mjs'
    if ($LASTEXITCODE -ne 0) { throw 'MediaPipe 资源准备失败。' }
    & $nodeExe 'scripts/sync-whisper-cli.mjs'
    if ($LASTEXITCODE -ne 0) { throw 'Whisper CLI 准备失败。' }
    & $nodeExe 'node_modules/tsx/dist/cli.mjs' 'server/agent-runs/generate-tool-catalog.mts' '--check'
    if ($LASTEXITCODE -ne 0) { throw '服务端工具目录检查失败。' }

    Write-Host '正在启动 OpenChatCut。请保持终端开启；在这个终端按 Ctrl+C 可以停止服务。'
    & $nodeExe 'scripts/dev-profile.mjs' '--host' '127.0.0.1'
    if ($LASTEXITCODE -ne 0) { throw "OpenChatCut 已退出，退出码为 $LASTEXITCODE。" }
} finally {
    Pop-Location
    foreach ($name in $savedEnvironment.Keys) {
        [Environment]::SetEnvironmentVariable($name, $savedEnvironment[$name], 'Process')
    }
}
