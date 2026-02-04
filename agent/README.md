# Eco-Compute Windows Agent

Windows desktop agent for system-level AI usage monitoring.

## Features

- ✅ HTTP/HTTPS proxy server
- ✅ AI API detection (OpenAI, Anthropic, etc.)
- ✅ Cost & carbon footprint calculation
- ✅ Local SQLite caching
- ✅ Cloud sync
- ✅ Windows system integration

## Building

```bash
# Install Rust (if not already installed)
# Download from: https://rustup.rs/

# Build debug version
cargo build

# Build release version
cargo build --release

# Run
cargo run
```

## Configuration

Copy `config.toml.example` to `config.toml` and update:

```toml
# API Settings
api_url = "http://localhost:8000"
agent_id = "your-agent-id"  # Get from registration
api_key = "your-api-key"    # Get from registration
```

## Registration

1. Login to Eco-Compute dashboard
2. Navigate to "Agents" section
3. Click "Register New Agent"
4. Copy the agent_id and api_key
5. Update `config.toml`

## Running

```bash
# Development
cargo run

# Production (as Windows Service)
# TODO: Service installation instructions
```

## Project Structure

```
agent/
├── src/
│   ├── main.rs           # Entry point
│   ├── config/           # Configuration
│   ├── proxy/            # HTTP/HTTPS proxy
│   ├── detector/         # AI API detection
│   ├── metrics/          # Cost/energy calculation
│   ├── storage/          # Local SQLite + sync
│   ├── windows/          # Windows integration
│   └── api/              # Cloud API client
├── Cargo.toml
└── config.toml.example
```

## Development Status

- [x] Project structure
- [x] Configuration management
- [x] Local SQLite storage
- [x] Windows registry integration
- [x] AI detection patterns
- [x] Metrics calculation
- [ ] HTTP proxy implementation
- [ ] HTTPS/TLS support
- [ ] Request/response parsing
- [ ] Cloud sync implementation
- [ ] Windows Service wrapper
- [ ] System tray UI

## License

Proprietary - Allianz Technology
