# ocr_tool_qt/core/config_manager.py

import json
import os
from utils.logger import log

class ConfigManager:
    """
    Handles loading, accessing, and saving the application's configuration.
    """
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self._ensure_workspace_dirs()

    def _get_default_config(self):
        """Returns the default configuration dictionary."""
        return {
            "poppler_path": "",
            "tesseract_cmd": "",
            "tesseract_lang": "eng",
            "workspace_dir": "data",
            "default_ocr_engine": "windows",
            "clear_cache_on_startup": False,
            "ocr_dpi": 300,
            "pdf_preview_dpi": 150,
            "dynamic_box_tolerance_px": 5,
            "template_match_threshold": 0.6,
            "windows_ocr_lang": "en-US",
            "tesseract_psm": "3",
            "tesseract_oem": "3"
        }

    def _load_config(self):
        """Loads the configuration from the JSON file."""
        default_config = self._get_default_config()
        if not os.path.exists(self.config_path):
            log.warning(f"Config file not found at {self.config_path}. Creating with default values.")
            self.save_config(default_config)
            return default_config

        try:
            with open(self.config_path, 'r') as f:
                user_config = json.load(f)
            
            # Merge user config with defaults to ensure all keys are present
            config = default_config.copy()
            config.update(user_config)
            return config
        except json.JSONDecodeError:
            log.error(f"Error decoding {self.config_path}. Using default configuration.")
            return default_config
        except Exception as e:
            log.error(f"Failed to load config file: {e}. Using defaults.")
            return default_config
            
    def _ensure_workspace_dirs(self):
        """Ensures that all necessary workspace directories exist."""
        workspace_root = self.get('workspace_dir', 'data')
        dirs_to_create = [
            workspace_root,
            os.path.join(workspace_root, 'imports'),
            os.path.join(workspace_root, 'exports'),
            os.path.join(workspace_root, 'cache'),
            os.path.join(workspace_root, 'templates'),
            os.path.join(workspace_root, 'samples')
        ]
        for dir_path in dirs_to_create:
            try:
                os.makedirs(dir_path, exist_ok=True)
            except OSError as e:
                log.error(f"Failed to create directory {dir_path}: {e}")

    def get(self, key, default=None):
        """Gets a configuration value by key."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Sets a configuration value by key."""
        self.config[key] = value

    def save_config(self, config_data=None):
        """Saves the provided configuration data or the current config to the file."""
        data_to_save = config_data if config_data is not None else self.config
        try:
            with open(self.config_path, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            log.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            log.error(f"Failed to save configuration: {e}")

