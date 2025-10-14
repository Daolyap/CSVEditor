@echo off
REM Build script for CSV Editor MSI installer
REM Requires WiX Toolset v3 or v4 to be installed

echo Building CSV Editor MSI Installer...
echo.

REM Check if WiX is installed
where candle >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: WiX Toolset not found!
    echo.
    echo Please install WiX Toolset from:
    echo   - WiX v3: https://github.com/wixtoolset/wix3/releases
    echo   - WiX v4: https://github.com/wixtoolset/wix4/releases
    echo.
    echo After installation, make sure the WiX bin directory is in your PATH.
    exit /b 1
)

REM Clean previous build artifacts
echo Cleaning previous build artifacts...
if exist obj rmdir /s /q obj
if exist *.wixobj del /q *.wixobj
if exist *.wixpdb del /q *.wixpdb
if exist *.msi del /q *.msi

REM Create obj directory
if not exist obj mkdir obj

echo.
echo Step 1: Compiling WiX source file...
candle.exe -arch x64 -out obj\CSVEditor.wixobj CSVEditor.wxs
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Compilation failed!
    exit /b 1
)

echo.
echo Step 2: Linking and creating MSI...
light.exe -ext WixUIExtension -out CSVEditor.msi obj\CSVEditor.wixobj
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Linking failed!
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
