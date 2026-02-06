
use rusqlite::{Connection, Result};
use tracing::info;
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
    ) -> Result<()> {
        let conn = self.get_connection();
        
        // Get system info
        let computer_name = whoami::devicename();
        // let user_name = whoami::username(); // Not used in backend schema directly, maybe in future
        
        // Generate new UUID for the record ID
        let id = uuid::Uuid::new_v4().to_string();
        
        // Current timestamp in ISO format (SQLAlchemy/SQLite friendly)
        let timestamp = chrono::Utc::now().naive_utc().to_string();

        // Note: We are writing directly to the backend's `genai_requests` table.
        // Schema keys: id, request_hash, model_name, provider, tokens_input, tokens_output, tokens_total, 
        //              latency_ms, computer_name, timestamp, user_id (FK), created_at
        // Foreign keys like app_id, model_id, agent_id are left NULL as the agent doesn't have them yet.
        // user_id is passed as string (UUID)
        
        conn.execute(
            "INSERT INTO genai_requests (
                id, request_hash, timestamp, user_id, 
                model_name, provider, 
                tokens_input, tokens_output, tokens_total,
                latency_ms, computer_name, created_at
            ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?3)",
            (
                id,             // ?1: id
                request_id,     // ?2: request_hash (mapped from request_id)
                timestamp,      // ?3: timestamp & created_at
                user_id.replace("-", ""), // ?4: user_id (strip hyphens to match backend UUID format)
                model,          // ?5: model_name
                provider,       // ?6: provider
                prompt_tokens,  // ?7: tokens_input
                completion_tokens, // ?8: tokens_output
                total_tokens,   // ?9: tokens_total
                latency_ms,     // ?10: latency_ms
                computer_name,  // ?11: computer_name
            ),
        )?;
        
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
