
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in environment variables")
    exit(1)

# Parse DATABASE_URL
result = urlparse(DATABASE_URL)
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port

# Connect to default 'postgres' database to create new db
try:
    con = psycopg2.connect(
        dbname='postgres',
        user=username,
        host=hostname,
        password=password,
        port=port
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    
    # Check if database exists
    cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{database}'")
    exists = cur.fetchone()
    
    if not exists:
        print(f"Creating database '{database}'...")
        cur.execute(f'CREATE DATABASE {database}')
    else:
        print(f"Database '{database}' already exists.")
        
    cur.close()
    con.close()
    
except Exception as e:
    print(f"Error creating database: {e}")
    exit(1)

# Connect to new database and run schema
try:
    print(f"Connecting to '{database}'...")
    con = psycopg2.connect(
        dbname=database,
        user=username,
        host=hostname,
        password=password,
        port=port
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
