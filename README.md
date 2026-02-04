# Eco-Compute - Windows Desktop Agent

Enterprise AI monitoring solution with system-level visibility.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Employee Computer                       │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ ChatGPT  │  │ VS Code  │  │ Any App  │             │
│  │ Browser  │  │ Copilot  │  │ with AI  │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       └─────────────┴──────────────┘                    │
│                     │                                    │
│       ┌─────────────▼─────────────────┐                │
│       │   Windows Desktop Agent       │                │
│       │   (Rust - System Service)     │                │
│       │   - HTTP/HTTPS Proxy          │                │
│       │   - AI Detection              │                │
│       │   - Metrics Calculation       │                │
│       │   - Local SQLite Cache        │                │
│       └─────────────┬─────────────────┘                │
│                     │                                    │
└─────────────────────┼────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  Eco-Compute Cloud     │
         │  - Analytics API       │
         │  - Dashboard           │
         │  - PostgreSQL DB       │
         └────────────────────────┘
```

## Project Structure

```
Allianz-Technology/
├── agent/                      # Windows Desktop Agent (Rust)
│   ├── Cargo.toml
│   ├── src/
│   │   ├── main.rs
│   │   ├── proxy/             # HTTP/HTTPS proxy
│   │   ├── detector/          # AI API detection
│   │   ├── metrics/           # Cost/energy calculation
│   │   ├── storage/           # Local SQLite + cloud sync
│   │   ├── windows/           # Windows service integration
│   │   └── tray/              # System tray UI
│   └── installer/             # WiX installer
│
├── backend/
│   ├── analytics-api/         # FastAPI backend
│   │   └── app/
│   │       ├── routes/
│   │       │   ├── auth.py
│   │       │   ├── agents.py  # Agent management
│   │       │   └── dashboard.py
│   │       └── models/
│   │           └── agent_schemas.py
│   └── database/
│       ├── schema.sql         # Includes agents table
│       └── migrations/
│
└── Frontend-Dashboard/        # Next.js dashboard
    └── app/
        ├── (auth)/
        │   └── login/
        └── (dashboard)/
            ├── agents/        # Agent management UI
            └── analytics/     # AI usage analytics
```

## Components

### 1. Windows Desktop Agent (Rust)
- **Purpose:** System-level monitoring of all AI API calls
- **Technology:** Rust (performance, security, Windows integration)
- **Deployment:** Windows Service (MSI installer)
- **Features:**
  - HTTP/HTTPS proxy server
  - AI API detection (OpenAI, Anthropic, etc.)
  - Token counting & cost calculation
  - Energy & CO2 estimation
  - Local SQLite caching
  - Cloud sync every 5 minutes

### 2. Analytics API (Python/FastAPI)
- **Purpose:** Central data collection and analytics
- **Endpoints:**
  - `/api/v1/agents/*` - Agent management
  - `/api/v1/dashboard/*` - Analytics data
  - `/api/v1/auth/*` - User authentication

### 3. Dashboard (Next.js)
- **Purpose:** Web-based analytics and management
- **Features:**
  - Agent installation & management
  - Real-time AI usage monitoring
  - Cost & carbon footprint tracking
  - Team-based multi-tenancy

## Getting Started

### Backend Setup

1. **Database:**
   ```bash
   cd backend/database
   python setup_fresh.py
   ```

2. **Start API:**
   ```bash
   cd backend/analytics-api
   python -m uvicorn app.main:app --reload --port 8000
   ```

### Agent Development

1. **Install Rust:**
   ```bash
   # Download from https://rustup.rs/
   rustup-init.exe
   ```

2. **Build Agent:**
   ```bash
   cd agent
   cargo build --release
   ```

3. **Run Agent:**
   ```bash
   cargo run
   ```

## API Endpoints

### Agent Management

- `POST /api/v1/agents/register` - Register new agent
- `POST /api/v1/agents/heartbeat` - Agent heartbeat
- `POST /api/v1/agents/logs/bulk` - Upload AI request logs
- `GET /api/v1/agents/{id}/stats` - Get agent statistics
- `GET /api/v1/agents/` - List all agents

### Authentication

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user

## Development Status

### ✅ Completed
- [x] Database schema with agents table
- [x] Agent management API endpoints
- [x] Authentication system
- [x] Backend infrastructure

### 🚧 In Progress
- [ ] Rust desktop agent development
- [ ] Network proxy implementation
- [ ] AI detection engine
- [ ] System tray UI

### 📋 Planned
- [ ] MSI installer
- [ ] Dashboard agent management UI
- [ ] Real-time monitoring
- [ ] Policy enforcement

## Documentation

- [Implementation Plan](docs/agent_implementation_plan.md)
- [Backend Agent Support](docs/backend_agent_support.md)
- [API Documentation](http://localhost:8000/docs)

## License

Proprietary - Allianz Technology
