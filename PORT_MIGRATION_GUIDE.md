# VoxCore Backend Port Migration Guide (8000 → 10000)

**Date:** March 12, 2026  
**Status:** ✅ Complete  
**Breaking Change:** Yes - Port changed from 8000 to 10000

---

## Summary of Changes

The VoxCore backend has been migrated from **port 8000** to **port 10000** for production deployments.

This change is **required** for the latest Dockerfile and docker-compose configurations.

---

## Why Port 10000?

| Aspect | Port 8000 | Port 10000 |
|--------|-----------|-----------|
| **Status** | Development-only | Production-grade |
| **Range** | Well-known ports | Custom private range |
| **Conflicts** | Common with other services | Rarely used |
| **Security** | No special restrictions | Requires explicit allow |
| **Convention** | Flask/Django default | VoxCore official |

---

## What Changed

### Backend Dockerfile

**Before:**
```dockerfile
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
EXPOSE 8000
```

**After:**
```dockerfile
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]
EXPOSE 10000
```

### docker-compose.prod.yml

**Before:**
```yaml
services:
  backend:
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mssql://...
```

**After:**
```yaml
services:
  backend:
    ports:
      - "10000:10000"
    environment:
      - DATABASE_URL=mssql+pyodbc://...
      - VOXCORE_ENCRYPTION_KEY=${VOXCORE_ENCRYPTION_KEY}
```

### docker-compose.simple.yml (New)

```yaml
services:
  backend:
    ports:
      - "10000:10000"  # ← Port 10000
```

---

## Migration Steps

### Step 1: Update Local Configuration

If you have existing deployments using port 8000:

```bash
# Update docker-compose overrides
cat > docker-compose.override.yml <<EOF
version: "3.9"
services:
  backend:
    ports:
      - "10000:10000"  # Changed from 8000:8000
EOF
```

### Step 2: Update Environment Variables

Update any scripts or CI/CD that reference port 8000:

```bash
# Old health check
curl http://localhost:8000/health

# New health check
curl http://localhost:10000/health
```

### Step 3: Update Frontend API URL

The frontend may have cached the old port. Update in `.env`:

```env
# Old
VITE_API_URL=http://localhost:8000/api

# New
VITE_API_URL=http://localhost:10000/api
```

Or in `docker-compose.prod.yml`:

```yaml
frontend:
  environment:
    - VITE_API_URL=http://backend:10000/api
```

### Step 4: Update Reverse Proxy Configuration

If using Nginx:

```nginx
# Before
upstream backend {
    server localhost:8000;
}

# After
upstream backend {
    server localhost:10000;
}
```

If using Apache:

```apache
# Before
ProxyPass "/" "http://localhost:8000/"

# After
ProxyPass "/" "http://localhost:10000/"
```

### Step 5: Rebuild and Redeploy

```bash
# Stop old containers
docker compose -f docker-compose.prod.yml down

# Remove old images
docker rmi voxcore-backend:latest

# Rebuild with new port
docker compose -f docker-compose.prod.yml build backend

# Start
docker compose -f docker-compose.prod.yml up -d

# Verify
curl http://localhost:10000/health
```

---

## Testing the Migration

### Quick Test

```bash
# Check if port is open
lsof -i :10000

# Test API health
curl -i http://localhost:10000/health

# Expected response:
# HTTP/1.1 200 OK
# {"status":"ok","database":"connected"}
```

### Full Integration Test

```bash
# 1. Start VoxCore
docker compose -f docker-compose.prod.yml up -d

# 2. Wait for startup
sleep 10

# 3. Test backend health
curl http://localhost:10000/health

# 4. Test frontend (if running)
curl http://localhost:5173

# 5. View logs
docker logs voxcore-backend | grep "Uvicorn running"
```

### Load Test (Optional)

```bash
# Install hey (HTTP benchmarking tool)
go install github.com/rakyll/hey@latest

# Send 100 requests
hey -n 100 -c 10 http://localhost:10000/health

# Expected: ~1000+ requests/sec on modern hardware
```

---

## Rollback (If Needed)

If you need to revert to port 8000:

```bash
# Checkout previous Dockerfile
git checkout HEAD~1 backend/Dockerfile

# Rebuild
docker compose build backend

# Redeploy
docker compose -f docker-compose.prod.yml up -d backend
```

---

## Docker Networking

### Internal Container Communication

When containers talk to each other (e.g., nginx → backend):

```yaml
# ❌ Don't use port on external interface
backend:
  ports:
    - "10000:10000"  # Opens to host
  # nginx accesses as: http://backend:10000

# ✅ Better: Only expose internally if not needed on host
backend:
  environment:
    - PORT=10000
  # nginx accesses as: http://backend:10000
```

### Port Mapping

