-- Migration: Add agent support
-- Version: 002
-- Description: Add agents table and agent tracking to genai_requests

-- Create agents table
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    computer_id VARCHAR(255) UNIQUE NOT NULL,
    computer_name VARCHAR(255),
    
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    
    agent_version VARCHAR(50),
    os_version VARCHAR(100),
    
    status VARCHAR(20) DEFAULT 'active',
    last_heartbeat TIMESTAMPTZ,
    
    installed_by UUID REFERENCES users(id),
    installed_at TIMESTAMPTZ DEFAULT NOW(),
    
    api_key_hash VARCHAR(255),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_agents_team_id ON agents(team_id);
CREATE INDEX IF NOT EXISTS idx_agents_computer_id ON agents(computer_id);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_last_heartbeat ON agents(last_heartbeat);

-- Add columns to genai_requests
ALTER TABLE genai_requests ADD COLUMN IF NOT EXISTS agent_id UUID REFERENCES agents(id);
ALTER TABLE genai_requests ADD COLUMN IF NOT EXISTS computer_name VARCHAR(255);
ALTER TABLE genai_requests ADD COLUMN IF NOT EXISTS process_name VARCHAR(255);

-- Create indexes for new columns
CREATE INDEX IF NOT EXISTS idx_genai_requests_agent_id ON genai_requests(agent_id);
CREATE INDEX IF NOT EXISTS idx_genai_requests_computer_name ON genai_requests(computer_name);
CREATE INDEX IF NOT EXISTS idx_genai_requests_process_name ON genai_requests(process_name);

-- Add comments
COMMENT ON TABLE agents IS 'Desktop monitoring agents installed on employee computers';
COMMENT ON COLUMN agents.computer_id IS 'Unique hardware identifier (e.g., motherboard UUID + MAC)';
COMMENT ON COLUMN agents.last_heartbeat IS 'Updated every 5 minutes by agent';
COMMENT ON COLUMN genai_requests.agent_id IS 'Desktop agent that captured this request';
COMMENT ON COLUMN genai_requests.process_name IS 'Application that made the API call (e.g., chrome.exe, vscode.exe)';
