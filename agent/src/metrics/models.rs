

use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AIRequestLog {
    pub timestamp: DateTime<Utc>,
    pub user_name: String,
    pub computer_name: String,
    pub process_name: Option<String>,
    
    pub provider: String,
    pub endpoint: String,
    pub model: String,
    
    pub tokens_input: i32,
    pub tokens_output: i32,
    pub tokens_total: i32,
    
    pub cost_usd: f64,
    pub energy_wh: f64,
    pub co2_g: f64,
    
    pub latency_ms: i32,
    pub response_status: i32,
    
    #[serde(skip_serializing_if = "Option::is_none")]
    pub prompt_hash: Option<String>,
}
