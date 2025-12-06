import sqlite3

# Check both database files
for db_file in ['instance/app.db', 'instance/digitalhome.db']:
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        print(f'\n{db_file}:')
        if tables:
            for table in tables:
                print(f'  ✓ {table}')
        else:
            print('  (empty)')
        conn.close()
    except Exception as e:
        print(f'\n{db_file}: Error - {e}')
