$ErrorActionPreference = 'Stop'
$bundle = (& node (Join-Path $PSScriptRoot 'make-review.cjs') | ConvertFrom-Json)
if ($LASTEXITCODE -ne 0) { throw 'Report generation failed' }
foreach ($property in $bundle.PSObject.Properties) {
    $property.Value | Set-Content -LiteralPath (Join-Path $PSScriptRoot $property.Name) -Encoding utf8
}
Get-Item -LiteralPath (Join-Path $PSScriptRoot 'review.json'), (Join-Path $PSScriptRoot 'review.md'), (Join-Path $PSScriptRoot 'candidates.json') | Select-Object Name,Length
