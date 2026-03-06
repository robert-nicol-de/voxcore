# VoxQuery Backend API Endpoints

**Base URL**: `http://localhost:8000`

## Health & Status

- `GET /health` - Basic health check
- `GET /ready` - Readiness check
- `GET /health/connection` - Connection health check
- `GET /metrics/health` - Metrics health check

## Query Endpoints

- `POST /api/v1/query` - Execute a natural language question
  ```json
  {
    "question": "What is our total balance?",
    "warehouse": "snowflake",
    "execute": true,
    "dry_run": false,
    "session_id": "test"
  }
  ```

- `POST /api/v1/query/validate` - Validate SQL syntax
  ```json
  {
    "sql": "SELECT * FROM accounts"
  }
  ```

- `POST /api/v1/query/explain` - Explain SQL query
  ```json
  {
    "sql": "SELECT * FROM accounts WHERE balance > 1000"
  }
  ```

## Schema Endpoints

- `GET /api/v1/schema` - Get full database schema
- `GET /api/v1/schema/tables` - List all tables
- `GET /api/v1/schema/tables/{table_name}` - Get specific table schema
- `POST /api/v1/schema/generate-questions` - Generate suggested questions
  ```json
  {
    "warehouse_type": "snowflake",
    "limit": 4
  }
  ```

## Connection Endpoints

- `POST /api/v1/connection/test` - Test database connection
  ```json
  {
    "warehouse_type": "snowflake",
    "host": "we08391.af-south-1.aws",
    "database": "VOXQUERY_DB",
    "username": "VOXQUERY_USER",
    "password": "VoxQuery@2024"
  }
  ```

## Auth Endpoints

- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/connect` - Connect to database

## Metrics Endpoints

- `GET /metrics/repair-stats` - Get repair statistics
- `GET /metrics/top-patterns` - Get top error patterns

## Documentation

- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation
- `GET /openapi.json` - OpenAPI schema

## Testing

Try these in your browser or with curl:

```bash
# Health check
curl http://localhost:8000/health

# Get schema
curl http://localhost:8000/api/v1/schema

# Generate questions
curl -X POST http://localhost:8000/api/v1/schema/generate-questions \
  -H "Content-Type: application/json" \
  -d '{"warehouse_type": "snowflake", "limit": 4}'

# Ask a question
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is our total balance?",
    "warehouse": "snowflake",
    "execute": true,
    "dry_run": false,
    "session_id": "test"
  }'
```

## Status

✅ Backend running on port 8000
✅ All endpoints available
✅ CORS enabled for frontend
✅ Mock schema available
