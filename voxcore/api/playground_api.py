from fastapi import APIRouter, Depends, Header, status, HTTPException
from pydantic import BaseModel
import uuid
import hashlib
import time
from datetime import datetime, timedelta
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.middleware import verify_api_key, log_query_execution, logger
from backend.db.queries_repository import QueryLogsRepository
from backend.db.org_repository import PolicyRepository
from backend.services.org_policy_engine import OrganizationPolicyEngine
from backend.services.context_builder import QueryContextBuilder
from voxcore.engine.conversation_manager import ConversationManager

router = APIRouter()

# ============================================================================
# STEP 2: INITIALIZE CONVERSATION MANAGER FOR DEMO SCENARIOS
# ============================================================================
conversation_manager = ConversationManager(demo_mode=True)

# ============================================================================
# STEP 1: STABLE PUBLIC CONTRACT + SESSION LIFECYCLE
# ============================================================================

# Configuration constants
MAX_ROWS = 10000
QUERY_TIMEOUT = 30  # seconds
SESSION_TIMEOUT = 3600  # 1 hour in seconds

# In-memory session store (replace with Redis for production)
ACTIVE_SESSIONS = {}

class PlaygroundRequest(BaseModel):
	text: str
	session_id: str = None
	environment: str = "dev"
	source: str = "playground"
	user: str = "ai-agent"
	org_id: str = None  # Multi-tenant support
	user_id: str = None  # User attribution

# ============================================================================
# STEP 1: NEW STABLE PUBLIC CONTRACT FOR PLAYGROUND
# ============================================================================

class ExecutionMetadata(BaseModel):
	"""Execution metadata for demo environment"""
	mode: str = "demo"
	sandbox: bool = True
	max_rows: int = MAX_ROWS
	timeout_seconds: int = QUERY_TIMEOUT
	execution_time_ms: int = 0

class GovernanceBlock(BaseModel):
	"""Unified governance response across all scenarios"""
	classification: str  # "SAFE" | "MEDIUM" | "HIGH"
	risk_score: int  # 0-100
	confidence: float  # 0.0-1.0
	reasons: list[str] = []
	policy_violations: list[str] = []
	policy_applied: str = "None"
	requires_approval: bool = False

class PlaygroundQueryResponse(BaseModel):
	"""Stable public contract for Playground endpoint - locked for frontend"""
	session_id: str
	query_id: str
	fingerprint: str
	
	# Core result
	hero_insight: str  # One-liner hero result
	why_this_answer: str  # Narrative explanation
	result: dict  # Actual data/response payload
	
	# Enrichment
	governance: GovernanceBlock  # Always present, even on error
	emd_preview: str  # Executive summary preview
	suggestions: list[str] = []  # Next-step suggestions
	
	# Metadata
	execution: ExecutionMetadata
	original_query: str = ""
	generated_sql: str = ""
	
	# Audit trail
	created_at: str  # ISO8601 timestamp
	response_time_ms: int = 0

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

# ============================================================================
# STEP 1: SESSION MANAGEMENT WITH PROPER TIMESTAMPS
# ============================================================================

class PlaygroundSession:
	"""Session lifecycle management with real timestamps and expiration"""
	
	def __init__(self, session_id: str, org_id: str, user_id: str):
		self.session_id = session_id
		self.org_id = org_id
		self.user_id = user_id
		self.created_at = time.time()  # Real Unix timestamp
		self.last_active_at = self.created_at
		self.message_count = 0
		self.expired = False
	
	def is_expired(self) -> bool:
		"""Check if session has exceeded SESSION_TIMEOUT"""
		elapsed = time.time() - self.created_at
		return elapsed > SESSION_TIMEOUT
	
	def mark_active(self):
		"""Update last_active_at to current time"""
		self.last_active_at = time.time()
	
	def increment_message_count(self):
		"""Increment message counter for this session"""
		self.message_count += 1
	
	def to_dict(self) -> dict:
		"""Serialize session for logging/debugging"""
		return {
			"session_id": self.session_id,
			"org_id": self.org_id,
			"user_id": self.user_id,
			"created_at": datetime.fromtimestamp(self.created_at).isoformat(),
			"last_active_at": datetime.fromtimestamp(self.last_active_at).isoformat(),
			"message_count": self.message_count,
			"expired": self.expired,
			"age_seconds": time.time() - self.created_at,
		}

