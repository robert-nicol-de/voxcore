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
		if [ "${ID:-}" = "ubuntu" ]; then
			REPO_URL="https://packages.microsoft.com/ubuntu/${VERSION_ID}/prod"
			REPO_SUITE="${VERSION_CODENAME}"
		elif [ "${ID:-}" = "debian" ]; then
			MAJOR_VERSION="${VERSION_ID%%.*}"
			REPO_URL="https://packages.microsoft.com/debian/${MAJOR_VERSION}/prod"
			REPO_SUITE="${VERSION_CODENAME}"
		else
			REPO_URL=""
			REPO_SUITE=""
			echo "Unsupported distro for automatic Microsoft ODBC repo setup: ${ID:-unknown}"
		fi

		if [ -n "$REPO_URL" ] && [ -n "$REPO_SUITE" ]; then
			run_root sh -c "echo 'deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] ${REPO_URL} ${REPO_SUITE} main' > /etc/apt/sources.list.d/microsoft-prod.list"
		fi

		run_root apt-get update

		if apt-cache show msodbcsql18 >/dev/null 2>&1; then
			ACCEPT_EULA=Y run_root apt-get install -y --no-install-recommends msodbcsql18
		elif apt-cache show msodbcsql17 >/dev/null 2>&1; then
			ACCEPT_EULA=Y run_root apt-get install -y --no-install-recommends msodbcsql17
		else
			echo "Microsoft SQL Server ODBC package not available from apt sources."
			echo "Install manually and verify with: odbcinst -q -d"
			exit 1
		fi
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