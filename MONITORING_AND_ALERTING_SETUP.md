# 📊 VOXCORE MONITORING & ALERTING SETUP GUIDE

**Use this guide to set up monitoring, metrics collection, and alerts for production.**

---

## 🎯 MONITORING STRATEGY

**Goal:** Detect and alert on issues before users notice them.

**Metrics to Monitor:**
1. Uptime (API availability)
2. Latency (response time)
3. Error rate (failed requests)
4. Throughput (requests per minute)
5. Database health
6. Redis health
7. Cost (execution cost of queries)

---

## 🔷 INTEGRATIONS SETUP

### 1. Render Built-in Monitoring

**What it provides:**
- Uptime monitoring
- Health check status
- CPU/Memory usage
- Response time

**Set up:**
```
1. Go to https://dashboard.render.com
2. Select voxquery-backend-prod
3. Click "Environment" → "Health Checks"
4. Configure:
   - Path: /api/v1/health
   - Interval: 30 seconds
   - Timeout: 5 seconds
   - Initial delay: 30 seconds
5. Save
```

### 2. Datadog Integration (Recommended)

**Why Datadog:**
- Real-time metrics and logs
- Custom dashboards
- Alert routing
- SLA tracking
- Cost analysis

**Setup:**
```
1. Create Datadog account: https://www.datadoghq.com/
2. Get API key from Datadog dashboard
3. Install Datadog agent in Render:
   render env set DATADOG_API_KEY=[your-key]
   render env set DD_TRACE_ENABLED=true
4. Add to Python app:
   pip install ddtrace
5. Initialize in main.py:
   from ddtrace import patch_all
   patch_all()
```

### 3. Sentry Integration (Error Tracking)

**Why Sentry:**
- Automatic error tracking
- Release tracking
- Session replay (PRO)
- Performance monitoring
- Alert on new errors

**Setup:**
```
1. Create Sentry account: https://sentry.io/
2. Create project for VoxCore
3. Get DSN (looks like https://abc123@sentry.io/project-id)
4. Install in Render:
   pip install sentry-sdk
5. Add to main.py:
   import sentry_sdk
   sentry_sdk.init(
       dsn="https://key@sentry.io/project",
       traces_sample_rate=0.1
   )
6. Test:
   curl https://api.voxquery.com/api/v1/debug/error
   # Should appear in Sentry within 30 seconds
```

### 4. PagerDuty Integration (Alert Routing)

**Why PagerDuty:**
- Notifies on-call engineer
- Escalation policies
- Incident tracking
- SLA enforcement

**Setup:**
```
1. Create PagerDuty account: https://pagerduty.com/
2. Create "VoxCore Production" service
3. Set up on-call schedule
4. Get integration key
5. Connect to Datadog/Sentry:
   Datadog → Integrations → PagerDuty
   Enter integration key
6. Test alert:
   curl https://api.voxquery.com/api/v1/debug/alert
```

---

## 📈 METRICS COLLECTION

### What to Collect

**Application Metrics:**
```python
# In your API endpoint
class MetricsCollector:
    def __init__(self):
        self.total_queries = 0
        self.total_errors = 0
        self.total_cached = 0
        self.total_latency_ms = 0
    
    def record_query(self, latency, size, cached, error):
        self.total_queries += 1
        self.total_latency_ms += latency
        if cached:
            self.total_cached += 1
        if error:
            self.total_errors += 1
    
    def get_metrics(self):
        return {
            "total_queries": self.total_queries,
            "error_rate": self.total_errors / self.total_queries,
            "avg_latency_ms": self.total_latency_ms / self.total_queries,
            "cache_hit_rate": self.total_cached / self.total_queries,
        }
```

**Infrastructure Metrics:**
```
- CPU usage (target: < 70%)
- Memory usage (target: < 80%)
- Disk usage (target: < 85%)
- Network I/O (look for spikes)
- Connection count (database and Redis)
```

