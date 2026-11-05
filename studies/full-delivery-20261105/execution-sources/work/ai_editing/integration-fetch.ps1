$ErrorActionPreference = 'Stop'
$gh = 'C:\Program Files\GitHub CLI\gh.exe'
$sha = '7fa4b7903e7ebecf832a36249f0c0c755200cc17'
$dir = Join-Path $PSScriptRoot '0xsline--OpenChatCut/source'
$paths = @(
 'cli/main.ts','cli/occ.mjs','cli/router.ts','cli/profile.ts','cli/store.ts','cli/session.ts','cli/tool-catalog.ts',
 'cli/commands/project.ts','cli/commands/media.ts','cli/commands/timeline.ts','cli/commands/item.ts','cli/commands/render.ts','cli/commands/tools.ts','cli/commands/run-op.ts',
 'server/external-agent/mcp.ts','server/external-agent/offline-tools.ts','server/external-agent/offline-runtime-support.ts','server/external-agent/offline-path-import.ts','server/external-agent/mcp-instructions.ts',
 'server/project-store-http-routes.ts','server/project-store-http-auth.ts','server/mcp-token.ts',
 'src/agent/tools/timeline-import-tools.ts','src/agent/tools/schemas/timeline-import-tools.ts','src/agent/tools/schemas/music-intelligence-tools.ts','src/agent/tools/schemas/project-tools.ts',
 'src/agent/tools/agent-path-import-tools.ts','src/components/settings/mcpClientConfig.ts','src/agent/skills/music-intelligence/SKILL.md'
)
foreach ($p in $paths) {
 $target = Join-Path $dir $p
 if (Test-Path -LiteralPath $target) { continue }
 $obj = & $gh api "repos/0xsline/OpenChatCut/contents/${p}?ref=$sha" | ConvertFrom-Json
 if ($LASTEXITCODE -ne 0) { throw "Failed $p" }
 New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($target)) -Force | Out-Null
 [IO.File]::WriteAllText($target,[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($obj.content)),[Text.UTF8Encoding]::new($false))
 Write-Output "FETCHED $p"
}
$paths | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'integration-source-paths.json') -Encoding UTF8
