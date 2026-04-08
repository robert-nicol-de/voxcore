from pydantic import BaseModel
from typing import Dict, Any, Optional

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    data: Dict[str, Any]
    insights: Optional[Dict[str, Any]] = None
