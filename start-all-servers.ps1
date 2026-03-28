# PowerShell Script to Start All ConnectSphere Services
# Run with: powershell -ExecutionPolicy Bypass -File start-all-servers.ps1

$currentDir = "c:\Users\Sai sidharth\social"
Set-Location $currentDir

Write-Host "========================================" -ForegroundColor Green
Write-Host "  ConnectSphere Full Stack Services" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
& ".\social\Scripts\Activate.ps1"

Write-Host "Starting all services in new windows..." -ForegroundColor Yellow
Write-Host ""

# Terminal 1: Redis Server
Write-Host "[1/5] Starting Redis Server..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/k redis-server" -WindowStyle Normal

Start-Sleep -Seconds 2

# Terminal 2: Django Backend
Write-Host "[2/5] Starting Django Backend..." -ForegroundColor Cyan
$djangoArgs = '/k "cd socialproject && python manage.py runserver"'
Start-Process -FilePath "cmd" -ArgumentList $djangoArgs -WindowStyle Normal

Start-Sleep -Seconds 2

# Terminal 3: Celery Worker
Write-Host "[3/5] Starting Celery Worker..." -ForegroundColor Cyan
$celeryWorkerArgs = '/k "cd socialproject && celery -A socialproject worker -l info --pool=solo"'
Start-Process -FilePath "cmd" -ArgumentList $celeryWorkerArgs -WindowStyle Normal

Start-Sleep -Seconds 2

# Terminal 4: Celery Beat
Write-Host "[4/5] Starting Celery Beat..." -ForegroundColor Cyan
$celeryBeatArgs = '/k "cd socialproject && celery -A socialproject beat -l info"'
Start-Process -FilePath "cmd" -ArgumentList $celeryBeatArgs -WindowStyle Normal

Start-Sleep -Seconds 2

# Terminal 5: React Frontend
Write-Host "[5/5] Starting React Frontend..." -ForegroundColor Cyan
$frontendArgs = '/k "cd frontend && npm run dev"'
Start-Process -FilePath "cmd" -ArgumentList $frontendArgs -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   All Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "BACKEND:" -ForegroundColor Yellow
Write-Host "   - Redis:           http://localhost:6379" -ForegroundColor White
Write-Host "   - Django API:      http://localhost:8000" -ForegroundColor White
Write-Host "   - Celery Worker:   Running in background" -ForegroundColor White
Write-Host "   - Celery Beat:     Running in background" -ForegroundColor White
Write-Host ""
Write-Host "FRONTEND:" -ForegroundColor Yellow
Write-Host "   - React Dev:       http://localhost:5173" -ForegroundColor White
Write-Host ""
