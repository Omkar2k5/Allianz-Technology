"""
Live inference example using the Eco-Compute SDK.

This script makes a REAL API call to OpenRouter.
You must set the OPENROUTER_API_KEY environment variable.

Usage:
    export OPENROUTER_API_KEY=sk-or-your-key
    python -m eco_compute.examples.live_inference
"""

import os
import sys
import time

# Ensure we can import the package even if running from local checkout
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from eco_compute import EcoCompute, EcoComputeConfig

def main():
    # ------------------------------------------------------------------
    # OPTION 1: Set your API key here (Easiest for testing)
    # ------------------------------------------------------------------
    manual_api_key = "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"

    # ------------------------------------------------------------------
    # OPTION 2: Load from environment variable (Best for production)
    # ------------------------------------------------------------------
    env_api_key = os.environ.get("OPENROUTER_API_KEY")
    
    # Use manual key if set and not default, otherwise use environment
    if manual_api_key and manual_api_key != "PASTE_YOUR_OPENROUTER_KEY_HERE":
        api_key = manual_api_key
    else:
        api_key = env_api_key
    
    if not api_key:
        print("\n❌ Error: API Key not found.")
        print("Please either:")
        print("1. Edit this script and paste your key in 'manual_api_key'")
        print("2. Set OPENROUTER_API_KEY environment variable")
        return

    print("=== Eco-Compute Live Inference Demo ===\n")

    # 1. Configure the SDK
    config = EcoComputeConfig(
        telemetry_enabled=True,
        telemetry_endpoint=None,  # No backend for demo, just local tracking
        region="us-east-1",       # AWS N. Virginia
        debug=True               # Show debug logs
    )

    print("Initializing SDK...")
    
    with EcoCompute(config) as eco:
        # 2. Define the request
        model = "mistralai/mistral-7b-instruct"  # Cheap, fast, good for demos
        prompt = "Explain the concept of 'Carbon Intensity' in 2 sentences."
        
        print(f"\nSending request to {model} via OpenRouter...")
        print(f"Prompt: \"{prompt}\"")
        
        try:
            start_time = time.time()
            
            # 3. Make the call
            result = eco.call_llm(
                prompt=prompt,
                config={
                    "model": model,
                    "api_key": api_key,
                    "use_case": "demo_script",
                    "app_id": "live-inference-demo"
                }
            )
            
            duration = time.time() - start_time
            print(f"\n✅ Request successful ({duration:.2f}s)")
            
            # 4. Show the response
            content = result["response"]["choices"][0]["message"]["content"]
            print(f"\n🤖 LLM Response:\n{'-'*20}\n{content}\n{'-'*20}")
            
            # 5. Show Metrics
            print("\n📊 Sustainability Metrics:")
            for key, value in result["metrics"].items():
                print(f"{key}: {value}")
            
        except Exception as e:
            print(f"\n❌ Error making API call: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
