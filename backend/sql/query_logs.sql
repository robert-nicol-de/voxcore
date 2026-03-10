CREATE TABLE IF NOT EXISTS query_logs (
    id SERIAL PRIMARY KEY,
    company_id INT,
    user_id INT,
    query TEXT,
    execution_time FLOAT,
    risk_level TEXT,
    blocked BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);
