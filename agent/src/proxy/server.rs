
use anyhow::Result;
use tracing::{info, error, debug};
use std::sync::Arc;
use std::net::SocketAddr;
use tokio::net::{TcpListener, TcpStream};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use crate::config::Config;
use crate::storage::LocalCache;
use crate::detector::AIDetector;

pub async fn start_server(config: Config, db: LocalCache) -> Result<()> {
    let addr: SocketAddr = config.proxy_addr.parse()?;
    let listener = TcpListener::bind(&addr).await?;
    let db = Arc::new(db);
    let ai_detector = Arc::new(AIDetector::new());
    
    info!("✅ Proxy server listening on {}", config.proxy_addr);
    info!("🌐 Proxy server started successfully");
    
    loop {
        let (stream, peer_addr) = listener.accept().await?;
        let db_clone = Arc::clone(&db);
        let ai_detector_clone = Arc::clone(&ai_detector);
        
        // Spawn a task to handle the connection
        tokio::spawn(async move {
            if let Err(e) = handle_connection(stream, db_clone, ai_detector_clone).await {
                debug!("Connection error from {}: {}", peer_addr, e);
            }
        });
    }
}

async fn handle_connection(
    stream: TcpStream,
    _db: Arc<LocalCache>,
    ai_detector: Arc<AIDetector>,
) -> Result<()> {
    // Read the first line to determine if it's a CONNECT request
    let mut buffer = vec![0u8; 8192];
    let n = stream.peek(&mut buffer).await?;
    
    if n == 0 {
        return Ok(());
    }
    
    let request_line = String::from_utf8_lossy(&buffer[..n]);
    
    // Check if this is a CONNECT request
    if request_line.starts_with("CONNECT ") {
        handle_connect_tunnel(stream, ai_detector).await
    } else {
        handle_http_request(stream, _db, ai_detector).await
    }
}

async fn handle_connect_tunnel(
    mut client_stream: TcpStream,
    ai_detector: Arc<AIDetector>,
) -> Result<()> {
    // Read the CONNECT request
    let mut buffer = vec![0u8; 8192];
    let n = client_stream.read(&mut buffer).await?;
    
    if n == 0 {
        return Ok(());
    }
    
    let request = String::from_utf8_lossy(&buffer[..n]);
    
    // Parse the CONNECT request to get the target host:port
    let first_line = request.lines().next().unwrap_or("");
    let parts: Vec<&str> = first_line.split_whitespace().collect();
    
    if parts.len() < 2 || parts[0] != "CONNECT" {
        let response = "HTTP/1.1 400 Bad Request\r\n\r\n";
        client_stream.write_all(response.as_bytes()).await?;
        return Ok(());
    }
    
    let target = parts[1];
    debug!("🔒 CONNECT tunnel to: {}", target);
    
    // Check if this is an AI API request
    let host = target.split(':').next().unwrap_or("");
    if ai_detector.is_ai_request(host, "") {
        info!("🤖 AI API HTTPS request detected: {}", host);
        // TODO: For now, we'll just tunnel. Later we can intercept with TLS.
    }
    
    // Connect to the target server
    match TcpStream::connect(target).await {
        Ok(mut target_stream) => {
            // Send 200 Connection Established response
            let response = "HTTP/1.1 200 Connection Established\r\n\r\n";
            client_stream.write_all(response.as_bytes()).await?;
            
            debug!("✅ Tunnel established to {}", target);
            
            // Start bidirectional copying
            let (mut client_read, mut client_write) = client_stream.split();
            let (mut target_read, mut target_write) = target_stream.split();
            
            let client_to_target = async {
                tokio::io::copy(&mut client_read, &mut target_write).await
            };
            
            let target_to_client = async {
                tokio::io::copy(&mut target_read, &mut client_write).await
            };
            
            // Run both directions concurrently
            tokio::select! {
                result = client_to_target => {
                    if let Err(e) = result {
                        debug!("Client to target copy error: {}", e);
                    }
                }
                result = target_to_client => {
                    if let Err(e) = result {
                        debug!("Target to client copy error: {}", e);
                    }
                }
            }
            
            debug!("🔒 Tunnel closed to {}", target);
        }
        Err(e) => {
            error!("Failed to connect to {}: {}", target, e);
            let response = "HTTP/1.1 502 Bad Gateway\r\n\r\n";
            client_stream.write_all(response.as_bytes()).await?;
        }
    }
    
    Ok(())
}

async fn handle_http_request(
    stream: TcpStream,
    _db: Arc<LocalCache>,
    _ai_detector: Arc<AIDetector>,
) -> Result<()> {
    // For HTTP requests, we'll use a simple forwarding approach
    let mut client_stream = stream;
    let mut buffer = vec![0u8; 8192];
    let n = client_stream.read(&mut buffer).await?;
    
    if n == 0 {
        return Ok(());
    }
    
    let request = String::from_utf8_lossy(&buffer[..n]);
    
    // Parse the request line
    let first_line = request.lines().next().unwrap_or("");
    let parts: Vec<&str> = first_line.split_whitespace().collect();
    
    if parts.len() < 3 {
        let response = "HTTP/1.1 400 Bad Request\r\n\r\n";
        client_stream.write_all(response.as_bytes()).await?;
        return Ok(());
    }
    
    // Extract host from headers
    let host = request
        .lines()
        .find(|line| line.to_lowercase().starts_with("host:"))
        .and_then(|line| line.split(':').nth(1))
        .map(|h| h.trim())
        .unwrap_or("");
    
    if host.is_empty() {
        let response = "HTTP/1.1 400 Bad Request\r\nContent-Length: 18\r\n\r\nMissing Host header";
        client_stream.write_all(response.as_bytes()).await?;
        return Ok(());
    }
    
    debug!("📨 HTTP request to: {}", host);
    
    // Connect to the target server (port 80 for HTTP)
    let target = format!("{}:80", host);
    match TcpStream::connect(&target).await {
        Ok(mut target_stream) => {
            // Forward the request
            target_stream.write_all(&buffer[..n]).await?;
            
            // Copy response back
            let mut response_buffer = vec![0u8; 8192];
            loop {
                let n = target_stream.read(&mut response_buffer).await?;
                if n == 0 {
                    break;
                }
                client_stream.write_all(&response_buffer[..n]).await?;
            }
        }
        Err(e) => {
            error!("Failed to connect to {}: {}", target, e);
            let response = "HTTP/1.1 502 Bad Gateway\r\n\r\n";
            client_stream.write_all(response.as_bytes()).await?;
        }
    }
    
    Ok(())
}
