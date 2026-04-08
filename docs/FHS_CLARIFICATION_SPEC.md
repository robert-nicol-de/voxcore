# Failure Handling System — Clarification System Spec

## Role
Engage the user for clarification when ambiguity, missing information, or conflicting intent is detected, ensuring the system never guesses and always delivers trusted results.

## Responsibilities
- Detect triggers for clarification (ambiguity, missing filters, conflicting intent, low confidence)
- Generate clear, context-aware clarification prompts
- Route prompts to the user via the UI or conversation manager
- Receive and process user responses to update the semantic plan
- Log all clarification interactions for learning and audit

## Input Contract
- `semantic_plan`: Current plan from SIL
- `error_report`: Output from Error Detection or Retry Engine
- `clarification_context`: (Optional) History of previous clarifications, user profile, etc.

## Output Contract
- `clarification_needed`: Boolean
- `clarification_prompt`: (Optional) User-facing question or prompt
- `clarification_type`: Enum (missing_filter, ambiguous_intent, conflicting_intent, other)
- `clarification_options`: (Optional) List of options for user selection
- `updated_semantic_plan`: (Optional) Revised plan after user response
- `log_entry`: Structured log of clarification event

## Clarification Triggers
- Multiple possible interpretations (e.g., ambiguous metric or dimension)
- Missing required filters (e.g., no date range)
- Conflicting or contradictory intent
- Low confidence score from intent parser or SIL

## Clarification Flow
1. Detect need for clarification
2. Generate prompt and options
3. Route to user and await response
4. Update semantic plan with user input
5. Log the interaction

## Boundaries
- Does NOT generate SQL or modify data
- Does NOT handle error recovery or fallback
- Purely manages human-in-the-loop clarification

## Integration Points
- **Upstream:** Receives context from Error Detection, Retry Engine, and SIL
- **Downstream:** Passes updated semantic plan to SQL Generation Engine (VUSE) and logs to Failure Logger

---

This spec is the authoritative contract for the Clarification System. All code and downstream systems must conform to these input/output and clarification standards.
