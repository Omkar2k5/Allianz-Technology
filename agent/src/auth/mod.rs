
use anyhow::{Result, Context};
use dialoguer::{Input, Password, Select};
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc, Duration};
use crate::storage::LocalCache;
use crate::config::Config;
use tracing::{info, error};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserSession {
    pub user_id: String,
    pub email: String,
    pub jwt_token: String,
    pub refresh_token: Option<String>,
    pub expires_at: DateTime<Utc>,
}

impl UserSession {
    pub fn is_expired(&self) -> bool {
        Utc::now() > self.expires_at
    }
}

#[derive(Debug, Serialize, Deserialize)]
struct LoginRequest {
    email: String,
    password: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct RegisterRequest {
    email: String,
    password: String,
    first_name: String,
    last_name: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct AuthResponse {
    access_token: String,
    refresh_token: String,
    user: UserResponse,
}

#[derive(Debug, Serialize, Deserialize)]
struct UserResponse {
    id: String,
    email: String,
}


pub async fn authenticate(config: &Config, db: &LocalCache) -> Result<UserSession> {
    // Check for existing session first
    if let Some(session) = get_stored_session(db)? {
        if !session.is_expired() {
            info!("✅ Using existing session for: {}", session.email);
            return Ok(session);
        } else {
            info!("⚠️  Session expired, re-authenticating...");
        }
    }

    // Show login/signup menu
    let options = vec!["Login", "Register", "Exit"];
    let selection = Select::new()
        .with_prompt("Eco-Compute Agent Authentication")
        .items(&options)
        .default(0)
        .interact()?;

    match selection {
        0 => login(config, db).await,
        1 => register(config, db).await,
        2 => {
            info!("Exiting...");
            std::process::exit(0);
        }
        _ => unreachable!(),
    }
}

async fn login(config: &Config, db: &LocalCache) -> Result<UserSession> {
    println!("\n🔐 Login to Eco-Compute");
    
    let email: String = Input::new()
        .with_prompt("Email")
        .interact_text()?;

    let password = Password::new()
        .with_prompt("Password")
        .interact()?;

    // Call backend API (bypass proxy to avoid circular dependency)
    let client = reqwest::Client::builder()
        .no_proxy()
        .build()?;
    let response = client
        .post(format!("{}/api/v1/auth/login", config.api_url))
        .json(&LoginRequest { email: email.clone(), password })
        .send()
        .await
        .context("Failed to connect to backend")?;

    if !response.status().is_success() {
        let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
        error!("Login failed: {}", error_text);
        anyhow::bail!("Login failed: {}", error_text);
    }

    let auth_response: AuthResponse = response.json().await?;
    
    let session = UserSession {
        user_id: auth_response.user.id,
        email: auth_response.user.email,
        jwt_token: auth_response.access_token,
        refresh_token: Some(auth_response.refresh_token),
        expires_at: Utc::now() + Duration::days(1), // Default 1 day
    };

    // Store session
    store_session(db, &session)?;
    
    info!("✅ Login successful: {}", session.email);
    Ok(session)
}

async fn register(config: &Config, db: &LocalCache) -> Result<UserSession> {
    println!("\n📝 Register for Eco-Compute");
    
    let first_name: String = Input::new()
        .with_prompt("First Name")
        .interact_text()?;

    let last_name: String = Input::new()
        .with_prompt("Last Name")
        .interact_text()?;

    let email: String = Input::new()
        .with_prompt("Email")
        .interact_text()?;

    let password = Password::new()
        .with_prompt("Password")
        .with_confirmation("Confirm Password", "Passwords don't match")
        .interact()?;

    // Call backend API
    let client = reqwest::Client::builder()
        .no_proxy()
        .build()?;
    let response = client
        .post(format!("{}/api/v1/auth/register", config.api_url))
        .json(&RegisterRequest { 
            email: email.clone(), 
            password, 
            first_name,
            last_name
        })
        .send()
        .await
        .context("Failed to connect to backend")?;

    if !response.status().is_success() {
        let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
        error!("Registration failed: {}", error_text);
        anyhow::bail!("Registration failed: {}", error_text);
    }

    let auth_response: AuthResponse = response.json().await?;
    
    let session = UserSession {
        user_id: auth_response.user.id,
        email: auth_response.user.email,
        jwt_token: auth_response.access_token,
        refresh_token: Some(auth_response.refresh_token),
        expires_at: Utc::now() + Duration::days(1), // Default 1 day
    };

    // Store session
    store_session(db, &session)?;
    
    info!("✅ Registration successful: {}", session.email);
    Ok(session)
}

pub fn get_stored_session(_db: &LocalCache) -> Result<Option<UserSession>> {
    // TODO: Implement PostgreSQL session storage
    // For now, always return None to force re-authentication
    Ok(None)
}


pub fn store_session(_db: &LocalCache, _session: &UserSession) -> Result<()> {
    // TODO: Implement PostgreSQL session storage
    // For now, skip session storage
    Ok(())
}

pub fn clear_session(_db: &LocalCache) -> Result<()> {
    // TODO: Implement PostgreSQL session storage
    Ok(())
}
