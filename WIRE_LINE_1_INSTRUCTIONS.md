# Wire Line 1: System Prompt - Exact Instructions

## What is Line 1?

```python
# Line 1: Build platform-specific system prompt BEFORE LLM call
prompt = build_system_prompt(platform, schema_context)
```

This ensures the LLM receives platform-specific instructions BEFORE generating SQL.

---

## Where to Wire It

**File**: `backend/voxquery/core/sql_generator.py`

**Method**: `generate()`

**Current Code** (approximate location):

```python
def generate(self, question: str, context: Optional[str] = None) -> GeneratedSQL:
    """Generate SQL from natural language question"""
    
    # ... existing code ...
    
    # Call LLM
    response = self.groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a SQL expert..."},  # ← REPLACE THIS
            {"role": "user", "content": question}
        ],
        temperature=0.1,
        max_tokens=1024,
    )
```

---

## Exact Code to Add

### Step 1: Find the generate() method

Search for:
```python
def generate(self, question: str, context: Optional[str] = None) -> GeneratedSQL:
```

### Step 2: Add imports at the top of the method

```python
def generate(self, question: str, context: Optional[str] = None) -> GeneratedSQL:
    """Generate SQL from natural language question"""
    
    # Import platform dialect engine
    from voxquery.core import platform_dialect_engine
```

### Step 3: Get the platform

Add this before the LLM call:

```python
    # Get platform (from engine or context)
    platform = getattr(self, 'platform', 'snowflake')  # Default to snowflake
    
    # Build schema context (if available)
    schema_context = ""
    if hasattr(self, 'schema_analyzer') and self.schema_analyzer.schema_cache:
        schema_context = self._build_schema_context()
```

### Step 4: Build the platform-specific prompt

Add this before the LLM call:

```python
    # Line 1: Build platform-specific system prompt
    system_prompt = platform_dialect_engine.build_system_prompt(
        platform,
        schema_context
    )
```

### Step 5: Use the platform-specific prompt

Replace the hardcoded system prompt:

```python
    # BEFORE:
    response = self.groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a SQL expert..."},  # ← OLD
            {"role": "user", "content": question}
        ],
        ...
    )
    
    # AFTER:
    response = self.groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},  # ← NEW (platform-specific)
            {"role": "user", "content": question}
        ],
        ...
    )
```

---

## Complete Example

Here's what the modified `generate()` method should look like:

```python
def generate(self, question: str, context: Optional[str] = None) -> GeneratedSQL:
    """Generate SQL from natural language question"""
    
    # Import platform dialect engine
    from voxquery.core import platform_dialect_engine
    
    # Get platform
    platform = getattr(self, 'platform', 'snowflake')
    
    # Build schema context
    schema_context = ""
    if hasattr(self, 'schema_analyzer') and self.schema_analyzer.schema_cache:
        schema_context = self._build_schema_context()
    
    # Line 1: Build platform-specific system prompt
    system_prompt = platform_dialect_engine.build_system_prompt(
        platform,
        schema_context
    )
    
    # Call LLM with platform-specific prompt
    response = self.groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},  # ← Platform-specific
            {"role": "user", "content": question}
        ],
        temperature=0.1,
        max_tokens=1024,
    )
    
    # ... rest of method (unchanged)
```

---

## What This Does

### Before (Without Line 1)

```
User: "Show top 10 accounts"
    ↓
LLM receives generic prompt: "You are a SQL expert..."
    ↓
LLM generates SQL (might use LIMIT or TOP, unclear)
    ↓
Layer 2: process_sql() fixes it
    ↓
Query executes
```

### After (With Line 1)

```
User: "Show top 10 accounts"
    ↓
Platform: "snowflake"
    ↓
Line 1: build_system_prompt("snowflake", schema)
    ↓
LLM receives Snowflake-specific prompt:
"Use Snowflake SQL. Use LIMIT N. Use schema qualification."
    ↓
LLM generates correct SQL: "SELECT * FROM PUBLIC.ACCOUNTS LIMIT 10"
    ↓
Layer 2: process_sql() validates (already correct)
    ↓
Query executes
```

---

## Benefits

1. **Better LLM Output**: LLM knows the target platform upfront
2. **Fewer Rewrites**: Less work for Layer 2 (process_sql)
3. **Higher Confidence**: LLM generates correct syntax first time
4. **Faster Execution**: No fallback queries needed
5. **Better Logging**: Can see platform-specific prompts in logs

---

## Testing Line 1

After wiring, test with:

```python
from voxquery.core import platform_dialect_engine

# Test SQL Server prompt
prompt_ss = platform_dialect_engine.build_system_prompt("sqlserver", "")
assert "TOP" in prompt_ss
assert "T-SQL" in prompt_ss

# Test Snowflake prompt
prompt_sf = platform_dialect_engine.build_system_prompt("snowflake", "")
assert "LIMIT" in prompt_sf
assert "Snowflake" in prompt_sf

# Test PostgreSQL prompt
prompt_pg = platform_dialect_engine.build_system_prompt("postgresql", "")
assert "LIMIT" in prompt_pg
assert "PostgreSQL" in prompt_pg
```

---

## Verification

After wiring, you should see in logs:

```
[LAYER 2] Applying platform dialect engine for snowflake
[LAYER 2] SQL rewritten and validated successfully
[LAYER 2] Validation score: 1.0  ← High score (LLM got it right)
[LAYER 2] Final SQL: SELECT * FROM PUBLIC.ACCOUNTS LIMIT 10...
```

Compare to before (without Line 1):

```
[LAYER 2] Applying platform dialect engine for snowflake
[LAYER 2] SQL rewritten and validated successfully
[LAYER 2] Validation score: 0.8  ← Lower score (had to fix it)
[LAYER 2] Final SQL: SELECT * FROM PUBLIC.ACCOUNTS LIMIT 10...
```

---

## Summary

**Time to wire**: 5 minutes
**Lines of code**: ~15 lines
**Impact**: Improves LLM accuracy and reduces rewrites

**Exact steps**:
1. Import `platform_dialect_engine`
2. Get `platform` from self
3. Build `schema_context`
4. Call `build_system_prompt(platform, schema_context)`
5. Use result as system prompt for LLM

Done!
