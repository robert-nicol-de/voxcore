from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class IntentModel(BaseModel):
    type: Optional[str]
    confidence: Optional[float]
    entities: Optional[Dict[str, Any]]


class SQLModel(BaseModel):
    query: Optional[str]
    structured: Optional[Dict[str, Any]]


class MetadataModel(BaseModel):
    pattern: Optional[str]
    pattern_confidence: Optional[float]
    validation: Optional[Dict[str, Any]]


class RiskModel(BaseModel):
    status: Optional[str]
    score: Optional[int]
    flags: Optional[List[str]]


class TrendModel(BaseModel):
    direction: str = "flat"
    strength: int = 0

class SummaryModel(BaseModel):
    headline: str = ""
    key_takeaway: str = ""

class InsightResponse(BaseModel):
    insights: list = []
    trend: TrendModel = TrendModel()
    anomalies: list = []
    summary: SummaryModel = SummaryModel()

class QueryResponse(BaseModel):
    intent: IntentModel
    plan: Dict[str, Any]
    sql: SQLModel
    metadata: MetadataModel
    risk: RiskModel
    insight: InsightResponse