```
Container:10000 ←→ Host:10000

External requests:
  Browser → http://localhost:10000
  
Internal requests (Docker):
  nginx → http://backend:10000
  worker → http://backend:10000
```

---

## Cloud Deployment Adjustments

### AWS ECS

```json
{
  "name": "voxcore-backend",
  "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/voxcore-backend:latest",
  "portMappings": [
    {
      "containerPort": 10000,
      "hostPort": 10000,
      "protocol": "tcp"
    }
  ]
}
```

### AWS ALB/NLB

```hcl
# Terraform
resource "aws_lb_target_group" "backend" {
  name        = "voxcore-backend"
  port        = 10000  # ← Changed from 8000
  target_type = "ip"
}
```

### Google Cloud Run

```bash
gcloud run deploy voxcore-backend \
  --image gcr.io/PROJECT_ID/voxcore-backend \
  --port 10000 \
  --allow-unauthenticated
```

### Azure Container Instances

```bash
az container create \
  --image voxcore-backend:latest \
  --ports 10000 \
  --port-protocol TCP
```

---

## Kubernetes Adjustments

```yaml
apiVersion: v1
kind: Service
metadata:
  name: voxcore-backend
spec:
  type: LoadBalancer
  ports:
  - port: 10000         # External port
    targetPort: 10000   # Container port
    protocol: TCP
  selector:
    app: voxcore-backend
```

---

## Monitoring & Logging

Update any monitoring/logging tools that track the old port:

### Prometheus Scrape Config

```yaml
# Before
scrape_configs:
  - job_name: 'voxcore'
    static_configs:
      - targets: ['localhost:8000']

# After
scrape_configs:
  - job_name: 'voxcore'
    static_configs:
      - targets: ['localhost:10000']
```

### Datadog Agent

```yaml
init_config:

instances:
  - openmetrics_endpoint: http://localhost:10000/metrics  # Changed from 8000
```

---

## CI/CD Pipeline Updates

### GitHub Actions

```yaml
- name: Test Backend Health
  run: |
    docker compose -f docker-compose.prod.yml up -d
    sleep 10
    curl -f http://localhost:10000/health || exit 1  # Changed port
```

### GitLab CI

```yaml
test_backend:
  script:
    - docker compose -f docker-compose.prod.yml up -d
    - sleep 10
    - curl -f http://localhost:10000/health || exit 1  # Changed port
```

---

## Firewall Rules

Update firewall to **allow port 10000** instead of 8000:

### Linux (UFW)

```bash
# Remove old rule
sudo ufw delete allow 8000

# Add new rule
sudo ufw allow 10000
sudo ufw status
```

### Linux (iptables)

```bash
# Remove old rule
iptables -D INPUT -p tcp --dport 8000 -j ACCEPT

# Add new rule
iptables -A INPUT -p tcp --dport 10000 -j ACCEPT
```

### Windows (Windows Defender Firewall)

```powershell
# Remove old rule
Remove-NetFirewallRule -DisplayName "VoxCore Backend 8000"

# Add new rule
New-NetFirewallRule -DisplayName "VoxCore Backend 10000" `
  -Direction Inbound -Action Allow -Protocol TCP -LocalPort 10000
```

---

## Checklist

- [ ] Updated `docker-compose.prod.yml` and `docker-compose.simple.yml`
- [ ] Updated `VITE_API_URL` in frontend config
- [ ] Updated nginx/reverse proxy configuration
- [ ] Updated health check scripts/monitoring
- [ ] Updated CI/CD pipelines
- [ ] Updated firewall rules
- [ ] Rebuilt Docker images
- [ ] Tested health endpoint on port 10000
- [ ] Verified frontend connects to backend
- [ ] Checked logs for any errors
- [ ] Documented changes for team

---

## Files Changed

| File | Change | Impact |
|------|--------|--------|
| `backend/Dockerfile` | Port 8000 → 10000 | Breaking |
| `docker-compose.prod.yml` | Port 8000 → 10000 | Breaking |
| `docker-compose.simple.yml` | New file with port 10000 | Breaking |
| `backend/requirements.txt` | Added sqlalchemy, mysqlclient | Non-breaking |

---

## Support

If you encounter issues:

1. **Check port is open:**
   ```bash
   netstat -an | grep 10000
   lsof -i :10000
   ```

2. **View Docker logs:**
   ```bash
   docker logs voxcore-backend
   ```

3. **Verify firewall:**
   ```bash
   curl http://localhost:10000/health
   ```

4. **Rollback if needed:**
   ```bash
   git checkout HEAD~1 backend/Dockerfile
   docker compose build backend
   ```

---

**Migration Complete!** Your VoxCore backend is now running on port 10000. 🚀

Version: 2.0  
Last Updated: March 12, 2026
