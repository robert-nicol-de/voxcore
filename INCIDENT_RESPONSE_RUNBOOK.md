# 🚨 VOXCORE INCIDENT RESPONSE RUNBOOK

**Use this guide during production incidents to respond quickly and effectively.**

---

## 📞 INCIDENT ESCALATION

### On-Call Contact Chain
```
Severity 1 (Down):
1. Page on-call (PagerDuty or Slack)
2. Notify engineering lead
3. Notify CTO
4. Start war room (Zoom link ready)

Severity 2 (Degraded):
1. Slack engineering channel
2. Alert assigned team member
3. Start investigation

Severity 3 (Minor):
1. Log in issue tracker
2. Review in next standup
```

---

## 🔴 SEVERITY LEVELS

| Level | Impact | Response Time | Example |
|-------|--------|----------------|---------|
| **CRITICAL (1)** | Entire system down | < 5 min | API returning 500 for all queries |
| **HIGH (2)** | Major feature broken | < 15 min | Queries timing out, rate limiting not working |
| **MEDIUM (3)** | Partial feature broken | < 1 hour | One organization's data not accessible |
| **LOW (4)** | Minor issue | < 24 hours | Metrics endpoint slow |

---

## 🚨 INCIDENT: API RETURNS 500 FOR ALL QUERIES

**Severity: CRITICAL**

### 1. Immediate Triage (2 minutes)
```bash
# Check if it's actually down
curl https://api.voxquery.com/api/v1/health
# If returns error: API is down ✓

# Check status page
# goto https://status.voxquery.com (if you have one)

# Get latest error logs
render logs voxquery-backend-prod --follow --lines=50

# Check Render dashboard
# goto https://dashboard.render.com
# Select voxquery-backend-prod
# Check status indicator (should be red/failed)
```

### 2. Initial Response (Immediate)
```
1. [ ] Acknowledge incident in Slack
2. [ ] Start war room (Zoom)
3. [ ] Invite: on-call eng, lead, ops
4. [ ] Assign incident commander
5. [ ] Start timeline log
```

### 3. Diagnosis (3-5 minutes)

**Check Error Logs:**
```bash
render logs voxquery-backend-prod --follow --lines=100

# Look for:
- "DatabaseConnectionError" → Database is down
- "RedisConnectionError" → Redis is down
- "FATAL ERROR" → Code bug
- "Out of memory" → Memory leak
- "Connection timeout" → Network issue
```

**Check Render Status:**
```
Dashboard → voxquery-backend-prod → Status tab
- Status: Live? or Crashed?
- Health checks: Passing? or Failing?
- CPU: Normal? or maxed?
- Memory: Normal? or growing?
```

**Check Database:**
```bash
# Connect directly (from bastion host)
psql $PRODUCTION_DATABASE_URL -c "SELECT version();"

# If error: Database is down
# If success: Database is responsive

# Check active connections
psql $PRODUCTION_DATABASE_URL -c "SELECT COUNT(*) FROM pg_stat_activity;"
# If > 50: Connection pool exhausted
```

**Check Redis:**
```bash
# Connect directly
redis-cli -u $PRODUCTION_REDIS_URL ping

# If error: Redis is down
# If 'PONG': Redis is responsive

# Check memory
redis-cli -u $PRODUCTION_REDIS_URL info memory
# Look for: used_memory, maxmemory
# If used_memory > 0.9 * maxmemory: evicting data
```

### 4. Common Causes & Fixes

**Cause: Database Connection Pool Exhausted**
```
Symptom: "Too many connections" errors
Fix:
1. Increase pool_size in Render env: DB_POOL_SIZE=20 (was 10)
2. Identify queries holding connections
   SELECT pid, usename, state, query 
   FROM pg_stat_activity 
   WHERE query != 'idle';
3. Kill long-running queries
   SELECT pg_terminate_backend(pid) 
   FROM pg_stat_activity 
   WHERE duration > '5 minutes';
4. Restart API service
   render restart voxquery-backend-prod
```

**Cause: Redis Out of Memory**
```
Symptom: Redis evicting keys, cache misses spike
Fix:
1. Check memory: redis-cli info memory
2. If > 90% full: increase maxmemory
   render env set REDIS_MAXMEMORY=512mb
3. Or reduce TTL
   REDIS_TTL_SECONDS=300 (was 3600)
4. Monitor memory drop
```

