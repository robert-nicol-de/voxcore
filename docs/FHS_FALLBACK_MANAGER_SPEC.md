# Failure Handling System — Fallback Manager Spec

## Role
Deliver the best possible outcome to the user when full accuracy is not achievable, ensuring value is always provided and user trust is maintained.

## Responsibilities
- Receive escalation from Retry & Recovery or Clarification System
- Select and apply the appropriate fallback mode based on context and failure type
- Generate partial answers, summaries, cached results, or clear explanations of limitations
- Ensure user experience is safe, actionable, and never exposes raw errors
- Log all fallback events for analytics and learning

## Input Contract
- `semantic_plan`: Current plan from SIL
- `error_report`: Output from Error Detection or Retry Engine
- `retry_context`: (Optional) History of previous attempts
- `clarification_context`: (Optional) User clarifications

## Output Contract
- `fallback_mode`: Enum (full_answer, partial_answer, summary, explanation)
- `fallback_result`: User-facing data or message (KPI, cached result, summary, or explanation)
- `fallback_details`: Structured object (what was used, why)
- `log_entry`: Structured log of fallback event

## Fallback Hierarchy
1. **Full Accurate Answer:** If possible, deliver the complete, correct result
2. **Partial Answer:** Limited scope (e.g., top-level KPI, subset of data)
3. **Summary/Trend Insight:** High-level summary or trend, not full detail
4. **Explanation of Limitation:** Clear, actionable message about what could not be delivered and why

## Fallback Examples
- Show top-level KPI instead of detailed breakdown
- Use cached or last successful result
- Provide summary insight (e.g., "Revenue is up 10% overall")
- Explain limitation (e.g., "Detailed breakdown unavailable due to missing data")

## Boundaries
- Does NOT attempt further recovery or clarification
- Does NOT generate SQL or modify data
- Purely manages fallback and user-facing messaging

## Integration Points
- **Upstream:** Receives escalation from Retry & Recovery or Clarification System
- **Downstream:** Passes fallback result to UI/Conversation Manager and logs to Failure Logger

---

This spec is the authoritative contract for the Fallback Manager. All code and downstream systems must conform to these input/output and fallback standards.
