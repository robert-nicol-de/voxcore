from fastapi import APIRouter, Depends, Header, status, HTTPException
from pydantic import BaseModel
import uuid
import hashlib
import time
from datetime import datetime
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.middleware import verify_api_key, log_query_execution, logger
from backend.db.queries_repository import QueryLogsRepository
from backend.db.org_repository import PolicyRepository
from backend.services.org_policy_engine import OrganizationPolicyEngine
from backend.services.context_builder import QueryContextBuilder

router = APIRouter()

class PlaygroundRequest(BaseModel):
	text: str
	session_id: str = None
	environment: str = "dev"
	source: str = "playground"
	user: str = "ai-agent"
	org_id: str = None  # Multi-tenant support
	user_id: str = None  # User attribution

class QueryResponse(BaseModel):
	"""Locked backend contract - stable API surface"""
	query_id: str
	fingerprint: str
	status: str  # "blocked" | "allowed" | "pending_approval"
	risk_score: int
	confidence: float
	reasons: list[str]
	analysis_time_ms: int
	original_sql: str
	rewritten_sql: str
	execution: dict  # {"rows_returned": int, "execution_time_ms": int}
	policy_applied: str  # Name of policy that was applied (if any)
	policy_violations: list[str]  # Policy IDs that were violated
	context: dict  # {"user": str, "environment": str, "source": str, "org_id": str}
	query_context: dict  # Rich structured context for LLM (NEW)
	context_formatted: str  # Human-readable context for UI display (NEW)

class ApprovalRequest(BaseModel):
	approve: bool
	reason: str = None

def hash_sql(sql: str) -> str:
	"""Generate stable fingerprint for query deduplication"""
	normalized = " ".join(sql.split()).lower()
	return "0x" + hashlib.sha256(normalized.encode()).hexdigest()[:12]

