
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
        
        // Create ai_requests table
        conn.execute(
            "CREATE TABLE IF NOT EXISTS ai_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                user_name TEXT NOT NULL,
                computer_name TEXT NOT NULL,
                process_name TEXT,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_tokens INTEGER,
                cost_usd REAL,
                energy_wh REAL,
                co2_g REAL,
                latency_ms INTEGER,
                region TEXT,
                synced INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )",
            [],
        )?;

        // Create user_session table
        conn.execute(
            "CREATE TABLE IF NOT EXISTS user_session (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                email TEXT NOT NULL,
                jwt_token TEXT NOT NULL,
                refresh_token TEXT,
                expires_at TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )",
            [],
        )?;

        info!("✅ Local database table created/verified");

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
        let user_name = whoami::username();
        let computer_name = whoami::devicename();
        
        conn.execute(
            "INSERT INTO ai_requests (
                request_id, timestamp, user_id, user_name, computer_name,
                provider, model, prompt_tokens, completion_tokens, total_tokens,
                latency_ms, region, synced
            ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12, 0)",
            (
                request_id,
                chrono::Utc::now().to_rfc3339(),
                user_id,
                user_name,
                computer_name,
                provider,
                model,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                latency_ms,
                "unknown", // region - can be enhanced later
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
