#!/usr/bin/env python3
"""Debug DELETE query parsing"""

import sqlparse
from sqlparse.tokens import Keyword

sql = "DELETE FROM Customers WHERE CustomerID = 1"
print(f"SQL: {sql}")

parsed = sqlparse.parse(sql)
print(f"Parsed: {parsed}")

if parsed:
    stmt = parsed[0]
    print(f"Statement: {stmt}")
    print(f"Statement type: {type(stmt)}")
    
    print("\nTokens:")
    for i, token in enumerate(stmt.flatten()):
        print(f"  {i}: {repr(token)} | ttype={token.ttype} | value={repr(token.value)}")
        if token.ttype is Keyword:
            print(f"      ^ This is a Keyword: {token.value.upper()}")
