
import sys
import os
from pathlib import Path
from sqlalchemy import text

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import SessionLocal
from app.database.models import GenAIRequest

def check_entries():
    db = SessionLocal()
    print("\n--- Checking Database Entries ---\n")
    
    # Query last 5 requests
    requests = db.query(GenAIRequest).order_by(GenAIRequest.timestamp.desc()).limit(5).all()
    
    if not requests:
        print("No requests found in database.")
    else:
        print(f"Found {len(requests)} recent requests:\n")
        for req in requests:
            print(f"ID: {req.id}")
            print(f"User ID: {req.user_id}")
            print(f"Model: {req.model_name}")
            print(f"Tokens: {req.tokens_total}")
            print(f"Energy: {req.energy_wh:.6f} Wh")
            print(f"CO2: {req.co2_g:.6f} g")
            print(f"Timestamp: {req.timestamp}")
            print("-" * 30)
            
    db.close()

if __name__ == "__main__":
    check_entries()
