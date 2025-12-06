import sqlite3

conn = sqlite3.connect('instance/digital_home.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(user);")
columns = cursor.fetchall()
print("User table columns:")
for col in columns:
    print(f"  {col}")
conn.close()
