# VoxCore AI Failure Handling System (AFHS)

This document describes the architecture, goals, and implementation plan for VoxCore's AI Failure Handling System (AFHS), which ensures every AI request is validated, recoverable, and explainable.

---

## Core Principle
AI must fail safely, transparently, and recoverably.

## Core Goals
- Prevent bad SQL from reaching databases
- Detect AI reasoning failures
- Attempt automated recovery
- Provide clear user feedback
- Log failures for system learning
- Continuously improve semantic coverage

## High-Level Architecture

```mermaid
graph TD
    A[User Query] --> B[Intent Parser]
    B --> C[Semantic Mapper]
    C --> D[SQL Generator]
    D --> E[AI Failure Handling System (AFHS)]
    E -->|Auto Recovery| F[Auto Recovery Engine]
    E -->|Clarification| G[Clarification Engine]
    F --> H[Guardian SQL Validator]
    G --> I[User Clarification]
    H --> J[Safe SQL Execution]
    J --> K[Result Delivery]
```

- The AFHS intercepts problems before execution, routes to recovery or clarification, and ensures only safe SQL is executed.

## The Five Failure Categories

1. **Semantic Failure**
   - Unknown metric, missing mapping, ambiguous entity
   - Response: Suggest possible matches
2. **SQL Generation Failure**
   - Invalid/missing tables, columns, or syntax
   - Recovery: Multi-attempt self-correction, escalate if needed
3. **Logical Failure**
   - SQL is valid but logically incorrect (e.g., wrong metric)
   - Solution: Metric validator layer
4. **Database Execution Failure**
   - Timeout, unavailable warehouse, permission denied
   - Recovery: Retry, switch warehouse, simplify, partial result
5. **Ambiguous Intent**
   - Multiple possible meanings
   - Response: Ask user to clarify

## Recovery Engine
- Attempts multiple correction strategies (regenerate SQL, use templates, simplify, escalate)

## Failure Logging System
- Every failure is logged with:
  - timestamp, user_question, failure_type, semantic_entity_missing, sql_generated, sql_error, recovery_attempts, final_resolution
- Logs feed into the Semantic Coverage Analyzer

## Safe Failure Response Types
- Always return structured, actionable responses (not generic errors)
- Examples:
  - Semantic failure: Suggest possible metrics
  - SQL failure: Report correction attempts
  - Ambiguous: Ask user to select

## Guardian Integration
- Guardian acts as the last safety gate:
  - Blocks dangerous SQL, full-table scans, schema violations, enforces limits

## System State Levels
| State   | Meaning              |
|---------|----------------------|
| GREEN   | High confidence      |
| YELLOW  | Possible ambiguity   |
| ORANGE  | AI corrected itself  |
| RED     | AI failure           |

- Every request receives a confidence classification for monitoring and dashboards.

## Fallback Mode
- If AI cannot answer, switch to Guided Query Mode (user selects dataset, metric, etc.)

## Production-Level Reliability Mechanisms
- Multi-attempt reasoning loop
- Structured failure taxonomy
- Failure telemetry
- Automated learning pipeline
- Semantic gap detection

## The Most Important Rule
Wrong answers are worse than failed answers. VoxCore must always prefer safe failure over confident hallucination.

## Recommended Internal Services
- AI Failure Detection Service
- AI Recovery Engine
- Semantic Gap Detector
- SQL Validator
- Guardian Safety Engine
- Failure Telemetry Service

---

_This system is a major enterprise differentiator for VoxCore._

_Last updated: March 15, 2026_
