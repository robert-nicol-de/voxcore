# VoxCore Credential Encryption Guide

## Overview

VoxCore now supports **encrypted credentials** in `.ini` files for secure database configuration management.

Instead of storing plaintext passwords:
```ini
password = MyDatabasePassword123!
```

Store encrypted values:
```ini
password = ENC:gAAAAABlxyz...
```

---

## Quick Start

### 1. Generate an Encryption Key

```bash
python3 encrypt_credentials.py --generate-key
```

Output:
```
======================================================================
Generated Encryption Key:
======================================================================

z0ODAvfvO_K9mJ4...example...key...here

======================================================================
Add this to your environment:
======================================================================

export VOXCORE_ENCRYPTION_KEY="z0ODAv..."

Or in .env:
VOXCORE_ENCRYPTION_KEY=z0ODAv...

======================================================================
```

### 2. Add Key to Environment

**Option A: .env file**
```env
VOXCORE_ENCRYPTION_KEY=z0ODAvfvO_K9mJ4...
```

**Option B: Docker environment**
```yaml
# docker-compose.prod.yml
environment:
  - VOXCORE_ENCRYPTION_KEY=z0ODAvfvO_K9mJ4...
```

**Option C: System environment (Linux/Mac)**
```bash
export VOXCORE_ENCRYPTION_KEY="z0ODAvfvO_K9mJ4..."
```

### 3. Encrypt Your Credentials

```bash
python3 encrypt_credentials.py --encrypt "MyDatabasePassword123!" --key "z0ODAvfvO_K9mJ4..."
```

Output:
```
======================================================================
Encrypted Credential:
======================================================================

ENC:gAAAAABlxyz...encrypted...value...here

======================================================================
Add to .ini file as:
======================================================================

password = ENC:gAAAAABlxyz...
```

### 4. Add to .ini File

```ini
[sql_server_prod]
type = sqlserver
host = prod-server.database.windows.net
database = AdventureWorks2022
username = sa
password = ENC:gAAAAABlxyz...
```

---

## Usage in Python Code

The encryption system is used automatically when:

### 1. Reading .ini Configuration

```python
from backend.services.credential_encryption import decrypt_if_needed
import configparser

config = configparser.ConfigParser()
config.read('voxcore/voxquery/config.ini')

password = config.get('sql_server_prod', 'password')
plaintext_password = decrypt_if_needed(password)

# plaintext_password is now decrypted even if it was ENC:...
```

### 2. Manual Encryption/Decryption

```python
from backend.services.credential_encryption import (
    encrypt_credential,
    decrypt_credential,
    decrypt_if_needed
)

# Encrypt a credential
encrypted = encrypt_credential("MyPassword123!")
# Returns: ENC:gAAAAABlxyz...

# Decrypt a credential
plaintext = decrypt_credential("ENC:gAAAAABlxyz...")
# Returns: MyPassword123!

# Decrypt only if encrypted (safe for mixed values)
result = decrypt_if_needed("ENC:gAAAAABlxyz...")
# Returns: MyPassword123!

result = decrypt_if_needed("PlainPassword")
# Returns: PlainPassword
```

---

## Security Best Practices

### ✅ DO:

1. **Generate a unique key per environment**
   ```bash
   python3 encrypt_credentials.py --generate-key  # Development
   python3 encrypt_credentials.py --generate-key  # Staging
   python3 encrypt_credentials.py --generate-key  # Production
   ```

2. **Store keys in secure environment management**
   - HashiCorp Vault
   - AWS Secrets Manager
   - Azure Key Vault
   - Google Cloud Secret Manager

3. **Rotate keys periodically** (quarterly recommended)

4. **Encrypt sensitive fields**
   - Database passwords
   - API keys
   - Secret tokens
   - SSH credentials

5. **Version control safely**
   ```bash
   # ✅ Safe: encrypted value in git
   git add voxcore/voxquery/config.ini
   
   # ❌ Never: plaintext .env in git
   echo ".env" >> .gitignore
   ```

### ❌ DON'T:

