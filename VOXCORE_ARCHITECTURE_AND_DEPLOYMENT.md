# VoxCore Architecture & Deployment Guide

**Date:** March 12, 2026  
**Version:** 2.0 - Enterprise Edition  
**Status:** ✅ Production Ready

---

## 🏗️ Architecture Overview

VoxCore is a **multi-database AI governance platform** that enables enterprises to govern AI queries across any database.

```
┌─────────────────────────────────────────────────────────────┐
│                  VoxCore Enterprise Edition                  │
│                                                             │
│  AI SQL Generator → Risk Analysis → Policy Firewall → Audit │
└─────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│              Multi-Database Access Layer                     │
├──────────────────────────────────────────────────────────────┤
│  SQL Server        PostgreSQL        MySQL        SQLite     │
│  (ODBC Driver 18)  (psycopg2)        (mysqlclient) (native) │
└──────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│              Enterprise Databases                             │
├──────────────────────────────────────────────────────────────┤
│  Financials       Analytics        Operations       Warehouse│
│  (SQL Server)     (PostgreSQL)      (MySQL)         (SQLite) │
└──────────────────────────────────────────────────────────────┘
```

---

## 📦 Components

### 1. Backend API (FastAPI, Port 10000)
- **Location:** `backend/` folder
- **Dockerfile:** `backend/Dockerfile`
- **Main File:** `backend/main.py`
- **Responsibilities:**
  - Accept natural language questions
  - Call Groq API for SQL generation
  - Analyze risk (SQL injection, data exposure)
  - Apply policy rules
  - Execute in sandbox
  - Log audit trail
  - Support multi-database drivers

### 2. Query Worker (Redis Queue)
- **Location:** `backend/workers/query_worker.py`
- **Queue:** Redis (port 6379)
- **Responsibilities:**
  - Process async query jobs
  - Execute approved queries
  - Update results cache
  - Retry failed jobs

### 3. Redis Cache (Port 6379)
- **Container:** `redis:7-alpine`
- **Responsibilities:**
  - Queue for async jobs
  - Cache query results
  - Session management
  - Rate limiting

### 4. Frontend (React/Vite, Port 5173)
- **Location:** `frontend/` folder
- **Dockerfile:** `frontend/Dockerfile.prod`
- **Responsibilities:**
  - Dashboard UI
  - Query builder
  - Results visualization
  - Settings/administration
  - Audit logs view

### 5. Database Drivers (Multi-Database)
- **SQL Server:** ODBC Driver 18 + pyodbc
- **PostgreSQL:** psycopg2 library
- **MySQL:** mysqlclient library
- **SQLite:** Python sqlite3 (built-in)

---

## 🔐 Security Layers

### Layer 1: Database Credentials
- ✅ Encrypted with Fernet (AES-128)
- ✅ Stored with `ENC:` prefix
- ✅ Decrypted at runtime using `VOXCORE_ENCRYPTION_KEY`

### Layer 2: AI Query Analysis
- ✅ Risk scoring (0-100)
- ✅ Sensitivity detection
- ✅ Injection pattern detection
- ✅ Column-level access tracking

### Layer 3: Policy Firewall
- ✅ Rule-based enforcement
- ✅ Role-based access control (RBAC)
- ✅ Workspace isolation
- ✅ Query whitelisting/blacklisting

### Layer 4: Audit Logging
- ✅ Query audit table
- ✅ Risk assessment logs
- ✅ Policy decisions
- ✅ Execution results

### Layer 5: Multi-Tenancy
- ✅ User .ini files
- ✅ Workspace isolation
- ✅ Company-level segregation
- ✅ Tenant-specific policies

---

## 🚀 Deployment Scenarios

### Scenario 1: Local Development

