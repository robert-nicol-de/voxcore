"""Tenant middleware for multi-tenant request handling."""

import logging
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to identify and validate tenant in requests.
    
    Tenant identification methods (in order of priority):
    1. X-Tenant-ID header
    2. Query parameter ?tenant=...
    3. Subdomain (tenant.voxcore.local)
    4. Default to "default"
    """
    
    async def dispatch(self, request: Request, call_next):
        tenant_id = await self._extract_tenant_id(request)
        
        # Store tenant_id in request state for access in endpoints
        request.state.tenant_id = tenant_id
        
        response = await call_next(request)
        
        # Add tenant ID to response headers for transparency
        response.headers["X-Tenant-ID"] = tenant_id
        
        return response
    
    async def _extract_tenant_id(self, request: Request) -> str:
        """
        Extract tenant ID from request.
        
        Priority:
        1. X-Tenant-ID header
        2. tenant query parameter
        3. Subdomain
        4. Default
        """
        
        # Method 1: Check X-Tenant-ID header
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            logger.debug(f"Tenant identified via X-Tenant-ID header: {tenant_id}")
            return tenant_id
        
        # Method 2: Check query parameter
        tenant_id = request.query_params.get("tenant")
        if tenant_id:
            logger.debug(f"Tenant identified via query parameter: {tenant_id}")
            return tenant_id
        
        # Method 3: Check subdomain
        # Example: tenant-acme.voxcore.com -> tenant_acme
        host = request.headers.get("host", "localhost")
        if "." in host and not host.startswith("localhost"):
            subdomain = host.split(".")[0]
            if subdomain and subdomain != "www":
                tenant_id = f"tenant_{subdomain.replace('-', '_')}"
                logger.debug(f"Tenant identified via subdomain: {tenant_id}")
                return tenant_id
        
        # Method 4: Default
        logger.debug("Using default tenant")
        return "default"


def get_tenant_id(request: Request) -> str:
    """Get tenant ID from request state."""
    return getattr(request.state, "tenant_id", "default")


class TenantIsolationError(HTTPException):
    """Raised when tenant isolation violation is detected."""
    
    def __init__(self, message: str = "Tenant isolation violation"):
        super().__init__(status_code=403, detail=message)


def validate_tenant_ownership(
    requested_tenant: str,
    resource_tenant: str,
    resource_name: str = "resource"
) -> None:
    """
    Validate that requested tenant owns the resource.
    
    Args:
        requested_tenant: The tenant making the request
        resource_tenant: The tenant that owns the resource
        resource_name: Name of resource for error messages
    
    Raises:
        TenantIsolationError: If tenant doesn't own the resource
    """
    if requested_tenant != resource_tenant:
        logger.warning(
            f"Tenant isolation violation: {requested_tenant} attempted to access "
            f"{resource_name} owned by {resource_tenant}"
        )
        raise TenantIsolationError(
            f"Access denied: {resource_name} belongs to different tenant"
        )
