"""Database connector management endpoints."""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .models import get_db
from ..connector_manager import (
    load_connectors,
    get_connector_by_name,
    get_connector_count,
    load_tenant_config,
    list_all_tenants,
    get_tenant_user,
)
from ..policy_enforcer import load_policy_enforcer, QueryViolation
from ..query_token import get_token_manager, initialize_token_manager

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Pydantic schemas ──────────────────────────────────────────────

class ConnectorDatabase(BaseModel):
    """Database connection details from .ini file"""
    name: str
    type: str  # postgres, mysql, mssql, etc
    host: str
    port: int
    database: str
    user: str
    password: Optional[str] = None  # Masked in responses


class ConnectorSecurity(BaseModel):
    """Security policies for database connector"""
    block_delete: bool = False
    block_update: bool = False
    block_drop: bool = False
    max_rows: int = 1000
    protect_tables: List[str] = []
    pii_protected: bool = False
    policy: Optional[str] = None  # strict, moderate, permissive


class ConnectorResponse(BaseModel):
    """Full connector response with database + security details"""
    name: str
    database: ConnectorDatabase
    security: ConnectorSecurity
    status: str = "available"  # available, testing, connected, error
    credential_status: Optional[str] = None  # loaded, not_found, missing
    tenant_id: Optional[str] = None


class ConnectorsListResponse(BaseModel):
    """List of all available connectors"""
    total: int
    connectors: List[ConnectorResponse]
    tenant_id: Optional[str] = None


class TenantUser(BaseModel):
    """Tenant user information"""
    id: str
    email: str
    name: str
    role: str  # admin, developer, viewer


class TenantConfig(BaseModel):
    """Tenant configuration"""
    tenant_id: str
    company_name: str
    subscription_plan: str
    created_at: str
    users: List[TenantUser]


# ── Zero-Trust Query Validation ──────────────────────────────────────────────

class QueryValidationRequest(BaseModel):
    """Request to validate a query against zero-trust policies."""
    query: str
    application: str  # Copilot, ChatGPT, custom_app, etc
    user_id: str
    role: str = "developer"  # admin, developer, viewer
    query_token: Optional[str] = None


class QueryViolationResponse(BaseModel):
    """Single policy violation."""
    type: str  # DENIED_TABLE, PII_ACCESS, etc
    message: str
    table: Optional[str] = None
    column: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class QueryValidationResponse(BaseModel):
    """Result of query validation."""
    is_valid: bool
    query: str
    violations: List[QueryViolationResponse] = []
    tenant_id: Optional[str] = None
    message: str = "Query passed validation"


class QueryTokenRequest(BaseModel):
    """Request to generate a query token."""
    application: str
    user_id: str
    allowed_tables: Optional[List[str]] = None
    max_rows: int = 1000
    expires_in_minutes: int = 5


class QueryTokenResponse(BaseModel):
    """Generated query token."""
    token: str
    token_id: str
    expires_at: float
    application: str
    tenant_id: str


@router.post("/zero-trust/validate-query")
def validate_query(
    request: QueryValidationRequest,
    db: Session = Depends(get_db),
    x_tenant_id: Optional[str] = Header(None)
) -> QueryValidationResponse:
    """
    Validate a query against zero-trust policies.
    
    Returns:
    - is_valid: true if query passes all security checks
    - violations: list of policy violations (if any)
    """
    try:
        tenant_id = x_tenant_id or "default"
        
        # Load tenant policies
        tenant_config = load_tenant_config(tenant_id)
        if not tenant_config:
            raise HTTPException(
                status_code=404,
                detail=f"Tenant '{tenant_id}' not found"
            )
        
        # Get policy enforcer
        policies_dict = tenant_config.get("policies", {})
        enforcer = load_policy_enforcer(policies_dict)
        
        if not enforcer:
            # If no zero-trust policy, allow query
            return QueryValidationResponse(
                is_valid=True,
                query=request.query,
                tenant_id=tenant_id,
                message="No zero-trust policy configured"
            )
        
        # Create request context
        context = {
            "tenant_id": tenant_id,
            "user_id": request.user_id,
            "application": request.application,
            "role": request.role,
            "query_token": request.query_token
        }
        
        # Validate query
        is_valid, violations = enforcer.validate_query(request.query, context)
        
        # Convert violations to response objects
        violation_responses = [
            QueryViolationResponse(
                type=v.violation_type.value,
                message=v.message,
                table=v.table,
                column=v.column,
                details=v.details
            )
            for v in violations
        ]
        
        message = "Query passed validation" if is_valid else f"Query blocked: {len(violations)} policy violation(s)"
        
        return QueryValidationResponse(
            is_valid=is_valid,
            query=request.query,
            violations=violation_responses,
            tenant_id=tenant_id,
            message=message
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error validating query: {str(e)}"
        )


