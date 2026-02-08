
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')
print(f"Checking database: {DATABASE_URL}")

try:
    con = psycopg2.connect(DATABASE_URL)
    cur = con.cursor()
    
    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'genai_requests';")
    columns = cur.fetchall()
    
    print("\nColumns in 'genai_requests':")
    found_metadata = False
    for col in columns:
        print(f"- {col[0]} ({col[1]})")
        if col[0] == 'meta_data':
            found_metadata = True
            
    if found_metadata:
        print("\n✅ 'meta_data' column FOUND.")
    else:
        print("\n❌ 'meta_data' column NOT FOUND.")

    cur.close()
    con.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
