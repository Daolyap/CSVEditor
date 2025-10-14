@echo off
REM Build script for CSV Editor MSI installer
REM Requires WiX Toolset v4 to be installed

echo Building CSV Editor MSI Installer with WiX 4.0...
echo.

REM Check if WiX 4.0 is installed
where wix >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: WiX Toolset 4.0 not found!
    echo.
    echo Please install WiX Toolset v4 using one of these methods:
    echo.
    echo Method 1 - .NET Tool (Recommended):
    echo   dotnet tool install --global wix
    echo.
    echo Method 2 - Download installer:
    echo   https://github.com/wixtoolset/wix4/releases
    echo.
    echo After installation, restart your terminal.
    exit /b 1
)

REM Clean previous build artifacts
echo Cleaning previous build artifacts...
if exist obj rmdir /s /q obj
if exist *.wixobj del /q *.wixobj
if exist *.wixpdb del /q *.wixpdb
if exist *.msi del /q *.msi

echo.
echo Building MSI with WiX 4.0...
wix build -arch x64 -ext WixToolset.UI.wixext -out CSVEditor.msi CSVEditor.wxs
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Build failed!
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! MSI installer created:
echo   installer\CSVEditor.msi
echo ========================================
echo.
echo You can now test the installer by running:
echo   msiexec /i CSVEditor.msi
echo.
echo Or double-click the MSI file to install.
echo.

pause
