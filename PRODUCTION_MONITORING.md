# VoxCore Production Monitoring & Troubleshooting

## **🔍 Real-Time Monitoring (During Deployment)**

### **Monitor Backend Startup**
```bash
ssh YOUR_USERNAME@voxcore.org

# Follow logs in real-time
tail -f ~/logs/voxcore-backend.log

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

### **Monitor Auto-Restart**
```bash
ssh YOUR_USERNAME@voxcore.org

# Check restart log
tail -f ~/logs/voxcore-restart.log

# Expected (just shows health checks, no errors):
# [2025-03-02 14:30:05] Backend is running
# [2025-03-02 14:35:05] Backend is running
```

### **Check Backend Process Status**
```bash
ssh YOUR_USERNAME@voxcore.org

# View full uvicorn process
ps aux | grep uvicorn

# Kill if needed (restarted by cron in 5 min)
pkill -f "uvicorn voxquery.api.main"

# Force restart
~/restart_voxcore.sh
```

---

## **🚨 Common Issues & Solutions**

### **Issue 1: "Connection refused" or 502 errors**

**Cause:** Backend is not running

**Solution:**
```bash
ssh YOUR_USERNAME@voxcore.org

# Check if running
ps aux | grep uvicorn

# If not running, start manually
cd ~/voxcore/voxcore/voxquery
source venv/bin/activate
nohup python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 >> ~/logs/voxcore-backend.log 2>&1 &

# Wait 5 seconds
sleep 5

# Test
curl http://127.0.0.1:8000/health
```

---

### **Issue 2: "Database connection failed" or "ODBC error"**

**Cause:** Database connection string incorrect or database unreachable

**Solution:**
```bash
ssh YOUR_USERNAME@voxcore.org

# Check .env file
cat ~/voxcore/voxcore/voxquery/.env | grep DATABASE

# Expected:
# DATABASE_URL=mssql://sa:PASSWORD@YOUR_DB_HOST:1433/AdventureWorks2022

# Test database connection from cPanel server
# Edit and run this test script:

cat > ~/test_db.py << 'EOF'
import pyodbc
connection_string = open('/home/YOUR_USERNAME/voxcore/voxcore/voxquery/.env').read()
# Parse and test...
EOF

# If database is on local Windows machine, may need to:
# 1. Whitelist cPanel server IP in SQL Server firewall
# 2. Enable SQL Server TCP/IP protocol in SQL Server Configuration Manager
# 3. Use public IP instead of localhost
```

**Check logs for specifics:**
```bash
tail -f ~/logs/voxcore-backend.log | grep -i "database\|error\|exception"
```

---

### **Issue 3: "ModuleNotFoundError" or "ImportError"**

**Cause:** Python dependencies not installed or wrong virtual environment

**Solution:**
```bash
ssh YOUR_USERNAME@voxcore.org

cd ~/voxcore/voxcore/voxquery

# Activate virtual environment
source venv/bin/activate

# Check Python version
python --version
# Should be 3.8+

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify imports work
python -c "import voxquery; print('OK')"

# Restart backend
pkill -f "uvicorn" || true
sleep 2
nohup python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 >> ~/logs/voxcore-backend.log 2>&1 &
```

---

### **Issue 4: "Frontend loads but API calls fail" (CORS errors)**

**Cause:** .htaccess proxy configuration incorrect

**Solution:**
```bash
ssh YOUR_USERNAME@voxcore.org

# Check .htaccess exists and content
cat ~/public_html/voxcore/.htaccess

# Should contain:
# RewriteRule ^api/(.*)$ http://127.0.0.1:8000/api/$1 [P,L]

# Make sure mod_rewrite enabled in cPanel:
# 1. Log into cPanel
# 2. Go to "MultiPHP INI Editor" 
# 3. Find php.ini, check extensions

# If missing, rebuild .htaccess
cat > ~/public_html/voxcore/.htaccess << 'EOF'
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /voxcore/
    RewriteRule ^api/(.*)$ http://127.0.0.1:8000/api/$1 [P,L]
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^ index.html [QSA,L]
</IfModule>
EOF

