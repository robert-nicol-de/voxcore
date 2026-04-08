"""
API endpoints for query log persistence.

Provides REST endpoints for:
- Storing query executions in database
- Retrieving recent queries
- Accessing query statistics
- Approving pending queries
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.middleware import verify_api_key, logger
from backend.db.queries_repository import QueryLogsRepository

# Create router
router = APIRouter(prefix="/api/queries", tags=["Queries"])

# ==================
# Request/Response Models
# ==================

class RecentQueriesRequest(BaseModel):
	org_id: str
	limit: int = 50
	status: Optional[str] = None
	user_id: Optional[str] = None
	environment: Optional[str] = None

class QueryLogResponse(BaseModel):
	query_id: str
	org_id: str
	user_id: Optional[str]
	sql: str
	fingerprint: str
	risk_score: int
	status: str
	confidence: float
	reasons: Optional[str]
	environment: str
	source: Optional[str]
	session_id: Optional[str]
	analysis_time_ms: int
	execution_time_ms: int
	rows_returned: int
	approved_by: Optional[str]
	approval_notes: Optional[str]
	created_at: Optional[str]
	executed_at: Optional[str]

class ApproveQueryRequest(BaseModel):
	query_id: str
	approved_by: str
	notes: str = ""

class ApprovalResponse(BaseModel):
	success: bool
	message: str

class StatisticsResponse(BaseModel):
	total_queries: int
	blocked: int
	pending_approval: int
	allowed: int
	average_risk_score: float

# ==================
# Endpoints
# ==================

@router.get("/recent", response_model=List[QueryLogResponse])
async def get_recent_queries(
	org_id: str,
	limit: int = 50,
	status: Optional[str] = None,
	user_id: Optional[str] = None,
	environment: Optional[str] = None,
	x_api_key: str = Depends(verify_api_key)
):
	"""
	Retrieve recent query logs for an organization.
	
	Query Parameters:
	- org_id: Organization ID (required)
	- limit: Max records to return (default 50)
	- status: Filter by status (blocked, allowed, pending_approval)
	- user_id: Filter by user
	- environment: Filter by environment (dev, staging, prod)
	
	Example:
	GET /api/queries/recent?org_id=acme&limit=10&status=pending_approval
	"""
	try:
		logs = QueryLogsRepository.get_recent_queries(
			org_id=org_id,
			limit=limit,
			status=status,
			user_id=user_id,
			environment=environment,
		)
		
		logger.info({
			"event": "recent_queries_retrieved",
			"org_id": org_id,
			"count": len(logs),
		})
		
		return logs
		
	except Exception as e:
		logger.error({
			"event": "recent_queries_failed",
			"org_id": org_id,
			"error": str(e),
		})
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Failed to retrieve queries"
		)

@router.get("/{query_id}", response_model=QueryLogResponse)
async def get_query(
	query_id: str,
	x_api_key: str = Depends(verify_api_key)
):
	"""
	Retrieve a specific query by ID.
	
	Example:
	GET /api/queries/QRY-abc12345
	"""
	log = QueryLogsRepository.get_query_by_id(query_id)
	
	if not log:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Query not found"
		)
	
	return log

@router.post("/approve", response_model=ApprovalResponse)
async def approve_query(
	request: ApproveQueryRequest,
	x_api_key: str = Depends(verify_api_key)
):
	"""
	Approve a pending query for execution.
	
	Request body:
	{
		"query_id": "QRY-abc12345",
		"approved_by": "user@example.com",
		"notes": "Looks good, proceed"
	}
	"""
	success = QueryLogsRepository.approve_query(
		query_id=request.query_id,
		approved_by=request.approved_by,
		notes=request.notes
	)
	
	if not success:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Query not found or already approved"
		)
	
	logger.info({
		"event": "query_approved_via_api",
		"query_id": request.query_id,
		"approved_by": request.approved_by,
	})
	
	return ApprovalResponse(
		success=True,
		message=f"Query {request.query_id} approved"
	)

@router.get("/stats/{org_id}", response_model=StatisticsResponse)
async def get_statistics(
	org_id: str,
	x_api_key: str = Depends(verify_api_key)
):
	"""
	Get query execution statistics for an organization.
	
	Returns:
	- total_queries: Total number of queries
	- blocked: Queries that were blocked
	- pending_approval: Queries awaiting approval
	- allowed: Queries that were allowed
	- average_risk_score: Average risk score
	
	Example:
	GET /api/queries/stats/acme
	"""
	stats = QueryLogsRepository.get_statistics(org_id)
	
	if not stats:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Failed to retrieve statistics"
		)
	
	return StatisticsResponse(
		total_queries=stats.get("total_queries", 0),
		blocked=stats.get("blocked", 0),
		pending_approval=stats.get("pending_approval", 0),
		allowed=stats.get("allowed", 0),
		average_risk_score=stats.get("average_risk_score", 0),
	)
