
import sqlite3
import os
import pandas as pd

def get_table_data(db_path, table_name):
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return None

    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    except Exception as e:
        print(f"❌ Error reading table {table_name} from {db_path}: {e}")
        return None

def main():
    output_file = "ecocompute_data.xlsx"
    
    # 1. Define sources
    agent_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../agent/agent.db"))
    backend_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "ecocompute.db"))
    
    print(f"Reading data...")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        has_data = False
        
        # Agent DB Tables
        for table in ["ai_requests", "user_session"]:
            df = get_table_data(agent_db_path, table)
            if df is not None:
                sheet_name = f"Agent_{table}"[:31] # Excel sheet limit
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"✅ Added sheet: {sheet_name} ({len(df)} rows)")
                has_data = True
                
        # Backend DB Tables
        for table in ["genai_requests", "agents", "users", "teams", "apps"]:
            df = get_table_data(backend_db_path, table)
            if df is not None:
                sheet_name = f"Backend_{table}"[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"✅ Added sheet: {sheet_name} ({len(df)} rows)")
                has_data = True
                
    if has_data:
        print(f"\n🎉 Data exported successfully to: {os.path.abspath(output_file)}")
    else:
        print("\n⚠️  No data found to export.")

if __name__ == "__main__":
    main()
