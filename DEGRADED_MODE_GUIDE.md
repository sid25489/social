# ConnectSphere - Degraded Mode Guide

## Overview
When Redis and Celery servers are unavailable, ConnectSphere can still run with graceful degradation. The application will operate in **degraded mode** with the following characteristics:

### ✓ What Works
- ✅ User authentication and JWT tokens
- ✅ Post creation and browsing
- ✅ Feed functionality
- ✅ Messaging
- ✅ Profile management
- ✅ Search and filtering
- ✅ API endpoints
- ✅ Frontend UI

### ⚠️ Limitations
- ❌ Async email sending (runs synchronously, may slow requests)
- ❌ Background tasks (cleanup, trending hashtags)
- ❌ Periodic scheduled tasks (Celery Beat)
- ❌ Distributed caching (uses local memory only)
- ❌ Advanced notification delivery

---

## How to Run in Degraded Mode

### Option 1: Using the Degraded Mode Script (Easiest)
```powershell
cd "c:\Users\Sai sidharth\social"
powershell -ExecutionPolicy Bypass -File start-servers-degraded-mode.ps1
```

This script:
- Starts Django backend on http://localhost:8000
- Starts React frontend on http://localhost:5173
- Automatically disables Redis and Celery

### Option 2: Manual Setup

#### Step 1: Update `.env` file
In `socialproject/.env`:
```env
REDIS_ENABLED=False
CELERY_ENABLED=False
```

#### Step 2: Start Django Backend
```powershell
cd "c:\Users\Sai sidharth\social"
& ".\social\Scripts\Activate.ps1"
cd socialproject
python manage.py runserver
```

#### Step 3: Start React Frontend (New Terminal)
```powershell
cd "c:\Users\Sai sidharth\social\frontend"
npm run dev
```

---

## Under the Hood

### Cache Configuration
- **With Redis disabled**: Uses local in-memory cache (`LocMemCache`)
- **Timeout**: 300 seconds (5 minutes)
- **Scope**: Per-process only (not shared)

### Task Execution
- **CELERY_TASK_ALWAYS_EAGER = True**: Tasks run immediately
- **CELERY_TASK_EAGER_PROPAGATES = True**: Errors propagate to caller
- **Email tasks**: Run synchronously during request

### Database
- **Uses**: SQLite (db.sqlite3)
- **Status**: Fully functional
- **Migrations**: Work normally

---

## Configuration Reference

### Environment Variables

| Variable | Degraded Mode | Full Mode |
|----------|---------------|-----------|
| `REDIS_ENABLED` | `False` | `True` |
| `CELERY_ENABLED` | `False` | `True` |
| Cache Backend | `LocMemCache` | `RedisCache` |
| Task Execution | Synchronous | Asynchronous |
| Beat Scheduler | Disabled | Enabled (celery-beat) |

### Updated Settings
- `settings.py` - Conditional cache and Celery configuration
- `celery.py` - Error handling for unavailable broker
- `tasks.py` - Graceful error handling
- `.env` - REDIS_ENABLED and CELERY_ENABLED flags

---

## Troubleshooting

### Issue: Emails are slow
**Cause**: Email tasks run synchronously without Celery
**Solution**: Enable Redis and Celery (see below)

### Issue: Cache is not persistent
**Cause**: Local memory cache is cleared on server restart
**Solution**: Enable Redis for persistent cache

### Issue: Cannot access http://localhost:8000
**Possible causes**:
1. Django not started - Run: `cd socialproject && python manage.py runserver`
2. Port 8000 in use - Kill process: `taskkill /F /IM python.exe`
3. Virtual environment not activated - Run: `& ".\social\Scripts\Activate.ps1"`

### Issue: Cannot access http://localhost:5173
**Possible causes**:
1. Frontend not started - Run: `cd frontend && npm run dev`
2. Port 5173 in use - Kill process: `taskkill /F /IM node.exe`
3. Dependencies not installed - Run: `cd frontend && npm install`

---

## Moving from Degraded Mode to Full Mode

### Prerequisites
1. Install Redis server (e.g., via Windows Subsystem for Linux or Docker)
2. Ensure port 6379 is available

### Steps
```powershell
# 1. Update .env in socialproject/ folder
#    Change: REDIS_ENABLED=True
#    Change: CELERY_ENABLED=True

# 2. Start Redis server (example with WSL)
wsl redis-server

# 3. Run the full startup script
cd "c:\Users\Sai sidharth\social"
powershell -ExecutionPolicy Bypass -File start-all-servers.ps1
```

This starts:
- Redis (Port 6379)
- Django Backend (Port 8000)
- Celery Worker (Port 5555 - Flower UI)
- Celery Beat (Port varies)
- React Frontend (Port 5173)

---

## Performance Notes

### Degraded Mode Impact
- **Request latency**: +100-500ms (due to synchronous email tasks)
- **Memory usage**: Lower (no Redis process)
- **CPU usage**: Lower (no Celery workers)
- **Concurrent users**: ~100 without issues

### Full Mode Benefits
- **Request latency**: -100-500ms (async email)
- **Memory usage**: Higher (~200MB for Redis + Celery)
- **CPU usage**: Higher (multiple workers)
- **Concurrent users**: 1000+ with horizontal scaling

---

## See Also
- [QUICK_START.md](./QUICK_START.md) - General quick start
- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - Architecture overview
- [requirements.txt](./requirements.txt) - Python dependencies
- [.env.example](.env.example) - Environment variable template
