# Definition of Done (DoD) for VoxCore

Every task must satisfy its `definition_of_done` checklist in `build_phases.yaml` before it can be marked as complete (`done`).

## Example

```
id: P1-1
description: PostgreSQL connector
definition_of_done:
  - Can connect to DB
  - Can run SELECT query
  - Returns results in API
  - Covered by test
status: not-started
demo: null
```

## Enforcement
- The CLI (`buildctl.py`) will block marking a task as `done` unless all checklist items are satisfied.
- CI/CD will enforce this for every phase and task.

## Why?
- Prevents incomplete work from being marked as finished
- Ensures production readiness
- Guarantees demo and integration coverage

## How to Use
- Update the checklist as you work
- Mark `checklist_complete: true` in the YAML when all items are satisfied
- Only then mark the task as `done`

---

**This is a core discipline for enterprise-grade engineering.**
