# TASK 34: Prompt Fix Applied - Dialect Instructions Now Included

## Problem Identified

The `_build_prompt()` method in `backend/voxquery/core/sql_generator.py` was **loading dialect instructions from INI files but NOT including them in the prompt sent to Groq**. This caused:

1. **Groq generating identical SQL for different questions** - Without dialect-specific rules, Groq couldn't differentiate between questions
2. **Broken SQL patterns** - Groq was generating invalid SQL Server syntax (e.g., using `LIMIT` instead of `TOP`)
3. **Groq degradation after 2-4 questions** - Without clear instructions, Groq's quality degraded

## Root Cause

In `_build_prompt()`:
- Dialect instructions were loaded from `backend/config/dialects/sqlserver.ini`
- But the `template` variable that builds the prompt **did not include these instructions**
- The prompt only had generic examples, not dialect-specific rules

## Fix Applied

### File: `backend/voxquery/core/sql_generator.py`

**Before:**
```python
# Load dialect-specific instructions from INI file
dialect_instructions = config_loader.get_dialect_instructions(self.dialect)

# ... logging code ...

# Build prompt with schema and clear examples
template = f"""You are a SQL expert for {self.dialect.upper()}.

SCHEMA:
{schema_context}

EXAMPLES:
...

QUESTION: {question}
...
"""
```

**After:**
```python
# Load dialect-specific instructions from INI file
dialect_instructions = config_loader.get_dialect_instructions(self.dialect)

# ... logging code ...

# Build prompt with dialect instructions, schema, and clear examples
# CRITICAL: Include dialect instructions to prevent Groq from hallucinating
# CRITICAL: Use "CURRENT QUESTION" marker to prevent Groq from reusing previous SQL
template = f"""You are a SQL expert for {self.dialect.upper()}.

{dialect_instructions if dialect_instructions else "Generate valid SQL using standard ANSI syntax."}

SCHEMA:
{schema_context}

EXAMPLES:
...

================================================================================
CURRENT QUESTION (ANSWER THIS SPECIFIC QUESTION ONLY):
{question}
================================================================================

Generate ONLY valid SQL for the CURRENT QUESTION above. No explanations, no markdown.
- Use only tables and columns from the schema above
- Return complete, executable SQL
- No code blocks or backticks
- IMPORTANT: This is a NEW question - do NOT reuse SQL from previous questions"""
```

## What This Fixes

1. **Dialect instructions now included** - Groq receives SQL Server-specific rules like:
   - "Use TOP N for limiting rows. Never use LIMIT."
   - "For strings use VARCHAR(8000) or VARCHAR(MAX)"
   - "NEVER use sys.databases, sys.tables, sys.columns"
   - "NEVER query system metadata tables"

2. **Clear question boundary** - The `================================================================================` markers and "CURRENT QUESTION" label make it explicit that this is a NEW question, preventing Groq from reusing previous SQL

3. **Explicit instruction** - Added "IMPORTANT: This is a NEW question - do NOT reuse SQL from previous questions" to reinforce the point

## Testing

The fix has been applied and the backend restarted (ProcessId: 35).

To verify the fix works:
1. Connect to a database via the Settings modal
2. Ask 3 different questions
3. Verify each generates different SQL (not identical queries)

## Files Modified

- `backend/voxquery/core/sql_generator.py` - Updated `_build_prompt()` method

## Backend Status

- **ProcessId**: 35 (running)
- **Frontend**: ProcessId 3 (running on port 5173)
- **Backend**: Running on port 8000
- **Changes**: Deployed and active

## Next Steps

If Groq still generates identical SQL after this fix:
1. The issue is likely with Groq's model behavior, not the prompt
2. Consider adding a "question hash" or "question ID" to make each question unique
3. May need to switch to a different LLM provider if Groq continues to be unreliable