@router.post("/api/playground/query", response_model=QueryResponse)
async def playground_query(
	request: PlaygroundRequest,
	x_api_key: str = Depends(verify_api_key)
):
	"""
	Complete query execution flow:
	1. Load org + policies
	2. Build query context (structured info for LLM)
	3. Run risk analysis
	4. Evaluate policies
	5. Combine risk + policy decisions
	6. Execute (if allowed)
	7. Persist audit log + context
	"""
	start_time = time.time()
	session_id = request.session_id or str(uuid.uuid4())
	org_id = request.org_id or "default-org"
	user_id = request.user_id or request.user or "unknown"
	
	# ** STEP 0: BUILD QUERY CONTEXT **
	# This is the critical new piece - structured context for SQL generation
	try:
		query_context = QueryContextBuilder.build_context(
			org_id=org_id,
			user_id=user_id,
			user_natural_language_query=request.text,
			session_history=None,  # Could load from DB later
			environment=request.environment,
		)
		context_formatted = QueryContextBuilder.format_for_llm_prompt(query_context)
		
		logger.info({
			"event": "context_built",
			"user_role": query_context.get("user_role"),
			"available_tables": len(query_context.get("schema", {}).get("available_tables", [])),
		})
	except Exception as e:
		logger.error({"event": "context_build_error", "error": str(e)})
		query_context = {}
		context_formatted = ""
	
	logger.info({
		"event": "playground_query_received",
		"session_id": session_id,
		"org_id": org_id,
		"user": user_id,
		"environment": request.environment,
		"source": request.source,
	})
	
	# Step 1: Risk scoring
	from voxcore.engine.pipeline import execute_pipeline
	from backend.services.risk_scorer import score_query

	response = execute_pipeline(
		question=request.text,
		session_id=session_id,
		db_connection=None  # demo mode for now
	)
	
	original_sql = response.get("query", "")
	rewritten_sql = response.get("final_query", original_sql)
	
	risk_result = score_query(original_sql)
	risk_score = risk_result.get("risk_score", 10)
	reasons = list(risk_result.get("reasons", []))
	
	# Step 2: Load policies and evaluate
	policy_violations = []
	policy_applied = None
	policy_action = None
	
	try:
		# Get all enabled policies for this org
		policies = PolicyRepository.get_org_policies(org_id, enabled_only=True)
		
		if policies:
			# Evaluate query against each policy
			violated_ids, action = OrganizationPolicyEngine.evaluate_query(org_id, original_sql)
			policy_violations = violated_ids
			policy_action = action
			
			# Find the policy names for logging
			if violated_ids:
				for policy_id in violated_ids:
					policy = PolicyRepository.get_policy(org_id, policy_id)
					if policy:
						policy_applied = policy.get("name", "Unknown Policy")
						break  # Just show first violated policy name
		
		logger.info({
			"event": "policies_evaluated",
			"org_id": org_id,
			"policy_violations": policy_violations,
			"policy_action": policy_action
		})
	except Exception as e:
		logger.error({"event": "policy_evaluation_error", "error": str(e)})
		policy_action = None  # Fall back to risk-based decision
	
	# Step 3: Combine risk + policy (CRITICAL LOGIC)
	def determine_final_status(risk_score, policy_action):
		"""Policies override risk scoring"""
		# Policies take precedence
		if policy_action == "block":
			return "blocked"
		
		if policy_action == "require_approval":
			return "pending_approval"
		
		# Fall back to risk-based decision
		if risk_score >= 80:
			return "blocked"
		elif risk_score >= 60:
			return "pending_approval"
		else:
			return "allowed"
	
	status = determine_final_status(risk_score, policy_action)
	
	# Add policy context to reasons
	if policy_violations:
		reasons.append(f"Policy violation: {policy_applied}" if policy_applied else "Policy violation detected")
	
	# Confidence score (inverse relationship with risk)
	confidence = max(0.1, 1.0 - (risk_score / 100))
	
	# Step 4: Generate metadata
	analysis_time_ms = int((time.time() - start_time) * 1000)
	query_id = f"QRY-{session_id[:8]}-{uuid.uuid4().hex[:4]}"
	fingerprint = hash_sql(original_sql)
	
	# Step 5: Log query execution
	log_query_execution(
		query_id=query_id,
		query=original_sql[:100],
		risk_score=risk_score,
		status=status,
		user=user_id,
		environment=request.environment,
		source=request.source,
		analysis_time_ms=analysis_time_ms,
		confidence=confidence,
	)
	
	# Step 6: Persist to database
	try:
		QueryLogsRepository.store_query_log(
			query_id=query_id,
			org_id=org_id,
			user_id=user_id,
			sql=original_sql,
			fingerprint=fingerprint,
			risk_score=risk_score,
			status=status,
			confidence=confidence,
			reasons=reasons,
			environment=request.environment,
			source=request.source,
			session_id=session_id,
			analysis_time_ms=analysis_time_ms,
			execution_time_ms=0,
			rows_returned=0,
			policy_violations=policy_violations,  # Store which policies were violated
		)
		logger.info({"event": "query_logged", "query_id": query_id, "org_id": org_id})
	except Exception as e:
		logger.error({"event": "query_log_error", "error": str(e)})
	
	# Step 7: Return response
	return QueryResponse(
		query_id=query_id,
		fingerprint=fingerprint,
		status=status,
		risk_score=risk_score,
		confidence=confidence,
		reasons=reasons,
		analysis_time_ms=analysis_time_ms,
		original_sql=original_sql,
		rewritten_sql=rewritten_sql,
		execution={
			"rows_returned": 0,
			"execution_time_ms": analysis_time_ms
		},
		policy_applied=policy_applied or "None",
		policy_violations=policy_violations,
		context={
			"user": user_id,
			"environment": request.environment,
			"source": request.source,
			"org_id": org_id
		},
		query_context=query_context,  # NEW: Structured context data
		context_formatted=context_formatted,  # NEW: Formatted for display
	)


@router.post("/api/playground/queries/{query_id}/approve")
async def approve_query(
	query_id: str,
	request: ApprovalRequest,
	x_api_key: str = Depends(verify_api_key)
):
	"""
	Human-in-the-loop approval workflow
	Allows admins to approve pending_approval queries
	"""
	try:
		# Fetch the pending query from database
		query_log = QueryLogsRepository.get_query_log(query_id)
		
		if not query_log:
			raise HTTPException(status_code=404, detail="Query not found")
		
		if query_log.get("status") != "pending_approval":
			raise HTTPException(
				status_code=400,
				detail=f"Query status is {query_log.get('status')}, not pending_approval"
			)
		
		# Update status based on approval
		new_status = "allowed" if request.approve else "blocked"
		
		# Store approval decision
		approval_note = request.reason or ("Admin approved" if request.approve else "Admin rejected")
		
		QueryLogsRepository.update_query_status(
			query_id=query_id,
			new_status=new_status,
			approval_notes=approval_note
		)
		
		logger.info({
			"event": "query_approved",
			"query_id": query_id,
			"approved": request.approve,
			"reason": approval_note
		})
		
		return {
			"query_id": query_id,
			"status": new_status,
			"approved": request.approve,
			"reason": approval_note
		}
	
	except HTTPException:
		raise
	except Exception as e:
		logger.error({"event": "approval_error", "query_id": query_id, "error": str(e)})
		raise HTTPException(status_code=500, detail=f"Approval failed: {str(e)}")