**Business Metrics:**
```
- Active organizations
- Active users
- Queries per minute
- Cost per query
- Revenue impact (cost * price)
```

### Expose Metrics Endpoint

**In main.py:**
```python
from fastapi import FastAPI

app = FastAPI()

# Global metrics
metrics = {
    "total_queries": 0,
    "total_errors": 0,
    "total_latency_ms": 0,
    "total_cached": 0,
}

@app.get("/api/v1/metrics/summary")
async def get_metrics_summary():
    """Return current metrics for monitoring"""
    q = metrics["total_queries"]
    e = metrics["total_errors"]
    return {
        "total_queries": q,
        "error_rate": (e / q) if q > 0 else 0,
        "avg_latency_ms": int(metrics["total_latency_ms"] / q) if q > 0 else 0,
        "cache_hit_rate": (metrics["total_cached"] / q) if q > 0 else 0,
        "timestamp": datetime.utcnow().isoformat(),
    }

@app.get("/api/v1/metrics/detailed")
async def get_metrics_detailed():
    """Detailed metrics for dashboards"""
    return {
        "performance": {
            "p50_latency_ms": 150,
            "p99_latency_ms": 900,
            "p999_latency_ms": 1500,
        },
        "reliability": {
            "uptime_percent": 99.99,
            "error_rate": 0.01,
            "timeout_rate": 0.001,
        },
        "resource": {
            "cpu_percent": 35,
            "memory_percent": 45,
            "active_connections": 15,
        },
        "business": {
            "active_orgs": 42,
            "active_users": 127,
            "queries_per_minute": 245,
        },
    }
```

---

## 🚨 ALERTS TO CONFIGURE

### Critical Alerts (Page on-call immediately)

| Metric | Threshold | Action |
|--------|-----------|--------|
| Uptime | < 99% | Page on-call |
| Error rate | > 5% | Page on-call |
| API latency (p99) | > 5000ms | Page on-call |
| Database down | Yes | Page on-call |
| Redis down | Yes | Page on-call |
| Memory > 90% | Yes | Page on-call |

### High Priority Alerts (Slack notification)

| Metric | Threshold | Action |
|--------|-----------|--------|
| Uptime | < 99.5% | Slack alert |
| Error rate | > 2% | Slack alert |
| API latency (avg) | > 2000ms | Slack alert |
| Cache hit rate | < 30% | Slack alert |
| DB connections | > 80% pool | Slack alert |
| Cost spike | 2x normal | Slack alert |

### Low Priority Alerts (Daily summary)

| Metric | Threshold | Action |
|--------|-----------|--------|
| Errors today | Any | Daily summary |
| Slow queries | > 1s | Daily summary |
| Deprecated endpoints | Used | Daily summary |

### Example Alert Rule (Datadog)

```
Alert if:
- Metric: system.cpu.user
- Over: voxquery-backend-prod
- Is above: 80 percent
- For the last: 5 minutes
- Trigger: 80% CPU for 5+ minutes

Notify:
- @pagerduty-prod-oncall
- @slack-#voxcore-alerts

Message:
"🚨 CRITICAL: voxquery-backend-prod CPU at {{value}}%"
```

---

## 📊 DASHBOARDS

### Main Production Dashboard

**Create in Datadog/Grafana:**

