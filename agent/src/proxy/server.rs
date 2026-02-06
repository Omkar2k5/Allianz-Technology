
use anyhow::Result;
use tracing::{info, error, debug};
use std::sync::Arc;
use std::net::SocketAddr;
use std::convert::Infallible;

use tokio::net::{TcpListener, TcpStream};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio_rustls::{TlsAcceptor, TlsConnector};
use rustls::{ServerConfig, ClientConfig, RootCertStore};

use hyper::{Request, Response, body::Bytes};
use hyper::service::service_fn;
use hyper::server::conn::http1;
use hyper_util::rt::TokioIo;
use http_body_util::{Full, BodyExt};

use crate::config::Config;
use crate::storage::LocalCache;
use crate::detector::AIDetector;
use crate::proxy::cert::CertificateManager;
use crate::proxy::ai_parser;

pub async fn start_server(config: Config, db: Arc<LocalCache>, user_id: String) -> Result<()> {
    let addr: SocketAddr = config.proxy_addr.parse()?;
    let listener = TcpListener::bind(&addr).await?;
    let ai_detector = Arc::new(AIDetector::new());
    
    // Initialize Certificate Manager
    let cert_manager = match CertificateManager::new() {
        Ok(cm) => Arc::new(cm),
        Err(e) => {
            error!("Failed to initialize Certificate Manager: {}", e);
            return Err(e);
        }
    };
    
    // Warn user about certificate installation if needed (CLI output)
    info!("⚠️  Ensure the root CA certificate (ca_cert.pem) is trusted by your browser/system for TLS interception to work.");

    info!("✅ Proxy server listening on {}", config.proxy_addr);
    
    loop {
        let (stream, peer_addr) = listener.accept().await?;
        let db_clone = Arc::clone(&db);
        let ai_detector_clone = Arc::clone(&ai_detector);
        let cert_manager_clone = Arc::clone(&cert_manager);
        let user_id_clone = user_id.clone();
        
        tokio::spawn(async move {
            if let Err(e) = handle_connection(stream, db_clone, ai_detector_clone, cert_manager_clone, user_id_clone).await {
                debug!("Connection error from {}: {}", peer_addr, e);
            }
        });
    }
}

async fn handle_connection(
    stream: TcpStream,
    _db: Arc<LocalCache>,
    ai_detector: Arc<AIDetector>,
    cert_manager: Arc<CertificateManager>,
    user_id: String,
) -> Result<()> {
    // Read the first line to determine if it's a CONNECT request
    let mut buffer = vec![0u8; 8192];
    let n = stream.peek(&mut buffer).await?;
    
    if n == 0 {
        return Ok(());
    }
    
    let request_line = String::from_utf8_lossy(&buffer[..n]);
    
    if request_line.starts_with("CONNECT ") {
        handle_connect_tunnel(stream, ai_detector, cert_manager, _db, user_id).await
    } else {
        handle_http_request(stream).await
    }
}

async fn handle_connect_tunnel(
    mut client_stream: TcpStream,
    ai_detector: Arc<AIDetector>,
    cert_manager: Arc<CertificateManager>,
    db: Arc<LocalCache>,
    user_id: String,
) -> Result<()> {
    // Read the CONNECT request
    let mut buffer = vec![0u8; 8192];
    let n = client_stream.read(&mut buffer).await?;
    
    if n == 0 {
        return Ok(());
    }
    
    let request = String::from_utf8_lossy(&buffer[..n]);
    
    // Parse target host
    let first_line = request.lines().next().unwrap_or("");
    let parts: Vec<&str> = first_line.split_whitespace().collect();
    
    if parts.len() < 2 || parts[0] != "CONNECT" {
        return Ok(());
    }
    
    let target = parts[1];
    let host = target.split(':').next().unwrap_or("");
    
    // Check if this is an AI API request
    if ai_detector.is_ai_request(host, "") {
        info!("🤖 AI API HTTPS request detected: {}", host);
        
        // 1. Send 200 Connection Established to client
        client_stream.write_all(b"HTTP/1.1 200 Connection Established\r\n\r\n").await?;
        
        // 2. Perform TLS Interception
        if let Err(e) = intercept_tls(client_stream, host, target, cert_manager, db, user_id).await {
            error!("TLS Interception failed for {}: {}", host, e);
        }
        
    } else {
        // Transparent tunneling for non-AI traffic
        debug!("🔒 Passthrough tunnel to: {}", target);
        
        // Connect to target
        match TcpStream::connect(target).await {
            Ok(mut target_stream) => {
                client_stream.write_all(b"HTTP/1.1 200 Connection Established\r\n\r\n").await?;
                
                let (mut cr, mut cw) = client_stream.split();
                let (mut tr, mut tw) = target_stream.split();
                
                let client_to_target = tokio::io::copy(&mut cr, &mut tw);
                let target_to_client = tokio::io::copy(&mut tr, &mut cw);
                
                let _ = tokio::join!(client_to_target, target_to_client);
            }
            Err(e) => {
                let _ = client_stream.write_all(b"HTTP/1.1 502 Bad Gateway\r\n\r\n").await;
                debug!("Failed to connect to {}: {}", target, e);
            }
        }
    }
    
    Ok(())
}

