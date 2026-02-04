"""
Database setup script - Creates tables and loads seed data
"""

import psycopg2
from psycopg2 import sql
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "omkar9211")
DB_NAME = os.getenv("POSTGRES_DB", "ecocompute")

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to postgres database to create ecocompute
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"✅ Database '{DB_NAME}' created successfully")
        else:
            print(f"ℹ️  Database '{DB_NAME}' already exists")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def run_sql_file(filepath, conn):
    """Execute SQL file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        cursor = conn.cursor()
        cursor.execute(sql_content)
        conn.commit()
        cursor.close()
        
        print(f"✅ Executed: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error executing {filepath}: {e}")
        conn.rollback()
        return False

def setup_database():
    """Main setup function"""
    print("🚀 Starting Eco-Compute Database Setup...\n")
    
    # Step 1: Create database
    print("Step 1: Creating database...")
    if not create_database():
        return False
    
    # Step 2: Connect to ecocompute database
    print("\nStep 2: Connecting to database...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # Step 3: Run schema
    print("\nStep 3: Creating tables...")
    schema_file = Path(__file__).parent / "schema.sql"
    if not run_sql_file(schema_file, conn):
        conn.close()
        return False
    
    # Step 4: Run seed data
    print("\nStep 4: Loading seed data...")
    seed_file = Path(__file__).parent / "seed.sql"
    if not run_sql_file(seed_file, conn):
        conn.close()
        return False
    
    # Step 5: Run auth migration
    print("\nStep 5: Running auth migration...")
    migration_file = Path(__file__).parent / "migrations" / "001_add_auth.sql"
    if not run_sql_file(migration_file, conn):
        conn.close()
        return False
    
    # Step 6: Verify setup
    print("\nStep 6: Verifying setup...")
    try:
        cursor = conn.cursor()
        
        # Count tables
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]
        print(f"✅ Tables created: {table_count}")
        
        # Count users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✅ Test users: {user_count}")
        
        # Count requests
        cursor.execute("SELECT COUNT(*) FROM genai_requests")
        request_count = cursor.fetchone()[0]
        print(f"✅ Sample requests: {request_count}")
        
        cursor.close()
    except Exception as e:
        print(f"⚠️  Verification warning: {e}")
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ Database setup completed successfully!")
    print("="*60)
    print("\n📝 Test Credentials:")
    print("   Email: admin@allianz.com")
    print("   Password: demo123")
    print("\n🔗 Connection String:")
    print(f"   postgresql://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    print("\n🚀 Next Steps:")
    print("   1. Start Analytics API: cd backend/analytics-api && python -m uvicorn app.main:app --reload")
    print("   2. Test auth: curl -X POST http://localhost:8000/api/v1/auth/login \\")
    print("                      -H 'Content-Type: application/json' \\")
    print("                      -d '{\"email\":\"admin@allianz.com\",\"password\":\"demo123\"}'")
    
    return True

if __name__ == "__main__":
    success = setup_database()
    exit(0 if success else 1)
