"""
File renaming logic with backup support.
"""

import os
import shutil
from datetime import datetime
from utils.logger import setup_logger
from utils.validators import sanitize_filename


logger = setup_logger(__name__)


class FileRenamer:
    """Handles PDF file renaming with backup support."""
    
    def __init__(self, backup_enabled=True, backup_folder="backups"):
        self.backup_enabled = backup_enabled
        self.backup_folder = backup_folder
    
    def rename_file(self, old_path, new_name, create_backup=None):
        try:
            should_backup = create_backup if create_backup is not None else self.backup_enabled
            
            if not os.path.exists(old_path):
                return False, old_path, f"File not found: {old_path}"
            
            new_name = sanitize_filename(new_name)
            directory = os.path.dirname(old_path)
            new_path = os.path.join(directory, new_name)
            
            if os.path.exists(new_path) and new_path != old_path:
                return False, old_path, f"File already exists: {new_path}"
            
            if should_backup:
                backup_path = self._create_backup(old_path)
                logger.info(f"Backup created: {backup_path}")
            
            os.rename(old_path, new_path)
            logger.info(f"File renamed: {old_path} -> {new_path}")
            
            return True, new_path, f"Successfully renamed to {new_name}"
        except Exception as e:
            logger.error(f"Error renaming file {old_path}: {e}")
            return False, old_path, f"Rename failed: {str(e)}"
    
    def _create_backup(self, file_path):
        try:
            os.makedirs(self.backup_folder, exist_ok=True)
            filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{os.path.splitext(filename)[0]}_{timestamp}.pdf"
            backup_path = os.path.join(self.backup_folder, backup_name)
            shutil.copy2(file_path, backup_path)
            logger.debug(f"Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")
            raise
    
    def format_filename(self, template, title=None, year=None, original_name=None):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            title = sanitize_filename(title) if title else "unknown"
            year = sanitize_filename(str(year)) if year else "unknown"
            original_name = sanitize_filename(original_name) if original_name else "unknown"
            
            formatted = template.format(
                title=title,
                year=year,
                original_name=original_name,
                timestamp=timestamp
            )
            
            if not formatted.lower().endswith('.pdf'):
                formatted += '.pdf'
            
            logger.debug(f"Formatted filename: {formatted}")
            return formatted
        except KeyError as e:
            logger.error(f"Invalid template key: {e}")
            return f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        except Exception as e:
            logger.error(f"Error formatting filename: {e}")
            return f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