# Restart Apache
sudo /usr/local/cpanel/scripts/restartsrv_httpd
```

---

### **Issue 5: "Frontend shows blank page" or 404**

**Cause:** Frontend files not uploaded correctly

**Solution:**
```bash
ssh YOUR_USERNAME@voxcore.org

# Check frontend directory
ls -la ~/public_html/voxcore/

# Should show:
# index.html
# assets/ (folder)
# favicon.ico
# config.json

# If missing dist files, re-upload:
# (On local Windows computer)
# scp -r frontend\dist\* YOUR_USERNAME@voxcore.org:~/public_html/voxcore/

# Check file permissions
chmod -R 755 ~/public_html/voxcore/
# Or in cPanel: Files > rights = 755

# Clear browser cache and reload
# Ctrl+Shift+Delete in browser, clear all
```

---

### **Issue 6: "Cron job not restarting backend"**

**Cause:** Cron job not configured or permissions issue

**Solution:**
```bash
ssh YOUR_USERNAME@voxcore.org

# Check cron jobs
crontab -l

# Should show:
# */5 * * * * /home/YOUR_USERNAME/restart_voxcore.sh

# If missing, add it
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/YOUR_USERNAME/restart_voxcore.sh 2>&1 >> ~/logs/cron.log") | crontab -

# Make restart script executable
chmod +x ~/restart_voxcore.sh

# Test manually
~/restart_voxcore.sh

# Check cron log
tail -f ~/logs/cron.log

# Verify cron is running
ps aux | grep cron
```

---

### **Issue 7: "Port already in use" or "Address already in use"**

**Cause:** Backend process still running from previous start

**Solution:**
```bash
ssh YOUR_USERNAME@voxcore.org

# Find what's using port 8000
lsof -i :8000
# or
netstat -tlnp | grep 8000

# Kill the process
pkill -f "uvicorn voxquery.api.main"

# Wait 3 seconds, verify it's gone
sleep 3
ps aux | grep uvicorn | grep -v grep

# Restart
cd ~/voxcore/voxcore/voxquery
source venv/bin/activate
nohup python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 >> ~/logs/voxcore-backend.log 2>&1 &
```

---

## **📊 Production Monitoring Setup**

### **Option A: Manual Daily Checks**

Create file: `~/check_voxcore_health.sh`

```bash
#!/bin/bash
LOG_FILE=~/logs/health-check.log
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Health Check" >> $LOG_FILE

# Check backend process
if pgrep -f "uvicorn voxquery.api.main" > /dev/null; then
    BACKEND_STATUS="✓ Running"
else
    BACKEND_STATUS="✗ NOT RUNNING - ALERT!"
fi

# Check API response
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health)
if [ "$API_RESPONSE" == "200" ]; then
    API_STATUS="✓ 200 OK"
else
    API_STATUS="✗ HTTP $API_RESPONSE"
fi

# Check disk space
DISK=$(df ~ | tail -1 | awk '{print $5}')
if [ ${DISK%\%} -gt 90 ]; then
    DISK_STATUS="⚠ WARNING: $DISK used"
else
    DISK_STATUS="✓ $DISK used"
fi

# Check memory
MEMORY=$(free | grep Mem | awk '{printf("%.0f%%", $3/$2 * 100.0)}')
if [ ${MEMORY%\%} -gt 80 ]; then
    MEMORY_STATUS="⚠ WARNING: $MEMORY used"
else
    MEMORY_STATUS="✓ $MEMORY used"
fi

# Log results
echo "  Backend:  $BACKEND_STATUS" >> $LOG_FILE
echo "  API:      $API_STATUS" >> $LOG_FILE
echo "  Disk:     $DISK_STATUS" >> $LOG_FILE
echo "  Memory:   $MEMORY_STATUS" >> $LOG_FILE
echo "" >> $LOG_FILE

# If any issues, log to alert file
if [[ "$BACKEND_STATUS" == *"NOT RUNNING"* ]] || [[ "$API_STATUS" == *"504"* ]]; then
    echo "[$TIMESTAMP] ALERT: Backend issue detected" >> ~/logs/alerts.log