```
╔════════════════════════════════════════════════╗
║ VoxCore Production Dashboard                   ║
╠════════════════════════════════════════════════╣
║                                                ║
║  [Uptime: 99.98%] [Error Rate: 0.12%]         ║
║  [Avg Latency: 245ms] [Cache Hit: 68%]       ║
║                                                ║
║  ┌─ Uptime (24h)          ┌─ Error Rate       ║
║  │ ████████████████░      │ ░░░░░░░░░░░░░  ║
║  │ 99.98%                 │ 0.12%             ║
║  └─────────────────────   └─────────────────  ║
║                                                ║
║  ┌─ Latency (ms)          ┌─ Requests/min    ║
║  │ ▁▂▃▂▁▂▃▂▁▂▃▂▂▃▂▃      │ ▅▆▇▆▅▆▇▆▅▆▇▆  ║
║  │ 245ms (avg)            │ 185/min           ║
║  └─────────────────────   └─────────────────  ║
║                                                ║
║  ┌─ Cache Hit Rate        ┌─ DB Connections  ║
║  │ 68% [████████░░]       │ 12 of 20 (60%)   ║
║  └─────────────────────   └─────────────────  ║
║                                                ║
║  Recent Alerts:                                ║
║  ✅ All systems normal (last 24h)            ║
║                                                ║
╚════════════════════════════════════════════════╝
```

### Query Performance Dashboard

```
╔════════════════════════════════════════════════╗
║ Query Performance Analysis                     ║
╠════════════════════════════════════════════════╣
║                                                ║
║  Top 5 Slowest Queries:                       ║
║  1. "JOIN organization" - 1250ms              ║
║  2. "SELECT * FROM --" - 890ms                ║
║  3. "CROSS JOIN" - 750ms                      ║
║                                                ║
║  Cost Distribution:                            ║
║  < 10:  [████████████░░░░░] 65%              ║
║  10-50: [████░░░░░░░░░░░░░░] 25%             ║
║  > 50:  [█░░░░░░░░░░░░░░░░░░] 10%            ║
║                                                ║
║  Blocked Queries (24h):                       ║
║  SQL Injection: 0                             ║
║  Cost Blocked: 12                             ║
║  Timeout: 3                                    ║
║  No Issues: 24,850                            ║
║                                                ║
╚════════════════════════════════════════════════╝
```

### Infrastructure Dashboard

```
╔════════════════════════════════════════════════╗
║ Infrastructure Status                          ║
╠════════════════════════════════════════════════╣
║                                                ║
║  API Instances:                                ║
║  Instance 1: ✅ CPU 35% | Mem 45% | ✓ Health║
║  Instance 2: ✅ CPU 42% | Mem 52% | ✓ Health║
║                                                ║
║  Database:                                     ║
║  Status: ✅ Connected                         ║
║  Latency: 12ms (avg)                         ║
║  Connections: 12 of 20 (60%)                 ║
║  Disk: 245GB of 500GB (49%)                  ║
║                                                ║
║  Redis:                                        ║
║  Status: ✅ Connected                         ║
║  Memory: 142MB of 256MB (55%)                ║
║  Evictions: 0 (24h)                          ║
║  Hit Rate: 68%                                ║
║                                                ║
║  Network:                                      ║
║  Inbound: 45Mbps (avg)                       ║
║  Outbound: 15Mbps (avg)                      ║
║  Errors: 0 (24h)                             ║
║                                                ║
╚════════════════════════════════════════════════╝
```

---

## 📝 LOGGING SETUP

### Structured Logging

**In main.py:**
```python
import json
import logging
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Log Levels

```
DEBUG   - Development only, verbose output
INFO    - Normal operation, important events
WARNING - Non-critical issues, should investigate
ERROR   - Critical issues, needs immediate attention
CRITICAL- System failure, service down
```

### What to Log

```python
# Query execution
logger.info(json.dumps({
    "event": "query_executed",
    "user_id": user_id,
    "org_id": org_id,
    "query_length": len(query),
    "execution_time_ms": execution_time,
    "rows_returned": rows,
    "cache_hit": is_cached,
    "cost_score": cost,
    "status": "success",
}))

# Errors
logger.error(json.dumps({
    "event": "query_failed",
    "user_id": user_id,
    "org_id": org_id,
    "error_type": type(error).__name__,
    "error_message": str(error),
    "traceback": traceback.format_exc(),
}))

# Security events
logger.warning(json.dumps({
    "event": "security_check_failed",
    "check_type": "sql_injection",
    "user_id": user_id,
    "query": query_snippet,
    "action_taken": "blocked",
}))

