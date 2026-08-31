# Apunta los perfiles de PowerShell al tema local de oh-my-posh.
# Cubre PowerShell 7 (pwsh) y Windows PowerShell 5.1.
$ErrorActionPreference = "Stop"

$theme = Join-Path $PSScriptRoot "zash-python.omp.json"
if (-not (Test-Path $theme)) {
    throw "No encuentro el tema en $theme"
}

if (-not (Get-Command oh-my-posh -ErrorAction SilentlyContinue)) {
    Write-Host "oh-my-posh no esta instalado. Instalalo con:" -ForegroundColor Red
    Write-Host "  winget install JanDeDobbeleer.OhMyPosh -s winget" -ForegroundColor Yellow
    return
}

# La linea usa `$HOME` literal para que el perfil quede portable.
$line = 'oh-my-posh init pwsh --config "$HOME\dotfiles\oh-my-posh\zash-python.omp.json" | Invoke-Expression'

$profiles = @(
    (Join-Path $HOME "Documents\PowerShell\Microsoft.PowerShell_profile.ps1"),
    (Join-Path $HOME "Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1")
)

foreach ($p in $profiles) {
    $dir = Split-Path $p -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    $content = ""
    if (Test-Path $p) {
        Copy-Item $p "$p.bak" -Force
        $content = Get-Content $p -Raw
    }

    if ($content -match 'zash-python\.omp\.json') {
        Write-Host "Ya configurado: $p" -ForegroundColor Yellow
        continue
    }

    # Comenta cualquier init de oh-my-posh previo en vez de duplicar el prompt.
    $content = $content -replace '(?m)^(oh-my-posh init)', '#$1'
    $content = $content.TrimEnd() + "`n`n$line`n"
    Set-Content -Path $p -Value $content -NoNewline -Encoding utf8NoBOM
    Write-Host "Configurado: $p" -ForegroundColor Green
}

# Sin una Nerd Font en la terminal, el icono de Python sale como cuadro vacio.
$fonts = @()
foreach ($hive in @("HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts",
                    "HKCU:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts")) {
    $key = Get-ItemProperty $hive -ErrorAction SilentlyContinue
    if ($key) { $fonts += $key.PSObject.Properties.Name }
}
if (-not ($fonts | Where-Object { $_ -match "Nerd Font|NF " })) {
    Write-Host ""
    Write-Host "No hay ninguna Nerd Font instalada: los iconos saldran como cuadros." -ForegroundColor Yellow
    Write-Host "  oh-my-posh font install 0xProto" -ForegroundColor Yellow
    Write-Host "Luego ponla como fuente en tu terminal y en VS Code" -ForegroundColor Yellow
    Write-Host "  (terminal.integrated.fontFamily)." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Listo. Abre una terminal nueva." -ForegroundColor Green
