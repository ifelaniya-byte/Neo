& {
    $Host.UI.RawUI.WindowTitle = "THE GARDENER: VESSEL COMMAND DASHBOARD"
    while ($true) {
        Clear-Host
        $os = Get-CimInstance Win32_OperatingSystem
        $cpu = Get-CimInstance Win32_Processor
        $disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
        $ramTotal = [math]::Round($os.TotalVisibleMemorySize/1MB, 1)
        $ramUsed = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory)/1MB, 1)
        $ramPct = [math]::Round(($ramUsed/$ramTotal)*100, 0)
        $diskFree = [math]::Round($disk.FreeSpace/1GB, 1)
        $diskTotal = [math]::Round($disk.Size/1GB, 1)
        $topProcs = Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 5
        
        Write-Host "=" * 65 -ForegroundColor DarkCyan
        Write-Host "  THE GARDENER: VESSEL COMMAND DASHBOARD (LIVE)" -ForegroundColor Cyan
        Write-Host "=" * 65 -ForegroundColor DarkCyan
        Write-Host "  CPU: $($cpu.LoadPercentage)% | RAM: $ramUsed GB ($ramPct%) | Disk: $diskFree GB Free"
        Write-Host "`n  [TOP MEMORY CONSUMERS]" -ForegroundColor White
        foreach ($p in $topProcs) { Write-Host "   - $($p.ProcessName) -> $([math]::Round($p.WorkingSet64/1MB, 0)) MB" }
        
        Write-Host "`n  [COMMANDS]" -ForegroundColor Green
        Write-Host "   [1] Kill Top Process   [2] Flush DNS   [3] Purge Temp"
        Write-Host "   [4] High Performance   [5] Restart UI  [Q] Quit"
        
        $choice = Read-Host "`n  > COMMAND"
        switch ($choice.ToUpper()) {
            '1' { Stop-Process -Id $topProcs[0].Id -Force -ErrorAction SilentlyContinue }
            '2' { Clear-DnsClientCache }
            '3' { Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue; Clear-RecycleBin -Force -ErrorAction SilentlyContinue }
            '4' { $plans = powercfg /list; $ultGuid = ($plans | Select-String "Ultimate" | ForEach-Object { ($_ -split '\s+')[3] }) | Select-Object -First 1; if ($ultGuid) { powercfg /setactive $ultGuid } }
            '5' { Stop-Process -Name "explorer" -Force -ErrorAction SilentlyContinue; Start-Sleep 2; Start-Process "explorer.exe" }
            'Q' { $Host.UI.RawUI.WindowTitle = "Windows PowerShell"; break }
        }
    }
}
