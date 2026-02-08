
import sys
import os
import time
import logging

# Add SDK to path
# The package is located at Eco-Compute-SDK-main/eco_compute/eco_compute
# So we need to add Eco-Compute-SDK-main/eco_compute to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Eco-Compute-SDK-main/eco_compute")))

from eco_compute import EcoCompute, EcoComputeConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_sdk")

def verify_sdk():
    print("Initializing SDK...")
    config = EcoComputeConfig(
        api_base_url="http://localhost:8000/api/v1",
        debug=True,
        fail_silently=False
    )
    eco = EcoCompute(config)
    
    print("Attempting login...")
    try:
        eco.login("test_sdk@example.com", "password123")
        print("Login successful!")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    print("Making LLM call (simulated)...")
    # We mock the LLM call or use a real one if API key provided, but here we just want to test telemetry.
    # The SDK wraps the call. If we don't have a real API key, it might fail the LLM call but still log telemetry?
    # No, it logs after success.
    # So I need to mock the `_make_openrouter_request` or use a dummy key and expect 401 but maybe telemetry is still sent?
    # Actually, `call_llm` raises exception if request fails.
    
    # Let's mock the request method in the instance
    class MockResponse:
        def json(self):
            return {
                "id": "mock-response-id",
                "model": "openai/gpt-4o-mini",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "total_tokens": 30
                },
                "choices": [{"message": {"content": "Mock response"}}]
            }
        
        def raise_for_status(self):
            pass
            
    eco._make_openrouter_request = lambda messages, config: MockResponse()
    
    try:
        result = eco.call_llm(
            prompt="Hello",
            config={
                "model": "openai/gpt-4o-mini",
                "api_key": "dummy"
            }
        )
        print("LLM call successful.")
        print(f"Energy: {result['estimation']['energy_wh']} Wh")
    except Exception as e:
        print(f"LLM call failed: {e}")
        return

    print("Waiting for telemetry to flush...")
    eco.flush_telemetry()
    eco.shutdown() # Ensure background threads finish and send remaining batch
    print("Telemetry flushed and SDK shutdown.")

if __name__ == "__main__":
    verify_sdk()