# Performance warnings
logger.warning(json.dumps({
    "event": "slow_query",
    "execution_time_ms": 3500,
    "threshold_ms": 2000,
    "query_hash": hash_query,
}))
```

### Log Retention

**Production:**
```
Duration: 90 days
Storage: CloudWatch or Datadog
Cost: ~$50-100/month
Searchable: Yes
Alerts: Yes
```

---

## 📞 ALERTING EXAMPLES

### Slack Integration

```python
import httpx
from fastapi import FastAPI

async def send_slack_alert(severity, message):
    """Send alert to Slack #voxcore-alerts channel"""
    slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
    
    color_map = {
        "critical": "danger",
        "high": "warning",
        "medium": "good",
    }
    
    payload = {
        "attachments": [{
            "color": color_map.get(severity, "good"),
            "title": f"🚨 {severity.upper()}: VoxCore Alert",
            "text": message,
            "footer": "VoxCore Monitoring",
            "ts": int(time.time()),
        }]
    }
    
    async with httpx.AsyncClient() as client:
        await client.post(slack_webhook, json=payload)

# Usage
await send_slack_alert("critical", "Error rate > 5%")
```

### PagerDuty Integration

```python
async def trigger_pagerduty_alert(event_action, description):
    """Trigger PagerDuty incident"""
    pagerduty_key = os.getenv("PAGERDUTY_INTEGRATION_KEY")
    
    payload = {
        "routing_key": pagerduty_key,
        "event_action": event_action,  # "trigger", "resolve"
        "dedup_key": "voxcore-prod",
        "payload": {
            "summary": description,
            "severity": "critical",
            "source": "VoxCore API",
            "custom_details": {
                "timestamp": datetime.utcnow().isoformat(),
                "service": "voxquery-backend-prod",
            },
        },
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://events.pagerduty.com/v2/enqueue",
            json=payload
        )
        return response.json()

# Usage
await trigger_pagerduty_alert("trigger", "Database connection pool exhausted")
```

---

## ✅ MONITORING CHECKLIST

**Before Production Launch:**

- [ ] Render health checks configured
- [ ] Datadog/Monitoring platform set up
- [ ] Key metrics dashboard created
- [ ] Critical alerts configured
- [ ] High-priority alerts configured
- [ ] Slack integration working
- [ ] PagerDuty integration working
- [ ] Logs being collected and stored
- [ ] On-call schedule configured
- [ ] Alert testing completed (test at 2am!)
- [ ] Team trained on alerts
- [ ] Runbook documented
- [ ] Historical baseline data collected (24h min)

**During Production:**

- [ ] Monitor dashboard daily
- [ ] Review alerts daily
- [ ] Adjust alert thresholds if too noisy
- [ ] Review slow query logs weekly
- [ ] Analyze cost trends monthly
- [ ] Capacity planning quarterly

---

## 🎯 SLA TARGETS

**Service Level Agreement (SLA) for Production:**

```
Availability: 99.9% (43 minutes downtime/month max)
Latency (p99): < 2 seconds
Error Rate: < 1%
Cache Hit Rate: > 60%
Data Freshness: < 60 seconds
RTO (Recovery Time): 15 minutes
RPO (Recovery Point): 1 hour (once daily backup)
```

**Dashboard to Track SLA:**

```
╔═══════════════════════════╗
║ SLA Status (This Month)   ║
╠═══════════════════════════╣
║ Availability: 99.98% ✅   ║
║ Target: 99.9%             ║
║ Remaining budget: 38 min   ║
║                           ║
║ Latency P99: 1,250ms ✅   ║
║ Target: 2,000ms           ║
║ Margin: 750ms             ║
║                           ║
║ Error Rate: 0.08% ✅      ║
║ Target: 1%                ║
║ Margin: 0.92%             ║
╚═══════════════════════════╝
```

---

**🎉 Monitoring setup complete! Your production system is now observable. 📊**