1. ❌ Commit plaintext `.env` files to version control
2. ❌ Use the same key across environments
3. ❌ Hardcode keys in source code
4. ❌ Log encrypted values (they could be decrypted if key leaks)
5. ❌ Store backup keys insecurely

---

## Example: Multi-Environment Setup

### Development (.env)
```env
VOXCORE_ENCRYPTION_KEY=dev_key_xyz...
VOXCORE_ENV=development
```

### Staging (.env.staging)
```env
VOXCORE_ENCRYPTION_KEY=staging_key_abc...
VOXCORE_ENV=staging
```

### Production (AWS Secrets Manager)
```bash
# Deployed via CI/CD
aws secretsmanager get-secret-value --secret-id voxcore/prod/encryption-key
```

---

## Migration: Existing Plaintext Credentials

If you have existing plaintext `.ini` files:

### Step 1: Backup Original
```bash
cp voxcore/voxquery/config.ini voxcore/voxquery/config.ini.backup
```

### Step 2: Encrypt Each Password

```bash
# Find all passwords in .ini
grep -n "^password = " voxcore/voxquery/config.ini

# For each, encrypt it
python3 encrypt_credentials.py --encrypt "your_password" --key "your_key"

# Replace the plaintext value with encrypted value in .ini
```

### Step 3: Verify

```python
# Test that decryption works
python3 -c "
from backend.services.credential_encryption import decrypt_if_needed
import configparser

config = configparser.ConfigParser()
config.read('voxcore/voxquery/config.ini')

for section in config.sections():
    password = config.get(section, 'password', fallback=None)
    if password:
        decrypted = decrypt_if_needed(password)
        print(f'{section}: {password[:20]}... -> {decrypted[:10]}...')
"
```

---

## Troubleshooting

### Error: "Invalid VOXCORE_ENCRYPTION_KEY"

**Cause:** Key format is incorrect or corrupted.

**Solution:**
```bash
# Re-generate the key
python3 encrypt_credentials.py --generate-key

# Update environment
export VOXCORE_ENCRYPTION_KEY="new_key_here"

# Re-encrypt credentials with new key
```

### Error: "Failed to decrypt credential: Invalid token"

**Cause:** Using wrong encryption key for decryption.

**Solution:**
1. Verify the correct `VOXCORE_ENCRYPTION_KEY` is set
2. Check if the credential was encrypted with a different key
3. Re-encrypt with the correct key:
   ```bash
   python3 encrypt_credentials.py --encrypt "password" --key "correct_key"
   ```

### Mixed Plaintext and Encrypted in Same .ini

**Safe:** VoxCore handles this automatically via `decrypt_if_needed()`

```python
# This works automatically
plaintext = config.get('section', 'port')  # Returns: "1433"
password = config.get('section', 'password')  # Returns: "ENC:gAA..."

# Both work with decrypt_if_needed
port = decrypt_if_needed(plaintext)  # Returns: "1433"
pwd = decrypt_if_needed(password)  # Returns: plaintext password
```

---

## Architecture

### Encryption Flow

```
Plaintext Password
       ↓
  Fernet (AES-128)
       ↓
   ENC:base64_value
       ↓
   Stored in .ini
```

### Decryption Flow

```
.ini loaded
    ↓
Check if starts with "ENC:"
    ↓
  If yes: Decrypt using VOXCORE_ENCRYPTION_KEY
  If no: Use as-is
    ↓
Plaintext credential ready
```

---

## Implementation Details

- **Algorithm:** Fernet (symmetric encryption, AES-128-CBC)
- **Key Format:** Base64-encoded 32-byte keys
- **Key Generation:** `cryptography.fernet.Fernet.generate_key()`
- **Encoding:** UTF-8 strings → Base64 bytes
- **Module:** `backend/services/credential_encryption.py`

---

## Related Files

- **Encryption Service:** `backend/services/credential_encryption.py`
- **Encryption Tool:** `encrypt_credentials.py` (at project root)
- **Requirements:** `cryptography==42.0.5` (already in `backend/requirements.txt`)

---

**Last Updated:** March 12, 2026  
**Version:** 1.0 - Production Ready
