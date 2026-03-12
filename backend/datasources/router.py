"""
API router for datasources and semantic models.
Provides endpoints for discovering, connecting to, and managing data sources.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from backend.datasources.models import (
    PlatformInfo,
    DataSourceCreate,
    SemanticModelCreate,
    SemanticModelUpdate,
)
from backend.datasources.service import DatasourceService, SemanticModelService
from backend.db import get_db

router = APIRouter(prefix="/api/v1/datasources", tags=["datasources"])


# ═══════════════════════════════════════════════════════════════
# Platforms & Discovery
# ═══════════════════════════════════════════════════════════════


@router.get("/platforms", response_model=List[Dict[str, Any]])
async def get_available_platforms():
    """
    Get list of supported data platforms.
    
    Returns platforms ordered by tier (1=must-have, 2=important, 3=nice-to-have).
    
    Example:
    [
      {
        "code": "snowflake",
        "name": "Snowflake",
        "tier": 1,
        "available": true,
        "description": "Connect to Snowflake data warehouse"
      },
      ...
    ]
    """
    return DatasourceService.get_available_platforms()


@router.post("/test-connection")
async def test_connection(
    platform: str = Query(..., description="Platform code (snowflake, sql_server, etc.)"),
    credentials: Dict[str, Any] = Query(..., description="Platform-specific credentials"),
):
    """
    Test if connection parameters are valid.
    
    Does not save anything; just validates the connection.
    
    Returns: {"valid": true/false}
    """
    try:
        valid = DatasourceService.test_connection(platform, credentials)
        return {"valid": valid}
    except Exception as e:
        return {"valid": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# Datasources (CRUD)
# ═══════════════════════════════════════════════════════════════


@router.get("/", response_model=List[Dict[str, Any]])
async def list_datasources(
    workspace_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """List all datasources in a workspace."""
    # TODO: Query database
    return []


@router.post("/", response_model=Dict[str, Any])
async def create_datasource(
    workspace_id: int = Query(...),
    req: DataSourceCreate = None,
    db: Session = Depends(get_db),
):
    """
    Create new datasource connection.
    
    Does NOT test connection; user should call test-connection first.
    """
    if not req:
        raise HTTPException(status_code=400, detail="Missing request body")
    # TODO: Save to database
    return {"id": 1, "platform": req.platform, "name": req.name}


@router.get("/{datasource_id}", response_model=Dict[str, Any])
async def get_datasource(
    datasource_id: int,
    db: Session = Depends(get_db),
):
    """Get datasource details."""
    # TODO: Query database
    return {}


@router.delete("/{datasource_id}")
async def delete_datasource(
    datasource_id: int,
    db: Session = Depends(get_db),
):
    """Delete datasource and associated semantic models."""
    # TODO: Delete from database with cascade
    return {"deleted": True}


# ═══════════════════════════════════════════════════════════════
# Schema Discovery
# ═══════════════════════════════════════════════════════════════


@router.get("/{datasource_id}/databases", response_model=List[str])
async def list_databases(
    datasource_id: int,
    db: Session = Depends(get_db),
):
    """
    List all databases in datasource.
    
    Usage:
    GET /api/v1/datasources/1/databases
    
    Returns: ["database1", "database2", ...]
    """
    # TODO: Use cached schema or connect and discover
    return []


@router.get("/{datasource_id}/schema", response_model=Dict[str, Any])
async def get_schema(
    datasource_id: int,
    database: str = Query(None, description="Database name (required for some platforms)"),
    schema: str = Query(None, description="Schema name (optional)"),
    force_refresh: bool = Query(False, description="Skip cache and re-discover"),
    db: Session = Depends(get_db),
):
    """
    Get full schema for datasource.
    
    Returns tables and columns with metadata.
    
    Caches result for 15 minutes (unless force_refresh=true).
    """
    # TODO: Call DatasourceService.discover_schema_cached()
    return {}


# ═══════════════════════════════════════════════════════════════
# Semantic Models (CRUD)
# ═══════════════════════════════════════════════════════════════


@router.get("/models", response_model=List[Dict[str, Any]])
async def list_semantic_models(
    workspace_id: int = Query(...),
    datasource_id: Optional[int] = Query(None, description="Filter by datasource"),
    db: Session = Depends(get_db),
):
    """List all semantic models in workspace."""
    # TODO: Query database
    return []


@router.post("/models", response_model=Dict[str, Any])
async def create_semantic_model(
    workspace_id: int = Query(...),
    req: SemanticModelCreate = None,
    db: Session = Depends(get_db),
):
    """
    Create new semantic model.
    
    Semantic models are business abstractions that map business concepts
    (entities, metrics) to SQL tables and columns.
    """
    if not req:
        raise HTTPException(status_code=400, detail="Missing request body")
    # TODO: Create model
    return {"id": 1, "name": req.name}


@router.get("/models/{model_id}", response_model=Dict[str, Any])
async def get_semantic_model(
    model_id: int,
    db: Session = Depends(get_db),
):
    """Get semantic model definition."""
    # TODO: Query database
    return {}


@router.patch("/models/{model_id}", response_model=Dict[str, Any])
async def update_semantic_model(
    model_id: int,
    req: SemanticModelUpdate = None,
    db: Session = Depends(get_db),
):
    """Update semantic model."""
    if not req:
        raise HTTPException(status_code=400, detail="Missing request body")
    # TODO: Update model
    return {"id": model_id}


@router.delete("/models/{model_id}")
async def delete_semantic_model(
    model_id: int,
    db: Session = Depends(get_db),
):
    """Delete semantic model."""
    # TODO: Delete from database
    return {"deleted": True}


# ═══════════════════════════════════════════════════════════════
# Semantic Model Entities (nested CRUD)
# ═══════════════════════════════════════════════════════════════


@router.post("/models/{model_id}/entities", response_model=Dict[str, Any])
async def add_entity(
    model_id: int,
    entity_name: str = Query(...),
    entity_def: Dict[str, Any] = None,
    db: Session = Depends(get_db),
):
    """
    Add entity to semantic model.
    
    Entity example:
    {
      "name": "customers",
      "display_name": "Customer",
      "sql_table": "customers",
      "primary_key": "customer_id",
      "fields": {
        "id": {
          "sql_column": "customer_id",
          "display_name": "Customer ID"
        }
      },
      "metrics": {
        "total_revenue": {
          "sql_expression": "SUM(order_total)",
          "display_name": "Total Revenue"
        }
      }
    }
    """
    # TODO: Add entity to model
    return {"added": True}


@router.delete("/models/{model_id}/entities/{entity_name}")
async def remove_entity(
    model_id: int,
    entity_name: str,
    db: Session = Depends(get_db),
):
    """Remove entity from semantic model."""
    # TODO: Remove entity
    return {"removed": True}
