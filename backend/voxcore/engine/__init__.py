"""
VoxCore engine - The 14-step pipeline orchestrator.

This is where the 14 STEPS of every request are executed:
1. Auth
2. Rate limit
3. Intent + State
4. Query build
5. Tenant enforcement
6. Policy engine
7. Cost check
8. Cache check
9. Execute query
10. Sanitize results
11. Generate metadata
12. Cache result
13. Track metrics
14. Return response
"""
