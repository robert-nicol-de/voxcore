# 🔥 VOXCORE PRODUCTION PRE-FLIGHT CHECKLIST

**Use this checklist 48 hours before production launch.**

---

## ✅ SECTION 1: ENVIRONMENT SEPARATION (Mandatory)

- [ ] `.env.dev` exists with SQLite config
- [ ] `.env.staging` exists with PostgreSQL config
- [ ] `.env.prod.template` exists (not committed to repo)
- [ ] Staging database is SEPARATE from production
- [ ] Staging Redis is SEPARATE from production
- [ ] Production variables are ONLY in Render dashboard (not in files)
- [ ] No `.env.prod` file in repository (would leak secrets!)
- [ ] `.env.*` files are in `.gitignore`

**Verification:**
```bash
# Should show no env files
git ls-files | grep -E "\.env\.(prod|staging)" && echo "FAIL" || echo "PASS"

# Should show .env.dev and .env.staging (dev only)
ls -la .env.* | grep -E "\.env\.(dev|staging)"
```

---

## ✅ SECTION 2: DATABASE (PostgreSQL - PRODUCTION ONLY)

### Local (Development)
- [ ] SQLite file exists at `voxquery.db`
- [ ] Can connect: `sqlite3 voxquery.db "SELECT 1;"`

### Staging
- [ ] PostgreSQL database provisioned in Render
- [ ] Connection pool configured (size=10, overflow=20)
- [ ] Database name: `voxquery_staging`
- [ ] User: `voxquery_user` (limited permissions)
- [ ] SSL required for connections
- [ ] Can connect: `psql $STAGING_DATABASE_URL`

### Production
- [ ] PostgreSQL database provisioned in Render
- [ ] Connection pool configured (size=10, overflow=20)
- [ ] Database name: `voxquery_prod`
- [ ] Two users created:
  - [ ] `voxquery_admin` (full access)
  - [ ] `voxquery_readonly` (SELECT only)
- [ ] SSL required
- [ ] Daily backups enabled (7+ day retention)
- [ ] Backup tested (verify restore works)

**Test Database Backup:**
```bash
# Take manual backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > backup.sql

# Verify it's not empty
wc -l backup.sql  # Should be thousands of lines

# Test restore to staging
psql $STAGING_DATABASE_URL < backup.sql
```

---

## ✅ SECTION 3: REDIS CACHE

### Local (Development)
- [ ] Redis running on localhost:6379
- [ ] Can connect: `redis-cli ping` → returns "PONG"

### Staging
- [ ] Render Redis provisioned
- [ ] AUTH enabled (password set)
- [ ] TLS enabled
- [ ] Memory: 256MB
- [ ] Eviction: allkeys-lru
- [ ] Can connect: `redis-cli -u $STAGING_REDIS_URL ping`

### Production
- [ ] Upstash Redis OR Render Redis provisioned
- [ ] AUTH enabled (strong password)
- [ ] TLS enforced
- [ ] Memory: 256MB
- [ ] Eviction: allkeys-lru
- [ ] No dangerous commands enabled (FLUSHALL, FLUSHDB, KEYS)
- [ ] Can connect and ping

**Test Redis Connection:**
```bash
# Staging
redis-cli -u $STAGING_REDIS_URL ping

# Production (in deploy process only)
redis-cli -u $PROD_REDIS_URL ping
```

---

## ✅ SECTION 4: SECRETS MANAGEMENT

### What Must Be Secret
- [ ] `SECRET_KEY` (32+ chars, random)
- [ ] `JWT_SECRET_KEY` (32+ chars, random)
- [ ] Database password
- [ ] Redis password
- [ ] Groq API key
- [ ] Any third-party API keys

### Storage Location
- [ ] STAGING secrets in Render dashboard (Settings → Environment)
- [ ] PRODUCTION secrets in Render dashboard (Settings → Environment)
- [ ] NEVER in `.env.prod` file
- [ ] NEVER committed to GitHub
- [ ] NEVER in logs