def cleanup_expired_sessions():
	"""Remove expired sessions from memory before processing new request"""
	expired_count = 0
	for session_id, session in list(ACTIVE_SESSIONS.items()):
		if session.is_expired():
			del ACTIVE_SESSIONS[session_id]
			expired_count += 1
			logger.info({
				"event": "session_expired",
				"session_id": session_id,
				"age_seconds": time.time() - session.created_at,
			})
	
	if expired_count > 0:
		logger.info({
			"event": "cleanup_complete",
			"expired_sessions": expired_count,
			"active_sessions": len(ACTIVE_SESSIONS),
		})

def get_or_create_session(session_id: str = None, org_id: str = "default-org", user_id: str = "unknown") -> PlaygroundSession:
	"""Get existing session or create new one with proper lifecycle"""
	cleanup_expired_sessions()  # Clean up first
	
	if session_id and session_id in ACTIVE_SESSIONS:
		session = ACTIVE_SESSIONS[session_id]
		
		# Check if it's expired
		if session.is_expired():
			logger.warning({
				"event": "session_expired_on_access",
				"session_id": session_id,
				"age_seconds": time.time() - session.created_at,
			})
			# Create new session
			session = PlaygroundSession(
				session_id=session_id,
				org_id=org_id,
				user_id=user_id
			)
			ACTIVE_SESSIONS[session_id] = session
		else:
			session.mark_active()
			session.increment_message_count()
	else:
		# Create new session
		new_session_id = session_id or str(uuid.uuid4())
		session = PlaygroundSession(
			session_id=new_session_id,
			org_id=org_id,
			user_id=user_id
		)
		ACTIVE_SESSIONS[new_session_id] = session
		logger.info({
			"event": "session_created",
			"session_id": new_session_id,
			"org_id": org_id,
			"user_id": user_id,
		})
	
	return session

def hash_sql(sql: str) -> str:
	"""Generate stable fingerprint for query deduplication"""
	normalized = " ".join(sql.split()).lower()
	return "0x" + hashlib.sha256(normalized.encode()).hexdigest()[:12]

# ============================================================================
# STEP 1: BUILD STABLE RESPONSE WITH GOVERNANCE GUARDRAIL
# ============================================================================

def build_governance_block(status: str, risk_score: int, confidence: float, 
                          reasons: list[str], policy_violations: list[str], 
                          policy_applied: str) -> GovernanceBlock:
	"""Ensure all responses include comprehensive governance block"""
	
	# Classify based on status and risk
	classification_map = {
		"blocked": "HIGH",
		"pending_approval": "MEDIUM",
		"allowed": "SAFE",
	}
	classification = classification_map.get(status, "MEDIUM")
	
	return GovernanceBlock(
		classification=classification,
		risk_score=risk_score,
		confidence=confidence,
		reasons=reasons,
		policy_violations=policy_violations,
		policy_applied=policy_applied or "None",
		requires_approval=(status == "pending_approval"),
	)

def build_playground_response(
	session: PlaygroundSession,
	query_id: str,
	fingerprint: str,
	status: str,
	risk_score: int,
	confidence: float,
	reasons: list[str],
	policy_violations: list[str],
	policy_applied: str,
	original_sql: str,
	generated_sql: str,
	hero_insight: str = "",
	why_this_answer: str = "",
	result: dict = None,
	emd_preview: str = "",
	suggestions: list[str] = None,
	execution_time_ms: int = 0,
) -> PlaygroundQueryResponse:
	"""Build complete stable response with governance guardrails"""
	
	governance = build_governance_block(
		status, risk_score, confidence, reasons, 
		policy_violations, policy_applied
	)
	
	# Ensure user-facing default messages if not provided
	if not hero_insight:
		if status == "blocked":
			hero_insight = "Query blocked due to governance policy"
		elif status == "pending_approval":
			hero_insight = "Query pending admin review"
		else:
			hero_insight = "Query cleared for execution"
	
	if not why_this_answer:
		why_this_answer = " ".join(reasons) if reasons else "Query passed governance checks"
	
	if not emd_preview:
		emd_preview = f"{hero_insight} — {why_this_answer}"
	
	if not suggestions:
		suggestions = []
		if status == "pending_approval":
			suggestions.append("Contact your admin for approval")
		elif status == "blocked":
			suggestions.append("Contact your admin to review the policy")
	
	execution_meta = ExecutionMetadata(execution_time_ms=execution_time_ms)
	
	return PlaygroundQueryResponse(
		session_id=session.session_id,
		query_id=query_id,
		fingerprint=fingerprint,
		hero_insight=hero_insight,
		why_this_answer=why_this_answer,
		result=result or {},
		governance=governance,
		emd_preview=emd_preview,
		suggestions=suggestions,
		execution=execution_meta,
		original_query=original_sql,
		generated_sql=generated_sql,
		created_at=datetime.utcnow().isoformat() + "Z",
		response_time_ms=execution_time_ms,
	)

