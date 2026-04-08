"""
STEP 16.6 — DATA CLASSIFICATION (VERY IMPORTANT)

Classify all data by sensitivity to control:
- Access restrictions
- Encryption policies
- Masking rules
- Retention periods
- Export restrictions

Classifications:
- PUBLIC: No restrictions, visible in UI
- INTERNAL: Company proprietary, restricted to employees
- SENSITIVE: PII, health, financial - heavily restricted
- RESTRICTED: Highly sensitive, need-to-know only

Used by:
- Policy engine (what users can see)
- Masking engine (what to mask)
- Audit engine (what to log)
- Encryption engine (what to encrypt)
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set
from datetime import datetime, timedelta


class DataClassification(str, Enum):
    """Data sensitivity levels"""
    PUBLIC = "public"           # No restrictions
    INTERNAL = "internal"       # Company only
    SENSITIVE = "sensitive"     # PII, financial, health
    RESTRICTED = "restricted"   # Need-to-know only


class DataCategory(str, Enum):
    """Types of data"""
    PERSONAL_INFO = "personal"
    FINANCIAL = "financial"
    HEALTH = "health"
    CREDENTIALS = "credentials"
    AUDIT = "audit"
    SYSTEM = "system"
    BUSINESS = "business"


@dataclass
class DataClassificationPolicy:
    """Policy for classified data"""
    
    classification: DataClassification
    category: DataCategory
    
    # Access control
    requires_mfa: bool = False
    requires_approval: bool = False
    permitted_roles: List[str] = field(default_factory=list)
    
    # Protection
    must_encrypt: bool = False
    must_mask: bool = False
    mask_format: Optional[str] = None  # e.g., "XXX-XX-XXXX" for SSN
    
    # Retention
    retention_days: Optional[int] = None  # None = indefinite
    auto_delete: bool = False
    
    # Export
    allow_export: bool = False
    export_formats: List[str] = field(default_factory=list)
    
    # Audit
    audit_all_access: bool = True
    audit_modifications: bool = True
    
    def get_description(self) -> str:
        """Get human-readable description"""
        descriptions = {
            DataClassification.PUBLIC: "No access restrictions. Can be displayed publicly.",
            DataClassification.INTERNAL: "Restricted to authorized employees. Requires authentication.",
            DataClassification.SENSITIVE: "Highly restricted. Requires MFA and approved role. Must be encrypted and masked.",
            DataClassification.RESTRICTED: "Need-to-know only. Requires explicit approval and MFA."
        }
        return descriptions.get(self.classification, "Unknown")


class DataClassificationFramework:
    """Framework for classifying data across the system"""
    
    def __init__(self):
        self.field_classifications: Dict[str, DataClassificationPolicy] = {}
        self.table_classifications: Dict[str, DataClassification] = {}
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Initialize standard field classifications"""
        
        policies = {
            # Personal Information
            "email": DataClassificationPolicy(
                classification=DataClassification.SENSITIVE,
                category=DataCategory.PERSONAL_INFO,
                requires_mfa=True,
                must_mask=True,
                mask_format="***@***.***",
                permit_roles=["admin", "manager"],
                audit_all_access=True
            ),
            "phone": DataClassificationPolicy(
                classification=DataClassification.SENSITIVE,
                category=DataCategory.PERSONAL_INFO,
                requires_mfa=True,
                must_mask=True,
                mask_format="***-***-XXXX",
                permitted_roles=["admin", "manager"],
                audit_all_access=True
            ),
            "ssn": DataClassificationPolicy(
                classification=DataClassification.RESTRICTED,
                category=DataCategory.PERSONAL_INFO,
                requires_mfa=True,
                requires_approval=True,
                must_encrypt=True,
                must_mask=True,
                mask_format="XXX-XX-XXXX",
                audit_all_access=True,
                allow_export=False
            ),
            "date_of_birth": DataClassificationPolicy(
                classification=DataClassification.SENSITIVE,
                category=DataCategory.PERSONAL_INFO,
                requires_mfa=False,
                must_mask=True,
                mask_format="YYYY-01-01",
                permitted_roles=["admin", "hr", "manager"]
            ),
            
            # Financial
            "salary": DataClassificationPolicy(
                classification=DataClassification.RESTRICTED,
                category=DataCategory.FINANCIAL,
                requires_mfa=True,
                requires_approval=True,
                must_encrypt=True,
                must_mask=True,
                mask_format="$XXX,XXX",
                audit_all_access=True,
                allow_export=False
            ),
            "credit_card": DataClassificationPolicy(
                classification=DataClassification.RESTRICTED,
                category=DataCategory.FINANCIAL,
                requires_mfa=True,
                requires_approval=True,
                must_encrypt=True,
                must_mask=True,
                mask_format="XXXX-XXXX-XXXX-XXXX",
                audit_all_access=True,
                allow_export=False
            ),
            "revenue": DataClassificationPolicy(
                classification=DataClassification.INTERNAL,
                category=DataCategory.FINANCIAL,
                requires_mfa=False,
                must_encrypt=True,
                permitted_roles=["finance", "executive", "admin"]
            ),
            "cost": DataClassificationPolicy(
                classification=DataClassification.INTERNAL,
                category=DataCategory.FINANCIAL,
                requires_mfa=False,
                must_encrypt=True,
                permitted_roles=["finance", "executive", "admin"]
            ),
            
            # Health
            "medical_condition": DataClassificationPolicy(
                classification=DataClassification.RESTRICTED,
                category=DataCategory.HEALTH,
                requires_mfa=True,
                requires_approval=True,
                must_encrypt=True,
                must_mask=True,
                audit_all_access=True,
                allow_export=False
            ),
            
            # Credentials
            "password": DataClassificationPolicy(
                classification=DataClassification.RESTRICTED,
                category=DataCategory.CREDENTIALS,
                must_encrypt=True,
                must_mask=True,
                mask_format="***",
                audit_all_access=True,
                allow_export=False
            ),
            "api_key": DataClassificationPolicy(
                classification=DataClassification.RESTRICTED,
                category=DataCategory.CREDENTIALS,
                must_encrypt=True,
                must_mask=True,
                mask_format="***",
                audit_all_access=True,
                allow_export=False
            ),
            
            # Audit logs
            "audit_log": DataClassificationPolicy(
                classification=DataClassification.INTERNAL,
                category=DataCategory.AUDIT,
                retention_days=730,  # 2 years
                audit_all_access=True,
                audit_modifications=False,  # Don't audit audit log access
                allow_export=False
            ),
            
            # Default/Public
            "name": DataClassificationPolicy(
                classification=DataClassification.PUBLIC,
                category=DataCategory.PERSONAL_INFO,
                audit_all_access=False
            ),
            "status": DataClassificationPolicy(
                classification=DataClassification.PUBLIC,
                category=DataCategory.SYSTEM,
                audit_all_access=False
            ),
        }
        
        self.field_classifications = policies
    
    def classify_field(self, field_name: str) -> Optional[DataClassificationPolicy]:
        """Get classification for field"""
        field_lower = field_name.lower()
        
        # Check exact match
        if field_lower in self.field_classifications:
            return self.field_classifications[field_lower]
        
        # Check partial match (e.g., "user_email" matches "email")
        for key, policy in self.field_classifications.items():
            if field_lower.endswith(f"_{key}") or field_lower.startswith(f"{key}_") or key in field_lower:
                return policy
        
        # Default: assume internal
        return DataClassificationPolicy(
            classification=DataClassification.INTERNAL,
            category=DataCategory.SYSTEM
        )
    
    def get_fields_by_classification(self, classification: DataClassification) -> List[str]:
        """Get all fields with specific classification"""
        return [field for field, policy in self.field_classifications.items()
                if policy.classification == classification]
    
    def should_encrypt_field(self, field_name: str) -> bool:
        """Check if field must be encrypted"""
        policy = self.classify_field(field_name)
        return policy.must_encrypt if policy else False
    
    def should_mask_field(self, field_name: str, user_role: str) -> bool:
        """Check if field should be masked for this role"""
        policy = self.classify_field(field_name)
        if not policy or not policy.must_mask:
            return False
        
        # Check if role has permission to see unmasked
        if policy.permitted_roles and user_role in policy.permitted_roles:
            return False
        
        return True
    
    def get_mask_format(self, field_name: str) -> Optional[str]:
        """Get masking format for field"""
        policy = self.classify_field(field_name)
        return policy.mask_format if policy else None
    
    def requires_approval(self, field_name: str) -> bool:
        """Check if field access requires approval"""
        policy = self.classify_field(field_name)
        return policy.requires_approval if policy else False
    
    def get_retention_days(self, field_name: str) -> Optional[int]:
        """Get data retention period"""
        policy = self.classify_field(field_name)
        return policy.retention_days if policy else None
    
    def add_classification(self, field_name: str, policy: DataClassificationPolicy):
        """Add or override field classification"""
        self.field_classifications[field_name.lower()] = policy
    
    def get_policy_summary(self) -> dict:
        """Get summary of all classifications"""
        by_classification = {}
        for classification in DataClassification:
            fields = self.get_fields_by_classification(classification)
            by_classification[classification.value] = {
                "count": len(fields),
                "fields": fields
            }
        
        return {
            "total_classified_fields": len(self.field_classifications),
            "by_classification": by_classification
        }


# Global classification framework
_framework = None


def get_classification_framework() -> DataClassificationFramework:
    """Get or create global classification framework"""
    global _framework
    if _framework is None:
        _framework = DataClassificationFramework()
    return _framework


def classify_field(field_name: str) -> Optional[DataClassificationPolicy]:
    """Classify a field"""
    return get_classification_framework().classify_field(field_name)


def should_mask(field_name: str, user_role: str) -> bool:
    """Check if field should be masked for user"""
    return get_classification_framework().should_mask_field(field_name, user_role)


def apply_masking(value: str, mask_format: str) -> str:
    """Apply mask format to value"""
    if not value or not mask_format:
        return value
    
    # Simple implementation - can be enhanced
    # For SSN: "123456789" + "XXX-XX-XXXX" = "123-45-XXXX"
    result = ""
    value_idx = 0
    for char in mask_format:
        if char == 'X':
            result += '*' if value_idx >= len(value) else value[value_idx]
            value_idx += 1
        else:
            result += char
    
    return result
