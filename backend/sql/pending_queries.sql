CREATE TABLE IF NOT EXISTS pending_queries (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    risk_score INT NOT NULL,
    risk_level TEXT NOT NULL,
    reasons TEXT,
    ai_agent TEXT NOT NULL DEFAULT 'anonymous',
    database_name TEXT,
    status TEXT NOT NULL DEFAULT 'pending',   -- pending | approved | rejected
    company_id INT,
    user_id INT,
    created_at TIMESTAMP DEFAULT NOW(),
    reviewed_by TEXT,
    reviewed_at TIMESTAMP
);
