# Quick Reference - Dialect Engine System

## Current Status: ✅ PRODUCTION READY

## Key Files

| File | Purpose | Status |
|------|---------|--------|
| `backend/voxquery/engines/platform_engine.py` | Bridges to platform_dialect_engine | ✅ Created |
| `backend/voxquery/config/dialects/dialect_config.py` | Main config interface | ✅ Fixed |
| `backend/voxquery/core/platform_dialect_engine.py` | Core implementation | ✅ Existing |

## How It Works

```python
# In sql_generator.py or any module:
from voxquery.config.dialects.dialect_config import get_dialect_config

config = get_dialect_config()  # Singleton instance
prompt = config.build_system_prompt("sqlserver", schema)
result = config.process_sql(sql, "sqlserver")
```

## Available Functions

```python
from voxquery.config.dialects.dialect_config import (
    get_dialect_config,              # Get singleton engine
    build_system_prompt,             # Build LLM prompt
    process_sql,                     # Validate/rewrite SQL
    get_live_platforms,              # ['sqlserver', 'snowflake', 'semantic_model']
    get_coming_soon_platforms,       # ['postgresql', 'redshift', 'bigquery']
    get_platform_info,               # Get platform config
    get_all_platforms,               # Get all platforms
)
```

## Testing

Run comprehensive test:
```bash
cd backend
python test_import_chain_verification.py
```

Quick import test:
```bash
python -c "from voxquery.config.dialects.dialect_config import get_dialect_config; print('OK')"
```

## Services

```bash
# Backend
cd backend
python -m uvicorn main:app --reload

# Frontend
cd frontend
npm run dev
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'voxquery.engines'` | Ensure `backend/voxquery/engines/` directory exists with `__init__.py` |
| `RecursionError` in `get_live_platforms()` | Check that `dialect_config.py` imports from `platform_engine` correctly |
| Import fails | Run `python test_import_chain_verification.py` to diagnose |

## Architecture

```
sql_generator.py
    ↓ imports
dialect_config.py (wrapper/interface)
    ↓ imports
platform_engine.py (bridge)
    ↓ imports
platform_dialect_engine.py (core implementation)
    ↓ uses
config/platforms/*.ini (platform configs)
```

## Next Steps

System is ready for:
- ✅ Query generation
- ✅ SQL validation
- ✅ Platform-specific rewrites
- ✅ LLM prompt generation

No further setup needed.
