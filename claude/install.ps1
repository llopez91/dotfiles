# Install personal Claude skills via symlinks.
# On Windows, falls back to junctions when symlink privileges are unavailable.
$ErrorActionPreference = "Stop"

$src = Join-Path $PSScriptRoot "skills"
$dest = Join-Path $env:USERPROFILE ".claude\skills"

function New-SkillLink {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path,
        [Parameter(Mandatory = $true)]
        [string] $Target
    )

    try {
        New-Item -ItemType SymbolicLink -Path $Path -Target $Target | Out-Null
        return "symlink"
    }
    catch {
        New-Item -ItemType Junction -Path $Path -Target $Target | Out-Null
        return "junction"
    }
}

if (-not (Test-Path $dest)) {
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
}

Get-ChildItem -Directory $src | ForEach-Object {
    $link = Join-Path $dest $_.Name
    if (Test-Path $link) {
        Remove-Item -Recurse -Force $link
    }
    $linkType = New-SkillLink -Path $link -Target $_.FullName
    Write-Host "Linked $($_.Name) -> $($_.FullName) ($linkType)" -ForegroundColor Green
}

Write-Host "Skills installed in $dest" -ForegroundColor Green

# El kit creativo necesita su .env para las etapas de IA.
$envFile = Join-Path $src "studio-creative\.env"
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $src "studio-creative\.env.example") $envFile
    Write-Host "Created $envFile - add your KIE_API_KEY" -ForegroundColor Yellow
}
