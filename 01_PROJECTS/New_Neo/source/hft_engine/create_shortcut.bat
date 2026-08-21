@echo off
REM Create a desktop shortcut that can be pinned to taskbar

set SCRIPT_DIR=%~dp0
set SHORTCUT_NAME=HFT Engine.lnk
set DESKTOP=%USERPROFILE%\Desktop

echo Creating shortcut for HFT Engine...

REM Use PowerShell to create the shortcut
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP%\%SHORTCUT_NAME%'); $s.TargetPath = '%SCRIPT_DIR%start_hft.bat'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Description = 'Bitcoin HFT Prediction Engine'; $s.Save()"

echo.
echo Shortcut created on desktop: %DESKTOP%\%SHORTCUT_NAME%
echo.
echo You can now:
echo 1. Right-click the shortcut on your desktop
echo 2. Select "Pin to taskbar"
echo 3. The HFT Engine will be on your taskbar for easy access
echo.
pause