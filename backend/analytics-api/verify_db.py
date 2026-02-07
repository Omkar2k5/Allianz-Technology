
import psycopg2
import sys

try:
    con = psycopg2.connect(
        dbname='ecocompute',
        user='postgres',
        host='localhost',
        password='123456'
    )
    cur = con.cursor()
    
    print("--- Check Tables ---")
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cur.fetchall()
    for t in tables:
        print(f"Table: {t[0]}")
        
    print("\n--- Check Users Columns ---")
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'users'
    """)
    columns = cur.fetchall()
    for c in columns:
        print(f" - {c[0]}: {c[1]}")

    cur.close()
    con.close()

except Exception as e:
    print(f"Error: {e}")
