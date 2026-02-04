//! Eco-Compute Windows Desktop Agent
//!
//! System-level monitoring of AI API usage with automatic cost and carbon tracking.

use anyhow::Result;
use tracing::{info, error};
use tracing_subscriber;

mod config;
mod proxy;
mod detector;
mod metrics;
mod storage;
mod windows;
mod api;

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize logging
    tracing_subscriber::fmt()
        .with_env_filter("ecocompute_agent=debug,info")
        .init();

    info!("🚀 Eco-Compute Agent starting...");
    info!("Version: {}", env!("CARGO_PKG_VERSION"));

    // Load configuration
    let config = config::load_config()?;
    info!("✅ Configuration loaded");

    // Initialize local database
    let db = storage::LocalCache::new(&config.db_path)?;
    info!("✅ Local database initialized");

    // Set Windows system proxy
    #[cfg(target_os = "windows")]
    {
        windows::registry::set_system_proxy(true, &config.proxy_addr)?;
        info!("✅ System proxy configured: {}", config.proxy_addr);
    }

    // Setup Ctrl+C handler for graceful shutdown
    tokio::spawn(async move {
        tokio::signal::ctrl_c().await.expect("Failed to listen for Ctrl+C");
        info!("🛑 Shutdown signal received");
        
        // Disable system proxy
        #[cfg(target_os = "windows")]
        {
            if let Err(e) = windows::registry::set_system_proxy(false, "") {
                error!("Failed to disable proxy: {}", e);
            } else {
                info!("✅ System proxy disabled");
            }
        }
        
        std::process::exit(0);
    });

    // Start proxy server
    info!("🌐 Starting proxy server on {}...", config.proxy_addr);
    
    match proxy::start_server(config.clone(), db).await {
        Ok(_) => {
            info!("✅ Proxy server started successfully");
        }
        Err(e) => {
            error!("❌ Proxy server error: {}", e);
            
            // Cleanup: disable system proxy
            #[cfg(target_os = "windows")]
            {
                let _ = windows::registry::set_system_proxy(false, "");
            }
            
            return Err(e);
        }
    }

    Ok(())
}
