"""
Backup and Restore Utilities Module
Handles database backup creation, listing, and restoration
"""
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


class BackupManager:
    """Manages database backups and restoration"""
    
    def __init__(self, db_path, backup_dir):
        """
        Initialize backup manager
        
        Args:
            db_path (str): Path to the main database file
            backup_dir (str): Directory to store backups
        """
        self.db_path = db_path
        self.backup_dir = backup_dir
        
        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, description=''):
        """
        Create a timestamped backup of the database
        
        Args:
            description (str): Optional description of the backup
            
        Returns:
            dict: Backup info with status and details
        """
        try:
            if not os.path.exists(self.db_path):
                return {
                    'success': False,
                    'message': f'Database not found at {self.db_path}'
                }
            
            # Generate backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"digitalhome_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Copy database file
            shutil.copy2(self.db_path, backup_path)
            
            # Get file sizes
            original_size = os.path.getsize(self.db_path)
            backup_size = os.path.getsize(backup_path)
            
            # Verify backup integrity
            if not self._verify_database(backup_path):
                os.remove(backup_path)
                return {
                    'success': False,
                    'message': 'Backup verification failed - corrupted file'
                }
            
            # Create metadata file
            metadata = {
                'filename': backup_filename,
                'timestamp': datetime.now().isoformat(),
                'size_bytes': backup_size,
                'description': description,
                'verified': True
            }
            
            self._save_metadata(backup_filename, metadata)
            
            return {
                'success': True,
                'message': f'Backup created: {backup_filename}',
                'filename': backup_filename,
                'size_bytes': backup_size,
                'size_mb': backup_size / (1024 * 1024),
                'timestamp': datetime.now().isoformat(),
                'description': description
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Backup failed: {str(e)}'
            }
    
    def list_backups(self):
        """
        List all available backups
        
        Returns:
            list: List of backup dictionaries sorted by date (newest first)
        """
        try:
            backups = []
            
            if not os.path.exists(self.backup_dir):
                return backups
            
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('digitalhome_backup_') and filename.endswith('.db'):
                    filepath = os.path.join(self.backup_dir, filename)
                    file_stat = os.stat(filepath)
                    
                    # Extract timestamp from filename
                    timestamp_str = filename.replace('digitalhome_backup_', '').replace('.db', '')
                    
                    # Try to load metadata
                    metadata = self._load_metadata(filename)
                    
                    backup_info = {
                        'filename': filename,
                        'path': filepath,
                        'size_bytes': file_stat.st_size,
                        'size_mb': file_stat.st_size / (1024 * 1024),
                        'created': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        'verified': metadata.get('verified', False),
                        'description': metadata.get('description', ''),
                        'record_count': self._get_record_count(filepath)
                    }
                    backups.append(backup_info)
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created'], reverse=True)
            return backups
        
        except Exception as e:
            print(f'Error listing backups: {str(e)}')
            return []
    
    def restore_backup(self, backup_filename):
        """
        Restore database from a backup
        
        Args:
            backup_filename (str): Name of the backup file to restore
            
        Returns:
            dict: Status of restoration
        """
        try:
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Validate backup file exists
            if not os.path.exists(backup_path):
                return {
                    'success': False,
                    'message': f'Backup file not found: {backup_filename}'
                }
            
            # Verify backup integrity before restoring
            if not self._verify_database(backup_path):
                return {
                    'success': False,
                    'message': 'Backup file is corrupted'
                }
            
            # Create a backup of current database before restoring
            current_backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pre_restore_backup = os.path.join(
                self.backup_dir, 
                f"pre_restore_backup_{current_backup_timestamp}.db"
            )
            shutil.copy2(self.db_path, pre_restore_backup)
            
            # Restore the backup
            shutil.copy2(backup_path, self.db_path)
            
            # Verify restoration
            if not self._verify_database(self.db_path):
                # Restore the pre-restore backup
                shutil.copy2(pre_restore_backup, self.db_path)
                os.remove(pre_restore_backup)
                return {
                    'success': False,
                    'message': 'Restoration failed - database corrupted after restore'
                }
            
            return {
                'success': True,
                'message': f'Database restored from: {backup_filename}',
                'backup_filename': backup_filename,
                'pre_restore_backup': os.path.basename(pre_restore_backup),
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Restoration failed: {str(e)}'
            }
    
    def delete_backup(self, backup_filename):
        """
        Delete a backup file
        
        Args:
            backup_filename (str): Name of the backup file to delete
            
        Returns:
            dict: Status of deletion
        """
        try:
            backup_path = os.path.join(self.backup_dir, backup_filename)
            metadata_path = backup_path.replace('.db', '_metadata.txt')
            
            if not os.path.exists(backup_path):
                return {
                    'success': False,
                    'message': f'Backup file not found: {backup_filename}'
                }
            
            # Delete backup and metadata
            os.remove(backup_path)
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            return {
                'success': True,
                'message': f'Backup deleted: {backup_filename}'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Deletion failed: {str(e)}'
            }
    
    def _verify_database(self, db_path):
        """
        Verify database integrity
        
        Args:
            db_path (str): Path to database file
            
        Returns:
            bool: True if database is valid, False otherwise
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            conn.close()
            
            # Database is valid if it has at least some tables
            return table_count > 0
        except:
            return False
    
    def _get_record_count(self, db_path):
        """
        Get total record count in database
        
        Args:
            db_path (str): Path to database file
            
        Returns:
            int: Total number of records
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            total = 0
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM [{table[0]}]")
                total += cursor.fetchone()[0]
            
            conn.close()
            return total
        except:
            return 0
    
    def _save_metadata(self, backup_filename, metadata):
        """
        Save backup metadata
        
        Args:
            backup_filename (str): Name of backup file
            metadata (dict): Metadata to save
        """
        try:
            metadata_path = os.path.join(
                self.backup_dir,
                backup_filename.replace('.db', '_metadata.txt')
            )
            
            with open(metadata_path, 'w') as f:
                for key, value in metadata.items():
                    f.write(f"{key}: {value}\n")
        except Exception as e:
            print(f'Error saving metadata: {str(e)}')
    
    def _load_metadata(self, backup_filename):
        """
        Load backup metadata
        
        Args:
            backup_filename (str): Name of backup file
            
        Returns:
            dict: Metadata dictionary
        """
        try:
            metadata_path = os.path.join(
                self.backup_dir,
                backup_filename.replace('.db', '_metadata.txt')
            )
            
            metadata = {}
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    for line in f:
                        if ':' in line:
                            key, value = line.strip().split(':', 1)
                            metadata[key.strip()] = value.strip()
            
            return metadata
        except:
            return {}
