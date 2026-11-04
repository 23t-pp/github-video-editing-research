<#
离线复算本次搜索快照的身份去重，无网络请求。
默认读取 evidence/search/raw。模板级归并请另读 docs/04-dedup-and-exclusions.md。
#>
[CmdletBinding()]
param(
    [string]$RawDirectory = (Join-Path $PSScriptRoot '../evidence/search/raw'),
    [string]$OutputFile = (Join-Path $PSScriptRoot '../replay/merged-candidates.json')
)
$ErrorActionPreference = 'Stop'
$files = @(Get-ChildItem -LiteralPath $RawDirectory -Filter '*.json' -File)
if ($files.Count -eq 0) { throw '没有找到搜索快照。' }
$byId = @{}
$recordCount = 0
foreach ($file in $files) {
    $raw = Get-Content -LiteralPath $file.FullName -Raw -Encoding utf8 | ConvertFrom-Json
    if ($null -eq $raw.items) { throw ('不是 GitHub 仓库搜索响应：' + $file.Name) }
    foreach ($repo in $raw.items) {
        $recordCount++
        $key = [string]$repo.id
        if (-not $byId.ContainsKey($key)) {
            $byId[$key] = [pscustomobject]@{
                id=$repo.id; repo=$repo.full_name; url=$repo.html_url
                description=$repo.description; stars=$repo.stargazers_count
                license=$repo.license.spdx_id; pushed_at=$repo.pushed_at
                archived=$repo.archived; fork=$repo.fork
                source_files=[System.Collections.Generic.List[string]]::new()
                review_status='仅检索命中；本脚本不做源码审查'
            }
        }
        $byId[$key].source_files.Add($file.Name)
    }
}
$parentDirectory = Split-Path -Parent ([IO.Path]::GetFullPath($OutputFile))
New-Item -ItemType Directory -Path $parentDirectory -Force | Out-Null
ConvertTo-Json -InputObject @($byId.Values | Sort-Object repo) -Depth 8 | Set-Content -LiteralPath $OutputFile -Encoding utf8
[pscustomobject]@{queries=$files.Count;records=$recordCount;unique_repositories=$byId.Count;duplicate_occurrences=$recordCount-$byId.Count;output=$OutputFile} | Format-List
