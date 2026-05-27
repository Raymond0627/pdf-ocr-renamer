"""
PDF OCR Renamer - Main entry point.

An intelligent desktop application that automatically renames scanned PDF 
documents based on their content using OCR and rule-based extraction.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import main


if __name__ == "__main__":
    main()
