"""
Cloud API client for syncing logs
"""

use reqwest::Client;
use anyhow::Result;

pub struct ApiClient {
    client: Client,
    api_url: String,
    agent_id: String,
    api_key: String,
}

impl ApiClient {
    pub fn new(api_url: String, agent_id: String, api_key: String) -> Self {
        Self {
            client: Client::new(),
            api_url,
            agent_id,
            api_key,
        }
    }

    pub async fn send_heartbeat(&self) -> Result<()> {
        let url = format!("{}/api/v1/agents/heartbeat", self.api_url);
        
        let response = self.client
            .post(&url)
            .header("X-Agent-ID", &self.agent_id)
            .header("X-API-Key", &self.api_key)
            .json(&serde_json::json!({
                "agent_id": self.agent_id,
                "status": "active"
            }))
            .send()
            .await?;

        if response.status().is_success() {
            Ok(())
        } else {
            anyhow::bail!("Heartbeat failed: {}", response.status())
        }
    }

    // TODO: Add bulk log upload method
}
