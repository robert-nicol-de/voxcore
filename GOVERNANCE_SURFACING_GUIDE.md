# Governance Surfacing — Step 3a: Making Governance Explicit

**Status:** ✅ **COMPLETE**  
**Commit:** `d7ca995d`  
**Files Modified:** 2 (voxcore/core.py, voxcore/api/playground_api.py)  
**Lines Added:** 482

---

## Overview

### The Problem
Previously, governance decisions (blocked, rewritten, approved, etc.) were buried in status fields and cryptic error messages. Users didn't understand:
- WHY their query was blocked or modified
- WHAT controls were applied for safety
- WHAT issues were detected
- WHETHER they could trust the results

### The Solution
Created explicit governance surfacing layer that:
1. Maps engine statuses to **clean UI labels** (not raw enum values)
2. Builds **user-facing explanations** of governance decisions
3. Lists **all controls applied** with descriptions and values
4. Surfaces **detected issues** that triggered governance actions
5. Makes governance status **always visible**, even on error

---

## Architecture

### 3 Layers of Governance

```
VoxCoreEngine (voxcore/core.py)
    ↓
creates ExecutionLog with ValidationResult + status
    ↓
GovernanceConverter
    ↓
creates PlaygroundGovernanceBlock (explicit governance)
    ↓
Playground API
    ↓
wraps in GovernanceBlock (Pydantic model)
    ↓
Frontend receives explicit governance in every response
```

---

## Implementation Details

### 1. Core Layer: VoxCore Engine (voxcore/core.py)

#### **New Data Classes**

**ControlApplied**
```python
@dataclass
class ControlApplied:
    name: str  # "row_limit" | "timeout" | "query_rewrite" | "destructive_operation_blocked"
    description: str  # Human-readable explanation
    value: Optional[Any] = None  # Optional value (e.g., limit=100)
```

**PlaygroundGovernanceBlock**
```python
@dataclass
class PlaygroundGovernanceBlock:
    # Decision & Status
    decision: str  # "ALLOWED" | "MODIFIED" | "BLOCKED" | "ERROR"
    status_label: str  # Clean UI label (e.g., "Query modified for safety")
    
    # Risk
    risk_score: int  # 0-100
    risk_explanation: str  # User-facing explanation
    
    # Issues & Controls
    issues: List[str]  # Detected issues
    controls_applied: List[ControlApplied]  # Safety measures applied
    
    # Transparency
    was_rewritten: bool
    sandbox_mode: bool
```

#### **GovernanceConverter Class**

A helper class with 4 static methods:

**1. map_status_to_label()**
Maps ExecutionStatus enum to clean UI labels:
```python
ExecutionStatus.SUCCESS → ("ALLOWED", "Query cleared for execution")
ExecutionStatus.REWRITTEN → ("MODIFIED", "Query modified for safe preview execution")
ExecutionStatus.BLOCKED → ("BLOCKED", "Query blocked due to governance policy")
ExecutionStatus.ERROR → ("ERROR", "Could not safely complete this request")
```

**2. build_risk_explanation()**
Generates user-facing explanation based on status and context:
```
BLOCKED:    "This request was blocked because destructive operations are not allowed..."
REWRITTEN:  "VoxCore rewrote your query to limit results for performance..."
ERROR:      "Query could not be safely processed. Contact your administrator."
SUCCESS:    "Query cleared by governance review. Safe to execute."
```

**3. extract_controls_applied()**
Extracts list of governance controls that were applied:
- **query_rewrite:** Query was rewritten for safety
- **row_limit:** Result set limited (e.g., "limit = 100")
- **destructive_operation_blocked:** DROP/DELETE/ALTER blocked
- **safe_demo_data:** Running against sample data
- **timeout:** Query execution limited (e.g., "timeout = 30 seconds")

**4. convert_execution_log_to_governance()**
Main conversion helper that orchestrates the above 3:
```python
PlaygroundGovernanceBlock = GovernanceConverter.convert_execution_log_to_governance(
    execution_log=ExecutionLog,
    policy_decision=PolicyDecision,
    execution_details={"sandbox_mode": True, "timeout_seconds": 30}
)
```

#### **Updated execute_query() Method**

Now returns governance information in all responses:

```python
# BLOCKED response
return {
    "message": "Destructive operations are not allowed",
    "status": "blocked",
    "governance": governance.to_dict(),  # ← NEW
    "execution_log": execution_log,  # ← NEW
}

# SUCCESS response
return {
    "message": "Query executed successfully",
    "status": "success",
    "rows": rows,
    "execution_time": execution_time,
    "governance": governance.to_dict(),  # ← NEW
    "execution_log": execution_log,  # ← NEW
}

# ERROR response
return {
    "message": str(e),
    "status": "error",
    "execution_time": execution_time,
    "governance": governance.to_dict(),  # ← NEW
    "execution_log": execution_log,  # ← NEW
}
```

