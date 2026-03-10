"""
Data Sensitivity Scanner API Routes

Provides endpoints for scanning database schemas and generating security policies.

Author: VoxCore
Date: March 2026
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

router = APIRouter(prefix="/api/scanner", tags=["sensitivity-scanner"])


# Pydantic models for request/response

class ColumnInfo(BaseModel):
    """Database column information"""
    column_name: str
    column_type: Optional[str] = None


class TableSchema(BaseModel):
    """Database table schema"""
    table_name: str
    columns: List[str]


class ScanRequest(BaseModel):
    """Request to scan a database schema"""
    connector_name: str
    schema_info: List[Dict]  # List of {table_name, columns}


class ScanResponse(BaseModel):
    """Scan results"""
    timestamp: str
    connector_name: str
    total_findings: int
    by_type: Dict
    risk_summary: Dict
    by_table: Dict


class PolicyGenerationRequest(BaseModel):
    """Request to generate a policy from scan results"""
    connector_name: str
    scan_results: Dict


class PolicyGenerationResponse(BaseModel):
    """Generated policy"""
    policy_name: str
    description: str
    mask_columns: List[str]
    deny_tables: List[str]
    deny_columns: List[str]
    max_rows: int
    allow_ai_access: bool
    require_approval: bool
    audit_all: bool
    recommendations: List[str]


class QueryAnalysisRequest(BaseModel):
    """Request to analyze a SQL query for risk"""
    query: str
    database: Optional[str] = None
    ai_agent: Optional[str] = None


class QueryAnalysisResponse(BaseModel):
    """Query risk analysis response"""
    query: str
    risk_score: int  # 0-100
    risk_level: str  # "low", "medium", "high"
    requires_approval: bool
    reason: str
    patterns_detected: List[str]
    timestamp: str


# Sensitive patterns database
SENSITIVE_PATTERNS = {
    # SECRETS
    "password": ("secret", 0.95),
    "api_key": ("secret", 0.95),
    "apikey": ("secret", 0.95),
    "secret": ("secret", 0.95),
    "token": ("secret", 0.85),
    "private_key": ("secret", 0.95),
    "access_key": ("secret", 0.9),
    "aws_key": ("secret", 0.95),
    
    # PII
    "email": ("pii", 0.9),
    "phone": ("pii", 0.9),
    "ssn": ("pii", 0.95),
    "social_security": ("pii", 0.95),
    "firstname": ("pii", 0.7),
    "lastname": ("pii", 0.7),
    "address": ("pii", 0.8),
    "dob": ("pii", 0.85),
    "date_of_birth": ("pii", 0.9),
    "customer_id": ("pii", 0.6),
    "user_id": ("pii", 0.6),
    
    # FINANCIAL
    "credit_card": ("financial", 0.95),
    "card_number": ("financial", 0.95),
    "cvv": ("financial", 0.95),
    "bank_account": ("financial", 0.95),
    "routing_number": ("financial", 0.9),
    "salary": ("financial", 0.8),
    "income": ("financial", 0.8),
    "transaction": ("financial", 0.6),
    
    # HEALTH
    "medical": ("health", 0.85),
    "health": ("health", 0.8),
    "diagnosis": ("health", 0.9),
    "prescription": ("health", 0.9),
    "allergy": ("health", 0.85),
    "medication": ("health", 0.85),
}


# Risk scoring logic for SQL queries

RISKY_SQL_PATTERNS = {
    # Destructive operations (90+ risk)
    "DROP TABLE": 95,
    "DROP DATABASE": 100,
    "TRUNCATE": 90,
    
    # Delete operations (80+ risk)
    "DELETE FROM": 85,
    "DELETE ": 80,
    
    # Alter/modify operations (60-70 risk)
    "ALTER TABLE": 70,
    "ALTER DATABASE": 75,
    "UPDATE": 65,
    
    # Safe operations (10-20 risk)
    "SELECT": 10,
    "INSERT INTO": 15,
}


def calculate_query_risk_score(query: str) -> tuple[int, str, bool, str, List[str]]:
    """
    Calculate risk score for a SQL query.
    
    Returns:
        (risk_score, risk_level, requires_approval, reason, patterns_detected)
    """
    if not query:
        return 0, "low", False, "Empty query", []
    
    query_upper = query.upper().strip()
    detected_patterns = []
    max_risk_score = 0
    primary_reason = ""
    
    # Check for risky patterns
    for pattern, risk_score in RISKY_SQL_PATTERNS.items():
        if pattern in query_upper:
            detected_patterns.append(pattern.lower())
            if risk_score > max_risk_score:
                max_risk_score = risk_score
                primary_reason = f"{pattern.lower()} operation detected"
    
    # Additional checks
    # UPDATE without WHERE is very risky
    if "UPDATE" in query_upper and "WHERE" not in query_upper:
        max_risk_score = max(max_risk_score, 85)
        if "UPDATE without WHERE" not in detected_patterns:
            detected_patterns.append("update without where clause")
        primary_reason = "UPDATE operation without WHERE clause - will modify all rows"
    
    # DELETE without WHERE is very risky
    if "DELETE" in query_upper and "WHERE" not in query_upper:
        max_risk_score = max(max_risk_score, 95)
        if "DELETE without WHERE" not in detected_patterns:
            detected_patterns.append("delete without where clause")
        primary_reason = "DELETE operation without WHERE clause - will delete all rows"
    
    # Determine risk level
    if max_risk_score >= 71:
        risk_level = "high"
        requires_approval = True
    elif max_risk_score >= 41:
        risk_level = "medium"
        requires_approval = False
    else:
        risk_level = "low"
        requires_approval = False
    
    if not primary_reason:
        primary_reason = f"SQL query with risk score {max_risk_score}/100"
    
    return max_risk_score, risk_level, requires_approval, primary_reason, detected_patterns


# Endpoints

@router.post("/scan", response_model=ScanResponse)
async def scan_database_schema(request: ScanRequest):
    """
    Scan a database schema for sensitive data.
    
    Analyzes column names and table names against patterns for:
    - SECRETS (passwords, tokens, API keys)
    - PII (emails, phone numbers, SSNs)
    - FINANCIAL (credit cards, bank accounts)
    - HEALTH (medical records, allergies)
    
    Args:
        connector_name: Name of the database connector
        schema_info: Database schema information
    
    Returns:
        Scan results with findings organized by type and table
    """
    try:
        from datetime import datetime
        
        findings_by_type = {"secret": [], "pii": [], "financial": [], "health": []}
        findings_by_table = {}
        
        for table_info in request.schema_info:
            table_name = table_info.get("table_name", "unknown")
            columns = table_info.get("columns", [])
            table_findings = []
            
            for column in columns:
                col_name = column.lower() if isinstance(column, str) else str(column).lower()
                
                for pattern, (category, confidence) in SENSITIVE_PATTERNS.items():
                    if pattern in col_name:
                        finding = {
                            "column": column,
                            "pattern": pattern,
                            "category": category,
                            "confidence": confidence,
                        }
                        findings_by_type[category].append(finding)
                        table_findings.append(finding)
                        break
            
            if table_findings:
                findings_by_table[table_name] = table_findings
        
        # Calculate risk summary
        risk_summary = {
            cat: len(findings_by_type[cat]) for cat in findings_by_type
        }
        
        return ScanResponse(
            timestamp=datetime.utcnow().isoformat(),
            connector_name=request.connector_name,
            total_findings=sum(len(v) for v in findings_by_type.values()),
            by_type=findings_by_type,
            risk_summary=risk_summary,
            by_table=findings_by_table,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Scan failed: {str(e)}"
        )


@router.post("/analyze-query", response_model=QueryAnalysisResponse)
async def analyze_query_risk(request: QueryAnalysisRequest):
    """
    Analyze a SQL query for risk and governance requirements.
    
    Detects destructive SQL patterns and calculates risk score:
    - 0-40: Low risk (SELECT, safe INSERT)
    - 41-70: Medium risk (UPDATE, ALTER operations)
    - 71-100: High risk (DELETE, DROP, TRUNCATE)
    
    High-risk queries require human approval in enterprise deployments.
    
    Args:
        query: SQL query to analyze
        database: Optional database name for audit logging
        ai_agent: Optional AI agent name for audit logging
    
    Returns:
        Risk analysis with score, level, and approval requirement
    """
    try:
        from datetime import datetime
        
        risk_score, risk_level, requires_approval, reason, patterns = calculate_query_risk_score(
            request.query
        )
        
        return QueryAnalysisResponse(
            query=request.query,
            risk_score=risk_score,
            risk_level=risk_level,
            requires_approval=requires_approval,
            reason=reason,
            patterns_detected=patterns,
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Query analysis failed: {str(e)}"
        )


@router.post("/generate-policy", response_model=PolicyGenerationResponse)
async def generate_security_policy(request: PolicyGenerationRequest):
    """
    Generate a security policy from scan results.
    
    Creates an automatic security policy based on detected sensitive data:
    - High confidence secrets → Block table, require approval
    - PII columns → Mask, audit all access
    - Financial columns → Restrict, AI requires approval
    - Health data → HIPAA-level protection
    
    Args:
        connector_name: Name of the database connector
        scan_results: Results from /scan endpoint
    
    Returns:
        Generated security policy
    """
    try:
        mask_columns = []
        deny_columns = []
        deny_tables = []
        
        # Analyze scan results
        by_type = request.scan_results.get("by_type", {})
        
        for secret in by_type.get("secret", []):
            deny_columns.append(secret.get("column"))
        
        for pii in by_type.get("pii", []):
            mask_columns.append(pii.get("column"))
        
        for financial in by_type.get("financial", []):
            if financial.get("confidence", 0) > 0.9:
                deny_tables.append(financial.get("table"))
            else:
                mask_columns.append(financial.get("column"))
        
        for health in by_type.get("health", []):
            deny_columns.append(health.get("column"))
        
        return PolicyGenerationResponse(
            policy_name=f"auto-policy-{request.connector_name}",
            description=f"Auto-generated security policy for {request.connector_name}",
            mask_columns=list(set(mask_columns)),
            deny_tables=list(set(deny_tables)),
            deny_columns=list(set(deny_columns)),
            max_rows=1000,
            allow_ai_access=len(deny_columns) == 0,
            require_approval=len(deny_tables) > 0,
            audit_all=True,
            recommendations=[
                "Review auto-generated policy before applying",
                "Consider custom thresholds for your data",
                "Test policy on non-production data first",
            ],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Policy generation failed: {str(e)}"
        )


@router.post("/generate-mask-map")
async def generate_mask_mapping(request: PolicyGenerationRequest):
    """
    Generate column masking specifications.
    
    Creates detailed masking instructions for each sensitive column:
    - email → Partial mask (show domain)
    - phone → Partial mask (show last 4 digits)
    - SSN → Partial mask (show last 4 digits)
    - Card number → Mask all digits
    - Passwords → Complete masking (never shown)
    
    Args:
        connector_name: Name of the database connector
        scan_results: Results from /scan endpoint
    
    Returns:
        Mapping of columns to masking strategies
    """
    try:
        mask_map = {}
        
        by_type = request.scan_results.get("by_type", {})
        
        for secret in by_type.get("secret", []):
            mask_map[secret.get("column")] = "complete_mask"
        
        for pii in by_type.get("pii", []):
            col = pii.get("column", "").lower()
            if "email" in col:
                mask_map[pii.get("column")] = "mask_email"
            elif "phone" in col:
                mask_map[pii.get("column")] = "mask_phone"
            elif "ssn" in col:
                mask_map[pii.get("column")] = "mask_ssn"
            else:
                mask_map[pii.get("column")] = "partial_mask"
        
        for financial in by_type.get("financial", []):
            col = financial.get("column", "").lower()
            if "card" in col:
                mask_map[financial.get("column")] = "mask_card"
            else:
                mask_map[financial.get("column")] = "partial_mask"
        
        return {"mask_map": mask_map}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Mask mapping failed: {str(e)}"
        )


@router.get("/patterns")
async def get_sensitive_patterns():
    """
    Get all sensitive patterns used by the scanner.
    
    Useful for understanding what the scanner detects and customizing
    sensitivity threshold for specific databases.
    
    Returns:
        Organized list of all patterns by sensitivity type
    """
    patterns_by_type = {
        "secret": [],
        "pii": [],
        "financial": [],
        "health": [],
    }

    for pattern, (category, confidence) in SENSITIVE_PATTERNS.items():
        patterns_by_type[category].append({
            "pattern": pattern,
            "confidence": confidence,
        })

    # Sort by confidence
    for category in patterns_by_type:
        patterns_by_type[category].sort(
            key=lambda x: x["confidence"], reverse=True
        )

    return {
        "patterns": patterns_by_type,
        "total_patterns": len(SENSITIVE_PATTERNS),
        "categories": list(patterns_by_type.keys()),
    }


@router.get("/health")
async def scanner_health():
    """Health check for scanner service"""
    return {
        "service": "sensitivity-scanner",
        "status": "operational",
        "version": "1.0",
    }
