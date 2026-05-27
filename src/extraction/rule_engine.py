"""
Rule-based extraction engine for title and year from OCR text.
"""

import re
from utils.logger import setup_logger


logger = setup_logger(__name__)


class ExtractionEngine:
    """Uses regex rules to extract title and year from text."""
    
    def __init__(self, rules):
        self.rules = sorted(rules, key=lambda x: x.get('priority', 999))
        logger.info(f"Loaded {len(self.rules)} extraction rules")
    
    def extract_title_and_year(self, text):
        logger.debug("Starting title and year extraction")
        
        for rule in self.rules:
            rule_name = rule.get('name', 'Unknown')
            title_pattern = rule.get('title_pattern')
            year_pattern = rule.get('year_pattern')
            
            if not title_pattern or not year_pattern:
                logger.warning(f"Rule '{rule_name}' missing patterns")
                continue
            
            try:
                title = self._extract_title(text, title_pattern)
                year = self._extract_year(text, year_pattern)
                
                if title and year:
                    logger.info(f"Successfully extracted using rule '{rule_name}': title='{title}', year='{year}'")
                    return title, year
                elif title:
                    logger.debug(f"Rule '{rule_name}' extracted title but not year")
                    return title, None
            except Exception as e:
                logger.warning(f"Error applying rule '{rule_name}': {e}")
                continue
        
        logger.warning("No rules successfully extracted title and year")
        return None, None
    
    def _extract_title(self, text, pattern):
        try:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                title = match.group(1) if match.groups() else match.group(0)
                title = title.strip()
                logger.debug(f"Extracted title: '{title}'")
                return title
            return None
        except re.error as e:
            logger.error(f"Regex pattern error: {e}")
            return None
    
    def _extract_year(self, text, pattern):
        try:
            match = re.search(pattern, text)
            if match:
                year = match.group(1) if match.groups() else match.group(0)
                year = year.strip()
                logger.debug(f"Extracted year: '{year}'")
                return year
            return None
        except re.error as e:
            logger.error(f"Regex pattern error: {e}")
            return None
