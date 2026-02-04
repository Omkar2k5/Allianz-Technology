
use anyhow::{Result, Context};
use hyper::{Request, Response, Method, StatusCode, Uri, Version};
use hyper::body::Incoming;
use http_body_util::Full;
use bytes::Bytes;
use tracing::{info, warn, error, debug};
use std::sync::Arc;
use tokio::net::TcpStream;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use hyper_util::rt::TokioIo;
use crate::detector::AIDetector;
use crate::storage::LocalCache;
use hyper_util::client::legacy::Client;
use hyper_util::rt::TokioExecutor;

pub struct ProxyHandler {
    client: Client<hyper_util::client::legacy::connect::HttpConnector, Full<Bytes>>,
    ai_detector: Arc<AIDetector>,
    pub db: Arc<LocalCache>,
}

impl ProxyHandler {
    pub fn new(db: Arc<LocalCache>) -> Self {
        let client = Client::builder(TokioExecutor::new())
            .build_http();

        Self {
            client,
            ai_detector: Arc::new(AIDetector::new()),
            db,
        }
    }

    pub async fn handle_request(&self, req: Request<Incoming>) -> Result<Response<Full<Bytes>>> {
        let method = req.method().clone();
        let uri = req.uri().clone();
        let headers = req.headers().clone();

        debug!("📨 {} {}", method, uri);

        // Handle CONNECT method for HTTPS tunneling
        if method == Method::CONNECT {
            return self.handle_connect(req).await;
        }

        // Extract host and path for AI detection
        let host = headers
            .get("host")
            .and_then(|h| h.to_str().ok())
            .unwrap_or("");
        let path = uri.path();

        // Check if this is an AI API request
        let is_ai_request = self.ai_detector.is_ai_request(host, path);
        if is_ai_request {
            info!("🤖 AI API request detected: {} {}", host, path);
            // TODO: Intercept and log request/response
        }

        // Forward regular HTTP request
        match self.forward_request(req).await {
            Ok(response) => {
                debug!("✅ Response: {}", response.status());
                Ok(response)
            }
            Err(e) => {
                error!("❌ Forward error: {}", e);
                Ok(Response::builder()
                    .status(StatusCode::BAD_GATEWAY)
                    .body(Full::new(Bytes::from(format!("Proxy Error: {}", e))))
                    .unwrap())
            }
        }
    }

    async fn handle_connect(&self, req: Request<Incoming>) -> Result<Response<Full<Bytes>>> {
        // Extract the target host and port from the URI
        let uri = req.uri();
        let host_port = uri.authority()
            .map(|auth| auth.as_str())
            .context("CONNECT request missing authority")?;

        debug!("🔒 CONNECT tunnel to: {}", host_port);

        // For now, we'll just return a 200 OK to establish the tunnel
        // The actual tunneling will be handled at the connection level
        Ok(Response::builder()
            .status(StatusCode::OK)
            .version(Version::HTTP_11)
            .body(Full::new(Bytes::new()))
            .unwrap())
    }

    async fn forward_request(&self, req: Request<Incoming>) -> Result<Response<Full<Bytes>>> {
        // Extract parts
        let (parts, body) = req.into_parts();
        
        // Collect the body
        let body_bytes = body
            .collect()
            .await
            .context("Failed to read request body")?
            .to_bytes();

        // Build the full URI if it's not already absolute
        let uri = if parts.uri.scheme().is_none() {
            // Get host from headers
            let host = parts
                .headers
                .get("host")
                .and_then(|h| h.to_str().ok())
                .context("Missing host header")?;

            // Build absolute URI
            let scheme = "http"; // We'll handle HTTPS separately with CONNECT
            let path_and_query = parts.uri.path_and_query()
                .map(|pq| pq.as_str())
                .unwrap_or("/");

            format!("{}://{}{}", scheme, host, path_and_query)
                .parse::<Uri>()
                .context("Failed to parse URI")?
        } else {
            parts.uri.clone()
        };

        // Rebuild the request
        let mut new_req = Request::builder()
            .method(parts.method)
            .uri(uri)
            .body(Full::new(body_bytes))
            .context("Failed to build request")?;

        // Copy headers (except proxy-specific ones)
        *new_req.headers_mut() = parts.headers.clone();
        new_req.headers_mut().remove("proxy-connection");

        // Forward the request
        let response = self.client
            .request(new_req)
            .await
            .context("Failed to forward request")?;

        // Collect response body
        let (parts, body) = response.into_parts();
        let body_bytes = body
            .collect()
            .await
            .context("Failed to read response body")?
            .to_bytes();

        // Rebuild response
        let mut new_response = Response::builder()
            .status(parts.status)
            .body(Full::new(body_bytes))
            .context("Failed to build response")?;

        *new_response.headers_mut() = parts.headers;

        Ok(new_response)
    }

    // Helper function to establish a tunnel (will be called from server.rs)
    pub async fn tunnel_connection(client_stream: TcpStream, target: &str) -> Result<()> {
        // Connect to the target server
        let mut target_stream = TcpStream::connect(target)
            .await
            .context("Failed to connect to target")?;

        debug!("✅ Tunnel established to {}", target);

        // Split both streams
        let (mut client_read, mut client_write) = client_stream.into_split();
        let (mut target_read, mut target_write) = target_stream.split();

        // Bidirectional copy
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
        Ok(())
    }
}
