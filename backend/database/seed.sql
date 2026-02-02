-- Seed data for Eco-Compute development and testing

-- ============================================================================
-- TEAMS
-- ============================================================================

INSERT INTO teams (id, name, organization, subscription_tier) VALUES
('11111111-1111-1111-1111-111111111111', 'Allianz Demo Team', 'Allianz SE', 'enterprise'),
('22222222-2222-2222-2222-222222222222', 'Customer Success', 'Allianz Partners', 'pro'),
('33333333-3333-3333-3333-333333333333', 'Development Team', 'Allianz Technology', 'free');

-- ============================================================================
-- USERS
-- ============================================================================

-- Password: "demo123" (hashed with bcrypt)
INSERT INTO users (id, team_id, email, password_hash, first_name, last_name, role) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', 'admin@allianz.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIvAprzZ3i', 'Admin', 'User', 'admin'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '11111111-1111-1111-1111-111111111111', 'analyst@allianz.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIvAprzZ3i', 'Data', 'Analyst', 'analyst'),
('cccccccc-cccc-cccc-cccc-cccccccccccc', '22222222-2222-2222-2222-222222222222', 'developer@allianz.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIvAprzZ3i', 'Dev', 'User', 'developer');

-- ============================================================================
-- APPLICATIONS
-- ============================================================================

