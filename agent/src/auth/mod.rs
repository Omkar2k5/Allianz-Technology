
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
    name: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct AuthResponse {
    user_id: String,
    email: String,
    jwt_token: String,
    refresh_token: Option<String>,
    expires_in: i64, // seconds
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
        .post(format!("{}/api/agent/login", config.api_url))
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
        user_id: auth_response.user_id,
        email: auth_response.email,
        jwt_token: auth_response.jwt_token,
        refresh_token: auth_response.refresh_token,
        expires_at: Utc::now() + Duration::seconds(auth_response.expires_in),
    };

    // Store session
    store_session(db, &session)?;
    
    info!("✅ Login successful: {}", session.email);
    Ok(session)
}

async fn register(config: &Config, db: &LocalCache) -> Result<UserSession> {
    println!("\n📝 Register for Eco-Compute");
    
    let name: String = Input::new()
        .with_prompt("Full Name")
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
        .post(format!("{}/api/agent/register", config.api_url))
        .json(&RegisterRequest { email: email.clone(), password, name })
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
        user_id: auth_response.user_id,
        email: auth_response.email,
        jwt_token: auth_response.jwt_token,
        refresh_token: auth_response.refresh_token,
        expires_at: Utc::now() + Duration::seconds(auth_response.expires_in),
    };

    // Store session
    store_session(db, &session)?;
    
    info!("✅ Registration successful: {}", session.email);
    Ok(session)
}

pub fn get_stored_session(db: &LocalCache) -> Result<Option<UserSession>> {
    let conn = db.get_connection();
    
    let mut stmt = conn.prepare(
        "SELECT user_id, email, jwt_token, refresh_token, expires_at 
         FROM user_session 
         ORDER BY id DESC 
         LIMIT 1"
    )?;

    let session = stmt.query_row([], |row| {
        Ok(UserSession {
            user_id: row.get(0)?,
            email: row.get(1)?,
            jwt_token: row.get(2)?,
            refresh_token: row.get(3)?,
            expires_at: row.get::<_, String>(4)?
                .parse::<DateTime<Utc>>()
                .map_err(|e| rusqlite::Error::ToSqlConversionFailure(Box::new(e)))?,
        })
    });

    match session {
        Ok(s) => Ok(Some(s)),
        Err(rusqlite::Error::QueryReturnedNoRows) => Ok(None),
        Err(e) => Err(e.into()),
    }
}

pub fn store_session(db: &LocalCache, session: &UserSession) -> Result<()> {
    let conn = db.get_connection();
    
    // Clear old sessions
    conn.execute("DELETE FROM user_session", [])?;
    
    // Insert new session
    conn.execute(
        "INSERT INTO user_session (user_id, email, jwt_token, refresh_token, expires_at) 
         VALUES (?1, ?2, ?3, ?4, ?5)",
        (
            &session.user_id,
            &session.email,
            &session.jwt_token,
            &session.refresh_token,
            session.expires_at.to_rfc3339(),
        ),
    )?;

    Ok(())
}

pub fn clear_session(db: &LocalCache) -> Result<()> {
    let conn = db.get_connection();
    conn.execute("DELETE FROM user_session", [])?;
    Ok(())
}
