#!/bin/bash
# School Management System - Linux Deployment Script
# Run: sudo bash deploy.sh

set -e

echo "==================================="
echo " School Management System Deployer "
echo "==================================="

APP_NAME="schoolms"
APP_DIR="/opt/$APP_NAME"
DOMAIN="${1:-schoolms.example.com}"

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

echo "[1/7] Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv nginx postgresql postgresql-contrib git curl

echo "[2/7] Setting up application directory..."
mkdir -p $APP_DIR
cp -r . $APP_DIR
cd $APP_DIR

echo "[3/7] Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt

echo "[4/7] Setting up PostgreSQL database..."
sudo -u postgres psql -c "CREATE DATABASE $APP_NAME;" 2>/dev/null || echo "Database may already exist"
sudo -u postgres psql -c "CREATE USER ${APP_NAME}user WITH PASSWORD 'changeme123';" 2>/dev/null || echo "User may already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $APP_NAME TO ${APP_NAME}user;" 2>/dev/null || true

echo "[5/7] Configuring environment..."
cat > .env << EOF
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=postgresql://${APP_NAME}user:changeme123@localhost:5432/$APP_NAME
EOF

echo "[6/7] Initializing database and seeding data..."
source venv/bin/activate
export FLASK_APP=app.py
export $(cat .env | xargs)
python3 seed.py

echo "[7/7] Setting up systemd service and nginx..."

cat > /etc/systemd/system/$APP_NAME.service << EOF
[Unit]
Description=School Management System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/nginx/sites-available/$APP_NAME << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias $APP_DIR/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /uploads/ {
        alias $APP_DIR/uploads/;
        expires 30d;
    }

    client_max_body_size 16M;
}
EOF

chown -R www-data:www-data $APP_DIR
chmod -R 755 $APP_DIR

ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

systemctl daemon-reload
systemctl enable $APP_NAME
systemctl restart $APP_NAME
nginx -t && systemctl reload nginx

echo ""
echo "==================================="
echo " Deployment Complete!"
echo "==================================="
echo ""
echo " Website:    http://$DOMAIN"
echo " Admin URL:  http://$DOMAIN/admin/login"
echo " Username:   admin"
echo " Password:   admin123"
echo ""
echo " IMPORTANT: Change the admin password and database password!"
echo "==================================="
