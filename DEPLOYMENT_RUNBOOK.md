# 🚀 VOXCORE DEPLOYMENT RUNBOOK

**Use this guide to deploy VoxCore to staging and production environments.**

---

## 📋 PRE-DEPLOYMENT (24 hours before)

### 1. Run Full Test Suite
```bash
# Run all tests
cd backend
pytest voxcore/tests/test_system.py -v
pytest voxcore/tests/test_production_validation.py -v
pytest voxcore/tests/test_production_security.py -v

# All tests must pass before proceeding
# If any fail: fix bugs and re-run
```

### 2. Review Recent Changes
```bash
# See what changed since last deployment
git log --oneline -20

# Make sure changes are reviewed and approved
# Check for: secrets, debugging code, production issues
```

### 3. Verify Configuration
```bash
# Staging configuration
cat .env.staging | grep -E "^[A-Z_]+="

# Production configuration (in Render dashboard only)
# DO NOT create .env.prod file!
```

### 4. Coordinate with Team
- [ ] Notify team of deployment window
- [ ] Check if critical issues are being worked on
- [ ] Ensure on-call support is available
- [ ] Have rollback plan ready

---

## 🧪 DEPLOY TO STAGING (First!)

**Always deploy to staging first. Never deploy directly to production.**

### Step 1: Create Release Branch
```bash
# Create release branch from main
git checkout -b release/v1.0.0 main

# Or if following semantic versioning
git checkout main
git pull origin main
git checkout -b release/v$(date +%Y%m%d)
```

### Step 2: Update Version Number
```bash
# Update in backend/voxcore/__init__.py
nano backend/voxcore/__init__.py

# Change:
# __version__ = "16.0.0"
# To:
# __version__ = "16.0.1"  # or next version
```

### Step 3: Commit Release
```bash
git add backend/voxcore/__init__.py
git commit -m "Release v16.0.1"
git push origin release/v1.0.0
```

### Step 4: Deploy via Render Dashboard

**Render Auto-Deploy (Recommended):**
```
1. Push to main branch (or your configured branch)
2. Render automatically detects
3. Auto-builds and deploys
4. Takes 2-5 minutes
5. Health check validates
```

**Manual Deploy (Alternative):**
```
1. Go to https://dashboard.render.com
2. Select "voxquery-backend-staging"
3. Click "Manual Deploy"
4. Select branch (usually main)
5. Click "Deploy"
6. Wait for status: "Live"
```

### Step 5: Monitor Deployment
```bash
# Watch build logs in Render dashboard
# Check:
# - Build successful (green ✓)
# - Start successful
# - Health check passing

# Or via terminal (if available)
render logs voxquery-backend-staging --follow
```

### Step 6: Verify Staging Deploy
```bash
# Test health endpoint
curl https://api-staging.voxquery.com/api/v1/health

# Should return: {"status": "healthy"}

# Test a real query
curl -X POST https://api-staging.voxquery.com/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show revenue by region",
    "org_id": "org-test",
    "user_id": "user-test",
    "user_role": "analyst"
  }'

# Should return valid response with metadata
```

### Step 7: Run Smoke Tests
```bash
# From frontend (if applicable)
npm test -- --env=staging

# Or manual API tests
# - Test login works
# - Test query execution
# - Test error handling
# - Test rate limiting
```

### Step 8: Monitor for 60 Minutes
```bash
# Watch logs for errors
# Check metrics endpoint
curl https://api-staging.voxquery.com/api/v1/metrics/summary

# Verify:
# - No error spikes
# - Latency normal
# - Cache hit rate > 50%
# - No critical bugs
```

**If Issues Found:**
```bash
# Rollback to previous version
git revert HEAD
git push origin main

# Render auto-redeploys
# Or manually select previous build in dashboard
```

---

## 🔥 DEPLOY TO PRODUCTION (Only After Staging Stable)

**Production deployment requires extra care and verification.**

### Pre-Production Checklist
- [ ] Staging has been stable for 60+ minutes
- [ ] No error spikes in logs
- [ ] Performance metrics acceptable
- [ ] Team is ready for go-live
- [ ] On-call support standing by
- [ ] Rollback plan documented
- [ ] Production database backed up (recent)

### Step 1: Tag Release in Git
```bash
# Create release tag
git tag -a v16.0.1 -m "Production release v16.0.1"

# Push tag to GitHub
git push origin v16.0.1

# This creates release notes automatically
```

### Step 2: Deploy via Render

**Important: Production is SEPARATE service from staging!**

