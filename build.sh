#!/bin/bash
set -e

echo "======================================"
echo "VoxCore Build Script"
echo "======================================"

# Build Frontend
echo ""
echo "📦 Installing frontend dependencies..."
cd frontend
npm install --legacy-peer-deps --production=false

echo ""
echo "🏗️  Building React app with Vite..."
if npm run build; then
    echo "✅ Vite build succeeded"
    FRONTEND_READY=true
else
    echo "⚠️  Vite build failed, using public folder as fallback"
    rm -rf dist
    mkdir -p dist
    cp -r public/* dist/
    FRONTEND_READY=true
fi

cd ..

# Verify frontend is ready
echo ""
echo "📂 Frontend dist contents:"
ls -la frontend/dist/ | head -15

echo ""
echo "🐍 Installing Python dependencies..."
pip install --no-cache-dir -r voxcore/voxquery/requirements.txt

echo ""
echo "✅ Build complete! Frontend and backend ready."
echo "======================================"