**Generate Secure Secrets:**
```bash
# Generate strong random secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy to Render dashboard:
# 1. Go to Render service
# 2. Settings → Environment
# 3. Add variable
# 4. Paste secret value
# 5. Save
```

### Staging Secrets Setup
- [ ] `DATABASE_URL` from Render Postgres
- [ ] `REDIS_URL` from Render Redis
- [ ] `SECRET_KEY` generated (save in Render)
- [ ] `JWT_SECRET_KEY` generated (save in Render)
- [ ] `GROQ_API_KEY` from https://console.groq.com

### Production Secrets Setup
- [ ] `DATABASE_URL` from Render Postgres (different from staging!)
- [ ] `REDIS_URL` from Upstash/Render Redis (different from staging!)
- [ ] `SECRET_KEY` generated (NEW, not reused)
- [ ] `JWT_SECRET_KEY` generated (NEW, not reused)
- [ ] `GROQ_API_KEY` from Groq console (production key)

**Verification:**
```bash
# Verify no secrets in code
grep -r "sk_prod\|password=\|GROQ_API_KEY" . \
  --exclude-dir=.git \
  --exclude-dir=node_modules \
  --exclude-dir=.venv && echo "FAIL: Secrets in code!" || echo "PASS"

# Verify env files not staged
git status | grep -E "\.env\.(prod|staging)" && echo "FAIL" || echo "PASS"
```

---

## ✅ SECTION 5: API SECURITY

### Authentication
- [ ] JWT middleware implemented
- [ ] Tokens expire after 24 hours
- [ ] HTTPS required for all endpoints
- [ ] Tokens verified on every request

**Test:**
```bash
# Try to call API without token
curl -X POST http://localhost:8000/api/v1/query

# Should get 401 Unauthorized (or similar)
```

### Rate Limiting
- [ ] Rate limiter implemented (slowapi or similar)
- [ ] 100 requests/minute per user
- [ ] 5000 requests/hour per user
- [ ] Returns 429 when limit exceeded
- [ ] Tracking per user_id (not IP)

**Test:**
```bash
# Send 101 requests rapidly
for i in {1..101}; do
  curl -X POST http://localhost:8000/api/v1/query \
    -H "Authorization: Bearer $TOKEN"
done

# Request 101 should get 429 Too Many Requests
```

### Request Validation
- [ ] Max request size: 10MB (enforced)
- [ ] Max rows returned: 10,000 (enforced)
- [ ] Max execution time: 30 seconds (enforced)
- [ ] All inputs validated (no SQL injection)

---

## ✅ SECTION 6: GOVERNANCE VALIDATION (RUN THESE TESTS!)

**CRITICAL: Run all 4 tests before production launch**

### Test 1: Destructive SQL Blocked
```bash
# Should be BLOCKED, not executed

curl -X POST https://api.voxquery.com/api/v1/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "DROP TABLE users",
    "org_id": "org-test",
    "user_id": "user-test",
    "user_role": "analyst"
  }'

# Expected response: status=BLOCKED, error="not allowed"
```

- [ ] Query is blocked
- [ ] Error message is present
- [ ] No data returned

### Test 2: Cross-Tenant Access Blocked
```bash
# User from org-123 tries to access org-999

curl -X POST https://api.voxquery.com/api/v1/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "SELECT * FROM users WHERE org_id = '\''org-999'\''",
    "org_id": "org-123",
    "user_id": "user-test",
    "user_role": "analyst"
  }'

# Expected: Only org-123 data returned (or empty if no match)
# metadata.tenant_enforced = true
```

- [ ] Only org-123 data returned
- [ ] metadata.org_id = "org-123"
- [ ] metadata.tenant_enforced = true

### Test 3: Sensitive Columns Masked
```bash
# Analyst tries to see salary (should be masked)

curl -X POST https://api.voxquery.com/api/v1/query \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "Show employee salary",
    "org_id": "org-123",
    "user_id": "analyst-user",
    "user_role": "analyst"
  }'

# Expected: salary field = "****" or in metadata.columns_masked
```

- [ ] Salary is masked ("****")
- [ ] metadata.columns_masked includes "salary"
- [ ] Other roles (executive) can see unmasked salary

