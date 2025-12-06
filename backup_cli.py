#!/usr/bin/env python
"""
Command-line Backup Management Utility
Usage: python backup_cli.py [command] [options]
"""
import sys
import os
import argparse
from backup_utils import BackupManager
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(
        description='Digital Home Database Backup Management Tool'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create backup command
    create_parser = subparsers.add_parser('create', help='Create a new backup')
    create_parser.add_argument('-d', '--description', type=str, default='',
                              help='Backup description')
    
    # List backups command
    list_parser = subparsers.add_parser('list', help='List all backups')
    list_parser.add_argument('-v', '--verbose', action='store_true',
                            help='Show detailed information')
    
    # Restore backup command
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('filename', type=str,
                               help='Backup filename to restore')
    
    # Delete backup command
    delete_parser = subparsers.add_parser('delete', help='Delete a backup')
    delete_parser.add_argument('filename', type=str,
                              help='Backup filename to delete')
    delete_parser.add_argument('-f', '--force', action='store_true',
                              help='Skip confirmation prompt')
    
    # Verify backup command
    verify_parser = subparsers.add_parser('verify', help='Verify backup integrity')
    verify_parser.add_argument('filename', type=str,
                              help='Backup filename to verify')
    
    args = parser.parse_args()
    
    # Initialize backup manager
    backup_manager = BackupManager(
        db_path='instance/digitalhome.db',
        backup_dir='backups'
    )
    
    # Execute commands
    if args.command == 'create':
        create_backup(backup_manager, args.description)
    
    elif args.command == 'list':
        list_backups(backup_manager, args.verbose)
    
    elif args.command == 'restore':
        restore_backup(backup_manager, args.filename)
    
    elif args.command == 'delete':
        delete_backup(backup_manager, args.filename, args.force)
    
    elif args.command == 'verify':
        verify_backup(backup_manager, args.filename)
    
    else:
        parser.print_help()


def create_backup(backup_manager, description):
    """Create a new backup"""
    print("\n" + "="*70)
    print("Creating Database Backup")
    print("="*70 + "\n")
    
    result = backup_manager.create_backup(description)
    
    if result['success']:
        print(f"✓ Success: {result['message']}")
        print(f"  Filename: {result['filename']}")
        print(f"  Size: {result['size_mb']:.2f} MB")
        print(f"  Description: {description if description else '(none)'}")
        print(f"  Timestamp: {result['timestamp']}")
    else:
        print(f"✗ Error: {result['message']}")
        sys.exit(1)
    
    print("="*70 + "\n")


def list_backups(backup_manager, verbose):
    """List all backups"""
    print("\n" + "="*70)
    print("Available Backups")
    print("="*70 + "\n")
    
    backups = backup_manager.list_backups()
    
    if not backups:
        print("No backups found.")
    else:
        if not verbose:
            # Simple format
            print(f"{'Filename':<45} {'Size':<12} {'Records':<10} {'Created':<20}")
            print("-" * 87)
            for backup in backups:
                print(f"{backup['filename']:<45} {backup['size_mb']:<10.2f}MB {backup['record_count']:<10} {backup['created'][:16]:<20}")
        else:
            # Detailed format
            for i, backup in enumerate(backups, 1):
                print(f"[{i}] {backup['filename']}")
                print(f"    Size: {backup['size_mb']:.2f} MB ({backup['size_bytes']} bytes)")
                print(f"    Created: {backup['created']}")
                print(f"    Modified: {backup['modified']}")
                print(f"    Records: {backup['record_count']}")
                print(f"    Verified: {'Yes' if backup['verified'] else 'No'}")
                if backup['description']:
                    print(f"    Description: {backup['description']}")
                print()
    
    print("="*70 + "\n")


def restore_backup(backup_manager, filename):
    """Restore from backup"""
    print("\n" + "="*70)
    print("Restore Database from Backup")
    print("="*70 + "\n")
    
    # Check if file exists
    backups = backup_manager.list_backups()
    backup_exists = any(b['filename'] == filename for b in backups)
    
    if not backup_exists:
        print(f"✗ Error: Backup file not found: {filename}")
        sys.exit(1)
    
    # Confirm restoration
    print(f"⚠ Warning: This will replace the current database!")
    print(f"  Backup filename: {filename}")
    confirmation = input("\nType 'YES' to confirm restoration: ").strip()
    
    if confirmation != 'YES':
        print("Restoration cancelled.")
        sys.exit(0)
    
    result = backup_manager.restore_backup(filename)
    
    if result['success']:
        print(f"\n✓ Success: {result['message']}")
        print(f"  Pre-restore backup: {result['pre_restore_backup']}")
        print(f"  Timestamp: {result['timestamp']}")
    else:
        print(f"\n✗ Error: {result['message']}")
        sys.exit(1)
    
    print("="*70 + "\n")


def delete_backup(backup_manager, filename, force):
    """Delete a backup"""
    print("\n" + "="*70)
    print("Delete Backup")
    print("="*70 + "\n")
    
    # Check if file exists
    backups = backup_manager.list_backups()
    backup_exists = any(b['filename'] == filename for b in backups)
    
    if not backup_exists:
        print(f"✗ Error: Backup file not found: {filename}")
        sys.exit(1)
    
    # Confirm deletion
    if not force:
        print(f"⚠ Warning: This will permanently delete the backup!")
        print(f"  Backup filename: {filename}")
        confirmation = input("\nType 'DELETE' to confirm deletion: ").strip()
        
        if confirmation != 'DELETE':
            print("Deletion cancelled.")
            sys.exit(0)
    
    result = backup_manager.delete_backup(filename)
    
    if result['success']:
        print(f"✓ Success: {result['message']}")
    else:
        print(f"✗ Error: {result['message']}")
        sys.exit(1)
    
    print("="*70 + "\n")


def verify_backup(backup_manager, filename):
    """Verify backup integrity"""
    print("\n" + "="*70)
    print("Verify Backup Integrity")
    print("="*70 + "\n")
    
    # Check if file exists
    backups = backup_manager.list_backups()
    backup = next((b for b in backups if b['filename'] == filename), None)
    
    if not backup:
        print(f"✗ Error: Backup file not found: {filename}")
        sys.exit(1)
    
    print(f"Verifying: {filename}")
    print(f"Size: {backup['size_mb']:.2f} MB")
    
    # Verify integrity
    is_valid = backup_manager._verify_database(backup['path'])
    record_count = backup_manager._get_record_count(backup['path'])
    
    if is_valid:
        print(f"\n✓ Backup is valid and intact")
        print(f"  Tables: Valid")
        print(f"  Records: {record_count}")
        print(f"  Verified: Yes")
    else:
        print(f"\n✗ Backup verification failed")
        print(f"  Database may be corrupted")
        sys.exit(1)
    
    print("="*70 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        sys.exit(1)
