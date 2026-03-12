"""
Data models for datasources and semantic models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# Datasource Platform Models
# ═══════════════════════════════════════════════════════════════


class PlatformInfo(BaseModel):
    """Information about a supported data platform."""

    code: str  # 'snowflake', 'bigquery', 'sql_server', etc.
    name: str  # 'Snowflake', 'BigQuery', etc.
    tier: int  # 1=must-have, 2=important, 3=nice-to-have
    description: str
    logo_url: Optional[str] = None
    available: bool = True  # Can be disabled if dependencies missing
    doc_url: Optional[str] = None


class DataSource(BaseModel):
    """A configured connection to a data platform."""

    id: Optional[int] = None
    workspace_id: int
    platform: str  # 'snowflake', 'sql_server', etc.
    name: str  # User-friendly name
    credentials: Dict[str, Any]  # Platform-specific (user, password, account, etc.)
    schema_cache: Optional[Dict[str, Any]] = None  # Cached schema discovery
    schema_cache_at: Optional[datetime] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DataSourceCreate(BaseModel):
    """Request to create a new datasource."""

    platform: str
    name: str
    credentials: Dict[str, Any]


# ═══════════════════════════════════════════════════════════════
# Schema Models
# ═══════════════════════════════════════════════════════════════


class ColumnSchema(BaseModel):
    """Column definition in table schema."""

    name: str
    type: str
    nullable: bool = True
    primary_key: bool = False
    sensitive: Optional[str] = None  # 'PII', 'sensitive', etc.


class TableSchema(BaseModel):
    """Table definition in database schema."""

    name: str
    schema: Optional[str] = None
    rows_estimate: int = 0
    columns: List[ColumnSchema] = []


class DatabaseSchema(BaseModel):
    """Complete database schema structure."""

    database: str
    schema: Optional[str] = None
    tables: List[TableSchema] = []


# ═══════════════════════════════════════════════════════════════
# Semantic Models
# ═══════════════════════════════════════════════════════════════


class SemanticField(BaseModel):
    """Field definition in semantic model entity."""

    sql_column: str  # Column name in actual table
    display_name: str  # User-friendly name
    description: Optional[str] = None
    field_type: str  # 'dimension', 'metric', 'id'


class SemanticMetric(BaseModel):
    """Metric definition (aggregation)."""

    name: str
    display_name: str
    sql_expression: str  # e.g., "SUM(order_total)"
    description: Optional[str] = None


class SemanticEntity(BaseModel):
    """Business entity definition."""

    name: str  # 'customers', 'orders', etc.
    display_name: str
    description: Optional[str] = None
    sql_table: str  # Actual table name
    sql_schema: Optional[str] = None
    primary_key: str  # Column name (e.g., 'customer_id')
    fields: Dict[str, SemanticField] = {}  # name -> field
    metrics: Dict[str, SemanticMetric] = {}  # name -> metric


class SemanticModel(BaseModel):
    """Business semantic model (maps business concepts to SQL tables)."""

    id: Optional[int] = None
    workspace_id: int
    datasource_id: int  # Link to specific datasource
    name: str  # 'Customer Analytics', 'Finance Model', etc.
    description: Optional[str] = None
    entities: Dict[str, SemanticEntity] = {}  # entity_name -> definition
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SemanticModelCreate(BaseModel):
    """Request to create semantic model."""

    datasource_id: int
    name: str
    description: Optional[str] = None


class SemanticModelUpdate(BaseModel):
    """Request to update semantic model."""

    name: Optional[str] = None
    description: Optional[str] = None
    entities: Optional[Dict[str, SemanticEntity]] = None


# ═══════════════════════════════════════════════════════════════
# Query Context Models (for AI)
# ═══════════════════════════════════════════════════════════════


class SemanticQueryContext(BaseModel):
    """
    Context for AI to generate queries using semantic model.
    Includes both semantic definitions and underlying SQL schema.
    """

    semantic_model: SemanticModel
    available_entities: List[str]  # Entity names AI can ask about
    entity_relationships: Dict[str, List[str]] = {}  # Which entities relate to each other
    query_hints: Optional[List[str]] = None  # e.g., ["Use entity 'customers'", "Filter by date"]
