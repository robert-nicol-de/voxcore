#!/bin/bash
set -e

echo "=========================================="
echo "VoxCore Production Setup - Full Auto"
echo "=========================================="
echo ""

# Create log directory
mkdir -p ~/logs
echo "[$(date)] Setup starting..." >> ~/logs/setup.log

# Navigate to backend
cd ~/VOXCORE/voxquery
echo "[1/7] Backend directory ready"

# Create virtual environment
echo "[2/7] Creating Python virtual environment..."
python3 -m venv venv || python -m venv venv
source venv/bin/activate

# Install dependencies
echo "[3/7] Installing dependencies..."
pip install --upgrade pip -q 2>/dev/null || pip install --upgrade pip
pip install -r requirements.txt -q 2>/dev/null || pip install -r requirements.txt
echo "Dependencies installed" >> ~/logs/setup.log

# Create .env file (locked)
echo "[4/7] Creating configuration file..."
cat > .env << 'ENVEOF'
VITE_API_URL=https://voxcore.org/api
ALLOWED_HOSTS=voxcore.org,www.voxcore.org
ENV=production
DATABASE_URL=
ENVEOF
echo ".env created (database locked)" >> ~/logs/setup.log

# Create restart script
echo "[5/7] Creating auto-restart script..."
cat > ~/restart_voxcore.sh << 'RESTARTEOF'
#!/bin/bash
LOGFILE=~/logs/voxcore-restart.log
if ! pgrep -f "uvicorn voxquery.api.main" > /dev/null; then
    echo "[$(date)] Backend down, restarting..." >> $LOGFILE
    cd ~/VOXCORE/voxquery
    source venv/bin/activate
    nohup python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 >> ~/logs/voxcore-backend.log 2>&1 &
    echo "[$(date)] Backend restarted (PID: $!)" >> $LOGFILE
else
    echo "[$(date)] Backend healthy" >> $LOGFILE
fi
RESTARTEOF

chmod +x ~/restart_voxcore.sh
echo "Auto-restart script created" >> ~/logs/setup.log

# Start backend
echo "[6/7] Starting backend..."
cd ~/VOXCORE/voxquery
source venv/bin/activate
nohup python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 >> ~/logs/voxcore-backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)" >> ~/logs/setup.log
sleep 3

# Setup .htaccess
echo "[7/7] Configuring web server routing..."
cat > ~/public_html/voxcore/.htaccess << 'HTACCESSEOF'
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /
    RewriteRule ^api/(.*)$ http://127.0.0.1:8000/api/$1 [P,L]
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^ index.html [QSA,L]
</IfModule>
HTACCESSEOF
echo ".htaccess configured" >> ~/logs/setup.log

# Add cron job for auto-restart
(crontab -l 2>/dev/null | grep -v "restart_voxcore"; echo "*/5 * * * * ~/restart_voxcore.sh") | crontab -
echo "Cron auto-restart configured" >> ~/logs/setup.log

# Verify backend is running
sleep 2
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo ""
    echo "=========================================="
    echo "✓✓✓ VOXCORE IS NOW LIVE! ✓✓✓"
    echo "=========================================="
    echo ""
    echo "🌐 Website:     https://voxcore.org/"
    echo "❤️  Health:      https://voxcore.org/api/health"
    echo "📚 API Docs:    https://voxcore.org/api/docs"
    echo ""
    echo "⚠️  DATABASE:    LOCKED (no credentials)"
    echo "    Browse the UI, but queries will fail"
    echo "    To unlock: Add DATABASE_URL to ~/.env"
    echo ""
    echo "🔄 AUTO-RESTART: Every 5 minutes via cron"
    echo "📝 Logs: ~/logs/voxcore-backend.log"
    echo ""
    echo "Setup completed at $(date)" >> ~/logs/setup.log
else
    echo ""
    echo "✗ Backend failed to start"
    echo "Check logs: cat ~/logs/voxcore-backend.log"
    exit 1
fi