**Cause: Code Bug (Recent Deploy)**
```
Symptom: "AttributeError" or "TypeError" in logs
Fix:
1. Identify the error
   grep -i "error" last_logs.txt | head
2. Check what changed
   git log --oneline -5
3. ROLLBACK IMMEDIATELY
   render redeploy (select previous build)
4. Investigate bug locally
   git checkout [commit]
   pytest tests/test_production_validation.py -v
```

**Cause: Database Corruption**
```
Symptom: "CORRUPTION" in logs or query returns wrong data
Fix:
1. Stop writes: ALTER DATABASE voxquery SET default_transaction_read_only=on;
2. Take backup: pg_dump > backup_corrupted.sql
3. Restore from last good backup
4. Verify data integrity
5. Investigate cause
6. Notify affected users
```

### 5. Resolution (Varies)

**If Database Down:**
- Contact Render support if hosted by Render
- Restore from backup if corruption
- Typically < 10 minutes to restore

**If Redis Down:**
- Render Redis has automatic failover
- If manual Redis: restart with: SERVICE restart redis

**If Code Bug:**
- Rollback to previous version
- Fix bug
- Test thoroughly
- Redeploy

**If Network Issue:**
- Check Render infrastructure status
- May require patience (2-30 minutes)

### 6. Post-Incident (After Resolved)

```bash
# Verify service is responsive
for i in {1..10}; do
  curl https://api.voxquery.com/api/v1/health
  if [ $? -eq 0 ]; then
    echo "✅ API healthy"
  else
    echo "❌ API still failing"
  fi
  sleep 5
done

# Run smoke tests
pytest tests/test_production_validation.py -v

# Check metrics returned to normal
curl https://api.voxquery.com/api/v1/metrics/summary | jq .
```

---

## ⚠️ INCIDENT: LATENCY SPIKE (>5 seconds)

**Severity: HIGH**

### Diagnosis (5 minutes)

```bash
# Check current metrics
curl https://api.voxquery.com/api/v1/metrics/summary | jq '.avg_latency_ms, .p99_latency_ms'

# Check what changed recently
git log --oneline -10

# Monitor real-time metrics
watch -n 5 'curl -s https://api.voxquery.com/api/v1/metrics/summary | jq .avg_latency_ms'
```

### Common Causes

**Cause 1: Slow Database Queries**
```sql
-- Find slow queries
SELECT query, calls, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;

-- Check missing indexes
SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;

-- Add missing index if needed
CREATE INDEX idx_users_org_id ON users(org_id);
```

**Cause 2: Memory Pressure (Swap)**
```bash
# Check memory on Render
render dashboard → voxquery-backend-prod → Metrics

# If memory > 90%:
# Option 1: Scale up instance (more CPU/RAM)
# Option 2: Enable query caching (already enabled)
# Option 3: Reduce log verbosity
```

**Cause 3: Network Latency**
```bash
# Check DNS resolution
time nslookup api.voxquery.com

# Check API response time vs network time
time curl https://api.voxquery.com/api/v1/health

# If network > 100ms: might be geography or ISP issue
```

### Fix

**Immediate (Temporary):**
```bash
# Scale up resources
render dashboard → voxquery-backend-prod → Environment
Min instances: 2 (was 1)
Max instances: 8 (was 5)

# or restart to clear memory
render restart voxquery-backend-prod
```

**Permanent (After Investigation):**
- Add database index
- Optimize slow query
- Increase cache TTL
- Scale instance size

---

## 🚫 INCIDENT: HIGH ERROR RATE (>5%)

**Severity: HIGH**

### Diagnosis

```bash
# See error breakdown
curl https://api.voxquery.com/api/v1/metrics/errors | jq '.errors_by_type'

# Sample output:
{
  "database_error": 150,
  "timeout_error": 45,
  "validation_error": 12,
  "rate_limit_error": 3
}

# Get latest error logs
render logs voxquery-backend-prod --lines=200 | grep -i "error\|exception"
```

### By Error Type

**Cause: Database Errors**
```bash
# Check database health
psql $PRODUCTION_DATABASE_URL -c "SELECT version();"

# If unresponsive: database is down
# Solution: Restore from backup or failover

# If responsive but slow:
SELECT query, calls, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 1;

# Kill long-running query
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE duration > '10 minutes';
```

