#!/usr/bin/env python3
"""
VoxCore Credential Encryption Tool

Generates encryption keys and encrypts database credentials for secure storage.

Usage:
    # Generate a new encryption key
    python3 encrypt_credentials.py --generate-key
    
    # Encrypt a password
    python3 encrypt_credentials.py --encrypt "mypassword" --key "your-key-here"
    
    # Decrypt a credential
    python3 encrypt_credentials.py --decrypt "ENC:gAAAAABlxxx..." --key "your-key-here"
"""

import argparse
import sys
import os
from pathlib import Path

# Add backend to path so we can import from it
sys.path.insert(0, str(Path(__file__).parent))

from services.credential_encryption import CredentialEncryptor, decrypt_credential


def main():
    parser = argparse.ArgumentParser(
        description='VoxCore Credential Encryption Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Generate encryption key for environment
  python3 encrypt_credentials.py --generate-key
  
  # Encrypt a credential
  python3 encrypt_credentials.py --encrypt "sa_password" --key "your-key"
  
  # Decrypt to verify
  python3 encrypt_credentials.py --decrypt "ENC:..." --key "your-key"
        '''
    )
    
    parser.add_argument('--generate-key', action='store_true',
                        help='Generate a new encryption key')
    parser.add_argument('--encrypt', metavar='VALUE',
                        help='Encrypt a credential value')
    parser.add_argument('--decrypt', metavar='VALUE',
                        help='Decrypt an encrypted credential')
    parser.add_argument('--key', metavar='KEY',
                        help='Encryption key (required for encrypt/decrypt)')
    
    args = parser.parse_args()
    
    if args.generate_key:
        key = CredentialEncryptor.generate_key()
        print('=' * 70)
        print('Generated Encryption Key:')
        print('=' * 70)
        print()
        print(key)
        print()
        print('=' * 70)
        print('Add this to your environment:')
        print('=' * 70)
        print()
        print(f'export VOXCORE_ENCRYPTION_KEY="{key}"')
        print()
        print('Or in .env:')
        print(f'VOXCORE_ENCRYPTION_KEY={key}')
        print()
        print('=' * 70)
        return 0
    
    if args.encrypt:
        if not args.key:
            print('Error: --key required for encryption', file=sys.stderr)
            return 1
        
        try:
            encryptor = CredentialEncryptor() if not args.key else CredentialEncryptor()
            # Override the cipher with the provided key
            from cryptography.fernet import Fernet
            if isinstance(args.key, str):
                args.key = args.key.encode()
            encryptor.cipher = Fernet(args.key)
            
            encrypted = encryptor.encrypt(args.encrypt)
            print('=' * 70)
            print('Encrypted Credential:')
            print('=' * 70)
            print()
            print(encrypted)
            print()
            print('=' * 70)
            print('Add to .ini file as:')
            print('=' * 70)
            print()
            print(f'password = {encrypted}')
            print()
        except Exception as e:
            print(f'Error: {e}', file=sys.stderr)
            return 1
        return 0
    
    if args.decrypt:
        if not args.key:
            print('Error: --key required for decryption', file=sys.stderr)
            return 1
        
        try:
            encryptor = CredentialEncryptor()
            # Override the cipher with the provided key
            from cryptography.fernet import Fernet
            if isinstance(args.key, str):
                args.key = args.key.encode()
            encryptor.cipher = Fernet(args.key)
            
            decrypted = encryptor.decrypt(args.decrypt)
            print('=' * 70)
            print('Decrypted Credential:')
            print('=' * 70)
            print()
            print(decrypted)
            print()
        except Exception as e:
            print(f'Error: {e}', file=sys.stderr)
            return 1
        return 0
    
    parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
