import os
from cryptography.fernet import Fernet

class KeyManager:
    @staticmethod
    def get_master_key():
        key = os.getenv("VOXCORE_MASTER_KEY")
        if not key:
            raise Exception("VOXCORE_MASTER_KEY not set")
        return key.encode()

    @staticmethod
    def get_cipher():
        return Fernet(KeyManager.get_master_key())
