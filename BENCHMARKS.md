# VoxCore SQL Benchmark Suite

## Overview
This suite provides an enterprise-grade, production-quality benchmark for evaluating the SQL generation, planning, and reliability of the VoxCore engine. It is designed to ensure correctness, robustness, and explainability for all core SQL patterns.

## Benchmark Datasets
- **voxcore/training/sql_benchmark_500.yaml**: 500 balanced queries across 10 categories
- (Recommended) **voxcore/training/sql_benchmark_edge_200.yaml**: 200 edge-case queries (future expansion)

### Distribution
- 50   basic queries
- 50   filtering queries
- 75   aggregation queries
- 75   group by queries
- 100  join queries
- 50   ranking queries
- 50   window function queries
- 50   time intelligence queries
- 25   comparison queries
- 25   advanced analytics queries

## Running the Benchmark

1. **Ensure your SQL engine implements `generate_sql(question)`**
2. Run:

```bash
python voxcore/tests/run_sql_benchmark.py
```

3. Review the output for pass/fail statistics and detailed failure analysis.

## Integration
- The benchmark is for development, CI, and model training only.
- It is never run in production or on live user queries.

## What This Provides
- SQL accuracy measurement
- Query planner evaluation
- Join and time intelligence testing
- Error repair validation

## Enterprise-Grade Reliability
- This benchmark is the gold standard for VUSE reliability.
- For maximum robustness, expand to 700 queries (500 core + 200 edge-case).

---

For questions, see 00_READ_ME_FIRST.md or contact the VoxCore engineering team.
