
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

# Connect to default 'postgres' database to create new db
try:
    con = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        host='localhost',
        password='123456'
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    
    # Check if database exists
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'ecocompute'")
    exists = cur.fetchone()
    
    if not exists:
        print("Creating database 'ecocompute'...")
        cur.execute('CREATE DATABASE ecocompute')
    else:
        print("Database 'ecocompute' already exists.")
        
    cur.close()
    con.close()
    
except Exception as e:
    print(f"Error creating database: {e}")
    exit(1)

# Connect to new database and run schema
try:
    print("Connecting to 'ecocompute'...")
    con = psycopg2.connect(
        dbname='ecocompute',
        user='postgres',
        host='localhost',
        password='123456'
    )
    cur = con.cursor()
    
    # Read schema file
    # backend/analytics-api/init_db.py -> backend/database/schema.sql
    schema_path = os.path.join(os.path.dirname(__file__), '../database/schema.sql')
    print(f"Applying schema from {schema_path}...")
    
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
        
    cur.execute(schema_sql)
    con.commit()
    print("Schema applied successfully!")
    
    cur.close()
    con.close()

except Exception as e:
    print(f"Error applying schema: {e}")
    exit(1)
