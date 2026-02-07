
import psycopg2

DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"
DB_PASSWORD = "omkar9211" 
DB_NAME = "ecocompute"

def find_null_columns():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # Get all column names first
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'genai_requests'")
        columns = [row[0] for row in cursor.fetchall()]

        print("Checking for NON-NULL counts in genai_requests:")
        for col in columns:
            cursor.execute(f"SELECT COUNT({col}) FROM genai_requests WHERE {col} IS NOT NULL")
            count = cursor.fetchone()[0]
            if count == 0:
                print(f"[EMPTY] {col}")
            else:
                print(f"[USED]  {col} ({count} non-null values)")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_null_columns()
