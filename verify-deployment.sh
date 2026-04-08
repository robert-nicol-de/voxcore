#!/bin/bash
# VoxCore Pre-Deployment Verification Script

set -e

echo "🚀 VoxCore Pre-Deployment Checklist"
echo "===================================="
echo ""

# ====== FRONTEND CHECKS ======
echo "📱 Frontend Checks"
echo "─────────────────"

if [ ! -f "frontend/package.json" ]; then
    echo "❌ frontend/package.json not found"
    exit 1
fi
echo "✅ frontend/package.json exists"

if [ ! -f "frontend/.env.production" ]; then
    echo "❌ frontend/.env.production not found"
    exit 1
fi
echo "✅ frontend/.env.production exists"

if [ ! -f "frontend/vite.config.ts" ]; then
    echo "❌ frontend/vite.config.ts not found"
    exit 1
fi
echo "✅ frontend/vite.config.ts exists"

if grep -q "sourcemap: false" frontend/vite.config.ts; then
    echo "✅ Sourcemaps disabled (production optimization)"
else
    echo "⚠️  Warning: Sourcemaps may not be disabled"
fi

# ====== BACKEND CHECKS ======
echo ""
echo "⚙️  Backend Checks"
echo "──────────────────"

if [ ! -f "backend/.env.production" ]; then
    echo "❌ backend/.env.production not found"
    exit 1
fi
echo "✅ backend/.env.production exists"

if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ backend/requirements.txt not found"
    exit 1
fi
echo "✅ backend/requirements.txt exists"

if grep -q "slowapi" backend/requirements.txt; then
    echo "✅ Rate limiting (slowapi) configured"
else
    echo "⚠️  Warning: slowapi not in requirements.txt"
fi

if [ ! -f "backend/middleware.py" ]; then
    echo "❌ backend/middleware.py not found"
    exit 1
fi
echo "✅ backend/middleware.py (auth/CORS/logging) exists"

# ====== ENVIRONMENT FILES ======
echo ""
echo "🔐 Environment Files"
echo "────────────────────"

# Frontend env files
for env in development staging production; do
    if [ -f "frontend/.env.$env" ]; then
        echo "✅ frontend/.env.$env exists"
    else
        echo "⚠️  Warning: frontend/.env.$env missing (might be needed)"
    fi
done

# Backend env files
for env in development staging production; do
    if [ -f "backend/.env.$env" ]; then
        echo "✅ backend/.env.$env exists"
    else
        echo "⚠️  Warning: backend/.env.$env missing (might be needed)"
    fi
done

# ====== DEPLOYMENT CONFIGS ======
echo ""
echo "📋 Deployment Configs"
echo "─────────────────────"

if [ -f "frontend/vercel.json" ]; then
    echo "✅ frontend/vercel.json (Vercel config) exists"
else
    echo "⚠️  Warning: frontend/vercel.json might be needed"
fi

if [ -f "DEPLOYMENT_GUIDE.md" ]; then
    echo "✅ DEPLOYMENT_GUIDE.md exists"
else
    echo "⚠️  Warning: DEPLOYMENT_GUIDE.md not found"
fi

# ====== API LAYER ======
echo ""
echo "🔌 API Layer"
echo "────────────"

if grep -q "verify_api_key" voxcore/api/playground_api.py; then
    echo "✅ API key authentication configured"
else
    echo "⚠️  Warning: API key authentication may not be configured"
fi

if grep -q "log_query_execution" voxcore/api/playground_api.py; then
    echo "✅ Query execution logging configured"
else
    echo "⚠️  Warning: Query execution logging may not be configured"
fi

# ====== FINAL SUMMARY ======
echo ""
echo "✅ All critical checks passed!"
echo ""
echo "Next steps:"
echo "1. Update API keys in .env files with real values"
echo "2. Configure database URLs in backend/.env.production"
echo "3. Push to GitHub"
echo "4. Connect to Vercel (frontend)"
echo "5. Connect to Render (backend)"
echo ""
echo "See DEPLOYMENT_GUIDE.md for detailed instructions."
