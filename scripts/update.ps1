# Update installed packages (Windows)
$ErrorActionPreference = "Continue"

if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "Updating winget packages..." -ForegroundColor Cyan
    winget upgrade --all --accept-source-agreements --accept-package-agreements
}

if (Get-Command scoop -ErrorAction SilentlyContinue) {
    Write-Host "Updating scoop packages..." -ForegroundColor Cyan
    scoop update *
}

if (Get-Command npm -ErrorAction SilentlyContinue) {
    Write-Host "Updating global npm packages..." -ForegroundColor Cyan
    npm update -g
}

Write-Host "System updated!" -ForegroundColor Green
