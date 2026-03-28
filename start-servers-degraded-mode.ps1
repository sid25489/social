# PowerShell Script to Start ConnectSphere in Degraded Mode
# (Without Redis and Celery)
# Run with: powershell -ExecutionPolicy Bypass -File start-servers-degraded-mode.ps1

$currentDir = "c:\Users\Sai sidharth\social"
Set-Location $currentDir

Write-Host "========================================" -ForegroundColor Green
Write-Host "  ConnectSphere Degraded Mode" -ForegroundColor Green
Write-Host "  (Without Redis & Celery)" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ".\social\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Starting services in new windows..." -ForegroundColor Yellow
Write-Host "⚠️  Note: Redis and Celery are DISABLED" -ForegroundColor Red
Write-Host "⚠️  Async tasks will run synchronously" -ForegroundColor Red
Write-Host "⚠️  Caching will use local memory only" -ForegroundColor Red
Write-Host ""

# Terminal 1: Django Backend
Write-Host "[1/2] Starting Django Backend..." -ForegroundColor Cyan
Write-Host "      URL: http://localhost:8000" -ForegroundColor Gray
$djangoArgs = '/k "cd socialproject && python manage.py runserver"'
Start-Process -FilePath "cmd" -ArgumentList $djangoArgs -WindowStyle Normal

Start-Sleep -Seconds 3

# Terminal 2: React Frontend
Write-Host "[2/2] Starting React Frontend..." -ForegroundColor Cyan
Write-Host "      URL: http://localhost:5173" -ForegroundColor Gray
$frontendArgs = '/k "cd frontend && npm run dev"'
Start-Process -FilePath "cmd" -ArgumentList $frontendArgs -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Services started successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Available Services:" -ForegroundColor Yellow
Write-Host "  ✓ Django API   : http://localhost:8000/api/" -ForegroundColor Green
Write-Host "  ✓ React UI     : http://localhost:5173" -ForegroundColor Green
Write-Host "  ✗ Redis        : DISABLED" -ForegroundColor Red
Write-Host "  ✗ Celery Worker: DISABLED" -ForegroundColor Red
Write-Host "  ✗ Celery Beat  : DISABLED" -ForegroundColor Red
Write-Host ""
Write-Host "Limitations in degraded mode:" -ForegroundColor Yellow
Write-Host "  • Email tasks run synchronously (may slow down requests)" -ForegroundColor Gray
Write-Host "  • Caching uses local memory (not shared across processes)" -ForegroundColor Gray
Write-Host "  • Background jobs don't execute asynchronously" -ForegroundColor Gray
Write-Host "  • No periodic task scheduling" -ForegroundColor Gray
Write-Host ""
Write-Host "To enable Redis & Celery:" -ForegroundColor Yellow
Write-Host "  1. Start Redis server" -ForegroundColor Gray
Write-Host "  2. Update .env: REDIS_ENABLED=True, CELERY_ENABLED=True" -ForegroundColor Gray
Write-Host "  3. Run: powershell -ExecutionPolicy Bypass -File start-all-servers.ps1" -ForegroundColor Gray
Write-Host ""
