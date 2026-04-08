-- Multi-tenant schema with organizations, users, and policies
-- Created: 2026-04-03

-- Organizations (tenants)
CREATE TABLE IF NOT EXISTS organizations (
  id VARCHAR(100) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users (org members with roles)
CREATE TABLE IF NOT EXISTS users (
  id VARCHAR(100) PRIMARY KEY,
  org_id VARCHAR(100) NOT NULL REFERENCES organizations(id),
  email VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL,  -- admin, analyst, viewer
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(org_id, email)
);

-- Policies (org-level query rules)
CREATE TABLE IF NOT EXISTS policies (
  id VARCHAR(100) PRIMARY KEY,
  org_id VARCHAR(100) NOT NULL REFERENCES organizations(id),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  rule_type VARCHAR(100) NOT NULL,  -- no_full_scan, max_joins, max_rows, destructive_check
  condition JSONB NOT NULL,  -- { "type": "...", "threshold": ... }
  action VARCHAR(50) NOT NULL,  -- block, allow, require_approval
  enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Updated queries table with org_id and policy tracking
ALTER TABLE IF EXISTS query_logs ADD COLUMN org_id VARCHAR(100);
ALTER TABLE IF EXISTS query_logs ADD COLUMN user_id VARCHAR(100);
ALTER TABLE IF EXISTS query_logs ADD COLUMN policy_violations JSONB;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_org_id ON users(org_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_policies_org_id ON policies(org_id);
CREATE INDEX IF NOT EXISTS idx_policies_enabled ON policies(enabled);
CREATE INDEX IF NOT EXISTS idx_query_logs_org_id ON query_logs(org_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_user_id ON query_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_org_created ON query_logs(org_id, created_at DESC);
