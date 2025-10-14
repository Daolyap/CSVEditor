# Build script for CSV Editor MSI installer
# Requires WiX Toolset v3 or v4 to be installed

Write-Host "Building CSV Editor MSI Installer..." -ForegroundColor Cyan
Write-Host ""

# Check if WiX is installed
$candleExists = Get-Command candle.exe -ErrorAction SilentlyContinue
if (-not $candleExists) {
    Write-Host "ERROR: WiX Toolset not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install WiX Toolset from:"
    Write-Host "  - WiX v3: https://github.com/wixtoolset/wix3/releases"
    Write-Host "  - WiX v4: https://github.com/wixtoolset/wix4/releases"
    Write-Host ""
    Write-Host "After installation, make sure the WiX bin directory is in your PATH."
    exit 1
}

# Clean previous build artifacts
Write-Host "Cleaning previous build artifacts..." -ForegroundColor Yellow
if (Test-Path "obj") { Remove-Item -Recurse -Force "obj" }
if (Test-Path "*.wixobj") { Remove-Item "*.wixobj" }
if (Test-Path "*.wixpdb") { Remove-Item "*.wixpdb" }
if (Test-Path "*.msi") { Remove-Item "*.msi" }

# Create obj directory
New-Item -ItemType Directory -Force -Path "obj" | Out-Null

Write-Host ""
Write-Host "Step 1: Compiling WiX source file..." -ForegroundColor Yellow
& candle.exe -arch x64 -out obj\CSVEditor.wixobj CSVEditor.wxs

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Compilation failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Linking and creating MSI..." -ForegroundColor Yellow
& light.exe -ext WixUIExtension -out CSVEditor.msi obj\CSVEditor.wixobj

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Linking failed!" -ForegroundColor Red
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
