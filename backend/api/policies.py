from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.policy_engine import (
    apply_policies,
    get_company_policies,
    save_company_policies,
    suggest_sensitive_columns,
)


router = APIRouter()


class PolicyUpdateRequest(BaseModel):
    policies: Dict[str, Any] = Field(default_factory=dict)


class QueryPolicyTestRequest(BaseModel):
    query: str


class SensitiveSuggestRequest(BaseModel):
    columns: List[str]


@router.get("/api/v1/policies/{company_id}")
def get_policies(company_id: str):
    return {
        "company_id": company_id,
        "policies": get_company_policies(company_id),
    }


@router.put("/api/v1/policies/{company_id}")
def update_policies(company_id: str, request: PolicyUpdateRequest):
    merged = save_company_policies(company_id, request.policies)
    return {
        "ok": True,
        "company_id": company_id,
        "policies": merged,
    }


@router.post("/api/v1/policies/{company_id}/test-query")
def test_query_against_policies(company_id: str, request: QueryPolicyTestRequest):
    result = apply_policies(company_id, request.query)
    if result["blocked"]:
        return {
            "allowed": False,
            "message": "Query blocked by VoxCore policy",
            **result,
        }
    return {
        "allowed": True,
        "message": "Query allowed by policy",
        **result,
    }


@router.post("/api/v1/policies/suggest-sensitive-columns")
def suggest_columns(request: SensitiveSuggestRequest):
    return {
        "suggested_sensitive_columns": suggest_sensitive_columns(request.columns)
    }
