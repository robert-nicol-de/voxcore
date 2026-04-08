"""
Repository for query logs persistence.

Handles all database operations for storing and retrieving query execution records.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
import os
import sys

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.db.models import QueryLog
from backend.db.connection_manager import SessionLocal
from backend.middleware import logger

class QueryLogsRepository:
	"""Repository for query log persistence operations"""
	
	@staticmethod
	def store_query_log(
		query_id: str,
		org_id: str,
		sql: str,
		fingerprint: str,
		risk_score: int,
		status: str,
		confidence: float,
		reasons: List[str],
		environment: str,
		source: str,
		session_id: str,
		user_id: str = None,
		analysis_time_ms: int = 0,
		execution_time_ms: int = 0,
		rows_returned: int = 0,
	) -> bool:
		"""
		Store a query execution record in the database.
		
		Args:
			query_id: Unique identifier for this query
			org_id: Organization/tenant ID
			sql: The SQL that was executed
			fingerprint: Hash fingerprint for deduplication
			risk_score: Risk score (0-100)
			status: blocked | allowed | pending_approval
			confidence: Confidence score (0-1)
			reasons: List of risk assessment reasons
			environment: dev | staging | production
			source: playground | api | scheduler | etc
			session_id: Session identifier
			user_id: User who executed the query (optional)
			analysis_time_ms: Time spent analyzing (ms)
			execution_time_ms: Time spent executing (ms)
			rows_returned: Number of rows in result
		
		Returns:
			True if successful, False on error
		"""
		try:
			db = SessionLocal()
			
			# Serialize reasons list to JSON
			reasons_json = json.dumps(reasons) if reasons else None
			
			# Create log record
			log_record = QueryLog(
				query_id=query_id,
				org_id=org_id,
				user_id=user_id,
				sql=sql,
				fingerprint=fingerprint,
				risk_score=risk_score,
				status=status,
				confidence=confidence,
				reasons=reasons_json,
				environment=environment,
				source=source,
				session_id=session_id,
				analysis_time_ms=analysis_time_ms,
				execution_time_ms=execution_time_ms,
				rows_returned=rows_returned,
				created_at=datetime.utcnow(),
				executed_at=datetime.utcnow(),
			)
			
			# Store in database
			db.add(log_record)
			db.commit()
			db.close()
			
			logger.info({
				"event": "query_log_stored",
				"query_id": query_id,
				"org_id": org_id,
				"risk_score": risk_score,
				"status": status,
				"environment": environment,
			})
			
			return True
			
		except Exception as e:
			logger.error({
				"event": "query_log_store_failed",
				"query_id": query_id,
				"error": str(e),
			})
			return False
	
	@staticmethod
	def get_recent_queries(
		org_id: str,
		limit: int = 50,
		status: Optional[str] = None,
		user_id: Optional[str] = None,
		environment: Optional[str] = None,
	) -> List[Dict[str, Any]]:
		"""
		Retrieve recent query logs for an organization.
		
		Args:
			org_id: Organization/tenant ID
			limit: Max number of records (default 50)
			status: Optional - filter by status (blocked, allowed, pending_approval)
			user_id: Optional - filter by user
			environment: Optional - filter by environment (dev, staging, prod)
		
		Returns:
			List of query log dictionaries, sorted by created_at DESC
		"""
		try:
			db = SessionLocal()
			
			# Build query
			query = db.query(QueryLog).filter(QueryLog.org_id == org_id)
			
			# Apply optional filters
			if status:
				query = query.filter(QueryLog.status == status)
			if user_id:
				query = query.filter(QueryLog.user_id == user_id)
			if environment:
				query = query.filter(QueryLog.environment == environment)
			
			# Order by creation time descending and limit
			logs = query.order_by(QueryLog.created_at.desc()).limit(limit).all()
			
			db.close()
			
			# Convert to dictionaries
			return [log.to_dict() for log in logs]
			
		except Exception as e:
			logger.error({
				"event": "query_log_retrieve_failed",
				"org_id": org_id,
				"error": str(e),
			})
			return []
	
	@staticmethod
	def get_query_by_id(query_id: str) -> Optional[Dict[str, Any]]:
		"""Get a specific query log by ID"""
		try:
			db = SessionLocal()
			log = db.query(QueryLog).filter(QueryLog.query_id == query_id).first()
			db.close()
			
			return log.to_dict() if log else None
			
		except Exception as e:
			logger.error({
				"event": "query_log_get_failed",
				"query_id": query_id,
				"error": str(e),
			})
			return None
	
	@staticmethod
	def approve_query(
		query_id: str,
		approved_by: str,
		notes: str = ""
	) -> bool:
		"""Approve a pending query for execution"""
		try:
			db = SessionLocal()
			
			log = db.query(QueryLog).filter(QueryLog.query_id == query_id).first()
			if not log:
				return False
			
			log.status = "allowed"
			log.approved_by = approved_by
			log.approval_notes = notes
			
			db.commit()
			db.close()
			
			logger.info({
				"event": "query_approved",
				"query_id": query_id,
				"approved_by": approved_by,
			})
			
			return True
			
		except Exception as e:
			logger.error({
				"event": "query_approve_failed",
				"query_id": query_id,
				"error": str(e),
			})
			return False
	
	@staticmethod
	def get_statistics(org_id: str) -> Dict[str, Any]:
		"""Get query statistics for an organization"""
		try:
			db = SessionLocal()
			
			total = db.query(QueryLog).filter(QueryLog.org_id == org_id).count()
			blocked = db.query(QueryLog).filter(
				QueryLog.org_id == org_id,
				QueryLog.status == "blocked"
			).count()
			pending = db.query(QueryLog).filter(
				QueryLog.org_id == org_id,
				QueryLog.status == "pending_approval"
			).count()
			allowed = total - blocked - pending
			
			avg_risk = db.query(QueryLog).filter(
				QueryLog.org_id == org_id
			).with_entities(
				db.func.avg(QueryLog.risk_score).label('avg')
			).first()
			
			db.close()
			
			return {
				"total_queries": total,
				"blocked": blocked,
				"pending_approval": pending,
				"allowed": allowed,
				"average_risk_score": round(float(avg_risk[0] or 0), 2),
			}
			
		except Exception as e:
			logger.error({
				"event": "statistics_failed",
				"org_id": org_id,
				"error": str(e),
			})
			return {}
