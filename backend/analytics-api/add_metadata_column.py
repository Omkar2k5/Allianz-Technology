
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("Error: DATABASE_URL not found in environment variables")
    exit(1)

print(f"Connecting to database...")

try:
    con = psycopg2.connect(DATABASE_URL)
    cur = con.cursor()
    
    # Add column if it doesn't exist
    print("Adding 'meta_data' column to 'genai_requests' table...")
    cur.execute("ALTER TABLE genai_requests ADD COLUMN IF NOT EXISTS meta_data JSONB;")
    
    con.commit()
    print("✅ Column 'meta_data' added successfully!")
    
    cur.close()
    con.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
