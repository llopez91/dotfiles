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

    # Si lo que hay es un directorio real con un .env, rescatalo antes de
    # borrarlo: es la unica copia de las llaves y no esta versionada.
    $existingEnv = Join-Path $link ".env"
    $repoEnv = Join-Path $_.FullName ".env"
    $item = Get-Item $link -Force -ErrorAction SilentlyContinue
    $isRealDir = $item -and $item.PSIsContainer -and -not $item.LinkType
    if ($isRealDir -and (Test-Path $existingEnv) -and -not (Test-Path $repoEnv)) {
        Copy-Item $existingEnv $repoEnv
        Write-Host "Rescued $($_.Name)\.env into the repo (untracked)" -ForegroundColor Cyan
    }

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
