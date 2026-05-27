"""
Configuration management for the application.
"""

import json
import os


class Config:
    """Manages application configuration from JSON files."""
    
    def __init__(self, settings_file="config/settings.json", rules_file="config/extraction_rules.json"):
        self.settings_file = settings_file
        self.rules_file = rules_file
        self.settings = self._load_json(settings_file)
        self.extraction_rules = self._load_json(rules_file)
    
    @staticmethod
    def _load_json(file_path):
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Configuration file not found: {file_path}")
            
            with open(file_path, ''r'') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}")
        except Exception as e:
            raise Exception(f"Error loading {file_path}: {e}")
    
    def get_setting(self, key, default=None):
        return self.settings.get(key, default)
    
    def get_extraction_rule(self, rule_name):
        for rule in self.extraction_rules.get("rules", []):
            if rule.get("name") == rule_name:
                return rule
        return None
    
    def get_all_rules(self):
        rules = self.extraction_rules.get("rules", [])
        return sorted(rules, key=lambda x: x.get("priority", 999))
    
    def get_output_format(self):
        return self.extraction_rules.get("output_format", "{title}_{year}.pdf")
    
    def get_backup_format(self):
        return self.extraction_rules.get("backup_format", "{original_name}_{timestamp}.pdf")
    
    def reload(self):
        self.settings = self._load_json(self.settings_file)
        self.extraction_rules = self._load_json(self.rules_file)
