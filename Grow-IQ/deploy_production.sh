#!/bin/bash

# CareerConnect Production Deployment Script
# This script sets up the production environment

set -e  # Exit on any error

echo "🚀 Starting CareerConnect Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="careerconnect"
APP_USER="careerconnect"
APP_DIR="/opt/$APP_NAME"
SERVICE_NAME="$APP_NAME.service"
NGINX_CONF="$APP_NAME.conf"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}This script should not be run as root${NC}"
   exit 1
fi

echo -e "${YELLOW}Step 1: System Updates${NC}"
sudo apt update
sudo apt upgrade -y

echo -e "${YELLOW}Step 2: Install System Dependencies${NC}"
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server supervisor

echo -e "${YELLOW}Step 3: Create Application User${NC}"
sudo useradd -r -s /bin/false $APP_USER || echo "User already exists"

echo -e "${YELLOW}Step 4: Create Application Directory${NC}"
sudo mkdir -p $APP_DIR
sudo chown $APP_USER:$APP_USER $APP_DIR

echo -e "${YELLOW}Step 5: Setup Python Environment${NC}"
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements_production.txt

echo -e "${YELLOW}Step 6: Setup PostgreSQL Database${NC}"
sudo -u postgres psql -c "CREATE DATABASE careerconnect;"
sudo -u postgres psql -c "CREATE USER careerconnect WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE careerconnect TO careerconnect;"

echo -e "${YELLOW}Step 7: Create Environment File${NC}"
cat > .env << EOF
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://careerconnect:your_secure_password@localhost:5432/careerconnect
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=strict
EOF

echo -e "${YELLOW}Step 8: Create Systemd Service${NC}"
sudo tee /etc/systemd/system/$SERVICE_NAME > /dev/null << EOF
[Unit]
Description=CareerConnect FastAPI Application
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo -e "${YELLOW}Step 9: Setup Nginx${NC}"
sudo tee /etc/nginx/sites-available/$NGINX_CONF > /dev/null << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration (you'll need to add your certificates)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Proxy to FastAPI app
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Static files
    location /static/ {
        alias $APP_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }
}
EOF

echo -e "${YELLOW}Step 10: Enable Services${NC}"
sudo ln -sf /etc/nginx/sites-available/$NGINX_CONF /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl enable $SERVICE_NAME
sudo systemctl enable nginx
sudo systemctl enable postgresql
sudo systemctl enable redis

echo -e "${YELLOW}Step 11: Setup Log Rotation${NC}"
sudo tee /etc/logrotate.d/$APP_NAME > /dev/null << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $APP_USER $APP_USER
    postrotate
        systemctl reload $SERVICE_NAME
    endscript
}
EOF

echo -e "${YELLOW}Step 12: Setup Firewall${NC}"
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo -e "${GREEN}✅ Production deployment completed!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update .env file with your actual domain and database credentials"
echo "2. Setup SSL certificates with Let's Encrypt"
echo "3. Start the services: sudo systemctl start $SERVICE_NAME"
echo "4. Check status: sudo systemctl status $SERVICE_NAME"
echo "5. View logs: sudo journalctl -u $SERVICE_NAME -f"