**Render Production Deploy:**
```
1. Go to https://dashboard.render.com
2. Select "voxquery-backend-prod" (NOT staging!)
3. Click "Manual Deploy"
4. Select branch: main
5. Click "Deploy"
6. Monitor build logs carefully
```

### Step 3: Monitor Build & Startup
```bash
# Watch Render logs
# Expected timeline:
# - Build: 2-3 minutes (install dependencies, tests)
# - Deploy: 1-2 minutes (start server, health checks)
# - Total: 5-10 minutes

# Signs of problems:
# - Build fails (red X)
# - Startup fails (boot errors)
# - Health check fails (timeout)
```

### Step 4: Verify Production Health
```bash
# Health endpoint
curl https://api.voxquery.com/api/v1/health

# Metrics endpoint
curl https://api.voxquery.com/api/v1/metrics/summary

# Sample query (with auth token)
curl -X POST https://api.voxquery.com/api/v1/query \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test production query",
    "org_id": "org-prod-test",
    "user_id": "user-test",
    "user_role": "analyst"
  }'
```

### Step 5: Monitor Production (First Hour)
```bash
# Check metrics every 5 minutes
for i in {1..12}; do
  echo "Check $i..."
  curl https://api.voxquery.com/api/v1/metrics/summary | jq .
  sleep 300  # 5 minutes
done

# Watch for:
# ✅ Error rate stays < 1%
# ✅ Latency stays < 2 seconds
# ✅ Cache hit rate > 50%
# ✅ No timeout errors
# ✅ No database connection issues

# ❌ Stop if you see:
# ❌ Error rate> 5%
# ❌ Timeouts > 1%
# ❌ Database connection errors
# ❌ Memory usage growing
```

### Step 6: Smoke Tests in Production
```bash
# Test critical user flows
# Example:
# 1. User logs in
# 2. User runs query
# 3. User sees results with trust badge
# 4. User checks metrics
# 5. All appears correct

# If user-facing issues found:
# IMMEDIATELY ROLLBACK (see below)
```

### Step 7: Communication
```bash
# When deploy successful:
# Alert stakeholders:
# - Slack: "Released v16.0.1 to production ✅"
# - Email: notify customers if applicable
# - Status page: update if available

# Links to include:
# - Deployment notes: "Fixed bugs X, Y, Z"
# - Metrics dashboard: "Everything running well"
# - Rollback status: "Go/NoGo decision made"
```

---

## ⏮️ ROLLBACK PROCEDURE

**If production has critical issues, rollback IMMEDIATELY.**

### Emergency Rollback
```bash
# Option 1: Render Dashboard (Fastest)
# 1. Go to https://dashboard.render.com
# 2. Select "voxquery-backend-prod"
# 3. Go to "Deployments" tab
# 4. Find previous successful deployment
# 5. Click three dots (...)
# 6. Click "Redeploy"
# 7. Confirm
# Takes ~5 minutes

# Option 2: Via Git (If Render dashboard unavailable)
git revert HEAD
git push origin main
# Render auto-redeploys
# Takes 5-10 minutes
```

### Post-Rollback Steps
```bash
# 1. Verify rollback successful
curl https://api.voxquery.com/api/v1/health

# 2. Notify team immediately
# Message: "Rolled back from v16.0.1 to v16.0.0 due to [issue]"
# Include: error logs, affected users, timeline

# 3. Investigate root cause
# - Review error logs
# - Check what changed
# - Fix the bug

# 4. RETEST before redeploying
pytest tests/test_production_validation.py -v

# 5. Create new release candidate
# - Tag: v16.0.2
# - Deploy to staging first
# - Monitor staging 60+ minutes
# - Then deploy to production again
```

### Rollback Checklist
- [ ] Acknowledged critical issue
- [ ] Initiated rollback
- [ ] Verified rollback successful
- [ ] Notified stakeholders
- [ ] Documented root cause
- [ ] Created fix
- [ ] Tested fix
- [ ] Scheduled re-deployment

---

## 📊 POST-DEPLOYMENT VERIFICATION

### First Hour Checks
```bash
# Every 5 minutes for first hour
curl https://api.voxquery.com/api/v1/metrics/summary

# Metrics to verify:
✅ total_queries: increasing normally
✅ error_rate: < 1%
✅ avg_latency_ms: < 2000ms
✅ cache_hit_rate: > 50%
✅ no_timeout_errors: 0

# Any of these alerts?
❌ error_rate > 5%
❌ latency > 5000ms
❌ cache_hit<20%
❌ database_errors or timeouts

# If alerts: ROLLBACK_IMMEDIATELY
```

