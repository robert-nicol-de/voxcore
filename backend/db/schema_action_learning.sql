-- SQL schema for action_learning table
CREATE TABLE IF NOT EXISTS action_learning (
    id TEXT PRIMARY KEY,
    action_type TEXT,
    metric TEXT,
    dimension TEXT,
    context TEXT,
    executions INTEGER,
    successes INTEGER,
    failures INTEGER,
    success_rate FLOAT,
    avg_impact FLOAT,
    last_updated TIMESTAMP
);
