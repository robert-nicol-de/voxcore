#!/usr/bin/env python
"""Debug schema analysis"""

import logging
import sys
import io

# Force UTF-8 encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

print("\n" + "="*80)
print("SCHEMA ANALYSIS DEBUG TEST")
print("="*80 + "\n")

try:
    from voxquery.core.engine import VoxQueryEngine
    
    print("Creating VoxQueryEngine...")
    engine = VoxQueryEngine(
        warehouse_type='snowflake',
        warehouse_host='ko05278.af-south-1.aws',
        warehouse_user='QUERY',
        warehouse_password='Robert210680!@#$',
        warehouse_database='FINANCIAL_TEST',
    )
    
    print("[OK] Engine created")
    print(f"  warehouse_type: {engine.warehouse_type}")
    print(f"  warehouse_host: {engine.warehouse_host}")
    print(f"  warehouse_database: {engine.warehouse_database}")
    
    print("\nAccessing schema_analyzer property (triggers lazy init)...")
    analyzer = engine.schema_analyzer
    print(f"[OK] Schema analyzer initialized: {analyzer}")
    print(f"  warehouse_type: {analyzer.warehouse_type}")
    print(f"  warehouse_host: {analyzer.warehouse_host}")
    print(f"  warehouse_database: {analyzer.warehouse_database}")
    
    print("\nCalling analyze_all_tables()...")
    schemas = analyzer.analyze_all_tables()
    print(f"[OK] Result: {len(schemas)} tables found")
    print(f"  Tables: {list(schemas.keys())}")
    
    if schemas:
        for table_name, schema in list(schemas.items())[:3]:
            print(f"\n  Table: {table_name}")
            print(f"    Columns: {len(schema.columns)}")
            for col_name, col in list(schema.columns.items())[:3]:
                print(f"      - {col_name}: {col.type}")
    else:
        print("\n[WARN] No tables found!")
        print("Checking schema_cache directly...")
        print(f"  schema_cache: {analyzer.schema_cache}")
        print(f"  schema_cache type: {type(analyzer.schema_cache)}")
        print(f"  schema_cache len: {len(analyzer.schema_cache) if analyzer.schema_cache else 'None'}")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
