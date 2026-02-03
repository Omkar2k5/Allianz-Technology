"""
Test script for GreenAI SDK with OpenRouter

This script demonstrates how to use the SDK to make requests
through the sustainability proxy.
"""

import asyncio
import httpx
import json

# Test configuration
PROXY_URL = "http://localhost:8001"
APP_ID = "test-app"
USE_CASE = "testing"
RISK_LEVEL = "low"

# OpenRouter API key (you'll need to set this)
OPENROUTER_API_KEY = ""  # Set your OpenRouter API key here


async def test_proxy_direct():
    """Test the proxy directly without SDK"""
    
    print("=" * 60)
    print("Testing GenAI Proxy Directly")
    print("=" * 60)
    
    # Request payload
    payload = {
        "model": "google/gemma-2-9b-it:free",  # Free model on OpenRouter
        "messages": [
            {
                "role": "user",
                "content": "What is the environmental impact of AI? Answer in one sentence."
            }
        ],
        "max_tokens": 100
    }
    
    # Headers with metadata
    headers = {
        "Content-Type": "application/json",
        "x-app-id": APP_ID,
        "x-use-case": USE_CASE,
        "x-risk-level": RISK_LEVEL,
        "x-region": "us-west-2"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"\n📤 Sending request to: {PROXY_URL}/v1/chat/completions")
            print(f"   Model: {payload['model']}")
            print(f"   App ID: {APP_ID}")
            print(f"   Use Case: {USE_CASE}")
            
            response = await client.post(
                f"{PROXY_URL}/v1/chat/completions",
                json=payload,
                headers=headers
            )
            
            print(f"\n📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract response
                message = data['choices'][0]['message']['content']
                print(f"\n💬 AI Response:\n   {message}")
                
                # Extract sustainability metrics from headers
                print(f"\n🌱 Sustainability Metrics:")
                print(f"   Energy: {response.headers.get('X-Energy-Wh', 'N/A')} Wh")
                print(f"   CO₂: {response.headers.get('X-CO2-g', 'N/A')} g")
                print(f"   Tokens: {response.headers.get('X-Tokens-Total', 'N/A')}")
                print(f"   Region: {response.headers.get('X-Region', 'N/A')}")
                
                # Show usage from response
                if 'usage' in data:
                    usage = data['usage']
                    print(f"\n📊 Token Usage:")
                    print(f"   Input: {usage.get('prompt_tokens', 0)}")
                    print(f"   Output: {usage.get('completion_tokens', 0)}")
                    print(f"   Total: {usage.get('total_tokens', 0)}")
                
                print(f"\n✅ Test Passed!")
                return True
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(f"   {response.text}")
                return False
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


async def test_health_checks():
    """Test health endpoints"""
    
    print("\n" + "=" * 60)
    print("Testing Health Endpoints")
    print("=" * 60)
    
    endpoints = [
        ("Proxy", "http://localhost:8001/health"),
        ("Analytics API", "http://localhost:8000/health")
    ]
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in endpoints:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    print(f"✅ {name}: {response.json()}")
                else:
                    print(f"❌ {name}: Status {response.status_code}")
            except Exception as e:
                print(f"❌ {name}: {e}")


async def main():
    """Run all tests"""
    
    print("\n🧪 Eco-Compute SDK & Proxy Test Suite")
    print("=" * 60)
    
    # Check if OpenRouter key is set in .env
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: OPENROUTER_API_KEY not set in .env file")
        print("   Please add your OpenRouter API key to .env")
        print("   Get one at: https://openrouter.ai/keys")
        print("\n   Continuing with tests (may fail without API key)...\n")
    
    # Test health endpoints
    await test_health_checks()
    
    # Test proxy
    print()
    success = await test_proxy_direct()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