```bash
# Start services
docker compose -f docker-compose.simple.yml up -d

# Using Docker host for SQL Server
export DATABASE_URL="mssql+pyodbc://sa:password@host.docker.internal:1433/AdventureWorks2022?driver=ODBC+Driver+18+for+SQL+Server"

# Check health
curl http://localhost:10000/health

# Access UI
open http://localhost:5173
```

### Scenario 2: Cloud Deployment (AWS)

```bash
# Build images
docker build ./backend -t AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/voxcore-backend:latest
docker build ./frontend -t AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/voxcore-frontend:latest

# Push to ECR
docker push AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/voxcore-backend:latest
docker push AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/voxcore-frontend:latest

# Update ECS task definition with:
# - DATABASE_URL from RDS endpoint
# - VOXCORE_ENCRYPTION_KEY from Secrets Manager
# - GROQ_API_KEY from Secrets Manager

# Deploy
aws ecs update-service --cluster voxcore --service backend --force-new-deployment
```

### Scenario 3: Kubernetes Deployment

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: voxcore-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: voxcore-backend
  template:
    metadata:
      labels:
        app: voxcore-backend
    spec:
      containers:
      - name: backend
        image: voxcore-backend:latest
        ports:
        - containerPort: 10000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: voxcore-secrets
              key: database-url
        - name: VOXCORE_ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: voxcore-secrets
              key: encryption-key
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: voxcore-secrets
              key: groq-api-key
```

---

## 📋 File Structure

```
VoxQuery/
├── backend/
│   ├── Dockerfile                          ← Backend multi-db image
│   ├── main.py                             ← FastAPI entry point
│   ├── requirements.txt                    ← Python dependencies
│   ├── api/
│   │   ├── auth.py                         ← Connection/auth endpoints
│   │   ├── query.py                        ← Query endpoints
│   │   └── governance.py                   ← Policy endpoints
│   ├── services/
│   │   ├── credential_encryption.py        ← Encryption service
│   │   ├── risk_engine.py                  ← Risk analysis
│   │   └── policy_engine.py                ← Policy enforcement
│   ├── workers/
│   │   └── query_worker.py                 ← Async query processing
│   └── db/
│       └── models.py                       ← Database models
│
├── frontend/
│   ├── Dockerfile.prod                     ← Frontend build
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Databases.tsx
│   │   │   ├── QueryLogs.tsx
│   │   │   ├── Policies.tsx
│   │   │   └── SqlAssistant.tsx
│   │   ├── components/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── PageHeader.tsx
│   │   │   └── LiveQueryFlow.tsx
│   │   └── App.tsx
│   └── package.json
│
├── Dockerfile                              ← Root Dockerfile (optional)
├── docker-compose.prod.yml                 ← Full production stack
├── docker-compose.simple.yml               ← Minimal stack
├── encrypt_credentials.py                  ← CLI encryption tool
│
├── MULTI_DATABASE_CONNECTION_GUIDE.md      ← Connection strings
├── CREDENTIAL_ENCRYPTION_GUIDE.md          ← Encryption setup
├── PRODUCTION_DOCKERFILE_AND_ENCRYPTION_SUMMARY.md
└── README.md
```

---

## 🔧 Configuration Files

### `.env` (Environment Variables)

```env
# Backend
ENV=production
DATABASE_URL=mssql+pyodbc://sa:password@host:1433/db?driver=ODBC+Driver+18+for+SQL+Server
REDIS_URL=redis://localhost:6379/0

# Encryption
VOXCORE_ENCRYPTION_KEY=z0ODAvfvO_K9mJ4...

# AI/LLM
GROQ_API_KEY=gsk_123...

# Server
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
PORT=10000
```

### `docker-compose.prod.yml` (Full Stack)

Services:
- `backend` - FastAPI app (port 10000)
- `frontend` - React app (port 5173)
- `redis` - Job queue (port 6379)
- `query-worker` - Async job processor
- `nginx` - Reverse proxy (port 80)

### `docker-compose.simple.yml` (Minimal)

Services:
- `backend` - FastAPI app (port 10000)
- `redis` - Job queue (port 6379)
- `query-worker` - Async job processor

**Use this** for development or when frontend/nginx are hosted separately.

---

## 📊 Data Flow

### Query Processing Pipeline

```
1. User asks: "Show me the sum of all transactions"
   ↓
