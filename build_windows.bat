@echo off
REM ================================================================
REM  duq-tools Windows Build Script
REM  Builds duq-tools.exe using PyInstaller
REM ================================================================
REM
REM  Requirements:
REM    - Python 3.8+ installed and on PATH
REM    - Run this from the project root directory
REM
REM  Usage:
REM    build_windows.bat
REM
REM  The .exe will be generated at: dist\duq-tools.exe
REM ================================================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo  duq-tools Windows Builder
echo ========================================
echo.

REM Check Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.8+ and add it to PATH.
    pause
    exit /b 1
)

echo [INFO] Python found:
python --version

REM Upgrade pip
echo.
echo [STEP 1/4] Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo [STEP 2/4] Installing project dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

REM Install PyInstaller
echo.
echo [STEP 3/4] Installing PyInstaller...
pip install pyinstaller
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install PyInstaller.
    pause
    exit /b 1
)

REM Build
echo.
echo [STEP 4/4] Building duq-tools.exe...
echo This may take a few minutes...
echo.
pyinstaller build.spec --noconfirm --clean
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  SUCCESS!
echo ========================================
echo.
echo Executable created at: dist\duq-tools.exe
echo.
echo To run:
echo   dist\duq-tools.exe
echo   dist\duq-tools.exe --https
echo   dist\duq-tools.exe --port 8080
echo.

pause
