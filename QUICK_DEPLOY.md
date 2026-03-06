# 🚀 VoxCore Deployment - Quick Start (30 Minutes)

## **What This Does**
Moves your working local VoxCore app (backend + frontend + friendly labels) to voxcore.org for 24/7 production uptime.

---

## **🎯 Quick Path (Fastest)**

### **1. Build Frontend (5 min)**
```bash
cd c:\Users\USER\Documents\trae_projects\VoxQuery\frontend
set VITE_API_URL=https://voxcore.org/api
npm install
npm run build
```

### **2. Get SSH Access (1 min)**
Ask your hosting provider or cPanel administrator for:
- SSH username (usually 'your_username')
- SSH password (or upload SSH key)
- Confirm Node.js and Python 3.8+ installed

### **3. Update Script (1 min)**
Edit `deploy_to_cpanel.sh` line 29 and update:
```bash
# Find this line:
DATABASE_URL=mssql://sa:YOUR_PASSWORD@YOUR_DB_HOST:1433/AdventureWorks2022

# Replace YOUR_PASSWORD and YOUR_DB_HOST with actual values
```

### **4. Run Deployment (10 min)**
```bash
# Upload and run script on cPanel server
scp deploy_to_cpanel.sh YOUR_USERNAME@voxcore.org:~/deploy.sh
ssh YOUR_USERNAME@voxcore.org bash ~/deploy.sh
```

### **5. Wait & Verify (2 min)**
Open browser:
- Frontend: https://voxcore.org
- API Health: https://voxcore.org/api/health
- API Docs: https://voxcore.org/api/docs

✅ **Done!** VoxCore is live and auto-restarts if it crashes.

---

## **⚠️ If Something Goes Wrong**

### **SSH into server and check logs:**
```bash
ssh YOUR_USERNAME@voxcore.org

# View backend logs
tail -f ~/logs/voxcore-backend.log

# Check if backend is running
ps aux | grep uvicorn

# View restart attempts
tail -f ~/logs/voxcore-restart.log

# Manually restart
pkill -f "uvicorn"
cd ~/voxcore/voxcore/voxquery
source venv/bin/activate
python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000
```

---

## **📋 Detailed Instructions (If Script Doesn't Work)**

See **CPANEL_DEPLOYMENT_STEPS.md** for step-by-step manual deployment.

---

## **✅ Verification Checklist**

After deployment, verify:

```bash
# 1. Frontend loads
curl -I https://voxcore.org/
# Expected: 200 OK

# 2. API health check
curl https://voxcore.org/api/health
# Expected: {"status":"healthy",...}

# 3. API documentation
curl -I https://voxcore.org/api/docs
# Expected: 200 OK

# 4. Backend process running
ssh YOUR_USERNAME@voxcore.org
ps aux | grep uvicorn
# Expected: python -m uvicorn voxquery.api.main:app ...

# 5. Auto-restart cron active
crontab -l
# Expected: Include "*/5 * * * * ~/restart_voxcore.sh"
```

---

## **🔄 Updating Production Later**

When you make local changes and want to update production:

```bash
# 1. Rebuild frontend locally
cd frontend
set VITE_API_URL=https://voxcore.org/api
npm run build

# 2. Upload new files
scp -r frontend\dist\* YOUR_USERNAME@voxcore.org:~/public_html/voxcore/

# 3. Backend usually doesn't need update unless you changed code
# If you changed Python code:
scp -r voxcore YOUR_USERNAME@voxcore.org:~/voxcore/

# 4. Restart backend (if needed)
ssh YOUR_USERNAME@voxcore.org pkill -f "uvicorn"
# Will auto-restart via cron in 5 minutes
```

---

## **📞 Support**

If deployment fails:
1. Check logs: `tail -f ~/logs/voxcore-backend.log`
2. Try manual start: See "If Something Goes Wrong" section
3. Verify database connection: Check `DATABASE_URL` in `.env`
4. Ensure ports: Backend should be on 127.0.0.1:8000
5. Check permissions: `chmod +x ~/restart_voxcore.sh`

---

## **File Locations on cPanel Server**

```
/home/YOUR_USERNAME/
├── public_html/voxcore/          (Frontend - React static files)
├── voxcore/
│   └── voxcore/voxquery/         (Backend - Python code)
│       ├── venv/                 (Virtual environment)
│       ├── .env                  (Configuration)
│       └── requirements.txt       (Dependencies)
└── logs/
    ├── voxcore-backend.log       (Backend output)
    ├── voxcore-restart.log       (Auto-restart log)
    └── cron.log                  (Cron activity)
```

---

## **Monitoring Commands**

```bash
# SSH once and keep terminal open
ssh YOUR_USERNAME@voxcore.org

# Watch backend in real-time
tail -f ~/logs/voxcore-backend.log

# In another terminal, check status
ps aux | grep uvicorn

# See last 24 hours of restarts
grep "restart" ~/logs/voxcore-restart.log

# Test API
curl http://127.0.0.1:8000/health
```

---

**That's it! Your VoxCore is now in production. 🎉**

Next step: Monitor for 24 hours to confirm 100% uptime, then celebrate! 🚀
