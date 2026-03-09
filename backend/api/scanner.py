"""
Data Sensitivity Scanner API Routes

Provides endpoints for scanning database schemas and generating security policies.

Author: VoxCore
Date: March 2026
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path to import scanner modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sensitivity_scanner import SensitivityScanner
from policy_generator import PolicyGenerator


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
        scanner = SensitivityScanner()
        results = scanner.scan_schema(request.schema_info)

        return ScanResponse(
            timestamp=results["timestamp"],
            connector_name=request.connector_name,
            total_findings=results["total_findings"],
            by_type=results["by_type"],
            risk_summary=results["risk_summary"],
            by_table=results["by_table"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Scan failed: {str(e)}"
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
        generator = PolicyGenerator()
        policy = generator.generate_policy(request.scan_results, request.connector_name)

        return PolicyGenerationResponse(
            policy_name=policy.policy_name,
            description=policy.description,
            mask_columns=policy.mask_columns,
            deny_tables=policy.deny_tables,
            deny_columns=policy.deny_columns,
            max_rows=policy.max_rows,
            allow_ai_access=policy.allow_ai_access,
            require_approval=policy.require_approval,
            audit_all=policy.audit_all,
            recommendations=policy.recommendations,
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
        generator = PolicyGenerator()
        mask_map = generator.generate_mask_map(request.scan_results)
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
    scanner = SensitivityScanner()

    patterns_by_type = {
        "secret": [],
        "pii": [],
        "financial": [],
        "health": [],
    }

    for pattern, (category, confidence) in scanner.SENSITIVE_PATTERNS.items():
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
        "total_patterns": len(scanner.SENSITIVE_PATTERNS),
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
