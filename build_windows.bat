@echo off
echo =========================================
echo   duq-tools Windows Builder
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.10+ from https://python.org
    echo Make sure to check 'Add Python to PATH' during installation.
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
pip install PySide6 Pillow pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo [2/3] Building executable...
pyinstaller build.spec
if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo [3/3] Creating ZIP package...
powershell Compress-Archive -Path "dist\duq-tools.exe" -DestinationPath "duq-tools-windows.zip" -Force

echo.
echo =========================================
echo   BUILD COMPLETE!
echo =========================================
echo.
echo Executable: dist\duq-tools.exe
echo ZIP Package: duq-tools-windows.zip
echo.
pause
