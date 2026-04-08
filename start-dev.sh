#!/bin/bash
# VoxCore Local Development Startup
# Usage: bash start-dev.sh

set -e

echo "🚀 VoxCore Development Environment"
echo "===================================="
echo ""

# Check if .env files exist
if [ ! -f "frontend/.env.development" ]; then
    echo "❌ frontend/.env.development not found"
    echo "Creating from template..."
    cat > frontend/.env.development << EOF
VITE_API_URL=http://localhost:8000
VITE_API_KEY=dev-key-local-testing
EOF
fi

if [ ! -f "backend/.env.development" ]; then
    echo "❌ backend/.env.development not found"
    echo "Creating from template..."
    cat > backend/.env.development << EOF
ENV=development
DEBUG=true
LOG_LEVEL=debug
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=dev-key-local-testing-only
SECRET_KEY=dev-secret-key-not-secure-change-in-prod
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
DATABASE_URL=sqlite:///voxquery.db
MAX_ROWS=500
QUERY_TIMEOUT=5
MAX_QUERIES_PER_MINUTE=60
REQUEST_TIMEOUT=30
EOF
fi

echo "✅ Environment files ready"
echo ""

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
else
    echo "   (node_modules already exists)"
fi
cd ..
echo "✅ Frontend ready"
echo ""

# Install backend dependencies
echo "📦 Installing backend dependencies..."
if [ -f "backend/requirements.txt" ]; then
    pip install -r backend/requirements.txt > /dev/null 2>&1 || true
    echo "✅ Backend ready"
fi
echo ""

# Show startup commands
echo "🎯 Ready to develop!"
echo ""
echo "Start development servers (in separate terminals):"
echo ""
echo "Terminal 1 - Frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "Terminal 2 - Backend:"
echo "  export ENV=development"
echo "  python -m uvicorn voxcore.api.playground_api:app --reload --port 8000"
echo ""
echo "Or run together:"
echo "  npm run dev  (from root directory)"
echo ""
echo "Then visit:"
echo "  Frontend: http://localhost:5173"
echo "  API Docs: http://localhost:8000/docs"
echo ""
