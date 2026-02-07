use anyhow::Result;
use std::sync::Arc;
use tokio::time::{interval, Duration};
use tracing::{info};

use crate::config::Config;
use crate::storage::LocalCache;

pub async fn start_sync_loop(_db: Arc<LocalCache>, _config: Config, _jwt_token: String) {
    // TODO: Implement PostgreSQL-based sync if needed
    // For now, we write directly to PostgreSQL, so no sync needed
    info!("🔄 Sync loop disabled - writing directly to PostgreSQL");
    
    // Keep the task alive but do nothing
    let mut interval = interval(Duration::from_secs(60));
    loop {
        interval.tick().await;
    }
}
