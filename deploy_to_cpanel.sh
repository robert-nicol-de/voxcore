#!/bin/bash

# VoxCore cPanel Deployment Script
# Deploy working VoxCore to voxcore.org for 100% uptime

set -e

DOMAIN="voxcore.org"
USERNAME=$(whoami)
HOME_DIR=/home/$USERNAME
PUBLIC_HTML=$HOME_DIR/public_html/voxcore
VOXCORE_DIR=$HOME_DIR/voxcore
LOG_DIR=$HOME_DIR/logs

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🚀 VoxCore cPanel Deployment Script${NC}"
echo "===================================="
echo "Domain: $DOMAIN"
echo "User: $USERNAME"
echo "Public HTML: $PUBLIC_HTML"
echo "===================================="

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p $LOG_DIR
mkdir -p $PUBLIC_HTML
mkdir -p $VOXCORE_DIR

# Step 1: Build Frontend
echo -e "${YELLOW}1️⃣  Building frontend...${NC}"
cd $VOXCORE_DIR/frontend
export VITE_API_URL="https://$DOMAIN/api"
npm install
npm run build
echo -e "${GREEN}✓ Frontend built${NC}"

# Step 2: Deploy Frontend to Public HTML
echo -e "${YELLOW}2️⃣  Deploying frontend to web...${NC}"
rm -rf $PUBLIC_HTML/*
cp -r $VOXCORE_DIR/frontend/dist/* $PUBLIC_HTML/
echo -e "${GREEN}✓ Frontend deployed to $PUBLIC_HTML${NC}"

# Step 3: Setup Backend
echo -e "${YELLOW}3️⃣  Setting up backend...${NC}"
cd $VOXCORE_DIR/voxcore/voxquery

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Virtual environment created and dependencies installed${NC}"
else
    source venv/bin/activate
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies updated${NC}"
fi

# Step 4: Create .env file for production
echo -e "${YELLOW}4️⃣  Creating production configuration...${NC}"
cat > $VOXCORE_DIR/voxcore/voxquery/.env << EOF
VITE_API_URL=https://$DOMAIN/api
DATABASE_URL=mssql://sa:YOUR_PASSWORD@YOUR_DB_HOST:1433/AdventureWorks2022
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
ENV=production
API_PORT=8000
EOF
echo -e "${GREEN}✓ Configuration created at .env${NC}"

# Step 5: Kill any existing backend process
echo -e "${YELLOW}5️⃣  Stopping old backend process...${NC}"
pkill -f "uvicorn voxquery.api.main" || true
sleep 2

# Step 6: Start Backend with nohup (stays running even after disconnect)
echo -e "${YELLOW}6️⃣  Starting backend...${NC}"
cd $VOXCORE_DIR/voxcore/voxquery
source venv/bin/activate
nohup python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 > $LOG_DIR/voxcore-backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
sleep 3

# Verify backend is running
if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✓ Backend started successfully (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}✗ Backend failed to start. Check logs:${NC}"
    cat $LOG_DIR/voxcore-backend.log
    exit 1
fi

# Step 7: Create .htaccess for frontend routing to API
echo -e "${YELLOW}7️⃣  Configuring web server routing...${NC}"
cat > $PUBLIC_HTML/.htaccess << 'HTACCESSEOF'
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /
    
    # Route API calls to backend server (127.0.0.1:8000)
    RewriteRule ^api/(.*)$ http://127.0.0.1:8000/api/$1 [P,L]
    RewriteRule ^health$ http://127.0.0.1:8000/health [P,L]
    
    # Route all other requests to React frontend index.html
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^ index.html [QSA,L]
</IfModule>

<IfModule mod_proxy.c>
    ProxyRequests Off
    ProxyPreferHTTPKeepAlive Off
    
    # Allow proxy to localhost:8000
    <Proxy http://127.0.0.1:8000*>
        Order allow,deny
        Allow from all
    </Proxy>
</IfModule>

# Security Headers
<IfModule mod_headers.c>
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-XSS-Protection "1; mode=block"
</IfModule>
HTACCESSEOF
echo -e "${GREEN}✓ Web server routing configured${NC}"

# Step 8: Create auto-restart cron job
echo -e "${YELLOW}8️⃣  Setting up auto-restart...${NC}"
cat > $HOME_DIR/restart_voxcore.sh << 'RESTARTEOF'
#!/bin/bash
# Auto-restart VoxCore backend if it crashes

VOXCORE_DIR=$HOME_DIR/voxcore
LOG_DIR=$HOME_DIR/logs
PROCESS_NAME="uvicorn voxquery.api.main"

# Check if process is running
if ! pgrep -f "$PROCESS_NAME" > /dev/null; then
    echo "Backend down at $(date). Restarting..." >> $LOG_DIR/voxcore-restart.log
    
    # Kill any zombie processes
    pkill -f "$PROCESS_NAME" || true
    
    # Start backend
    cd $VOXCORE_DIR/voxcore/voxquery
    source venv/bin/activate
    nohup python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 >> $LOG_DIR/voxcore-backend.log 2>&1 &
    
    echo "Backend restarted. New PID: $!" >> $LOG_DIR/voxcore-restart.log
fi
RESTARTEOF

chmod +x $HOME_DIR/restart_voxcore.sh
echo -e "${GREEN}✓ Auto-restart script created${NC}"

# Add cron job for every 5 minutes
(crontab -l 2>/dev/null; echo "*/5 * * * * $HOME_DIR/restart_voxcore.sh") | crontab -
echo -e "${GREEN}✓ Cron job added (checks every 5 minutes)${NC}"

# Step 9: Verify deployment
echo -e "${YELLOW}9️⃣  Verifying deployment...${NC}"
sleep 3

echo -e "${GREEN}✓ Deployment Summary:${NC}"
echo "=================================="
echo -e "🌐 Website:     ${GREEN}https://$DOMAIN/${NC}"
echo -e "🎨 Frontend:    ${GREEN}https://$DOMAIN/${NC}"
echo -e "⚙️  API:         ${GREEN}https://$DOMAIN/api${NC}"
echo -e "❤️  Health:      ${GREEN}https://$DOMAIN/api/health${NC}"
echo -e "📚 API Docs:    ${GREEN}https://$DOMAIN/api/docs${NC}"
echo ""
echo -e "📂 Directories:"
echo "   Frontend: $PUBLIC_HTML"
echo "   Backend:  $VOXCORE_DIR/voxcore/voxquery"
echo "   Logs:     $LOG_DIR"
echo ""
echo -e "📝 Useful Commands:"
echo "   View backend logs:  tail -f $LOG_DIR/voxcore-backend.log"
echo "   View restart logs:  tail -f $LOG_DIR/voxcore-restart.log"
echo "   Check backend:      ps aux | grep uvicorn"
echo "   Manual restart:     $HOME_DIR/restart_voxcore.sh"
echo "   Test API:           curl https://$DOMAIN/api/health"
echo ""
echo -e "${GREEN}✓ VoxCore is now LIVE on https://$DOMAIN/${NC}"
echo "=================================="