async fn intercept_tls(
    client_stream: TcpStream,
    host: &str,
    target_addr: &str,
    cert_manager: Arc<CertificateManager>,
    db: Arc<LocalCache>,
    user_id: String,
) -> Result<()> {
    // 1. Generate certificate for the domain
    let (cert_pem, key_pem) = cert_manager.generate_domain_cert(host)?;
    
    let parsable_cert = rustls_pemfile::certs(&mut cert_pem.as_bytes())
        .collect::<Result<Vec<_>, _>>()?;
    
    let parsable_key = rustls_pemfile::pkcs8_private_keys(&mut key_pem.as_bytes())
        .next()
        .ok_or_else(|| anyhow::anyhow!("No private key found"))??;

    let parsable_key = rustls::pki_types::PrivateKeyDer::Pkcs8(parsable_key);

    let server_config = ServerConfig::builder()
        .with_no_client_auth()
        .with_single_cert(parsable_cert, parsable_key)?;
    
    let tls_acceptor = TlsAcceptor::from(Arc::new(server_config));
    
    // 2. Accept TLS from client
    let client_tls_stream = tls_acceptor.accept(client_stream).await?;
    let client_io = TokioIo::new(client_tls_stream);

    // 3. Setup client config to connect to upstream
    let mut root_store = RootCertStore::empty();
    root_store.extend(webpki_roots::TLS_SERVER_ROOTS.iter().cloned());
    
    let client_config = ClientConfig::builder()
        .with_root_certificates(root_store)
        .with_no_client_auth();
    let tls_connector = TlsConnector::from(Arc::new(client_config));

    // 4. Connect to upstream
    let target_stream = TcpStream::connect(target_addr).await?;
    let domain = rustls::pki_types::ServerName::try_from(host.to_string())?;
    let target_tls_stream = tls_connector.connect(domain, target_stream).await?;
    let target_io = TokioIo::new(target_tls_stream);

    // 5. Handshake HTTP/1.1 with upstream
    let (sender, conn) = hyper::client::conn::http1::handshake(target_io).await?;
    let sender = Arc::new(tokio::sync::Mutex::new(sender));
    
    tokio::spawn(async move {
        if let Err(e) = conn.await {
            error!("Upstream connection error: {}", e);
        }
    });

    // 6. Serve client requests
    let service = service_fn(move |req: Request<hyper::body::Incoming>| {
        let sender = Arc::clone(&sender);
        let db = db.clone();
        let user_id = user_id.clone();
        let provider = host.to_string(); // Simple provider detection
        
        async move {
            proxy_request(req, sender, db, user_id, provider).await
        }
    });

    if let Err(e) = http1::Builder::new()
        .serve_connection(client_io, service)
        .await
    {
        error!("Error serving connection: {}", e);
    }

    Ok(())
}

