"""
Database models for VoxCore persistence layer
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Organization(Base):
	"""Organization/tenant in multi-tenant system"""
	__tablename__ = "organizations"
	
	id = Column(String(100), primary_key=True, nullable=False)
	name = Column(String(255), nullable=False)
	created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
	
	def to_dict(self):
		return {
			"id": self.id,
			"name": self.name,
			"created_at": self.created_at.isoformat() if self.created_at else None,
		}

class User(Base):
	"""User with org membership and role"""
	__tablename__ = "users"
	
	id = Column(String(100), primary_key=True, nullable=False)
	org_id = Column(String(100), ForeignKey("organizations.id"), nullable=False, index=True)
	email = Column(String(255), nullable=False, index=True)
	role = Column(String(50), nullable=False)  # admin, analyst, viewer
	created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
	
	def to_dict(self):
		return {
			"id": self.id,
			"org_id": self.org_id,
			"email": self.email,
			"role": self.role,
			"created_at": self.created_at.isoformat() if self.created_at else None,
		}

class Policy(Base):
	"""Query execution policy (org-level rules)"""
	__tablename__ = "policies"
	
	id = Column(String(100), primary_key=True, nullable=False)
	org_id = Column(String(100), ForeignKey("organizations.id"), nullable=False, index=True)
	name = Column(String(255), nullable=False)
	description = Column(Text, nullable=True)
	rule_type = Column(String(100), nullable=False)  # no_full_scan, max_joins, max_rows, destructive_check
	condition = Column(JSON, nullable=False)  # {"type": "...", "threshold": ...}
	action = Column(String(50), nullable=False)  # block, allow, require_approval
	enabled = Column(Boolean, default=True, index=True)
	created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
	updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
	
	def to_dict(self):
		return {
			"id": self.id,
			"org_id": self.org_id,
			"name": self.name,
			"description": self.description,
			"rule_type": self.rule_type,
			"condition": self.condition,
			"action": self.action,
			"enabled": self.enabled,
			"created_at": self.created_at.isoformat() if self.created_at else None,
			"updated_at": self.updated_at.isoformat() if self.updated_at else None,
		}

class QueryLog(Base):
	"""
	Persistent audit log of all query executions.
	
	Tracks:
	- What SQL was executed
	- Who executed it (user_id, org_id)
	- Risk assessment (score, status)
	- Confidence metrics
	- Policy violations
	- Execution timing
	- Compliance/audit trail
	"""
	__tablename__ = "query_logs"
	
	# Primary key
	query_id = Column(String(50), primary_key=True, nullable=False)
	
	# Identity & context
	org_id = Column(String(100), nullable=False, index=True)
	user_id = Column(String(100), nullable=True, index=True)
	
	# Query content
	sql = Column(Text, nullable=False)
	fingerprint = Column(String(50), nullable=False, index=True)
	
	# Risk assessment
	risk_score = Column(Integer, nullable=False)
	status = Column(String(20), nullable=False, index=True)  # blocked, allowed, pending_approval
	confidence = Column(Float, nullable=False)
	reasons = Column(Text, nullable=True)  # JSON serialized
	
	# Policy violations
	policy_violations = Column(JSON, nullable=True)  # List of violated policy IDs
	
	# Execution tracking
	environment = Column(String(20), nullable=False, index=True)  # dev, staging, prod
	source = Column(String(50), nullable=True)  # playground, api, scheduler, etc
	session_id = Column(String(100), nullable=True, index=True)
	
	# Performance metrics
	analysis_time_ms = Column(Integer, nullable=False)
	execution_time_ms = Column(Integer, nullable=False, default=0)
	rows_returned = Column(Integer, nullable=False, default=0)
	
	# Approval workflow
	approved_by = Column(String(100), nullable=True)
	approval_notes = Column(Text, nullable=True)
	
	# Audit trail
	created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
	executed_at = Column(DateTime, nullable=True)
	
	def to_dict(self):
		"""Convert to dictionary for JSON serialization"""
		return {
			"query_id": self.query_id,
			"org_id": self.org_id,
			"user_id": self.user_id,
			"sql": self.sql,
			"fingerprint": self.fingerprint,
			"risk_score": self.risk_score,
			"status": self.status,
			"confidence": self.confidence,
			"reasons": self.reasons,
			"policy_violations": self.policy_violations,
			"environment": self.environment,
			"source": self.source,
			"session_id": self.session_id,
			"analysis_time_ms": self.analysis_time_ms,
			"execution_time_ms": self.execution_time_ms,
			"rows_returned": self.rows_returned,
			"approved_by": self.approved_by,
			"approval_notes": self.approval_notes,
			"created_at": self.created_at.isoformat() if self.created_at else None,
			"executed_at": self.executed_at.isoformat() if self.executed_at else None,
		}
