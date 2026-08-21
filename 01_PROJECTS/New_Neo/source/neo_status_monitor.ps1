# NEO STATUS MONITOR - PowerShell Script
# Real-time Neo status monitoring and grading system

# Configuration
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$StatusFile = Join-Path $ScriptPath "neo_status.json"
$RefreshInterval = 5  # seconds

# Color schemes
$Colors = @{
    "A+" = "Green"
    "A"  = "Green"
    "B"  = "Cyan"
    "C"  = "Yellow"
    "D"  = "Orange"
    "F"  = "Red"
    "X"  = "DarkGray"
    "NORMAL" = "Green"
    "WARNING" = "Yellow"
    "CRITICAL" = "Red"
    "DEGRADED" = "Magenta"
    "DEAD" = "DarkGray"
}

function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

function Write-SectionHeader {
    param([string]$Title)
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
}

function Write-Metric {
    param(
        [string]$Label,
        [string]$Value,
        [string]$Color = "White"
    )
    $LabelPadded = $Label.PadRight(25)
    Write-Host "  $LabelPadded : " -NoNewline
    Write-ColorText -Text $Value -Color $Color
}

function Write-ProgressBar {
    param(
        [string]$Label,
        [double]$Value,
        [double]$Max = 100
    )
    $Percentage = [math]::Min(($Value / $Max) * 100, 100)
    $BarLength = 30
    $Filled = [math]::Floor(($Percentage / 100) * $BarLength)
    $Empty = $BarLength - $Filled
    
    $Bar = "█" * $Filled + "░" * $Empty
    $Color = if ($Percentage -ge 70) { "Green" } 
             elseif ($Percentage -ge 50) { "Yellow" } 
             else { "Red" }
    
    Write-Host "  $Label : " -NoNewline
    Write-Host "[$Bar]" -ForegroundColor $Color -NoNewline
    Write-Host " $Percentage.ToString("0.0")%" -ForegroundColor White
}

function Get-NeoStatus {
    # Try to get status from Python API
    try {
        $Response = Invoke-RestMethod -Uri "http://localhost:8000/api/neo-status" -ErrorAction Stop
        return $Response
    }
    catch {
        # Fallback to JSON file
        if (Test-Path $StatusFile) {
            $Json = Get-Content $StatusFile -Raw | ConvertFrom-Json
            return $Json
        }
        else {
            # Return mock data if nothing available
            return Get-MockStatus
        }
    }
}

function Get-MockStatus {
    return @{
        timestamp = (Get-Date).ToString("o")
        system_state = "AUTONOMOUS"
        phase = "AUTONOMOUS"
        survival = @{
            total_units = 500000000
            frozen_units = 1250
            frozen_percentage = 0.00025
            consecutive_failures = 5
            total_failures = 15
            total_successes = 145
            survival_score = 0.987
            memory_punishment_rate = 2.0
            state = "NORMAL"
        }
        performance = @{
            accuracy = 0.92
            loss = 0.15
            mmlu_score = 72.5
            humaneval_score = 65.0
            inference_time_ms = 45.2
            memory_usage_gb = 1.8
            parameter_count = 485000000
            efficiency_score = 0.15
        }
        api = @{
            cache_hit_rate = 0.78
            efficiency_score = 0.82
            total_api_calls = 1250
            cached_calls = 975
            credits_spent = 12.50
            credits_saved = 45.00
            target_cache_hit_rate = 0.7
            target_efficiency_score = 0.7
        }
        karpathy_loop = @{
            iteration = 1250
            total_iterations = 1250
            improvements_committed = 875
            modifications_reverted = 375
            commit_rate = 0.70
            average_improvement = 0.025
            state = "RUNNING"
        }
        grades = @{
            overall_grade = "A"
            survival_grade = "A+"
            performance_grade = "A"
            api_grade = "A"
            loop_grade = "B"
            overall_score = 88.5
            weighted_score = 3.54
        }
        alerts = @(
            "API efficiency approaching target threshold",
            "Memory punishment rate at 2x (post-graduation)"
        )
        last_update = (Get-Date).ToString("o")
    }
}

