# Build script for CSV Editor MSI installer
# Requires WiX Toolset v4 to be installed

Write-Host "Building CSV Editor MSI Installer with WiX 4.0..." -ForegroundColor Cyan
Write-Host ""

# Check if WiX 4.0 is installed
$wixExists = Get-Command wix -ErrorAction SilentlyContinue
if (-not $wixExists) {
    Write-Host "ERROR: WiX Toolset 4.0 not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install WiX Toolset v4 using one of these methods:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Method 1 - .NET Tool (Recommended):" -ForegroundColor Cyan
    Write-Host "  dotnet tool install --global wix" -ForegroundColor White
    Write-Host ""
    Write-Host "Method 2 - Download installer:" -ForegroundColor Cyan
    Write-Host "  https://github.com/wixtoolset/wix4/releases" -ForegroundColor White
    Write-Host ""
    Write-Host "After installation, restart your terminal." -ForegroundColor Yellow
    exit 1
}

# Clean previous build artifacts
Write-Host "Cleaning previous build artifacts..." -ForegroundColor Yellow
if (Test-Path "obj") { Remove-Item -Recurse -Force "obj" }
if (Test-Path "*.wixobj") { Remove-Item "*.wixobj" }
if (Test-Path "*.wixpdb") { Remove-Item "*.wixpdb" }
if (Test-Path "*.msi") { Remove-Item "*.msi" }

Write-Host ""
Write-Host "Building MSI with WiX 4.0..." -ForegroundColor Yellow
& wix build -arch x64 -ext WixToolset.UI.wixext -out CSVEditor.msi CSVEditor.wxs

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "SUCCESS! MSI installer created:" -ForegroundColor Green
Write-Host "  installer\CSVEditor.msi" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now test the installer by running:"
Write-Host "  msiexec /i CSVEditor.msi"
Write-Host ""
Write-Host "Or double-click the MSI file to install."
Write-Host ""
