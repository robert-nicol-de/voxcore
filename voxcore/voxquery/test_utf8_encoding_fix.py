#!/usr/bin/env python
"""Test UTF-8 encoding fix for SQL Server connections"""

import sys
import os
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Force UTF-8 encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("UTF-8 ENCODING FIX VERIFICATION TEST")
print("=" * 70)

# Test 1: Verify environment setup
print("\n[TEST 1] Environment Setup")
print("-" * 70)
print(f"Python version: {sys.version}")
print(f"Default encoding: {sys.getdefaultencoding()}")
print(f"PYTHONIOENCODING: {os.getenv('PYTHONIOENCODING', 'NOT SET')}")
print(f"stdout encoding: {sys.stdout.encoding}")
print(f"stderr encoding: {sys.stderr.encoding}")

# Test 2: Verify pyodbc is available
print("\n[TEST 2] PyODBC Availability")
print("-" * 70)
try:
    import pyodbc
    print(f"✓ PyODBC version: {pyodbc.version}")
    print(f"✓ PyODBC drivers available: {pyodbc.drivers()}")
except ImportError as e:
    print(f"✗ PyODBC not available: {e}")
    sys.exit(1)

# Test 3: Verify SQLAlchemy event listener setup
print("\n[TEST 3] SQLAlchemy Event Listener Setup")
print("-" * 70)
try:
    from sqlalchemy import create_engine, event
    from sqlalchemy.engine import Engine
    
    # Create a test engine
    test_engine = create_engine("sqlite:///:memory:")
    
    # Check if event listeners can be registered
    @event.listens_for(test_engine, "connect")
    def test_listener(dbapi_conn, connection_record):
        pass
    
    print("✓ SQLAlchemy event listeners working correctly")
except Exception as e:
    print(f"✗ Event listener setup failed: {e}")

# Test 4: Test VoxQuery Engine initialization
print("\n[TEST 4] VoxQuery Engine Initialization")
print("-" * 70)
try:
    from voxquery.core.engine import VoxQueryEngine
    from voxquery.config import settings
    
    print(f"Warehouse type: {settings.warehouse_type}")
    print(f"Warehouse host: {settings.warehouse_host}")
    print(f"Warehouse database: {settings.warehouse_database}")
    
    # Initialize engine
    engine = VoxQueryEngine(
        warehouse_type=settings.warehouse_type,
        warehouse_host=settings.warehouse_host,
        warehouse_user=settings.warehouse_user,
        warehouse_password=settings.warehouse_password,
        warehouse_database=settings.warehouse_database,
    )
    print("✓ VoxQuery Engine initialized successfully")
    
    # Test 5: Test connection
    print("\n[TEST 5] Database Connection Test")
    print("-" * 70)
    try:
        with engine.engine.connect() as conn:
            result = conn.execute("SELECT 1 AS test_value")
            row = result.fetchone()
            print(f"✓ Connection successful, test query returned: {row}")
    except Exception as e:
        error_msg = str(e)
        print(f"✗ Connection failed: {error_msg}")
        
        # Check if it's an encoding issue
        if any(x in error_msg for x in ['encoding', 'decode', 'cp1252', 'utf-8']):
            print("  → This appears to be an encoding issue")
        elif any(x in error_msg for x in ['syntax', 'near', 'incorrect']):
            print("  → This appears to be a SQL syntax issue")
        else:
            print("  → This appears to be a connection issue")
    
    # Test 6: Test schema analysis
    print("\n[TEST 6] Schema Analysis")
    print("-" * 70)
    try:
        schema = engine.get_schema()
        table_count = len(schema)
        print(f"✓ Schema analysis successful")
        print(f"  Tables found: {table_count}")
        if table_count > 0:
            first_table = list(schema.keys())[0]
            print(f"  First table: {first_table}")
            print(f"  Columns: {list(schema[first_table].get('columns', {}).keys())[:5]}")
    except Exception as e:
        error_msg = str(e)
        print(f"✗ Schema analysis failed: {error_msg}")
    
    # Test 7: Test question generation
    print("\n[TEST 7] Question Generation")
    print("-" * 70)
    try:
        schema = engine.get_schema()
        if schema:
            questions = engine.generate_questions_from_schema(schema, limit=3)
            print(f"✓ Generated {len(questions)} questions:")
            for i, q in enumerate(questions, 1):
                print(f"  {i}. {q}")
        else:
            print("⚠ No schema available for question generation")
    except Exception as e:
        error_msg = str(e)
        print(f"✗ Question generation failed: {error_msg}")
    
    engine.close()

except Exception as e:
    error_msg = str(e)
    print(f"✗ VoxQuery Engine initialization failed: {error_msg}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
