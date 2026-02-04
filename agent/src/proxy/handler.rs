
use anyhow::{Result, Context};
use hyper::{Request, Response, Method, StatusCode, Uri};
use hyper::body::{Body, Incoming};
use hyper::client::conn::http1::SendRequest;
use http_body_util::{BodyExt, Full};
use hyper::upgrade::Upgraded;
use bytes::Bytes;
use tracing::{info, warn, error, debug};
use std::sync::Arc;
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

        // For now, just forward the request
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
}
