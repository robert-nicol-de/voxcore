import os
from cryptography.fernet import Fernet
from pathlib import Path


def _fernet_key_file() -> Path:
    # backend/db/crypto.py -> backend/db -> backend -> project root
    root = Path(__file__).resolve().parents[2]
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "fernet.key"


def _load_or_create_file_key() -> str:
    key_file = _fernet_key_file()
    if key_file.exists():
        return key_file.read_text(encoding="utf-8").strip()
    generated = Fernet.generate_key().decode("utf-8")
    key_file.write_text(generated, encoding="utf-8")
    return generated


def _get_fernet() -> Fernet:
    key = os.getenv("FERNET_KEY")
    if not key:
        # Fallback persists to disk so encrypted connection files survive restarts.
        key = _load_or_create_file_key()
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
