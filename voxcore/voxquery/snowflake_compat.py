"""
Compatibility shim for Snowflake connector with Python 3.14+
Patches missing modules that were removed in Python 3.13+
"""

import sys
import types

def patch_python314_compatibility():
    """Patch Python 3.14+ compatibility issues for Snowflake connector"""
    
    if sys.version_info >= (3, 13):
        # Patch 1: Add cgi module (removed in Python 3.13)
        if 'cgi' not in sys.modules:
            cgi = types.ModuleType('cgi')
            sys.modules['cgi'] = cgi
        
        # Patch 2: Fix collections.Mapping -> collections.abc.Mapping
        import collections
        if not hasattr(collections, 'Mapping'):
            from collections import abc
            collections.Mapping = abc.Mapping
            collections.MutableMapping = abc.MutableMapping
            collections.Sequence = abc.Sequence
            collections.MutableSequence = abc.MutableSequence
            collections.Set = abc.Set
            collections.MutableSet = abc.MutableSet
        
        # Patch 3: Create mock cryptography module if needed
        try:
            from cryptography.hazmat.backends.openssl import x509
        except (ImportError, ModuleNotFoundError):
            # Create a mock module structure
            if 'cryptography' not in sys.modules:
                cryptography = types.ModuleType('cryptography')
                sys.modules['cryptography'] = cryptography
            
            if 'cryptography.hazmat' not in sys.modules:
                hazmat = types.ModuleType('cryptography.hazmat')
                sys.modules['cryptography.hazmat'] = hazmat
            
            if 'cryptography.hazmat.backends' not in sys.modules:
                backends = types.ModuleType('cryptography.hazmat.backends')
                sys.modules['cryptography.hazmat.backends'] = backends
            
            if 'cryptography.hazmat.backends.openssl' not in sys.modules:
                openssl = types.ModuleType('cryptography.hazmat.backends.openssl')
                x509_module = types.ModuleType('x509')
                x509_module._Certificate = type('_Certificate', (), {})
                openssl.x509 = x509_module
                sys.modules['cryptography.hazmat.backends.openssl'] = openssl
                sys.modules['cryptography.hazmat.backends.openssl.x509'] = x509_module
        
        print("✓ Python 3.14+ compatibility patches applied")

# Apply patches immediately on import
patch_python314_compatibility()
