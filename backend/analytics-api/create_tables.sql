-- Create all tables for Eco-Compute Analytics API

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    organization VARCHAR(255),
    subscription_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Apps table
CREATE TABLE IF NOT EXISTS apps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    environment VARCHAR(50) DEFAULT 'production',
    api_key_hash VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    computer_id VARCHAR(255) UNIQUE NOT NULL,
    computer_name VARCHAR(255),
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    agent_version VARCHAR(50),
    os_version VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    last_heartbeat TIMESTAMP,
    installed_by UUID REFERENCES users(id),
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    api_key_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Models table
CREATE TABLE IF NOT EXISTS models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    provider VARCHAR(50) NOT NULL,
    context_window INTEGER,
    input_cost_per_1k FLOAT,
    output_cost_per_1k FLOAT,
    energy_per_token_wh FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GenAI Requests table
CREATE TABLE IF NOT EXISTS genai_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    app_id UUID REFERENCES apps(id) ON DELETE CASCADE,
    model_id UUID REFERENCES models(id),
    user_id UUID REFERENCES users(id),
    agent_id UUID REFERENCES agents(id),
    
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_hash VARCHAR(64) NOT NULL,
    
    computer_name VARCHAR(255),
    process_name VARCHAR(255),
    
    model_name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    
    tokens_input INTEGER NOT NULL,
    tokens_output INTEGER NOT NULL,
    tokens_total INTEGER NOT NULL,
    
    energy_wh FLOAT,
    co2_g FLOAT,
    
    region VARCHAR(50),
    carbon_intensity FLOAT,
    
    latency_ms INTEGER,
    
    use_case VARCHAR(100),
    risk_level VARCHAR(20),
    
    policy_applied BOOLEAN DEFAULT FALSE,
    policy_action VARCHAR(50),
    
    cost_usd FLOAT,
    meta_data JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_genai_requests_timestamp ON genai_requests(timestamp);
CREATE INDEX IF NOT EXISTS idx_genai_requests_agent_id ON genai_requests(agent_id);
CREATE INDEX IF NOT EXISTS idx_genai_requests_model_name ON genai_requests(model_name);
CREATE INDEX IF NOT EXISTS idx_genai_requests_region ON genai_requests(region);
CREATE INDEX IF NOT EXISTS idx_agents_team_id ON agents(team_id);
CREATE INDEX IF NOT EXISTS idx_apps_team_id ON apps(team_id);

COMMIT;
