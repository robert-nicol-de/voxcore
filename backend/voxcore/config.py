"""
PRODUCTION CONFIGURATION

Loads all environment variables and validates them for production safety.
This module ensures all required secrets and settings are present before app starts.

Usage:
    from backend.voxcore.config import settings
    
    # In production, all required values must be set
    settings.validate_production()
"""

import os
from typing import Optional
from pydantic import BaseSettings, validator
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # ============= ENVIRONMENT =============
    ENV: str = os.getenv("ENV", "dev")  # dev, staging, prod
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # ============= DATABASE =============
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///voxquery.db")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    
    # ============= REDIS =============
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_TTL_DEFAULT: int = int(os.getenv("REDIS_TTL_DEFAULT", "3600"))
    REDIS_MAX_MEMORY: str = os.getenv("REDIS_MAX_MEMORY", "256mb")
    
    # ============= API KEYS =============
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # ============= SECURITY =============
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-12345")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-jwt-key-67890")
    
    # ============= URLS =============
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # ============= LOGGING =============
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # ============= FEATURES =============
    ALLOW_CORS: bool = os.getenv("ALLOW_CORS", "false").lower() == "true"
    ALLOW_INTROSPECTION: bool = os.getenv("ALLOW_INTROSPECTION", "false").lower() == "true"
    
    # ============= DATABASE LIMITS =============
    MAX_ROWS_RETURNED: int = int(os.getenv("MAX_ROWS_RETURNED", "10000"))
    MAX_EXECUTION_TIME_SECONDS: int = int(os.getenv("MAX_EXECUTION_TIME_SECONDS", "30"))
    MAX_REQUEST_SIZE: int = int(os.getenv("MAX_REQUEST_SIZE", "10485760"))  # 10MB
    
    # ============= RATE LIMITING =============
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "5000"))
    RATE_LIMIT_PER_DAY: int = int(os.getenv("RATE_LIMIT_PER_DAY", "50000"))
    
    # ============= CACHE TTL =============
    CACHE_TTL_CHEAP: int = int(os.getenv("CACHE_TTL_CHEAP", "3600"))
    CACHE_TTL_MODERATE: int = int(os.getenv("CACHE_TTL_MODERATE", "300"))
    CACHE_TTL_EXPENSIVE: int = int(os.getenv("CACHE_TTL_EXPENSIVE", "60"))
    
    # ============= SECURITY SETTINGS =============
    REQUIRE_HTTPS: bool = os.getenv("REQUIRE_HTTPS", "false").lower() == "true"
    HSTS_MAX_AGE: int = int(os.getenv("HSTS_MAX_AGE", "31536000"))
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "480"))
    MASK_SENSITIVE_COLUMNS: bool = os.getenv("MASK_SENSITIVE_COLUMNS", "true").lower() == "true"
    ENFORCE_TENANT_ISOLATION: bool = os.getenv("ENFORCE_TENANT_ISOLATION", "true").lower() == "true"
    
    # ============= COST QUOTAS =============
    COST_QUOTA_ANALYST: int = int(os.getenv("COST_QUOTA_ANALYST", "5000"))
    COST_QUOTA_FINANCE: int = int(os.getenv("COST_QUOTA_FINANCE", "10000"))
    COST_QUOTA_EXECUTIVE: int = int(os.getenv("COST_QUOTA_EXECUTIVE", "50000"))
    
    # ============= OBSERVABILITY =============
    DATADOG_API_KEY: Optional[str] = os.getenv("DATADOG_API_KEY")
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    
    # ============= COMPLIANCE =============
    AUDIT_LOG_RETENTION_DAYS: int = int(os.getenv("AUDIT_LOG_RETENTION_DAYS", "90"))
    DATA_RETENTION_POLICY: str = os.getenv("DATA_RETENTION_POLICY", "comply_with_local_law")
    PII_ENCRYPTION_ENABLED: bool = os.getenv("PII_ENCRYPTION_ENABLED", "true").lower() == "true"
    
    class Config:
        env_file = None  # Don't load from .env in production
        case_sensitive = True
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        """Secret key must be at least 32 characters in production"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters (run: python -c 'import secrets; print(secrets.token_urlsafe(32))')")
        return v
    
    @validator("JWT_SECRET_KEY")
    def validate_jwt_secret_key(cls, v):
        """JWT secret must be at least 32 characters in production"""
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters (run: python -c 'import secrets; print(secrets.token_urlsafe(32))')")
        return v
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Production database must be PostgreSQL"""
        if "prod" in v or os.getenv("ENV") == "prod":
            if not v.startswith("postgresql://"):
                raise ValueError("Production database MUST use PostgreSQL (not SQLite)")
        return v
    
    @validator("GROQ_API_KEY")
    def validate_groq_api_key(cls, v):
        """Groq API key is required in production"""
        if os.getenv("ENV") == "prod" and not v:
            raise ValueError("GROQ_API_KEY is required in production")
        return v
    
    def validate_production(self):
        """
        Call this on app startup to ensure production readiness.
        Raises ValueError if any required settings are missing.
        """
        if self.ENV != "prod":
            return  # Skip validation for dev/staging
        
        logger.info("🔥 Validating production configuration...")
        
        errors = []
        
        # Check required secrets
        if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
            errors.append("❌ SECRET_KEY not set or too short (min 32 chars)")
        
        if not self.JWT_SECRET_KEY or len(self.JWT_SECRET_KEY) < 32:
            errors.append("❌ JWT_SECRET_KEY not set or too short (min 32 chars)")
        
        if not self.GROQ_API_KEY:
            errors.append("❌ GROQ_API_KEY not set")
        
        # Check database
        if not self.DATABASE_URL.startswith("postgresql://"):
            errors.append("❌ DATABASE_URL must use PostgreSQL (not SQLite)")
        
        if not self.DATABASE_URL:
            errors.append("❌ DATABASE_URL not set")
        
        # Check Redis
        if not self.REDIS_URL:
            errors.append("❌ REDIS_URL not set")
        
        if "password" not in self.REDIS_URL and not self.REDIS_URL.startswith("redis://"):
            errors.append("⚠️  REDIS_URL should include password for production")
        
        # Check URLs
        if self.FRONTEND_URL in ["http://localhost:3000", "http://localhost"]:
            errors.append("❌ FRONTEND_URL configured for local development (not production)")
        
        if self.BACKEND_URL in ["http://localhost:8000", "http://localhost"]:
            errors.append("❌ BACKEND_URL configured for local development (not production)")
        
        # Check security settings
        if not self.REQUIRE_HTTPS:
            errors.append("⚠️  REQUIRE_HTTPS not enforced")
        
        # Check logging
        if self.DEBUG:
            errors.append("⚠️  DEBUG mode enabled in production")
        
        if self.LOG_LEVEL == "DEBUG":
            errors.append("⚠️  LOG_LEVEL set to DEBUG in production")
        
        # Check CORS
        if self.ALLOW_CORS:
            errors.append("⚠️  CORS all-origins enabled (should be restricted)")
        
        # Report findings
        if errors:
            logger.error("🔴 PRODUCTION CONFIGURATION ERRORS:")
            for error in errors:
                logger.error(f"   {error}")
            raise ValueError(f"Production configuration has {len(errors)} errors")
        
        logger.info("✅ All production settings validated!")
        logger.info(f"   Database: PostgreSQL")
        logger.info(f"   Redis: Configured")
        logger.info(f"   Frontend: {self.FRONTEND_URL}")
        logger.info(f"   Backend: {self.BACKEND_URL}")
        logger.info(f"   Security: Enforced")


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get global settings instance"""
    return settings


# Validate on import if production
if os.getenv("ENV") == "prod":
    try:
        settings.validate_production()
        logger.info("✅ PRODUCTION CONFIGURATION VALID")
    except ValueError as e:
        logger.error(f"❌ PRODUCTION CONFIGURATION INVALID: {e}")
        raise
