"""
PDF processing - Convert PDF pages to images for OCR.
"""

from pdf2image import convert_from_path
from PIL import Image, ImageOps, ImageFilter
import os
from utils.logger import setup_logger


logger = setup_logger(__name__)


class PDFProcessor:
    """Handles PDF to image conversion with preprocessing."""
    
    def __init__(self, dpi=300, poppler_path=None):
        self.dpi = dpi
        self.poppler_path = poppler_path
    
    def convert_pdf_to_images(self, pdf_path):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            logger.info(f"Converting PDF to images: {pdf_path} (DPI: {self.dpi})")
            kwargs = {"dpi": self.dpi}
            if self.poppler_path:
                kwargs["poppler_path"] = self.poppler_path
            
            images = convert_from_path(pdf_path, **kwargs)
            logger.info(f"Successfully converted {len(images)} pages from {pdf_path}")
            return images
        except Exception as e:
            logger.error(f"Failed to convert PDF {pdf_path}: {e}")
            raise
    
    def preprocess_image(self, image, grayscale=True, autocontrast=True, 
                         binarize=True, threshold=140):
        try:
            if grayscale:
                image = image.convert('L')
            if autocontrast:
                image = ImageOps.autocontrast(image)
            if binarize:
                image = image.point(lambda x: 0 if x < threshold else 255, '1')
            logger.debug("Image preprocessing completed")
            return image
        except Exception as e:
            logger.error(f"Error during image preprocessing: {e}")
            raise
    
    def preprocess_images_batch(self, images, **kwargs):
        preprocessed = []
        for i, img in enumerate(images):
            try:
                processed = self.preprocess_image(img, **kwargs)
                preprocessed.append(processed)
            except Exception as e:
                logger.warning(f"Failed to preprocess image {i}: {e}")
                preprocessed.append(img)
        return preprocessed
    
    def get_first_page_image(self, pdf_path, preprocess=True, **kwargs):
        images = self.convert_pdf_to_images(pdf_path)
        if not images:
            raise ValueError(f"No pages found in PDF: {pdf_path}")
        first_page = images[0]
        if preprocess:
            first_page = self.preprocess_image(first_page, **kwargs)
        return first_page