### Test 4: High-Cost Query Blocked
```bash
# Very expensive query should be blocked

curl -X POST https://api.voxquery.com/api/v1/query \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "JOIN 10 tables and full scan 1B rows",
    "org_id": "org-123",
    "user_id": "user-test",
    "user_role": "analyst"
  }'

# Expected: blocked OR cost_score > 85
```

- [ ] Query is blocked or warns
- [ ] metadata.cost_score > 85 if not blocked
- [ ] No expensive query executes

---

## ✅ SECTION 7: PERFORMANCE VALIDATION

### Cache Performance
- [ ] Run same query twice
- [ ] Second query < 500ms (cache hit)
- [ ] metadata.cache_hit = true

**Test:**
```bash
# First query
curl -X POST https://api.voxquery.com/api/v1/query ... > response1.json

# Wait 1 second
sleep 1

# Second query (same)
curl -X POST https://api.voxquery.com/api/v1/query ... > response2.json

# Check latency
jq '.metadata.execution_time_ms' response2.json
# Should be < 500ms

# Check cache hit
jq '.metadata.cache_hit' response2.json
# Should be true
```

- [ ] Cache hit detected
- [ ] Latency < 500ms

### Latency Targets
- [ ] Cached queries: < 500ms
- [ ] Fresh queries: < 2000ms
- [ ] P99 latency: < 5000ms

**Test with Load:**
```bash
# Send 100 queries and measure latency
for i in {1..100}; do
  curl -X POST https://api.voxquery.com/api/v1/query ... &
done
wait

# Check metrics endpoint
curl https://api.voxquery.com/api/v1/metrics/summary
# Review: avg_latency_ms, p95_latency_ms, p99_latency_ms
```

- [ ] P50 latency reasonable
- [ ] P95 latency < 2000ms
- [ ] No timeouts

---

## ✅ SECTION 8: FAILURE HANDLING

### Database Down
- [ ] Render Redis still works
- [ ] Queries return error (not hang)
- [ ] System doesn't crash

**Test:**
```bash
# In Render, temporarily disable database
# Try to run query
curl -X POST https://api.voxquery.com/api/v1/query ...

# Should get: error response, status_code >= 400
# Should NOT get: 500+ after timeout (hang)
# Should NOT crash backend
```

- [ ] Error response returned
- [ ] No timeout/hang
- [ ] Backend stays running

### Redis Down
- [ ] Queries still work (without cache)
- [ ] Degraded performance (expected)
- [ ] No crash

**Test:**
```bash
# In Render, temporarily disable Redis
curl -X POST https://api.voxquery.com/api/v1/query ...

# Should work (slow), not crash
```

- [ ] Queries execute (slowly)
- [ ] Cache disabled (expected)
- [ ] No crash

### Request Timeout
- [ ] All requests complete within 10 seconds
- [ ] Long queries timeout gracefully
- [ ] No hanging requests

**Test:**
```bash
# Send very slow query
timeout 15 curl -X POST https://api.voxquery.com/api/v1/query ...

# Should return within 10s, not hang until timeout

# Or should return TIMEOUT status
```

- [ ] Complete within time limit
- [ ] Error status returned
- [ ] No request hangs forever

---

## ✅ SECTION 9: OBSERVABILITY & MONITORING

### Metrics Collection
- [ ] Latency being tracked
- [ ] Error rate being tracked
- [ ] Cache hit rate visible
- [ ] Cost score tracked

**Check:**
```bash
curl https://api.voxquery.com/api/v1/metrics/summary

# Should return JSON with:
# - total_queries
# - avg_latency_ms
# - error_rate
# - cache_hit_rate
# - avg_cost_score
```

- [ ] Metrics endpoint returns data
- [ ] All fields populated

### Logging
- [ ] Structured JSON logs
- [ ] request_id in every log
- [ ] user_id and org_id tracked
- [ ] Query execution logged
- [ ] Errors logged with context

**Check:**
```bash
# Watch logs in Render
# Should see structured JSON format:
# {"timestamp": "...", "request_id": "...", "user_id": "...", ...}

# NOT plain text logs or missing fields
```

