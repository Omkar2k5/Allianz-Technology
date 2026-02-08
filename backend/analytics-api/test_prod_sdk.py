
import sys
import os
import getpass

# Add SDK to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Eco-Compute-SDK-main/eco_compute")))

from eco_compute import EcoCompute, EcoComputeConfig

def test_prod():
    print("--- Production SDK Verification ---")
    
    # Get user inputs
    email = input("Email: ").strip()
    if not email:
        print("Email is required.")
        return
        
    password = input("Password: ").strip()
    if not password:
        print("Password is required.")
        return
        
    api_key = input("OpenRouter/LLM API Key: ").strip()
    if not api_key:
        print("API Key is required.")
        return

    # Initialize SDK with production endpoint
    print("\nInitializing SDK...")
    prod_url = "https://allianz-technology.onrender.com/api/v1"
    
    config = EcoComputeConfig(
        api_base_url=prod_url,
        debug=True,
        fail_silently=False
    )
    
    with EcoCompute(config) as eco:
        # Login
        print(f"Attempting login to {prod_url}...")
        try:
            if eco.login(email, password):
                print("Login successful!")
            else:
                print("Login failed (invalid credentials?).")
                return
        except Exception as e:
            print(f"Login error: {e}")
            return

        # Make LLM call
        print("\nMaking LLM call...")
        try:
            result = eco.call_llm(
                prompt="Hello from production test script!",
                config={
                    "model": "openai/gpt-4o-mini",  # Using a standard model
                    "api_key": api_key
                }
            )
            
            print("\nLLM Call Successful!")
            print(f"Response: {result['response']['choices'][0]['message']['content']}")
            print("\nMetrics:")
            print(f"- Tokens: {result['metrics']['tokens_total']}")
            print(f"- Energy: {result['metrics']['energy_wh']:.6f} Wh")
            print(f"- CO2: {result['metrics']['co2_g']:.6f} g")
            print(f"- Cost: ${result['metrics']['cost_usd']:.6f}")
            
        except Exception as e:
            print(f"LLM call failed: {e}")
            return

        print("\nFlushing telemetry...")
        # Context manager handles shutdown/flush automatically
        
    print("\nTest completed successfully.")

if __name__ == "__main__":
    test_prod()
