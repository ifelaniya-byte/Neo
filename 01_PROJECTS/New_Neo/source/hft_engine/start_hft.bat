@echo off
title HFT Engine - Bitcoin Prediction System
color 0a

echo.
echo    /\
echo   /  \
echo  /____\
echo /      \
echo/__________\
echo.
echo    HFT ENGINE
echo   START SCRIPT
echo.
echo ============================================
echo    Starting Bitcoin Prediction System...
echo ============================================
echo.

cd /d "C:\Users\AIAli\OneDrive\Desktop\NEO\hft_engine"

if not exist main.py (
    echo ERROR: main.py not found!
    echo Please ensure you're in the correct directory.
    pause
    exit /b 1
)

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python to run this program.
    pause
    exit /b 1
)

echo Python found.
echo.
echo ============================================
echo    Starting HFT Engine...
echo ============================================
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ============================================
    echo    Program exited with errors
    echo ============================================
    echo.
) else (
    echo.
    echo ============================================
    echo    Program closed normally
    echo ============================================
    echo.
)

pause