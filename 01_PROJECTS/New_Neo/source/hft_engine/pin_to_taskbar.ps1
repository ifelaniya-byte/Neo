# PowerShell script to pin HFT Engine to taskbar
$WshShell = New-Object -ComObject WScript.Shell
$shell = New-Object -ComObject Shell.Application

# Refresh desktop to ensure shortcut is visible
$shell.ToggleDesktopIcons()
Start-Sleep -Seconds 2
$shell.ToggleDesktopIcons()

# Get the shortcut path
$shortcutPath = "C:\Users\AIAli\Desktop\HFT Engine.lnk"

# Check if shortcut exists
if (Test-Path $shortcutPath) {
    Write-Host "Shortcut found at: $shortcutPath"
    
    # Try to pin using Windows shell
    try {
        # This method simulates a right-click and pin operation
        $verb = $WshShell.NameSpace(0x10).ParseName($shortcutPath).Verbs()
        foreach ($v in $verb) {
            if ($v.Name -eq "Pin to taskbar") {
                $v.DoIt()
                Write-Host "Successfully pinned to taskbar!"
                break
            }
        }
    }
    catch {
        Write-Host "Could not programmatically pin (security restriction)"
        Write-Host "Please manually right-click the shortcut and select 'Pin to taskbar'"
    }
} else {
    Write-Host "Shortcut not found at: $shortcutPath"
    Write-Host "Please ensure the shortcut exists on your desktop"
}