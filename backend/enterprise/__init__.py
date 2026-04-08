"""
STEP 16 — ENTERPRISE READINESS LAYER

Complete enterprise security, compliance, and governance stack.

Includes:
1. Compliance Controls (SOC2 foundation)
2. Encryption (transit + rest)
3. Secrets Management (central)
4. Immutable Audit Logs (hash chaining)
5. Compliance Export (audit reports)
6. Data Classification (sensitivity framework)
7. Access Traceability (forensic logging)
8. Security Headers (browser protection)
9. Rate Limiting (abuse prevention)

Usage:
    from backend.enterprise import (
        get_controls_manager,
        get_encryption_service,
        get_secret_manager,
        get_audit_log,
        get_classification_framework,
        get_traceability_log,
        get_security_middleware
    )
"""

# Compliance Controls
from .compliance_controls import (
    ComplianceControlsManager,
    ComplianceControl,
    ControlCategory,
    get_controls_manager,
    verify_rbac_control,
    verify_encryption_control,
    verify_audit_logging
)

# Encryption
from .encryption_service import (
    EncryptionService,
    TransitEncryptionConfig,
    FieldEncryptionPolicy,
    get_encryption_service,
    encrypt_sensitive_value,
    decrypt_sensitive_value
)

# Secrets Management
from .secrets_manager import (
    SecretManager,
    LocalDevSecretManager,
    AWSSecretsManager,
    SecretManagerChain,
    SecretType,
    get_secret_manager,
    get_secret,
    store_secret,
    configure_aws_secrets_manager
)

# Immutable Audit Logs
from .immutable_audit_log import (
    ImmutableAuditLog,
    InMemoryAuditLog,
    AuditLogEntry,
    AuditEventType,
    get_audit_log,
    log_data_access,
    log_query_executed,
    log_auth_event
)

# Compliance Export
from .compliance_export import (
    ComplianceExporter,
    ComplianceExportRequest,
    ComplianceReportType,
    ExportFormat,
    generate_compliance_report
)

# Data Classification
from .data_classification import (
    DataClassification,
    DataCategory,
    DataClassificationPolicy,
    DataClassificationFramework,
    get_classification_framework,
    classify_field,
    should_mask,
    apply_masking
)

# Access Traceability
from .access_traceability import (
    AccessTraceabilityLog,
    AccessTraceabilityReport,
    DataAccessRecord,
    AccessResult,
    get_traceability_log,
    log_data_access as log_access
)

# Security Middleware
from .security_middleware import (
    SecurityHeadersMiddleware,
    RateLimiter,
    RateLimitConfig,
    SecurityMiddlewareStack,
    RateLimitStrategy,
    get_security_middleware
)

__all__ = [
    # Compliance Controls
    "ComplianceControlsManager",
    "ComplianceControl",
    "ControlCategory",
    "get_controls_manager",
    "verify_rbac_control",
    "verify_encryption_control",
    "verify_audit_logging",
    
    # Encryption
    "EncryptionService",
    "TransitEncryptionConfig",
    "FieldEncryptionPolicy",
    "get_encryption_service",
    "encrypt_sensitive_value",
    "decrypt_sensitive_value",
    
    # Secrets Management
    "SecretManager",
    "LocalDevSecretManager",
    "AWSSecretsManager",
    "SecretManagerChain",
    "SecretType",
    "get_secret_manager",
    "get_secret",
    "store_secret",
    "configure_aws_secrets_manager",
    
    # Immutable Audit Logs
    "ImmutableAuditLog",
    "InMemoryAuditLog",
    "AuditLogEntry",
    "AuditEventType",
    "get_audit_log",
    "log_data_access",
    "log_query_executed",
    "log_auth_event",
    
    # Compliance Export
    "ComplianceExporter",
    "ComplianceExportRequest",
    "ComplianceReportType",
    "ExportFormat",
    "generate_compliance_report",
    
    # Data Classification
    "DataClassification",
    "DataCategory",
    "DataClassificationPolicy",
    "DataClassificationFramework",
    "get_classification_framework",
    "classify_field",
    "should_mask",
    "apply_masking",
    
    # Access Traceability
    "AccessTraceabilityLog",
    "AccessTraceabilityReport",
    "DataAccessRecord",
    "AccessResult",
    "get_traceability_log",
    "log_access",
    
    # Security Middleware
    "SecurityHeadersMiddleware",
    "RateLimiter",
    "RateLimitConfig",
    "SecurityMiddlewareStack",
    "RateLimitStrategy",
    "get_security_middleware",
]
