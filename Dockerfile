FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    dirmngr \
    unixodbc \
    unixodbc-dev \
    gcc \
    g++ \
    build-essential \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# Add Microsoft repository for SQL Server ODBC driver
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft-rolling.asc \
    | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg
RUN mkdir -p /root/.gnupg && chmod 700 /root/.gnupg
RUN gpg --batch --no-default-keyring \
    --keyring /usr/share/keyrings/microsoft-prod.gpg \
    --keyserver hkps://keyserver.ubuntu.com \
    --recv-keys EB3E94ADBE1229CF
RUN . /etc/os-release; \
    DEBIAN_VERSION="${VERSION_ID%%.*}"; \
    if [ "$DEBIAN_VERSION" -ge 12 ]; then REPO_VERSION=12; else REPO_VERSION=11; fi; \
    curl -fsSL "https://packages.microsoft.com/config/debian/${REPO_VERSION}/prod.list" \
    | sed 's#deb \[arch=amd64\]#deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg]#' \
    > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update

# Install SQL Server ODBC Driver
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ /app/backend/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run API server
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
