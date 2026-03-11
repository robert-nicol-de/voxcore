#!/bin/bash
set -euo pipefail

run_root() {
	if command -v sudo >/dev/null 2>&1; then
		sudo "$@"
	else
		"$@"
	fi
}

echo "======================================"
echo "VoxCore Build Script"
echo "======================================"

echo ""
echo "🔧 Installing SQL Server ODBC prerequisites (Linux)..."
if command -v apt-get >/dev/null 2>&1; then
	export DEBIAN_FRONTEND=noninteractive
	run_root apt-get update
	run_root apt-get install -y --no-install-recommends curl gnupg2 ca-certificates apt-transport-https unixodbc unixodbc-dev

	if ! odbcinst -q -d | grep -q "ODBC Driver 18 for SQL Server"; then
		echo "Adding Microsoft package repository for msodbcsql18..."
		run_root mkdir -p /etc/apt/keyrings
		curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | run_root gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg

		source /etc/os-release
		run_root sh -c "echo 'deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/ubuntu/${VERSION_ID}/prod ${VERSION_CODENAME} main' > /etc/apt/sources.list.d/microsoft-prod.list"

		run_root apt-get update
		ACCEPT_EULA=Y run_root apt-get install -y --no-install-recommends msodbcsql18
	else
		echo "ODBC Driver 18 already installed"
	fi

	echo "Installed ODBC drivers:"
	odbcinst -q -d || true
else
	echo "Skipping apt-based ODBC install (apt-get not available on this host)."
fi

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