"""
Validation utilities for input and file handling.
"""

import os
import re
from pathlib import Path


def validate_folder_path(folder_path):
    if not folder_path:
        return False, "Folder path is empty"
    if not os.path.exists(folder_path):
        return False, f"Folder does not exist: {folder_path}"
    if not os.path.isdir(folder_path):
        return False, f"Path is not a directory: {folder_path}"
    if not os.access(folder_path, os.R_OK):
        return False, f"Folder is not readable: {folder_path}"
    return True, ""


def validate_pdf_files(folder_path):
    is_valid, error = validate_folder_path(folder_path)
    if not is_valid:
        raise ValueError(error)
    
    pdf_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(''.pdf''):
            pdf_files.append(os.path.join(folder_path, file))
    
    return pdf_files


def validate_filename(filename):
    if not filename:
        return False, "Filename is empty"
    invalid_chars = r''[<>:"/\\|?*]''
    if re.search(invalid_chars, filename):
        return False, f"Filename contains invalid characters: {filename}"
    if len(filename) > 255:
        return False, "Filename is too long (max 255 characters)"
    return True, ""


def sanitize_filename(filename, replacement="_"):
    invalid_chars = r''[<>:"/\\|?*]''
    sanitized = re.sub(invalid_chars, replacement, filename)
    sanitized = sanitized.rstrip('''. '')
    if len(sanitized) > 255:
        sanitized = sanitized[:251] + "..."
    return sanitized


def validate_regex_pattern(pattern):
    try:
        re.compile(pattern)
        return True, ""
    except re.error as e:
        return False, f"Invalid regex pattern: {e}"
