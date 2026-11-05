$ErrorActionPreference = 'Stop'
$gh = 'C:\Program Files\GitHub CLI\gh.exe'
$queries = @(
 '"AI video editor" in:name,description,readme stars:>50',
 '"video highlight" "AI" in:name,description,readme stars:>20',
 '"short clips" "whisper" in:readme stars:>50',
 '"automatic video editing" in:name,description,readme stars:>20',
 '"video clipping" "LLM" in:readme stars:>20',
 '"subtitle" "video editing" "AI" in:name,description stars:>20',
 '"ClipAnything" in:name,description,readme',
 '"MoneyPrinterTurbo" OR "ShortGPT" in:name stars:>100'
)
$summary = @()
for ($i = 0; $i -lt $queries.Count; $i++) {
 $q = $queries[$i]
 $file = 'search-{0:d2}.json' -f ($i + 1)
 $raw = & $gh api --method GET search/repositories -f "q=$q" -f 'per_page=30' -f 'sort=stars'
 if ($LASTEXITCODE -ne 0) { throw "Search failed: $q" }
 [IO.File]::WriteAllText((Join-Path $PSScriptRoot $file), ($raw -join "`n"), [Text.UTF8Encoding]::new($false))
 $obj = $raw | ConvertFrom-Json
 $summary += [pscustomobject]@{query=$q;count=$obj.items.Count;total_count=$obj.total_count;raw_file=$file}
}
$summary | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'searches.json') -Encoding UTF8
$all = foreach ($s in $summary) { (Get-Content -LiteralPath (Join-Path $PSScriptRoot $s.raw_file) -Raw | ConvertFrom-Json).items }
$all | Sort-Object full_name -Unique | Select-Object full_name,description,stargazers_count,pushed_at,archived,fork,license,html_url,default_branch | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'candidates.json') -Encoding UTF8
$summary | Format-Table -AutoSize
$all | Sort-Object full_name -Unique | Sort-Object stargazers_count -Descending | Select-Object -First 65 full_name,stargazers_count,pushed_at,description | Format-Table -AutoSize -Wrap
