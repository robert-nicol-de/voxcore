import os
from cryptography.fernet import Fernet


def _get_fernet() -> Fernet:
    key = os.getenv("FERNET_KEY")
    if not key:
        # Fallback keeps local dev working, but persistent env key is recommended.
        key = Fernet.generate_key().decode("utf-8")
    if isinstance(key, str):
        key_bytes = key.encode("utf-8")
    else:
        key_bytes = key
    return Fernet(key_bytes)


def encrypt_secret(value: str) -> str:
    if not value:
        return ""
    return _get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_secret(value: str) -> str:
    if not value:
        return ""
    if not value.startswith("gAAAA"):
        return value
    return _get_fernet().decrypt(value.encode("utf-8")).decode("utf-8")
