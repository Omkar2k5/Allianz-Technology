
use rusqlite::{Connection, Result};
use tracing::{info, debug};
use std::sync::Mutex;

pub struct LocalCache {
    conn: Mutex<Connection>,
}

// Implement Send and Sync for LocalCache
unsafe impl Send for LocalCache {}
unsafe impl Sync for LocalCache {}

impl LocalCache {
    pub fn new(db_path: &str) -> Result<Self> {
        let conn = Connection::open(db_path)?;
        
        // Optimize for concurrency
        conn.pragma_update(None, "journal_mode", "WAL")?;
        conn.pragma_update(None, "synchronous", "NORMAL")?;
        conn.busy_timeout(std::time::Duration::from_millis(5000))?;
        
        // We are using the Shared Backend DB (ecocompute.db).
        // The tables (genai_requests) are created by the Python backend.
        // We do NOT create tables here to avoid conflicts.
        
        // Check if we can access the table
        // let _ = conn.execute("SELECT 1 FROM genai_requests LIMIT 1", []);

        let abs_path = std::fs::canonicalize(db_path).unwrap_or_else(|_| std::path::PathBuf::from(db_path));
        info!("✅ Connected to shared database: {:?} (configured: {})", abs_path, db_path);

        Ok(Self { 
            conn: Mutex::new(conn)
        })
    }

