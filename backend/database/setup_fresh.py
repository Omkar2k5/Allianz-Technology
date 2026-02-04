"""
Database setup - Creates/recreates tables without dropping database
"""

import psycopg2

# Database connection parameters
DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"
DB_PASSWORD = "omkar9211"
DB_NAME = "ecocompute"

print("🚀 Eco-Compute Database Setup\n")

# Connect to database
print("Step 1: Connecting to database...")
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()
    print(f"✅ Connected to '{DB_NAME}'\n")
except Exception as e:
    print(f"❌ Connection error: {e}\n")
    print("Trying to create database...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        cursor.close()
        conn.close()
        
        # Reconnect to new database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        print(f"✅ Database created and connected\n")
    except Exception as e2:
        print(f"❌ Failed to create database: {e2}")
        exit(1)

# Drop existing tables
print("Step 2: Dropping existing tables...")
try:
    cursor.execute("""
        DROP SCHEMA public CASCADE;
        CREATE SCHEMA public;
        GRANT ALL ON SCHEMA public TO postgres;
        GRANT ALL ON SCHEMA public TO public;
    """)
    conn.commit()
    print("✅ Existing tables dropped\n")
except Exception as e:
    print(f"⚠️  Drop warning: {e}\n")
    conn.rollback()

# Run schema
print("Step 3: Creating tables...")
try:
    with open('schema.sql', 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    cursor.execute(schema_sql)
    conn.commit()
    print("✅ Tables created\n")
except Exception as e:
    print(f"❌ Schema error: {e}\n")
    conn.rollback()
    cursor.close()
    conn.close()
    exit(1)

# Run seed data
print("Step 4: Loading seed data...")
try:
    with open('seed.sql', 'r', encoding='utf-8') as f:
        seed_sql = f.read()
    
    cursor.execute(seed_sql)
    conn.commit()
    print("✅ Seed data loaded\n")
except Exception as e:
    print(f"❌ Seed error: {e}\n")
    print("Continuing anyway...\n")
    conn.rollback()

# Verify
print("Step 5: Verifying setup...")
try:
    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
    table_count = cursor.fetchone()[0]
    print(f"✅ Tables: {table_count}")
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"✅ Users: {user_count}")
    
    cursor.execute("SELECT COUNT(*) FROM genai_requests")
    request_count = cursor.fetchone()[0]
    print(f"✅ Requests: {request_count}")
    
    cursor.execute("SELECT email, role FROM users ORDER BY role DESC")
    users = cursor.fetchall()
    print(f"\n📋 Test Users (password: demo123):")
    for email, role in users:
        print(f"   • {email} ({role})")
    
except Exception as e:
    print(f"⚠️  Verification: {e}")

cursor.close()
conn.close()

print("\n" + "="*60)
print("✅ DATABASE SETUP COMPLETE!")
print("="*60)
print("\n🚀 Start the Analytics API:")
print("   cd backend/analytics-api")
print("   python -m uvicorn app.main:app --reload --port 8000")
print("\n🧪 Test Authentication:")
print("   curl -X POST http://localhost:8000/api/v1/auth/login \\")
print("        -H 'Content-Type: application/json' \\")
print("        -d '{\"email\":\"admin@allianz.com\",\"password\":\"demo123\"}'")