INSERT INTO apps (id, team_id, name, description, environment, api_key_hash) VALUES
('app11111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 'Customer Support Chatbot', 'AI-powered customer support for insurance claims', 'production', 'hash_customer_support_key'),
('app22222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', 'Content Generator', 'Marketing content generation tool', 'production', 'hash_content_gen_key'),
('app33333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222222', 'Document Analyzer', 'Policy document analysis and summarization', 'staging', 'hash_doc_analyzer_key'),
('app44444-4444-4444-4444-444444444444', '33333333-3333-3333-3333-333333333333', 'Test Application', 'Development testing app', 'development', 'hash_test_app_key');

-- ============================================================================
-- SAMPLE GENAI REQUESTS (Last 7 days)
-- ============================================================================

-- Helper function to generate timestamps over last 7 days
DO $$
DECLARE
    app_ids UUID[] := ARRAY[
        'app11111-1111-1111-1111-111111111111'::UUID,
        'app22222-2222-2222-2222-222222222222'::UUID,
        'app33333-3333-3333-3333-333333333333'::UUID
    ];
    models TEXT[] := ARRAY['gpt-4', 'gpt-3.5-turbo', 'claude-3-opus', 'claude-3-sonnet'];
    providers TEXT[] := ARRAY['openai', 'openai', 'anthropic', 'anthropic'];
    use_cases TEXT[] := ARRAY['customer-support', 'content-generation', 'document-analysis', 'code-generation'];
    regions TEXT[] := ARRAY['us-east-1', 'us-west-2', 'eu-west-3', 'eu-central-1'];
    i INTEGER;
    random_app UUID;
    random_model TEXT;
    random_provider TEXT;
    random_use_case TEXT;
    random_region TEXT;
    random_tokens_in INTEGER;
    random_tokens_out INTEGER;
    random_timestamp TIMESTAMPTZ;
    energy DECIMAL;
    co2 DECIMAL;
    carbon_int DECIMAL;
BEGIN
    -- Generate 500 sample requests over last 7 days
    FOR i IN 1..500 LOOP
        -- Random selections
        random_app := app_ids[1 + floor(random() * array_length(app_ids, 1))];
        random_model := models[1 + floor(random() * array_length(models, 1))];
        random_provider := providers[1 + floor(random() * array_length(providers, 1))];
        random_use_case := use_cases[1 + floor(random() * array_length(use_cases, 1))];
        random_region := regions[1 + floor(random() * array_length(regions, 1))];
        
        -- Random tokens (realistic distribution)
        random_tokens_in := 100 + floor(random() * 2000);
        random_tokens_out := 50 + floor(random() * 1000);
        
        -- Random timestamp in last 7 days
        random_timestamp := NOW() - (random() * INTERVAL '7 days');
        
        -- Get carbon intensity for region
        SELECT carbon_intensity INTO carbon_int 
        FROM carbon_intensity_regions 
        WHERE region_code = random_region;
        
        -- Calculate energy (model-specific)
        energy := CASE random_model
            WHEN 'gpt-4' THEN (random_tokens_in + random_tokens_out) / 1000.0 * 0.0008 * 1000
            WHEN 'gpt-3.5-turbo' THEN (random_tokens_in + random_tokens_out) / 1000.0 * 0.0003 * 1000
            WHEN 'claude-3-opus' THEN (random_tokens_in + random_tokens_out) / 1000.0 * 0.0007 * 1000
            ELSE (random_tokens_in + random_tokens_out) / 1000.0 * 0.0005 * 1000
        END;
        
        -- Calculate CO2
        co2 := energy * carbon_int;
        
        -- Insert request
        INSERT INTO genai_requests (
            app_id, model_name, provider, timestamp,
            request_hash, tokens_input, tokens_output, tokens_total,
            energy_wh, co2_g, region, carbon_intensity,
            latency_ms, use_case, risk_level, policy_applied, policy_action
        ) VALUES (
            random_app, random_model, random_provider, random_timestamp,
            md5(random()::text), random_tokens_in, random_tokens_out, random_tokens_in + random_tokens_out,
            energy, co2, random_region, carbon_int,
            200 + floor(random() * 500), random_use_case, 
            CASE WHEN random() < 0.3 THEN 'low' WHEN random() < 0.7 THEN 'medium' ELSE 'high' END,
            random() < 0.1, 'allowed'
        );
    END LOOP;
END $$;

-- ============================================================================
-- POLICIES
-- ============================================================================

INSERT INTO policies (team_id, name, description, policy_type, conditions, action, action_config, threshold_value, threshold_unit, priority) VALUES
('11111111-1111-1111-1111-111111111111', 
 'Block GPT-4 for Low Priority', 
 'Prevent expensive GPT-4 usage for low-priority use cases',
 'model_restriction',
 '{"risk_level": "low", "model": "gpt-4"}',
 'downgrade',
 '{"downgrade_to": "gpt-3.5-turbo", "message": "Request downgraded to GPT-3.5 due to low priority"}',
 NULL, NULL, 10),

('11111111-1111-1111-1111-111111111111',
 'Daily Carbon Limit',
 'Alert when daily CO2 emissions exceed 5kg',
 'carbon_limit',
 '{}',
 'warn',
 '{"alert_channels": ["email", "dashboard"]}',
 5000, 'g_co2', 5);

-- ============================================================================
-- RECOMMENDATIONS
-- ============================================================================

INSERT INTO recommendations (team_id, app_id, recommendation_type, title, description, estimated_co2_savings_g, estimated_cost_savings_usd, difficulty, status) VALUES
('11111111-1111-1111-1111-111111111111',
 'app11111-1111-1111-1111-111111111111',
 'model_switch',
 'Switch to GPT-3.5 Turbo for Simple Queries',
 'Analysis shows 60% of your customer support queries could be handled by GPT-3.5 Turbo with similar quality but 62% less energy consumption.',
 250000, 1200, 'medium', 'pending'),

('11111111-1111-1111-1111-111111111111',
 'app22222-2222-2222-2222-222222222222',
 'region_migration',
 'Migrate to EU-West-3 (Paris)',
 'Your content generation workload is currently in US-East-1. Migrating to EU-West-3 would reduce CO2 emissions by 75% due to higher renewable energy usage.',
 320000, 0, 'medium', 'pending'),

('11111111-1111-1111-1111-111111111111',
 'app11111-1111-1111-1111-111111111111',
 'prompt_optimization',
 'Optimize Customer Support Prompts',
 'Your average prompt length is 1500 tokens. Refining prompts could reduce token usage by 15% without quality loss.',
 180000, 850, 'low', 'pending');

-- ============================================================================
-- ALERTS
-- ============================================================================

INSERT INTO alerts (team_id, app_id, alert_type, severity, title, message, metric_name, metric_value, threshold_value, status) VALUES
('11111111-1111-1111-1111-111111111111',
 'app11111-1111-1111-1111-111111111111',
 'threshold_exceeded',
 'warning',
 'High Energy Consumption Detected',
 'Customer Support Chatbot consumed 150 kWh today, exceeding the 100 kWh threshold.',
 'energy_wh', 150000, 100000, 'active'),

('11111111-1111-1111-1111-111111111111',
 'app22222-2222-2222-2222-222222222222',
 'anomaly_detected',
 'info',
 'Unusual Token Usage Pattern',
 'Content Generator showed 3x normal token usage in the last hour. This may indicate inefficient prompts.',
 'tokens_total', 150000, 50000, 'acknowledged');

-- ============================================================================
-- CARBON METRICS (Pre-aggregated daily data)
-- ============================================================================

-- Generate daily metrics for last 30 days
DO $$
DECLARE
    day_offset INTEGER;
    current_date DATE;
BEGIN
    FOR day_offset IN 0..29 LOOP
        current_date := CURRENT_DATE - day_offset;
        
        INSERT INTO carbon_metrics (
            app_id, team_id, period_start, period_end, granularity,
            total_requests, total_tokens, total_energy_wh, total_co2_g,
            avg_latency_ms, avg_tokens_per_request
        )
        SELECT 
            app_id,
            (SELECT team_id FROM apps WHERE id = app_id),
            current_date::TIMESTAMPTZ,
            (current_date + INTERVAL '1 day')::TIMESTAMPTZ,
            'daily',
            COUNT(*),
            SUM(tokens_total),
            SUM(energy_wh),
            SUM(co2_g),
            AVG(latency_ms)::INTEGER,
            AVG(tokens_total)::INTEGER
        FROM genai_requests
        WHERE DATE(timestamp) = current_date
        GROUP BY app_id;
    END LOOP;
END $$;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify data was inserted
SELECT 'Teams' AS table_name, COUNT(*) AS count FROM teams
UNION ALL
SELECT 'Users', COUNT(*) FROM users
UNION ALL
SELECT 'Apps', COUNT(*) FROM apps
UNION ALL
SELECT 'Models', COUNT(*) FROM models
UNION ALL
SELECT 'GenAI Requests', COUNT(*) FROM genai_requests
UNION ALL
SELECT 'Policies', COUNT(*) FROM policies
UNION ALL
SELECT 'Recommendations', COUNT(*) FROM recommendations
UNION ALL
SELECT 'Alerts', COUNT(*) FROM alerts
UNION ALL
SELECT 'Carbon Metrics', COUNT(*) FROM carbon_metrics
UNION ALL
SELECT 'Carbon Intensity Regions', COUNT(*) FROM carbon_intensity_regions;
