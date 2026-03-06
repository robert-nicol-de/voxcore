#!/usr/bin/env python
"""
Wrapper script to run VoxQuery backend with Snowflake compatibility patches
Run this instead of: python backend/main.py
"""

import sys
import types

# Apply Python 3.14+ compatibility patches FIRST, before any other imports
if sys.version_info >= (3, 13):
    print("Applying Python 3.14+ compatibility patches...")
    
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
    
    print("✓ Compatibility patches applied")

# Now run the backend
if __name__ == "__main__":
    from voxquery.api import app
    from voxquery.config import settings
    import uvicorn
    
    uvicorn.run(
        "voxquery.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
