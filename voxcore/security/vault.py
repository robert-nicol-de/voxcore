from voxcore.security.key_manager import KeyManager
import json

class CredentialVault:
    @staticmethod
    def encrypt(data: dict) -> str:
        cipher = KeyManager.get_cipher()
        payload = json.dumps(data).encode()
        return cipher.encrypt(payload).decode()

    @staticmethod
    def decrypt(token: str) -> dict:
        cipher = KeyManager.get_cipher()
        decrypted = cipher.decrypt(token.encode())
        return json.loads(decrypted.decode())
