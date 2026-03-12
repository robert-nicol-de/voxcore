"""
Credential Encryption/Decryption Service

Provides secure encryption and decryption of database credentials.
Supports credentials in .ini files using the ENC: prefix.

Example .ini usage:
    password = ENC:gAAAAABlxxx...
    api_key = ENC:gAAAAABlyyy...
"""

import os
from cryptography.fernet import Fernet, InvalidToken
import base64
import logging

logger = logging.getLogger(__name__)


class CredentialEncryptor:
    """Handles encryption and decryption of sensitive credentials."""

    def __init__(self):
        """Initialize the encryptor with a key from environment or generate one."""
        # Try to get encryption key from environment
        key = os.getenv('VOXCORE_ENCRYPTION_KEY')
        
        if not key:
            # For development: generate a temporary key
            # In production: must be set via environment variable
            logger.warning('VOXCORE_ENCRYPTION_KEY not set. Generating temporary key for development.')
            key = Fernet.generate_key().decode()
        
        # Ensure key is bytes
        if isinstance(key, str):
            key = key.encode()
        
        try:
            self.cipher = Fernet(key)
        except Exception as e:
            logger.error(f'Failed to initialize Fernet cipher: {e}')
            raise ValueError('Invalid VOXCORE_ENCRYPTION_KEY. Must be a valid Fernet key.')

    def encrypt(self, value: str) -> str:
        """
        Encrypt a credential value.
        
        Args:
            value: The plaintext credential to encrypt
            
        Returns:
            Encrypted value in format: ENC:xxxxx
        """
        try:
            encrypted = self.cipher.encrypt(value.encode())
            return f"ENC:{encrypted.decode()}"
        except Exception as e:
            logger.error(f'Encryption failed: {e}')
            raise

    def decrypt(self, value: str) -> str:
        """
        Decrypt a credential value.
        
        Args:
            value: The encrypted value (with or without ENC: prefix)
            
        Returns:
            The plaintext credential
            
        Raises:
            ValueError: If decryption fails or value is not valid encrypted data
        """
        try:
            # Remove ENC: prefix if present
            if value.startswith('ENC:'):
                value = value[4:]
            
            decrypted = self.cipher.decrypt(value.encode())
            return decrypted.decode()
        except InvalidToken:
            logger.error('Invalid encrypted token. Wrong encryption key or corrupted data.')
            raise ValueError('Failed to decrypt credential. Invalid token or wrong key.')
        except Exception as e:
            logger.error(f'Decryption failed: {e}')
            raise ValueError(f'Failed to decrypt credential: {e}')

    def is_encrypted(self, value: str) -> bool:
        """Check if a value is encrypted (starts with ENC:)."""
        return isinstance(value, str) and value.startswith('ENC:')

    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key for use in environment."""
        return Fernet.generate_key().decode()


# Singleton instance
_encryptor = None


def get_encryptor() -> CredentialEncryptor:
    """Get or create the singleton encryptor instance."""
    global _encryptor
    if _encryptor is None:
        _encryptor = CredentialEncryptor()
    return _encryptor


def encrypt_credential(value: str) -> str:
    """Convenience function to encrypt a credential."""
    return get_encryptor().encrypt(value)


def decrypt_credential(value: str) -> str:
    """Convenience function to decrypt a credential."""
    return get_encryptor().decrypt(value)


def decrypt_if_needed(value: str) -> str:
    """
    Decrypt a value if it's encrypted, otherwise return as-is.
    
    Useful for handling .ini files that may have mixed encrypted/plaintext values.
    
    Args:
        value: The value that may be encrypted
        
    Returns:
        Plaintext credential value
    """
    if get_encryptor().is_encrypted(value):
        return decrypt_credential(value)
    return value
