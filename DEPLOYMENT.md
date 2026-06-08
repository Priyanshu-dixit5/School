# Deployment Guide

Production deployment for the Excellence Global School website using Gunicorn and Nginx on Linux (Ubuntu/Debian).

## Prerequisites

- Ubuntu 20.04+ or Debian 11+
- Python 3.10+
- Nginx
- Domain name (optional but recommended)

## Step 1: Server Setup

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv nginx -y
```

## Step 2: Deploy Application

```bash
sudo mkdir -p /var/www/school
sudo chown $USER:$USER /var/www/school

# Copy project files to /var/www/school
cd /var/www/school

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 3: Environment Configuration

```bash
cp .env.example .env
nano .env
```

Set production values:

```env
FLASK_ENV=production
SECRET_KEY=<generate-a-strong-random-key>
GEMINI_API_KEY=<your-api-key>
MAIL_USERNAME=<smtp-email>
MAIL_PASSWORD=<smtp-app-password>
SCHOOL_EMAIL=school@yourdomain.com
```

Generate a secret key:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Step 4: Initialize Database

```bash
source venv/bin/activate
python3 -c "from app import create_app; create_app('production')"
```

Change default admin password:

```bash
python3 << 'EOF'
from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app('production')
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    admin.set_password('YOUR-STRONG-PASSWORD')
    db.session.commit()
    print('Password updated.')
EOF
```

## Step 5: Gunicorn Systemd Service

Create `/etc/systemd/system/school.service`:

```ini
[Unit]
Description=Excellence Global School Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/school
Environment="PATH=/var/www/school/venv/bin"
EnvironmentFile=/var/www/school/.env
ExecStart=/var/www/school/venv/bin/gunicorn -c gunicorn.conf.py wsgi:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo chown -R www-data:www-data /var/www/school
sudo systemctl daemon-reload
sudo systemctl enable school
sudo systemctl start school
sudo systemctl status school
```

## Step 6: Nginx Configuration

```bash
sudo cp nginx.conf.example /etc/nginx/sites-available/school
sudo nano /etc/nginx/sites-available/school
# Update server_name to your domain

sudo ln -s /etc/nginx/sites-available/school /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Step 7: SSL with Certbot (Recommended)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Step 8: File Permissions

```bash
sudo chown -R www-data:www-data /var/www/school/app/static/uploads
sudo chmod -R 755 /var/www/school/app/static/uploads
```

## Monitoring & Logs

```bash
# Application logs
sudo journalctl -u school -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Updating the Application

```bash
cd /var/www/school
source venv/bin/activate
git pull  # if using git
pip install -r requirements.txt
sudo systemctl restart school
```

## Security Checklist

- [ ] Change default admin password
- [ ] Set strong SECRET_KEY
- [ ] Enable HTTPS with SSL certificate
- [ ] Configure firewall (UFW): allow 80, 443, deny others
- [ ] Keep `.env` out of version control
- [ ] Set up regular database backups
- [ ] Configure Gmail App Password (not regular password) for SMTP

## Troubleshooting

**Emails not sending:** Verify MAIL_USERNAME, MAIL_PASSWORD, and that Gmail "App Passwords" are enabled.

**AI not working:** Ensure GEMINI_API_KEY is set and valid.

**502 Bad Gateway:** Check Gunicorn is running: `sudo systemctl status school`

**Upload errors:** Verify upload directory permissions and `client_max_body_size` in Nginx.
