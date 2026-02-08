"""
Example usage of the Eco-Compute SDK.
This script demonstrates the main features of the SDK.
"""

import sys
import os
import time

# Ensure we can import the package even if running from local checkout
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from eco_compute import (
    EcoCompute, 
    EcoComputeConfig, 
    estimate_energy, 
    estimate_carbon, 
    estimate_cost,
    get_cleanest_regions,
    compare_regions
)

def main():
    print("=== Eco-Compute SDK Demo ===\n")

    # 1. Basic Estimation Usage (No API Key Required)
    print("--- 1. Standalone Estimation ---")
    
    # Estimate for a hypothetical GPT-4 request
    tokens = 1500
    model = "gpt-4"
    energy = estimate_energy(tokens, model)
    print(f"Energy for {tokens} tokens with {model}: {energy:.6f} Wh")
    
    # Estimate carbon impact in different regions
    print("\nCarbon impact by region:")
    comparisons = compare_regions(energy)
    for region, co2 in comparisons.items():
        print(f"  - {region.ljust(15)}: {co2:.6f} g CO2")
        
    # Get cleanest regions
    top_clean = get_cleanest_regions(3)
    print(f"\nTop 3 cleanest regions: {[r[0] for r in top_clean]}")

    # 2. SDK Client Usage
    print("\n--- 2. SDK Client Usage ---")
    
    # Initialize SDK
    config = EcoComputeConfig(
        telemetry_enabled=False,  # Disable for demo
        region="us-west-2",       # AWS Oregon
        debug=True
    )
    
    with EcoCompute(config) as eco:
        # Simulate an LLM call (using estimate_only to avoid API keys in demo)
        print("Simulating LLM request...")
        
        # Hypothetical request: "Write a story about a green AI"
        input_tokens = 50
        output_tokens = 500
        model = "claude-3-opus"
        
        result = eco.estimate_only(input_tokens, output_tokens, model)
        
        print(f"\nRequest: {input_tokens} in / {output_tokens} out ({model})")
        print(f"Est. Cost:   ${result['cost_usd']:.6f}")
        print(f"Est. Carbon: {result['co2_g']:.6f} g CO2")
        print(f"Est. Energy: {result['energy_wh']:.6f} Wh")
        
        # In a real app, you would use:
        # response = eco.call_llm("your prompt", {"model": "gpt-4", "api_key": "..."})

    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    main()
