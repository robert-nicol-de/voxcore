# 🎯 VoxCore to Production - Complete Deployment Map

## **Your Situation**
✅ Local VoxCore is working perfectly:
- Backend running on port 8000 with FastAPI
- Frontend running on port 5175 with Vite
- Friendly column labels working (MonthStart → Month Start)
- Database: SQL Server AdventureWorks2022

❌ But it only works on localhost and crashes when you restart

✅ Goal: Move to voxcore.org for 100% uptime production

---

## **📂 Deployment Files Created**

Here are the 4 files I created to help you deploy:

### **1. `deploy_to_cpanel.sh` (FASTEST - If you want automation)**
**What:** Completely automated deployment script
**Time:** ~15-20 minutes total (including upload time)
**How to use:**
1. Edit line where it says `DATABASE_URL=mssql://...` with your real credentials
2. Upload to cPanel: `scp deploy_to_cpanel.sh YOUR_USER@voxcore.org:~/deploy.sh`
3. Run it: `ssh YOUR_USER@voxcore.org bash ~/deploy.sh`
4. ✅ Done - your app is live

**Pros:** Fastest, handles everything automatically
**Cons:** Requires SSH access, need to edit one line

---

### **2. `QUICK_DEPLOY.md` (RECOMMENDED - If you're in a hurry)**
**What:** 30-minute quick reference with 5 main steps
**Time:** 30 minutes
**Use when:** You understand the general process and want the speediest path
**Contains:**
- Quick execution steps
- What to do if something goes wrong
- Verification checklist

---

### **3. `CPANEL_DEPLOYMENT_STEPS.md` (DETAILED - If you want to understand everything)**
**What:** 13-step comprehensive deployment guide with explanations
**Time:** 45-60 minutes (if doing everything manually)
**Use when:**
- You want to understand each step
- You don't have SSH/can only use cPanel File Manager
- You want to manually configure each part
- You need to troubleshoot issues step-by-step

**Contains:**
- Build frontend locally
- Upload via SCP or FTP
- Setup Python virtual environment
- Configure .htaccess for routing
- Auto-restart setup
- Verification tests

---

### **4. `PRODUCTION_MONITORING.md` (FOR 100% UPTIME)**
**What:** Monitoring, troubleshooting, and health checks
**Use when:**
- Deployment is done and you want to keep it running 24/7
- You need to troubleshoot issues
- You want to setup automatic monitoring
- Backend crashes and you need to recover

**Contains:**
- 7 common issues and solutions
- Real-time monitoring commands
- Performance monitoring
- Security monitoring
- Daily maintenance checklist

---

## **🚀 Recommended Path (Choose one)**

### **Path A: Fast & Automated (20 minutes)**
1. Build frontend locally (5 min)
2. Edit deploy script (1 min)
3. Run deploy script (10 min)
4. Verify in browser (2 min)

**Files to use:** `deploy_to_cpanel.sh` + `PRODUCTION_MONITORING.md`

```bash
# Step 1: Build
cd frontend
set VITE_API_URL=https://voxcore.org/api
npm run build

# Step 2: Edit script
# Open deploy_to_cpanel.sh, change DATABASE_URL line

# Step 3: Deploy
scp deploy_to_cpanel.sh YOUR_USER@voxcore.org:~/deploy.sh
ssh YOUR_USER@voxcore.org bash ~/deploy.sh

# Step 4: Open browser
# https://voxcore.org
```

**Time investment:** 20 minutes

---

### **Path B: Manual but Comprehensive (60 minutes)**
Follow `CPANEL_DEPLOYMENT_STEPS.md` line-by-line

**Pros:**
- Learn exactly what's happening
- Can debug easier
- Control each piece

**Cons:**
- Takes longer
- More individual commands

**Time investment:** 60 minutes

---

### **Path C: FTP Only (No SSH)**
If you don't have SSH access:
1. Use `CPANEL_DEPLOYMENT_STEPS.md` Phases 1-2
2. Use FileZilla (FTP/SFTP) instead of SCP
3. Use cPanel File Manager for .htaccess setup
4. Contact hosting support to start backend

**Time investment:** 45 minutes (minus tech support wait time)

---

## **✅ Pre-Deployment Checklist**

Before starting, have ready:

- [ ] Database credentials (host, username, password, database name)
- [ ] cPanel username and password (or SSH key)
- [ ] cPanel hosting with SSH access (if using automated path)
- [ ] Node.js installed locally (check: `node --version`)
- [ ] Python 3.8+ on cPanel server (hosting provider has it)
- [ ] Local VoxCore working (backend on 8000, frontend on 5175)
- [ ] `frontend/dist/` folder ready (run `npm run build`)

---

## **🎯 Which File to Read?**

| Your Situation | Read This File |
|---|---|
| I want the fastest deployment possible | `QUICK_DEPLOY.md` |
| I want to automate everything | Use `deploy_to_cpanel.sh` |
| I want detailed step-by-step instructions | `CPANEL_DEPLOYMENT_STEPS.md` |
| I want to understand the process deeply | `CPANEL_DEPLOYMENT_STEPS.md` (Phase 1-5 explanations) |
| My backend crashes, how do I fix it? | `PRODUCTION_MONITORING.md` (Issues section) |
| I want 100% uptime monitoring | `PRODUCTION_MONITORING.md` (Monitoring Setup section) |
| I'm getting an error during deployment | `PRODUCTION_MONITORING.md` (Troubleshooting section) |
| I need to update my app after deployment | `QUICK_DEPLOY.md` (Updating Production section) |

---

## **🔄 Deployment Decision Tree**

