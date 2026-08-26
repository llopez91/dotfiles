# Clean up caches and temp files (Windows)
$ErrorActionPreference = "Continue"

# Temp files older than 7 days
Write-Host "Cleaning temp files older than 7 days..." -ForegroundColor Cyan
$cutoff = (Get-Date).AddDays(-7)
foreach ($dir in @($env:TEMP, "$env:SystemRoot\Temp")) {
    if (Test-Path $dir) {
        Get-ChildItem $dir -Recurse -Force -ErrorAction SilentlyContinue |
            Where-Object { -not $_.PSIsContainer -and $_.LastAccessTime -lt $cutoff } |
            Remove-Item -Force -ErrorAction SilentlyContinue
    }
}

if (Get-Command npm -ErrorAction SilentlyContinue) {
    Write-Host "Cleaning npm cache..." -ForegroundColor Cyan
    npm cache clean --force 2>$null
}

if (Get-Command pip -ErrorAction SilentlyContinue) {
    Write-Host "Cleaning pip cache..." -ForegroundColor Cyan
    pip cache purge 2>$null
}

if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "Pruning docker..." -ForegroundColor Cyan
    docker system prune -f 2>$null
}

Write-Host "Cleanup done!" -ForegroundColor Green
