"""
Local SQLite cache
"""

use rusqlite::{Connection, Result};
use tracing::info;

pub struct LocalCache {
    _conn: Connection,
}

impl LocalCache {
    pub fn new(db_path: &str) -> Result<Self> {
        let conn = Connection::open(db_path)?;
        
        // Create table
        conn.execute(
            "CREATE TABLE IF NOT EXISTS ai_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_name TEXT NOT NULL,
                computer_name TEXT NOT NULL,
                process_name TEXT,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                tokens_input INTEGER,
                tokens_output INTEGER,
                tokens_total INTEGER,
                cost_usd REAL,
                energy_wh REAL,
                co2_g REAL,
                latency_ms INTEGER,
                synced INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )",
            [],
        )?;

        info!("✅ Local database table created/verified");

        Ok(Self { _conn: conn })
    }
}
