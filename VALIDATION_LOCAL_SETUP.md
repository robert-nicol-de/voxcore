# Local Validation Setup

Use this when Docker is unavailable and you need a reproducible local schema source for checklist validation.

## 1) Seed Local Validation Schema

Run:

```powershell
./scripts/seed_validation_schema.ps1
```

This creates:
- `data/companies/1/workspaces/1/connections/sqlserver-default.ini`
- `data/sqlite/sqlserver_default.db`

## 2) Start Local API

Run:

```powershell
$env:VOXCORE_ADMIN_PASSWORD='VoxCore123!'
.venv/Scripts/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

## 3) Run Checklist

Run:

```powershell
./.tmp/run_checklist.ps1
```

## Notes

- Runtime-generated `data/` artifacts are intentionally ignored by git.
- Query execution now queues successfully even if Redis is unavailable (in-memory fallback).
