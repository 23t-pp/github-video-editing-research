<#
用已登录的 GitHub CLI 复跑检索。只读 GitHub；输出到 replay，不覆盖历史快照。
建议 PowerShell 7。示例：pwsh -NoProfile -File ./scripts/Search-GitHub.ps1 -MaxQueries 1
#>
[CmdletBinding()]
param(
    [string]$QueryFile = (Join-Path $PSScriptRoot '../evidence/search/queries.json'),
    [string]$OutputDirectory = (Join-Path $PSScriptRoot '../replay'),
    [ValidateRange(0,1000)][int]$MaxQueries = 0
)
$ErrorActionPreference = 'Stop'
$ghCommand = Get-Command gh -ErrorAction SilentlyContinue
if ($ghCommand) {
    $ghExecutable = $ghCommand.Source
} else {
    $ghExecutable = Join-Path $env:ProgramFiles 'GitHub CLI/gh.exe'
    if (-not (Test-Path -LiteralPath $ghExecutable)) { throw '没有找到 gh，请先安装 GitHub CLI 并重新打开终端。' }
}
$queries = @(Get-Content -LiteralPath $QueryFile -Raw -Encoding utf8 | ConvertFrom-Json)
if ($MaxQueries -gt 0) { $queries = @($queries | Select-Object -First $MaxQueries) }
if ($queries.Count -eq 0) { throw '查询清单为空。' }
$runDirectory = Join-Path $OutputDirectory (Get-Date -Format 'yyyyMMdd-HHmmss-fff')
$rawDirectory = Join-Path $runDirectory 'raw'
New-Item -ItemType Directory -Path $rawDirectory -Force | Out-Null
$records = @()
for ($index = 0; $index -lt $queries.Count; $index++) {
    $item = $queries[$index]
    Write-Host (('[{0}/{1}] {2}' -f ($index+1),$queries.Count,$item.query))
    $raw = & $ghExecutable api --method GET search/repositories -f ('q=' + $item.query) -f per_page=30
    if ($LASTEXITCODE -ne 0) { throw 'GitHub API 失败。请检查上面的错误；如有限流提示，等额度恢复后重试。已有结果已保留。' }
    $parsed = ($raw -join "`n") | ConvertFrom-Json
    if ($null -eq $parsed.items) { throw '响应缺少 items，停止以免保存错误数据。' }
    $rawName = '{0:D2}.json' -f ($index+1)
    $raw | Set-Content -LiteralPath (Join-Path $rawDirectory $rawName) -Encoding utf8
    $records += [pscustomobject]@{
        id=$item.id; query=$item.query; count=@($parsed.items).Count
        total_count=$parsed.total_count; incomplete_results=$parsed.incomplete_results
        retrieved_at=[DateTimeOffset]::UtcNow.ToString('o'); raw_file=('raw/' + $rawName)
    }
    ConvertTo-Json -InputObject @($records) -Depth 8 | Set-Content -LiteralPath (Join-Path $runDirectory 'queries.json') -Encoding utf8
    Write-Host ('本页 {0} 条；服务端匹配总量 {1}；incomplete_results={2}' -f @($parsed.items).Count,$parsed.total_count,$parsed.incomplete_results)
    if ($index -lt $queries.Count-1) { Start-Sleep -Seconds 3 }
}
Write-Host ('已保存到：' + $runDirectory)
Write-Host '搜索结果不等于源码审查结论；请继续核查模板入口和许可。'
[pscustomobject]@{run_directory=$runDirectory;raw_directory=$rawDirectory;queries=$records.Count;records=($records | Measure-Object -Property count -Sum).Sum}
