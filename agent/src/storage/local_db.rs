
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
        
        // Create table
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

        info!("✅ Local database table created/verified");

        Ok(Self { 
            conn: Mutex::new(conn)
        })
    }

    pub fn get_connection(&self) -> std::sync::MutexGuard<Connection> {
        self.conn.lock().unwrap()
    }
}