@router.post("/zero-trust/generate-token")
def generate_query_token(
    request: QueryTokenRequest,
    x_tenant_id: Optional[str] = Header(None)
) -> QueryTokenResponse:
    """
    Generate a signed query token for zero-trust execution.
    
    Token is valid for:
    - Specific tenant
    - Specific application
    - Specific user
    - Limited time (expires_in_minutes)
    - Optional table restrictions
    """
    try:
        tenant_id = x_tenant_id or "default"
        
        # Get or initialize token manager
        try:
            token_manager = get_token_manager()
        except RuntimeError:
            # Initialize with default secret (should come from environment in production)
            import os
            secret = os.getenv("VOXCORE_TOKEN_SECRET", "default_secret_change_me")
            token_manager = initialize_token_manager(secret)
        
        # Generate token
        token = token_manager.generate_token(
            tenant_id=tenant_id,
            user_id=request.user_id,
            application=request.application,
            allowed_tables=request.allowed_tables,
            max_rows=request.max_rows,
            expires_in_minutes=request.expires_in_minutes
        )
        
        # Get token info
        info = token_manager.get_token_info(token)
        
        return QueryTokenResponse(
            token=token,
            token_id=info["token_id"],
            expires_at=info["expires_at"],
            application=request.application,
            tenant_id=tenant_id
        )
    
    except Exception as e:
        logger.error(f"Error generating token: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating token: {str(e)}"
        )