**Cause: Timeout Errors**
```
Usually means:
1. Database is slow
2. External API (Groq) is slow
3. Timeout value too short

Check:
1. Database performance (see above)
2. Groq API status: https://groq.com/status
3. Increase timeout: MAX_EXECUTION_TIME_SECONDS=60 (was 30)
```

**Cause: Validation Errors**
```
Usually means:
1. Clients sending bad requests
2. Validation logic broke (code bug)

Check:
1. Recent code changes: git log -p -1
2. Sample errors in logs
3. If code bug: rollback

This is usually LOW severity
```

**Cause: Rate Limit Errors**
```
If legitimate users are getting rate limited:
1. Check traffic spike
2. Increase rate limits: RATE_LIMIT_PER_MINUTE=200
3. Or scale up instances

If suspicious (DDoS):
1. Contact Render support
2. Enable WAF (Web Application Firewall)
3. Block malicious IPs
```

---

## 💾 INCIDENT: DATA LOSS OR CORRUPTION

**Severity: CRITICAL**

### Immediate Actions (< 1 minute)

```
1. STOP writes to database immediately
2. Take snapshot/backup
3. Notify legal/compliance
4. Start incident war room
5. Preserve evidence (logs, state)
```

### Technical Response

```bash
# Put database in read-only mode
psql $PRODUCTION_DATABASE_URL -c "ALTER DATABASE voxquery SET default_transaction_read_only=on;"

# Verify no writes are happening
psql $PRODUCTION_DATABASE_URL -c "SELECT SUM(n_tup_del) FROM pg_stat_user_tables;"

# Identify what was deleted/corrupted
SELECT * FROM pg_stat_statements WHERE query LIKE '%DELETE%' OR query LIKE '%UPDATE%' ORDER BY calls DESC LIMIT 5;

# Check backup integrity
pg_restore --validate backup_latest.sql
```

### Recovery

```bash
# 1. Restore from last good backup
render restart restore-from-backup voxquery-prod

# 2. Or manually
pg_dump voxquery_backup > /tmp/restore.sql
psql $PRODUCTION_DATABASE_URL < /tmp/restore.sql

# 3. Verify data
SELECT COUNT(*) FROM users; -- Should match old value
SELECT MAX(updated_at) FROM audit_logs; -- Should be recent

# 4. Identify gap
# "Which records were lost between [time] and [now]?"

# 5. Notify affected users
# "We restored your data to [timestamp]"
# "These queries since [time] will need to be re-run"
```

### Post-Incident

- [ ] Root cause analysis (why did corruption happen?)
- [ ] Implement safeguards (checksums, constraints)
- [ ] Increase backup frequency
- [ ] Add corruption detection queries to monitoring

---

## 🔒 INCIDENT: SUSPECTED SECURITY BREACH

**Severity: CRITICAL**

### Immediate Actions (< 5 minutes)

```
1. [ ] Do NOT panic or blame
2. [ ] Activate security incident team
3. [ ] Preserve all logs (do not delete)
4. [ ] Take full database backup
5. [ ] Note exact time of discovery
6. [ ] Notify CTO + Security lead
```

### Investigation (30 minutes)

```bash
# 1. Check for unauthorized access
psql $PRODUCTION_DATABASE_URL -c "SELECT * FROM pg_stat_activity WHERE usename NOT IN ('admin', 'readonly');"

# 2. Check for unusual queries
render logs voxquery-backend-prod --since "60m ago" | grep -i "drop\|delete\|grant\|select.*from.*shadow"

# 3. Check audit logs
SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 50;

# 4. Check for API token abuse
SELECT user_id, COUNT(*) as request_count 
FROM api_audit_log 
WHERE created_at > NOW() - INTERVAL '1 hour' 
GROUP BY user_id 
HAVING COUNT(*) > 1000
ORDER BY request_count DESC;

# 5. Check Redis for stolen tokens
redis-cli -u $PRODUCTION_REDIS_URL KEYS "session:*" | head -20
```

### Response

**If Token Leaked:**
```bash
# Invalidate all sessions
redis-cli -u $PRODUCTION_REDIS_URL FLUSHALL  # ⚠️ Drastic but effective

# Force re-authentication
UPDATE user_sessions SET expires_at = NOW();

# Notify users to change passwords
```

