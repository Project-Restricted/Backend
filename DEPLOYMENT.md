# Production Deployment Guide

## Overview
This project is ready for deployment to a Linux VPS running PostgreSQL. The application uses environment variables for configuration, allowing safe separation of secrets from code.

## Pre-Deployment Checklist on VPS

### 1. PostgreSQL Installation & Setup

Connect to your VPS and run:

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib -y

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql <<EOF
CREATE USER cinemaportal_user WITH PASSWORD 'your-secure-password-here';
CREATE DATABASE cinemaportal OWNER cinemaportal_user;
ALTER ROLE cinemaportal_user SET client_encoding TO 'utf8';
ALTER ROLE cinemaportal_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE cinemaportal_user SET default_transaction_deferrable TO on;
EOF

# Verify connection (replace password with actual)
psql -h localhost -U cinemaportal_user -d cinemaportal
# Type: \q to exit
```

### 2. Create Production `.env` File

On your VPS, create `/opt/cinemaportal/.env` (or wherever your project directory is):

```bash
# Generate a strong SECRET_KEY - run this locally and copy the output
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Then create the `.env` file:

```bash
cat > /opt/cinemaportal/.env <<'EOF'
DEBUG=False
SECRET_KEY=<paste-generated-secret-key-here>
ALLOWED_HOSTS=your-domain.com,your-server-ip-address

DB_ENGINE=django.db.backends.postgresql
DB_NAME=cinemaportal
DB_USER=cinemaportal_user
DB_PASSWORD=your-secure-password-here
DB_HOST=localhost
DB_PORT=5432
EOF

# Secure the file
chmod 600 /opt/cinemaportal/.env
```

### 3. Project Directory Structure

Expected structure on server:
```
/opt/cinemaportal/
├── .env                    # Created in step 2
├── .venv/                  # Virtual environment
├── cinemaportal/           # Project directory
│   ├── manage.py
│   ├── settings.py         # Already updated to use .env
│   └── ...
├── media/                  # User-uploaded files
├── requirements.txt
└── deploy_develop.sh       # Deployment script
```

### 4. Automatic Deployment via GitHub Actions

When you push to `develop` branch:
1. GitHub Actions workflow triggers (`.github/workflows/deploy_develop.yml`)
2. SSH connects to your VPS using secrets:
   - `SERVER_HOST` - IP address or domain
   - `SERVER_USER` - SSH username
   - `SERVER_SSH_KEY` - Private SSH key
3. Runs `/var/www/deploy_develop.sh` (or your configured path)

**The deployment script should:**
```bash
#!/bin/bash
cd /opt/cinemaportal
source .venv/bin/activate
git pull origin develop
pip install -r requirements.txt
python cinemaportal/manage.py migrate
python cinemaportal/manage.py collectstatic --noinput
# Restart your application server (gunicorn/uwsgi/etc)
systemctl restart cinemaportal  # or your service name
```

### 5. First-Time Manual Setup

```bash
# SSH into server
ssh user@your-server-ip

# Navigate to project
cd /opt/cinemaportal

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (see step 2)
nano .env

# Run migrations
python cinemaportal/manage.py migrate

# Create superuser (optional)
python cinemaportal/manage.py createsuperuser

# Test collectstatic
python cinemaportal/manage.py collectstatic --noinput
```

### 6. Service Configuration (systemd example)

Create `/etc/systemd/system/cinemaportal.service`:

```ini
[Unit]
Description=CinemaPortal Django Application
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/cinemaportal
Environment="PATH=/opt/cinemaportal/.venv/bin"
ExecStart=/opt/cinemaportal/.venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --timeout 60 \
    cinemaportal.wsgi:application

Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cinemaportal
sudo systemctl start cinemaportal
sudo systemctl status cinemaportal
```

### 7. Nginx Reverse Proxy Configuration

Example `/etc/nginx/sites-available/cinemaportal`:

```nginx
upstream cinemaportal {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /opt/cinemaportal/staticfiles/;
    }

    location /media/ {
        alias /opt/cinemaportal/media/;
    }

    location / {
        proxy_pass http://cinemaportal;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and test:
```bash
sudo ln -s /etc/nginx/sites-available/cinemaportal /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### 9. Monitoring & Logs

```bash
# Check application status
systemctl status cinemaportal

# View application logs
journalctl -u cinemaportal -f

# View Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## Troubleshooting

**Database connection failed:**
- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Check `.env` credentials match database user
- Ensure DB_HOST is correct (usually `localhost` for same-server setup)

**Import error for `decouple`:**
- Ensure `python-decouple==3.8` is in `requirements.txt` and installed
- Run: `pip install python-decouple==3.8`

**Migration errors:**
- Run migrations manually: `python cinemaportal/manage.py migrate`
- Check database connection in `.env`

**Static files not loading:**
- Run collectstatic: `python cinemaportal/manage.py collectstatic --noinput`
- Verify Nginx alias path matches `STATIC_ROOT` in settings

## Key Files to Review

- `.env.example` - Example environment variables (copy to `.env` on production)
- `cinemaportal/settings.py` - Now reads from environment using `decouple`
- `.github/workflows/deploy_develop.yml` - GitHub Actions deployment automation
- `requirements.txt` - All dependencies including `python-decouple` for .env support
