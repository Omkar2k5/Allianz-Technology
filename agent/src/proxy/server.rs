
use anyhow::Result;
use tracing::{info, error};
use std::sync::Arc;
use std::convert::Infallible;
use std::net::SocketAddr;
use hyper::server::conn::http1;
use hyper::service::service_fn;
use hyper::{Request, Response, StatusCode};
use hyper::body::Incoming;
use http_body_util::Full;
use bytes::Bytes;
use tokio::net::TcpListener;
use hyper_util::rt::TokioIo;
use crate::config::Config;
use crate::storage::LocalCache;
use crate::proxy::handler::ProxyHandler;

pub async fn start_server(config: Config, db: LocalCache) -> Result<()> {
    let addr: SocketAddr = config.proxy_addr.parse()?;
    let listener = TcpListener::bind(&addr).await?;
    let db = Arc::new(db);
    
    info!("✅ Proxy server listening on {}", config.proxy_addr);
    info!("🌐 Proxy server started successfully");
    
    loop {
        let (stream, peer_addr) = listener.accept().await?;
        let db_clone = Arc::clone(&db);
        
        // Spawn a task to handle the connection
        tokio::spawn(async move {
            let io = TokioIo::new(stream);
            
            // Create service for this connection
            let service = service_fn(move |req: Request<Incoming>| {
                let db = Arc::clone(&db_clone);
                async move {
                    let handler = ProxyHandler::new(db);
                    match handler.handle_request(req).await {
                        Ok(response) => Ok::<Response<Full<Bytes>>, Infallible>(response),
                        Err(e) => {
                            error!("Handler error: {}", e);
                            Ok(Response::builder()
                                .status(StatusCode::INTERNAL_SERVER_ERROR)
                                .body(Full::new(Bytes::from(format!("Error: {}", e))))
                                .unwrap())
                        }
                    }
                }
            });

            // Serve the connection
            if let Err(e) = http1::Builder::new()
                .preserve_header_case(true)
                .title_case_headers(true)
                .serve_connection(io, service)
                .await
            {
                error!("Connection error from {}: {}", peer_addr, e);
            }
        });
    }
}
