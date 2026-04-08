# Failure Handling System — Retry & Recovery Engine Spec

## Role
Automatically recover from detected failures by retrying, simplifying, or adapting queries before the user sees an error.

## Responsibilities
- Receive structured error reports from Error Detection Layer
- Apply retry strategies based on error type and context
- Regenerate or simplify SQL queries as needed
- Switch aggregation or metric strategies if required
- Use alternative data sources (e.g., pre-aggregated, cached)
- Apply safe defaults when ambiguity or missing data is detected
- Escalate to fallback or clarification if retries fail
- Log all retry attempts and outcomes for learning

## Input Contract
- `original_query`: The initial SQL string
- `semantic_plan`: Structured plan from SIL
- `error_report`: Output from Error Detection Layer
- `retry_context`: (Optional) History of previous attempts

## Output Contract
- `recovered`: Boolean
- `final_query`: (Optional) The SQL string to execute next
- `recovery_strategy`: Enum (regenerate, simplify, switch_metric, use_fallback, safe_default)
- `recovery_details`: Structured object (what changed, why)
- `escalate`: Boolean (if further action needed)
- `log_entry`: Structured log of attempt

## Retry Strategies
- **Regenerate SQL:** Tighter constraints, more explicit joins, stricter filters
- **Simplify Query:** Reduce joins, remove complex filters, limit scope
- **Switch Aggregation:** Use alternative metric or aggregation method
- **Use Fallback Data:** Pre-aggregated, cached, or last-known-good results
- **Apply Safe Defaults:** Substitute missing filters, use default values

## Recovery Flow
1. Receive error report
2. Select strategy based on error type and retry context
3. Attempt recovery (regenerate/simplify/switch)
4. If recovery fails, escalate to fallback or clarification
5. Log all attempts and outcomes

## Boundaries
- Does NOT generate user-facing errors
- Does NOT handle UI or clarification prompts
- Purely attempts automated recovery before escalation

## Integration Points
- **Upstream:** Receives error reports from Error Detection Layer
- **Downstream:** Passes recovered query or escalation to Fallback Manager, Clarification System, and Failure Logger

---

This spec is the authoritative contract for the Retry & Recovery Engine. All code and downstream systems must conform to these input/output and recovery strategy standards.