**Key Point:** Governance is now ALWAYS present, even on blocked/error responses.

---

### 2. API Layer: Playground API (voxcore/api/playground_api.py)

#### **Enhanced GovernanceBlock (Pydantic)**

Updated to match VoxCore's explicit governance:

```python
class GovernanceBlock(BaseModel):
    # PRIMARY (what matters most)
    decision: str  # "ALLOWED" | "MODIFIED" | "BLOCKED" | "ERROR"
    status_label: str  # "Query modified for safety"
    
    # RISK
    risk_score: int  # 0-100
    risk_explanation: str  # User-facing explanation
    
    # ISSUES & CONTROLS
    issues: List[str]
    controls_applied: List[Control]
    
    # TRANSPARENCY
    was_rewritten: bool
    sandbox_mode: bool
    
    # BACKWARD COMPAT
    classification: str  # "SAFE" | "MEDIUM" | "HIGH"
    confidence: float  # 0.0-1.0
    reasons: List[str]
    policy_violations: List[str]
    requires_approval: bool
```

#### **Control Class (Pydantic)**

```python
class Control(BaseModel):
    name: str  # "row_limit", "timeout", "query_rewrite", etc.
    description: str  # "Result set limited to prevent resource exhaustion"
    value: any = None  # 100, 30, etc.
```

#### **convert_core_governance_to_playground()**

Helper function that translates core.py's explicit governance to Playground's format:

```python
def convert_core_governance_to_playground(
    core_governance: PlaygroundGovernanceBlock
) -> GovernanceBlock:
    """Convert core.py governance to Playground format"""
    
    # Map decision to classification
    decision_to_classification = {
        "ALLOWED": "SAFE",
        "MODIFIED": "SAFE",
        "BLOCKED": "HIGH",
        "ERROR": "MEDIUM",
    }
    
    # Build Playground block with all fields
    return GovernanceBlock(
        decision=core_governance.decision,
        status_label=core_governance.status_label,
        risk_score=core_governance.risk_score,
        risk_explanation=core_governance.risk_explanation,
        issues=core_governance.issues,
        controls_applied=[
            Control(name=c.name, description=c.description, value=c.value)
            for c in core_governance.controls_applied
        ],
        was_rewritten=core_governance.was_rewritten,
        sandbox_mode=core_governance.sandbox_mode,
        
        # AUTO-FILL backward compat fields
        classification=classification,
        confidence=1.0 - (risk_score / 100.0),
        reasons=[core_governance.risk_explanation],
        requires_approval=(core_governance.decision == "BLOCKED"),
    )
```

---

## Example Responses

### Example 1: Destructive Operation Blocked

**User Request:** "DROP TABLE customers"

**Response:**
```json
{
  "governance": {
    "decision": "BLOCKED",
    "status_label": "Query blocked due to governance policy",
    "risk_score": 95,
    "risk_explanation": "This request was blocked because destructive operations are not allowed in this workspace.",
    "issues": ["Destructive operation detected"],
    "controls_applied": [
      {
        "name": "destructive_operation_blocked",
        "description": "DROP, DELETE, ALTER operations are not allowed in preview mode"
      }
    ],
    "was_rewritten": false,
    "sandbox_mode": true
  }
}
```

### Example 2: Large Query Modified

**User Request:** "SELECT * FROM orders WHERE year = 2023"

**Response:**
```json
{
  "governance": {
    "decision": "MODIFIED",
    "status_label": "Query modified for safe preview execution",
    "risk_score": 45,
    "risk_explanation": "VoxCore rewrote your query to limit results for performance. Full table scans may impact shared resources.",
    "issues": [
      "Large table scan detected",
      "SELECT * without WHERE clause"
    ],
    "controls_applied": [
      {
        "name": "query_rewrite",
        "description": "Query was rewritten to limit results and ensure safe execution"
      },
      {
        "name": "row_limit",
        "description": "Result set limited to prevent resource exhaustion",
        "value": 100
      },
      {
        "name": "timeout",
        "description": "Query execution limited to prevent runaway processes",
        "value": 30
      }
    ],
    "was_rewritten": true,
    "sandbox_mode": true
  }
}
```

### Example 3: Complex Query Allowed

**User Request:** "SELECT region, SUM(revenue) FROM sales WHERE year = 2023 GROUP BY region"

**Response:**
```json
{
  "governance": {
    "decision": "ALLOWED",
    "status_label": "Query cleared for execution",
    "risk_score": 35,
    "risk_explanation": "Query cleared by governance review. Safe to execute.",
    "issues": [],
    "controls_applied": [
      {
        "name": "timeout",
        "description": "Query execution limited to prevent runaway processes",
        "value": 30
      }
    ],
    "was_rewritten": false,
    "sandbox_mode": true
  }
}
```

---

## Decision Mapping Reference

### Status → Decision → Label → Classification