```
Do you have SSH access to cPanel?
├─ YES
│  ├─ Want fastest deployment?
│  │  └─ Use: deploy_to_cpanel.sh + QUICK_DEPLOY.md
│  └─ Want to understand each step?
│     └─ Use: CPANEL_DEPLOYMENT_STEPS.md (manual)
└─ NO (FTP only)
   └─ Use: CPANEL_DEPLOYMENT_STEPS.md (FTP sections)
```

---

## **⏱ Time Estimates**

| Task | Time | Tool |
|------|------|------|
| Build frontend | 5 min | Local terminal |
| Automated deploy | 10 min | `deploy_to_cpanel.sh` |
| Manual deploy | 40 min | `CPANEL_DEPLOYMENT_STEPS.md` |
| Verify everything | 5 min | Browser |
| **TOTAL (Fastest Path)** | **20 min** | Script + Quick Deploy |
| **TOTAL (Manual Path)** | **60 min** | Detailed steps |

---

## **📊 What Gets Deployed**

Your will have on voxcore.org:

```
📦 Frontend (React/Vite)
   ├─ https://voxcore.org/  (loads React app)
   ├─ All charts with friendly labels ✓
   ├─ All tables with friendly column names ✓
   └─ Auto-refreshing API calls ✓

📦 Backend (Python/FastAPI)
   ├─ https://voxcore.org/api/health (monitoring)
   ├─ https://voxcore.org/api/docs (API documentation)
   ├─ https://voxcore.org/api/v1/query (execute queries)
   ├─ Column mapping enabled ✓
   ├─ Friendly labels in responses ✓
   └─ Auto-restart if crashes ✓

🗄️ Database
   └─ SQL Server (your existing database)

🔄 Auto-Restart
   └─ Checks every 5 minutes, restarts if down
```

---

## **🎓 Learning Outcomes**

After deployment, you'll understand:

1. **Frontend deployment:** How to build React and deploy static files
2. **Backend deployment:** How to run Python FastAPI in production
3. **Process management:** How auto-restart keeps services alive
4. **Web server routing:** How Apache .htaccess routes requests
5. **Monitoring:** How to monitor and troubleshoot production systems
6. **DevOps basics:** Everything you need for small-scale production

---

## **❓ FAQ**

### **Q: Will my data be safe?**
A: Your SQL Server database stays on your original host. Only frontend + backend code move to cPanel.

### **Q: What if something breaks?**
A: Auto-restart runs every 5 minutes. Worst case, your site is down for 5 minutes, then auto-recovers. See `PRODUCTION_MONITORING.md` for manual recovery.

### **Q: Can I update my app after deployment?**
A: Yes! Rebuild frontend locally, upload new files. Backend auto-restarts if you update code. See `QUICK_DEPLOY.md` "Updating Production" section.

### **Q: What if I don't have SSH?**
A: Use `CPANEL_DEPLOYMENT_STEPS.md` with FTP File Manager instead of SCP/SSH commands.

### **Q: How do I monitor uptime?**
A: See `PRODUCTION_MONITORING.md` "Monitoring Setup" - includes free services like UptimeRobot.

### **Q: Can I rollback if something goes wrong?**
A: Yes! Upload old `frontend/dist/` files again, or restore old backend code, then restart.

---

## **🚨 Deployment Troubleshooting Quick Guide**

| Problem | Quick Fix |
|---------|-----------|
| "Connection refused" | Check if backend running: `ps aux | grep uvicorn` |
| "502 Bad Gateway" | Backend crashed, auto-restart in 5 min or manual: `~/restart_voxcore.sh` |
| "Blank frontend page" | Check files uploaded: `ls ~/public_html/voxcore/` |
| "API calls failing" | Check .htaccess proxy settings in `PRODUCTION_MONITORING.md` |
| "Database error" | Edit .env with correct credentials, restart backend |
| "Module not found" | Run `pip install -r requirements.txt` in venv |

**For any issue:** Check `PRODUCTION_MONITORING.md` "Common Issues" section - answer is there 99% of the time.

---

## **✨ Success = You Should See**

After successful deployment:

```
1. Open https://voxcore.org in browser
   ✅ You see the VoxCore UI loading
   ✅ Charts render with data
   ✅ Can type queries
   
2. Open https://voxcore.org/api/health in browser
   ✅ You see {"status":"healthy","timestamp":"..."}
   
3. Execute a query in the UI
   ✅ Results appear with friendly column names
   ✅ Charts show with clean axis labels
   ✅ No errors in browser console
   
4. Test 24/7 uptime
   ✅ Leave it running for a day
   ✅ Check logs show successful restarts
   ✅ Site still works after 24 hours
```

---

## **🎉 Next Steps After Successful Deployment**

1. **Monitor for 24 hours:** Keep an eye on logs
2. **Test performance:** See how many concurrent users before slowdown
3. **Setup backups:** Ask hosting about database backup policies
4. **Get SSL certificate:** Should be automatic via AutoSSL (check cPanel)
5. **Setup email:** If you want to send notifications
6. **Monitor uptime:** Setup UptimeRobot or similar for alerts
7. **Plan updates:** How often will you update the app?
8. **Document:** Keep notes on what you deployed and when

---

## **📞 Getting Help**

1. **Script-related issues:** Check logs: `tail -f ~/logs/voxcore-backend.log`
2. **Deployment stuck:** Read `CPANEL_DEPLOYMENT_STEPS.md` for that specific phase
3. **Backend crashed:** Use `PRODUCTION_MONITORING.md` troubleshooting section
4. **Can't upload files:** Contact cPanel support for FTP/SSH help
5. **Database connection fails:** Verify credentials in `.env` file

---

**Ready? Start with:** `QUICK_DEPLOY.md` if you have 30 minutes, or `deploy_to_cpanel.sh` if you want full automation.

**Questions?** Each deployment file has detailed explanations. Read the appropriate file for your situation above.

**Good luck! 🚀**
