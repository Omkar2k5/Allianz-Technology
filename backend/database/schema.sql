-- Eco-Compute Database Schema
-- PostgreSQL 15+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop tables if they exist (Order matters due to foreign keys)
DROP TABLE IF EXISTS user_model_recommendations CASCADE;
DROP TABLE IF EXISTS recommendations CASCADE;
DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS policies CASCADE;
DROP TABLE IF EXISTS carbon_metrics CASCADE;
DROP TABLE IF EXISTS genai_requests CASCADE;
DROP TABLE IF EXISTS agents CASCADE;
DROP TABLE IF EXISTS refresh_tokens CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS models CASCADE;
DROP TABLE IF EXISTS apps CASCADE;
DROP TABLE IF EXISTS carbon_intensity_regions CASCADE;
DROP TABLE IF EXISTS datacenter_info CASCADE;
DROP TABLE IF EXISTS model_specs CASCADE;

-- ============================================================================
-- APPLICATIONS
-- ============================================================================

CREATE TABLE apps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    environment VARCHAR(50) DEFAULT 'production', -- development, staging, production
    api_key_hash VARCHAR(255) UNIQUE NOT NULL, -- Hashed API key for SDK auth
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_apps_api_key_hash ON apps(api_key_hash);

-- ============================================================================
-- USERS (For dashboard authentication)
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    
    full_name VARCHAR(255),
    -- first_name VARCHAR(100), -- Removed to match model
    -- last_name VARCHAR(100), -- Removed to match model
    
    -- role VARCHAR(50) DEFAULT 'viewer', -- Removed to match model (not in User model)
    is_superuser BOOLEAN DEFAULT false, -- Added to match model
    
    is_active BOOLEAN DEFAULT true,
    -- last_login TIMESTAMPTZ, -- Removed to match model
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

COMMENT ON TABLE users IS 'Dashboard users with authentication credentials';
COMMENT ON COLUMN users.hashed_password IS 'Bcrypt hashed password';

-- ============================================================================
-- GENAI REQUESTS (Core logging table)
-- ============================================================================

CREATE TABLE genai_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    app_id UUID REFERENCES apps(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),  -- Track which user made the request
    
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
CREATE INDEX idx_carbon_metrics_period ON carbon_metrics(period_start, period_end);
CREATE INDEX idx_carbon_metrics_granularity ON carbon_metrics(granularity);

-- ============================================================================
-- POLICIES (Governance rules)
-- ============================================================================

CREATE TABLE policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

CREATE INDEX idx_policies_app_id ON policies(app_id);
CREATE INDEX idx_policies_is_active ON policies(is_active);

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
-- REFRESH TOKENS (JWT Token Management)
-- ============================================================================

CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

COMMENT ON TABLE refresh_tokens IS 'JWT refresh tokens for extended user sessions';

-- ============================================================================
-- MODEL SPECS
-- ============================================================================

CREATE TABLE model_specs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(255) NOT NULL UNIQUE,
    provider VARCHAR(100) NOT NULL,
    model_family VARCHAR(100),
    parameters VARCHAR(50),
    architecture VARCHAR(100),
    gpu_type VARCHAR(100),
    energy_j_per_token FLOAT,
    energy_kwh_per_1k_tokens FLOAT,
    co2_g_per_1k_tokens FLOAT,
    training_energy_mwh FLOAT,
    training_co2_tons FLOAT,
    quality_score FLOAT,
    latency_ms_per_token FLOAT,
    cost_per_1k_input_tokens FLOAT,
    cost_per_1k_output_tokens FLOAT,
    data_source VARCHAR(255),
    is_measured BOOLEAN DEFAULT false,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_model_specs_model_name ON model_specs(model_name);

-- ============================================================================
-- DATACENTER INFO
-- ============================================================================

CREATE TABLE datacenter_info (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider VARCHAR(100) NOT NULL,
    region_code VARCHAR(50) NOT NULL,
    region_name VARCHAR(255),
    country VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    carbon_intensity_g_per_kwh FLOAT,
    renewable_percent FLOAT,
    pue FLOAT DEFAULT 1.2,
    coal_percent FLOAT,
    natural_gas_percent FLOAT,
    nuclear_percent FLOAT,
    hydro_percent FLOAT,
    wind_percent FLOAT,
    solar_percent FLOAT,
    data_source VARCHAR(255),
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

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
CREATE TRIGGER update_apps_updated_at BEFORE UPDATE ON apps
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_carbon_metrics_updated_at BEFORE UPDATE ON carbon_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_policies_updated_at BEFORE UPDATE ON policies
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
