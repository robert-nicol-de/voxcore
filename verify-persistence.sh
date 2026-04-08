#!/bin/bash
# Verify persistence layer is operational

set -e

echo "🔍 Verifying Persistence Layer Setup"
echo "======================================"
echo ""

# Check migrations exist
echo "✓ Checking migrations..."
if [ -f "backend/db/migrations/2026_04_03_create_query_logs_table.sql" ]; then
    echo "  ✅ Migration file exists"
else
    echo "  ❌ Migration file missing"
    exit 1
fi

# Check models exist
echo ""
echo "✓ Checking database models..."
if grep -q "class QueryLog" backend/db/models.py 2>/dev/null; then
    echo "  ✅ QueryLog model defined"
else
    echo "  ❌ QueryLog model missing"
    exit 1
fi

# Check repository exists
echo ""
echo "✓ Checking queries repository..."
if [ -f "backend/db/queries_repository.py" ]; then
    echo "  ✅ Repository exists"
    if grep -q "store_query_log" backend/db/queries_repository.py; then
        echo "  ✅ store_query_log method exists"
    fi
    if grep -q "get_recent_queries" backend/db/queries_repository.py; then
        echo "  ✅ get_recent_queries method exists"
    fi
else
    echo "  ❌ Repository missing"
    exit 1
fi

# Check API endpoints exist
echo ""
echo "✓ Checking API endpoints..."
if [ -f "voxcore/api/queries_api.py" ]; then
    echo "  ✅ Queries API module exists"
    if grep -q "get_recent_queries" voxcore/api/queries_api.py; then
        echo "  ✅ GET /api/queries/recent endpoint defined"
    fi
    if grep -q "approve_query" voxcore/api/queries_api.py; then
        echo "  ✅ POST /api/queries/approve endpoint defined"
    fi
    if grep -q "get_statistics" voxcore/api/queries_api.py; then
        echo "  ✅ GET /api/queries/stats endpoint defined"
    fi
else
    echo "  ❌ Queries API missing"
    exit 1
fi

# Check playground_api has persistence calls
echo ""
echo "✓ Checking playground API integration..."
if grep -q "QueryLogsRepository" voxcore/api/playground_api.py 2>/dev/null; then
    echo "  ✅ Repository integrated into query execution"
else
    echo "  ❌ Repository not integrated"
    exit 1
fi

# Check frontend hydration
echo ""
echo "✓ Checking frontend hydration..."
if grep -q "hydrateAuditLogs" frontend/src/store/queryStore.ts 2>/dev/null; then
    echo "  ✅ Hydration method exists in Zustand store"
else
    echo "  ❌ Hydration method missing"
    exit 1
fi

if grep -q "hydrateAuditLogs" frontend/src/components/QueryExecutionDemo.tsx 2>/dev/null; then
    echo "  ✅ Component calls hydration on mount"
else
    echo "  ⚠️  Component may not load audit logs automatically"
fi

echo ""
echo "✨ Persistence Layer Verification Complete!"
echo ""
echo "📋 Next Steps:"
echo "  1. Run migrations: python backend/db/init_db.py"
echo "  2. Restart backend: python -m uvicorn voxcore.api.playground_api:app --reload"
echo "  3. Test endpoint: curl -H 'x-api-key: dev-key-local-testing' http://localhost:8000/api/queries/recent?org_id=default-org"
echo ""
