
import requests
import json
import time

def debug_prod():
    print("--- Debugging Production Metrics Endpoint ---")
    
    email = input("Email: ").strip()
    if not email:
        print("Email is required.")
        return
        
    password = input("Password: ").strip()
    if not password:
        print("Password is required.")
        return
    
    base_url = "https://allianz-technology.onrender.com/api/v1"
    
    # 1. Login
    print(f"\n1. Logging in to {base_url}...")
    try:
        resp = requests.post(f"{base_url}/auth/login", json={"email": email, "password": password})
        if resp.status_code != 200:
            print(f"Status: {resp.status_code}")
            print(f"Login failed: {resp.text}")
            return
            
        data = resp.json()
        token = data.get("access_token")
        user_id = data.get("user", {}).get("id")
        print(f"Token obtained. User ID: {user_id}")
        
    except Exception as e:
        print(f"Login request error: {e}")
        return

    if not token:
        print("No access token found in login response.")
        return

    # 2. Send Metrics
    print("\n2. Sending dummy metrics payload...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    record = {
        "id": f"debug-{int(time.time())}",
        "app_id": "debug-script",
        "user_id": user_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "request_hash": "debug-hash",
        "model_name": "debug-model",
        "provider": "debug-provider",
        "tokens_input": 10,
        "tokens_output": 10,
        "tokens_total": 20,
        "energy_wh": 0.001,
        "co2_g": 0.001,
        "latency_ms": 100,
        "computer_name": "debug-pc",
        "policy_applied": False,
        "policy_action": "allowed",
        "cost_usd": 0.0001,
        "region": "debug-region",
        "carbon_intensity": 0.5,
        "use_case": "debug",
        "risk_level": "low",
        "meta_data": {"source": "debug_prod_metrics.py"}
    }
    
    payload = {
        "records": [record],
        "sdk_version": "0.1.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    
    try:
        url = f"{base_url}/metrics"
        print(f"POST {url}")
        resp = requests.post(url, headers=headers, json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        
    except Exception as e:
        print(f"Metrics request error: {e}")

if __name__ == "__main__":
    debug_prod()
