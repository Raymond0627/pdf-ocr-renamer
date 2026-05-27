"""
Text extraction using Tesseract OCR.
"""

import pytesseract
import os
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class TextExtractor:
    """Handles OCR text extraction using Tesseract."""
    
    def __init__(self, tesseract_path=None, language="eng"):
        self.language = language
        
        if tesseract_path:
            pytesseract.pytesseract.pytesseract_cmd = tesseract_path
            logger.info(f"Tesseract path set to: {tesseract_path}")
        
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR is available")
        except pytesseract.TesseractNotFoundError:
            logger.error("Tesseract OCR not found. Please install it and configure the path.")
            raise
    
    def extract_text(self, image):
        try:
            logger.debug(f"Extracting text using language: {self.language}")
            text = pytesseract.image_to_string(image, lang=self.language)
            logger.debug(f"Extracted {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise
    
    def extract_text_batch(self, images):
        extracted_texts = []
        for i, img in enumerate(images):
            try:
                text = self.extract_text(img)
                extracted_texts.append(text)
            except Exception as e:
                logger.warning(f"Failed to extract text from image {i}: {e}")
                extracted_texts.append("")
        return extracted_texts
    
    def clean_text(self, text):
        lines = [line.strip() for line in text.split(''\n'')]
        lines = [line for line in lines if line]
        cleaned = '' ''.join(lines)
        return cleaned
