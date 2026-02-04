

use serde::{Deserialize, Serialize};
use anyhow::Result;
use std::fs;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    // Proxy settings
    pub proxy_addr: String,
    pub proxy_port: u16,
    
    // API settings
    pub api_url: String,
    pub agent_id: Option<String>,
    pub api_key: Option<String>,
    
    // Storage
    pub db_path: String,
    
    // Sync settings
    pub sync_interval_secs: u64,
    pub batch_size: usize,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            proxy_addr: "127.0.0.1:8080".to_string(),
            proxy_port: 8080,
            api_url: "http://localhost:8000".to_string(),
            agent_id: None,
            api_key: None,
            db_path: "ecocompute.db".to_string(),
            sync_interval_secs: 300, // 5 minutes
            batch_size: 100,
        }
    }
}

pub fn load_config() -> Result<Config> {
    // Try to load from config file
    match fs::read_to_string("config.toml") {
        Ok(contents) => {
            let config: Config = toml::from_str(&contents)?;
            Ok(config)
        }
        Err(_) => {
            // Use default config
            let config = Config::default();
            
            // Save default config
            let toml_str = toml::to_string_pretty(&config)?;
            fs::write("config.toml", toml_str)?;
            
            Ok(config)
        }
    }
}
