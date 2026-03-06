# VoxCore cPanel Deployment Guide
## Moving Working Local App to voxcore.org for 100% Uptime Production

---

## **Overview**
You have a working VoxCore app running locally:
- **Backend:** Python FastAPI on port 8000
- **Frontend:** React/Vite on port 5175  
- **Database:** SQL Server (AdventureWorks2022)
- **Features:** Column label mapping, friendly names in charts

This guide walks through deploying it to cPanel-hosted voxcore.org for 24/7 uptime.

---

## **Prerequisites**
1. ✅ cPanel account with SSH access enabled
2. ✅ voxcore.org domain pointing to cPanel server
3. ✅ Node.js installed on cPanel server (check with `node --version`)
4. ✅ Python 3.8+ installed on cPanel server (check with `python3 --version`)
5. ✅ Database access from cPanel server to your SQL Server instance
6. ✅ Local code ready with all fixes applied

---

## **Phase 1: Prepare Local Code (On Your Windows Computer)**

### **Step 1: Build Production Frontend**

```bash
cd c:\Users\USER\Documents\trae_projects\VoxQuery\frontend

# Set production API URL
set VITE_API_URL=https://voxcore.org/api

# Install dependencies
npm install

# Build optimized production version
npm run build
```

**Result:** Creates `frontend/dist/` folder with minified HTML/CSS/JS

### **Step 2: Create Backend Startup Script**

Create file: `voxcore/voxquery/start_backend.sh`

```bash
#!/bin/bash
cd /home/YOUR_USERNAME/voxcore/voxcore/voxquery
source venv/bin/activate
python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 --workers 4
```

Make it executable:
```bash
chmod +x voxcore/voxquery/start_backend.sh
```

### **Step 3: Create .env File for Production**

Create file: `voxcore/voxquery/.env.production`

```env
VITE_API_URL=https://voxcore.org/api
DATABASE_HOST=YOUR_DB_HOST
DATABASE_NAME=AdventureWorks2022
DATABASE_USER=sa
DATABASE_PASSWORD=YOUR_PASSWORD
ALLOWED_HOSTS=voxcore.org,www.voxcore.org
ENV=production
```

---

## **Phase 2: Upload to cPanel Server (Via SSH)**

### **Step 4: Connect via SSH**

```bash
# On Windows PowerShell or Command Prompt:
# (Or use PuTTY/Git Bash if preferred)

ssh YOUR_USERNAME@voxcore.org

# Example:
ssh myuser@voxcore.org
```

Enter your cPanel password when prompted.

### **Step 5: Create Directory Structure**

```bash
# Create directories if they don't exist
mkdir -p ~/voxcore
mkdir -p ~/logs
mkdir -p ~/public_html/voxcore

# Verify
ls -la ~/ | grep voxcore
```

### **Step 6: Upload Files via SCP**

