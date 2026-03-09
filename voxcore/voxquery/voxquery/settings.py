"""Configuration management for VoxQuery"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

# Load .env file explicitly - CRITICAL for environment variables
# Try multiple paths to find .env
env_paths = [
    Path(__file__).parent.parent / ".env",  # voxcore/voxquery/.env
    Path(__file__).parent.parent.parent / ".env",  # voxcore/.env
    Path.cwd() / ".env",  # Current working directory
]

for env_path in env_paths:
    if env_path.exists():
        print(f"[SETTINGS] Loading .env from: {env_path}")
        load_dotenv(env_path, override=True)  # override=True ensures env vars are updated
        break
else:
    print("[SETTINGS] Warning: No .env file found in standard locations")


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # App
    app_name: str = "VoxQuery"
    debug: bool = False
    environment: str = "development"
    
    # Warehouse Defaults (None = user must select database on startup)
    warehouse_type: Optional[str] = None  # snowflake, redshift, bigquery, postgres, sqlserver
    warehouse_host: Optional[str] = None
    warehouse_port: int = 443
    warehouse_user: Optional[str] = None
    warehouse_password: Optional[str] = None
    warehouse_database: Optional[str] = None
    warehouse_schema: str = "PUBLIC"
    
    # LLM Configuration (Groq only)
    llm_provider: str = "groq"
    llm_model: str = "llama-3.3-70b-versatile"  # Available Groq model
    llm_temperature: float = 0.0  # Deterministic for SQL generation
    llm_max_tokens: int = 768  # Reduced from 1024 to prevent over-generation
    groq_api_key: Optional[str] = None  # Groq API key for LLM calls
    
    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Query Execution
    query_timeout_seconds: int = 300
    max_result_rows: int = 100000
    enable_dry_run: bool = True
    
    # Cost Guards
    enable_cost_tracking: bool = True
    max_query_cost_usd: float = 100.0
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: list = ["http://localhost:3000", "http://localhost:8080"]

    # Admin credentials (from .env)
    voxcore_admin_username: Optional[str] = None
    voxcore_admin_password: Optional[str] = None
    
    model_config = ConfigDict(
        extra='ignore',  # Ignore extra environment variables that aren't defined fields
        case_sensitive=False,
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
    )


# Global settings instance
settings = Settings()

# CRITICAL: Ensure groq_api_key is loaded from environment
# If not set via pydantic, try to get it directly from os.environ
if not settings.groq_api_key:
    settings.groq_api_key = os.getenv("GROQ_API_KEY")
    if settings.groq_api_key:
        print(f"[SETTINGS] ✓ Loaded GROQ_API_KEY from environment")
    else:
        print(f"[SETTINGS] ✗ WARNING: GROQ_API_KEY not found in environment!")
