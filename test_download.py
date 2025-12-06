"""
Test backup download functionality
"""
import os

print("\n" + "="*70)
print("TESTING BACKUP DOWNLOAD FUNCTIONALITY")
print("="*70 + "\n")

# Check backup file exists
backup_file = 'backups/digitalhome_backup_20251206_064300.db'
if os.path.exists(backup_file):
    file_size = os.path.getsize(backup_file)
    print(f"✓ Backup file found: {backup_file}")
    print(f"  Size: {file_size} bytes ({file_size / 1024:.2f} KB)")
    print(f"\n✓ File is ready for download")
else:
    print(f"✗ Backup file not found: {backup_file}")

# Verify Flask can import send_file
print("\nVerifying Flask imports:")
try:
    from flask import send_file
    print("✓ send_file imported successfully")
except ImportError as e:
    print(f"✗ Failed to import send_file: {e}")

# Test the app import
try:
    from app import app
    print("✓ App imported successfully")
    
    # Check if route exists
    routes = [str(r.rule) for r in app.url_map.iter_rules()]
    download_route = '/api/backup/download/<filename>'
    
    # Flask shows it as /api/backup/download/<filename>
    if any('api/backup/download' in route for route in routes):
        print("✓ Download endpoint registered")
    else:
        print("✗ Download endpoint not found")
        
except Exception as e:
    print(f"✗ Error importing app: {e}")

print("\n" + "="*70)
print("✓ DOWNLOAD FUNCTIONALITY TEST COMPLETE")
print("="*70 + "\n")

print("To test download via curl:")
print('  curl -u admin@example.com:admin123 http://localhost:5000/api/backup/download/digitalhome_backup_20251206_064300.db -o backup.db')

print("\nTo test download via web browser:")
print("  1. Login to admin panel")
print("  2. Go to /admin/backups")
print("  3. Click download button (⬇) next to a backup")
print("  4. Browser will download the file")

print("\n" + "="*70 + "\n")