async fn proxy_request(
    req: Request<hyper::body::Incoming>,
    sender: Arc<tokio::sync::Mutex<hyper::client::conn::http1::SendRequest<Full<Bytes>>>>,
    db: Arc<LocalCache>,
    user_id: String,
    provider: String,
) -> Result<Response<Full<Bytes>>, Infallible> {
    
    // Read request body
    let (parts, body) = req.into_parts();
    let body_bytes = match body.collect().await {
        Ok(collected) => collected.to_bytes(),
        Err(_) => return Ok(Response::new(Full::default())), 
    };
    
    let body_str = String::from_utf8_lossy(&body_bytes.clone()).into_owned();
    let mut request_data = None;

    // Log ALL intercepted requests for ChatGPT to diagnose filtering
    // if provider.contains("chatgpt.com") {
    //     debug!("🔬 Intercepted ChatGPT request: method={}, path={}, body_len={}", 
    //            parts.method, parts.uri.path(), body_str.len());
    //     
    //     // Log body for /backend-api/f/conversation to understand structure
    //     if parts.uri.path().contains("/backend-api/f/conversation") && body_str.len() > 0 {
    //         debug!("📦 ChatGPT conversation body: {}", &body_str.chars().take(1000).collect::<String>());
    //     }
    // }

    // Parse AI request
    if ai_parser::is_ai_completion_endpoint(&parts.uri.path()) {
        debug!("🔍 AI endpoint detected: {}", parts.uri.path());
        request_data = ai_parser::parse_ai_request(&body_str);
        if request_data.is_none() && body_str.len() > 0 {
            let req_preview: String = body_str.chars().take(500).collect();
            debug!("📄 Request body preview (first 500 chars): {}", req_preview);
        }
    } else if parts.uri.host().map(|h| h.contains("chatgpt.com")).unwrap_or(false) {
        // Log all ChatGPT paths to help identify the actual prompt endpoint
        debug!("🔎 ChatGPT request (not matched): path={}, method={}", parts.uri.path(), parts.method);
    }
    
    // Reconstruct request to forward
    let mut upstream_req = Request::builder()
        .method(&parts.method)
        .uri(&parts.uri)
        .version(parts.version);
        
    for (k, v) in &parts.headers {
        upstream_req = upstream_req.header(k, v);
    }
    
    let upstream_req = upstream_req
        .body(Full::new(body_bytes))
        .unwrap();

    // Send to upstream
    let start_time = std::time::Instant::now();
    let mut sender_guard = sender.lock().await;
    let res = match sender_guard.send_request(upstream_req).await {
        Ok(res) => res,
        Err(e) => {
            error!("Upstream request failed: {}", e);
            return Ok(Response::builder()
                .status(502)
                .body(Full::default())
                .unwrap());
        }
    };
    drop(sender_guard); // Release lock early
    
    let latency = start_time.elapsed().as_millis() as i64;
    
    // We need to read the response body to log tokens
    let (res_parts, res_body) = res.into_parts();
    let res_bytes = match res_body.collect().await {
        Ok(collected) => collected.to_bytes(),
        Err(_) => return Ok(Response::builder().status(502).body(Full::default()).unwrap()),
    };
    
    let res_body_str = String::from_utf8_lossy(&res_bytes);
    
    // Log if we have request data
    if let Some(req_data) = request_data {
        // Skip logging for unknown models (e.g. init requests)
        let should_log = req_data.model != "unknown";

        if should_log {
            debug!("📊 Parsed AI request: model={}, prompt_len={}", req_data.model, req_data.prompt.len());
            if let Some(resp_data) = ai_parser::parse_ai_response(&res_body_str) {
                if let Err(e) = db.log_ai_request(
                    &uuid::Uuid::new_v4().to_string(),
                    &user_id,
                    &provider,
                    &req_data.model,
                    resp_data.prompt_tokens,
                    resp_data.completion_tokens,
                    resp_data.total_tokens,
                    latency
                ) {
                    error!("❌ Failed to log AI request: {}", e);
                } else {
                    info!("📝 Logged AI Request: {} ({} tokens)", req_data.model, resp_data.total_tokens);
                }
            } else {
                // Fallback: Log with estimated tokens based on content length
                // Rough estimate: 1 token ≈ 4 characters
                let estimated_prompt_tokens = (req_data.prompt.len() / 4).max(10) as i32;
                let estimated_completion_tokens = (res_body_str.len() / 4).max(10) as i32;
                let estimated_total = estimated_prompt_tokens + estimated_completion_tokens;
                
                if let Err(e) = db.log_ai_request(
                    &uuid::Uuid::new_v4().to_string(),
                    &user_id,
                    &provider,
                    &req_data.model,
                    estimated_prompt_tokens,
                    estimated_completion_tokens,
                    estimated_total,
                    latency
                ) {
                    error!("❌ Failed to log AI request (fallback): {}", e);
                }
            }
        } else {
            let body_preview: String = body_str.chars().take(200).collect();
            debug!("⚠️  Filtered AI request (unknown model): path={}, body_preview={}", parts.uri.path(), body_preview);
        }
    } else {
        // debug!("⚠️  No request data parsed for path: {}", parts.uri.path());
    }
    
    let upstream_res = Response::builder()
        .status(res_parts.status)
        .version(res_parts.version);
        
    let mut final_res = upstream_res.body(Full::new(res_bytes)).unwrap();
    *final_res.headers_mut() = res_parts.headers;

    Ok(final_res)
}

async fn handle_http_request(
    mut stream: TcpStream,
) -> Result<()> {
     // Simple forwarding for cleartext HTTP (not focus of this task)
      let mut buffer = vec![0u8; 8192];
      let n = stream.read(&mut buffer).await?;
      if n == 0 { return Ok(()); }
      
      let request = String::from_utf8_lossy(&buffer[..n]);
        let host = request
        .lines()
        .find(|line| line.to_lowercase().starts_with("host:"))
        .and_then(|line| line.split(':').nth(1))
        .map(|h| h.trim())
        .unwrap_or("");
        
    if host.is_empty() { return Ok(()); }
    
     match TcpStream::connect(format!("{}:80", host)).await {
        Ok(mut target_stream) => {
             target_stream.write_all(&buffer[..n]).await?;
             let (mut cr, mut cw) = stream.split();
             let (mut tr, mut tw) = target_stream.split();
             let _ = tokio::join!(tokio::io::copy(&mut cr, &mut tw), tokio::io::copy(&mut tr, &mut cw));
        }
        Err(_) => {}
    }
    Ok(())
}
