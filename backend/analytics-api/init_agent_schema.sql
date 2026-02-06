-- SQLite schema for genai_requests table (minimal version for agent)

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT,
    is_active INTEGER DEFAULT 1,
    is_superuser INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS genai_requests (
    id TEXT PRIMARY KEY,
    app_id TEXT,
    model_id TEXT,
    user_id TEXT,
    agent_id TEXT,
    
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_hash TEXT NOT NULL,
    
    computer_name TEXT,
    process_name TEXT,
    
    model_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    
    tokens_input INTEGER NOT NULL,
    tokens_output INTEGER NOT NULL,
    tokens_total INTEGER NOT NULL,
    
    energy_wh REAL,
    co2_g REAL,
    
    region TEXT,
    carbon_intensity REAL,
    
    latency_ms INTEGER,
    
    use_case TEXT,
    risk_level TEXT,
    
    policy_applied INTEGER DEFAULT 0,
    policy_action TEXT,
    
    cost_usd REAL,
    meta_data TEXT,
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_genai_requests_timestamp ON genai_requests(timestamp);
CREATE INDEX IF NOT EXISTS idx_genai_requests_model_name ON genai_requests(model_name);
CREATE INDEX IF NOT EXISTS idx_genai_requests_provider ON genai_requests(provider);
CREATE INDEX IF NOT EXISTS idx_genai_requests_user_id ON genai_requests(user_id);
