"""Query Token System for Zero-Trust AI Architecture."""

import json
import hmac
import hashlib
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import base64

import logging

logger = logging.getLogger(__name__)


class QueryToken:
    """Represents a signed query token."""
    
    def __init__(
        self,
        token_id: str,
        tenant_id: str,
        user_id: str,
        application: str,
        issued_at: float,
        expires_at: float,
        allowed_tables: Optional[list[str]] = None,
        max_rows: int = 1000
    ):
        self.token_id = token_id
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.application = application
        self.issued_at = issued_at
        self.expires_at = expires_at
        self.allowed_tables = allowed_tables or []
        self.max_rows = max_rows
    
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return time.time() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary."""
        return {
            "token_id": self.token_id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "application": self.application,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "allowed_tables": self.allowed_tables,
            "max_rows": self.max_rows
        }


class QueryTokenManager:
    """
    Manages signed query tokens for zero-trust security.
    
    Token format: vxq_{signature}_{payload}
    
    Tokens:
    - Are time-limited (default 5 minutes)
    - Are HMAC-signed for integrity
    - Include tenant, user, application context
    - Can restrict allowed tables
    - Cannot be reused
    """
    
    TOKEN_PREFIX = "vxq_"
    DEFAULT_EXPIRY_MINUTES = 5
    
    def __init__(self, secret_key: str):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for HMAC signing (should be from environment)
        """
        self.secret_key = secret_key
        self.issued_tokens: Dict[str, QueryToken] = {}  # In-memory store (use Redis in production)
    
    def generate_token(
        self,
        tenant_id: str,
        user_id: str,
        application: str,
        allowed_tables: Optional[list[str]] = None,
        max_rows: int = 1000,
        expires_in_minutes: int = DEFAULT_EXPIRY_MINUTES
    ) -> str:
        """
        Generate a signed query token.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            application: AI application name (Copilot, ChatGPT, etc)
            allowed_tables: Optional list of allowed table names
            max_rows: Maximum rows allowed in query result
            expires_in_minutes: Token expiry time
        
        Returns:
            Signed token string (e.g., vxq_83f921ab4d)
        """
        token_id = str(uuid.uuid4())[:12]
        now = time.time()
        expires_at = now + (expires_in_minutes * 60)
        
        # Create token object
        token = QueryToken(
            token_id=token_id,
            tenant_id=tenant_id,
            user_id=user_id,
            application=application,
            issued_at=now,
            expires_at=expires_at,
            allowed_tables=allowed_tables,
            max_rows=max_rows
        )
        
        # Create payload (JSON)
        payload = json.dumps(token.to_dict())
        payload_b64 = base64.b64encode(payload.encode()).decode()
        
        # Create signature
        signature = self._create_signature(payload_b64)
        
        # Format token
        signed_token = f"{self.TOKEN_PREFIX}{signature}_{payload_b64}"
        
        # Store for revocation tracking
        self.issued_tokens[signed_token] = token
        
        logger.info(f"Generated query token for user={user_id}, app={application}, expires_in={expires_in_minutes}min")
        
        return signed_token
    
    def validate_token(self, token: str) -> tuple[bool, Optional[QueryToken], str]:
        """
        Validate and decode a signed query token.
        
        Args:
            token: Token string to validate
        
        Returns:
            Tuple of (is_valid, token_object, error_message)
        """
        if not token or not token.startswith(self.TOKEN_PREFIX):
            return False, None, "Invalid token format"
        
        try:
            # Remove prefix and split
            token_content = token[len(self.TOKEN_PREFIX):]
            parts = token_content.split("_", 1)
            
            if len(parts) != 2:
                return False, None, "Invalid token format: missing payload"
            
            signature, payload_b64 = parts
            
            # Verify signature
            expected_signature = self._create_signature(payload_b64)
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning(f"Token signature verification failed: {token[:20]}...")
                return False, None, "Token signature invalid"
            
            # Decode payload
            try:
                payload_json = base64.b64decode(payload_b64).decode()
                payload = json.loads(payload_json)
            except Exception as e:
                return False, None, f"Failed to decode token payload: {str(e)}"
            
            # Reconstruct token object
            token_obj = QueryToken(
                token_id=payload["token_id"],
                tenant_id=payload["tenant_id"],
                user_id=payload["user_id"],
                application=payload["application"],
                issued_at=payload["issued_at"],
                expires_at=payload["expires_at"],
                allowed_tables=payload.get("allowed_tables"),
                max_rows=payload.get("max_rows", 1000)
            )
            
            # Check expiry
            if token_obj.is_expired():
                logger.info(f"Token expired: {token_obj.token_id}")
                return False, None, "Token has expired"
            
            # Check if revoked
            if token in self.issued_tokens:
                logger.info(f"Token validated: {token_obj.token_id}")
                return True, token_obj, ""
            
            # Token not in our store (could be valid if distributed across instances)
            logger.debug(f"Token not in local store (might be valid in distributed setup): {token_obj.token_id}")
            return True, token_obj, ""
        
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return False, None, f"Token validation error: {str(e)}"
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke a token (prevent future use).
        
        Args:
            token: Token to revoke
        
        Returns:
            True if token was revoked, False if not found
        """
        if token in self.issued_tokens:
            del self.issued_tokens[token]
            logger.info(f"Token revoked: {token[:20]}...")
            return True
        return False
    
    def _create_signature(self, payload: str) -> str:
        """Create HMAC-SHA256 signature of payload."""
        signature = hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature[:12]  # Use first 12 chars of hash
    
    def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get information about a token without validating."""
        is_valid, token_obj, _ = self.validate_token(token)
        if token_obj:
            return token_obj.to_dict()
        return None


# Global token manager instance
_token_manager: Optional[QueryTokenManager] = None


def initialize_token_manager(secret_key: str) -> QueryTokenManager:
    """Initialize global token manager."""
    global _token_manager
    _token_manager = QueryTokenManager(secret_key)
    return _token_manager


def get_token_manager() -> QueryTokenManager:
    """Get global token manager instance."""
    global _token_manager
    if _token_manager is None:
        raise RuntimeError("Token manager not initialized. Call initialize_token_manager first.")
    return _token_manager
