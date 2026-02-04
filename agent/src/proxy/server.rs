"""
Proxy server implementation
"""

use anyhow::Result;
use tokio::net::TcpListener;
use tracing::{info, error};
use crate::config::Config;
use crate::storage::LocalCache;

pub async fn start_server(config: Config, _db: LocalCache) -> Result<()> {
    let addr = config.proxy_addr.clone();
    let listener = TcpListener::bind(&addr).await?;
    
    info!("✅ Proxy server listening on {}", addr);
    
    loop {
        match listener.accept().await {
            Ok((stream, peer_addr)) => {
                info!("📥 New connection from: {}", peer_addr);
                
                // TODO: Handle connection
                // For now, just accept and close
                drop(stream);
            }
            Err(e) => {
                error!("❌ Accept error: {}", e);
            }
        }
    }
}
