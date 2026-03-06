# VoxQuery Deployment Checklist

## Pre-Deployment (CRITICAL)

### 1. Backup Configuration Files
```bash
# Backup .env files
cp backend/.env backend/.env.backup
cp backend/.env backend/.env.$(date +%Y%m%d_%H%M%S).backup

# Backup connection strings (if stored elsewhere)
# cp /path/to/connections.json /path/to/connections.json.backup
```

**Files to Backup:**
- ✅ `backend/.env` - Main environment configuration
- ✅ `backend/.env.backup` - Already created
- ✅ Connection strings (if in separate files)
- ✅ Database credentials (if stored in config files)
- ✅ API keys (LLM, LangSmith, etc.)

### 2. Verify All Services Running
```bash
# Check backend
curl http://localhost:8000/api/v1/health

# Check frontend
curl http://localhost:5175

# Check database connection
# Test from backend logs
```

**Checklist:**
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5175
- [ ] Database connection working
- [ ] LLM (Ollama) accessible
- [ ] No error logs in console

### 3. Test All Features
```bash
# Test SQL generation
# Test chart generation
# Test exports (CSV, Excel, Markdown)
# Test SSRS embed URL
# Test connection indicator
# Test frozen columns
# Test KPI cards
# Test refresh button
# Test share report button
```

**Checklist:**
- [ ] Natural language → SQL generation works
- [ ] Results display with KPI cards
- [ ] Charts render correctly (all 4 types)
- [ ] Frozen columns work on scroll
- [ ] All export formats work
- [ ] SSRS URL generates correctly
- [ ] Connection status shows correctly
- [ ] Refresh button re-runs query
- [ ] Share button generates link
- [ ] Print output looks professional

### 4. Security Review
```bash
# Check .env doesn't contain secrets in git
git status backend/.env

# Verify SECRET_KEY is changed
grep SECRET_KEY backend/.env

# Check CORS origins are correct
grep CORS backend/.env

# Verify database credentials are secure
# (not hardcoded in code)
```

**Checklist:**
- [ ] .env file is in .gitignore
- [ ] SECRET_KEY is changed from default
- [ ] Database credentials are secure
- [ ] API keys are not exposed
- [ ] CORS origins are restricted
- [ ] No sensitive data in logs
- [ ] HTTPS enabled (if production)

### 5. Performance Check
```bash
# Check response times
# Monitor memory usage
# Check database query performance
# Verify chart generation speed
```

**Checklist:**
- [ ] Query response time < 5 seconds
- [ ] Chart generation < 2 seconds
- [ ] Memory usage stable
- [ ] No memory leaks
- [ ] Database indexes optimized

---

## Deployment Steps

### Step 1: Stop Current Services
```bash
# Stop backend
# Stop frontend
# Stop any other services
```

### Step 2: Deploy Backend
```bash
# Pull latest code
git pull origin main

# Install dependencies
pip install -r backend/requirements.txt

# Run migrations (if any)
# python backend/migrate.py

# Start backend
python backend/main.py
```

### Step 3: Deploy Frontend
```bash
# Pull latest code
git pull origin main

# Install dependencies
npm install

# Build
npm run build

# Start
npm run dev
```

### Step 4: Verify Deployment
```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Check frontend loads
curl http://localhost:5175

# Test a query
# Verify all features work
```

### Step 5: Monitor
```bash
# Watch logs for errors
# Monitor performance
# Check database connections
# Verify no memory leaks
```

---

## Post-Deployment

### 1. Verify All Features
- [ ] Welcome message displays correctly
- [ ] Connection indicator shows status
- [ ] KPI cards appear above table
- [ ] Frozen columns work
- [ ] All export formats work
- [ ] Charts render correctly
- [ ] Refresh button works
- [ ] Share button works
- [ ] Print output looks good
- [ ] Mobile responsive

### 2. Monitor Performance
- [ ] Query response times
- [ ] Chart generation speed
- [ ] Memory usage
- [ ] Database performance
- [ ] API response times

### 3. Check Logs
- [ ] No error messages
- [ ] No warning messages
- [ ] No memory leaks
- [ ] No database connection issues
- [ ] No LLM errors

