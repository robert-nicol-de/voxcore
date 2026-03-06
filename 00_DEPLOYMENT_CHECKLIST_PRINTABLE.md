# 📋 VoxCore Production Deployment Checklist

**Deployment Date:** ________________  
**Deployed By:** ________________  
**voxcore.org Domain:** ________________  

---

## **PHASE 1: PRE-DEPLOYMENT (Do These First)**

### Local Preparation
- [ ] Backend running on `http://localhost:8000` (verified with `curl http://localhost:8000/health`)
- [ ] Frontend running on `http://localhost:5175` (opens in browser)
- [ ] Can execute a query locally and see friendly column names
- [ ] Charts display with proper labels (no raw SQL names)
- [ ] All local fixes working (column mapping, label formating, etc.)

### Credentials Ready
- [ ] Have cPanel username and password
- [ ] Have SSH credentials (if SSH available)
- [ ] Have database host, username, password for production
- [ ] Have FTP/SFTP username and password (if not using SSH)
- [ ] Have domain: `https://voxcore.org` accessible

### Tools Installed Locally
- [ ] Node.js v14+: `node --version` ✓
- [ ] npm v6+: `npm --version` ✓
- [ ] Python 3.8+: `python --version` ✓
- [ ] Git or file copy method ready

---

## **PHASE 2: BUILD FRONTEND (Do on Your Computer)**

### Step 1: Prepare Frontend for Production
- [ ] Open terminal/cmd in `VoxQuery/frontend` directory
- [ ] Set environment variable: `set VITE_API_URL=https://voxcore.org/api`
- [ ] Run: `npm install` (wait for completion)
- [ ] Run: `npm run build` (wait for "dist/" folder to appear)
- [ ] Verify: `frontend/dist/` folder exists with these files:
  - [ ] `index.html` (main entry point)
  - [ ] `assets/` folder (CSS/JS bundles)
  - [ ] `config.json` (if app uses it)

---

## **PHASE 3: UPLOAD TO CPANEL (Choose One)**

### OPTION A: Using Automated Script (Fastest - 10 min)
- [ ] Edit `deploy_to_cpanel.sh` file:
  - [ ] Find line with `DATABASE_URL=mssql://...`
  - [ ] Replace `YOUR_PASSWORD` with actual password
  - [ ] Replace `YOUR_DB_HOST` with actual host (e.g., `192.168.1.100`)
  - [ ] Save file
- [ ] Open terminal in VoxQuery directory
- [ ] Run: `scp deploy_to_cpanel.sh YOUR_USER@voxcore.org:~/deploy.sh`
- [ ] Run: `ssh YOUR_USER@voxcore.org bash ~/deploy.sh`
- [ ] Watch output in terminal, wait for "✓ VoxCore is now LIVE"
- [ ] **Jump to Phase 4**

### OPTION B: Manual Upload via SCP (15 min)
- [ ] Open terminal/cmd in VoxQuery directory
- [ ] Upload frontend files:
  ```bash
  scp -r frontend\dist\* YOUR_USER@voxcore.org:~/public_html/voxcore/
  ```
  - [ ] Wait for all files to upload
  
- [ ] Upload backend:
  ```bash
  scp -r voxcore YOUR_USER@voxcore.org:~/voxcore/
  ```
  - [ ] Wait for all files to upload

- [ ] Upload start script:
  ```bash
  scp voxcore\voxquery\start_backend.sh YOUR_USER@voxcore.org:~/voxcore/voxcore/voxquery/
  ```
  - [ ] Verify upload complete

- [ ] **Continue to Phase 3, Step B2 below**

### OPTION B2: Manual Setup (Continue if using manual upload)

#### SSH into cPanel Server
- [ ] Run: `ssh YOUR_USER@voxcore.org`
- [ ] You now see prompt: `[YOUR_USER@server ~]$`

#### Create Virtual Environment
- [ ] Run: `cd ~/voxcore/voxcore/voxquery`
- [ ] Run: `python3 -m venv venv`
- [ ] Run: `source venv/bin/activate`
- [ ] Run: `pip install --upgrade pip`
- [ ] Run: `pip install -r requirements.txt`
- [ ] Wait for all packages to install (2-5 minutes)

#### Create .env Configuration File
- [ ] Run: 
  ```bash
  cat > .env << EOF
  DATABASE_URL=mssql://sa:YOUR_PASSWORD@YOUR_DB_HOST:1433/AdventureWorks2022
  VITE_API_URL=https://voxcore.org/api
  ALLOWED_HOSTS=voxcore.org,www.voxcore.org
  ENV=production
  EOF
  ```
  - [ ] Verify syntax is correct

#### Test Backend Startup
- [ ] Run: `python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000`
- [ ] Wait for: `INFO: Application startup complete`
- [ ] In another terminal, test: `curl http://127.0.0.1:8000/health`
- [ ] Verify response: `{"status":"healthy","timestamp":"..."}`
- [ ] Stop backend: Press `Ctrl+C`

#### Start Backend in Background
- [ ] Run: `nohup python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 >> ~/logs/voxcore-backend.log 2>&1 &`
- [ ] Verify running: `ps aux | grep uvicorn`
- [ ] Should see the uvicorn process in output

