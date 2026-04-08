# STEP 16 — INTEGRATION GUIDE
## Step-by-Step Implementation Instructions

**Document Version:** 1.0  
**Target:** FastAPI + Python backend  
**Integration Points:** 5 major, 3 minor

---

## 📋 INTEGRATION CHECKLIST

### Priority 1: Immediate (Blocking)

- [ ] Create `/backend/enterprise/` directory
- [ ] Copy all 9 component files
- [ ] Update main FastAPI app with middleware
- [ ] Configure secrets manager
- [ ] Enable HTTPS

### Priority 2: This Week

- [ ] Integrate encryption into query results
- [ ] Apply data classification to database
- [ ] Enable audit logging in query execution
- [ ] Deploy access traceability
- [ ] Test compliance export

### Priority 3: This Month

- [ ] Configure AWS/Azure secrets manager
- [ ] Set up audit log persistence (database)
- [ ] Implement key rotation schedule
- [ ] Create monitoring dashboard for violations

---

## 🔧 INTEGRATION POINTS

### INTEGRATION 1: Security Middleware (Fast API)

**File:** `main.py` or `app.py`

```python
# At top of file
from fastapi import FastAPI, Request, Response
from backend.enterprise import get_security_middleware
import time

app = FastAPI()

# Add security middleware FIRST (runs on all requests)
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Add security headers and rate limiting to all requests"""
    middleware = get_security_middleware()
    
    # Extract request info
    user_id = None
    if hasattr(request.user, 'id'):
        user_id = request.user.id
    
    ip_address = request.client.host if request.client else "unknown"
    endpoint = request.url.path
    
    # Check rate limit
    is_throttled, error_message = middleware.rate_limiter.is_throttled(
        user_id=user_id,
        ip_address=ip_address,
        endpoint=endpoint
    )
    
    if is_throttled:
        return Response(
            status_code=429,
            content=f"Too Many Requests: {error_message}",
            media_type="text/plain"
        )
    
    # Record this request
    middleware.rate_limiter.record_request(user_id, ip_address, endpoint)
    
    # Process request
    response = await call_next(request)
    
    # Add security headers to response
    security_headers = {
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'",
    }
    
    for header_name, header_value in security_headers.items():
        response.headers[header_name] = header_value
    
    return response
```

**Test It:**
```bash
# Should work (within limit)
curl http://localhost:8000/api/query

# Test rate limit (send 100 requests rapidly)
for i in {1..100}; do curl http://localhost:8000/api/query; done
# Should get 429 Too Many Requests after ~60 requests
```

---

### INTEGRATION 2: Encryption in Query Results

**File:** `backend/api/query_endpoint.py` or similar

```python
from fastapi import APIRouter
from backend.enterprise import (
    get_encryption_service,
    get_classification_framework,
    encrypt_sensitive_value
)
from backend.enterprise.data_classification import apply_masking

router = APIRouter()

@router.post("/api/query")
async def execute_query(request: QueryRequest, current_user):
    """Execute query with encryption and masking"""
    
    # Execute query normally
    result = await query_executor.execute(request.sql)
    
    # Get encryption service
    encryption_service = get_encryption_service()
    classification_framework = get_classification_framework()
    
    # Apply encryption and masking to results
    encrypted_result = []
    for row in result:
        encrypted_row = {}
        for field_name, field_value in row.items():
            # Should this field be encrypted?
            if classification_framework.should_encrypt_field(field_name):
                # Encrypt it
                encrypted_row[field_name] = encryption_service.encrypt(str(field_value))
            
            # Should this field be masked?
            elif classification_framework.should_mask_field(field_name, current_user.role):
                # Apply mask
                mask_format = classification_framework.get_mask_format(field_name)
                encrypted_row[field_name] = apply_masking(str(field_value), mask_format)
            
            else:
                # Keep as-is
                encrypted_row[field_name] = field_value
        
        encrypted_result.append(encrypted_row)
    
    return encrypted_result
```

