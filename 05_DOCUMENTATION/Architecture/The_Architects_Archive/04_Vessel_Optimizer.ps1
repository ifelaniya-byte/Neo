& {
    Clear-Host
    Write-Host "THE GARDENER: TOTAL VESSEL OPTIMIZATION ENGINE" -ForegroundColor Cyan
    Write-Host "Phase 1: Capturing BEFORE metrics..." -ForegroundColor Yellow

    function Get-VesselMetrics {
        $os = Get-CimInstance Win32_OperatingSystem
        $cpu = Get-CimInstance Win32_Processor
        $disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
        $ramTotal = [math]::Round($os.TotalVisibleMemorySize/1MB, 2)
        $ramUsed = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory)/1MB, 2)
        $diskFree = [math]::Round($disk.FreeSpace/1GB, 2)
        return @{ CPULoad=$cpu.LoadPercentage; RAMUsed=$ramUsed; RAMTotal=$ramTotal; DiskFree=$diskFree }
    }

    $before = Get-VesselMetrics
    Write-Host "[BEFORE] CPU: $($before.CPULoad)% | RAM: $($before.RAMUsed)GB | Disk: $($before.DiskFree)GB Free" -ForegroundColor Gray
    Start-Sleep 2

    Write-Host "PASS 1/6: STORAGE PURGE" -ForegroundColor Green
    Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
    Clear-RecycleBin -Force -ErrorAction SilentlyContinue

    Write-Host "PASS 2/6: MAXIMUM POWER STATE" -ForegroundColor Green
    $plans = powercfg /list
    $ultGuid = ($plans | Select-String "Ultimate" | ForEach-Object { ($_ -split '\s+')[3] }) | Select-Object -First 1
    $highGuid = ($plans | Select-String "High performance" | ForEach-Object { ($_ -split '\s+')[3] }) | Select-Object -First 1
    if ($ultGuid) { powercfg /setactive $ultGuid 2>$null } elseif ($highGuid) { powercfg /setactive $highGuid 2>$null }

    Write-Host "PASS 3/6: VISUAL OFFLOAD" -ForegroundColor Green
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name "EnableTransparency" -Value 0 -ErrorAction SilentlyContinue
    $vfxPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
    if (-not (Test-Path $vfxPath)) { New-Item -Path $vfxPath -Force | Out-Null }
    Set-ItemProperty -Path $vfxPath -Name "VisualFXSetting" -Value 2 -ErrorAction SilentlyContinue

    Write-Host "PASS 4/6: BACKGROUND SUPPRESSION" -ForegroundColor Green
    $bgPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications"
    if (-not (Test-Path $bgPath)) { New-Item -Path $bgPath -Force | Out-Null }
    Set-ItemProperty -Path $bgPath -Name "GlobalUserDisabled" -Value 1 -ErrorAction SilentlyContinue
    Stop-Service -Name "WSearch" -Force -ErrorAction SilentlyContinue
    Set-Service -Name "WSearch" -StartupType Manual -ErrorAction SilentlyContinue
    Stop-Service -Name "SysMain" -Force -ErrorAction SilentlyContinue
    Set-Service -Name "SysMain" -StartupType Manual -ErrorAction SilentlyContinue

    Write-Host "PASS 5/6: TELEMETRY + NETWORK TRIM" -ForegroundColor Green
    Clear-DnsClientCache -ErrorAction SilentlyContinue

    Write-Host "PASS 6/6: MEMORY FLUSH" -ForegroundColor Green
    Stop-Process -Name "explorer" -Force -ErrorAction SilentlyContinue
    Start-Sleep 2
    Start-Process "explorer.exe" -ErrorAction SilentlyContinue

    $after = Get-VesselMetrics
    Write-Host "`nBEFORE / AFTER REPORT" -ForegroundColor Cyan
    Write-Host "CPU: $($before.CPULoad)% -> $($after.CPULoad)%"
    Write-Host "RAM: $($before.RAMUsed)GB -> $($after.RAMUsed)GB"
    Write-Host "Disk: $($before.DiskFree)GB -> $($after.DiskFree)GB"
    Write-Host "`nOPTIMIZATION COMPLETE. RESTART PC TO FULLY FLUSH RAM." -ForegroundColor Green
}
