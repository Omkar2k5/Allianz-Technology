use anyhow::Result;
use std::sync::Arc;
use tokio::time::{interval, Duration};
use tracing::{info, error, warn, debug};
use serde::{Serialize, Deserialize};

use crate::config::Config;
use crate::storage::LocalCache;



#[derive(Deserialize)]
struct BatchLogResponse {
    synced_count: i32,
    failed_ids: Vec<String>,
}

pub async fn start_sync_loop(db: Arc<LocalCache>, config: Config, jwt_token: String) {
    let mut interval = interval(Duration::from_secs(5)); // Sync every 5 seconds for near-real-time updates
    
    info!("🔄 Background sync task started (interval: 5s)");
    
    loop {
        interval.tick().await;
        
        if let Err(e) = sync_logs(&db, &config, &jwt_token).await {
            error!("❌ Sync failed: {}", e);
        }
    }
}

async fn sync_logs(db: &LocalCache, config: &Config, jwt_token: &str) -> Result<()> {
    // Get unsynced logs
    let logs = db.get_unsynced_requests()?;
    
    if logs.is_empty() {
        return Ok(());
    }
    
    info!("📤 Syncing {} logs to backend...", logs.len());
    
    // Send to backend
    let client = reqwest::Client::builder()
        .no_proxy() // Don't use system proxy for backend calls
        .build()?;
    let response = client
        .post(format!("{}/api/agent/logs/batch", config.api_url))
        .header("Authorization", format!("Bearer {}", jwt_token))
        .json(&serde_json::json!({ "logs": logs }))
        .send()
        .await?;
    
    if response.status().is_success() {
        let result: BatchLogResponse = response.json().await?;
        
        // Mark as synced
        let all_ids: Vec<String> = logs.iter().map(|l| l.request_id.clone()).collect();
        let failed_set: std::collections::HashSet<_> = result.failed_ids.iter().collect();
        
        let synced_ids: Vec<String> = all_ids.into_iter()
            .filter(|id| !failed_set.contains(id))
            .collect();
        
        if !synced_ids.is_empty() {
            db.mark_as_synced(&synced_ids)?;
            info!("✅ Synced {} logs successfully", result.synced_count);
        }
        
        if !result.failed_ids.is_empty() {
            warn!("⚠️  {} logs failed to sync", result.failed_ids.len());
        }
    } else {
        error!("❌ Sync failed with status: {}", response.status());
        let text = response.text().await?;
        debug!("Response: {}", text);
    }
    
    Ok(())
}
