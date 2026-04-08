"""
TenantContext - Multi-Tenant Isolation and Context Management

Ensures every operation is tagged with the current organization (tenant).
No cross-tenant data leakage.

Usage:
  with tenant_context(org_id="acme_corp", user_id="user_123"):
      result = query_service.execute(sql)  # Automatically isolated to acme_corp
"""

import contextvars
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

# Context variables (thread-safe, async-safe)
_current_org_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "org_id", default=None
)
_current_user_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "user_id", default=None
)
_current_workspace_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "workspace_id", default=None
)
_current_session_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "session_id", default=None
)


@dataclass
class TenantContext:
    """Immutable tenant context for current request/operation"""

    org_id: str  # REQUIRED: Organization ID (primary tenant key)
    user_id: Optional[str] = None  # User within the org
    workspace_id: Optional[str] = None  # Workspace within the org
    session_id: Optional[str] = None  # Session ID for tracking
    created_at: datetime = None

    def __post_init__(self):
        if not self.org_id:
            raise ValueError("org_id is required - cannot execute without tenant context")
        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for logging/auditing"""
        return {
            "org_id": self.org_id,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
        }

    def validate(self) -> bool:
        """Validate context is properly initialized"""
        return bool(self.org_id)


def get_current_context() -> Optional[TenantContext]:
    """Get the current tenant context (None if not set)"""
    org_id = _current_org_id.get()
    if not org_id:
        return None

    return TenantContext(
        org_id=org_id,
        user_id=_current_user_id.get(),
        workspace_id=_current_workspace_id.get(),
        session_id=_current_session_id.get(),
    )


def require_context() -> TenantContext:
    """Get the current context, raise if not set"""
    ctx = get_current_context()
    if not ctx:
        raise RuntimeError(
            "Tenant context not set. Use set_context() or tenant_context() first."
        )
    return ctx


def set_context(
    org_id: str,
    user_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> TenantContext:
    """
    Set the current tenant context.

    IMPORTANT: Call at start of request to initialize tenant isolation.

    Args:
        org_id: Organization ID (required)
        user_id: User ID within org (optional)
        workspace_id: Workspace ID within org (optional)
        session_id: Session ID for tracking (optional)

    Returns:
        TenantContext object

    Raises:
        ValueError: If org_id is empty
    """
    if not org_id:
        raise ValueError("org_id is required")

    _current_org_id.set(org_id)
    _current_user_id.set(user_id)
    _current_workspace_id.set(workspace_id)
    _current_session_id.set(session_id)

    return get_current_context()


def clear_context():
    """Clear tenant context (for cleanup between requests)"""
    _current_org_id.set(None)
    _current_user_id.set(None)
    _current_workspace_id.set(None)
    _current_session_id.set(None)


class tenant_context:
    """
    Context manager for tenant isolation.

    Usage:
        with tenant_context(org_id="acme_corp", user_id="john@acme.com"):
            result = query_service.execute(sql)  # Automatically isolated
    """

    def __init__(
        self,
        org_id: str,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        if not org_id:
            raise ValueError("org_id is required for tenant_context")

        self.org_id = org_id
        self.user_id = user_id
        self.workspace_id = workspace_id
        self.session_id = session_id

        # Save previous context to restore later
        self._previous_org_id = None
        self._previous_user_id = None
        self._previous_workspace_id = None
        self._previous_session_id = None

    def __enter__(self) -> TenantContext:
        """Enter context: set tenant info"""
        # Save previous values
        self._previous_org_id = _current_org_id.get()
        self._previous_user_id = _current_user_id.get()
        self._previous_workspace_id = _current_workspace_id.get()
        self._previous_session_id = _current_session_id.get()

        # Set new values
        return set_context(
            org_id=self.org_id,
            user_id=self.user_id,
            workspace_id=self.workspace_id,
            session_id=self.session_id,
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context: restore previous tenant info"""
        _current_org_id.set(self._previous_org_id)
        _current_user_id.set(self._previous_user_id)
        _current_workspace_id.set(self._previous_workspace_id)
        _current_session_id.set(self._previous_session_id)

        return False  # Don't suppress exceptions


def get_org_id() -> str:
    """Get current org_id (required for all operations)"""
    org_id = _current_org_id.get()
    if not org_id:
        raise RuntimeError(
            "No tenant context set. Call set_context() or use tenant_context() first."
        )
    return org_id


def get_user_id() -> Optional[str]:
    """Get current user_id (may be None)"""
    return _current_user_id.get()


def get_workspace_id() -> Optional[str]:
    """Get current workspace_id (may be None)"""
    return _current_workspace_id.get()


def get_session_id() -> Optional[str]:
    """Get current session_id (may be None)"""
    return _current_session_id.get()
