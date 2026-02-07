
import psycopg2

DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"
DB_PASSWORD = "omkar9211" 
DB_NAME = "ecocompute"

def drop_unused_columns():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # Columns to drop based on previous check
        columns_to_drop = [
            "app_id",
            "model_id",
            "agent_id",
            "carbon_intensity", 
            "cost_usd",
            "process_name",
            "use_case",
            "risk_level",
            "policy_action"
        ]

        print(f"Dropping columns: {', '.join(columns_to_drop)}")
        
        # Construct ALTER TABLE statement
        actions = [f"DROP COLUMN IF EXISTS {col}" for col in columns_to_drop]
        sql = f"ALTER TABLE genai_requests {', '.join(actions)};"
        
        print(f"Executing: {sql}")
        cursor.execute(sql)
        conn.commit()
        
        print("✅ Unused columns dropped successfully.")
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    drop_unused_columns()
