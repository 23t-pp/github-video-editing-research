[CmdletBinding()]
param([string]$PythonPath)
$ErrorActionPreference='Stop'
$projectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$workspaceRoot=[IO.Path]::GetFullPath((Join-Path $projectRoot '../..'))
$audioWork=Join-Path $workspaceRoot 'work/reference-library-20261105'
if(-not $PythonPath){$PythonPath=Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'}
if(-not(Test-Path -LiteralPath $PythonPath)){throw '请通过 -PythonPath 指定Python 3.12可执行文件。'}
$environment=Join-Path $audioWork 'audio-env'
New-Item -ItemType Directory -Force -Path $audioWork | Out-Null
if(-not(Test-Path -LiteralPath (Join-Path $environment 'Scripts/python.exe'))){& $PythonPath -m venv $environment; if($LASTEXITCODE -ne 0){throw '创建本地隔离环境失败'}}
$localPython=Join-Path $environment 'Scripts/python.exe'
& $localPython -m pip install --disable-pip-version-check -r (Join-Path $PSScriptRoot 'requirements-lock.txt')
if($LASTEXITCODE -ne 0){throw '依赖安装失败，请检查上方输出；没有修改全局Python。'}
$modelDirectory=Join-Path $audioWork 'models'
New-Item -ItemType Directory -Force -Path $modelDirectory | Out-Null
$model=Join-Path $modelDirectory 'UVR_MDXNET_KARA_2.onnx'
if(-not(Test-Path -LiteralPath $model)){Invoke-WebRequest -Uri 'https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR_MDXNET_KARA_2.onnx' -OutFile $model}
if((Get-FileHash -LiteralPath $model -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'bf32e15105a09c0f7dddd2b67346146334d6f3ecb399ed7638eba2ab07cbf5f4'){throw '模型SHA256与本轮验证权重不一致，已停止；请检查下载文件。'}
Write-Host '隔离依赖与模型已就绪。模型权重仅保存在work，不随本研究仓库发布。'
Write-Host '下一步先prepare-separation-inputs.mjs，再用该环境的Python运行separate-local.py。'