    pub fn get_connection(&self) -> std::sync::MutexGuard<'_, Connection> {
        self.conn.lock().unwrap()
    }
    
    /// Calculate energy consumption in Wh using physics-based formula
    /// Formula: Energy (Wh) = (Node_Power_W / Batch_size) × Latency_ms × PUE / 3,600,000
    /// 
    /// Datacenter parameters (realistic):
    /// - Node power: 1200W (GPU + CPU + memory)
    /// - Batch size: 8 (concurrent requests per node)
    /// - PUE (Power Usage Effectiveness): 1.3 (datacenter overhead)
    fn calculate_energy_wh(_model: &str, _total_tokens: i32, latency_ms: i64) -> f64 {
        // Datacenter parameters
        const NODE_POWER_W: f64 = 1200.0;  // GPU + CPU + memory
        const BATCH_SIZE: f64 = 8.0;        // Concurrent requests
        const PUE: f64 = 1.3;               // Datacenter overhead (cooling, etc.)
        
        // Physics-based formula: Energy = Power × Time
        // Energy (Wh) = (Node_Power_W / Batch_size) × Latency_ms × PUE / 3,600,000
        let effective_power_w = NODE_POWER_W / BATCH_SIZE;
        let latency_hours = latency_ms as f64 / 3_600_000.0;
        
        effective_power_w * latency_hours * PUE
    }
    
    /// Detect region/datacenter from API endpoint or provider
    /// This helps track carbon intensity by geographic location
    fn detect_region(provider: &str, model: &str) -> String {
        let provider_lower = provider.to_lowercase();
        let model_lower = model.to_lowercase();
        
        // Log the inputs for debugging
        debug!("detect_region called with provider='{}', model='{}'", provider, model);

        // Detect region based on provider and model patterns
        let region = match provider_lower.as_str() {
            p if p.contains("openai") || p.contains("chatgpt") => {
                // OpenAI primarily uses US datacenters
                "US-East (Virginia)".to_string()
            },
            p if p.contains("anthropic") || p.contains("claude") => {
                // Anthropic uses AWS, primarily US regions
                "US-West (Oregon)".to_string()
            },
            p if p.contains("google") || p.contains("gemini") => {
                // Google Cloud - detect from model or default to US
                if model_lower.contains("asia") {
                    "Asia-Pacific (Singapore)".to_string()
                } else if model_lower.contains("europe") {
                    "Europe (Frankfurt)".to_string()
                } else {
                    "US-Central (Iowa)".to_string()
                }
            },
            _ => {
                // Fallback based on model name if provider is generic
                if model_lower.contains("gpt") {
                    "US-East (Virginia)".to_string()
                } else if model_lower.contains("claude") {
                    "US-West (Oregon)".to_string()
                } else if model_lower.contains("gemini") {
                    "US-Central (Iowa)".to_string()
                } else {
                    "Unknown".to_string()
                }
            }
        };
        
        debug!("detect_region result: '{}'", region);
        region
    }
    
    /// Calculate CO2 emissions in grams based on energy consumption
    fn calculate_co2_g(energy_wh: f64) -> f64 {
        // India grid carbon intensity: 750 g CO2/kWh (conservative estimate)
        // Convert Wh to kWh and multiply by carbon intensity
        (energy_wh / 1000.0) * 750.0
    }
    
    pub fn log_ai_request(
        &self,
        request_id: &str,
        user_id: &str,
        provider: &str,
        model: &str,
        prompt_tokens: i32,
        completion_tokens: i32,
        total_tokens: i32,
        latency_ms: i64,
        server_ip: Option<&str>,
    ) -> Result<()> {
        let conn = self.get_connection();
        
        // Get system info
        let computer_name = whoami::devicename();
        // let user_name = whoami::username(); // Not used in backend schema directly, maybe in future
        
        // Generate new UUID for the record ID
        let id = uuid::Uuid::new_v4().to_string();
        
        // Current timestamp in ISO format (SQLAlchemy/SQLite friendly)
        let timestamp = chrono::Utc::now().naive_utc().to_string();
        
        // Detect region and calculate energy/CO2
        let region = Self::detect_region(provider, model);
        let energy_wh = Self::calculate_energy_wh(model, total_tokens, latency_ms);
        let co2_g = Self::calculate_co2_g(energy_wh);

        // Note: We are writing directly to the backend's `genai_requests` table.
        // Schema keys: id, request_hash, model_name, provider, tokens_input, tokens_output, tokens_total, 
        //              latency_ms, computer_name, timestamp, user_id (FK), created_at, energy_wh, co2_g
        // Foreign keys like app_id, model_id, agent_id are left NULL as the agent doesn't have them yet.
        // user_id is passed as string (UUID)
        
        conn.execute(
            "INSERT INTO genai_requests (
                id, request_hash, timestamp, user_id, 
                model_name, provider, 
                tokens_input, tokens_output, tokens_total,
                latency_ms, computer_name, created_at,
                energy_wh, co2_g, region, carbon_intensity
            ) VALUES (?1, ?2, ?3, NULL, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?3, ?11, ?12, ?13, ?14)",
            (
                id,             // ?1: id
                request_id,     // ?2: request_hash (mapped from request_id)
                &timestamp,      // ?3: timestamp (also used for created_at)
                // user_id is NULL (not in params)
                model,          // ?4: model_name
                provider,       // ?5: provider
                prompt_tokens,  // ?6: tokens_input
                completion_tokens, // ?7: tokens_output
                total_tokens,   // ?8: tokens_total
                latency_ms,     // ?9: latency_ms
                computer_name,  // ?10: computer_name
                energy_wh,      // ?11: energy_wh
                co2_g,          // ?12: co2_g
                &region,        // ?13: region
                server_ip.unwrap_or("unknown"), // ?14: carbon_intensity (will be detected by backend)
            ),
        )?;
        
        info!("✅ Logged AI request to database: model={}, tokens={}, energy={:.2}Wh, co2={:.2}g", 
              model, total_tokens, energy_wh, co2_g);
        
        Ok(())
    }

    pub fn get_unsynced_requests(&self) -> Result<Vec<AIRequestLog>> {
        let conn = self.get_connection();
        let mut stmt = conn.prepare(
            "SELECT request_id, timestamp, user_id, provider, model,
                    prompt_tokens, completion_tokens, total_tokens,
                    latency_ms, region, user_name, computer_name
             FROM ai_requests
             WHERE synced = 0
             ORDER BY timestamp ASC
             LIMIT 100"
        )?;
        
        let logs = stmt.query_map([], |row| {
            Ok(AIRequestLog {
                request_id: row.get(0)?,
                timestamp: row.get(1)?,
                user_id: row.get(2)?,
                provider: row.get(3)?,
                model: row.get(4)?,
                prompt_tokens: row.get(5)?,
                completion_tokens: row.get(6)?,
                total_tokens: row.get(7)?,
                latency_ms: row.get(8)?,
                region: row.get(9)?,
                user_name: row.get(10)?,
                computer_name: row.get(11)?,
            })
        })?
        .collect::<Result<Vec<_>, _>>()?;
        
        Ok(logs)
    }
    
    pub fn mark_as_synced(&self, request_ids: &[String]) -> Result<()> {
        let conn = self.get_connection();
        if request_ids.is_empty() {
            return Ok(());
        }
        
        let placeholders = request_ids.iter()
            .map(|_| "?")
            .collect::<Vec<_>>()
            .join(",");
        
        let query = format!(
            "UPDATE ai_requests SET synced = 1 WHERE request_id IN ({})",
            placeholders
        );
        
        conn.execute(&query, rusqlite::params_from_iter(request_ids))?;
        Ok(())
    }
}

use serde::Serialize;

#[derive(Serialize)]
pub struct AIRequestLog {
    pub request_id: String,
    pub timestamp: String,
    pub user_id: String,
    pub provider: String,
    pub model: String,
    pub prompt_tokens: i32,
    pub completion_tokens: i32,
    pub total_tokens: i32,
    pub latency_ms: i64,
    pub region: String,
    pub user_name: Option<String>,
    pub computer_name: Option<String>,
}
