"""
Database Backup Script - Digital Home E-Commerce
Creates a backup of the SQLite database with timestamp
"""
import shutil
import os
from datetime import datetime
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("\n" + "="*80)
print("DATABASE BACKUP - DIGITAL HOME E-COMMERCE")
print("="*80 + "\n")

# Database file path (using digitalhome.db which is the actual database)
db_path = 'e:\\python_projects\\digialhome\\instance\\digitalhome.db'
backup_dir = 'e:\\python_projects\\digialhome\\backups'

# Create backups directory if it doesn't exist
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)
    print(f"[OK] Created backup directory: {backup_dir}\n")

# Check if database exists
if not os.path.exists(db_path):
    print(f"[ERROR] Database not found at: {db_path}")
    sys.exit(1)

print(f"Source database: {db_path}")
print(f"Database size: {os.path.getsize(db_path) / (1024*1024):.2f} MB\n")

# Create timestamped backup filename
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_filename = f"digitalhome_backup_{timestamp}.db"
backup_path = os.path.join(backup_dir, backup_filename)

try:
    # Copy database file
    print(f"[IN PROGRESS] Creating backup: {backup_filename}...")
    shutil.copy2(db_path, backup_path)
    
    backup_size = os.path.getsize(backup_path) / (1024*1024)
    print(f"[OK] Backup created successfully")
    print(f"     Location: {backup_path}")
    print(f"     Size: {backup_size:.2f} MB")
    
    # Also create a manifest file
    manifest_path = os.path.join(backup_dir, f"backup_manifest_{timestamp}.txt")
    with open(manifest_path, 'w') as f:
        f.write(f"Digital Home E-Commerce Database Backup\n")
        f.write(f"{'='*70}\n\n")
        f.write(f"Backup Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Backup File: {backup_filename}\n")
        f.write(f"Backup Path: {backup_path}\n")
        f.write(f"Backup Size: {backup_size:.2f} MB\n")
        f.write(f"Source Database: {db_path}\n")
        f.write(f"Original Size: {os.path.getsize(db_path) / (1024*1024):.2f} MB\n\n")
        f.write(f"Tables Included:\n")
        f.write(f"  - user (User accounts)\n")
        f.write(f"  - product (Product catalog)\n")
        f.write(f"  - category (Product categories)\n")
        f.write(f"  - order (Customer orders)\n")
        f.write(f"  - order_item (Items in orders)\n")
        f.write(f"  - cart_item (Shopping cart items)\n")
        f.write(f"  - system_settings (Configuration)\n")
        f.write(f"  - review (Product reviews)\n")
        f.write(f"  - and more...\n\n")
        f.write(f"Restore Instructions:\n")
        f.write(f"  1. Stop the Flask application\n")
        f.write(f"  2. Copy this backup file to: instance/app.db\n")
        f.write(f"  3. Restart the Flask application\n\n")
        f.write(f"Backup Status: SUCCESSFUL\n")
    
    print(f"\n[OK] Manifest file created: backup_manifest_{timestamp}.txt\n")
    
    # List recent backups
    print("Recent backups:")
    backups = sorted([f for f in os.listdir(backup_dir) if f.startswith('digitalhome_backup_') and f.endswith('.db')], reverse=True)[:5]
    for i, backup_file in enumerate(backups, 1):
        file_path = os.path.join(backup_dir, backup_file)
        file_size = os.path.getsize(file_path) / (1024*1024)
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        print(f"  {i}. {backup_file} ({file_size:.2f} MB) - {file_time}")
    
    print("\n" + "="*80)
    print("BACKUP COMPLETED SUCCESSFULLY ✓")
    print("="*80 + "\n")
    
except Exception as e:
    print(f"[ERROR] Backup failed: {str(e)}")
    sys.exit(1)
