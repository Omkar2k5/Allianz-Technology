
import sys
import os
from sqlalchemy import create_engine, inspect, text

# Prod DB URL provided by user
DATABASE_URL = "postgresql://postgres:sFyYEuXHzbcnnDMvJbrVeeocpROjCqAm@ballast.proxy.rlwy.net:54516/railway"

def check_prod_schema():
    print("Connecting to production database...")
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        # Check genai_requests columns
        if inspector.has_table("genai_requests"):
            columns = [col['name'] for col in inspector.get_columns("genai_requests")]
            print(f"\nColumns in 'genai_requests':\n{columns}")
            
            missing = []
            for col in ['created_at', 'computer_name', 'metadata']:
                if col not in columns:
                    missing.append(col)
            
            if missing:
                print(f"\n❌ MISSING COLUMNS: {missing}")
            else:
                print("\n✅ All expected columns present.")
                
            # Check row count
            with engine.connect() as conn:
                count = conn.execute(text("SELECT COUNT(*) FROM genai_requests")).scalar()
                print(f"\nTotal rows in genai_requests: {count}")
                
                # Show last 5
                print("\nLast 5 entries:")
                result = conn.execute(text("SELECT id, timestamp, model_name FROM genai_requests ORDER BY timestamp DESC LIMIT 5"))
                for row in result:
                    print(row)
        else:
            print("\n❌ Table 'genai_requests' does not exist!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    check_prod_schema()