### 4. User Testing
- [ ] Test with different warehouses
- [ ] Test with different query types
- [ ] Test with large datasets
- [ ] Test on mobile devices
- [ ] Test print functionality

---

## Rollback Plan

If deployment fails:

```bash
# Stop services
# Restore from backup
cp backend/.env.backup backend/.env

# Restart services
python backend/main.py
npm run dev

# Verify
curl http://localhost:8000/api/v1/health
```

---

## Environment Variables Reference

### Required
```bash
WAREHOUSE_TYPE=snowflake|sqlserver|postgres|redshift|bigquery
WAREHOUSE_HOST=your-host
WAREHOUSE_USER=your-user
WAREHOUSE_PASSWORD=your-password
WAREHOUSE_DATABASE=your-database
WAREHOUSE_SCHEMA=your-schema
```

### LLM Configuration
```bash
LLM_PROVIDER=ollama|openai|anthropic
LLM_MODEL=model-name
LLM_API_KEY=your-api-key
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=2000
```

### Security
```bash
SECRET_KEY=change-me-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### API
```bash
API_HOST=0.0.0.0
API_PORT=8000
API_CORS_ORIGINS=["http://localhost:5175"]
```

---

## Backup Strategy

### Daily Backups
```bash
# Backup .env
cp backend/.env backend/.env.$(date +%Y%m%d).backup

# Backup database (if applicable)
# pg_dump database > backup_$(date +%Y%m%d).sql
```

### Weekly Backups
```bash
# Full system backup
# tar -czf voxquery_backup_$(date +%Y%m%d).tar.gz .
```

### Retention Policy
- Daily backups: Keep 7 days
- Weekly backups: Keep 4 weeks
- Monthly backups: Keep 12 months

---

## Disaster Recovery

### If Database Connection Lost
1. Check database is running
2. Verify credentials in .env
3. Check network connectivity
4. Restart backend service

### If LLM Not Responding
1. Check Ollama is running
2. Verify LLM_PROVIDER setting
3. Check API key (if using OpenAI)
4. Restart backend service

### If Frontend Not Loading
1. Check frontend is running
2. Verify port 5175 is accessible
3. Check browser console for errors
4. Clear browser cache

### If Queries Failing
1. Check database connection
2. Verify schema exists
3. Check table permissions
4. Review query logs

---

## Performance Optimization

### Database
- [ ] Create indexes on frequently queried columns
- [ ] Analyze query execution plans
- [ ] Optimize slow queries
- [ ] Monitor connection pool

### Backend
- [ ] Enable query caching
- [ ] Optimize LLM prompts
- [ ] Reduce token usage
- [ ] Monitor memory usage

### Frontend
- [ ] Enable code splitting
- [ ] Optimize bundle size
- [ ] Cache static assets
- [ ] Lazy load components

---

## Monitoring

### Key Metrics
- Query response time
- Chart generation time
- Memory usage
- Database connections
- API response time
- Error rate

### Alerts
- Response time > 5 seconds
- Memory usage > 80%
- Error rate > 1%
- Database connection failures
- LLM API failures

---

## Support

### Common Issues

**Q: Backend won't start**
A: Check .env file, verify database connection, check port 8000 is available

**Q: Frontend won't load**
A: Check npm dependencies, verify port 5175 is available, check browser console

**Q: Queries failing**
A: Check database connection, verify schema/table names, check LLM is running

**Q: Charts not rendering**
A: Check data format, verify Vega-Lite library loaded, check browser console

---

## Checklist Summary

### Pre-Deployment
- [ ] Backup .env files
- [ ] Verify all services running
- [ ] Test all features
- [ ] Security review
- [ ] Performance check

### Deployment
- [ ] Stop current services
- [ ] Deploy backend
- [ ] Deploy frontend
- [ ] Verify deployment
- [ ] Monitor

### Post-Deployment
- [ ] Verify all features
- [ ] Monitor performance
- [ ] Check logs
- [ ] User testing
- [ ] Document any issues

---

**Status**: Ready for Production Deployment ✅
