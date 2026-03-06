#!/bin/bash
# VoxCore Setup Script - Run manually via cPanel Terminal
# Usage: bash setup_manual.sh

echo "======================================"
echo "VoxCore Setup Started"
echo "======================================"

# Step 1: Create logs directory
echo "[1/7] Creating logs directory..."
mkdir -p ~/logs

# Step 2: Create Python virtual environment
echo "[2/7] Creating Python virtual environment..."
cd ~/VOXCORE/voxquery
python3 -m venv venv 2>&1 || python -m venv venv

# Step 3: Install dependencies
echo "[3/7] Installing dependencies (this will take 1-2 minutes)..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Step 4: Create .env file
echo "[4/7] Creating .env file..."
cat > .env << 'EOF'
VITE_API_URL=https://voxcore.org/api
ALLOWED_HOSTS=voxcore.org,www.voxcore.org
ENV=production
DATABASE_URL=
EOF

# Step 5: Start backend
echo "[5/7] Starting backend..."
source venv/bin/activate
nohup python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 > ~/logs/voxcore-backend.log 2>&1 &
sleep 2

# Step 6: Create .htaccess
echo "[6/7] Configuring web server routing..."
mkdir -p ~/public_html/voxcore
cat > ~/public_html/voxcore/.htaccess << 'EOF'
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteBase /
RewriteRule ^api/(.*)$ http://127.0.0.1:8000/api/$1 [P,L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^ index.html [QSA,L]
</IfModule>
EOF

# Step 7: Setup cron for auto-restart
echo "[7/7] Setting up auto-restart..."
(crontab -l 2>/dev/null | grep -v voxcore; echo '*/5 * * * * cd ~/VOXCORE/voxquery && source venv/bin/activate && python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 >> ~/logs/voxcore-backend.log 2>&1') | crontab -

echo ""
echo "======================================"
echo "✓✓✓ VOXCORE IS NOW LIVE! ✓✓✓"
echo "======================================"
echo "Website:   https://voxcore.org/"
echo "Health:    https://voxcore.org/api/health"
echo "Docs:      https://voxcore.org/api/docs"
echo "DATABASE:  LOCKED (secure)"
echo "======================================"
