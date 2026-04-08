"""
STEP 16.2 — ENCRYPTION LAYER (MANDATORY)

Encryption for:
- Data in transit (TLS 1.2+)
- Data at rest (Fernet symmetric encryption)
- Sensitive fields in DB/logs/cache

Uses cryptography.fernet for field-level encryption with key management.
"""

from cryptography.fernet import Fernet
from typing import Optional, Any, List
import os
import hashlib
import json
from datetime import datetime


class EncryptionService:
    """
    Handles encryption/decryption of sensitive data at rest.
    
    Key rotation tracking:
    - Current key
    - Previous key (for decryption during rotation)
    - Key version tracking
    """
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize encryption service.
        
        Args:
            key: Fernet key (from Fernet.generate_key()). 
                 If None, loads from environment or generates new.
        """
        if key is None:
            # Load from environment (NEVER hardcode)
            key_str = os.getenv("ENCRYPTION_KEY")
            if key_str:
                self.current_key = key_str.encode() if isinstance(key_str, str) else key_str
            else:
                # Fallback: generate new (for dev only)
                self.current_key = Fernet.generate_key()
        else:
            self.current_key = key
        
        self.cipher = Fernet(self.current_key)
        self.previous_key: Optional[bytes] = None  # For key rotation
        self.key_version = 1
        self.encrypted_fields_count = 0
        self.decrypted_fields_count = 0
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt sensitive string data.
        
        Args:
            data: Plain text to encrypt
            
        Returns:
            Encrypted token (safe to store in DB/logs)
        """
        if not data:
            return None
        
        try:
            encrypted = self.cipher.encrypt(data.encode())
            self.encrypted_fields_count += 1
            # Return as string for DB storage
            return encrypted.decode('utf-8')
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive string data.
        
        Args:
            encrypted_data: Encrypted token from DB/logs
            
        Returns:
            Plain text (keep in memory, don't log)
        """
        if not encrypted_data:
            return None
        
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            self.decrypted_fields_count += 1
            return decrypted.decode('utf-8')
        except Exception as e:
            # Try with previous key if main key fails (key rotation)
            if self.previous_key:
                try:
                    old_cipher = Fernet(self.previous_key)
                    decrypted = old_cipher.decrypt(encrypted_data.encode())
                    self.decrypted_fields_count += 1
                    return decrypted.decode('utf-8')
                except:
                    pass
            raise Exception(f"Decryption failed: {str(e)}")
    
    def encrypt_dict(self, data: dict, fields_to_encrypt: List[str]) -> dict:
        """
        Encrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary to encrypt
            fields_to_encrypt: List of field names to encrypt
            
        Returns:
            Dictionary with specified fields encrypted
        """
        result = data.copy()
        for field in fields_to_encrypt:
            if field in result and result[field]:
                result[field] = self.encrypt(str(result[field]))
        return result
    
    def decrypt_dict(self, data: dict, fields_to_decrypt: List[str]) -> dict:
        """
        Decrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary with encrypted fields
            fields_to_decrypt: List of field names to decrypt
            
        Returns:
            Dictionary with specified fields decrypted
        """
        result = data.copy()
        for field in fields_to_decrypt:
            if field in result and result[field]:
                result[field] = self.decrypt(result[field])
        return result
    
    def rotate_key(self, new_key: bytes):
        """
        Rotate encryption key (new key becomes current, old becomes previous).
        
        Args:
            new_key: New Fernet key
            
        Note: All encrypted data with old key must be re-encrypted with new key
        """
        self.previous_key = self.current_key
        self.current_key = new_key
        self.cipher = Fernet(new_key)
        self.key_version += 1
    
    def get_stats(self) -> dict:
        """Get encryption operation statistics"""
        return {
            "encrypted_fields": self.encrypted_fields_count,
            "decrypted_fields": self.decrypted_fields_count,
            "key_version": self.key_version,
            "has_previous_key": self.previous_key is not None
        }


class TransitEncryptionConfig:
    """
    Configuration for encryption in transit (TLS).
    
    Enforces:
    - TLS 1.2 minimum
    - Strong cipher suites
    - HSTS headers
    """
    
    @staticmethod
    def get_tls_config() -> dict:
        """Get TLS configuration for FastAPI/HTTPS"""
        return {
            "ssl_version": "TLSv1_2",
            "min_version": "TLSv1.2",
            "ciphers": [
                "ECDHE-ECDSA-AES256-GCM-SHA384",
                "ECDHE-RSA-AES256-GCM-SHA384",
                "ECDHE-ECDSA-CHACHA20-POLY1305",
                "ECDHE-RSA-CHACHA20-POLY1305",
                "ECDHE-ECDSA-AES128-GCM-SHA256",
                "ECDHE-RSA-AES128-GCM-SHA256"
            ],
            "options": [
                "NO_SSLv2",
                "NO_SSLv3",
                "NO_TLSv1",
                "NO_TLSv1_1"
            ]
        }
    
    @staticmethod
    def get_https_redirect_middleware() -> dict:
        """Middleware to redirect HTTP to HTTPS"""
        return {
            "middleware_type": "HTTPSRedirect",
            "enforce": True,
            "hsts_max_age": 31536000,  # 1 year
            "hsts_include_subdomains": True,
            "hsts_preload": True
        }
    
    @staticmethod
    def get_security_headers() -> dict:
        """Security headers to force HTTPS and secure connections"""
        return {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }


class FieldEncryptionPolicy:
    """
    Define which fields should be encrypted in database.
    
    Sensitivity levels:
    - SENSITIVE: Personally identifiable, financial, health data
    - INTERNAL: Company proprietary, should not be visible to all users
    - PUBLIC: Can be displayed without restriction
    """
    
    SENSITIVITY_LEVELS = {
        "SENSITIVE": ["password", "ssn", "credit_card", "salary", "email", "phone"],
        "INTERNAL": ["api_key", "secret_token", "internal_id", "cost"],
        "PUBLIC": ["name", "created_at", "status", "count"]
    }
    
    @staticmethod
    def should_encrypt(field_name: str, sensitivity: str = "SENSITIVE") -> bool:
        """Check if field should be encrypted"""
        field_lower = field_name.lower()
        sensitive_fields = FieldEncryptionPolicy.SENSITIVITY_LEVELS.get(sensitivity.upper(), [])
        return any(field_lower.startswith(prefix) or field_lower.endswith(f"_{prefix}") 
                   for prefix in sensitive_fields)
    
    @staticmethod
    def get_encryption_list(table_fields: List[str], sensitivity: str = "SENSITIVE") -> List[str]:
        """Get list of fields from table that should be encrypted"""
        return [f for f in table_fields if FieldEncryptionPolicy.should_encrypt(f, sensitivity)]


# Global encryption service instance
_encryption_service = None


def get_encryption_service(key: Optional[bytes] = None) -> EncryptionService:
    """Get or create global encryption service"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService(key)
    return _encryption_service


def encrypt_sensitive_value(value: str) -> str:
    """Convenience function: encrypt sensitive value"""
    return get_encryption_service().encrypt(value)


def decrypt_sensitive_value(encrypted: str) -> str:
    """Convenience function: decrypt sensitive value"""
    return get_encryption_service().decrypt(encrypted)
