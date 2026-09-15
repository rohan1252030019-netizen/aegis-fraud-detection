# AEGIS Windows Launch Script
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Starting AEGIS Fraud Detection Suite    " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$Root = Split-Path -Parent $PSScriptRoot
$ApiDir = Join-Path $Root "apps\api"
$WebDir = Join-Path $Root "apps\web"

# 1. Start FastAPI Backend in new window
Write-Host "[1/2] Starting FastAPI Backend on http://localhost:8000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ApiDir'; python -m uvicorn app.main:app --reload --port 8000"

# 2. Start Next.js Frontend in new window
Write-Host "[2/2] Starting Next.js Web on http://localhost:3000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$WebDir'; npm run dev"

Write-Host ""
Write-Host "✅ Both services are launching in dedicated windows!" -ForegroundColor Green
Write-Host "Web Interface: http://localhost:3000" -ForegroundColor White
Write-Host "API Swagger:   http://localhost:8000/docs" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
