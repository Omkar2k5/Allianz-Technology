"""
Create all database tables using SQLAlchemy models
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import engine, Base
from app.database.models import (
    User, Team, App, Agent, GenAIRequest, Model
)

def create_tables():
    """Create all tables defined in models"""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\nCreated tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_tables()
