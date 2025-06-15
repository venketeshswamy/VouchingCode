# ocr_tool_qt/tests/test_core_logic.py

import pytest
import os
import json
from unittest.mock import MagicMock

# To run tests, you'll need to configure the Python path
# For now, we assume the core modules can be imported.
# In a real project, you'd use a proper setup (e.g., setup.py or pyproject.toml)

from core.config_manager import ConfigManager
from core.template_manager import TemplateManager

# Fixture to create a temporary config file for testing
@pytest.fixture
def temp_config(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "test_config.json"
    
    test_data = {"test_key": "test_value", "workspace_dir": str(tmp_path / "data")}
    
    with open(config_file, 'w') as f:
        json.dump(test_data, f)
        
    return str(config_file)


class TestConfigManager:
    def test_load_config(self, temp_config):
        """Tests that the config manager loads a file correctly."""
        cm = ConfigManager(config_path=temp_config)
        assert cm.get("test_key") == "test_value"
        assert cm.get("non_existent_key") is None

    def test_default_config_creation(self, tmp_path):
        """Tests that a default config is created if none exists."""
        config_file = tmp_path / "new_config.json"
        cm = ConfigManager(config_path=str(config_file))
        assert os.path.exists(config_file)
        assert cm.get("ocr_dpi") == 300 # Check a default value


class TestTemplateManager:
    def test_load_templates(self, tmp_path):
        """Tests that templates are loaded from the templates directory."""
        # Setup mock config manager
        mock_config = MagicMock()
        mock_config.get.return_value = str(tmp_path)
        
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        
        template_data = {"name": "Test Template", "type": "visual"}
        with open(templates_dir / "test.json", "w") as f:
            json.dump(template_data, f)
            
        tm = TemplateManager(mock_config)
        loaded_templates = tm.get_templates()
        
        assert len(loaded_templates) == 1
        assert loaded_templates[0]["name"] == "Test Template"

# You could add more tests for SessionManager, regex parsing in TemplateManager, etc.
# These tests should not depend on any GUI components.
