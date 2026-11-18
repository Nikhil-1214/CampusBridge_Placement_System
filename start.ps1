Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "      CampusBridge - NSUT Placement Portal" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Set-Location $PSScriptRoot

Write-Host "Credentials for Login:" -ForegroundColor Yellow
Write-Host "  - Admin:   NSUT ID: ADMIN001      Password: admin123" -ForegroundColor Yellow
Write-Host "  - Student: NSUT ID: 2024NSUT1001  Password: student123" -ForegroundColor Yellow
Write-Host ""
Write-Host "Starting server on http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process "http://127.0.0.1:8000"
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