@router.post("/api/playground/query", response_model=PlaygroundQueryResponse)
async def playground_query(
	request: PlaygroundRequest,
	x_api_key: str = Depends(verify_api_key)
):
	"""
	Stable Playground query endpoint with guaranteed response contract.
	
	Steps:
	1. Session lifecycle (create/validate/extend with real timestamps)
	2. Build query context
	3. Run risk analysis
	4. Evaluate policies
	5. Combine risk + policy decisions
	6. Execute (if allowed)
	7. Persist audit log
	8. Return stable contract response with governance guardrail
	"""
	start_time = time.time()
	
	org_id = request.org_id or "default-org"
	user_id = request.user_id or request.user or "unknown"
	
	try:
		# ========================================================================
		# STEP 1: SESSION LIFECYCLE WITH REAL TIMESTAMPS
		# ========================================================================
		session = get_or_create_session(
			session_id=request.session_id,
			org_id=org_id,
			user_id=user_id
		)
		
		logger.info({
			"event": "playground_query_received",
			"session_id": session.session_id,
			"org_id": org_id,
			"message_count": session.message_count,
			"session_age_seconds": time.time() - session.created_at,
		})
		
		# ========================================================================
		# STEP 1.5: ROUTE THROUGH CONVERSATION MANAGER (STEP 2)
		# ========================================================================
		scenario_result = conversation_manager.process_message(
			session_id=session.session_id,
			message=request.text,
		)
		
		internal_result = scenario_result.get("_internal_result", {})
		hero_insight = internal_result.get("hero_insight", "Analysis complete")
		why_this_answer = internal_result.get("why_this_answer", "")
		demo_response = internal_result.get("result", {})
		emd_preview = internal_result.get("emd_preview", "")
		demo_suggestions = internal_result.get("suggestions", [])
		
		logger.info({
			"event": "scenario_routed",
			"session_id": session.session_id,
			"intent": internal_result.get("intent", "unknown"),
		})
		
		# ========================================================================
		# STEP 2: BUILD QUERY CONTEXT
		# ========================================================================
		query_context = {}
		context_formatted = ""
		
		try:
			query_context = QueryContextBuilder.build_context(
				org_id=org_id,
				user_id=user_id,
				user_natural_language_query=request.text,
				session_history=None,
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
			# Continue anyway - context is optional
		
		# ========================================================================
		# STEP 3: RISK SCORING
		# ========================================================================
		from voxcore.engine.pipeline import execute_pipeline
		from backend.services.risk_scorer import score_query

		response = execute_pipeline(
			question=request.text,
			session_id=session.session_id,
			db_connection=None  # demo mode
		)
		
		original_sql = response.get("query", "")
		generated_sql = response.get("final_query", original_sql)
		
		risk_result = score_query(original_sql)
		risk_score = risk_result.get("risk_score", 10)
		reasons = list(risk_result.get("reasons", []))
		
		# ========================================================================
		# STEP 4: POLICY EVALUATION
		# ========================================================================
		policy_violations = []
		policy_applied = None
		policy_action = None
		
		try:
			policies = PolicyRepository.get_org_policies(org_id, enabled_only=True)
			
			if policies:
				violated_ids, action = OrganizationPolicyEngine.evaluate_query(org_id, original_sql)
				policy_violations = violated_ids
				policy_action = action
				
				if violated_ids:
					for policy_id in violated_ids:
						policy = PolicyRepository.get_policy(org_id, policy_id)
						if policy:
							policy_applied = policy.get("name", "Unknown Policy")
							break
			
			logger.info({
				"event": "policies_evaluated",
				"org_id": org_id,
				"policy_violations": policy_violations,
				"policy_action": policy_action
			})
		except Exception as e:
			logger.error({"event": "policy_evaluation_error", "error": str(e)})
			policy_action = None
		
		# ========================================================================
		# STEP 5: COMBINE RISK + POLICY (FINAL DECISION)
		# ========================================================================
		def determine_final_status(risk_score, policy_action):
			"""Policies override risk scoring"""
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
		
		if policy_violations:
			reasons.append(f"Policy violation: {policy_applied}" if policy_applied else "Policy violation detected")
		
		confidence = max(0.1, 1.0 - (risk_score / 100))
		
		# ========================================================================
		# STEP 6: GENERATE METADATA
		# ========================================================================
		analysis_time_ms = int((time.time() - start_time) * 1000)
		query_id = f"QRY-{session.session_id[:8]}-{uuid.uuid4().hex[:4]}"
		fingerprint = hash_sql(original_sql)
		
		# ========================================================================
		# STEP 7: LOG TO DATABASE
		# ========================================================================
		try:
			QueryLogsRepository.store_query_log(
				query_id=query_id,
				org_id=org_id,
				user_id=user_id,
				sql=original_sql[:100],
				fingerprint=fingerprint,
				risk_score=risk_score,
				status=status,
				confidence=confidence,
				reasons=reasons,
				environment=request.environment,
				source=request.source,
				session_id=session.session_id,
				analysis_time_ms=analysis_time_ms,
				execution_time_ms=0,
				rows_returned=0,
				policy_violations=policy_violations,
			)
			logger.info({"event": "query_logged", "query_id": query_id, "org_id": org_id})
		except Exception as e:
			logger.error({"event": "query_log_error", "error": str(e)})
		
		# ========================================================================
		# STEP 8: BUILD STABLE RESPONSE WITH GOVERNANCE GUARDRAIL
		# ========================================================================
		result_data = {
			"query_id": query_id,
			"status": status,
			"demo_data": demo_response.get("data", []),
			"narrative": demo_response.get("narrative", ""),
			"chart_type": demo_response.get("chart_type", ""),
			"chart_config": demo_response.get("chart_config", {}),
		}
		
		# Merge governance from scenario with governance from policy
		scenario_governance = internal_result.get("governance", {})
		combined_governance_reasons = reasons.copy()
		if scenario_governance.get("sensitivity"):
			combined_governance_reasons.append(f"Sensitivity: {scenario_governance['sensitivity'].title()}")
		
		# Build suggestions combining scenario suggestions with policy suggestions
		combined_suggestions = []
		if demo_suggestions:
			combined_suggestions.extend([s.label for s in demo_suggestions if isinstance(s, object) and hasattr(s, 'label')])
		
		if status != "allowed":
			combined_suggestions.append("Contact your admin" if status == "blocked" else "Pending approval")
		
		return build_playground_response(
			session=session,
			query_id=query_id,
			fingerprint=fingerprint,
			status=status,
			risk_score=risk_score,
			confidence=confidence,
			reasons=combined_governance_reasons,
			policy_violations=policy_violations,
			policy_applied=policy_applied,
			original_sql=original_sql,
			generated_sql=generated_sql,
			hero_insight=hero_insight,
			why_this_answer=why_this_answer,
			result=result_data,
			emd_preview=emd_preview if emd_preview else f"{status.upper()} — {hero_insight}",
			suggestions=combined_suggestions if combined_suggestions else ["Query analyzed successfully"],
			execution_time_ms=analysis_time_ms,
		)
	
	except Exception as e:
		# ========================================================================
		# ERROR HANDLING WITH USER-FACING WORDING
		# ========================================================================
		logger.error({
			"event": "playground_query_error",
			"error": str(e),
			"type": type(e).__name__,
		})
		
		# Create fallback session for error response
		session = get_or_create_session(
			session_id=request.session_id,
			org_id=org_id,
			user_id=user_id
		)
		
		# User-facing error message, not raw traceback
		error_message = "The governance pipeline encountered an issue processing your query. Please try again."
		if "timeout" in str(e).lower():
			error_message = "Query analysis took too long. Please simplify your query and retry."
		elif "database" in str(e).lower():
			error_message = "Unable to reach the query governance system. Please try again later."
		
		# Still return stable contract with governance block for error case
		return build_playground_response(
			session=session,
			query_id=f"ERR-{uuid.uuid4().hex[:12]}",
			fingerprint="error",
			status="blocked",
			risk_score=100,
			confidence=0.0,
			reasons=[error_message],
			policy_violations=[],
			policy_applied="SystemError",
			original_sql=request.text,
			generated_sql="",
			hero_insight="Error processing query",
			why_this_answer=error_message,
			result={"error": error_message},
			emd_preview=f"Unable to analyze query: {error_message}",
			suggestions=["Simplify your query", "Contact support if issue persists"],
			execution_time_ms=int((time.time() - start_time) * 1000),
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
