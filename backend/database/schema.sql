-- Eco-Compute Database Schema
-- PostgreSQL 15+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TEAMS & MULTI-TENANCY
-- ============================================================================

CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    organization VARCHAR(255),
    subscription_tier VARCHAR(50) DEFAULT 'free', -- free, pro, enterprise
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_teams_organization ON teams(organization);

-- ============================================================================
-- APPLICATIONS
-- ============================================================================

CREATE TABLE apps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    environment VARCHAR(50) DEFAULT 'production', -- development, staging, production
    api_key_hash VARCHAR(255) UNIQUE NOT NULL, -- Hashed API key for SDK auth
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_apps_team_id ON apps(team_id);
CREATE INDEX idx_apps_api_key_hash ON apps(api_key_hash);

-- ============================================================================
-- AI MODELS CATALOG
-- ============================================================================

CREATE TABLE models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    provider VARCHAR(50) NOT NULL, -- openai, azure, google, anthropic
    parameters VARCHAR(50), -- 7B, 13B, 175B, etc.
    energy_per_1k_tokens DECIMAL(10, 6) NOT NULL, -- kWh per 1000 tokens
    co2_per_1k_tokens DECIMAL(10, 6), -- Baseline CO2 (optional)
    efficiency_score VARCHAR(5), -- A+, A, B, C, D
    tokens_per_sec INTEGER,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB, -- Additional model info
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_models_provider ON models(provider);
CREATE INDEX idx_models_name ON models(name);

-- Insert sample models
INSERT INTO models (name, provider, parameters, energy_per_1k_tokens, efficiency_score, tokens_per_sec) VALUES
('gpt-4', 'openai', '175B', 0.0008, 'C', 40),
('gpt-3.5-turbo', 'openai', '175B', 0.0003, 'B', 120),
('claude-3-opus', 'anthropic', '175B', 0.0007, 'C', 45),
('claude-3-sonnet', 'anthropic', '70B', 0.0005, 'B', 85),
('gemini-pro', 'google', '540B', 0.0009, 'D', 35),
('llama-3-70b', 'meta', '70B', 0.0006, 'B', 60);

-- ============================================================================
-- GENAI REQUESTS (Core logging table)
-- ============================================================================

CREATE TABLE genai_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    app_id UUID REFERENCES apps(id) ON DELETE CASCADE,
    model_id UUID REFERENCES models(id),
    
    -- Request metadata
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    request_hash VARCHAR(64) NOT NULL, -- SHA-256 hash of request (NOT the actual prompt)
    
    -- Model & Provider
    model_name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    
    -- Token usage
    tokens_input INTEGER NOT NULL,
    tokens_output INTEGER NOT NULL,
    tokens_total INTEGER NOT NULL,
    
    -- Environmental metrics
    energy_wh DECIMAL(10, 4), -- Watt-hours
    co2_g DECIMAL(10, 4), -- Grams of CO2
    
    -- Infrastructure
    region VARCHAR(50), -- us-east-1, eu-west-3, etc.
    carbon_intensity DECIMAL(10, 6), -- kg CO2/kWh for the region
    
    -- Performance
    latency_ms INTEGER,
    
    -- Application context
    use_case VARCHAR(100), -- customer-support, content-generation, etc.
    risk_level VARCHAR(20), -- low, medium, high
    
    -- Policy enforcement
    policy_applied BOOLEAN DEFAULT false,
    policy_action VARCHAR(50), -- allowed, blocked, downgraded
    
    -- Cost (optional)
    cost_usd DECIMAL(10, 6),
    
    -- Metadata
    metadata JSONB, -- Additional custom fields
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_genai_requests_app_id ON genai_requests(app_id);
CREATE INDEX idx_genai_requests_timestamp ON genai_requests(timestamp DESC);
CREATE INDEX idx_genai_requests_model_name ON genai_requests(model_name);
CREATE INDEX idx_genai_requests_provider ON genai_requests(provider);
CREATE INDEX idx_genai_requests_use_case ON genai_requests(use_case);
CREATE INDEX idx_genai_requests_region ON genai_requests(region);

