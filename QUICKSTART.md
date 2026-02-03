# Quick Start Guide

## 🚀 Start Services & Test

### 1. Add Your OpenRouter API Key

Edit `.env` file and add your API key:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

Get a free key at: https://openrouter.ai/keys

### 2. Start Backend Services

**Terminal 1 - Analytics API:**
```bash
cd backend/analytics-api
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - GenAI Proxy:**
```bash
cd backend/genai-proxy
python -m uvicorn app.main:app --reload --port 8001
```

### 3. Run Test

**Terminal 3:**
```bash
python test_sdk.py
```

## Expected Output

```
🧪 Eco-Compute SDK & Proxy Test Suite
============================================================

Testing Health Endpoints
============================================================
✅ Proxy: {'status': 'healthy', ...}
✅ Analytics API: {'status': 'healthy', ...}

Testing GenAI Proxy Directly
============================================================
📤 Sending request...
📥 Response Status: 200

💬 AI Response:
   [AI response about environmental impact]

🌱 Sustainability Metrics:
   Energy: 0.45 Wh
   CO₂: 0.09 g
   Tokens: 150
   Region: us-west-2

✅ Test Passed!
```

## Free Models to Test

- `google/gemma-2-9b-it:free`
- `meta-llama/llama-3-8b-instruct:free`
- `microsoft/phi-3-mini-128k-instruct:free`

## Troubleshooting

**Services not starting?**
```bash
# Install dependencies
pip install -r backend/analytics-api/requirements.txt
pip install -r backend/genai-proxy/requirements.txt
pip install -r test_requirements.txt
```

**Connection refused?**
- Make sure both services are running (ports 8000 and 8001)
- Check `.env` file has OPENROUTER_API_KEY set

See `TESTING.md` for detailed instructions.