#### Setup Auto-Restart
- [ ] Create restart script:
  ```bash
  cat > ~/restart_voxcore.sh << 'EOF'
  #!/bin/bash
  if ! pgrep -f "uvicorn voxquery.api.main" > /dev/null; then
      echo "[$(date)] Restarting backend" >> ~/logs/voxcore-restart.log
      cd ~/voxcore/voxcore/voxquery
      source venv/bin/activate
      nohup python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 >> ~/logs/voxcore-backend.log 2>&1 &
  fi
  EOF
  ```
  - [ ] Script created successfully

- [ ] Make executable: `chmod +x ~/restart_voxcore.sh`
- [ ] Add to cron: `(crontab -l 2>/dev/null; echo "*/5 * * * * ~/restart_voxcore.sh") | crontab -`
- [ ] Verify cron: `crontab -l` shows the restart command

#### Setup .htaccess for Frontend Routing
- [ ] Run:
  ```bash
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
  ```
  - [ ] .htaccess created successfully

- [ ] Disconnect SSH: `logout` or `exit`

---

## **PHASE 4: VERIFY DEPLOYMENT (Do in Browser)**

### Frontend Check
- [ ] Open: `https://voxcore.org/`
- [ ] React app loads (you see VoxCore UI)
- [ ] No error messages in browser console (F12 > Console)

### API Health Check
- [ ] Open: `https://voxcore.org/api/health`
- [ ] See response: `{"status":"healthy",...}`

### API Documentation
- [ ] Open: `https://voxcore.org/api/docs`
- [ ] See Swagger UI with all endpoints listed

### Functional Testing
- [ ] Type a test query: "Show me sales by month"
- [ ] Results appear with friendly column names (not raw SQL)
- [ ] Chart displays with clean labels (not table.column)
- [ ] Table displays with formatted headers

### Data Verification
- [ ] Can see actual data from AdventureWorks2022
- [ ] Column names are readable (e.g., "Month Start", not "MonthStart")
- [ ] Charts have proper axis labels
- [ ] No database connection errors

---

## **PHASE 5: PRODUCTION MONITORING SETUP**

### Manual Monitoring
- [ ] SSH into server once per day to check logs:
  ```bash
  ssh YOUR_USER@voxcore.org
  tail -f ~/logs/voxcore-backend.log
  ```
  - [ ] Look for errors or exceptions
  - [ ] If clean, backend is healthy

### Automated Monitoring (Optional but Recommended)
- [ ] Sign up for free service: UptimeRobot.com
- [ ] Add monitor for: `https://voxcore.org/api/health`
- [ ] Set alerts to your email/phone
- [ ] Will notify you if site goes down (24/7 monitoring)

### Backup & Documentation
- [ ] Note deployment date: ________________
- [ ] Note database host/credentials location
- [ ] Keep copy of `.env` file safe (contains passwords)
- [ ] Document any custom changes you made

---

## **PHASE 6: VERIFY 24-HOUR UPTIME (Tomorrow)**

After letting it run overnight:

- [ ] Check site still accessible: `https://voxcore.org`
- [ ] Check API health: `https://voxcore.org/api/health`
- [ ] Check backend logs: `ssh YOUR_USER@voxcore.org; tail -f ~/logs/voxcore-backend.log`
- [ ] See auto-restart in action: Check `~/logs/voxcore-restart.log`
- [ ] Execute queries and verify results
- [ ] Check system resources didn't max out: `free -h` (memory), `df -h` (disk)

---

## **TROUBLESHOOTING QUICK REFERENCE**

If something breaks, check this in order:

1. **"Connection refused"**
   - [ ] SSH and check: `ps aux | grep uvicorn`
   - [ ] If not running: `~/restart_voxcore.sh`
   - [ ] If still fails: Check logs with `tail ~/logs/voxcore-backend.log`

2. **"Blank page"**
   - [ ] Check frontend files uploaded: `ls ~/public_html/voxcore/`
   - [ ] If missing: Re-upload with SCP
   - [ ] Clear browser cache (Ctrl+Shift+Delete)

3. **"API errors"**
   - [ ] Database credentials in `.env` correct?
   - [ ] Check .htaccess routing configured
   - [ ] Restart backend: `pkill -f uvicorn; sleep 2; ~/restart_voxcore.sh`

4. **"Port 8000 already in use"**
   - [ ] Kill old process: `pkill -f "uvicorn voxquery"`
   - [ ] Wait 3 seconds
   - [ ] Start new: `~/restart_voxcore.sh`

5. **Full debugging**
   - [ ] Read `PRODUCTION_MONITORING.md` "Common Issues" section
   - [ ] Check all logs:
     ```bash
     tail ~/logs/voxcore-backend.log
     tail ~/logs/voxcore-restart.log
     tail ~/logs/cron.log
     ```

---

## **SIGN-OFF**

- [ ] Deployment completed successfully
- [ ] All verification tests passed
- [ ] Monitoring setup complete
- [ ] Team notified of go-live
- [ ] Deployment notes saved for future reference

**Deployment Status:** ☐ In Progress | ☐ Complete | ☐ Issues Found

**Notes:** 
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

**Completed By:** ________________________  
**Date/Time:** ________________________  
**Next Review:** ________________________  

---

**Remember:** If anything goes wrong, check `PRODUCTION_MONITORING.md` - it has solutions for 99% of issues. Good luck! 🚀
