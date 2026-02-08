


use tokio_postgres::{Client, NoTls, Error};
use tracing::{info, debug, error};
use tokio::sync::Mutex;
use serde_json::json;
use anyhow::{Result, Context};

pub struct LocalCache {
    conn: Mutex<Client>,
}

// Implement Send and Sync for LocalCache
unsafe impl Send for LocalCache {}
unsafe impl Sync for LocalCache {}

impl LocalCache {
    pub async fn new(db_url: &str) -> Result<Self> {
        info!("🔌 Connecting to database...");
        
        let (client, connection) = tokio::time::timeout(
            std::time::Duration::from_secs(10),
            tokio_postgres::connect(db_url, NoTls)
        ).await
        .context("Database connection timed out after 10 seconds. Check your network/firewall or if the DB is asleep.")?
        .context("Failed to connect to database")?;
        
        // Spawn connection handler
        tokio::spawn(async move {
            if let Err(e) = connection.await {
                eprintln!("PostgreSQL connection error: {}", e);
            }
        });
        
        info!("✅ Connected to PostgreSQL database: {}", db_url.split('@').last().unwrap_or("configured"));
        
        Ok(Self { 
            conn: Mutex::new(client)
        })
    }

    pub async fn get_connection(&self) -> tokio::sync::MutexGuard<'_, Client> {
        self.conn.lock().await
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
    
    /// Detect region/datacenter and carbon intensity from provider/model
    fn detect_region_info(provider: &str, model: &str) -> (String, f64) {
        let provider_lower = provider.to_lowercase();
        let model_lower = model.to_lowercase();
        
        // Carbon Intensity (gCO2/kWh) estimates:
        // US-East (Virginia): ~380 (PJM grid)
        // US-West (Oregon): ~100 (Hydro dominated)
        // US-Central (Iowa): ~475 (MISO grid)
        // Asia-Pacific (Singapore): ~400
        // Europe (Frankfurt): ~350
        // Global Average: ~475
        // India Average: ~725 (User location default fallback)

        match provider_lower.as_str() {
            p if p.contains("openai") || p.contains("chatgpt") => {
                ("US-East (Virginia)".to_string(), 380.0)
            },
            p if p.contains("anthropic") || p.contains("claude") => {
                ("US-West (Oregon)".to_string(), 100.0)
            },
            p if p.contains("google") || p.contains("gemini") => {
                if model_lower.contains("asia") {
                    ("Asia-Pacific (Singapore)".to_string(), 400.0)
                } else if model_lower.contains("europe") {
                    ("Europe (Frankfurt)".to_string(), 350.0)
                } else {
                    ("US-Central (Iowa)".to_string(), 475.0)
                }
            },
            _ => {
                if model_lower.contains("gpt") {
                    ("US-East (Virginia)".to_string(), 380.0)
                } else if model_lower.contains("claude") {
                    ("US-West (Oregon)".to_string(), 100.0)
                } else if model_lower.contains("gemini") {
                    ("US-Central (Iowa)".to_string(), 475.0)
                } else {
                    // Fallback to average or user location (India) if unknown
                    ("Unknown (India)".to_string(), 725.0)
                }
            }
        }
    }
    
    /// Calculate CO2 emissions in grams based on energy consumption
    /// Calculate CO2 emissions in grams based on energy consumption and grid intensity
    fn calculate_co2_g(energy_wh: f64, carbon_intensity_g_kwh: f64) -> f64 {
        // Convert Wh to kWh and multiply by carbon intensity
        (energy_wh / 1000.0) * carbon_intensity_g_kwh
    }
    
    pub async fn log_ai_request(
        &self,
        request_id: &str,
        _user_id: &str,
        provider: &str,
        model: &str,
        prompt_tokens: i32,
        completion_tokens: i32,
        total_tokens: i32,
        latency_ms: i64,
        server_ip: Option<&str>,
    ) -> Result<(), Error> {
        let conn = self.get_connection().await;
        
        // Get system info
        let computer_name = whoami::devicename();
        
        // Generate new UUID for the record ID
        let id = uuid::Uuid::new_v4();
        
        // Initial timestamp (use NaiveDateTime for "timestamp without time zone")
        let timestamp = chrono::Utc::now().naive_utc();
        
        // Detect region and calculate energy/CO2
        let (region, carbon_intensity) = Self::detect_region_info(provider, model);
        let energy_wh = Self::calculate_energy_wh(model, total_tokens, latency_ms);
        let co2_g = Self::calculate_co2_g(energy_wh, carbon_intensity);

        // Insert into PostgreSQL using $1, $2 placeholders
        // Create metadata JSON (only for server_ip now, computer_name has own column)
        let meta_data = json!({
            "server_ip": server_ip.unwrap_or("unknown"),
            "grid_intensity_g_kwh": carbon_intensity
        });

        // Insert into PostgreSQL using $1, $2 placeholders
        conn.execute(
            "INSERT INTO genai_requests (
                id, request_hash, timestamp, user_id, 
                model_name, provider, 
                tokens_input, tokens_output, tokens_total,
                latency_ms, created_at,
                energy_wh, co2_g, region, 
                computer_name, meta_data
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $3, $11, $12, $13, $14, $15)",
            &[
                &id,
                &request_id,
                &timestamp,
                &uuid::Uuid::parse_str(_user_id).ok(), // Returns Option<Uuid>, maps to NULL if None
                &model,
                &provider,
                &prompt_tokens,
                &completion_tokens,
                &total_tokens,
                &(latency_ms as i32),
                &energy_wh,
                &co2_g,
                &region,
                &computer_name,
                &meta_data,
            ],
        ).await.map_err(|e| {
            error!("❌ DB Error Detail: {:?}", e);
            e
        })?;
        
        info!("✅ Logged AI request to PostgreSQL: model={}, tokens={}, energy={:.2}Wh, co2={:.2}g", 
              model, total_tokens, energy_wh, co2_g);
        
        Ok(())
    }
}
