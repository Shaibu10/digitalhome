import sqlite3

conn = sqlite3.connect('digitalhome.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("All tables in database:")
for table in tables:
    print(f"  - {table[0]}")
    cursor.execute(f'PRAGMA table_info([{table[0]}])')
    cols = cursor.fetchall()
    print(f"    Columns: {[col[1] for col in cols]}")
conn.close()