-- Composite index for common queries
CREATE INDEX idx_genai_requests_app_timestamp ON genai_requests(app_id, timestamp DESC);

-- ============================================================================
-- CARBON METRICS (Aggregated data for fast dashboard queries)
-- ============================================================================

CREATE TABLE carbon_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    app_id UUID REFERENCES apps(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    
    -- Time period
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    granularity VARCHAR(20) NOT NULL, -- hourly, daily, weekly, monthly
    
    -- Aggregated metrics
    total_requests INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_energy_wh DECIMAL(12, 4) DEFAULT 0,
    total_co2_g DECIMAL(12, 4) DEFAULT 0,
    total_cost_usd DECIMAL(12, 4) DEFAULT 0,
    
    -- Averages
    avg_latency_ms INTEGER,
    avg_tokens_per_request INTEGER,
    avg_energy_per_request DECIMAL(10, 4),
    
    -- Breakdown by model
    model_breakdown JSONB, -- {"gpt-4": {"requests": 100, "tokens": 50000, ...}, ...}
    
    -- Breakdown by use case
    use_case_breakdown JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_carbon_metrics_app_id ON carbon_metrics(app_id);
CREATE INDEX idx_carbon_metrics_team_id ON carbon_metrics(team_id);
CREATE INDEX idx_carbon_metrics_period ON carbon_metrics(period_start, period_end);
CREATE INDEX idx_carbon_metrics_granularity ON carbon_metrics(granularity);

-- ============================================================================
-- POLICIES (Governance rules)
-- ============================================================================

CREATE TABLE policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    app_id UUID REFERENCES apps(id) ON DELETE SET NULL, -- NULL = applies to all apps
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Policy type
    policy_type VARCHAR(50) NOT NULL, -- model_restriction, token_limit, cost_limit, carbon_limit
    
    -- Conditions
    conditions JSONB NOT NULL, -- {"risk_level": "low", "use_case": "marketing"}
    
    -- Actions
    action VARCHAR(50) NOT NULL, -- block, warn, downgrade, allow
    action_config JSONB, -- {"downgrade_to": "gpt-3.5-turbo"}
    
    -- Thresholds
    threshold_value DECIMAL(12, 4),
    threshold_unit VARCHAR(50), -- tokens, wh, g_co2, usd
    
    is_active BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 0, -- Higher priority = evaluated first
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_policies_team_id ON policies(team_id);
CREATE INDEX idx_policies_app_id ON policies(app_id);
CREATE INDEX idx_policies_is_active ON policies(is_active);

-- ============================================================================
-- ALERTS & NOTIFICATIONS
-- ============================================================================

CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    app_id UUID REFERENCES apps(id) ON DELETE CASCADE,
    
    alert_type VARCHAR(50) NOT NULL, -- threshold_exceeded, policy_violation, anomaly_detected
    severity VARCHAR(20) NOT NULL, -- info, warning, critical
    
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    
    -- Related data
    metric_name VARCHAR(100), -- energy_wh, co2_g, cost_usd
    metric_value DECIMAL(12, 4),
    threshold_value DECIMAL(12, 4),
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, acknowledged, resolved
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    
    metadata JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_team_id ON alerts(team_id);
CREATE INDEX idx_alerts_app_id ON alerts(app_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);

-- ============================================================================
-- RECOMMENDATIONS (AI-generated optimization suggestions)
-- ============================================================================

CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    app_id UUID REFERENCES apps(id) ON DELETE CASCADE,
    
    recommendation_type VARCHAR(50) NOT NULL, -- model_switch, prompt_optimization, region_migration
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    
    -- Impact estimation
    estimated_co2_savings_g DECIMAL(12, 4),
    estimated_cost_savings_usd DECIMAL(12, 4),
    estimated_energy_savings_wh DECIMAL(12, 4),
    
    -- Implementation
    difficulty VARCHAR(20), -- low, medium, high
    implementation_steps TEXT,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, applied, dismissed
    applied_at TIMESTAMPTZ,
    
    metadata JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_recommendations_team_id ON recommendations(team_id);
CREATE INDEX idx_recommendations_app_id ON recommendations(app_id);
CREATE INDEX idx_recommendations_status ON recommendations(status);

-- ============================================================================
-- REGIONAL CARBON INTENSITY (Reference data)
-- ============================================================================

CREATE TABLE carbon_intensity_regions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    region_code VARCHAR(50) NOT NULL UNIQUE, -- us-east-1, eu-west-3
    region_name VARCHAR(255) NOT NULL,
    cloud_provider VARCHAR(50), -- aws, azure, gcp
    
    -- Carbon intensity
    carbon_intensity DECIMAL(10, 6) NOT NULL, -- kg CO2/kWh
    renewable_percentage DECIMAL(5, 2), -- 0-100
    
    -- Location
    country VARCHAR(100),
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_carbon_intensity_region_code ON carbon_intensity_regions(region_code);

-- Insert sample carbon intensity data
INSERT INTO carbon_intensity_regions (region_code, region_name, cloud_provider, carbon_intensity, renewable_percentage, country) VALUES
('us-east-1', 'US East (N. Virginia)', 'aws', 0.4, 25.0, 'USA'),
('us-west-2', 'US West (Oregon)', 'aws', 0.2, 65.0, 'USA'),
('eu-west-3', 'EU West (Paris)', 'aws', 0.1, 85.0, 'France'),
('eu-central-1', 'EU Central (Frankfurt)', 'aws', 0.15, 70.0, 'Germany'),
('ap-southeast-1', 'Asia Pacific (Singapore)', 'aws', 0.5, 15.0, 'Singapore'),
('ca-central-1', 'Canada (Central)', 'aws', 0.05, 95.0, 'Canada');

-- ============================================================================
-- USERS (For dashboard authentication)
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    
    role VARCHAR(50) DEFAULT 'viewer', -- admin, analyst, developer, viewer
    
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_team_id ON users(team_id);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to relevant tables
CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_apps_updated_at BEFORE UPDATE ON apps
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_models_updated_at BEFORE UPDATE ON models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_carbon_metrics_updated_at BEFORE UPDATE ON carbon_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_policies_updated_at BEFORE UPDATE ON policies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recommendations_updated_at BEFORE UPDATE ON recommendations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS (For common queries)
-- ============================================================================

-- View: Recent requests with model details
CREATE VIEW v_recent_requests AS
SELECT 
    r.id,
    r.timestamp,
    a.name AS app_name,
    r.model_name,
    r.provider,
    r.tokens_total,
    r.energy_wh,
    r.co2_g,
    r.latency_ms,
    r.use_case,
    r.region
FROM genai_requests r
JOIN apps a ON r.app_id = a.id
ORDER BY r.timestamp DESC;

-- View: Daily metrics summary
CREATE VIEW v_daily_metrics AS
SELECT 
    DATE(timestamp) AS date,
    app_id,
    COUNT(*) AS total_requests,
    SUM(tokens_total) AS total_tokens,
    SUM(energy_wh) AS total_energy_wh,
    SUM(co2_g) AS total_co2_g,
    AVG(latency_ms) AS avg_latency_ms
FROM genai_requests
GROUP BY DATE(timestamp), app_id;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE genai_requests IS 'Core logging table for all GenAI API requests. NO PROMPTS STORED - only metadata and metrics.';
COMMENT ON COLUMN genai_requests.request_hash IS 'SHA-256 hash of the request for deduplication. NOT the actual prompt.';
COMMENT ON TABLE carbon_metrics IS 'Pre-aggregated metrics for fast dashboard queries. Updated by background jobs.';
COMMENT ON TABLE policies IS 'Governance rules for controlling GenAI usage based on environmental and cost constraints.';
