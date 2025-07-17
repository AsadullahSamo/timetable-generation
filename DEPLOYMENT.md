# Deployment Guide

This guide will help you deploy the Timetable Generation System to production.

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL (recommended) or MySQL
- Nginx (for production)
- SSL certificate (for HTTPS)

## Backend Deployment

### 1. Production Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd timetable-generation-master

# Create production virtual environment
cd django-backend
python3 -m venv venv_prod
source venv_prod/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 2. Database Setup

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE timetable_db;
CREATE USER timetable_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE timetable_db TO timetable_user;
\q
```

### 3. Environment Configuration

Create `.env` file in `django-backend/backend/`:

```env
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://timetable_user:your_password@localhost:5432/timetable_db
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### 4. Django Configuration

Update `django-backend/backend/backend/settings.py`:

```python
# Add to settings.py
import os
from pathlib import Path

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'timetable_db',
        'USER': 'timetable_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 5. Run Migrations

```bash
cd django-backend/backend
source ../venv_prod/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

### 6. Gunicorn Configuration

Create `gunicorn.conf.py` in `django-backend/backend/`:

```python
bind = "0.0.0.0:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
```

### 7. Systemd Service

Create `/etc/systemd/system/timetable-backend.service`:

```ini
[Unit]
Description=Timetable Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/timetable-generation-master/django-backend/backend
Environment="PATH=/path/to/timetable-generation-master/django-backend/venv_prod/bin"
ExecStart=/path/to/timetable-generation-master/django-backend/venv_prod/bin/gunicorn --config gunicorn.conf.py backend.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### 8. Start Backend Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable timetable-backend
sudo systemctl start timetable-backend
sudo systemctl status timetable-backend
```

## Frontend Deployment

### 1. Build Production Version

```bash
cd frontend
npm install
npm run build
```

### 2. Nginx Configuration

Create `/etc/nginx/sites-available/timetable`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    # Frontend
    location / {
        root /path/to/timetable-generation-master/frontend/out;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /path/to/timetable-generation-master/django-backend/backend/staticfiles/;
    }
}
```

### 3. Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/timetable /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring

### 1. Log Monitoring

```bash
# Backend logs
sudo journalctl -u timetable-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Health Check

Create a simple health check endpoint in Django:

```python
# In views.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy'})
```

## Backup Strategy

### 1. Database Backup

```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump timetable_db > backup_$DATE.sql
gzip backup_$DATE.sql
```

### 2. File Backup

```bash
# Backup static files and uploads
tar -czf backup_files_$(date +%Y%m%d).tar.gz /path/to/staticfiles/
```

## Performance Optimization

### 1. Database Optimization

```sql
-- Add indexes for better performance
CREATE INDEX idx_timetable_entry_day_period ON timetable_timetableentry(day, period);
CREATE INDEX idx_timetable_entry_teacher ON timetable_timetableentry(teacher_id);
CREATE INDEX idx_timetable_entry_subject ON timetable_timetableentry(subject_id);
```

### 2. Caching

Install Redis and configure Django caching:

```python
# In settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**: Check if Gunicorn is running
2. **Database Connection**: Verify PostgreSQL is running
3. **Static Files**: Ensure collectstatic was run
4. **SSL Issues**: Check certificate paths and permissions

### Useful Commands

```bash
# Check service status
sudo systemctl status timetable-backend

# Restart services
sudo systemctl restart timetable-backend
sudo systemctl restart nginx

# Check logs
sudo journalctl -u timetable-backend -n 50
```

## Security Checklist

- [ ] HTTPS enabled
- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY
- [ ] Database credentials secured
- [ ] Firewall configured
- [ ] Regular security updates
- [ ] SSL certificate auto-renewal
- [ ] Backup strategy implemented 