# SQL Inspector Architecture

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER QUESTION                               │
│                    "Show top 10 customers"                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SQL GENERATOR (LLM)                              │
│                  Groq / llama-3.3-70b                               │
│                                                                     │
│  Generated SQL:                                                     │
│  SELECT * FROM customers LIMIT 10                                  │
│  Confidence: 0.95                                                   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  SQL INSPECTOR (NEW)                                │
│                                                                     │
│  1. Extract Tables:                                                 │
│     {CUSTOMERS}                                                     │
│                                                                     │
│  2. Extract Columns:                                                │
│     {*} (wildcard)                                                  │
│                                                                     │
│  3. Validate Against Schema:                                        │
│     ✅ CUSTOMERS exists in schema                                   │
│     ✅ No forbidden keywords                                        │
│     ✅ Wildcard columns OK                                          │
│                                                                     │
│  4. Calculate Score:                                                │
│     Score = 1.0 (perfect)                                           │
│                                                                     │
│  5. Decision:                                                       │
│     Score >= 0.95 → Use SQL as-is                                   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FINAL SQL & CONFIDENCE                           │
│                                                                     │
│  SQL: SELECT * FROM customers LIMIT 10                             │
│  Confidence: 0.95 (unchanged)                                       │
│  Status: ✅ PASS                                                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EXECUTE QUERY                                    │
│                                                                     │
│  Results: 10 customer rows                                          │
└─────────────────────────────────────────────────────────────────────┘
```

## Hallucination Detection Example

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER QUESTION                               │
│                    "Show all revenue data"                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SQL GENERATOR (LLM)                              │
│                                                                     │
│  Generated SQL:                                                     │
│  SELECT * FROM revenue_table                                        │
│  Confidence: 0.85                                                   │
│                                                                     │
│  ⚠️  LLM HALLUCINATED TABLE NAME!                                   │
│     (Actual schema has: SALES, ORDERS, CUSTOMERS)                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  SQL INSPECTOR (NEW)                                │
│                                                                     │
│  1. Extract Tables:                                                 │
│     {REVENUE_TABLE}                                                 │
│                                                                     │
│  2. Validate Against Schema:                                        │
│     ❌ REVENUE_TABLE NOT FOUND in schema!                           │
│     Known tables: {SALES, ORDERS, CUSTOMERS}                       │
│                                                                     │
│  3. Calculate Score:                                                │
│     Score = 1.0 × 0.4 = 0.4 (unknown table penalty)                │
│                                                                     │
│  4. Decision:                                                       │
│     Score < 0.5 → USE FALLBACK QUERY                               │
│     Fallback: SELECT * FROM SALES LIMIT 10                         │
│     Set confidence to 0.0                                           │
│                                                                     │
│  5. Log Warning:                                                    │
│     ❌ SQL inspection FAILED (score 0.40)                           │
│     Unknown tables: {'REVENUE_TABLE'}                               │
│     ⚠️  Using fallback query: SELECT * FROM SALES LIMIT 10          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FINAL SQL & CONFIDENCE                           │
│                                                                     │
│  SQL: SELECT * FROM SALES LIMIT 10                                 │
│  Confidence: 0.0 (hallucination detected)                           │
│  Status: ⚠️  FALLBACK USED                                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EXECUTE FALLBACK QUERY                           │
│                                                                     │
│  Results: 10 sales rows (safe fallback)                             │
│  UI Warning: "Low confidence SQL - showing safe results"            │
└─────────────────────────────────────────────────────────────────────┘
```

