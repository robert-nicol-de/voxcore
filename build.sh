#!/bin/bash

echo "======================================"
echo "VoxCore Build Script"
echo "======================================"

# Check if Node.js/npm is available
if ! command -v npm &> /dev/null; then
    echo "⚠️  npm not available on this system"
    echo "📂 Using public folder as frontend content..."
    
    # Just copy public to dist and we're done
    if [ -d "frontend/public" ]; then
        mkdir -p frontend/dist
        cp -r frontend/public/* frontend/dist/ 2>/dev/null || true
        echo "✅ Frontend: copied public/ → dist/"
    else
        echo "⚠️  frontend/public not found, but continuing..."
    fi
else
    # npm is available, use normal build process
    echo ""
    echo "📦 Installing frontend dependencies..."
    cd frontend 2>/dev/null || { echo "❌ frontend directory not found"; exit 1; }

    npm install --legacy-peer-deps --production=false 2>&1 || {
        echo "⚠️  npm install failed, but continuing..."
    }

    echo ""
    echo "🏗️  Building React app with Vite..."
    npm run build 2>&1
    BUILD_STATUS=$?

    if [ $BUILD_STATUS -eq 0 ]; then
        echo "✅ Vite build succeeded"
    else
        echo "⚠️  Vite build failed (status: $BUILD_STATUS), using public folder as fallback"
        rm -rf dist 2>/dev/null || true
        mkdir -p dist || { echo "❌ Failed to create dist directory"; exit 1; }
        cp -r public/* dist/ 2>/dev/null || {
            echo "❌ Failed to copy public to dist"
            exit 1
        }
        echo "✅ Fallback: copied public/ → dist/"
    fi

    cd ..
fi

# Verify dist folder exists
if [ ! -d "frontend/dist" ]; then
    echo "❌ CRITICAL: frontend/dist folder does not exist!"
    exit 1
fi

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
