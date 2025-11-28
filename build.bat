@echo off
REM ============================================================
REM CSV Editor - Windows Build Script
REM ============================================================
REM This script builds the CSV Editor Windows application.
REM
REM Prerequisites:
REM   - Python 3.8+ installed and in PATH
REM   - pip (Python package manager)
REM
REM Usage:
REM   build.bat
REM
REM Output:
REM   dist\CSVEditor\CSVEditor.exe - The main application
REM ============================================================

echo ============================================================
echo CSV Editor - Windows Build Script
echo ============================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8 or later from https://python.org
    exit /b 1
)

echo [1/4] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies.
    exit /b 1
)

echo.
echo [2/4] Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller.
    exit /b 1
)

echo.
echo [3/4] Building application with PyInstaller...
pyinstaller --clean CSVEditor.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    exit /b 1
)

echo.
echo [4/4] Verifying build...
if exist "dist\CSVEditor\CSVEditor.exe" (
    echo.
    echo ============================================================
    echo BUILD SUCCESSFUL!
    echo ============================================================
    echo.
    echo Application built successfully at:
    echo   dist\CSVEditor\CSVEditor.exe
    echo.
    echo To create an MSI installer, run:
    echo   build_installer.bat
    echo.
) else (
    echo ERROR: Build verification failed. CSVEditor.exe not found.
    exit /b 1
)
