<#
只读采集一个仓库的元数据、固定提交、目录树和 README。
不会下载/安装依赖，不执行仓库代码。源码单文件读取例子见中文教程。
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')][string]$Repository,
    [string]$OutputDirectory = (Join-Path $PSScriptRoot '../replay/snapshots')
)
$ErrorActionPreference = 'Stop'
$ghCommand = Get-Command gh -ErrorAction SilentlyContinue
if ($ghCommand) { $ghExecutable = $ghCommand.Source }
else {
    $ghExecutable = Join-Path $env:ProgramFiles 'GitHub CLI/gh.exe'
    if (-not (Test-Path -LiteralPath $ghExecutable)) { throw '没有找到 GitHub CLI。' }
}
function Read-GitHubJson([string]$Endpoint) {
    $body = & $ghExecutable api $Endpoint
    if ($LASTEXITCODE -ne 0) { throw ('API 读取失败：' + $Endpoint) }
    return (($body -join "`n") | ConvertFrom-Json)
}
$metadata = Read-GitHubJson ('repos/' + $Repository)
$commit = Read-GitHubJson ('repos/' + $Repository + '/commits/' + $metadata.default_branch)
$sha = $commit.sha
$tree = Read-GitHubJson ('repos/' + $Repository + '/git/trees/' + $sha + '?recursive=1')
$directory = Join-Path $OutputDirectory ($metadata.full_name.Replace('/','__') + '__' + $sha.Substring(0,7))
New-Item -ItemType Directory -Path $directory -Force | Out-Null
# 仅保存审查所需公开字段，不导出登录凭据或提交作者邮箱。
$snapshot = [pscustomobject]@{
    repo=$metadata.full_name; id=$metadata.id; url=$metadata.html_url
    stars=$metadata.stargazers_count; description=$metadata.description
    pushed_at=$metadata.pushed_at; default_branch=$metadata.default_branch
    archived=$metadata.archived; fork=$metadata.fork; parent=$metadata.parent.full_name
    license=$metadata.license.spdx_id; sha=$sha
    retrieved_at=[DateTimeOffset]::UtcNow.ToString('o')
}
$snapshot | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $directory 'metadata.json') -Encoding utf8
$tree | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $directory 'tree.json') -Encoding utf8
$readme = & $ghExecutable api -H 'Accept: application/vnd.github.raw+json' ('repos/' + $Repository + '/readme?ref=' + $sha)
if ($LASTEXITCODE -eq 0) {
    $readme | Set-Content -LiteralPath (Join-Path $directory 'README.upstream.md') -Encoding utf8
} else {
    Write-Warning 'README 未取到；元数据和目录树已保存，请用树确认文件路径。'
}
if ($tree.truncated) { Write-Warning '目录树被截断，需要继续读取子树。' }
Write-Host ('固定版本：' + $sha)
Write-Host ('快照位置：' + $directory)
Write-Host '上述下载只供本地阅读；重新发布上游文件前需遵循其许可。'
