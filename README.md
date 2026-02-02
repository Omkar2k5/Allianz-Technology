# Eco-Compute: Environmental Impact Assessment for Generative AI

A comprehensive platform to help Allianz and its customers evaluate, monitor, and manage the environmental impact, energy consumption, and CO₂ footprint of Generative AI applications.

## 🏗️ Architecture

This project follows a **5-core architecture**:

1. **Frontend Dashboard** (`Frontend-Dashboard/`) - Next.js visualization platform
2. **PostgreSQL Database** (`backend/database/`) - Persistent metrics storage
3. **Analytics & Control API** (`backend/analytics-api/`) - Dashboard data & policy management
4. **Developer SDK** (`sdk/greenai-sdk/`) - Easy integration for apps
5. **GenAI Sustainability Proxy** (`backend/genai-proxy/`) - Core observability & control engine

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for SDK development)
- Python 3.11+ (for backend services)

### Run Full Stack
```bash
# Clone repository
git clone <repo-url>
cd Allianz-Technology

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# Access dashboard
open http://localhost:3000
```

### Services
- **Frontend Dashboard**: http://localhost:3000
- **Analytics API**: http://localhost:8000 (Docs: http://localhost:8000/docs)
- **GenAI Proxy**: http://localhost:8001 (Docs: http://localhost:8001/docs)
- **PostgreSQL**: localhost:5432

## 📦 Components

### Frontend Dashboard
Modern Next.js application with 8 core modules:
- Dashboard Overview
- Usage Tracking
- Energy Consumption
- Carbon Emissions
- Model Efficiency Comparison
- Recommendations & Optimization
- Reports & ESG
- Settings & Integrations

**Tech Stack**: Next.js 16, React 19, TypeScript, Tailwind CSS, Recharts

### Analytics & Control API
FastAPI backend serving dashboard data and managing policies.

**Key Endpoints**:
- `GET /api/v1/metrics/overview` - Dashboard summary
- `GET /api/v1/metrics/usage` - Usage tracking
- `GET /api/v1/metrics/energy` - Energy consumption
- `GET /api/v1/metrics/emissions` - Carbon emissions
- `POST /api/v1/policies` - Create governance policy

### GenAI Sustainability Proxy
Application-aware reverse proxy that intercepts GenAI requests to:
- Count tokens
- Calculate energy consumption
- Estimate CO₂ emissions
- Enforce policies
- Log metrics
- Forward to providers

### Developer SDK
TypeScript/JavaScript SDK for easy integration.

**Usage**:
```javascript
// Before
import OpenAI from 'openai';
const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// After
import { GreenAI } from '@greenai/sdk';
const client = new GreenAI({
  apiKey: process.env.OPENAI_API_KEY,
  proxyUrl: 'http://localhost:8001',
  appId: 'my-app',
  useCase: 'customer-support'
});

// Same API, automatic sustainability tracking
const response = await client.chat.completions.create({
  model: 'gpt-4',
  messages: [{ role: 'user', content: 'Hello!' }]
});
```

### Database Schema
PostgreSQL database with tables:
- `apps` - Application registry
- `genai_requests` - Request metadata (NO prompts stored)
- `carbon_metrics` - Aggregated sustainability metrics
- `policies` - Governance rules
- `models` - AI model catalog with energy profiles
- `teams` - Multi-tenancy support

## 🔒 Privacy & Compliance

- **NO prompt storage** - Only hashed references
- **Token-level stats only** - Metadata, not content
- **Optional PII redaction** - In SDK
- **Region-aware storage** - Compliance with data residency

## 📊 Environmental Metrics

### Energy Calculation
```
Energy (Wh) = Tokens × Model_Energy_Per_Token
```

### CO₂ Estimation
```
CO₂ (g) = Energy (Wh) × Region_Carbon_Intensity
```

### Regional Carbon Intensity
- US-East-1: 0.4 kg CO₂/kWh
- EU-West-3: 0.1 kg CO₂/kWh (renewable-heavy)
- Asia-Pacific: 0.5 kg CO₂/kWh

## 🛠️ Development

### Frontend Development
```bash
cd Frontend-Dashboard
npm install
npm run dev
```

### Backend Development
```bash
# Analytics API
cd backend/analytics-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# GenAI Proxy
cd backend/genai-proxy
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### SDK Development
```bash
cd sdk/greenai-sdk
npm install
npm run build
npm test
```

## 🧪 Testing

```bash
# Run all tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Unit tests
cd backend/analytics-api && pytest
cd backend/genai-proxy && pytest
cd sdk/greenai-sdk && npm test

# Integration tests
python tests/integration/test_full_flow.py
```

## 📈 Request Flow

```
User Application
    ↓
GreenAI SDK (metadata injection)
    ↓
GenAI Sustainability Proxy
    ├─→ Token counting
    ├─→ Energy calculation
    ├─→ CO₂ estimation
    ├─→ Policy enforcement
    ├─→ Logging to Analytics API
    └─→ Forward to OpenAI/Azure/Google
         ↓
    Response returned
         ↓
Frontend Dashboard ←─ Analytics API ←─ PostgreSQL
```

## 🌱 Sustainability Impact

**Potential Savings** (based on recommendations):
- **750 tons CO₂/year** if all optimizations applied
- **$24.5K annual cost savings**
- **40% emissions reduction** via low-carbon region routing

## 📝 License

[Your License Here]

## 🤝 Contributing

[Contribution guidelines]

## 📧 Contact

For questions or support, contact [your-email]