function Show-NeoStatus {
    param([object]$Status)
    
    Clear-Host
    
    # Header
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                                              ║" -ForegroundColor Cyan
    Write-Host "║                    🚀 NEO STATUS MONITOR - PowerShell                     ║" -ForegroundColor Cyan
    Write-Host "║                                                                              ║" -ForegroundColor Cyan
    Write-Host "║                  Real-time Monitoring & Grading System                      ║" -ForegroundColor Cyan
    Write-Host "║                                                                              ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    # Overall Grade Display
    $OverallGrade = $Status.grades.overall_grade
    $GradeColor = if ($Colors.ContainsKey($OverallGrade)) { $Colors[$OverallGrade] } else { "White" }
    
    Write-Host "                        OVERALL GRADE: " -NoNewline
    Write-Host " $($OverallGrade) " -BackgroundColor $GradeColor -ForegroundColor Black -NoNewline
    Write-Host ""
    Write-Host "                        Overall Score: $($Status.grades.overall_score.ToString("0.0"))/100" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "                    Press CTRL+C to exit | Auto-refresh: $($RefreshInterval)s" -ForegroundColor Gray
    Write-Host ""
    
    # System State
    Write-SectionHeader "🎯 SYSTEM STATE"
    Write-Metric "State" $Status.system_state "Cyan"
    Write-Metric "Phase" $Status.phase "Cyan"
    Write-Metric "Last Update" $Status.last_update "Gray"
    
    # Survival Metrics
    Write-SectionHeader "💪 SURVIVAL METRICS (Weight: 40%)"
    $SurvivalGrade = $Status.grades.survival_grade
    $SurvivalColor = if ($Colors.ContainsKey($SurvivalGrade)) { $Colors[$SurvivalGrade] } else { "White" }
    Write-Metric "Survival Grade" $SurvivalGrade $SurvivalColor
    Write-Metric "Survival Score" $Status.survival.survival_score.ToString("0.000") "Cyan"
    Write-Metric "Frozen Units" $Status.survival.frozen_units.ToString("N0") "Yellow"
    Write-Metric "Frozen %" "$($Status.survival.frozen_percentage.ToString("0.0000"))%" "Yellow"
    Write-Metric "Consecutive Failures" $Status.survival.consecutive_failures.ToString("N0") "Red"
    
    $SurvivalState = $Status.survival.state
    $StateColor = if ($Colors.ContainsKey($SurvivalState)) { $Colors[$SurvivalState] } else { "White" }
    Write-Metric "State" $SurvivalState $StateColor
    Write-Metric "Punishment Rate" "$($Status.survival.memory_punishment_rate)x" "Magenta"
    
    # Performance Metrics
    Write-SectionHeader "⚡ PERFORMANCE METRICS (Weight: 30%)"
    $PerfGrade = $Status.grades.performance_grade
    $PerfColor = if ($Colors.ContainsKey($PerfGrade)) { $Colors[$PerfGrade] } else { "White" }
    Write-Metric "Performance Grade" $PerfGrade $PerfColor
    Write-Metric "Accuracy" "$($Status.performance.accuracy.ToString("0.0"))%" "Green"
    Write-Metric "Loss" $Status.performance.loss.ToString("0.0000") "Cyan"
    Write-Metric "MMLU Score" $Status.performance.mmlu_score.ToString("0.0") "Green"
    Write-Metric "HumanEval Score" $Status.performance.humaneval_score.ToString("0.0") "Green"
    Write-Metric "Inference Time" "$($Status.performance.inference_time_ms.ToString("0.0"))ms" "Cyan"
    Write-Metric "Memory Usage" "$($Status.performance.memory_usage_gb.ToString("0.00"))GB" "Yellow"
    Write-Metric "Parameter Count" $Status.performance.parameter_count.ToString("N0") "Cyan"
    
    # API Metrics
    Write-SectionHeader "💰 API METRICS (Weight: 20%)"
    $ApiGrade = $Status.grades.api_grade
    $ApiColor = if ($Colors.ContainsKey($ApiGrade)) { $Colors[$ApiGrade] } else { "White" }
    Write-Metric "API Grade" $ApiGrade $ApiColor
    Write-Metric "Cache Hit Rate" "$($Status.api.cache_hit_rate.ToString("0.0"))%" "Green"
    Write-ProgressBar "Cache Hit Rate" $Status.api.cache_hit_rate 1.0
    Write-Metric "Efficiency Score" $Status.api.efficiency_score.ToString("0.000") "Cyan"
    Write-ProgressBar "Efficiency Score" $Status.api.efficiency_score 1.0
    Write-Metric "Total API Calls" $Status.api.total_api_calls.ToString("N0") "Cyan"
    Write-Metric "Cached Calls" $Status.api.cached_calls.ToString("N0") "Green"
    Write-Metric "Credits Spent" "`$$($Status.api.credits_spent.ToString("0.00"))" "Yellow"
    Write-Metric "Credits Saved" "`$$($Status.api.credits_saved.ToString("0.00"))" "Green"
    
    # Karpathy Loop Metrics
    Write-SectionHeader "🔄 KARPATHY LOOP (Weight: 10%)"
    $LoopGrade = $Status.grades.loop_grade
    $LoopColor = if ($Colors.ContainsKey($LoopGrade)) { $Colors[$LoopGrade] } else { "White" }
    Write-Metric "Loop Grade" $LoopGrade $LoopColor
    Write-Metric "Iteration" $Status.karpathy_loop.iteration.ToString("N0") "Cyan"
    Write-Metric "Improvements Committed" $Status.karpathy_loop.improvements_committed.ToString("N0") "Green"
    Write-Metric "Modifications Reverted" $Status.karpathy_loop.modifications_reverted.ToString("N0") "Red"
    Write-Metric "Commit Rate" "$($Status.karpathy_loop.commit_rate.ToString("0.0"))%" "Cyan"
    Write-ProgressBar "Commit Rate" $Status.karpathy_loop.commit_rate 1.0
    Write-Metric "Average Improvement" "$($Status.karpathy_loop.average_improvement.ToString("0.0"))%" "Green"
    Write-Metric "State" $Status.karpathy_loop.state "Cyan"
    
    # Weighted Score Breakdown
    Write-SectionHeader "📊 WEIGHTED SCORE BREAKDOWN"
    
    # Calculate weighted scores
    $SurvivalPoints = switch ($Status.grades.survival_grade) {
        "A+" { 4.0 } "A" { 3.5 } "B" { 3.0 } "C" { 2.0 } "D" { 1.0 } default { 0.0 }
    }
    $PerfPoints = switch ($Status.grades.performance_grade) {
        "A+" { 4.0 } "A" { 3.5 } "B" { 3.0 } "C" { 2.0 } "D" { 1.0 } default { 0.0 }
    }
    $ApiPoints = switch ($Status.grades.api_grade) {
        "A+" { 4.0 } "A" { 3.5 } "B" { 3.0 } "C" { 2.0 } "D" { 1.0 } default { 0.0 }
    }
    $LoopPoints = switch ($Status.grades.loop_grade) {
        "A+" { 4.0 } "A" { 3.5 } "B" { 3.0 } "C" { 2.0 } "D" { 1.0 } default { 0.0 }
    }
    
    $SurvivalWeighted = $SurvivalPoints * 0.40
    $PerfWeighted = $PerfPoints * 0.30
    $ApiWeighted = $ApiPoints * 0.20
    $LoopWeighted = $LoopPoints * 0.10
    $TotalWeighted = $SurvivalWeighted + $PerfWeighted + $ApiWeighted + $LoopWeighted
    
    Write-Metric "Survival (40%)" $SurvivalWeighted.ToString("0.00") "Cyan"
    Write-ProgressBar "Survival Weighted" $SurvivalWeighted 1.6
    Write-Metric "Performance (30%)" $PerfWeighted.ToString("0.00") "Cyan"
    Write-ProgressBar "Performance Weighted" $PerfWeighted 1.2
    Write-Metric "API (20%)" $ApiWeighted.ToString("0.00") "Cyan"
    Write-ProgressBar "API Weighted" $ApiWeighted 0.8
    Write-Metric "Loop (10%)" $LoopWeighted.ToString("0.00") "Cyan"
    Write-ProgressBar "Loop Weighted" $LoopWeighted 0.4
    Write-Metric "Total Weighted" $TotalWeighted.ToString("0.00") "Green"
    
    # Alerts
    if ($Status.alerts -and $Status.alerts.Count -gt 0) {
        Write-SectionHeader "⚠️ ACTIVE ALERTS"
        foreach ($Alert in $Status.alerts) {
            Write-Host "  ⚠ $Alert" -ForegroundColor Red
        }
    }
    
    # Footer
    Write-Host ""
    Write-Host "══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Gray
    Write-Host "  Neo Status Monitor | Project APEX | Auto-refresh: $($RefreshInterval)s" -ForegroundColor Gray
    Write-Host "  Last updated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host "══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Gray
    Write-Host ""
}

function Start-NeoStatusMonitor {
    param(
        [int]$RefreshSeconds = $RefreshInterval
    )
    
    Write-Host "Starting Neo Status Monitor..." -ForegroundColor Green
    Write-Host "Refresh interval: $RefreshSeconds seconds" -ForegroundColor Cyan
    Write-Host "Press CTRL+C to exit" -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    
    while ($true) {
        try {
            $Status = Get-NeoStatus
            Show-NeoStatus -Status $Status
        }
        catch {
            Write-Host "Error fetching status: $_" -ForegroundColor Red
        }
        
        Start-Sleep -Seconds $RefreshSeconds
    }
}

# Main execution
try {
    Start-NeoStatusMonitor -RefreshSeconds $RefreshInterval
}
catch {
    Write-Host "Neo Status Monitor stopped." -ForegroundColor Yellow
    Write-Host "Error: $_" -ForegroundColor Red
}