@router.post("/zero-trust/validate-token")
def validate_query_token(
    token: str,
    x_tenant_id: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Validate a query token and return its information.
    """
    try:
        try:
            token_manager = get_token_manager()
        except RuntimeError:
            import os
            secret = os.getenv("VOXCORE_TOKEN_SECRET", "default_secret_change_me")
            token_manager = initialize_token_manager(secret)
        
        is_valid, token_obj, error = token_manager.validate_token(token)
        
        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail=f"Token validation failed: {error}"
            )
        
        return {
            "is_valid": True,
            "token_id": token_obj.token_id,
            "tenant_id": token_obj.tenant_id,
            "user_id": token_obj.user_id,
            "application": token_obj.application,
            "expires_at": token_obj.expires_at,
            "allowed_tables": token_obj.allowed_tables,
            "max_rows": token_obj.max_rows
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error validating token: {str(e)}"
        )



# ── API Endpoints ──────────────────────────────────────────────

@router.get("/connectors")
def list_connectors(
    db: Session = Depends(get_db),
    x_tenant_id: Optional[str] = Header(None)
) -> ConnectorsListResponse:
    """Get list of all available database connectors for a tenant."""
    try:
        # Load connectors for the specified tenant (or default)
        connector_list = load_connectors(tenant_id=x_tenant_id)
        
        # Convert to response format (hide passwords)
        responses = []
        for connector in connector_list:
            # Build database section (never include password)
            db_section = ConnectorDatabase(
                name=connector.get("name", "unknown"),
                type=connector.get("type", "unknown"),
                host=connector.get("host", ""),
                port=connector.get("port", 5432),
                database=connector.get("database", ""),
                user=connector.get("user", ""),
                password=None  # Never send passwords to frontend
            )
            
            # Build security section
            sec_config = connector.get("security", {})
            sec_section = ConnectorSecurity(
                block_delete=sec_config.get("block_delete", False),
                block_update=sec_config.get("block_update", False),
                block_drop=sec_config.get("block_drop", False),
                max_rows=sec_config.get("max_rows", 1000),
                protect_tables=sec_config.get("protect_tables", []),
                pii_protected=sec_config.get("pii_protected", False),
                policy=sec_config.get("policy")
            )
            
            # Build full connector response
            connector_response = ConnectorResponse(
                name=connector.get("name", "unknown"),
                database=db_section,
                security=sec_section,
                status=connector.get("status", "available"),
                credential_status=connector.get("credential_status"),
                tenant_id=connector.get("tenant_id")
            )
            responses.append(connector_response)
        
        return ConnectorsListResponse(
            total=len(responses),
            connectors=responses,
            tenant_id=x_tenant_id or "default"
        )
    
    except Exception as e:
        logger.error(f"Error loading connectors: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading connectors: {str(e)}"
        )


@router.get("/connectors/{connector_name}")
def get_connector(
    connector_name: str,
    db: Session = Depends(get_db),
    x_tenant_id: Optional[str] = Header(None)
) -> ConnectorResponse:
    """Get details for a specific database connector."""
    try:
        # Load all connectors and find the one matching name
        connector_list = load_connectors(tenant_id=x_tenant_id)
        connector = next((c for c in connector_list if c.get("name") == connector_name), None)
        
        if not connector:
            raise HTTPException(
                status_code=404,
                detail=f"Connector '{connector_name}' not found for tenant '{x_tenant_id or 'default'}'"
            )
        
        # Build database section (never include password)
        db_section = ConnectorDatabase(
            name=connector.get("name", "unknown"),
            type=connector.get("type", "unknown"),
            host=connector.get("host", ""),
            port=connector.get("port", 5432),
            database=connector.get("database", ""),
            user=connector.get("user", ""),
            password=None  # Never send passwords to frontend
        )
        
        # Build security section
        sec_config = connector.get("security", {})
        sec_section = ConnectorSecurity(
            block_delete=sec_config.get("block_delete", False),
            block_update=sec_config.get("block_update", False),
            block_drop=sec_config.get("block_drop", False),
            max_rows=sec_config.get("max_rows", 1000),
            protect_tables=sec_config.get("protect_tables", []),
            pii_protected=sec_config.get("pii_protected", False),
            policy=sec_config.get("policy")
        )
        
        return ConnectorResponse(
            name=connector.get("name", "unknown"),
            database=db_section,
            security=sec_section,
            status=connector.get("status", "available"),
            credential_status=connector.get("credential_status"),
            tenant_id=connector.get("tenant_id")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting connector '{connector_name}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting connector: {str(e)}"
        )


@router.get("/tenants")
def list_tenants() -> Dict[str, Any]:
    """List all available tenants."""
    try:
        tenants = list_all_tenants()
        return {
            "total": len(tenants),
            "tenants": tenants
        }
    except Exception as e:
        logger.error(f"Error listing tenants: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing tenants: {str(e)}"
        )


@router.get("/tenants/{tenant_id}/config")
def get_tenant_config(tenant_id: str) -> Dict[str, Any]:
    """Get configuration for a specific tenant."""
    try:
        config = load_tenant_config(tenant_id)
        if not config:
            raise HTTPException(
                status_code=404,
                detail=f"Tenant '{tenant_id}' not found"
            )
        return config
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tenant config: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting tenant config: {str(e)}"
        )


@router.get("/connectors/stats/count")
def connector_count(
    db: Session = Depends(get_db),
    x_tenant_id: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """Get total count of available connectors for a tenant."""
    try:
        connectors = load_connectors(tenant_id=x_tenant_id)
        return {
            "total_connectors": len(connectors),
            "tenant_id": x_tenant_id or "default",
            "status": "ok"
        }
    except Exception as e:
        logger.error(f"Error getting connector count: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting connector count: {str(e)}"
        )

