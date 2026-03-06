#!/usr/bin/env python
"""Test connection string building"""

import sys
import io
from urllib.parse import quote

# Force UTF-8 encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

warehouse_user = "QUERY"
warehouse_password = "Robert210680!@#$"
warehouse_host = "ko05278.af-south-1.aws"
warehouse_database = "FINANCIAL_TEST"

print("\n" + "="*80)
print("CONNECTION STRING BUILDING TEST")
print("="*80 + "\n")

print(f"Raw password: {warehouse_password}")
print(f"Raw password repr: {repr(warehouse_password)}")

# URL encode the password
encoded_password = quote(warehouse_password, safe='')
print(f"\nURL-encoded password: {encoded_password}")

# Build connection string with raw password (WRONG)
connection_string_raw = (
    f"snowflake://{warehouse_user}:{warehouse_password}"
    f"@{warehouse_host}/{warehouse_database}/PUBLIC"
)
print(f"\nConnection string (RAW PASSWORD - WRONG):")
print(f"  {connection_string_raw}")

# Build connection string with encoded password (CORRECT)
connection_string_encoded = (
    f"snowflake://{warehouse_user}:{encoded_password}"
    f"@{warehouse_host}/{warehouse_database}/PUBLIC"
)
print(f"\nConnection string (ENCODED PASSWORD - CORRECT):")
print(f"  {connection_string_encoded}")

print("\n" + "="*80)
