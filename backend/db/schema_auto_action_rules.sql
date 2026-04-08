-- SQL schema for auto_action_rules table
CREATE TABLE IF NOT EXISTS auto_action_rules (
    id TEXT PRIMARY KEY,
    action_type TEXT,
    metric TEXT,
    dimension TEXT,
    context TEXT,
    min_confidence FLOAT,
    min_success_rate FLOAT,
    min_avg_impact FLOAT,
    enabled BOOLEAN,
    mode TEXT,
    created_at TIMESTAMP
);
