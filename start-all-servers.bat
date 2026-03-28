@echo off
title ConnectSphere Full Stack Server
color 0A
echo.
echo ========================================
echo   ConnectSphere Full Stack Services
echo ========================================
echo.
echo Starting all services...
echo.

REM Get to the correct directory
cd /d "c:\Users\Sai sidharth\social"

REM Activate Python virtual environment
call social\Scripts\activate.bat

echo Creating new terminal windows...
echo.

REM Terminal 1: Redis Server
echo [1/5] Starting Redis Server...
start "Redis Server" cmd /k "redis-server"
timeout /t 2 /nobreak

REM Terminal 2: Django Backend
echo [2/5] Starting Django Backend...
start "Django Backend" cmd /k "cd socialproject && python manage.py runserver"
timeout /t 2 /nobreak

REM Terminal 3: Celery Worker
echo [3/5] Starting Celery Worker...
start "Celery Worker" cmd /k "cd socialproject && celery -A socialproject worker -l info --pool=solo"
timeout /t 2 /nobreak

REM Terminal 4: Celery Beat
echo [4/5] Starting Celery Beat...
start "Celery Beat" cmd /k "cd socialproject && celery -A socialproject beat -l info"
timeout /t 2 /nobreak

REM Terminal 5: React Frontend
echo [5/5] Starting React Frontend...
start "React Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo   All Services Started!
echo ========================================
echo.
echo BACKEND:
echo   - Redis:           http://localhost:6379
echo   - Django API:      http://localhost:8000
echo   - Celery Worker:   Running in background
echo   - Celery Beat:     Running in background
echo.
echo FRONTEND:
echo   - React Dev:       http://localhost:5173
echo.
echo Press any key to close this window...
pause