fi
```

Set as daily cron job:
```bash
# Run daily at 3 AM
(crontab -l 2>/dev/null; echo "0 3 * * * ~/check_voxcore_health.sh") | crontab -
```

### **Option B: Use Third-Party Monitoring**

Services that send alerts when your site goes down:

1. **UptimeRobot** (Free)
   - https://uptimerobot.com
   - Monitor: https://voxcore.org/api/health
   - Get alerts via email/SMS if down

2. **Pingdom** (Free)
   - https://www.pingdom.com
   - Monitors uptime from multiple locations globally

3. **StatusCake** (Free)
   - https://www.statuscake.com
   - Detailed performance analytics

---

## **📈 Performance Monitoring**

### **Check Backend Resource Usage**

```bash
ssh YOUR_USERNAME@voxcore.org

# Real-time process monitor
top -p $(pgrep -f "uvicorn voxquery.api.main")

# Memory usage
ps aux | grep uvicorn | grep -v grep | awk '{print "Memory:", $6/1024 "MB"}'

# CPU usage
# (from top output, look for %CPU column)
```

### **Analyze Logs for Performance Issues**

```bash
ssh YOUR_USERNAME@voxcore.org

# Find slow queries
grep -E "duration|took|ms" ~/logs/voxcore-backend.log | tail -20

# Count errors by type
grep "ERROR\|WARNING\|Exception" ~/logs/voxcore-backend.log | sort | uniq -c

# View last errors
grep "ERROR" ~/logs/voxcore-backend.log | tail -10
```

---

## **🔒 Security Monitoring**

### **Check for Unauthorized Access**

```bash
ssh YOUR_USERNAME@voxcore.org

# View failed login attempts
grep "failed" ~/logs/voxcore-backend.log

# Check API error rates (401, 403, 500)
grep -E "401|403|500" ~/logs/voxcore-backend.log | wc -l

# IP addresses making requests
grep -oP '(?<=client_ip=)[^ ]+' ~/logs/voxcore-backend.log | sort | uniq -c
```

---

## **✅ Daily Maintenance Checklist**

```bash
# Run daily (add to cron at 3 AM)
echo "=== VoxCore Daily Health Check ===" 
echo "Timestamp: $(date)"

# 1. Backend running?
ps aux | grep uvicorn | grep -v grep && echo "[✓] Backend running" || echo "[✗] ALERT: Backend down"

# 2. API responding?
curl -s http://127.0.0.1:8000/health | grep healthy > /dev/null && echo "[✓] API healthy" || echo "[✗] ALERT: API unhealthy"

# 3. Frontend accessible?
curl -s https://voxcore.org/ | grep -q "VoxCore\|React" && echo "[✓] Frontend loaded" || echo "[✗] ALERT: Frontend issue"

# 4. Disk space OK?
DISK=$(df ~ | tail -1 | awk '{print $5}' | sed 's/%//')
[ $DISK -lt 90 ] && echo "[✓] Disk OK ($DISK% used)" || echo "[✗] ALERT: Disk critical ($DISK%)"

# 5. Cron job active?
crontab -l | grep -q restart_voxcore && echo "[✓] Auto-restart active" || echo "[✗] ALERT: Cron disabled"

echo "Check complete at $(date +%H:%M:%S)"
```

---

## **🚑 Emergency Recovery**

If everything fails:

```bash
ssh YOUR_USERNAME@voxcore.org

# Kill everything
pkill -f "uvicorn"
pkill -f "python -m uvicorn"

# Wait
sleep 5

# Start fresh
cd ~/voxcore/voxcore/voxquery
source venv/bin/activate
python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 --reload --log-level debug

# Watch output, Ctrl+C to stop
# Fix issues as they appear
```

---

## **📞 Getting Help**

1. **Check logs first:**
   ```bash
   tail -f ~/logs/voxcore-backend.log
   ```

2. **Search error in logs:**
   ```bash
   grep -i "your error message" ~/logs/voxcore-backend.log
   ```

3. **Test individual components:**
   ```bash
   # Database connection
   python -c "import pyodbc; print('Database OK')"
   
   # API startup
   python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000
   
   # Frontend files
   ls -la ~/public_html/voxcore/
   ```

---

**Remember:** Problems are usually logging-related. Always check the logs first. The answer is almost always in `~/logs/voxcore-backend.log`.
