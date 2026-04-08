-- Migration: Create query_logs table for persistence layer
-- Date: 2026-04-03
-- Purpose: Store persistent audit logs of all query executions for compliance, analytics, and governance

CREATE TABLE IF NOT EXISTS query_logs (
	query_id VARCHAR(50) PRIMARY KEY NOT NULL,
	
	-- Identity & context
	org_id VARCHAR(100) NOT NULL,
	user_id VARCHAR(100),
	
	-- Query content
	sql TEXT NOT NULL,
	fingerprint VARCHAR(50) NOT NULL,
	
	-- Risk assessment
	risk_score INTEGER NOT NULL,
	status VARCHAR(20) NOT NULL,  -- blocked, allowed, pending_approval
	confidence FLOAT NOT NULL,
	reasons TEXT,  -- JSON serialized
	
	-- Execution tracking
	environment VARCHAR(20) NOT NULL,  -- dev, staging, prod
	source VARCHAR(50),  -- playground, api, scheduler, etc
	session_id VARCHAR(100),
	
	-- Performance metrics
	analysis_time_ms INTEGER NOT NULL,
	execution_time_ms INTEGER NOT NULL DEFAULT 0,
	rows_returned INTEGER NOT NULL DEFAULT 0,
	
	-- Approval workflow
	approved_by VARCHAR(100),
	approval_notes TEXT,
	
	-- Audit trail
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	executed_at TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_query_logs_org_id ON query_logs(org_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_user_id ON query_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_fingerprint ON query_logs(fingerprint);
CREATE INDEX IF NOT EXISTS idx_query_logs_status ON query_logs(status);
CREATE INDEX IF NOT EXISTS idx_query_logs_environment ON query_logs(environment);
CREATE INDEX IF NOT EXISTS idx_query_logs_session_id ON query_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_created_at ON query_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_query_logs_org_created ON query_logs(org_id, created_at DESC);  -- For efficient "recent queries by org"
