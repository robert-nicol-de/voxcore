import snowflake.connector

params = {
    'account': 'we08391.af-south-1.aws',
    'user': 'VOXQUERY',
    'password': 'Robert210680!@#$',
    'warehouse': 'COMPUTE_WH',
    'database': 'VOXQUERYTRAININGPIN2025',
    'schema': 'PUBLIC',
    'role': 'ACCOUNTADMIN'
}

try:
    print("Connecting to Snowflake...")
    conn = snowflake.connector.connect(**params)
    print("✓ Connected")
    
    cursor = conn.cursor()
    print("✓ Cursor created")
    
    print("\nExecuting: SELECT CURRENT_VERSION() AS version")
    result = cursor.execute("SELECT CURRENT_VERSION() AS version")
    print(f"execute() returned: {result}")
    print(f"execute() type: {type(result)}")
    
    row = cursor.fetchone()
    print(f"fetchone() returned: {row}")
    print(f"fetchone() type: {type(row)}")
    
    if row:
        print(f"✓ Success! Version: {row[0]}")
    else:
        print("✗ No row returned")
    
    cursor.close()
    conn.close()
    print("✓ Connection closed")
    
except Exception as e:
    print(f"✗ Failed: {repr(e)}")
    print(f"Exception type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
