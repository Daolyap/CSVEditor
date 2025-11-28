<#
.SYNOPSIS
    CSV Editor - MSI Installer Build Script (PowerShell)

.DESCRIPTION
    This script creates an MSI installer for CSV Editor using WiX Toolset.

.PREREQUISITES
    - Application built with Build.ps1 (dist\CSVEditor exists)
    - WiX Toolset v4+ installed
      Download from: https://wixtoolset.org/releases/
      Or install via: dotnet tool install --global wix

.OUTPUTS
    installer\CSVEditor.msi - The MSI installer

.EXAMPLE
    .\Build-Installer.ps1
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CSV Editor - MSI Installer Build Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if application was built
if (-not (Test-Path "dist\CSVEditor\CSVEditor.exe")) {
    Write-Host "ERROR: Application not found at dist\CSVEditor\CSVEditor.exe" -ForegroundColor Red
    Write-Host "Please run Build.ps1 first to build the application." -ForegroundColor Yellow
    exit 1
}

# Check WiX installation
try {
    $wixVersion = wix --version 2>&1
    Write-Host "Found WiX Toolset: $wixVersion" -ForegroundColor Green
} catch {
    Write-Host "WARNING: WiX Toolset not found in PATH." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please install WiX Toolset v4 or later:" -ForegroundColor White
    Write-Host "  Option 1: dotnet tool install --global wix" -ForegroundColor Cyan
    Write-Host "  Option 2: Download from https://wixtoolset.org/releases/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "After installation, run this script again." -ForegroundColor White
    exit 1
}

# Step 1: Prepare installer files
Write-Host ""
Write-Host "[1/2] Preparing installer files..." -ForegroundColor Yellow

# Copy resources to dist if not present
$resourcesPath = "dist\CSVEditor\resources"
if (-not (Test-Path $resourcesPath)) {
    New-Item -ItemType Directory -Path $resourcesPath -Force | Out-Null
}
Copy-Item -Path "resources\icon.ico" -Destination $resourcesPath -Force

# Step 2: Build MSI installer
Write-Host ""
Write-Host "[2/2] Building MSI installer..." -ForegroundColor Yellow

Push-Location installer
try {
    wix build -o CSVEditor.msi Product.wxs
    if ($LASTEXITCODE -ne 0) { throw "WiX build failed" }
} catch {
    Write-Host "ERROR: WiX build failed." -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "INSTALLER BUILD SUCCESSFUL!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "MSI installer created at:" -ForegroundColor White
Write-Host "  installer\CSVEditor.msi" -ForegroundColor Cyan
Write-Host ""
Write-Host "Users can install the application by:" -ForegroundColor White
Write-Host "  1. Double-clicking CSVEditor.msi" -ForegroundColor Cyan
Write-Host "  2. Running: msiexec /i CSVEditor.msi" -ForegroundColor Cyan
Write-Host ""
Write-Host "The installer will:" -ForegroundColor White
Write-Host "  - Install CSV Editor to Program Files" -ForegroundColor Cyan
Write-Host "  - Create Start Menu shortcuts" -ForegroundColor Cyan
Write-Host "  - Create Desktop shortcut" -ForegroundColor Cyan
Write-Host "  - Register .csv file association" -ForegroundColor Cyan
Write-Host ""