### 24-Hour Checks
- [ ] Error rate stayed < 1%
- [ ] No cascade failures
- [ ] Performance stable
- [ ] All features working
- [ ] Users reporting no issues
- [ ] Cost metrics normal

### 1-Week Check
- [ ] No regressions found
- [ ] Performance metrics stable
- [ ] User feedback positive
- [ ] No data integrity issues
- [ ] Backups working
- [ ] Team confident in release

---

## 🔄 DEPLOYMENT PATTERNS

### Zero-Downtime Deployment (Blue-Green)

**How it works with Render:**
```
1. Staging service = "Green" (old code)
2. Production service = "Blue" (running)
3. Deploy new code to staging first
4. Test staging fully
5. When ready, promote staging → production
6. If issue: revert to previous production
```

### Canary Deployment (Gradual Rollout)

**Not built-in with Render, but achievable:**
```
1. Feature flags in code: if flag enabled
2. Deploy to production
3. Enable for 10% of traffic
4. Monitor metrics
5. Increase to 50%, then 100%
6. If issues at any step: disable flag

Example feature flag:
if settings.ENABLE_NEW_QUERY_ENGINE:
    use new_engine()
else:
    use old_engine()
```

---

## 📝 DEPLOYMENT LOG

**Keep a record of all deployments:**

```
Date: 2026-04-02
Time: 14:30 UTC
Version: v16.0.1
Status: ✅ Successful
Duration: 8 minutes
Deployed by: @dev-team
Metrics Before: latency=245ms, error_rate=0.5%, cache_hit=65%
Metrics After: latency=235ms, error_rate=0.3%, cache_hit=68%
Issues: None observed
Rollback needed: No
Notes: Smooth deployment, all tests passed
```

---

## 🎓 DEPLOYMENT BEST PRACTICES

1. **Always stage first** - Never deploy directly to production
2. **Test before deploying** - Run full test suite
3. **Monitor actively** - Watch metrics for 60+ minutes
4. **Have rollback ready** - Know how to revert instantly
5. **Communicate changes** - Notify team and users
6. **Document decisions** - Keep deployment log
7. **Review code first** - Ensure changes are reviewed
8. **Backup before deploys** - Especially database
9. **Deploy during low-traffic** - Easier to monitor
10. **Have on-call ready** - Team available during deploy

---

## 🚨 COMMON ISSUES & FIXES

### Issue: Build Fails
```
❌ Error: "Module not found: backend.voxcore"

Fix:
1. Check requirements.txt is correct
2. Verify build command: pip install -r requirements.txt
3. Check imports in code are correct
4. Test locally: python -m pytest tests/
```

### Issue: Startup Fails
```
❌ Error: "ModuleNotFoundError" or "CRITICAL ERROR"

Fix:
1. Check environment variables in dashboard
2. Verify DATABASE_URL and REDIS_URL are set
3. Check secrets are not empty
4. Review recent code changes
5. Run locally to reproduce: python -m backend.voxcore.main
```

### Issue: Health Check Fails
```
❌ Error: "Health check failed"

Fix:
1. Check health endpoint works locally
2. Verify database connection
3. Verify Redis connection
4. Check port 8000 is being used
5. Increase health check timeout (if needed)
```

### Issue: Latency Spike
```
❌ Error: "avg_latency_ms > 5000"

Fix:
1. Check database connections: SELECT COUNT(*) FROM pg_stat_activity
2. Check Redis memory: info memory
3. Scale up instances: increase min_instances
4. Enable query logging: LOG_LEVEL=DEBUG
5. Check for N+1 queries or missing indexes
```

### Issue: Error Rate High
```
❌ Error: "error_rate > 5%"

Fix:
1. Check error logs: render logs [service] --follow
2. Identify error pattern
3. Check if database is reachable
4. Check if Redis is reachable
5. Verify all secrets are set
6. Consider rollback if critical
```

---

## ✅ DEPLOYMENT CHECKLIST

Before deploying to production:

Pre-Deploy:
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] No secrets in code
- [ ] Database backed up
- [ ] Staging stable (60+ minutes)
- [ ] Runbook prepared
- [ ] Team notified
- [ ] On-call ready

Deploy Steps:
- [ ] Tagged release in git
- [ ] Initiated render deployment
- [ ] Monitoring deployment logs
- [ ] Verified health endpoint
- [ ] Ran smoke tests
- [ ] Checked metrics

Post-Deploy:
- [ ] First hour monitoring complete
- [ ] Error rate normal
- [ ] Performance acceptable
- [ ] No user complaints
- [ ] Logs show normal operation
- [ ] Documented deployment

---

**🎉 Deployment complete! Monitor for 24 hours and celebrate! 🚀**