**From your Windows PowerShell** (NOT while SSH'd):

```bash
# Upload built frontend
scp -r "c:\Users\USER\Documents\trae_projects\VoxQuery\frontend\dist\*" YOUR_USERNAME@voxcore.org:~/public_html/voxcore/

# Upload backend
scp -r "c:\Users\USER\Documents\trae_projects\VoxQuery\voxcore" YOUR_USERNAME@voxcore.org:~/voxcore/

# Upload .env.production
scp "c:\Users\USER\Documents\trae_projects\VoxQuery\voxcore\voxquery\.env.production" YOUR_USERNAME@voxcore.org:~/voxcore/voxcore/voxquery/.env
```

**Alternative:** Use FileZilla (FTP/SFTP) GUI tool for easier file transfer.

---

## **Phase 3: Setup Backend on cPanel (Via SSH)**

### **Step 7: Setup Python Virtual Environment**

```bash
# SSH into cPanel
ssh YOUR_USERNAME@voxcore.org

# Navigate to backend directory
cd ~/voxcore/voxcore/voxquery

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### **Step 8: Test Backend Startup**

```bash
# Still in ~/voxcore/voxcore/voxquery with venv activated

# Start backend (test mode)
python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000

# In another SSH terminal, test:
curl http://127.0.0.1:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2025-03-02T..."}

# Stop with Ctrl+C
```

### **Step 9: Start Backend in Background (Persistent)**

```bash
# Still SSH'd with venv activated
# Navigate to correct directory
cd ~/voxcore/voxcore/voxquery

# Start with nohup (stays running after disconnect)
nohup python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 > ~/logs/voxcore-backend.log 2>&1 &

# Verify it's running
ps aux | grep uvicorn

# Check logs
tail -f ~/logs/voxcore-backend.log

# Exit SSH
logout
```

---

## **Phase 4: Configure Web Server (Via cPanel)**

### **Step 10: Setup .htaccess for Frontend Routing**

**Option A: Via cPanel File Manager**
1. Log into cPanel
2. Navigate to `/public_html/voxcore/`
3. Create `.htaccess` file with this content:

```apache
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /voxcore/
    
    # Route API calls to backend
    RewriteRule ^api/(.*)$ http://127.0.0.1:8000/api/$1 [P,L]
    RewriteRule ^health$ http://127.0.0.1:8000/health [P,L]
    
    # Route all other requests to React index.html (SPA routing)
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^ index.html [QSA,L]
</IfModule>
```

**Option B: Via SSH**
```bash
ssh YOUR_USERNAME@voxcore.org

cat > ~/public_html/voxcore/.htaccess << 'EOF'
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /voxcore/
    
    RewriteRule ^api/(.*)$ http://127.0.0.1:8000/api/$1 [P,L]
    RewriteRule ^health$ http://127.0.0.1:8000/health [P,L]
    
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^ index.html [QSA,L]
</IfModule>
EOF

logout
```

---

## **Phase 5: Setup Auto-Restart for 100% Uptime**

### **Step 11: Create Auto-Restart Script**

```bash
# SSH into cPanel
ssh YOUR_USERNAME@voxcore.org

# Create restart script
cat > ~/restart_voxcore.sh << 'EOF'
#!/bin/bash
PROCESS_NAME="uvicorn voxquery.api.main"
LOG_FILE=~/logs/voxcore-restart.log

if ! pgrep -f "$PROCESS_NAME" > /dev/null; then
    echo "[$(date)] Backend down. Restarting..." >> $LOG_FILE
    
    pkill -f "$PROCESS_NAME" || true
    sleep 2
    
    cd ~/voxcore/voxcore/voxquery
    source venv/bin/activate
    nohup python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 >> ~/logs/voxcore-backend.log 2>&1 &
    
    echo "[$(date)] Backend restarted (PID: $!)" >> $LOG_FILE
else
    echo "[$(date)] Backend is running" >> $LOG_FILE
fi
EOF

# Make executable
chmod +x ~/restart_voxcore.sh

# Test it
~/restart_voxcore.sh

logout
```

### **Step 12: Add Cron Job for Auto-Restart**

```bash
# SSH into cPanel
ssh YOUR_USERNAME@voxcore.org

# Add cron job to check every 5 minutes
(crontab -l 2>/dev/null; echo "*/5 * * * * ~/restart_voxcore.sh") | crontab -

# Verify cron was added
crontab -l

logout
```

---

## **Phase 6: Verify Deployment**

### **Step 13: Test Everything**

**Test 1: Frontend Accessible**
```bash
# Open in browser
https://voxcore.org
# Should load VoxCore UI (React app)
```

**Test 2: API Health**
```bash
# Open in browser or curl:
curl https://voxcore.org/api/health
# Expected: {"status":"healthy","timestamp":"..."}
```

**Test 3: API Docs**
```bash
# Open in browser
https://voxcore.org/api/docs
# Should show Swagger UI with all endpoints
```

**Test 4: Run a Query**
```bash
# Via UI: Go to https://voxcore.org and execute a query
# Or via curl:
curl -X POST "https://voxcore.org/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"Show me sales by month"}'
```

**Test 5: Check Backend Process**
```bash
ssh YOUR_USERNAME@voxcore.org
ps aux | grep uvicorn
# Should see: python -m uvicorn voxquery.api.main:app ...
logout
```

---

## **Monitoring & Maintenance**

### **View Logs**
```bash
ssh YOUR_USERNAME@voxcore.org

# Backend logs
tail -f ~/logs/voxcore-backend.log

# Restart logs (auto-restart activity)
tail -f ~/logs/voxcore-restart.log

logout
```

### **Manual Restart**
```bash
ssh YOUR_USERNAME@voxcore.org

# Kill current process
pkill -f "uvicorn voxquery.api.main"

# Start new one
cd ~/voxcore/voxcore/voxquery
source venv/bin/activate
nohup python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 >> ~/logs/voxcore-backend.log 2>&1 &

logout
```

### **Update Version**
```bash
# Rebuild frontend locally
cd c:\Users\USER\Documents\trae_projects\VoxQuery\frontend
set VITE_API_URL=https://voxcore.org/api
npm run build

# Upload new files via SCP
scp -r "frontend\dist\*" YOUR_USERNAME@voxcore.org:~/public_html/voxcore/
```

---

## **Troubleshooting**

### **Issue: Backend won't start**
```bash
ssh YOUR_USERNAME@voxcore.org
tail -f ~/logs/voxcore-backend.log
# Check for errors about database, ports, etc.
```

### **Issue: "Connection refused" on frontend**
```bash
# Check if backend is running
ssh YOUR_USERNAME@voxcore.org
ps aux | grep uvicorn

# Check firewall/proxy settings in cPanel
# Verify .htaccess proxy settings
cat ~/public_html/voxcore/.htaccess
```

### **Issue: Static files not loading (CSS/JS blank)**
```bash
# Verify frontend files uploaded correctly
ssh YOUR_USERNAME@voxcore.org
ls -la ~/public_html/voxcore/
# Should see: index.html, assets/ folder, etc.
```

### **Issue: Cron job not working**
```bash
ssh YOUR_USERNAME@voxcore.org

# Check cron log
grep CRON /var/log/syslog | tail -20

# Re-add cron job
(crontab -l 2>/dev/null; echo "*/5 * * * * ~/restart_voxcore.sh 2>&1 >> ~/logs/cron.log") | crontab -

logout
```

---

## **Success Checklist**

- [ ] Frontend deployed to `~/public_html/voxcore/`
- [ ] Backend uploaded to `~/voxcore/voxcore/voxquery/`
- [ ] Virtual environment created and dependencies installed
- [ ] `.env` configured with production database credentials
- [ ] Backend starts and running on 127.0.0.1:8000
- [ ] `.htaccess` file routing API calls to backend
- [ ] https://voxcore.org loads React UI
- [ ] https://voxcore.org/api/health returns 200 OK
- [ ] Can execute queries and see results with friendly labels
- [ ] Cron job set up for auto-restart
- [ ] Verified uptime monitoring (check backend logs)

---

## **Quick Reference Commands**

```bash
# Connect to cPanel
ssh YOUR_USERNAME@voxcore.org

# Check if backend running
ps aux | grep uvicorn

# View backend logs
tail -f ~/logs/voxcore-backend.log

# Restart backend
pkill -f "uvicorn voxquery.api.main" && \
cd ~/voxcore/voxcore/voxquery && \
source venv/bin/activate && \
nohup python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 >> ~/logs/voxcore-backend.log 2>&1 &

# Test API
curl https://voxcore.org/api/health

# View cron jobs
crontab -l

# Disconnect
logout
```

---

## **Next Steps**

1. ✅ Have all prerequisites ready
2. ✅ Build and upload frontend
3. ✅ Upload and setup backend
4. ✅ Test all endpoints
5. ✅ Setup auto-restart for 100% uptime
6. ✅ Monitor logs for 24-48 hours
7. ✅ Verify database connections under load
8. ✅ Consider setting up alerts/monitoring (New Relic, DataDog, etc.)

---

**Questions?** Check the logs first:
```bash
ssh YOUR_USERNAME@voxcore.org
tail -f ~/logs/voxcore-backend.log
```
