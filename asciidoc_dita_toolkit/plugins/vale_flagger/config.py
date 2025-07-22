import copy
import yaml
from pathlib import Path
from typing import Dict, Any

# Default Docker image for Vale with AsciiDocDITA rules
DEFAULT_DOCKER_IMAGE = "ghcr.io/rolfedh/asciidoc-dita-toolkit-vale-adv:latest"


class ValeFlaggerConfig:
    """Configuration management for ValeFlagger."""

    DEFAULT_CONFIG = {
        'vale': {
            'enabled_rules': [],
            'disabled_rules': [],
            'timeout_seconds': 300,  # 5 minute default timeout
            'docker_image': DEFAULT_DOCKER_IMAGE
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
        config = copy.deepcopy(self.DEFAULT_CONFIG)

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

    @property
    def timeout_seconds(self):
        return self.config['vale'].get('timeout_seconds', self.DEFAULT_CONFIG['vale']['timeout_seconds'])

    @property
    def docker_image(self):
        return self.config['vale'].get('docker_image', self.DEFAULT_CONFIG['vale']['docker_image'])
