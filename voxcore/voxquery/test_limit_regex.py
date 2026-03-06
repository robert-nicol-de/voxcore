import re

# Test the IMPROVED regex pattern
test_cases = [
    "SELECT * FROM ErrorLog LIMIT 10",
    "SELECT * FROM ErrorLog LIMIT 10;",
    """SELECT * 
FROM ErrorLog 
LIMIT 10""",
    "SELECT col1, col2 FROM table1 LIMIT 5",
    """SELECT col1, col2, col3
FROM table1
WHERE col1 > 100
LIMIT 20""",
]

# NEW pattern from _translate_to_dialect (improved)
pattern = r'\bSELECT\s+(\*|[^;]+?)\s+FROM\s+([^;]+?)\s+LIMIT\s+(\d+)(?:\s|;|$)'
replacement = r'SELECT TOP \3 \1 FROM \2 '

print("Testing IMPROVED regex pattern:")
print("=" * 80)

for sql in test_cases:
    result = re.sub(
        pattern,
        replacement,
        sql,
        flags=re.IGNORECASE | re.DOTALL
    )
    print(f"Original:\n{sql}")
    print(f"Result:\n{result}")
    print(f"Match found: {result != sql}")
    print("-" * 80)
