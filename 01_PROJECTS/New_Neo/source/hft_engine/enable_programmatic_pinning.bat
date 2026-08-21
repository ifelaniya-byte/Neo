@echo off
REM Enable Programmatic Taskbar Pinning
REM This script checks and modifies registry settings to allow programmatic taskbar pinning

echo ============================================
echo    Checking Current Pinning Restrictions
echo ============================================
echo.

echo Checking registry for pinning restrictions...
reg query "HKCU\Software\Policies\Microsoft\Windows\Explorer" /v "NoPinningToTaskbar" >nul 2>&1
if errorlevel 1 (
    echo [OK] No pinning restrictions found in user policy
) else (
    echo [WARNING] Pinning restriction found in user policy
    echo.
    echo Removing restriction...
    reg delete "HKCU\Software\Policies\Microsoft\Windows\Explorer" /v "NoPinningToTaskbar" /f >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to remove restriction
    ) else (
        echo [SUCCESS] Restriction removed successfully
    )
)

echo.
echo Checking system-wide pinning restrictions...
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\Explorer" /v "NoPinningToTaskbar" >nul 2>&1
if errorlevel 1 (
    echo [OK] No pinning restrictions found in system policy
) else (
    echo [WARNING] Pinning restriction found in system policy
    echo.
    echo Removing restriction...
    reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\Explorer" /v "NoPinningToTaskbar" /f >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to remove restriction
        echo.
        echo [NOTE] System policy removal may require administrator privileges
        echo Try running this script as administrator
    ) else (
        echo [SUCCESS] Restriction removed successfully
    )
)

echo.
echo ============================================
echo    Creating Registry Key for Allowed Pinning
echo ============================================
echo.

REM Create registry key to explicitly allow pinning
reg add "HKCU\Software\Microsoft\Windows\Explorer" /v "NoPinningToTaskbar" /t REG_DWORD /d 0 /f >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Could not set explicit allow policy
) else (
    echo [SUCCESS] Set explicit allow policy for pinning
)

echo.
echo ============================================
echo    Configuration Complete
echo ============================================
echo.
echo Programmatic taskbar pinning should now be enabled.
echo You may need to restart your computer for changes to take effect.
echo.
echo After restart, you can:
echo 1. Use the HFT Engine shortcut on your desktop
echo 2. Right-click and select "Pin to taskbar"
echo 3. Or use programmatic methods if implemented
echo.
pause