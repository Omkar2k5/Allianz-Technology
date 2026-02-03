# 🧪 Testing Eco-Compute with OpenRouter

This guide will help you test the complete Eco-Compute stack using OpenRouter's free LLM models.

## Prerequisites

1. **OpenRouter API Key** (Free)
   - Sign up at: https://openrouter.ai/
   - Get your API key: https://openrouter.ai/keys
   - Free models available (no credit card required)

2. **Python 3.11+** installed
3. **Node.js 18+** installed (for SDK)

## Quick Start

### 1. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenRouter API key
# OPENROUTER_API_KEY=sk-or-v1-...
```

### 2. Install Dependencies

```bash
# Install Python dependencies for backend services
cd backend/analytics-api
pip install -r requirements.txt
cd ../..

cd backend/genai-proxy
pip install -r requirements.txt
cd ../..

# Install test dependencies
pip install -r test_requirements.txt

# Install SDK dependencies (optional)
cd sdk/greenai-sdk
npm install
npm run build
cd ../..
```

### 3. Start Services

**Option A: Without Docker (Recommended for Testing)**

```bash
# Terminal 1: Start Analytics API
cd backend/analytics-api
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Start GenAI Proxy
cd backend/genai-proxy
python -m uvicorn app.main:app --reload --port 8001

# Terminal 3: Run tests
python test_sdk.py
```

**Option B: With Docker**

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Run tests
python test_sdk.py
```

### 4. Run Test Script

```bash
python test_sdk.py
```

Expected output:
```
🧪 Eco-Compute SDK & Proxy Test Suite
============================================================

Testing Health Endpoints
============================================================
✅ Proxy: {'status': 'healthy', 'service': 'genai-proxy', ...}
✅ Analytics API: {'status': 'healthy', 'service': 'analytics-api', ...}

Testing GenAI Proxy Directly
============================================================
📤 Sending request to: http://localhost:8001/v1/chat/completions
   Model: google/gemma-2-9b-it:free
   App ID: test-app
   Use Case: testing

📥 Response Status: 200

💬 AI Response:
   AI models consume significant energy during training and inference...

🌱 Sustainability Metrics:
   Energy: 0.45 Wh
   CO₂: 0.09 g
   Tokens: 150
   Region: us-west-2

📊 Token Usage:
   Input: 25
   Output: 125
   Total: 150

✅ Test Passed!

============================================================
🎉 All tests passed!
============================================================
```

## Free OpenRouter Models

Use these models for testing (no cost):

- `google/gemma-2-9b-it:free` - Google Gemma 2 9B
- `meta-llama/llama-3-8b-instruct:free` - Meta Llama 3 8B
- `microsoft/phi-3-mini-128k-instruct:free` - Microsoft Phi-3
- `mistralai/mistral-7b-instruct:free` - Mistral 7B

## Testing Different Scenarios

### Test 1: Basic Request

```python
import httpx

response = httpx.post(
    "http://localhost:8001/v1/chat/completions",
    json={
        "model": "google/gemma-2-9b-it:free",
        "messages": [{"role": "user", "content": "Hello!"}]
    },
    headers={
        "x-app-id": "my-app",
        "x-use-case": "testing"
    }
)

print(response.json())
print(f"Energy: {response.headers['X-Energy-Wh']} Wh")
print(f"CO₂: {response.headers['X-CO2-g']} g")
```

### Test 2: Policy Enforcement

The proxy will automatically downgrade expensive models for low-priority requests:

```python
# This will be downgraded from gpt-4 to gpt-3.5-turbo
response = httpx.post(
    "http://localhost:8001/v1/chat/completions",
    json={
        "model": "gpt-4",  # Expensive model
        "messages": [{"role": "user", "content": "Test"}]
    },
    headers={
        "x-risk-level": "low"  # Low priority
    }
)
```

### Test 3: Different Regions

Test carbon intensity differences:

```python
# High carbon region
response1 = httpx.post(..., headers={"x-region": "us-east-1"})
print(f"US-East-1 CO₂: {response1.headers['X-CO2-g']} g")

# Low carbon region
response2 = httpx.post(..., headers={"x-region": "eu-west-3"})
print(f"EU-West-3 CO₂: {response2.headers['X-CO2-g']} g")
```

## Troubleshooting

### Error: "No API key configured"

Make sure you've set `OPENROUTER_API_KEY` in your `.env` file:

```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### Error: "Connection refused"

Make sure the services are running:

```bash
# Check if services are up
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### Error: "Module not found"

Install dependencies:

```bash
pip install -r backend/analytics-api/requirements.txt
pip install -r backend/genai-proxy/requirements.txt
pip install -r test_requirements.txt
```

## Next Steps

1. ✅ Test basic proxy functionality
2. ✅ Verify sustainability metrics calculation
3. ✅ Test policy enforcement
4. 🔄 Set up PostgreSQL database
5. 🔄 Test Analytics API endpoints
6. 🔄 Connect frontend to real API
7. 🔄 View metrics in dashboard

## API Endpoints

### GenAI Proxy (Port 8001)

- `GET /health` - Health check
- `POST /v1/chat/completions` - Chat completions (OpenAI-compatible)

### Analytics API (Port 8000)

- `GET /health` - Health check
- `GET /api/v1/dashboard/overview` - Dashboard metrics
- `GET /api/v1/dashboard/usage` - Usage statistics
- `GET /api/v1/dashboard/energy` - Energy consumption
- `GET /api/v1/dashboard/emissions` - Carbon emissions

## Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Review the walkthrough: `walkthrough.md`
3. Check configuration: `.env` file

---

**Happy Testing! 🌱**
