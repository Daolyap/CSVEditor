<#
.SYNOPSIS
    CSV Editor - Windows Build Script (PowerShell)

.DESCRIPTION
    This script builds the CSV Editor Windows application using PyInstaller.

.PREREQUISITES
    - Python 3.8+ installed and in PATH
    - pip (Python package manager)

.OUTPUTS
    dist\CSVEditor\CSVEditor.exe - The main application

.EXAMPLE
    .\Build.ps1
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CSV Editor - Windows Build Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.8 or later from https://python.org" -ForegroundColor Yellow
    exit 1
}

# Step 1: Install Python dependencies
Write-Host ""
Write-Host "[1/4] Installing Python dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
} catch {
    Write-Host "ERROR: Failed to install Python dependencies." -ForegroundColor Red
    exit 1
}

# Step 2: Install PyInstaller
Write-Host ""
Write-Host "[2/4] Installing PyInstaller..." -ForegroundColor Yellow
try {
    pip install pyinstaller
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller install failed" }
} catch {
    Write-Host "ERROR: Failed to install PyInstaller." -ForegroundColor Red
    exit 1
}

# Step 3: Build application
Write-Host ""
Write-Host "[3/4] Building application with PyInstaller..." -ForegroundColor Yellow
try {
    pyinstaller --clean CSVEditor.spec
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed" }
} catch {
    Write-Host "ERROR: PyInstaller build failed." -ForegroundColor Red
    exit 1
}

# Step 4: Verify build
Write-Host ""
Write-Host "[4/4] Verifying build..." -ForegroundColor Yellow
if (Test-Path "dist\CSVEditor\CSVEditor.exe") {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Application built successfully at:" -ForegroundColor White
    Write-Host "  dist\CSVEditor\CSVEditor.exe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To create an MSI installer, run:" -ForegroundColor White
    Write-Host "  .\Build-Installer.ps1" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "ERROR: Build verification failed. CSVEditor.exe not found." -ForegroundColor Red
    exit 1
}
