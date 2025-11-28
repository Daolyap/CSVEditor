@echo off
REM ============================================================
REM CSV Editor - MSI Installer Build Script
REM ============================================================
REM This script creates an MSI installer for CSV Editor.
REM
REM Prerequisites:
REM   - Application built with build.bat (dist\CSVEditor exists)
REM   - WiX Toolset v4+ installed
REM     Download from: https://wixtoolset.org/releases/
REM     Or install via: dotnet tool install --global wix
REM
REM Usage:
REM   build_installer.bat
REM
REM Output:
REM   installer\CSVEditor.msi - The MSI installer
REM ============================================================

echo ============================================================
echo CSV Editor - MSI Installer Build Script
echo ============================================================
echo.

REM Check if application was built
if not exist "dist\CSVEditor\CSVEditor.exe" (
    echo ERROR: Application not found at dist\CSVEditor\CSVEditor.exe
    echo Please run build.bat first to build the application.
    exit /b 1
)

REM Check WiX installation
wix --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: WiX Toolset not found in PATH.
    echo.
    echo Please install WiX Toolset v4 or later:
    echo   Option 1: dotnet tool install --global wix
    echo   Option 2: Download from https://wixtoolset.org/releases/
    echo.
    echo After installation, run this script again.
    exit /b 1
)

echo [1/2] Preparing installer files...

REM Copy resources to dist if not present
if not exist "dist\CSVEditor\resources" mkdir "dist\CSVEditor\resources"
copy /Y "resources\icon.ico" "dist\CSVEditor\resources\" >nul

echo.
echo [2/2] Building MSI installer...

cd installer

REM Build the MSI
wix build -o CSVEditor.msi Product.wxs

if errorlevel 1 (
    echo ERROR: WiX build failed.
    cd ..
    exit /b 1
)

cd ..

echo.
echo ============================================================
echo INSTALLER BUILD SUCCESSFUL!
echo ============================================================
echo.
echo MSI installer created at:
echo   installer\CSVEditor.msi
echo.
echo Users can install the application by:
echo   1. Double-clicking CSVEditor.msi
echo   2. Running: msiexec /i CSVEditor.msi
echo.
echo The installer will:
echo   - Install CSV Editor to Program Files
echo   - Create Start Menu shortcuts
echo   - Create Desktop shortcut
echo   - Register .csv file association
echo.
