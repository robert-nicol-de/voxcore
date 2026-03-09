#!/bin/bash

echo "======================================"
echo "VoxCore Build Script"
echo "======================================"

echo ""
echo "✅ Serving marketing site from frontend/public/"
echo "   Available at: / (index.html)"
echo "   API docs at: /docs (Swagger UI)"

echo ""
echo "🐍 Installing Python dependencies..."
pip install --no-cache-dir -r voxcore/voxquery/requirements.txt

echo ""
echo "⚛️  Building React frontend..."
cd frontend
npm install
npm run build
cd ..

echo ""
echo "✅ Build complete! VoxCore ready to start."
echo "======================================