-- Create user_session table for agent authentication in shared DB

CREATE TABLE IF NOT EXISTS user_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    email TEXT NOT NULL,
    jwt_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups (though table is usually small)
CREATE INDEX IF NOT EXISTS idx_user_session_user_id ON user_session(user_id);