- [ ] Logs are structured JSON
- [ ] request_id, user_id, org_id present
- [ ] Searchable and parseable

### Alerts Configured
- [ ] Alert: Latency p95 > 2000ms
- [ ] Alert: Error rate > 5%
- [ ] Alert: Cache hit rate < 50%
- [ ] Alert: Database connections max'd out
- [ ] Alert: Redis memory > 200MB

**Test:**
```bash
# Trigger alert (manually or via test load)
# Verify alert fires (check Slack, email, etc.)
```

- [ ] At least 1 alert configured
- [ ] Can receive alerts
- [ ] On-call team knows about alerts

---

## ✅ SECTION 10: COMPLIANCE & AUDIT

### Audit Logging
- [ ] Every query creates audit log entry
- [ ] audit_log_id in every response
- [ ] Audit logs immutable (can't be deleted)
- [ ] Retention: 90 days

**Verify:**
```bash
# Extract audit_log_id from response
curl -X POST https://api.voxquery.com/api/v1/query ... \
  | jq '.metadata.audit_log_id'

# Should be non-null UUID
# Audit logs stored somewhere (database, S3, etc.)
```

- [ ] audit_log_id created for queries
- [ ] Audit logs retained
- [ ] Can query audit log history

### Data Security
- [ ] PII encryption enabled
- [ ] Sensitive columns masked by default
- [ ] Data classification implemented
- [ ] Export compliance working

**Test:**
```bash
# Try to export sensitive data
curl https://api.voxquery.com/api/v1/compliance/export

# Should work, PII should be masked
# Should be audit-able (who exported what)
```

- [ ] Export available
- [ ] Compliant format
- [ ] Audit trail for exports

---

## ✅ SECTION 11: DEPLOYMENT CONFIGURATION

### Render Backend Configuration
- [ ] Plan: Standard (NOT free tier)
- [ ] Auto-deploy: enabled
- [ ] Min instances: 1
- [ ] Max instances: 3-5
- [ ] Health check: /api/v1/health
- [ ] Timeout: 30 seconds
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `uvicorn backend.voxcore.main:app --port 8000`

**Verify in Render Dashboard:**
```
Settings → Instance Type
Settings → Scaling
Settings → Health Checks
Settings → Build Command
Settings → Start Command
```

- [ ] All configured in Render
- [ ] Auto-scaling enabled

### Vercel Frontend Configuration
- [ ] Framework: Next.js (or React)
- [ ] Build: `npm run build`
- [ ] Output: `.next`
- [ ] Node version: 18 LTS
- [ ] Environment: REACT_APP_API_URL = https://api.voxquery.com

**Verify in Vercel Dashboard:**
```
Settings → General
Settings → Environment Variables
```

- [ ] Correct API URL configured
- [ ] HTTPS enforced
- [ ] Auto-deploy enabled

---

## ✅ SECTION 12: DOMAIN & HTTPS

### Custom Domain
- [ ] Domain registered
- [ ] Frontend domain: https://voxquery.com
- [ ] Backend domain: https://api.voxquery.com

**For Vercel:**
```
Settings → Domains → Add Domain
Points to Vercel nameservers
```

**For Render Backend:**
```
Settings → Custom Domain
Or use Render's default domain if preferred
```

- [ ] Frontend accessible via custom domain
- [ ] Backend accessible via custom domain

### HTTPS & Security Headers
- [ ] HTTPS enforced (HTTP → HTTPS redirect)
- [ ] HSTS enabled (max-age: 31536000)
- [ ] X-Frame-Options: DENY
- [ ] X-Content-Type-Options: nosniff
- [ ] Content-Security-Policy configured

**Test:**
```bash
# Check HTTPS enforced
curl -i http://voxquery.com
# Should redirect to https://

# Check security headers
curl -i https://voxquery.com
# Should see:
# Strict-Transport-Security: max-age=31536000
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
```

- [ ] HTTPS enforced
- [ ] Security headers present

---

## ✅ SECTION 13: BACKUP & RECOVERY

### Database Backups
- [ ] Render automatic backups enabled
- [ ] Retention: 7+ days
- [ ] Manual backup tested (successful restore)

**Test Backup & Restore:**
```bash
# Create manual backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > backup_$(date +%s).sql

# Verify backup size/content
wc -l backup_*.sql
# Should be thousands of lines

# Test restore to staging (verify it works)
psql $STAGING_DATABASE_URL < backup_*.sql

# Verify data integrity
psql $STAGING_DATABASE_URL -c "SELECT COUNT(*) FROM users;"
```

- [ ] Automated backups configured
- [ ] Manual backup successful
- [ ] Restore verified to work

### Code Backups
- [ ] GitHub repo is backup (version control)
- [ ] Protected main branch (require reviews)
- [ ] No force-push to main
- [ ] Tags for releases

**Verify:**
```bash
# Check GitHub branch rules
# Settings → Branches → Branch Protection Rules
# - Require pull request reviews
# - Dismiss stale reviews
```

- [ ] GitHub repo protected
- [ ] Can recover from any commit

---

## ✅ SECTION 14: SCALING & AUTO-SCALING

### Backend Scaling
- [ ] Min instances: 1
- [ ] Max instances: 5
- [ ] Scale up on: CPU > 70%
- [ ] Scale down on: CPU < 30%
- [ ] Health check passing
- [ ] No hanging requests (timeout < 10s)

**Monitor:**
```bash
# Check metrics
curl https://api.voxquery.com/api/v1/metrics/summary

# In Render dashboard, watch "Instances" panel
# Should see 1 instance normally
# Multiple instances under load
```

- [ ] Auto-scaling configured
- [ ] Can handle traffic spikes

### Queue Management
- [ ] Monitor queue depth
- [ ] Alert if queue > 1000
- [ ] Auto-scale on queue depth

---

## ✅ SECTION 15: COST CONTROLS

### Monthly Cost Limits
- [ ] Analyst: 5,000 cost units/month
- [ ] Finance: 10,000 cost units/month
- [ ] Executive: 50,000 cost units/month
- [ ] Enforcement at VoxCore level

**Verify:**
```bash
# In app, user should see:
# "Cost this month: 2,500 / 5,000 (analyst)"

# When limit reached:
# New queries return: "Cost quota exceeded"
```

- [ ] Cost tracking visible
- [ ] Enforcement working

### Execution Limits
- [ ] Max rows returned: 10,000
- [ ] Max execution time: 30 seconds
- [ ] Max request size: 10MB

**Test:**
```bash
# Try to return 100K rows
# Should get truncated to 10K

# Try query that takes 60 seconds
# Should timeout at 30s

# Try to upload 20MB file
# Should get 413 Request Entity Too Large
```

- [ ] Row limits enforced
- [ ] Time limits enforced
- [ ] Size limits enforced

---

## ✅ SECTION 16: FINAL GO/NO-GO DECISION

### ✅ GO LIVE IF:

- [ ] All tests passing ✅
- [ ] No security issues found ✅
- [ ] Monitoring operational ✅
- [ ] Alerts configured ✅
- [ ] Backup tested ✅
- [ ] Performance acceptable ✅
- [ ] Team trained ✅
- [ ] Runbook written ✅
- [ ] On-call schedule ready ✅
- [ ] No critical bugs ✅

### ❌ DO NOT LAUNCH IF:

- [ ] Any data leak risk
- [ ] Tests failing
- [ ] Monitoring not working
- [ ] No rate limiting
- [ ] Secrets in code
- [ ] Database not PostgreSQL
- [ ] Backup not tested
- [ ] Governance tests failing
- [ ] Performance > 5 seconds
- [ ] Team not trained

---

## 📋 FINAL DECISION

**Date:** _______________  
**Reviewer:** _______________  
**Status:** ☐ GO ☐ NO-GO

**Notes:**
```
_________________________________________
_________________________________________
_________________________________________
```

**Sign-off:**
- [ ] CTO approved
- [ ] DevOps approved
- [ ] Security approved
- [ ] Product lead approved

---

**Once all sections complete and signed off: DEPLOY TO PRODUCTION! 🚀**

