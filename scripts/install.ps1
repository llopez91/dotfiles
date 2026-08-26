# Add scripts folder to the user PATH (Windows)
$ErrorActionPreference = "Stop"

$scriptsDir = $PSScriptRoot
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")

if ($userPath -notlike "*$scriptsDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$scriptsDir", "User")
    Write-Host "Added $scriptsDir to user PATH" -ForegroundColor Green
} else {
    Write-Host "Scripts already in PATH" -ForegroundColor Yellow
}

Write-Host "Scripts installed! Restart your terminal to apply." -ForegroundColor Green
