# NationBot Backend Startup Script (PowerShell)
# Uses Python 3.13 with all dependencies installed

$PYTHON = "C:\Users\Rentorzo\AppData\Local\Programs\Python\Python313\python.exe"

Write-Host "Starting NationBot API server..." -ForegroundColor Cyan
Write-Host "Python: $PYTHON" -ForegroundColor DarkGray
Write-Host ""

Set-Location $PSScriptRoot
& $PYTHON -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