| ExecutionStatus | Decision | Label | Classification | Risk Color |
|---|---|---|---|---|
| SUCCESS | ALLOWED | Query cleared for execution | SAFE | 🟢 Green |
| REWRITTEN | MODIFIED | Query modified for safe preview | SAFE | 🟡 Yellow |
| BLOCKED | BLOCKED | Query blocked due to policy | HIGH | 🔴 Red |
| ERROR | ERROR | Could not safely complete | MEDIUM | 🟠 Orange |

---

## Controls Applied — Reference Guide

### Control Names & Meanings

| Control | Triggered When | Example Value | Purpose |
|---|---|---|---|
| **query_rewrite** | Query was rewritten for safety | — | User knows query was modified |
| **row_limit** | LIMIT clause added/modified | `100` | Prevent full table scans |
| **timeout** | Query timeout enforced | `30` seconds | Prevent runaway queries |
| **safe_demo_data** | Running in sandbox/demo | — | User knows they're viewing sample data |
| **destructive_operation_blocked** | DROP/DELETE/ALTER detected | — | User knows why query was blocked |

### Control Usage in Code

```python
controls = [
    ControlApplied(
        name="row_limit",
        description="Result set limited to prevent resource exhaustion",
        value=100
    ),
    ControlApplied(
        name="timeout",
        description="Query execution limited to prevent runaway processes",
        value=30
    ),
]
```

---

## User Experience Impact

### Before (Without Governance Surfacing)

```
❌ "Destructive operations are not allowed"
❌ "Query executed successfully" (but query was rewritten!)
❌ No explanation of what controls were applied
❌ No visibility into why a query was modified
```

### After (With Governance Surfacing)

```
✅ "Query blocked due to governance policy"
✅ Explains: "Destructive operations (DROP, DELETE, ALTER) are not allowed in preview mode"
✅ Shows: [Control: destructive_operation_blocked]
✅ All governance decisions are explicit and clear
```

---

## Integration with Playground

### Typical Playground Response Now Includes

```json
{
  "session_id": "...",
  "query_id": "...",
  "hero_insight": "...",
  "why_this_answer": "...",
  "result": {...},
  
  "governance": {
    "decision": "ALLOWED",
    "status_label": "Query cleared for execution",
    "risk_score": 35,
    "risk_explanation": "...",
    "issues": [],
    "controls_applied": [
      {"name": "timeout", "description": "...", "value": 30}
    ],
    "was_rewritten": false,
    "sandbox_mode": true
  },
  
  "emd_preview": "...",
  "suggestions": [...]
}
```

**Result:** Every Playground answer **visibly feels governed**. Governance is not implied; it is explicit.

---

## Backward Compatibility

The new GovernanceBlock automatically fills backward-compatibility fields:

```python
# Calculate classification from decision
classification = {
    "ALLOWED": "SAFE",
    "MODIFIED": "SAFE",
    "BLOCKED": "HIGH",
    "ERROR": "MEDIUM",
}.get(decision)

# Calculate confidence from risk_score
confidence = 1.0 - (risk_score / 100.0)

# Build reasons list
reasons = [risk_explanation] + [c.description for c in controls_applied]
```

This means existing frontends expecting the old fields will still work.

---

## Code Quality

### Type Safety
- All classes use dataclasses or Pydantic
- Type hints throughout
- Python @dataclass for core layer
- Pydantic BaseModel for API layer

### Clarity
- Class names are self-documenting (PlaygroundGovernanceBlock, ControlApplied)
- Methods have clear docstrings
- Logging at key points (blocked, rewritten, etc.)

### Testing Points
Tests should verify:
1. **Mapping:** ExecutionStatus → decision correctly
2. **Labels:** Each decision gets appropriate status_label
3. **Explanations:** Risk explanations are user-friendly and accurate
4. **Controls:** Controls list is complete and non-empty for each scenario
5. **Backward Compat:** Old fields are auto-filled correctly

---

## Checklist: Done When ✅

- ✅ **Governance mapping:** ExecutionLog → PlaygroundGovernanceBlock via GovernanceConverter
- ✅ **Surface all fields:** decision, risk_score, issues, controls_applied, status_label, sandbox, was_rewritten
- ✅ **Decision labeling:** ExecutionStatus → "ALLOWED" | "MODIFIED" | "BLOCKED" | "ERROR"
- ✅ **Risk explanation:** User-facing governance notes for each scenario
- ✅ **Controls applied:** Structured list of controls with name/description/value
- ✅ **Every answer governed:** Governance always visible, always explicit

**Result:** Governance is no longer implied. It is explicit, visible, and clear in every Playground response.

---

## Next Steps

This sets the foundation for **Step 3b: Risk Scoring with Semantic Fingerprinting**, which will add:
- Query semantic analysis (SELECT * = high risk, etc.)
- Fingerprinting to detect query patterns
- Reusable fingerprint cache

Once risk scoring is in place, the governance layer will have more confidence in its decisions.

---

**Status:** ✅ Step 3a Complete / Ready for Step 3b

