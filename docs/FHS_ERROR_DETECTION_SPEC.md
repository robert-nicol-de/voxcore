# Failure Handling System — Error Detection Layer Spec

## Role
Detect, classify, and report all query-related failures as early as possible, before user-facing output or downstream processing.

## Responsibilities
- Validate generated SQL for syntax and structure
- Cross-check all referenced tables/columns against the Semantic Intelligence Layer (SIL)
- Detect semantic mismatches (e.g., type errors, ambiguous fields)
- Validate query results for emptiness, unexpected types, or out-of-bounds values
- Monitor query execution for timeouts and excessive cost
- Identify hallucinated or non-existent fields (AI mistakes)
- Classify all detected failures using a standardized taxonomy
- Report errors in a structured, non-user-facing format for recovery/clarification

## Input Contract
- `query`: The generated SQL string
- `semantic_plan`: Structured plan from SIL (metrics, dimensions, relationships, time logic)
- `result`: (Optional) Query result set (if available)
- `execution_metadata`: (Optional) Execution stats (duration, cost, error messages)

## Output Contract
- `error_detected`: Boolean
- `error_type`: Enum (see taxonomy below)
- `error_details`: Structured object (field, table, message, etc.)
- `suggested_action`: Enum (retry, clarify, fallback, block)
- `raw_error`: (Optional) Original error message (never shown to user)

## Error Taxonomy
| Error Type              | Detection Method         | Example Action         |
|------------------------|-------------------------|------------------------|
| SQL_SYNTAX_ERROR       | SQL parser/DB error     | Retry/regenerate SQL   |
| MISSING_TABLE          | Schema validation       | Map via SIL           |
| MISSING_COLUMN         | Schema validation       | Map via SIL           |
| SEMANTIC_MISMATCH      | Type/schema check       | Clarify/adjust        |
| EMPTY_RESULT           | Result validation       | Clarify/adjust filter |
| TIMEOUT                | Execution monitor       | Simplify query        |
| HIGH_COST              | Cost estimation         | Optimize/block        |
| HALLUCINATED_FIELD     | SIL/schema check        | Map/clarify           |

## Detection Methods
- **SQL Parsing:** Use SQL parser or DB EXPLAIN/VALIDATE to catch syntax errors
- **Schema Validation:** Cross-reference all fields/tables with SIL definitions
- **Result Validation:** Check for empty sets, nulls, or unexpected types
- **Query Cost/Timeout:** Use EXPLAIN plans, monitor execution time/cost
- **Semantic Validation:** Ensure all query elements map to valid business concepts in SIL

## Boundaries
- Does NOT generate SQL
- Does NOT handle UI or user prompts
- Purely detects, classifies, and reports errors for downstream handling

## Integration Points
- **Upstream:** Receives SQL and semantic plan from SQL Generation Engine (VUSE) and SIL
- **Downstream:** Passes structured error reports to Retry Engine, Clarification System, Fallback Manager, and Failure Logger

---

This spec is the authoritative contract for the Error Detection Layer. All code and downstream systems must conform to these input/output and error classification standards.
