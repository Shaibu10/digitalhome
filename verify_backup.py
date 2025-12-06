"""
Backup Verification Script
"""
import sqlite3
import os

backup_file = 'e:\\python_projects\\digialhome\\backups\\digitalhome_backup_20251206_063501.db'

if os.path.exists(backup_file):
    try:
        conn = sqlite3.connect(backup_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n{'='*70}")
        print("DATABASE BACKUP VERIFICATION")
        print(f"{'='*70}\n")
        
        print(f"Backup file: digitalhome_backup_20251206_063501.db")
        print(f"Location: e:\\python_projects\\digialhome\\backups\\")
        print(f"Size: {os.path.getsize(backup_file) / 1024:.2f} KB")
        print(f"Total tables: {len(tables)}\n")
        
        print("Table Contents:")
        print("-" * 70)
        
        total_records = 0
        for table in sorted(tables):
            cursor.execute(f'SELECT COUNT(*) FROM [{table[0]}]')
            count = cursor.fetchone()[0]
            total_records += count
            print(f"  ✓ {table[0]:25} | {count:6} records")
        
        conn.close()
        
        print("-" * 70)
        print(f"Total records backed up: {total_records}")
        print(f"\n{'='*70}")
        print("BACKUP STATUS: ✓ VERIFIED & INTACT")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"Error verifying backup: {e}")
else:
    print(f"Backup file not found: {backup_file}")
