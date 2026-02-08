import sys
import os
from sqlalchemy import create_engine, inspect, text
from app.config import settings

def check_columns():
    print(f"Checking database at: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    columns = [c['name'] for c in inspector.get_columns('genai_requests')]
    print(f"Columns in genai_requests: {columns}")
    
    missing = []
    if 'energy_wh' not in columns:
        missing.append('energy_wh')
    if 'co2_g' not in columns:
        missing.append('co2_g')
        
    if missing:
        print(f"MISSING COLUMNS: {missing}")
        return False
    else:
        print("All columns present.")
        return True

if __name__ == "__main__":
    try:
        if check_columns():
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
