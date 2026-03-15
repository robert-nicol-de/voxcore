# VoxCore Metric Levels

This document describes the three-level metric system for VoxCore, mapping each metric to its source/component and intended audience.

---

## Level 1 — Internal (Engineering Only)

| Metric              | Description                                 | Source/Component                |
|---------------------|---------------------------------------------|---------------------------------|
| AI Accuracy         | Benchmark/canonical question score           | benchmark_runner.py, canonical_questions.py |
| Semantic Coverage   | % of metrics/dimensions covered by tests     | semantic_coverage_analyzer.py   |
| Benchmark Score     | Aggregated score from automated test harness | benchmark_runner.py             |

- **Audience:** Engineering, CI/CD, QA
- **Visibility:** Internal dashboards, CI pipelines

---

## Level 2 — Platform Health (Owner Dashboard)

| Metric                | Description                                 | Source/Component                |
|-----------------------|---------------------------------------------|---------------------------------|
| Query Success Rate    | % of successful queries                     | backend logs, API metrics       |
| AI Response Latency   | Average/percentile response time            | backend, semantic layer         |
| Guardian Security Events | Count/type of security events             | Guardian module, event logs     |

- **Audience:** Platform owners, DevOps
- **Visibility:** Owner dashboard, monitoring tools

---

## Level 3 — Customer View

| Metric            | Description                                   | Source/Component                |
|-------------------|-----------------------------------------------|---------------------------------|
| AI Capabilities   | Supported analytics, NLQ, coverage summary    | benchmark_runner.py, docs       |
| Security Features | Guardian protections, audit, compliance       | Guardian, docs                  |
| Data Governance   | Data lineage, access controls, certifications | backend, docs                   |

- **Audience:** End customers, compliance, sales
- **Visibility:** Customer dashboard, product site, documentation

---

## Governance & Architecture Notes

VoxCore’s architecture (Brain, Semantic Layer, Insight Engine, Guardian, Benchmark system) enables:
- Stronger governance and explainability than most AI data tools
- Measurable, reportable AI quality and security
- Clear separation of internal, platform, and customer-facing metrics

**This is a major differentiator and should be highlighted in product materials.**

---

_Last updated: March 15, 2026_
