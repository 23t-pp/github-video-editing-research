<# 校验研究资料，不安装或执行任何候选剪辑软件。 #>
[CmdletBinding()]
param([string]$RepositoryDirectory = (Join-Path $PSScriptRoot '..'))
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath($RepositoryDirectory)
$evidenceDirectory = Join-Path $root 'evidence'
$stats = Get-Content -LiteralPath (Join-Path $evidenceDirectory 'statistics.json') -Raw -Encoding utf8 | ConvertFrom-Json
$queries = @(Get-Content -LiteralPath (Join-Path $evidenceDirectory 'search/queries.json') -Raw -Encoding utf8 | ConvertFrom-Json)
$catalog = @(Get-Content -LiteralPath (Join-Path $evidenceDirectory 'catalog.json') -Raw -Encoding utf8 | ConvertFrom-Json)
$reviewed = @(Get-Content -LiteralPath (Join-Path $evidenceDirectory 'reviewed-projects.json') -Raw -Encoding utf8 | ConvertFrom-Json)
$errors = [System.Collections.Generic.List[string]]::new()
$ids = [System.Collections.Generic.HashSet[long]]::new()
$records = 0
foreach ($q in $queries) {
    $rawPath = Join-Path $root $q.raw_file
    $raw = Get-Content -LiteralPath $rawPath -Raw -Encoding utf8 | ConvertFrom-Json
    if (@($raw.items).Count -ne $q.count) { $errors.Add('查询条数不一致：' + $q.id) }
    foreach ($item in $raw.items) { [void]$ids.Add([long]$item.id); $records++ }
}
if ($queries.Count -ne $stats.query_count -or $records -ne $stats.retrieved_search_records -or $ids.Count -ne $stats.unique_search_repositories) { $errors.Add('搜索汇总计数不一致') }
if (($records-$ids.Count) -ne $stats.duplicate_search_occurrences) { $errors.Add('重复数不一致') }
if ($catalog.Count -ne $stats.catalog_repositories) { $errors.Add('总目录计数不一致') }
if (@($catalog | Group-Object id).Count -ne $catalog.Count) { $errors.Add('总目录仍有重复id') }
if ($reviewed.Count -ne $stats.focused_source_review_repositories) { $errors.Add('审查项目数不一致') }
$evidenceLinks = 0
foreach ($r in $reviewed) {
    if ($r.sha -notmatch '^[a-f0-9]{40}$') { $errors.Add('SHA格式错误：' + $r.repo) }
    $expected = 'https://github.com/' + $r.repo + '/blob/' + $r.sha + '/'
    foreach ($e in $r.evidence) {
        $evidenceLinks++
        if (-not $e.url.StartsWith($expected,[StringComparison]::OrdinalIgnoreCase)) { $errors.Add('证据不是对应固定SHA：' + $e.url) }
    }
}
if ($evidenceLinks -ne $stats.source_evidence_links) { $errors.Add('源码证据数不一致') }
$jsonFiles = @(Get-ChildItem -LiteralPath $evidenceDirectory -Filter '*.json' -File -Recurse)
foreach ($file in $jsonFiles) {
    try { Get-Content -LiteralPath $file.FullName -Raw -Encoding utf8 | ConvertFrom-Json | Out-Null }
    catch { $errors.Add('JSON解析失败：' + $file.Name) }
}
$internalLinks = 0
$docs = @(Get-ChildItem -LiteralPath $root -Filter '*.md' -File -Recurse | Where-Object { $_.FullName -notmatch '[\\/](\.git|replay|work)[\\/]' })
foreach ($doc in $docs) {
    $body = Get-Content -LiteralPath $doc.FullName -Raw -Encoding utf8
    foreach ($m in [regex]::Matches($body,'\[[^\]]+\]\(([^\s\)]+)\)')) {
        $href = $m.Groups[1].Value
        if ($href -match '^(https?://|mailto:|#)') { continue }
        $target = [Uri]::UnescapeDataString(($href -split '#')[0])
        if (-not $target) { continue }
        $internalLinks++
        if (-not (Test-Path -LiteralPath (Join-Path $doc.DirectoryName $target))) { $errors.Add('失效内部链接：' + $doc.Name + ' -> ' + $href) }
    }
    if ($body.Contains('[object Object]')) { $errors.Add('对象未正确格式化：' + $doc.Name) }
}
$powershellFiles = @(Get-ChildItem -LiteralPath (Join-Path $root 'scripts') -Filter '*.ps1' -File)
foreach ($script in $powershellFiles) {
    $tokens=$null; $parseErrors=$null
    [void][System.Management.Automation.Language.Parser]::ParseFile($script.FullName,[ref]$tokens,[ref]$parseErrors)
    if ($parseErrors.Count) { $errors.Add('PowerShell解析失败：' + $script.Name) }
}
$report = [pscustomobject]@{
    checked_at=[DateTimeOffset]::UtcNow.ToString('o')
    scope='研究资料自身校验；不代表候选剪辑软件运行验证'
    passed=($errors.Count -eq 0); queries=$queries.Count; search_records=$records
    search_unique=$ids.Count; catalog=$catalog.Count; reviewed=$reviewed.Count
    fixed_sha_links=$evidenceLinks; json_files=$jsonFiles.Count; internal_links=$internalLinks
    powershell_files=$powershellFiles.Count; errors=@($errors)
}
$report | ConvertTo-Json -Depth 6
if ($errors.Count) { throw ('研究校验失败：' + ($errors -join '；')) }