**If Data Accessed:**
```
1. Identify which data was accessed
2. Notify affected users
3. Legal review required
4. Follow GDPR/privacy laws
5. Public disclosure if required
```

**If Data Modified/Deleted:**
```
1. Restore from backup (see data corruption section)
2. Full forensic analysis
3. Law enforcement notification (maybe)
4. Increase security measures
```

### Prevention Going Forward

- [ ] Rotate all secrets (keys, tokens, passwords)
- [ ] Enable MFA for all admins
- [ ] Restrict database access (IP allowlist)
- [ ] Enable query logging
- [ ] Implement intrusion detection
- [ ] Schedule security audit

---

## 📋 INCIDENT COMMANDER CHECKLIST

**When you become incident commander:**

```
Initial (0-5 min):
- [ ] Gather team in war room (Zoom)
- [ ] Get situation report from discoverer
- [ ] Assess severity (Critical/High/Medium/Low)
- [ ] Identify and delegate:
    - Investigation lead (technical diagnosis)
    - Mitigation lead (fix the issue)
    - Communications lead (notify stakeholders)
    - Timeline recorder (document everything)

Diagnosis (5-15 min):
- [ ] Receive initial findings
- [ ] Ask clarifying questions
- [ ] Decide on immediate action (mitigate vs fix)

Action (15-60 min):
- [ ] Mitigation lead executes fix
- [ ] Monitor for success/failure
- [ ] Adjust plan if needed
- [ ] Communications lead updates status

Resolution (60+ min):
- [ ] Confirm issue resolved
- [ ] Verify normalcy
- [ ] Document root cause
- [ ] Schedule post-mortem

Post-Incident (24-48 hours):
- [ ] Conduct thorough post-mortem
- [ ] Document learnings
- [ ] Assign action items
- [ ] Update runbooks
```

---

## 📊 POST-INCIDENT REVIEW

**After EVERY incident (24 hours later):**

### What Happened?
```
- [ ] Timeline of events
- [ ] What symptoms appeared
- [ ] How long until resolution
- [ ] Impact (users affected, data lost, etc)
```

### Why Did It Happen?
```
- [ ] Root cause: single point of failure?
- [ ] Contributing factors
- [ ] Was it preventable?
```

### What Did We Learn?
```
- [ ] Process improvements
- [ ] Monitoring improvements
- [ ] Testing improvements
- [ ] Documentation improvements
```

### What Will We Do Different?
```
- [ ] Action item 1: [What] [Who] [When]
- [ ] Action item 2: [What] [Who] [When]
- [ ] Action item 3: [What] [Who] [When]
```

### Example Post-Mortem
```
Timeline:
- 14:32: User reports "API down" in Slack
- 14:33: On-call engineer investigating
- 14:35: Identified database connection pool exhausted
- 14:40: Increased pool size from 10 to 20
- 14:42: Service recovered
- Duration: 10 minutes

Root Cause:
- Load spike caused by new customer onboarding
- Connection pool was too small
- No alerting on pool usage

Prevention:
1. Alert when pool usage > 70% (add to monitoring)
2. Auto-scale pool size (implement in code)
3. Load testing before customer onboarding (process)
4. Increase default pool size from 10 to 15 (config)
```

---

## 🛠️ TOOLS & COMMANDS

### Quick Commands

```bash
# Render logs (live)
render logs voxquery-backend-prod --follow

# Render logs (last hour)
render logs voxquery-backend-prod --since="60m ago"

# Restart service
render restart voxquery-backend-prod

# Scale up
render env set MIN_INSTANCES=2

# Database health
psql $PRODUCTION_DATABASE_URL -c "SELECT version(), current_database();"

# Redis health
redis-cli -u $PRODUCTION_REDIS_URL PING

# API health
curl https://api.voxquery.com/api/v1/health

# Metrics
curl https://api.voxquery.com/api/v1/metrics/summary | jq .
```

### Emergency Contacts

```
On-Call (Primary): [Name] [Phone] [Email]
On-Call (Secondary): [Name] [Phone] [Email]
Engineering Lead: [Name] [Phone] [Email]
CTO: [Name] [Phone] [Email]
Database Admin: [Name] [Phone] [Email]
Security Lead: [Name] [Phone] [Email]
```

---

**Remember: Stay calm, communicate clearly, and document everything. 🚀**