2. Frontend sends to backend (/api/v1/query/ask)
   ↓
3. Backend calls Groq API
   → AI generates SQL: "SELECT SUM(amount) FROM Transactions"
   ↓
4. Risk Analysis Engine
   → Score: 15 (LOW RISK)
   → Sensitivity: PUBLIC
   ↓
5. Policy Firewall
   → Check: Is user allowed to access Transactions?
   → Check: Does query match security policies?
   → Result: ✅ APPROVED
   ↓
6. Sandbox Execution
   → Execute SELECT (read-only)
   → Get result count
   → Preview data
   ↓
7. Store Audit Log
   → Query text
   → Risk score
   → User ID
   → Timestamp
   → Result
   ↓
8. Return to Frontend
   → Query result
   → Risk badge
   → Execution time
   → Forensic ID (for investigation)
```

---

## 📈 Scaling Considerations

### Single Backend Instance
```
Suitable for: <100 concurrent users
Setup: docker-compose.simple.yml
Performance: ~50 queries/second
```

### Multiple Backends + Load Balancer
```
Suitable for: 100-1000 concurrent users
Setup: Kubernetes or ECS with load balancer
Performance: ~500 queries/second
```

### Distributed Architecture
```
Suitable for: 1000+ concurrent users
Setup: Multi-region, auto-scaling
Performance: Limited by database capacity
```

---

## 🔍 Monitoring & Observability

### Health Check
```bash
curl http://localhost:10000/health
# Returns: {"status": "ok", "database": "connected", "redis": "connected"}
```

### logs
```bash
# Docker logs
docker logs voxcore-backend
docker logs voxcore-query-worker

# Or use ELK stack, Datadog, etc. for production
```

### Metrics
- Query latency (p50, p95, p99)
- Risk scores (distribution)
- Policy rejections
- Audit trail
- Database connection pool utilization

---

## 🎯 Next Steps

1. **Choose deployment approach** (Local / Cloud / K8s)
2. **Set up database** (SQL Server / PostgreSQL / MySQL)
3. **Configure environment variables**
4. **Build Docker images**
5. **Deploy with chosen compose file**
6. **Test with /health endpoint**
7. **Access frontend, create workspace**
8. **Connect database via UI**
9. **Start governing queries!**

---

## 📞 Support & References

| Topic | File | Link |
|-------|------|------|
| Connection Strings | MULTI_DATABASE_CONNECTION_GUIDE.md | ✅ |
| Credential Encryption | CREDENTIAL_ENCRYPTION_GUIDE.md | ✅ |
| ODBC Setup | ODBC_DRIVER_AND_DATABASE_UI_FIX.md | ✅ |
| Production Summary | PRODUCTION_DOCKERFILE_AND_ENCRYPTION_SUMMARY.md | ✅ |

---

## 🏆 Why VoxCore Is Enterprise-Grade

### ✅ Multi-Database Support
- SQL Server, PostgreSQL, MySQL, SQLite
- Connection pooling
- Automatic driver installation

### ✅ AI-Powered Governance
- Groq API for SQL generation
- Risk scoring algorithm
- Policy-based enforcement

### ✅ Security First
- Encrypted credentials
- Multi-tenant isolation
- Audit logging
- RBAC

### ✅ Scalable Architecture
- Async job queues (Redis)
- Horizontal scaling
- Cloud-native deployment

### ✅ Enterprise Features
- Query forensics/investigation
- Live query flow visualization
- Dashboard analytics
- Admin controls

---

**VoxCore: Your AI Database Governor** 🚀

**Version:** 2.0 Enterprise Edition  
**Last Updated:** March 12, 2026
