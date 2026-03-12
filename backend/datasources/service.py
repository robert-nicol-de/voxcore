"""
Business logic for datasources and semantic models.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# Database Models (for SQLAlchemy)
# ═══════════════════════════════════════════════════════════════


class DataSourceDB:
    """SQLAlchemy model for DataSource."""

    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, nullable=False, index=True)
    platform = Column(String(50), nullable=False)  # 'snowflake', 'bigquery', etc.
    name = Column(String(255), nullable=False)
    credentials = Column(JSON, nullable=False)  # Encrypted in practice
    schema_cache = Column(JSON, nullable=True)
    schema_cache_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SemanticModelDB:
    """SQLAlchemy model for SemanticModel."""

    __tablename__ = "semantic_models"

    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, nullable=False, index=True)
    datasource_id = Column(Integer, nullable=False)  # Foreign key to data_sources
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    definition = Column(JSON, nullable=False)  # Full semantic model as JSON
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════
# Service Logic
# ═══════════════════════════════════════════════════════════════


class DatasourceService:
    """Manages datasources and their connections."""

    CACHE_TTL_MINUTES = 15  # Cache schema for 15 minutes
    SUPPORTED_PLATFORMS = {
        "sql_server": {"tier": 1, "name": "SQL Server", "available": True},
        "snowflake": {"tier": 1, "name": "Snowflake", "available": True},
        "postgres": {"tier": 1, "name": "PostgreSQL", "available": True},
        "bigquery": {"tier": 2, "name": "BigQuery", "available": True},
        "redshift": {"tier": 2, "name": "Amazon Redshift", "available": True},
        "mysql": {"tier": 3, "name": "MySQL", "available": True},
        "sqlite": {"tier": 3, "name": "SQLite", "available": True},
    }

    @staticmethod
    def get_available_platforms() -> List[Dict[str, Any]]:
        """Return list of supported platforms ordered by tier."""
        platforms = []
        for code, info in DatasourceService.SUPPORTED_PLATFORMS.items():
            platforms.append(
                {
                    "code": code,
                    "name": info["name"],
                    "tier": info["tier"],
                    "available": info["available"],
                    "description": f"Connect to {info['name']} data warehouse",
                }
            )
        return sorted(platforms, key=lambda p: (p["tier"], p["name"]))

    @staticmethod
    def get_driver(platform: str, connection_params: Dict[str, Any]):
        """Factory method to get appropriate driver for platform."""
        if platform == "snowflake":
            from .drivers.snowflake_driver import SnowflakeDriver

            return SnowflakeDriver(connection_params)
        elif platform == "sql_server":
            # TODO: Enhance SQL Server driver for datasource context
            from backend.schema.drivers.sqlserver_driver import SQLServerDriver

            return SQLServerDriver(connection_params)
        elif platform == "postgres":
            from backend.schema.drivers.postgres_driver import PostgreSQLDriver

            return PostgreSQLDriver(connection_params)
        elif platform == "bigquery":
            # TODO: Implement BigQuery driver
            raise NotImplementedError("BigQuery driver coming soon")
        elif platform == "redshift":
            # TODO: Implement Redshift driver (similar to PostgreSQL)
            raise NotImplementedError("Redshift driver coming soon")
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    @staticmethod
    def test_connection(platform: str, credentials: Dict[str, Any]) -> bool:
        """Test if connection parameters are valid."""
        try:
            driver = DatasourceService.get_driver(platform, credentials)
            connected = driver.connect()
            if connected:
                result = driver.test_connection()
                driver.disconnect()
                return result
            return False
        except Exception as e:
            logger.error(f"Connection test failed for {platform}: {e}")
            return False

    @staticmethod
    def discover_schema_cached(
        db: Session,
        workspace_id: int,
        datasource_id: int,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Get schema, using cache if available and fresh.
        TTL is 15 minutes.
        """
        # TODO: Query database for cached schema
        # if not force_refresh and cache is fresh:
        #   return cached_schema
        # otherwise, fetch fresh and cache
        raise NotImplementedError()


class SemanticModelService:
    """Manages semantic models (business abstractions)."""

    @staticmethod
    def create_model(
        db: Session,
        workspace_id: int,
        datasource_id: int,
        name: str,
        description: Optional[str] = None,
    ):
        """Create new semantic model."""
        # TODO: Insert into semantic_models table
        raise NotImplementedError()

    @staticmethod
    def get_model(db: Session, model_id: int):
        """Get semantic model by ID."""
        # TODO: Query semantic_models table
        raise NotImplementedError()

    @staticmethod
    def list_models(db: Session, workspace_id: int) -> List[Dict[str, Any]]:
        """List all semantic models in workspace."""
        # TODO: Query semantic_models table filtered by workspace_id
        raise NotImplementedError()

    @staticmethod
    def update_model(db: Session, model_id: int, update_data: Dict[str, Any]):
        """Update semantic model definition."""
        # TODO: Update semantic_models table
        raise NotImplementedError()

    @staticmethod
    def delete_model(db: Session, model_id: int):
        """Delete semantic model."""
        # TODO: Delete from semantic_models table
        raise NotImplementedError()

    @staticmethod
    def add_entity(
        db: Session,
        model_id: int,
        entity_name: str,
        entity_def: Dict[str, Any],
    ):
        """Add/update entity in semantic model."""
        # TODO: Merge entity into model's definition JSON
        raise NotImplementedError()

    @staticmethod
    def remove_entity(db: Session, model_id: int, entity_name: str):
        """Remove entity from semantic model."""
        # TODO: Remove entity from model's definition JSON
        raise NotImplementedError()
