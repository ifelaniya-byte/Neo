# HFT Engine PowerShell Start Script
# Black Pyramid Theme

Write-Host ""
Write-Host "    /\" -ForegroundColor Gray
Write-Host "   /  \" -ForegroundColor Gray
Write-Host "  /____\" -ForegroundColor Gray
Write-Host " /      \" -ForegroundColor Gray
Write-Host "/__________\" -ForegroundColor Gray
Write-Host ""
Write-Host "    HFT ENGINE" -ForegroundColor Yellow
Write-Host "   START SCRIPT" -ForegroundColor Green
Write-Host ""
Write-Host "============================================" -ForegroundColor Gray
Write-Host "   Starting Bitcoin Prediction System..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Gray
Write-Host ""

# Navigate to the correct directory
Set-Location "C:\Users\AIAli\OneDrive\Desktop\NEO\hft_engine"

# Check if main.py exists
if (-not (Test-Path "main.py")) {
    Write-Host "ERROR: main.py not found!" -ForegroundColor Red
    Write-Host "Please ensure you're in the correct directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python to run this program." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Gray
Write-Host "   Starting HFT Engine..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Gray
Write-Host ""

# Start the HFT engine
python main.py

# Handle exit
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Gray
    Write-Host "   Program closed normally" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Gray
    Write-Host "   Program exited with errors" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Gray
    Write-Host ""
}

Read-Host "Press Enter to exit"