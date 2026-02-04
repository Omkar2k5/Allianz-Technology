"""
Simple database setup using psycopg2
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database connection parameters
DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"
DB_PASSWORD = "omkar9211"
DB_NAME = "ecocompute"

print("🚀 Eco-Compute Database Setup\n")

# Step 1: Drop and create database
print("Step 1: Creating database...")
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Drop if exists
    cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
    print(f"   Dropped existing database (if any)")
    
    # Create new
    cursor.execute(f"CREATE DATABASE {DB_NAME}")
    print(f"✅ Database '{DB_NAME}' created\n")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}\n")
    print("Please ensure PostgreSQL is running and credentials are correct.")
    print(f"   Host: {DB_HOST}:{DB_PORT}")
    print(f"   User: {DB_USER}")
    print(f"   Password: {'*' * len(DB_PASSWORD)}")
    exit(1)

# Step 2: Run schema
print("Step 2: Creating tables...")
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()
    
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

# Step 3: Run seed data
print("Step 3: Loading seed data...")
try:
    with open('seed.sql', 'r', encoding='utf-8') as f:
        seed_sql = f.read()
    
    cursor.execute(seed_sql)
    conn.commit()
    print("✅ Seed data loaded\n")
    
except Exception as e:
    print(f"❌ Seed error: {e}\n")
    conn.rollback()

# Step 4: Verify
print("Step 4: Verifying setup...")
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
    
    cursor.execute("SELECT email, role FROM users")
    users = cursor.fetchall()
    print(f"\n📋 Test Users:")
    for email, role in users:
        print(f"   {email} ({role})")
    
except Exception as e:
    print(f"⚠️  Verification warning: {e}")

cursor.close()
conn.close()

print("\n" + "="*60)
print("✅ Database setup complete!")
print("="*60)
print("\n🔑 Test Credentials:")
print("   Email: admin@allianz.com")
print("   Password: demo123")
print("\n🚀 Next: Start the Analytics API")
print("   cd ../analytics-api")
print("   python -m uvicorn app.main:app --reload --port 8000")
