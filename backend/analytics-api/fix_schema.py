
import sys
import os
from sqlalchemy import text

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import SessionLocal


def fix_schema():
    db = SessionLocal()

from sqlalchemy import inspect

def fix_schema():
    db = SessionLocal()
    print("Inspecting schema...")
    try:
        inspector = inspect(db.bind)
        columns = [col['name'] for col in inspector.get_columns('genai_requests')]
        print(f"Current columns: {columns}")
        
        if 'created_at' not in columns:
            print("Adding created_at column...")
            sql = text("ALTER TABLE genai_requests ADD COLUMN created_at TIMESTAMPTZ DEFAULT NOW();")
            db.execute(sql)
            db.commit()
            print("Column created_at added.")
            
        if 'computer_name' not in columns:
            print("Adding computer_name column...")
            sql = text("ALTER TABLE genai_requests ADD COLUMN computer_name VARCHAR(255);")
            db.execute(sql)
            db.commit()
            print("Column computer_name added.")
        else:
            print("Column created_at already exists.")
            
        # Verify again
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'genai_requests';"))
        columns = [row[0] for row in result.fetchall()]
        print(f"Columns after check: {columns}")
        
    except Exception as e:
        print(f"Error fixing schema: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_schema()
