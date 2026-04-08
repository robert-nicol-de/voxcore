from fastapi import APIRouter, Depends
from pydantic import BaseModel
from voxcore.services.connector_service import ConnectorService

router = APIRouter(prefix="/api/connectors", tags=["connectors"])
service = ConnectorService()

# Mock user dependency (replace with real auth)
def get_current_user():
    # Example: return user object or dict with tier and permissions
    return {"id": "123", "tier": "pro", "permissions": ["data.query"]}

class ConnectorRequest(BaseModel):
    connector_type: str
    config: dict

class QueryRequest(ConnectorRequest):
    query: str

@router.post("/test")
def test_connection(req: ConnectorRequest, user=Depends(get_current_user)):
    return service.test(user, req.connector_type, req.config)

@router.post("/schema")
def get_schema(req: ConnectorRequest, user=Depends(get_current_user)):
    return service.get_schema(user, req.connector_type, req.config)

@router.post("/query")
def run_query(req: QueryRequest, user=Depends(get_current_user)):
    return service.query(user, req.connector_type, req.config, req.query)
