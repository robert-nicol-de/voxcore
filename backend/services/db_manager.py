from cryptography.fernet import Fernet
import psycopg2
import os

# Load Fernet key from env or generate new
FERNET_KEY = os.environ.get("FERNET_KEY")
if not FERNET_KEY:
    FERNET_KEY = Fernet.generate_key()
    print(f"[✓] Fernet key generated: {FERNET_KEY}")
cipher = Fernet(FERNET_KEY)

def encrypt_password(password):
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(password):
    return cipher.decrypt(password.encode()).decode()

class DatabaseConnection:
    def __init__(self, host, port, username, password, database_name):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database_name = database_name

# Test PostgreSQL connection

def test_connection(db: DatabaseConnection):
    try:
        conn = psycopg2.connect(
            host=db.host,
            port=db.port,
            user=db.username,
            password=decrypt_password(db.password),
            database=db.database_name
        )
        conn.close()
        return True
    except Exception as e:
        print(f"[⚠] DB connection failed: {e}")
        return False
