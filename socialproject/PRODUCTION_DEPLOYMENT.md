# Production Deployment Checklist

## Server Setup

### 1. Environment & Dependencies
```bash
# Install Python 3.12+
python --version

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install production server
pip install gunicorn psycopg2-binary redis celery
```

### 2. Database Setup (PostgreSQL)
```bash
# Install PostgreSQL
# On Ubuntu: sudo apt-get install postgresql postgresql-contrib
# On macOS: brew install postgresql
# On Windows: Download from https://www.postgresql.org/download/windows/

# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE connectsphere_db;
CREATE USER connectsphere WITH PASSWORD 'strong_password_here';
ALTER ROLE connectsphere SET client_encoding TO 'utf8';
ALTER ROLE connectsphere SET default_transaction_isolation TO 'read committed';
ALTER ROLE connectsphere SET default_transaction_deferrable TO on;
ALTER ROLE connectsphere SET default_transaction_level TO 'read committed';
ALTER ROLE connectsphere SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE connectsphere_db TO connectsphere;
\q
```

### 3. Environment Configuration
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env with production values
nano .env  # or your preferred editor
```

**Critical settings to update in .env:**
- `DEBUG=False`
- `SECRET_KEY=` (generate a strong key)
- `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com`
- `DB_*=` (PostgreSQL credentials)
- `SECURE_*=True` (all security settings)

### 4. Generate Secret Key
```python
python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
```

## Server Configuration

### Gunicorn (Production WSGI Server)
Create `gunicorn_config.py`:
```python
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

### Nginx (Reverse Proxy)
Create `/etc/nginx/sites-available/connectsphere`:
```nginx
upstream connectsphere {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Certificate (use Let's Encrypt)
    ssl_certificate /etc/ssl/certs/your_domain.crt;
    ssl_certificate_key /etc/ssl/private/your_domain.key;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    gzip_min_length 1000;

    # Proxy settings
    location / {
        proxy_pass http://connectsphere;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 90;
    }

    # Static files
    location /static/ {
        alias /path/to/project/staticfiles/;
        expires 30d;
    }
}
```

### Systemd Service Files

Create `/etc/systemd/system/connectsphere.service`:
```ini
[Unit]
Description=ConnectSphere Gunicorn Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/socialproject
ExecStart=/path/to/venv/bin/gunicorn \
    --config gunicorn_config.py \
    --chdir /path/to/socialproject \
    socialproject.wsgi:application
Restart=always
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/connectsphere-celery.service`:
```ini
[Unit]
Description=ConnectSphere Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/socialproject
ExecStart=/path/to/venv/bin/celery \
    -A socialproject \
    worker \
    -l info \
    -c 4
Restart=always

[Install]
WantedBy=multi-user.target
```

### Redis (for Caching & Celery)
```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu
# or
brew install redis  # macOS

# Start Redis
redis-server
```

## Startup Commands

```bash
# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable connectsphere
sudo systemctl enable connectsphere-celery
sudo systemctl start connectsphere
sudo systemctl start connectsphere-celery

# Check status
sudo systemctl status connectsphere
sudo systemctl status connectsphere-celery

# View logs
sudo journalctl -u connectsphere -f
sudo journalctl -u connectsphere-celery -f
```

## SSL/HTTPS Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

## Database Backups

Create `/usr/local/bin/backup-connectsphere.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/backups/connectsphere"
DB_NAME="connectsphere_db"
DB_USER="connectsphere"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p $BACKUP_DIR

pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/db_$TIMESTAMP.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
```

```bash
chmod +x /usr/local/bin/backup-connectsphere.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-connectsphere.sh
```

## Monitoring & Logging

### Application Monitoring
```bash
# Install and setup monitoring tools
pip install sentry-sdk  # For error tracking

# In settings.py:
import sentry_sdk
sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=0.1,
    environment="production"
)
```

### Log Rotation
Create `/etc/logrotate.d/connectsphere`:
```
/var/log/connectsphere/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

## Testing Production Setup

```bash
# Test health endpoint
curl https://yourdomain.com/api/v1/auth/token/

# Check SSL configuration
openssl s_client -connect yourdomain.com:443

# Performance testing
# Use: ab, wrk, or locust
```

## Production Environment Variables (.env)

```
DEBUG=False
SECRET_KEY=your-generated-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=connectsphere_db
DB_USER=connectsphere
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Redis/Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Troubleshooting

### Static files not loading
```bash
# Ensure STATIC_ROOT is correct
python manage.py collectstatic --clear --noinput

# Configure Nginx to serve static files properly
```

### Database connection errors
```bash
# Test database connection
python manage.py dbshell

# Check PostgreSQL is running
sudo systemctl status postgresql
```

### Celery workers not processing tasks
```bash
# Check Redis is running
redis-cli ping

# Restart Celery
sudo systemctl restart connectsphere-celery
```

### High memory usage
```bash
# Check Gunicorn workers
ps aux | grep gunicorn

# Adjust workers in gunicorn_config.py
# Reduce: workers = 2  (for low-memory servers)
```

## Security Checklist

- [ ] DEBUG = False
- [ ] SECRET_KEY is strong and environment-based
- [ ] ALLOWED_HOSTS specified correctly
- [ ] Database uses PostgreSQL (not SQLite)
- [ ] HTTPS/SSL enabled
- [ ] HSTS headers configured
- [ ] CSRF protection enabled
- [ ] SQL injection protection (Django ORM)
- [ ] XSS protection enabled
- [ ] Regular backups enabled
- [ ] Error logging configured (Sentry/similar)
- [ ] Rate limiting enabled
- [ ] API authentication via JWT
- [ ] Admin panel secured (/admin)
- [ ] Dependencies regularly updated

## Performance Optimization

1. **Enable Redis Caching**
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

2. **Database Connection Pooling**
```python
# Use pgbouncer or similar
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,
        # ... other settings
    }
}
```

3. **Enable Query Optimization**
```python
# Use select_related and prefetch_related in ViewSets
# Monitor slow queries in production
```

4. **CDN Integration**
```python
# Use CloudFront, Cloudflare, or similar for static assets
```

---

**Last Updated:** March 2026
**Compatibility:** Django 6.0.3, Python 3.12.13