## Security Example: Blocked DELETE

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER QUESTION                               │
│                    "Delete old records"                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SQL GENERATOR (LLM)                              │
│                                                                     │
│  Generated SQL:                                                     │
│  DELETE FROM customers WHERE created_date < '2020-01-01'           │
│  Confidence: 0.90                                                   │
│                                                                     │
│  ⚠️  DANGEROUS OPERATION!                                           │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  SQL INSPECTOR (NEW)                                │
│                                                                     │
│  1. Check Forbidden Keywords:                                       │
│     ❌ DELETE keyword found!                                        │
│     Forbidden: [DROP, DELETE, UPDATE, INSERT, ALTER, ...]          │
│                                                                     │
│  2. Calculate Score:                                                │
│     Score = 1.0 × 0.1 = 0.1 (forbidden keyword penalty)            │
│                                                                     │
│  3. Decision:                                                       │
│     Score < 0.5 → USE FALLBACK QUERY                               │
│     Fallback: SELECT * FROM CUSTOMERS LIMIT 10                     │
│     Set confidence to 0.0                                           │
│                                                                     │
│  4. Log Warning:                                                    │
│     ❌ SQL inspection: Forbidden keyword detected                   │
│     ❌ SQL inspection FAILED (score 0.10)                           │
│     Forbidden DDL/DML detected                                      │
│     ⚠️  Using fallback query: SELECT * FROM CUSTOMERS LIMIT 10      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FINAL SQL & CONFIDENCE                           │
│                                                                     │
│  SQL: SELECT * FROM CUSTOMERS LIMIT 10                             │
│  Confidence: 0.0 (dangerous operation blocked)                      │
│  Status: ❌ BLOCKED - FALLBACK USED                                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EXECUTE FALLBACK QUERY                           │
│                                                                     │
│  Results: 10 customer rows (safe fallback)                          │
│  UI Alert: "⚠️ Dangerous operation blocked - showing safe results"  │
│  Audit Log: DELETE attempt blocked at 2026-02-01 14:30:45          │
└─────────────────────────────────────────────────────────────────────┘
```

## Confidence Score Calculation

```
┌──────────────────────────────────────────────────────────────────┐
│                    CONFIDENCE SCORE FORMULA                      │
│                                                                  │
│  score = 1.0                                                     │
│                                                                  │
│  IF forbidden_keyword_found:                                     │
│    score *= 0.1  (score becomes 0.1)                             │
│                                                                  │
│  IF unknown_tables_found:                                        │
│    score *= 0.4  (score becomes 0.04 or 0.4)                     │
│                                                                  │
│  IF invalid_columns_found:                                       │
│    score *= 0.6  (score becomes 0.024 or 0.24 or 0.6)            │
│                                                                  │
│  IF score < 0.5:                                                 │
│    Use fallback query                                            │
│    Set confidence to 0.0                                         │
│  ELSE IF score < 0.95:                                           │
│    Use SQL but log warnings                                      │
│    Reduce overall confidence                                     │
│  ELSE:                                                           │
│    Use SQL as-is                                                 │
│    Keep original confidence                                      │
└──────────────────────────────────────────────────────────────────┘
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────────────────┐
│                         VoxQueryEngine                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ ask(question)                                                │  │
│  │                                                              │  │
│  │  1. Call sql_generator.generate(question)                   │  │
│  │     → Returns: GeneratedSQL object                          │  │
│  │                                                              │  │
│  │  2. Call inspect_and_repair(sql, schema_tables, columns)    │  │
│  │     → Returns: (final_sql, confidence_score)                │  │
│  │                                                              │  │
│  │  3. Adjust confidence if needed                             │  │
│  │                                                              │  │
│  │  4. Execute query (if requested)                            │  │
│  │                                                              │  │
│  │  5. Return result with final_sql and confidence             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ schema_analyzer (lazy-initialized)                           │  │
│  │                                                              │  │
│  │  Provides:                                                   │  │
│  │  - schema_cache: Dict[table_name, TableSchema]              │  │
│  │  - schema_columns: Dict[table_name, Set[column_names]]      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      sql_safety Module                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ extract_tables(sql, dialect)                                 │  │
│  │ → Set[table_names]                                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ extract_columns(sql, dialect)                                │  │
│  │ → Dict[table_name, Set[column_names]]                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ inspect_and_repair(sql, schema_tables, schema_columns)       │  │
│  │ → (final_sql, confidence_score)                              │  │
│  │                                                              │  │
│  │  Validation Checks:                                          │  │
│  │  1. Forbidden keywords                                       │  │
│  │  2. Unknown tables                                           │  │
│  │  3. Invalid columns                                          │  │
│  │  4. Fallback logic                                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Input:
  - generated_sql: str (from LLM)
  - schema_tables: set (from schema_analyzer)
  - schema_columns: dict (from schema_analyzer)
  - dialect: str (warehouse type)

Processing:
  1. Extract tables from SQL
  2. Extract columns from SQL
  3. Validate tables against schema
  4. Validate columns against schema
  5. Calculate confidence score
  6. Determine action (use/fallback)

Output:
  - final_sql: str (validated or fallback)
  - confidence_score: float (0.0-1.0)

Side Effects:
  - Logging (info/warning/error)
  - Audit trail
```

## Error Handling

```
┌─────────────────────────────────────────────────────────────────────┐
│                      ERROR SCENARIOS                                │
│                                                                     │
│  1. SQL Parse Error                                                 │
│     → Log warning                                                   │
│     → Return empty set/dict                                         │
│     → Continue validation                                           │
│                                                                     │
│  2. Schema Not Available                                            │
│     → Log warning                                                   │
│     → Skip validation                                               │
│     → Use SQL as-is                                                 │
│                                                                     │
│  3. Invalid SQL                                                     │
│     → Log error                                                     │
│     → Return fallback query                                         │
│     → Set confidence to 0.0                                         │
│                                                                     │
│  4. Hallucinated Table                                              │
│     → Log warning                                                   │
│     → Reduce score                                                  │
│     → Return fallback if score < 0.5                                │
│                                                                     │
│  5. Forbidden Operation                                             │
│     → Log error                                                     │
│     → Reduce score to 0.1                                           │
│     → Return fallback if score < 0.5                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

**Architecture Status:** ✅ Complete and Production-Ready
