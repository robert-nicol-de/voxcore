"""Configuration management for VoxQuery"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # App
    app_name: str = "VoxQuery"
    debug: bool = False
    environment: str = "development"
    
    # Warehouse Defaults
    warehouse_type: str = "snowflake"  # snowflake, redshift, bigquery, postgres, sqlserver
    warehouse_host: str
    warehouse_port: int = 443
    warehouse_user: str
    warehouse_password: str
    warehouse_database: str
    warehouse_schema: str = "PUBLIC"
    
    # LLM Configuration
    llm_provider: str = "openai"  # openai, anthropic, local
    llm_model: str = "gpt-4"
    llm_api_key: Optional[str] = None
    llm_temperature: float = 0.1
    llm_max_tokens: int = 2000
    
    # LangChain Tracing
    langsmith_api_key: Optional[str] = None
    langsmith_project: str = "voxquery"
    
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
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