**What Happens:**
- `salary` field → encrypted (users can't see it)
- `email` field → masked as `***@***.***` (unless user has "finance" role)
- `name` field → kept as-is (not sensitive)

---

### INTEGRATION 3: Audit Logging

**File:** `backend/api/query_endpoint.py` (same as above, add audit logging)

```python
from backend.enterprise import log_query_executed, log_data_access
from datetime import datetime
import time

@router.post("/api/query")
async def execute_query(request: QueryRequest, current_user):
    """Execute query with audit logging"""
    
    ip_address = request.client.host
    start_time = time.time()
    
    try:
        # Execute query
        result = await query_executor.execute(request.sql)
        execution_time_ms = (time.time() - start_time) * 1000
        
        # 1. Log the query execution
        await log_query_executed(
            user_id=current_user.id,
            query=request.sql[:200],  # Don't log full query for privacy
            execution_time_ms=execution_time_ms,
            rows_returned=len(result),
            ip_address=ip_address,
            success=True
        )
        
        # 2. Log data access
        # Extract which columns were accessed
        columns_accessed = extract_columns_from_query(request.sql)
        
        await log_data_access(
            user_id=current_user.id,
            resource=extract_table_from_query(request.sql),
            columns=columns_accessed,
            classification="sensitive",
            user_role=current_user.role,
            result=AccessResult.GRANTED,
            ip_address=ip_address,
            rows_accessed=len(result),
            data_masked=False
        )
        
        return result
    
    except Exception as e:
        # Log failed query
        await log_query_executed(
            user_id=current_user.id,
            query=request.sql[:200],
            execution_time_ms=(time.time() - start_time) * 1000,
            rows_returned=0,
            ip_address=ip_address,
            success=False,
            error=str(e)
        )
        raise
```

---

### INTEGRATION 4: Data Classification & Access Control

**File:** `backend/api/query_endpoint.py` (add before query execution)

```python
from backend.enterprise import get_classification_framework

@router.post("/api/query")
async def execute_query(request: QueryRequest, current_user):
    """Check data classification before executing query"""
    
    classification_framework = get_classification_framework()
    columns_in_query = extract_columns_from_query(request.sql)
    
    for column_name in columns_in_query:
        policy = classification_framework.classify_field(column_name)
        
        # Check if user has required MFA
        if policy.requires_mfa and not current_user.mfa_verified:
            return Response(
                status_code=403,
                content=f"MFA required to access {column_name}"
            )
        
        # Check if user has required role
        if policy.permitted_roles and current_user.role not in policy.permitted_roles:
            return Response(
                status_code=403,
                content=f"Role {current_user.role} cannot access {column_name}"
            )
        
        # Check if access requires approval
        if policy.requires_approval:
            if not await check_approval(current_user.id, column_name):
                return Response(
                    status_code=403,
                    content=f"Access to {column_name} requires manager approval"
                )
    
    # All checks passed, execute query
    result = await query_executor.execute(request.sql)
    return result
```

---

### INTEGRATION 5: Compliance Export Endpoint

**File:** `backend/api/compliance_endpoint.py` (new file)

```python
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from backend.enterprise import (
    ComplianceReportType,
    ExportFormat,
    generate_compliance_report
)

router = APIRouter()

@router.get("/api/compliance/export")
async def export_compliance_report(
    report_type: str = "soc2_compliance",
    export_format: str = "json",
    days_back: int = 30,
    current_user = Depends(get_current_user)
):
    """
    Export compliance report for auditors.
    
    Requires admin role.
    
    Example:
        GET /api/compliance/export?report_type=soc2_compliance&export_format=pdf&days_back=90
    
    Response:
        PDF file with compliance report
    """
    
    # Require admin role
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    
    # Parse parameters
    try:
        report_enum = ComplianceReportType[report_type.upper()]
        format_enum = ExportFormat[export_format.upper()]
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {e}")
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days_back)
    
    # Generate report
    try:
        report = await generate_compliance_report(
            report_type=report_enum,
            start_date=start_date,
            end_date=end_date,
            export_format=format_enum
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")
    
    # Return based on format
    if format_enum == ExportFormat.JSON:
        return report  # FastAPI automatically serializes to JSON
    
    elif format_enum == ExportFormat.CSV:
        return Response(
            content=report,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=compliance_{report_type}.csv"}
        )
    
    elif format_enum == ExportFormat.PDF:
        return Response(
            content=report,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=compliance_{report_type}.pdf"}
        )


# Additional endpoints
@router.get("/api/compliance/controls")
async def get_controls_status(current_user = Depends(get_current_user)):
    """Get SOC2 control verification status"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    
    from backend.enterprise import get_controls_manager
    manager = get_controls_manager()
    return manager.get_control_status_summary()


@router.get("/api/compliance/audit-log")
async def get_audit_log_records(
    limit: int = 100,
    user_id: str = None,
    current_user = Depends(get_current_user)
):
    """Get audit log records"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    
    from backend.enterprise import get_audit_log
    audit_log = await get_audit_log()
    
    records = await audit_log.list_events(
        user_id=user_id,
        limit=limit
    )
    
    return [r.to_dict() for r in records]


@router.get("/api/compliance/violations")
async def get_security_violations(
    hours: int = 24,
    current_user = Depends(get_current_user)
):
    """Get security violations report"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    
    from backend.enterprise import get_security_middleware
    middleware = get_security_middleware()
    return middleware.get_violation_report(hours=hours)
```

**Usage:**
```bash
# Get JSON report
curl "http://localhost:8000/api/compliance/export?report_type=soc2_compliance&export_format=json"

# Get CSV for Excel
curl "http://localhost:8000/api/compliance/export?report_type=query_audit&export_format=csv" > audit.csv

# Get PDF for printing
curl "http://localhost:8000/api/compliance/export?report_type=soc2_compliance&export_format=pdf" > report.pdf

# Get control status
curl "http://localhost:8000/api/compliance/controls"

# Get violations
curl "http://localhost:8000/api/compliance/violations?hours=24"
```

---

## 🔑 SECRETS MANAGER SETUP

### Option A: Local Development (Simple)

```python
# No setup needed, uses LocalDevSecretManager
# Secrets can be passed via environment:

export DB_PASSWORD="mypassword"
export API_KEY="mykey"

# Then in code:
from backend.enterprise import get_secret
password = await get_secret("db_password")  # Reads from env
```

### Option B: AWS Secrets Manager (Production)

```python
# 1. Install boto3
pip install boto3

# 2. Configure AWS credentials
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="us-east-1"

# 3. In your app startup
from backend.enterprise import configure_aws_secrets_manager

@app.on_event("startup")
async def startup():
    configure_aws_secrets_manager(region="us-east-1")

# 4. Now use it
from backend.enterprise import get_secret

@app.post("/api/query")
async def query(request):
    # Retrieve secret from AWS Secrets Manager
    db_password = await get_secret("prod/db_password")
    ...
```

### Option C: Azure Key Vault (Production)

```python
# Similar pattern using Azure SDK
# See backend/enterprise/secrets_manager.py for AzureKeyVault implementation
```

---

## 🗄️ DATABASE SCHEMA

If using persistent audit logs instead of in-memory:

```sql
-- Audit logs table (immutable, append-only)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    user_id VARCHAR(255),
    resource VARCHAR(255),
    action VARCHAR(100),
    details JSONB,
    ip_address VARCHAR(45),
    entry_hash VARCHAR(64) NOT NULL,
    previous_hash VARCHAR(64),
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    INDEX (user_id, timestamp),
    INDEX (event_type, timestamp)
);

-- Data classification table
CREATE TABLE data_classifications (
    id SERIAL PRIMARY KEY,
    field_name VARCHAR(255) UNIQUE NOT NULL,
    classification VARCHAR(20) NOT NULL,
    must_encrypt BOOLEAN DEFAULT FALSE,
    must_mask BOOLEAN DEFAULT FALSE,
    requires_approval BOOLEAN DEFAULT FALSE,
    retention_days INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Access traceability table
CREATE TABLE access_logs (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    user_role VARCHAR(50),
    resource VARCHAR(255),
    column_name VARCHAR(255),
    classification VARCHAR(20),
    result VARCHAR(20),
    rows_accessed INTEGER,
    data_masked BOOLEAN,
    ip_address VARCHAR(45),
    INDEX (user_id, timestamp),
    INDEX (column_name, timestamp)
);

-- SOC2 control verification
CREATE TABLE compliance_controls (
    id VARCHAR(50) PRIMARY KEY,
    control_name VARCHAR(255),
    category VARCHAR(50),
    description TEXT,
    implemented BOOLEAN,
    last_verified TIMESTAMP,
    verification_count INTEGER DEFAULT 0
);
```

---

## ✅ TESTING

### Test 1: Rate Limiting

```python
# test_rate_limiting.py
import asyncio
import time

async def test_rate_limit():
    from backend.enterprise import get_security_middleware
    
    middleware = get_security_middleware()
    
    # Should allow first 60 requests
    for i in range(60):
        is_throttled, _ = middleware.rate_limiter.is_throttled("user1", "1.1.1.1")
        assert not is_throttled, f"Request {i} should be allowed"
        middleware.rate_limiter.record_request("user1", "1.1.1.1")
    
    # 61st should be throttled
    is_throttled, reason = middleware.rate_limiter.is_throttled("user1", "1.1.1.1")
    assert is_throttled, "Request 61 should be throttled"
    print(f"✅ Rate limiting works: {reason}")

asyncio.run(test_rate_limit())
```

### Test 2: Immutable Audit Logs

```python
# test_immutable_logs.py
import asyncio

async def test_immutable_logs():
    from backend.enterprise import get_audit_log, AuditEventType, AuditLogEntry
    from datetime import datetime
    
    audit_log = await get_audit_log()
    
    # Create 10 entries
    for i in range(10):
        entry = AuditLogEntry(
            id=f"entry_{i}",
            event_type=AuditEventType.QUERY_EXECUTED,
            timestamp=datetime.utcnow(),
            user_id=f"user_{i}",
            action="query",
            resource="database"
        )
        await audit_log.log_event(entry)
    
    # Verify chain integrity
    result = await audit_log.verify_chain()
    assert result["chain_integrity"], "Chain should be valid"
    assert result["verified_entries"] == 10, "All 10 entries should verify"
    print(f"✅ Immutable logs work: {result}")

asyncio.run(test_immutable_logs())
```

### Test 3: Data Classification

```python
# test_classification.py
from backend.enterprise import get_classification_framework

def test_classification():
    framework = get_classification_framework()
    
    # Test salary field
    policy = framework.classify_field("salary")
    assert policy.must_encrypt, "Salary should be encrypted"
    assert policy.must_mask, "Salary should be masked"
    assert "finance" in policy.permitted_roles, "Only finance role can see unmasked"
    
    # Should mask for viewer role
    assert framework.should_mask_field("salary", "viewer"), "Mask for viewer"
    assert not framework.should_mask_field("salary", "finance"), "Don't mask for finance"
    
    # Test public field  
    assert not framework.should_mask_field("name", "viewer"), "Name shouldn't be masked"
    
    print("✅ Data classification works")

test_classification()
```

---

## 🚀 DEPLOYMENT CHECKLIST

Before going to production:

- [ ] All secrets moved from `.env` to secrets manager
- [ ] HTTPS enabled (TLS 1.2+ enforced)
- [ ] Rate limiting tested (verify 429 responses)
- [ ] Audit logging persistence (database, not memory)
- [ ] Encryption keys backed up and rotated
- [ ] Data classification policies reviewed by security team
- [ ] Access traceability tested (can query who accessed what)
- [ ] Compliance export tested (PDF/CSV generation working)
- [ ] SOC2 controls verified as passing
- [ ] Security headers visible in responses (`curl -i`)
- [ ] Immutable audit logs verified (hash chain intact)
- [ ] Disaster recovery procedure tested
- [ ] Admin can generate compliance reports

---

## 📞 TROUBLESHOOTING

**Q: "Secret not found" error**  
A: Check that environment variables are set or secrets manager is configured.

**Q: Encryption performance is slow**  
A: Normal (2-5ms per field). For high throughput, consider field-level caching.

**Q: Audit logs filling up database**  
A: Implement log rotation (archive old logs after 1 year).

**Q: How to rotate encryption key?**  
A: Call `encryption_service.rotate_key(new_key)` then re-encrypt all existing data.

**Q: Can I disable rate limiting for internal IPs?**  
A: Yes, check IP in middleware before rate limiting.

---

