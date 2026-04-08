# VoxCore Environment Variables Reference

Quick lookup for all environment variables needed across all 3 deployment stages.

---

## Frontend Environment Variables

### `.env.development` (Local Development)
```
VITE_API_URL=http://localhost:8000
VITE_API_KEY=dev-key-local-testing
```

### `.env.staging` (Staging Deployment)
```
VITE_API_URL=https://staging-api.onrender.com
VITE_API_KEY=staging-secret-key-replace-with-real
```

### `.env.production` (Production Deployment)
```
VITE_API_URL=https://api.voxcore.app
VITE_API_KEY=prod-secret-key-replace-with-real
```

**Frontend Variables Explained:**
| Variable | Purpose | Example |
|----------|---------|---------|
| VITE_API_URL | Where the backend API is running | http://localhost:8000 |
| VITE_API_KEY | API key for authentication (sent in x-api-key header) | openssl rand -hex 32 |

---

## Backend Environment Variables

### `.env.development` (Local Development)
```
ENV=development
DEBUG=true
LOG_LEVEL=debug
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=dev-key-local-testing-only
SECRET_KEY=dev-secret-key-not-secure-change-in-prod
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
DATABASE_URL=sqlite:///voxquery.db
MAX_ROWS=500
QUERY_TIMEOUT=5
MAX_QUERIES_PER_MINUTE=60
REQUEST_TIMEOUT=30
```

### `.env.staging` (Staging Deployment)
```
ENV=staging
DEBUG=false
LOG_LEVEL=info
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=staging-api-key-changeme
SECRET_KEY=staging-secret-key-changeme
CORS_ORIGINS=https://staging.voxcore.app,https://staging-api.onrender.com
DATABASE_URL=postgresql://user:pass@staging-db.onrender.com/voxquery_staging
MAX_ROWS=500
QUERY_TIMEOUT=5
MAX_QUERIES_PER_MINUTE=30
REQUEST_TIMEOUT=30
```

### `.env.production` (Production Deployment)
```
ENV=production
DEBUG=false
LOG_LEVEL=info
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=prod-secret-key-replace-with-real
SECRET_KEY=prod-secret-key-replace-with-real
CORS_ORIGINS=https://voxcore.app,https://www.voxcore.app
DATABASE_URL=postgresql://user:pass@prod-db.onrender.com/voxquery
MAX_ROWS=500
QUERY_TIMEOUT=5
MAX_QUERIES_PER_MINUTE=20
REQUEST_TIMEOUT=30
```

**Backend Variables Explained:**
| Variable | Purpose | Dev Example | Prod Value |
|----------|---------|------------|-----------|
| ENV | Environment mode | development | production |
| DEBUG | Enable debug output | true | false |
| LOG_LEVEL | Logging verbosity | debug | info |
| API_HOST | Server bind address | 0.0.0.0 | 0.0.0.0 |
| API_PORT | Server port | 8000 | 8000 |
| API_KEY | Required authentication key | dev-key... | openssl rand -hex 32 |
| SECRET_KEY | Encryption key | dev-secret... | openssl rand -hex 32 |
| CORS_ORIGINS | Allowed frontend origins | localhost:5173 | voxcore.app |
| DATABASE_URL | PostgreSQL connection | sqlite://... | postgresql://... |
| MAX_ROWS | Query result limit | 500 | 500 |
| QUERY_TIMEOUT | Query max duration (seconds) | 5 | 5 |
| MAX_QUERIES_PER_MINUTE | Rate limit | 60 | 20 |
| REQUEST_TIMEOUT | HTTP request timeout | 30 | 30 |

---

## Where to Set These

### Local Development
Set in `.env` file in each folder:
```bash
# Frontend
frontend/.env.development

# Backend
backend/.env.development
```

### Staging Deployment (Render)
Go to **Render Dashboard > Your Service > Environment**:
1. Add each variable from `.env.staging`
2. Click "Save"
3. Render auto-redeploys

### Production Deployment (Render)
Go to **Render Dashboard > Your Service > Environment**:
1. Add each variable from `.env.production`
2. **⚠️ Use REAL values:**
   - Generate API_KEY: `openssl rand -hex 32`
   - Get DATABASE_URL from PostgreSQL service
   - Set CORS_ORIGINS to your domain
3. Click "Save"
4. Render auto-redeploys

### Production Deployment (Vercel)
Go to **Vercel Dashboard > Project > Settings > Environment**:
1. Add for all environments (or override per-environment):
   - `VITE_API_URL=https://api.voxcore.app`
   - `VITE_API_KEY=<same-value-as-backend-API_KEY>`
2. **Type:** "Plaintext" (not encrypted)
3. Click "Save"
4. Vercel auto-redeploys

---

## 🔑 Generating Secure Keys

```bash
# Generate API_KEY (use in both frontend AND backend)
openssl rand -hex 32

# Generate SECRET_KEY (backend only)
openssl rand -hex 32

# Example outputs:
# API_KEY=a7f3c9e2b1d4f8e6a2c5d9f1b3e7a9c2
# SECRET_KEY=5k9m2q7p1r8t3w6y9z2c4v7x0a3d6g9j
```

---

## ☑️ Checklist: Setting Up Production

- [ ] Generate API_KEY: `openssl rand -hex 32`
- [ ] Generate SECRET_KEY: `openssl rand -hex 32`
- [ ] Add both to `frontend/.env.production`
- [ ] Add both to `backend/.env.production`
- [ ] Get DATABASE_URL from Render PostgreSQL
- [ ] Add to `backend/.env.production`
- [ ] Update CORS_ORIGINS with your domain
- [ ] Push to GitHub
- [ ] Add variables to Vercel environment
- [ ] Add variables to Render environment
- [ ] Verify: `curl -H "x-api-key: <key>" https://api.yourdomain.com/docs`

---

## 🚨 Security Tips

1. **Never** commit real API keys to GitHub
   - Use `.gitignore` to exclude `.env.production`
   - Always add via platform UI (Vercel/Render)

2. **Rotate keys** every 90 days
   - Generate new API_KEY
   - Update Vercel and Render
   - Old requests will be rejected

3. **Use different keys** for each environment
   - Dev key: `dev-key...`
   - Staging key: different from dev
   - Prod key: different from staging and dev

4. **Log all changes**
   - Who updated the key
   - When
   - Which environment
   - Why

---

## Reference: What Each Service Reads

```
Frontend (Vercel)
└─ Reads: VITE_API_URL, VITE_API_KEY
└─ Purpose: Know where backend is and how to authenticate

Backend (Render)
├─ Reads: ENV, DEBUG, LOG_LEVEL
├─ Reads: API_KEY (validation), SECRET_KEY (encryption)
├─ Reads: DATABASE_URL (connection)
├─ Reads: CORS_ORIGINS (cross-origin control)
└─ Reads: Query limits and timeouts
```

---

**Reference Version:** 1.0  
**Last Updated:** 2025-03-02  
**Production Ready:** ✅
