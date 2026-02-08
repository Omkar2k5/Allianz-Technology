import sys
import os
from fastapi.testclient import TestClient
from app.main import app
from app.auth.jwt import create_access_token

def debug_usage_endpoint():
    print("Testing /api/v1/dashboard/usage endpoint...")
    
    # Create test client
    client = TestClient(app)
    
    # Create a fake token for a test user (or existing user if possible)
    # We'll need a user ID. Let's try to get one from DB or just create a dummy one.
    # Ideally, we should use a real user from the DB to avoid "User not found" errors
    # if the endpoint relies on existing usage data.
    
    # For now, let's try to fetch a user first.
    from app.database.connection import get_db
    from app.database.models import User
    
    db = next(get_db())
    user = db.query(User).first()
    
    if not user:
        print("No user found in DB. Cannot test endpoint authenticated.")
        return
        
    print(f"Using user: {user.email} ({user.id})")
    
    # Generate token
    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = client.get("/api/v1/dashboard/usage?days=7", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print("Response Content:", response.text)
            print("Test FAILED with non-200 status.")
        else:
            print("Response JSON:", response.json())
            print("Test PASSED.")
            
    except Exception as e:
        print(f"Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_usage_endpoint()
