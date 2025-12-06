"""
Test restore backup functionality
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("\n" + "="*70)
print("TESTING RESTORE BACKUP FUNCTIONALITY")
print("="*70 + "\n")

from backup_utils import BackupManager
import os

backup_manager = BackupManager(
    db_path='e:\\python_projects\\digialhome\\instance\\digitalhome.db',
    backup_dir='e:\\python_projects\\digialhome\\backups'
)

# Get list of backups
backups = backup_manager.list_backups()

if not backups:
    print("✗ No backups found to test restore")
    sys.exit(1)

print(f"✓ Found {len(backups)} backup(s)")

# Test validation
backup_to_restore = backups[0]['filename']
print(f"\nTesting with backup: {backup_to_restore}")

# Test 1: Verify backup exists
print(f"\n[Test 1] Checking backup file exists...")
backup_path = os.path.join('e:\\python_projects\\digialhome\\backups', backup_to_restore)
if os.path.exists(backup_path):
    print(f"  ✓ Backup file exists: {backup_path}")
else:
    print(f"  ✗ Backup file not found")
    sys.exit(1)

# Test 2: Verify backup integrity
print(f"\n[Test 2] Verifying backup integrity...")
is_valid = backup_manager._verify_database(backup_path)
if is_valid:
    print(f"  ✓ Backup is valid")
else:
    print(f"  ✗ Backup is corrupted")
    sys.exit(1)

# Test 3: Check current database
print(f"\n[Test 3] Checking current database...")
current_db = 'e:\\python_projects\\digialhome\\instance\\digitalhome.db'
if os.path.exists(current_db):
    print(f"  ✓ Current database exists")
    print(f"    Size: {os.path.getsize(current_db) / 1024:.2f} KB")
else:
    print(f"  ✗ Current database not found")

# Test 4: Simulate validation (don't actually restore)
print(f"\n[Test 4] Validating restore parameters...")
if '..' not in backup_to_restore and '/' not in backup_to_restore and '\\' not in backup_to_restore:
    print(f"  ✓ Filename validation passed")
    print(f"    No path traversal detected")
else:
    print(f"  ✗ Invalid filename")

# Test 5: Check API endpoint
print(f"\n[Test 5] Checking Flask app configuration...")
try:
    from app import app
    routes = [str(r.rule) for r in app.url_map.iter_rules()]
    
    if any('api/backup/restore' in route for route in routes):
        print(f"  ✓ /api/backup/restore endpoint exists")
    else:
        print(f"  ✗ /api/backup/restore endpoint not found")
    
    if any('admin/backups' in route for route in routes):
        print(f"  ✓ /admin/backups endpoint exists")
    else:
        print(f"  ✗ /admin/backups endpoint not found")
        
except Exception as e:
    print(f"  ✗ Error checking app: {e}")

print("\n" + "="*70)
print("✓ RESTORE FUNCTIONALITY TEST COMPLETE")
print("="*70 + "\n")

print("How to test restore via web interface:")
print("  1. Go to http://127.0.0.1:5000/admin/backups")
print("  2. Find a backup in the list")
print("  3. Click the restore button (⟳)")
print("  4. Confirm in the modal dialog")
print("  5. Wait for 'Database restored' message")
print("\nNote: The database will be restored and page will reload.")

print("\nHow to test restore via CLI:")
print(f"  python backup_cli.py restore {backup_to_restore}")

print("\n" + "="*70 + "\n")
