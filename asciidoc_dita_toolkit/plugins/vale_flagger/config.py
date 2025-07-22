import yaml
from pathlib import Path
from typing import Dict, Any


class ValeFlaggerConfig:
    """Configuration management for ValeFlagger."""

    DEFAULT_CONFIG = {
        'vale': {
            'enabled_rules': [],
            'disabled_rules': []
        },
        'valeflag': {
            'flag_format': '// ADT-FLAG [{rule}]: {message}',
            'backup_files': False
        }
    }

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        config = self.DEFAULT_CONFIG.copy()

        if config_path:
            path = Path(config_path)
            if path.exists():
                with open(path, 'r') as f:
                    user_config = yaml.safe_load(f) or {}
                    # Deep merge
                    for key, value in user_config.items():
                        if key in config and isinstance(value, dict):
                            config[key].update(value)
                        else:
                            config[key] = value

        return config

    @property
    def enabled_rules(self):
        return self.config['vale'].get('enabled_rules', [])

    @property
    def disabled_rules(self):
        return self.config['vale'].get('disabled_rules', [])

    @property
    def flag_format(self):
        return self.config['valeflag'].get('flag_format', self.DEFAULT_CONFIG['valeflag']['flag_format'])
